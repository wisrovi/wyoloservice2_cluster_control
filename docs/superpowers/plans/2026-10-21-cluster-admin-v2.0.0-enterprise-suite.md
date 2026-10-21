# Implementation Plan - Cluster Admin v2.0.0 Enterprise Management Suite

This plan details the full implementation of NeuralForge Cluster Admin v2.0.0, incorporating Optuna sweep orchestration, image broadcast pull matrix, dataset pre-flight check, dead letter queue (DLQ) quarantine, day/night automated scheduler, diagnostic support bundle export, and rich webhook alerts.

## Proposed Enhancements

1. **Optuna Sweep Aggregator & Multi-Trial Concurrency:**
   - Group active and historical trials by study sweep name.
   - Endpoint: `GET /api/v1/tasks/sweeps`
   - Endpoint: `POST /api/v1/tasks/sweeps/{sweep_name}/cancel`
   - UI: Sweep aggregator panel with convergence progress and batch sweep controls.

2. **Cluster Docker/K8s Image Synchronization & Broadcast Pull:**
   - Track local image versions / digest on all invokers.
   - Endpoint: `GET /api/v1/cluster/images/status`
   - Endpoint: `POST /api/v1/cluster/images/broadcast-pull` (triggers Celery `force_docker_pull`, excluding NAS manager).
   - UI: Image synchronization matrix with 1-click broadcast trigger and progress bars.

3. **Dataset Pre-Flight Check & Samba Auto-Discovery:**
   - Inspects shared dataset storage (`/examples` or Samba CIFS).
   - Validates class counts (`nc`), splits (`train/`, `val/`), and image counts.
   - Endpoint: `GET /api/v1/cluster/datasets/inspect`
   - Endpoint: `POST /api/v1/cluster/datasets/validate`
   - UI: Interactive dataset dropdown and pre-flight validation banner.

4. **Dead Letter Queue (DLQ) & Quarantine Management:**
   - Isolate repeated failures (e.g. fatal CUDA asserts, NaN loss, malformed yaml).
   - Endpoint: `GET /api/v1/tasks/quarantine`
   - Endpoint: `POST /api/v1/tasks/quarantine/{task_id}/retry`
   - Endpoint: `DELETE /api/v1/tasks/quarantine/{task_id}`
   - UI: Quarantine view in Tasks & Queues Monitor.

5. **Day / Night Office Hours Automated Scheduler:**
   - Define profiles: Office Hours (09:00-18:30) Quiet Mode on designated IPs vs Night/Weekend Maximum Performance.
   - Endpoint: `GET /api/v1/cluster/scheduler/policy`
   - Endpoint: `POST /api/v1/cluster/scheduler/policy`
   - Endpoint: `POST /api/v1/cluster/scheduler/apply-policy`
   - UI: Interactive schedule configuration card.

6. **Diagnostic Support Bundle Exporter (1-Click Black Box):**
   - Generates a full diagnostic JSON snapshot (invokers, K8s conditions, queues, logs, audit trail).
   - Endpoint: `GET /api/v1/cluster/support-bundle`
   - UI: Download button in Maintenance.

7. **Rich Webhook Notification Templates:**
   - Format Discord/Slack embeds for study completion, pod eviction, and queue stall.
   - Endpoint: `POST /api/v1/cluster/webhook/test-rich`

---

## Step-by-Step Implementation Flow

1. Bump versions to `2.0.0` in `api/backend/__init__.py` and `ui/frontend/__init__.py`.
2. Add Schemas in `api/backend/schemas.py`.
3. Implement Repository methods in `api/backend/redis_client.py`.
4. Add router endpoints in `tasks_router.py`, `overview_router.py`.
5. Add client methods in `ui/frontend/api_client.py`.
6. Update UI views:
   - `tasks_view.py`: Add Optuna Sweeps Tab and DLQ Quarantine Tab.
   - `dispatch_view.py`: Add Dataset Pre-Flight check selector.
   - `invokers_view.py`: Add Image Synchronization Matrix & Broadcast Pull button.
   - `overview_view.py` and `settings_view.py`: Add Schedule Policy card and Support Bundle exporter.
7. Add unit tests in `tests/api/test_api.py`.
8. Verify test suite passes inside Docker container (`run_tests.sh` and `coverage.sh`).
9. Update `docker-compose.yml`, `CHANGELOG.md`, and `README.md`.
10. Commit one file per commit with category tags in English.
11. Push commits to `origin/main` and rebuild Docker Compose stack for ports 8501 and 8001.
