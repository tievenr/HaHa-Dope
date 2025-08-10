from datetime import datetime, timedelta
from block_manager import split_file_into_blocks
from typing import Dict, Any
import os 
import json

METADATA_DIR = "/usr/local/app/namenode_metadata"
active_datanodes = {}  
file_metadata={}
block_assignments={}
HEARTBEAT_TIMEOUT_SECONDS = 30  # Node considered alive if heartbeat within this window


os.makedirs(METADATA_DIR, exist_ok=True)

def update_datanode_heartbeat(node_id):
    """Update heartbeat timestamp for a DataNode."""
    active_datanodes[node_id] = datetime.now()

def get_available_datanodes():
    """Return list of DataNodes with recent heartbeats (alive)."""
    current_time = datetime.now()
    available_nodes = []
    for node_id, last_heartbeat in active_datanodes.items():
        # Only include nodes with heartbeat within timeout
        if (current_time - last_heartbeat).total_seconds() <= HEARTBEAT_TIMEOUT_SECONDS:
            available_nodes.append(node_id)
    return available_nodes

def assign_blocks_to_datanode(filename, filesize, replication_factor=2):
    """
    Assign each block to a set of DataNodes for replication.
    Returns a dict with block info and assigned datanodes.
    """
    available_nodes = get_available_datanodes()  # Get all alive DataNodes
    blocks = split_file_into_blocks(filename, filesize)  # Split file into blocks
    if not available_nodes:
        print(f"WARNING: No available datanodes for file {filename}")
        return {"blocks": []}
    result_blocks = []
    for block_index, block in enumerate(blocks):
        assigned_datanodes = []
        # Assign block to consecutive datanodes (n, n+1, ...)
        num_replicas = min(replication_factor, len(available_nodes))
        for i in range(num_replicas):
            node_index = (block_index + i) % len(available_nodes)
            assigned_datanodes.append(available_nodes[node_index])
        result_blocks.append({
            "block_id": block["block_id"],
            "size": block["size"],
            "assigned_datanodes": assigned_datanodes
        })
        print(f"Assigned block {block['block_id']} to datanodes: {assigned_datanodes}")
        #updates block assignements to the global var for persistent metatda
        block_assignments[block["block_id"]] = assigned_datanodes
    #updates file metadata to the global var so we can persist fr 
    file_metadata[filename] = {
        "filesize": filesize,
        "total_blocks": len(blocks),
        "created_at": datetime.now().isoformat(),
        "replication_factor": replication_factor
    }
    store_metadata()

    return {"blocks": result_blocks}



def store_metadata():
    """
    Persist all metadata to disk in JSON format.
    """
    try:
        # convert datetime to string
        metadata = {
            "active_datanodes": {
                node_id: dt.isoformat() for node_id,dt in active_datanodes.items()
            },
            "file_metadata": file_metadata,
            "block_assignments": block_assignments,
            "last_updated": datetime.now().isoformat()
        }
        temp_file = os.path.join(METADATA_DIR, "metadata.json.tmp")
        final_file = os.path.join(METADATA_DIR, "metadata.json")
        
        # json.dump() to write metadata into temp
        with open(temp_file,"w",encoding="utf-8") as f:
            json.dump(metadata,f,indent=2)

        # atomic move temp_file to final_file to prevent partial writes
        os.rename(temp_file,final_file)
        
        print(f"✅ Metadata saved to {final_file}")
        
    except Exception as e:
        print(f"Failed to save metadata: {e}")
         # only remove if file exists
        if os.path.exists(temp_file):
            try:
                os.remove(temp_file)
            except Exception:
                pass  


def load_metadata():
    """
    Load metadata from disk on NameNode startup.
    """
    global active_datanodes, file_metadata, block_assignments
    
    metadata_file = os.path.join(METADATA_DIR, "metadata.json")
    
    # Check if file exists
    if not os.path.exists(metadata_file):
        print("No existing metadata found. Starting fresh.")
        return
    
    try:
        # read the JSON file
        with open(metadata_file,"r",encoding="utf-8") as f:
            metadata= json.load(f)
        
        # Restore active_datanodes (convert ISO strings back to datetime)
        active_datanodes={
            node_id: datetime.fromisoformat(dt_str) for node_id, dt_str in metadata["active_datanodes"].items()
        }
        # Restore file_metadata and block_assignments
        file_metadata=metadata["file_metadata"]
        block_assignments=metadata["block_assignments"]
        print(f"Metadata loaded successfully")
        
    except Exception as e:
        print(f"Failed to load metadata: {e}")
        active_datanodes={}
        file_metadata={}
        block_assignments={}