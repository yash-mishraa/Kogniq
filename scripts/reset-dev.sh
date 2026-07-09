#!/usr/bin/env bash
echo "Resetting Kogniq Local Development Environment..."
echo "WARNING: This will destroy all local data in containers."
read -p "Are you sure you want to continue? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]
then
    docker compose down -v
    echo "Containers and volumes removed. Run start-dev to initialize again."
fi
