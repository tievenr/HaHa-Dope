# HaHa-Dope

A distributed file system simulation inspired by Hadoop HDFS, built with Python, FastAPI, and Docker. This project demonstrates core concepts of distributed storage including block-based file splitting, data replication, metadata management, and fault tolerance.

## What Is This?

HaHa-Dope is a simplified implementation of a distributed file system that mimics the behavior of Hadoop's HDFS. It's designed for learning and experimentation, showcasing how large files are broken into blocks, distributed across multiple storage nodes, and managed through a centralized coordinator.

## System Architecture

```
                        ┌─────────────────┐
                        │      User       │
                        │  (Has Files)    │
                        └─────────┬───────┘
                                  │ Files to Upload
                                  │ (.txt, .pdf, etc.)
                                  ▼
                        ┌─────────────────┐
                        │     Client      │
                        │  (Upload Tool)  │
                        └─────────┬───────┘
                                  │ HTTP Requests
                                  │ (Get Block Assignments)
                                  ▼
                        ┌─────────────────┐
                        │    NameNode     │
                        │   (Metadata)    │
                        │                 │
                        │ • File Registry │
                        │ • Block Mapping │
                        │ • Node Health   │
                        └─────────┬───────┘
                                  │ Heartbeats &
                                  │ Health Monitoring
                     ┌────────────┼────────────┐
                     ▼            ▼            ▼
            ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
            │  DataNode1  │ │  DataNode2  │ │  DataNode3  │
            │             │ │             │ │    ...      │
            │ • Block     │ │ • Block     │ │ • Block     │
            │   Storage   │ │   Storage   │ │   Storage   │
            │ • Heartbeat │ │ • Heartbeat │ │ • Heartbeat │
            └─────┬───────┘ └─────┬───────┘ └─────┬───────┘
                  ▲               ▲               ▲
                  │               │               │
                  └───────────────┼───────────────┘
                          Direct Block Upload
                            (From Client)
```

### Components Overview

- **NameNode**: The central coordinator that manages file system metadata, tracks block locations, and monitors DataNode health. It doesn't store actual file data—only the "map" of where everything is located.

- **DataNode(s)**: Worker nodes that store the actual file blocks as `.dat` files on their filesystem. They send periodic heartbeats to the NameNode and can be scaled horizontally.

- **Client**: A command-line utility that uploads files to the system. It communicates with the NameNode to get block assignments, then sends the actual data blocks to the designated DataNodes.

## Key Features

- **RESTful API**: Built with FastAPI for modern, fast HTTP communication
- **Horizontal Scaling**: Add more DataNodes with a simple Docker Compose command
- **Block-Based Storage**: Files split into 32MB blocks for efficient distribution
- **Data Replication**: Round-robin (n, n+1) strategy ensures fault tolerance
- **Persistent State**: Docker volumes preserve metadata and logs across restarts
- **Concurrent Operations**: Multi-threaded client handles simultaneous uploads
- **Base64 Transfer**: Secure block transfer via JSON over HTTP
- **Real-time Monitoring**: Live heartbeat system tracks node health

## Quick Start Guide

Ready to try it out? Follow these steps to get your distributed file system running in minutes!

### Step 1: Launch the System

Start with the basic setup (1 NameNode + 1 DataNode):

```bash
docker-compose up --build -d
```

### Step 2: Scale Your Cluster

```bash
# Add more DataNodes for a bigger cluster
docker-compose up --scale datanode=3 -d
```

### Step 3: Upload Some Files

It's distributing time I said and distributed all over the datanodes

**Run Client in Docker**

```bash
# Start cluster with multiple nodes
docker-compose up --scale datanode=3 -d

# Upload files using the containerized client
docker-compose run --rm client
```

The client will show you exactly where each file block gets stored across your DataNodes!

## Configuration Options

Customize your distributed file system to fit your needs!

### Environment Variables

Edit these in your `docker-compose.yml` under the `namenode` service:

| Variable             | Default    | Description                         |
| -------------------- | ---------- | ----------------------------------- |
| `REPLICATION_FACTOR` | `2`        | How many DataNodes store each block |
| `BLOCK_SIZE_BYTES`   | `33554432` | Size of each block (32MB)           |

### Client Settings

- **Upload Directory**: Place files in `client_testfiles/` (supports `.txt` and `.pdf`)
- **Supported Formats**: Text files, PDFs, and other binary formats
- **Concurrent Uploads**: Client automatically handles multiple files in parallel (it is limited to 5 concurrent uploads)

## Monitoring & Verification

### Check Where Your Blocks Are Stored

So you can replace the datanode name with the ones you get when you run docker-compose ps. Here are some examples below

```bash
# View blocks on DataNode 1
docker exec haha-dope-datanode-1 ls -la /usr/local/app/data/*/

# View blocks on DataNode 2
docker exec haha-dope-datanode-2 ls -la /usr/local/app/data/*/

# Inspect specific DataNode storage
docker exec haha-dope-datanode-1 ls -la /usr/local/app/data/[datanode-id]/
```

You'll see actual `.dat` files with your block data:

```
-rw-r--r-- 1 root root 33554432 Aug 11 07:52 block_test_txt_0000_6fa85c9f.dat
-rw-r--r-- 1 root root 12582912 Aug 11 07:52 block_test2_txt_0000_39d72e11.dat
```

### Watch the System in Real-Time

Monitor live activity across your cluster:

```bash
# All services
docker-compose logs -f

# Just the NameNode
docker-compose logs -f namenode

# Specific DataNode
docker-compose logs -f datanode-1
```

## Understanding the Storage System

### How Data Persists

HaHa-Dope uses Docker volumes to keep your data safe across container restarts:

| Volume                | Purpose                                     |
| --------------------- | ------------------------------------------- |
| `namenode_data`       | Stores `metadata.json` (the system's brain) |
| `namenode_logs`       | General NameNode activity logs              |
| `namenode_block_logs` | Block management event logs                 |
| `datanode_data`       | Actual file blocks as `.dat` files          |

It can reset the namenode state by updating the state/env variables to the ones stored metadata volume.

### The Metadata Brain

The `metadata.json` file is where all the magic happens. Here's what it looks like:

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

### Inspect Persistent Data

Want to peek under the hood?

```bash
# Check the metadata
docker run --rm -it -v haha-dope_namenode_data:/data alpine cat /data/metadata.json

# Read the main log
docker run --rm -it -v haha-dope_namenode_logs:/logs alpine cat /logs/namenode.log

# Check block operations
docker run --rm -it -v haha-dope_namenode_block_logs:/logs alpine cat /logs/blocks.log
```

## Stopping the System

```bash
# Stop services (keeps your data)
docker-compose down

# Nuclear option: Stop AND delete all data
docker-compose down -v
```

You can also use the cleanup scripts `docker-cleanup.ps1` or `docker-cleanup.sh` to clear everything

## Work yet to be done:

Here are some features I am yet to build(probably never) but they sort of complete the dfs ?

- [ ] **File Retrieval**: Download files from the distributed storage
- [ ] **Fault Tolerance**: Auto-replicate blocks when DataNodes fail

---

**Happy Distributing!** If you found this project cool, give it a star and feel free to contribute. I'd love to finally merge PR's
