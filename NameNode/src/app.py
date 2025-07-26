from fastapi import FastAPI

app= FastAPI()

@app.get("/health")
async def namenode_healthcheck():
    return{"status":"ok"}
