#!/bin/bash
# Calculates API and UI test coverage inside a python:3.10-slim Docker container.
set -e
echo "Calculating test coverage in Docker container for NeuralForge Cluster Admin..."
docker run --rm -v "$(pwd)":/src -w /src python:3.10-slim bash -c "\
  pip install -q -r api/requirements.txt -r ui/requirements.txt -r requirements-dev.txt && \
  PYTHONPATH=/src/api python -m pytest -p no:cacheprovider --cov=api --cov-report=term-missing tests/api && \
  PYTHONPATH=/src/ui python -m pytest -p no:cacheprovider --cov=ui/states --cov=ui/dto --cov=ui/main.py --cov-report=term-missing tests/ui"
