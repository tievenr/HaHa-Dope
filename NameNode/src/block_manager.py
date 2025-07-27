import os
import uuid
import logging
import re


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s: %(name)s: %(levelname)s: %(message)s',
    handlers=[
        logging.FileHandler('/usr/local/app/namenode_logs/blocks.log'),  #This line is for persistent logs under the log volume hahadope-namenode_logs/
    ]
)
logger = logging.getLogger(__name__)
block_size=int(os.getenv("BLOCK_SIZE_BYTES", "33554432")) #sets the block size to 32MB but in bytes for manipulation

def sanitize_filename(filename="unknown_file"):
    sanitized = re.sub(r'[^a-zA-Z0-9]', '_', filename) #removing non alphanumeric characters in the filename
    sanitized = re.sub(r'_+', '_', sanitized) # replacing consecutive underscores with _
    return sanitized.strip('_')  


def generate_block_id(filename="unknown_file", block_index=0):
    sanitized_name = sanitize_filename(filename)
    short_uuid = str(uuid.uuid4())[:8]
    return f"block_{sanitized_name}_{block_index:04d}_{short_uuid}"


def split_file_into_blocks(filename="unknown_file",filesize=0):
    if not filename:  # this is to handle in the edge case of when "None" is passed onto to the function as an argument
        filename = "unknown_file"
    if filesize <= 0:
        logger.warning(f"File '{filename}' has invalid size: {filesize}")  
        return []
    
    blocks=[] #Empty list of dictionaries to store the block data 
    num_blocks= (filesize+ block_size-1 )//block_size
    
    for i in range(num_blocks):
        start_byte= i*block_size
        end_byte= min((i+1)*block_size,filesize)
        size=end_byte-start_byte
        block_id= generate_block_id(filename,i)

        blocks.append({
            "block_id": block_id,
            "start_byte":start_byte,
            "end_byte":end_byte,
            "size": size

        })
    logger.info(f"Splitting {filename} of size {filesize} into {num_blocks} blocks")

    return blocks
    
