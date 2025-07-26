import logging
from fastapi import FastAPI, Request

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s: %(name)s: %(levelname)s: %(message)s',
    handlers=[
        logging.FileHandler('/usr/local/app/namenode_logs/namenode.log'),  #This line is for persistent logs under the log volume
        logging.StreamHandler()  # This one is for when docker container logs
    ]
)
logger = logging.getLogger(__name__)

app = FastAPI()

@app.get("/health")
async def namenode_healthcheck():
    return {"status": "ok"}

@app.post("/nodes/{node_id}/heartbeat")
async def recieve_heartbeats(node_id: str, request: Request):
    payload = await request.json()
    logger.info(f"Heartbeat received from {node_id}: {payload}")
    return {"recieved from": node_id, "payload": payload}