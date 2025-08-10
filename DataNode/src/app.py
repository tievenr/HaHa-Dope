from fastapi import FastAPI
import requests
import os
import logging
import time
from datetime import datetime, timezone
import threading
from contextlib import asynccontextmanager


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s: %(name)s: %(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)

NODE_ID = os.getenv("NODE_ID", "datanode")
DATA_DIR = f"/usr/local/app/data/{NODE_ID}"
os.makedirs(DATA_DIR, exist_ok=True)
HEARTBEAT_URL = f"http://namenode:9870/nodes/{NODE_ID}/heartbeat"


def send_heartbeats():
    """Background function to send heartbeats"""
    while True:
        timestamp = datetime.now(timezone.utc)
        payload = {"node_id": NODE_ID, "timestamp": timestamp.isoformat()}
        try:
            response = requests.post(HEARTBEAT_URL, json=payload)
            logger.info(f"{timestamp} | {response.status_code} | {response.json()}")
        except Exception as e:
            logger.error(f"{timestamp} | Error: {e}")
        time.sleep(1)


@asynccontextmanager
async def lifespan(app: FastAPI):
    thread = threading.Thread(target=send_heartbeats, daemon=True)
    thread.start()
    logger.info(f"DataNode {NODE_ID} started, sending heartbeats to NameNode")
    yield

app = FastAPI(title=f"DataNode {NODE_ID}", lifespan=lifespan)


# Health enpoint for datanode
@app.get("/health")
async def datanode_health():
    return {"status": "ok", "node_id": NODE_ID}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)