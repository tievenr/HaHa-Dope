import logging
import os

# Create logs directory if it doesn't exist
os.makedirs('/usr/local/app/namenode_logs', exist_ok=True)
os.makedirs('/usr/local/app/namenode_block_logs', exist_ok=True)

def get_namenode_logger():
    """Get the main NameNode logger"""
    logger = logging.getLogger('namenode_main')  # Changed from 'namenode'
    if not logger.handlers:  # Only configure once
        logger.setLevel(logging.INFO)
        
        handler = logging.FileHandler('/usr/local/app/namenode_logs/namenode.log')
        handler.setLevel(logging.INFO)
        
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        
        logger.addHandler(handler)
    
    return logger

def get_blocks_logger():
    """Get the blocks-specific logger"""
    logger = logging.getLogger('namenode_blocks')  # Changed from 'namenode.blocks'
    if not logger.handlers:  # Only configure once
        logger.setLevel(logging.INFO)
        
        handler = logging.FileHandler('/usr/local/app/namenode_block_logs/blocks.log')
        handler.setLevel(logging.INFO)
        
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        
        logger.addHandler(handler)
    
    return logger 