
from datetime import datetime, timedelta



active_datanodes = {}  

HEARTBEAT_TIMEOUT_SECONDS = 30

def update_datanode_heartbeat(node_id):
    """Called when a heartbeat is received from a datanode"""
    active_datanodes[node_id] = datetime.now()

def get_available_datanodes():
    """Get list of datanodes that sent heartbeats recently"""
    current_time = datetime.now()
    available_nodes = []
    
    for node_id, last_heartbeat in active_datanodes.items():
        # Check if heartbeat is within the timeout window
        time_since_heartbeat = current_time - last_heartbeat
        if time_since_heartbeat.total_seconds() <= HEARTBEAT_TIMEOUT_SECONDS:
            available_nodes.append(node_id)
    
    return available_nodes

