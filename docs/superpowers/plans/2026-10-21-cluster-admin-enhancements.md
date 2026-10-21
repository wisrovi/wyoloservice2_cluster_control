# NeuralForge Cluster Admin UI & API Enhancements Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement 7 key administrative enhancements in `wyoloservice2_cluster_control` to transform the Streamlit UI and FastAPI backend into a comprehensive, real-time cluster management center.

**Architecture:** Extend FastAPI backend (`ClusterRepository` and routers) with endpoints for live log retrieval, GPU process/zombie tracking, Celery queue inspection and prioritization, epoch-level telemetry, failure diagnostics, and orchestration runtime badges. Update the Streamlit frontend views (`invokers_view.py`, `dispatch_view.py`, `tasks_view.py`, `app.py`) to render real-time telemetry, interactive actions, and reconnect the orphaned `tasks_view.py`.

**Tech Stack:** Python 3.10, FastAPI, Streamlit, Redis, WPipe, Pytest.

---

### Task 1: Version Bump & Schemas Definition
**Files:**
- Modify: `api/backend/__init__.py`
- Modify: `ui/frontend/__init__.py`
- Modify: `api/backend/schemas.py`
- Modify: `ui/frontend/dto/` (if applicable)
- Test: `tests/api/test_startup_pipeline.py`, `tests/ui/test_startup_pipeline.py`

- [ ] Bump version from `1.6.0` to `1.7.0` in `api/backend/__init__.py` and `ui/frontend/__init__.py`.
- [ ] Add Pydantic schemas in `api/backend/schemas.py`:
  - `GpuProcessInfo` (pid, name, vram_used_mb, elapsed, is_zombie, zombie_reason)
  - `NodeGpuProcessesResponse` (worker_ip, hostname, gpu_model, processes)
  - `KillProcessResponse` (status, message, pid)
  - `QueuedTaskInfo` (task_id, study_name, author, model, dataset, priority, queue_name, queued_at)
  - `QueueStatusResponse` (queues, total_queued, tasks)
  - `PromoteTaskRequest` (new_priority)
  - `TaskDiagnosticsResponse` (study_id, status, error, root_cause, suggested_action, timestamp)
  - `TaskLogsResponse` (study_id, worker_ip, source, logs)
- [ ] Verify schemas with `pytest tests/api/test_startup_pipeline.py tests/ui/test_startup_pipeline.py`.

---

### Task 2: Backend Repository Implementation (`redis_client.py`)
**Files:**
- Modify: `api/backend/redis_client.py`
- Test: `tests/api/test_api.py`

- [ ] Implement `get_node_gpu_processes(worker_ip)` in `ClusterRepository`:
  - Extract GPU processes from telemetry, detect zombie state (>24h idle VRAM).
- [ ] Implement `kill_node_gpu_process(worker_ip, pid)` in `ClusterRepository`.
- [ ] Implement `get_celery_queues()` in `ClusterRepository`:
  - Inspect `gpus_high`, `gpus_medium`, `gpus_low`, parse queued task headers/body.
- [ ] Implement `promote_celery_task(task_id, target_queue)` in `ClusterRepository`:
  - Move queued task between Redis queue lists.
- [ ] Implement `delete_celery_task(task_id)` in `ClusterRepository`.
- [ ] Implement `get_task_logs(study_id)` in `ClusterRepository`:
  - Read from Redis task logs, stdout streams, or active trial metadata.
- [ ] Implement `get_task_diagnostics(study_id)` in `ClusterRepository`:
  - Analyze `study:{id}:error` and return root cause (OOM, missing files, config errors).
- [ ] Enhance `list_active_tasks()` with epoch-level telemetry (`epoch_progress`).
- [ ] Enhance `list_invokers()` with `orchestration_runtime` ("Kubernetes (RKE2/K3s)" vs "Docker Standalone").
- [ ] Add unit tests in `tests/api/test_api.py` for new repository methods.

---

