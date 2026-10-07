#!/usr/bin/env bash
set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

echo "=== [CLUSTER CONTROL] Starting wyoloservice2_cluster_control ==="
export PYTHONPATH="$DIR:${PYTHONPATH}"

# Default ports
API_PORT="${API_PORT:-8001}"
STREAMLIT_PORT="${STREAMLIT_PORT:-8501}"
export CLUSTER_API_URL="http://localhost:${API_PORT}"

echo "-> Launching FastAPI backend on port ${API_PORT}..."
uvicorn backend.app:app --host 0.0.0.0 --port "${API_PORT}" &
API_PID=$!

echo "-> Launching Streamlit frontend on port ${STREAMLIT_PORT}..."
streamlit run frontend/app.py --server.port "${STREAMLIT_PORT}" --server.address 0.0.0.0 --server.headless true &
STREAMLIT_PID=$!

cleanup() {
    echo "=== [CLUSTER CONTROL] Shutting down services ==="
    kill -TERM "$API_PID" 2>/dev/null || true
    kill -TERM "$STREAMLIT_PID" 2>/dev/null || true
    wait "$API_PID" 2>/dev/null || true
    wait "$STREAMLIT_PID" 2>/dev/null || true
    exit 0
}

trap cleanup SIGINT SIGTERM

echo "=== [CLUSTER CONTROL] Services are running! ==="
echo "Backend API:  http://localhost:${API_PORT}"
echo "Streamlit UI: http://localhost:${STREAMLIT_PORT}"
echo "Press Ctrl+C to terminate."

wait
