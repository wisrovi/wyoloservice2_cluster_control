# Implementation Plan - Cluster Admin v1.9.0 Kubernetes Pod Management Suite

This plan details the full implementation of Kubernetes Pod management, node conditions, GPU device plugin telemetry, and pod lifecycle diagnostics for `wyoloservice2_cluster_control`.

## Proposed Enhancements

1. **Kubernetes Pod Lifecycle & Diagnostics:**
   - Track and display K8s pod phase and conditions (`Pending`, `Running`, `Succeeded`, `Failed`, `CrashLoopBackOff`, `ImagePullBackOff`, `OOMKilled`, `Evicted`).
   - Endpoint: `GET /api/v1/tasks/{study_id}/k8s-events` to inspect Kubernetes events for the executor pod.
   - Endpoint: `POST /api/v1/tasks/{study_id}/kill-pod` to trigger immediate Pod eviction/deletion.

2. **K8s Node Conditions & Pressure Monitor:**
   - Store and report Kubernetes node status conditions (`Ready`, `DiskPressure`, `MemoryPressure`, `PIDPressure`, `NetworkUnavailable`).
   - Display visual status badges in the invoker inventory cards.

3. **NVIDIA Device Plugin K8s Telemetry:**
   - Display `nvidia.com/gpu` Allocatable vs Capacity per node.
   - Healthcheck alert if a node is online in Celery but has 0 allocatable K8s GPUs.

4. **Dynamic PyTorch Shared Memory (`/dev/shm` sizeLimit) Allocator:**
   - Add `shm_size_gb` to `InvokerLimits` schema and UI slider (e.g. 2Gi to 64Gi).
   - Injected into Redis so `wyoloservice2_invoker` can size the `emptyDir: {medium: "Memory"}` volume properly.

5. **1-Click Stale K8s Pod Purge:**
   - Endpoint: `POST /api/v1/cluster/k8s/purge-stale-pods`.
   - UI Maintenance button to safely clear pods in `Failed`, `Evicted`, or `Terminating` states.

6. **Dozzle & Live K8s Stream Deep Integration:**
   - Direct link to Dozzle web UI (`http://{worker_ip}:8888`) from each active task and invoker card.

---

## Step-by-Step Implementation Flow

1. Bump versions to `1.9.0` in `api/backend/__init__.py` and `ui/frontend/__init__.py`.
2. Add Schemas in `api/backend/schemas.py`:
   - `K8sPodEvent`, `K8sPodEventsResponse`
   - `K8sNodeConditions`, `K8sGpuPluginStatus`
   - Update `InvokerLimits` with `shm_size_gb`
   - `K8sPurgeResponse`, `KillPodResponse`
3. Implement Repository methods in `api/backend/redis_client.py`:
   - `get_task_k8s_events(study_id)`
   - `kill_task_pod(study_id, user)`
   - `purge_stale_k8s_pods(user)`
   - Update `get_invoker` / `list_invokers` to include K8s node conditions and GPU device plugin status.
   - Support `shm_size_gb` in `set_invoker_limits`.
4. Add router endpoints:
   - `tasks_router.py`: `GET /tasks/{study_id}/k8s-events`, `POST /tasks/{study_id}/kill-pod`
   - `overview_router.py`: `POST /cluster/k8s/purge-stale-pods`
5. Add client methods in `ui/frontend/api_client.py`:
   - `get_task_k8s_events(token, study_id)`
   - `kill_task_pod(token, study_id)`
   - `purge_stale_k8s_pods(token)`
6. Update UI views:
   - `tasks_view.py` and `dispatch_view.py`: Add K8s Pod status badge, K8s Events expander, Dozzle link, and "🛑 Desalojar Pod K8s" button.
   - `invokers_view.py`: Add K8s Node Conditions banner (DiskPressure, MemoryPressure), NVIDIA Device Plugin status, and `/dev/shm` size slider.
   - `overview_view.py`: Add K8s Pod cleanup button and K8s node condition summary.
7. Add unit tests in `tests/api/test_api.py`.
8. Verify test suite passes inside Docker container (`run_tests.sh` and `coverage.sh`).
9. Update `docker-compose.yml`, `CHANGELOG.md`, and `README.md`.
10. Commit one file per commit with category tags in English.
11. Push commits to `origin/main` and rebuild Docker Compose stack for ports 8501 and 8001.
