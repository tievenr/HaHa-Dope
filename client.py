import os  
import requests  
import json
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

# Setup logging for the client
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Base URL for the NameNode API
namenode_url = "http://127.0.0.1:9870"

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

def upload(filename):
    #Send a POST request to NameNode to upload file metadata
    url = namenode_url + "/files"
    file_size = os.path.getsize(filename)  # File size in bytes
    payload = {
        "filename": filename,
        "filesize_bytes": file_size
    }
    logger.info(f"Uploading {filename} ({file_size:,} bytes)")
    try:
        r = requests.post(url, json=payload)
        logger.info(f"Upload response status: {r.status_code}")
        return r  # Return the response object
    except Exception as e:
        logger.error(f"Upload error: {e}")
        return None

def upload_multiple_files(files_list, max_concurrent=5):
    if not files_list:
        logger.info("No files to upload")
        return
    logger.info(f"Starting concurrent upload of {len(files_list)} files (max {max_concurrent} at once)")

    failed_files=[] # This is to retry the upload again on case of failure
    with ThreadPoolExecutor(max_workers=max_concurrent) as executor:
        future_to_file = {executor.submit(upload, file): file for file in files_list}
    #Dictionary which maps the file being uploaded to it's file name

    # Process results as they complete
        for future in as_completed(future_to_file):
            filename = future_to_file[future] #get's da filename from the key
            try:
                response = future.result()
                if response and response.status_code == 200:
                    logger.info(f"{filename} uploaded successfully")
                else:
                    #This is to catch errors which occurred after the upload began
                    logger.error(f"{filename} upload failed")
                    failed_files.append(filename)

            except Exception as e:
                #errors before uploading
                logger.error(f"{filename} failed with exception: {e}")
                failed_files.append(filename)
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
                    else:
                        logger.error(f"{filename} retry failed - giving up")
                except Exception as e:
                    logger.error(f"{filename} retry failed with exception: {e}")    


def display_upload_result(response):
    #THIS BLOCK IS PURELY FOR AESTHETICS; displays the upload result from the NameNode
    try:
        data = response.json()
        blocks = data.get("blocks", [])
        print("\n" + "="*60)
        print("FILE UPLOAD RESULT")
        print("="*60)
        if blocks:
            total_size = sum(block["size"] for block in blocks)
            print(f"Total file size: {total_size:,} bytes")
            print(f"Number of blocks: {len(blocks)}")
            print(f"Block size: 32MB (33,554,432 bytes)")
            print("\nBlock Details:")
            print("-" * 60)
            for i, block in enumerate(blocks, 1):
                print(f"Block {i}:")
                print(f"  ID: {block['block_id']}")
                print(f"  Size: {block['size']:,} bytes ({block['size'] / 1024 / 1024:.1f} MB)")
                if i < len(blocks):
                    print()
        print("="*60)
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