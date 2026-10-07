#!/bin/bash
# Runs the API and UI unit tests inside a python:3.10-slim Docker container.
set -e
echo "Running tests in Docker container for NeuralForge Cluster Admin..."
docker run --rm -v "$(pwd)":/src -w /src python:3.10-slim bash -c "\
  pip install -q -r api/requirements.txt -r ui/requirements.txt -r requirements-dev.txt && \
  PYTHONPATH=/src/api python -m pytest -p no:cacheprovider tests/api && \
  PYTHONPATH=/src/ui python -m pytest -p no:cacheprovider tests/ui"
