# HAHAHAHAHAHAHa-Dope

A Hadoop-inspired distributed file system simulation built with Python, FastAPI, and Docker.

## Architecture

- **NameNode**: Central coordinator that manages file metadata and receives heartbeats
- **DataNode(s)**: Worker nodes that send periodic heartbeats to the NameNode
- **Client**: (Coming soon) File upload interface

## Current Features

- ✅ NameNode with REST API endpoints
- ✅ DataNode heartbeat mechanism
- ✅ Docker Compose orchestration
- ✅ Persistent logging with Docker volumes
- ✅ File upload endpoint with block splitting logic
- ✅ Scalable DataNode deployment

## Quick Start

### 1. Build and Start the System

```bash
# Start with default configuration (3 DataNodes)
docker-compose up --build

# Or run in detached mode
docker-compose up --build -d
```

### 2. Scale DataNodes

```bash
# Scale to 5 DataNodes
docker-compose up --scale datanode=5 -d

# Scale to 10 DataNodes
docker-compose up --scale datanode=10 -d

# Scale down to 2 DataNodes
docker-compose up --scale datanode=2 -d
```

### 3. View System Activity

```bash
# Watch all logs in real-time
docker-compose logs -f

# View specific service logs
docker-compose logs -f namenode
docker-compose logs -f datanode

# View logs from specific DataNode
docker-compose logs datanode-1
```

### 4. Test the System

```bash
# Check NameNode health
curl http://localhost:9870/health

# Test file upload endpoint
curl -X POST http://localhost:9870/files \
  -H "Content-Type: application/json" \
  -d '{"filename": "test.txt", "size": 1024}'
```

## System Endpoints

### NameNode (Port 9870)

- `GET /health` - Health check
- `POST /nodes/{node_id}/heartbeat` - Receive DataNode heartbeats
- `POST /files` - File upload and block splitting

## Logging

The system uses persistent logging for observability and debugging. Here’s how logs are managed:

### NameNode Logs

- **namenode.log**: General NameNode events (startup, heartbeats, file uploads)
  - **Location in container:** `/usr/local/app/namenode_logs/namenode.log`
- **blocks.log**: Block splitting and block management events
  - **Location in container:** `/usr/local/app/namenode_logs/blocks.log`
- **Docker volume:** Both files are stored in the `namenode_logs` volume for persistence.

### DataNode Logs

- By default, DataNode logs are written to the container’s console output (stdout).
- You can view these logs using `docker-compose logs datanode` or `docker logs <datanode-container-name>`.
- **No persistent log file** is configured for DataNodes by default.

### Log Volumes

- **NameNode logs:** `namenode_logs` volume
- **NameNode metadata:** `namenode_data` volume
- **DataNode data:** `datanode_data` volume

## Stop the System

```bash
# Stop all services
docker-compose down

# Stop and remove volumes (WARNING: deletes all data)
docker-compose down -v
```

## Project Structure

```
.
├── namenode/
│   ├── Dockerfile
│   ├── app.py
│   └── block_manager.py
├── datanode/
│   ├── Dockerfile
│   ├── app.py
│   └── entrypoint.sh
└── docker-compose.yml
```

## Next Steps

- [ ] Build client for file uploads
- [ ] Implement actual data storage in DataNodes
- [ ] Add replication logic

- [ ] Build file retrieval system
