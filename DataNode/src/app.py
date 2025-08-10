from fastapi import FastAPI, HTTPException
import requests
import os
import logging
import time
from datetime import datetime, timezone
import threading
from contextlib import asynccontextmanager
from pydantic import BaseModel
import base64

# logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s: %(name)s: %(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)

NODE_ID = os.getenv("NODE_ID", "datanode")
DATA_DIR = f"/usr/local/app/data/{NODE_ID}"
os.makedirs(DATA_DIR, exist_ok=True)
HEARTBEAT_URL = f"http://namenode:9870/nodes/{NODE_ID}/heartbeat"

# Request model for storing a block
class BlockStorageRequest(BaseModel):
    block_id: str
    block_data: str  # base64-encoded

# Background thread: send heartbeats to NameNode
def send_heartbeats():
    while True:
        timestamp = datetime.now(timezone.utc)
        payload = {"node_id": NODE_ID, "timestamp": timestamp.isoformat()}
        try:
            response = requests.post(HEARTBEAT_URL, json=payload)
            logger.info(f"{timestamp} | {response.status_code} | {response.json()}")
        except Exception as e:
            logger.error(f"{timestamp} | Error: {e}")
        time.sleep(1)

# FastAPI lifespan event: start heartbeat thread
@asynccontextmanager
async def lifespan(app: FastAPI):
    thread = threading.Thread(target=send_heartbeats, daemon=True)
    thread.start()
    logger.info(f"DataNode {NODE_ID} started, sending heartbeats to NameNode")
    yield

app = FastAPI(title=f"DataNode {NODE_ID}", lifespan=lifespan)

# Health endpoint for monitoring
@app.get("/health")
async def datanode_health():
    return {"status": "ok", "node_id": NODE_ID}

# Endpoint to store a file block
@app.post("/store_block")
async def store_block(request: BlockStorageRequest):
    """
    Store a file block on this DataNode
    """
    try:
        # Decode the base64 block data
        block_data = base64.b64decode(request.block_data)
        # Create the file path using DATA_DIR and block_id
        block_path = os.path.join(DATA_DIR, f"{request.block_id}.dat")
        # Write the block data to a .dat file
        with open(block_path, "wb") as f:
            f.write(block_data)
        # Return success response with file info
        return {
            "status": "success",
            "node_id": NODE_ID,
            "block_id": request.block_id,
            "block_path": block_path,
            "block_size": os.path.getsize(block_path),
            "message": f"Block stored successfully"
        }
    except Exception as e:
        logger.error(f"Failed to store block {request.block_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to store block: {str(e)}")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)