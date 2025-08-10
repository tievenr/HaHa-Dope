
from fastapi import FastAPI, Request
from block_manager import split_file_into_blocks
from pydantic import BaseModel
import os 
from metadata_manager import update_datanode_heartbeat,assign_blocks_to_datanode, load_metadata
from namenode_logger import get_namenode_logger

REPLICATION_FACTOR = int(os.getenv('REPLICATION_FACTOR', '2'))


logger = get_namenode_logger()
# Logger done initialized above 🥀
logger.info(f"NameNode starting with replication factor: {REPLICATION_FACTOR}")
logger.info("Loading metadat on Namenode Startup ...")
load_metadata()
logger.info("Namenode ready to serve request")

app = FastAPI()


#pydantic class for file upload
class FileUploadRequest(BaseModel):
    filename:str
    filesize_bytes:int

#below function be beating only if Namenode is up and running 
@app.get("/health")
async def namenode_healthcheck():
    return {"status": "ok"}


# ts is to just for namenode to know that datanode is alive
@app.post("/nodes/{node_id}/heartbeat")
async def recieve_heartbeats(node_id: str, request: Request):
    payload = await request.json()
    logger.info(f"Heartbeat received from {node_id}: {payload}")
    update_datanode_heartbeat(node_id)
    return {"recieved from": node_id, "payload": payload}

# This one is when client upload the file so namenode has to split it up 
@app.post("/files")
async def upload_file(file_request: FileUploadRequest):
    filename = file_request.filename
    filesize_bytes = file_request.filesize_bytes
    assignment = assign_blocks_to_datanode(filename, filesize_bytes, REPLICATION_FACTOR)
    return assignment