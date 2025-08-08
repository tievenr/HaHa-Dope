import os
import requests
import json
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

namenode_url = "http://127.0.0.1:9870"

def namenode_healthcheck():
    try:
        res = requests.get(namenode_url + "/health")
        return res.status_code == 200
    except Exception as e:
        logger.error(f"Failed to connect to NameNode: {e}")
        return False

def upload(filename):
    url = namenode_url + "/files"
    file_size = os.path.getsize(filename)
    payload = {
        "filename": filename,
        "filesize_bytes": file_size
    }
    
    logger.info(f"Uploading {filename} ({file_size:,} bytes)")
    
    try:
        r = requests.post(url, json=payload)
        logger.info(f"Upload response status: {r.status_code}")
        return r
    except Exception as e:
        logger.error(f"Upload error: {e}")
        return None

def display_upload_result(response):
    """Pretty print the upload result"""
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
    
    if namenode_healthcheck():
        logger.info("NameNode is healthy!")
        
        filename = os.path.join("client_testfiles", "test.txt")
        response = upload(filename)
        
        if response and response.status_code == 200:
            display_upload_result(response)
        else:
            logger.error("Upload failed")
    else:
        logger.error("NameNode is not reachable")