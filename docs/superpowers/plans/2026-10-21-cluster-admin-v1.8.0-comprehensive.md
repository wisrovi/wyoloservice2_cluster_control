# Implementation Plan - Cluster Admin v1.8.0 Comprehensive Enhancements

This plan details the full implementation of the cluster management suite v1.8.0 for `wyoloservice2_cluster_control`.

## Proposed Enhancements

1. **Queue Categorization & Noise Suppression:**
   - Filter out technical/internal Celery queues (`managers`, `reply.celery.pidbox`, etc.).
   - Hide/collapse empty invoker queues with 0 pending tasks.
   - Display prominent metric cards for:
     - ⚡ Global Queue (`wyolo_gpu_queue`)
     - 🔥 High Priority (`gpus_high`)
     - ⚖️ Medium Priority (`gpus_medium`)
     - 📦 Low Priority (`gpus_low`)
     - 🎯 Node-Targeted Queues (only nodes with pending tasks)
     - 📊 Total Backlog count.
   - Friendly and intuitive Spanish annotations in UI with clear explanations.

2. **Task Re-router & Re-queue:**
   - Endpoint: `POST /api/v1/tasks/queues/{task_id}/reassign` with payload `{"target_queue": str}`.
   - Allows moving a task stuck in a private queue (e.g. `192.168.1.72`) to the global public queue (`wyolo_gpu_queue`) or another node.
   - Button in UI waitlist table: "🔀 Mover a Cola Pública" and dropdown reassign.

3. **Backlog Clearance Estimator & Queue Jam Warning:**
   - Algorithm in backend and UI calculating total backlog clearance time based on active online invokers and average training duration.
   - Jam detector: triggers warning when tasks are waiting (>5) while online nodes are paused or drained, with a 1-click "▶️ Reanudar Todos los Nodos" action.

4. **Remote Invoker Operations (Service Restart & Docker Prune):**
   - Endpoints:
     - `POST /api/v1/invokers/{worker_ip}/restart-service`
     - `POST /api/v1/invokers/{worker_ip}/prune-docker`
   - UI buttons in `invokers_view.py` with confirmation dialogs.

5. **Live NVML GPU Telemetry (Watts, Temp, Compute Util):**
   - Schemas & backend repository enhanced to parse NVML fields (`temp_c`, `power_w`, `power_limit_w`, `utilization_gpu_pct`).
   - UI visual progress/meters in `invokers_view.py` (color-coded temperature: green < 70°C, orange 70-80°C, red > 80°C).

6. **Cluster Smoke Test (1-Click Health Validation):**
   - Endpoint: `POST /api/v1/cluster/smoke-test`
   - Dispatches a lightweight 1-epoch validation run to all online invoker nodes.
   - UI dashboard panel in Operations Center displaying the cluster readiness matrix.

7. **User / Author Quota Breakdown & Filters:**
   - Aggregates queued tasks by author (`Diego: X, William: Y, etc.`).
   - Dropdown filter by author in queue manager view.

---

## Step-by-Step Implementation Flow

1. Bump versions to `1.8.0` in `api/backend/__init__.py` and `ui/frontend/__init__.py`.
2. Add Schemas in `api/backend/schemas.py`.
3. Implement Repository methods in `api/backend/redis_client.py`.
4. Add router endpoints in `tasks_router.py`, `invokers_router.py`, and `overview_router.py`.
5. Add client methods in `ui/frontend/api_client.py`.
6. Update UI views:
   - `ui/frontend/views/dispatch_view.py`
   - `ui/frontend/views/tasks_view.py`
   - `ui/frontend/views/invokers_view.py`
   - `ui/frontend/views/overview_view.py`
7. Add unit tests in `tests/api/test_api.py`.
8. Verify test suite passes inside Docker container (`run_tests.sh` and `coverage.sh`).
9. Update `docker-compose.yml`, `CHANGELOG.md`, and `README.md`.
10. Commit one file per commit with category tags in English.
11. Push commits to `origin/main` and rebuild Docker Compose stack for ports 8501 and 8001.
