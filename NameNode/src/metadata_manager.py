from datetime import datetime, timedelta
from block_manager import split_file_into_blocks

active_datanodes = {}  
HEARTBEAT_TIMEOUT_SECONDS = 30  # Node considered alive if heartbeat within this window

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
    return {"blocks": result_blocks}



def store_metadata():
    pass