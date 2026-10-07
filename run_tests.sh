#!/bin/bash
# Runs pytest inside a Docker container
echo "Running tests in Docker container for wyoloservice2_cluster_control..."
docker run --rm -v $(pwd):/app -w /app python:3.10-slim bash -c "pip install -q -r requirements.txt && pytest tests/"
