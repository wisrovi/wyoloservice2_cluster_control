#!/bin/bash
# Calculates test coverage inside a Docker container
echo "Calculating test coverage in Docker container for wyoloservice2_cluster_control..."
docker run --rm -v $(pwd):/app -w /app python:3.10-slim bash -c "pip install -q -r requirements.txt && pytest --cov=backend --cov-report=term-missing tests/"
