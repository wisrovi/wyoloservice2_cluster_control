#!/usr/bin/env bash
# Local development launcher (no Docker): runs the API and UI WPipe entrypoints.
set -e
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

export API_PORT="${API_PORT:-8001}"
export STREAMLIT_PORT="${STREAMLIT_PORT:-8501}"
export CLUSTER_API_URL="http://localhost:${API_PORT}"

echo "=== [CLUSTER ADMIN] Starting API on :${API_PORT} and UI on :${STREAMLIT_PORT} ==="
(cd api && python main.py) &
API_PID=$!
(cd ui && python main.py) &
UI_PID=$!

cleanup() {
    echo "=== [CLUSTER ADMIN] Shutting down services ==="
    kill -TERM "$API_PID" "$UI_PID" 2>/dev/null || true
    wait 2>/dev/null || true
    exit 0
}
trap cleanup SIGINT SIGTERM
wait
