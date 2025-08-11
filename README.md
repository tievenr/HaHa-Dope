# HAHAHAHAHAHAHa-Dope

A distributed file system simulation inspired by Hadoop HDFS, built with Python, FastAPI, and Docker. This project demonstrates core concepts like a central NameNode for metadata management, DataNodes for storage, block-based file splitting, and data replication.

## Architecture

The system is composed of three main components that communicate over a Docker network:

- **NameNode**: The central coordinator. It manages the file system's namespace, tracks which blocks belong to which files, and monitors the health of all DataNodes via a heartbeat mechanism. It does **not** store any file data itself, only metadata.
- **DataNode(s)**: Worker nodes responsible for storing the actual file blocks. They periodically send heartbeats to the NameNode to report that they are alive and ready. The system is designed to be horizontally scalable by adding more DataNode services.
- **Client**: A command-line utility that interacts with the NameNode to upload files. It handles concurrent uploads and displays the block assignment results.

## Features

- **RESTful NameNode**: Built with FastAPI, providing endpoints for health checks, heartbeats, and file operations.
- **Scalable DataNodes**: Easily scale the number of DataNodes up or down using Docker Compose.
- **Block-Based Storage**: Files are split into fixed-size blocks (default 32MB) for distribution across DataNodes.
- **Data Replication**: Implements a round-robin (n, n+1) block assignment strategy to ensure each block is replicated across multiple DataNodes for fault tolerance.
- **Persistent Metadata & Logs**: Utilizes Docker volumes to persist NameNode metadata and logs, ensuring state is not lost on restart.
- **Concurrent Client**: A multi-threaded client capable of uploading multiple files simultaneously.
- **Actual Block Storage**: DataNodes receive and store file blocks as .dat files on their filesystem.
- **Docker Network Communication**: Client communicates with NameNode and DataNodes within Docker network.
- **Base64 Block Transfer**: File blocks are encoded in base64 and transferred via JSON over HTTP.

## Quick Start

### 1. Build and Run the System

First, build the Docker images and start the services in detached mode. This will start one NameNode and one DataNode by default.

```bash
docker-compose up --build -d
```

### 2. Scale DataNodes

You can easily scale the number of DataNodes to simulate a larger cluster.

```bash
# Scale up to 3 DataNodes
docker-compose up --scale datanode=3 -d
```

### 3. Upload Files with the Client

Run the client to upload test files located in the `client_testfiles` directory.

**Option 1: Run client inside Docker network (Recommended)**

```bash
# Start the cluster with multiple DataNodes
docker-compose up --scale datanode=3 -d

# Run client inside Docker network
docker-compose run --rm client
```

**Option 2: Run client locally**

```bash
# Update namenode_url to "http://127.0.0.1:9870" in Client/client.py
python Client/client.py
```

The client will display the block assignments for each uploaded file, including the DataNode IDs where each block is replicated. The client now actually sends the file blocks to the assigned DataNodes for storage.

## Configuration

You can customize the system's behavior through environment variables and client settings.

### Environment Variables

These variables are set in the `docker-compose.yml` file for the `namenode` service:

- `REPLICATION_FACTOR`: The number of DataNodes each block should be replicated to. Default is `2`.
- `BLOCK_SIZE_BYTES`: The size of each file block in bytes. Default is `33554432` (32MB).

To change them, simply edit the `environment` section in `docker-compose.yml` and rebuild the containers.

### Client Upload Directory

The client script is organized in the `Client/` directory and configured to look for files to upload in a directory named `client_testfiles` by default. Place any `.txt` or `.pdf` files you wish to upload into this folder before running the client.

## Verifying Block Storage

After uploading files, you can verify that blocks are actually stored on the DataNodes:

```bash
# Check blocks stored on DataNode 1
docker exec haha-dope-datanode-1 ls -la /usr/local/app/data/*/

# Check blocks stored on DataNode 2
docker exec haha-dope-datanode-2 ls -la /usr/local/app/data/*/

# Check a specific DataNode directory for .dat files
docker exec haha-dope-datanode-1 ls -la /usr/local/app/data/[datanode-id]/
```

You should see `.dat` files named with block IDs, like:

```
-rw-r--r-- 1 root root 33554432 Aug 11 07:52 block_test_txt_0000_6fa85c9f.dat
-rw-r--r-- 1 root root 12582912 Aug 11 07:52 block_test2_txt_0000_39d72e11.dat
```

## Viewing Logs

You can monitor the real-time activity of the NameNode and DataNodes.

```bash
# View logs from all services
docker-compose logs -f

# View logs from only the NameNode
docker-compose logs -f namenode

# View logs from a specific DataNode instance
docker-compose logs -f datanode-1
```

## Persistent Storage and Metadata

The system uses Docker volumes to persist critical data across container restarts. This is crucial for the NameNode to maintain the file system's state.

- **`namenode_data`**: Stores the NameNode's metadata in `metadata.json`.
- **`namenode_logs`**: Stores the general `namenode.log`.
- **`namenode_block_logs`**: Stores the `blocks.log` for block management events.
- **`datanode_data`**: Mount point for DataNodes to store file blocks as .dat files.

### Metadata Format

The `metadata.json` file is the brain of the NameNode. It stores the entire state of the file system in a JSON format, allowing the NameNode to recover its state after a restart.

Here is an example of its structure:

```json
{
  "last_updated": "2025-08-10T12:00:00.123456",
  "active_datanodes": {
    "fdf585333e7e": "2025-08-10T11:59:59.543210",
    "b1604c5e3d29": "2025-08-10T11:59:58.987654"
  },
  "file_metadata": {
    "client_testfiles/test.txt": {
      "size": 73400320,
      "blocks": ["block_test_txt_0000_a6bc20dc", "block_test_txt_0001_c267b2be"]
    }
  },
  "block_assignments": {
    "block_test_txt_0000_a6bc20dc": ["fdf585333e7e", "b1604c5e3d29"],
    "block_test_txt_0001_c267b2be": ["b1604c5e3d29", "fdf585333e7e"]
  }
}
```

### Accessing Persistent Data

To inspect the log files or metadata stored in the persistent volumes:

```bash
# Inspect the main metadata file
docker run --rm -it -v haha-dope_namenode_data:/data alpine cat /data/metadata.json

# Inspect namenode.log
docker run --rm -it -v haha-dope_namenode_logs:/logs alpine cat /logs/namenode.log

# Inspect blocks.log
docker run --rm -it -v haha-dope_namenode_block_logs:/logs alpine cat /logs/blocks.log
```

## Stopping the System

```bash
# Stop all running services
docker-compose down

# Stop services AND remove all persistent data (logs, metadata)
docker-compose down -v
```

## Next Steps

- [ ] **File Retrieval**: Build the client and NameNode logic to read/download files.
- [ ] **Fault Tolerance**: Implement re-replication of blocks when a DataNode goes offline.
- [ ] **Advanced Health Checks**: Add more detailed health reporting from DataNodes (e.g., disk space).
