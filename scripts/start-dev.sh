#!/usr/bin/env bash
echo "Starting Kogniq Local Development Environment..."
docker compose up -d
if [ $? -ne 0 ]; then
    echo "Failed to start containers. Please ensure Docker is running."
    exit 1
fi
echo "Containers started successfully."
