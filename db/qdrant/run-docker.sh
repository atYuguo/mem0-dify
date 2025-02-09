#!/bin/bash

# 清除可能存在的环境变量
unset NETWORK
unset MEM0_API_AUTH_KEY

# 加载当前目录的环境变量
if [ -f ../../.env ]; then
    # 使用 source 命令来加载环境变量，确保在当前shell中生效
    set -a
    source ../../.env
    set +a
else
    echo "Error: .env file not found in current directory"
    exit 1
fi

# 检查必要的环境变量是否存在
if [ -z "$NETWORK" ] || [ -z "$MEM0_API_AUTH_KEY" ]; then
    echo "Error: Required environment variables are not set"
    echo "Please make sure NETWORK and MEM0_API_AUTH_KEY are defined in .env file"
    exit 1
fi

# 检查并创建 Docker 网络
if ! docker network inspect "$NETWORK" >/dev/null 2>&1; then
    echo "Creating Docker network: $NETWORK"
    docker network create "$NETWORK"
    if [ $? -eq 0 ]; then
        echo "Network created successfully"
    else
        echo "Failed to create network"
        exit 1
    fi
else
    echo "Network $NETWORK already exists"
fi

echo "Using configuration:"
echo "NETWORK: $NETWORK"
echo "API_KEY: ${VECTOR_STORE_DB_API_KEY:0:8}..." # 只显示API key的前8位

# By default, the Qdrant service listens on port 6333 for the REST API and dashboard, and on port 6334 for the gRPC API
docker run --name=mem0-qdrant \
    --restart=always \
    --network="$NETWORK" \
    -p 6333:6333 \
    -p 6334:6334 \
    -v ./data:/qdrant/storage \
    -v ./snapshots:/qdrant/snapshots \
    -e QDRANT__SERVICE__API_KEY="$VECTOR_STORE_DB_API_KEY" \
    qdrant/qdrant