### Task 3: Backend Routers Integration
**Files:**
- Modify: `api/backend/routers/tasks_router.py`
- Modify: `api/backend/routers/invokers_router.py`
- Test: `tests/api/test_api.py`

- [ ] Add endpoints to `tasks_router.py`:
  - `GET /api/v1/tasks/queues` -> `get_celery_queues`
  - `POST /api/v1/tasks/queues/{task_id}/promote` -> `promote_celery_task`
  - `DELETE /api/v1/tasks/queues/{task_id}` -> `delete_celery_task`
  - `GET /api/v1/tasks/{study_id}/logs` -> `get_task_logs`
  - `GET /api/v1/tasks/{study_id}/diagnostics` -> `get_task_diagnostics`
- [ ] Add endpoints to `invokers_router.py`:
  - `GET /api/v1/invokers/{worker_ip}/processes` -> `get_node_gpu_processes`
  - `POST /api/v1/invokers/{worker_ip}/kill-process/{pid}` -> `kill_node_gpu_process`
- [ ] Write API tests in `tests/api/test_api.py` verifying each new route with TestClient.

---

### Task 4: Frontend API Client Extension (`api_client.py`)
**Files:**
- Modify: `ui/frontend/api_client.py`

- [ ] Add `get_node_gpu_processes(token, worker_ip)` method.
- [ ] Add `kill_node_gpu_process(token, worker_ip, pid)` method.
- [ ] Add `get_celery_queues(token)` method.
- [ ] Add `promote_celery_task(token, task_id, new_priority)` method.
- [ ] Add `delete_celery_task(token, task_id)` method.
- [ ] Add `get_task_logs(token, study_id)` method.
- [ ] Add `get_task_diagnostics(token, study_id)` method.

---

### Task 5: UI Views Implementation
**Files:**
- Modify: `ui/frontend/views/invokers_view.py`
- Modify: `ui/frontend/views/dispatch_view.py`
- Modify: `ui/frontend/views/tasks_view.py`
- Modify: `ui/frontend/views/history_view.py`
- Modify: `ui/frontend/app.py`

- [ ] In `invokers_view.py`:
  - Display `[☸️ Kubernetes (RKE2/K3s)]` or `[🐳 Docker Standalone]` badge per node.
  - Add collapsible expander "🖥️ GPU Processes & Zombie Leak Detection (`nvidia-smi`)".
  - Render process table with PID, process name, VRAM used, runtime, and zombie warning badge.
  - Add "Kill Process" button with confirmation.
- [ ] In `dispatch_view.py`:
  - Add "🚦 Celery Queues & Waitlist" tab/expander showing waiting jobs with "Promote to Urgent" and "Cancel" buttons.
  - In "Active Tasks", display epoch-level progress bar (`Epoch 101/250 | Loss: 0.2098 | Top-1: 88.2%`).
  - Add "📜 Live Logs" expander per active task with auto-refresh toggle.
  - Add "🩺 Diagnostics" expander for failed tasks showing error root cause and fix suggestions.
- [ ] In `tasks_view.py`:
  - Reconnect and modernize with the new queue manager, live log viewer, and diagnostic panel.
- [ ] In `app.py`:
  - Add `🚀 Training & Task Monitoring` to sidebar navigation pointing to `render_tasks(api_client, token)`.
  - Update version badge.

---

### Task 6: Testing, Documentation & Validation
**Files:**
- Modify: `wyoloservice2_cluster_control/README.md`
- Modify: `wyoloservice2_cluster_control/CHANGELOG.md`
- Run: `bash run_tests.sh` and `bash coverage.sh`

- [ ] Run full test suite in Docker container (`bash run_tests.sh`) and verify 100% pass rate.
- [ ] Run test coverage (`bash coverage.sh`) and verify coverage metrics.
- [ ] Update `CHANGELOG.md` with version v1.7.0 features.
- [ ] Update `README.md` with the new features, architecture changes, and key libraries.
- [ ] Run `codegraph-sync` post-edit.
- [ ] Perform git commit per modified file according to git rules.
