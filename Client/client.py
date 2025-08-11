import os  
import requests  
import json
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import base64

# Setup logging for the client
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Base URL for the NameNode API
namenode_url = "http://namenode:9870"

def namenode_healthcheck():
    """Check if the NameNode is reachable and healthy."""
    try:
        res = requests.get(namenode_url + "/health")
        return res.status_code == 200
    except Exception as e:
        logger.error(f"Failed to connect to NameNode: {e}")
        return False

def scan_directory(directory_path="client_testfiles"):
    if os.path.exists(directory_path):  # Fix this
        files_list = [os.path.join(directory_path, f) for f in os.listdir(directory_path) if f.endswith((".txt",".pdf")) and os.path.isfile(os.path.join(directory_path, f))]
        #This above line checks if there are files with .txt or .pdf extensions and then joins it to the directory path so upload() function doesn't have to be modified
        if len(files_list) <= 0:
            logger.info(f"{directory_path} has no valid files")
        logger.info(f"Found {len(files_list)} files_list to upload")  
        return files_list
    else:
        logger.error(f"{directory_path} doesn't exist")
        return []  

def send_blocks_to_datanodes(filename, blocks):
    """Send file blocks directly to assigned DataNodes"""
    try:
        with open(filename, 'rb') as file:
            for block in blocks:
                block_id = block['block_id']
                block_size = block['size'] 
                assigned_datanodes = block['assigned_datanodes']
                
                # Read the exact block_size bytes from file
                block_data = file.read(block_size)
                
                # Sends this block to each assigned DataNode
                for datanode_id in assigned_datanodes:
                    url = f"http://{datanode_id}:8000/store_block"
                    block_b64 = base64.b64encode(block_data).decode()
                    payload = {
                               "block_id": block_id,
                               "block_data": block_b64
                            }
                    response = requests.post(url, json=payload, timeout=10)
                    if response.status_code != 200:
                        logger.error(f"Failed to send block {block_id} to {datanode_id}")
                        return False
                    else:
                        logger.info(f"Successfully sent block {block_id} to {datanode_id}")
                    
        return True
    except Exception as e:
        logger.error(f"Error sending blocks: {e}")
        return False

def upload(filename):
    # Get block assignments from NameNode (existing code)
    url = namenode_url + "/files"
    file_size = os.path.getsize(filename)
    payload = {"filename": filename, "filesize_bytes": file_size}
    
    try:
        r = requests.post(url, json=payload)
        if r.status_code != 200:
            return r
            
        assignments = r.json()
        blocks = assignments.get("blocks", [])
        
        if blocks:
            success = send_blocks_to_datanodes(filename, blocks)
            if not success:
                logger.error(f"Failed to upload blocks for {filename}")
                return None
        
        return r
        
    except Exception as e:
        logger.error(f"Upload error: {e}")
        return None

def upload_multiple_files(files_list, max_concurrent=5):
    if not files_list:
        logger.info("No files to upload")
        return
    logger.info(f"Starting concurrent upload of {len(files_list)} files (max {max_concurrent} at once)")

    failed_files=[] # This is to retry the upload again on case of failure
    successful_uploads=[]
    with ThreadPoolExecutor(max_workers=max_concurrent) as executor:
        #Dictionary which maps the file being uploaded to it's file name
        future_to_file = {executor.submit(upload, file): file for file in files_list}

         # Process results as they complete
        for future in as_completed(future_to_file):
            filename = future_to_file[future] #get's da filename from the key
            try:
                response = future.result()
                if response and response.status_code == 200:
                    logger.info(f"{filename} uploaded successfully")
                    successful_uploads.append((filename, response))
                else:
                    #This is to catch errors which occurred after the upload began
                    logger.error(f"{filename} upload failed")
                    failed_files.append(filename)

            except Exception as e:
                #errors before uploading
                logger.error(f"{filename} failed with exception: {e}")
                failed_files.append(filename)

    #Failed upload handler
    if failed_files:
        logger.info(f"Retrying {len(failed_files)} failed files after 2 second delay...")
        time.sleep(2)  
    
        with ThreadPoolExecutor(max_workers=max_concurrent) as executor:
            future_to_file = {executor.submit(upload, file): file for file in failed_files}
        
            for future in as_completed(future_to_file):
                filename = future_to_file[future]
                try:
                    response = future.result()
                    if response and response.status_code == 200:
                        logger.info(f"{filename} retry successful")
                        successful_uploads.append((filename,response))
                    else:
                        logger.error(f"{filename} retry failed - giving up")
                except Exception as e:
                    logger.error(f"{filename} retry failed with exception: {e}") 
    if successful_uploads:
        logger.info(f"\nDisplaying block information for {len(successful_uploads)} successful uploads:")
        for filename, response in successful_uploads:
            print(f"\n--- Results for {filename} ---")
            display_upload_result(response)   

def display_upload_result(response):
    # This function is purely for aesthetics  
    print(f"Raw response: {response.text}")
    try:
        data = response.json()
        blocks = data.get("blocks", [])
        print("\n" + "="*80)
        print("FILE UPLOAD RESULT")
        print("="*80)
        if blocks:
            total_size = sum(block["size"] for block in blocks)
            print(f"Total file size: {total_size:,} bytes ({total_size / 1024 / 1024:.1f} MB)")
            print(f"Number of blocks: {len(blocks)}")
            print(f"Block size: 32MB (33,554,432 bytes)")
            print("\nBlock Assignment Table:")
            print("-" * 80)
            # Table header
            print(f"{'Block':<8} {'Block ID':<25} {'Size (MB)':<12} {'Assigned DataNodes'}")
            print("-" * 80)
            # Table rows
            for i, block in enumerate(blocks, 1):
                block_id = block['block_id']
                size_mb = block['size'] / 1024 / 1024
                datanodes = ', '.join(block.get('assigned_datanodes', []))
                # Truncate long datanode lists if needed
                if len(datanodes) > 30:
                    datanodes = datanodes[:27] + "..."
                print(f"{i:<8} {block_id:<25} {size_mb:<12.1f} {datanodes}")
        print("="*80)
    except Exception as e:
        logger.error(f"Error parsing response: {e}")
        print(f"Raw response: {response.text}")

if __name__ == "__main__":
    logger.info("Starting client...")
    files = scan_directory()
    print(files)  
    if namenode_healthcheck():
        logger.info("NameNode is healthy!")
        upload_multiple_files(files)  
    else:
        logger.error("NameNode is not reachable")
