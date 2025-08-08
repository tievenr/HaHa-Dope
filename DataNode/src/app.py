import requests
import os
import logging
import time
from datetime import datetime, timezone

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s: %(name)s: %(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)

node_id = os.getenv("NODE_ID", "datanode")
heartbeat_url = f"http://namenode:9870/nodes/{node_id}/heartbeat"

while True:
    timestamp = datetime.now(timezone.utc)
    payload = {"node_id": node_id, "timestamp": timestamp.isoformat()}
    try:
        response = requests.post(heartbeat_url, json=payload)
        logger.info(f"{timestamp} | {response.status_code} | {response.json()}")
    except Exception as e:
        logger.error(f"{timestamp} | Error: {e}")
    time.sleep(1)