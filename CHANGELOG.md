# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.1.0] - 2026-10-21

### Added
- **Enterprise 5-Star UI Redesign:** Comprehensive visual overhaul with deep-space dark theme, glassmorphic cards, custom radial ambient glow, and micro-interactions.
- **Unified Design System (`frontend/styles.py`):** Centralized theme engine importing `Plus Jakarta Sans` and `JetBrains Mono`, custom metric cards with top gradient borders and lift-on-hover, custom pill tabs, and gradient primary buttons.
- **Top HUD Cluster Pulse Bar:** Real-time cluster health ribbon across views showing active invokers, allocatable GPUs, running trials, Redis broker latency, and storage fabrics status.
- **Branded Enterprise Sidebar:** Modernized dark sidebar with NeuralForge glowing brain badge, version chip, live cluster heartbeat indicator, categorized navigation, and operator user chip.
- **Enterprise Security Gateway Login:** Redesigned authentication portal with glassmorphism card, security badges, and instant demo pre-fill capabilities.

### Changed
- Bumped project version to `2.1.0` across backend, frontend, Docker Compose, and documentation.

## [2.0.0] - 2026-10-21

### Added
- **Optuna Sweeps & Multi-Trial Aggregator:** Added `GET /api/v1/tasks/sweeps` and `POST /api/v1/tasks/sweeps/{sweep_name}/cancel` to aggregate trials by hyperparameter sweep, monitor global convergence (mAP50 / Fitness), and cancel active trials in batch.
- **Cluster Docker/K8s Image Synchronization & Broadcast Pull:** Added `GET /api/v1/cluster/images/status` and `POST /api/v1/cluster/images/broadcast-pull` with node-by-node image digest inspection and 1-click broadcast pull across all invoker workers, strictly excluding the NAS manager (`celery@NAS_Train_service`).
- **Dataset Pre-Flight Check & Samba Auto-Discovery:** Added `GET /api/v1/cluster/datasets/inspect`, `POST /api/v1/cluster/datasets/validate`, and `GET /api/v1/cluster/datasets/available` validating `data.yaml`, class count (`nc`), and split images (`train/`, `val/`) before dispatch.
- **Dead Letter Queue (DLQ) & Quarantine Management:** Added `GET /api/v1/tasks/quarantine`, `POST /api/v1/tasks/quarantine/{task_id}/retry`, and `DELETE /api/v1/tasks/quarantine/{task_id}` to isolate repeated failures (CUDA device-side asserts, NaN loss, OOM) and protect worker queues.
- **Day / Night Office Hours Automated Scheduler:** Added `GET /api/v1/cluster/scheduler/policy`, `POST /api/v1/cluster/scheduler/policy`, and `POST /api/v1/cluster/scheduler/apply-policy` to configure quiet profiles (25% GPU) during office hours (09:00-18:30) and maximum uncapped performance (90% GPU) at night and weekends.
- **Diagnostic Support Bundle Exporter:** Added `GET /api/v1/cluster/support-bundle` delivering a unified JSON diagnostic black box snapshot containing node conditions, active tasks, DLQ entries, audit trails, and system telemetry.
- **Rich Webhook Embed Notifications:** Added `POST /api/v1/cluster/webhook/test-rich` supporting Discord/Slack structured embed templates for study completion, pod eviction, and queue stalls.

### Changed
- Bumped project version to `2.0.0` across backend, frontend, Docker Compose, and documentation.

## [1.9.0] - 2026-10-21

### Added
- **Kubernetes Pod Lifecycle & Event Streamer:** Added `GET /api/v1/tasks/{study_id}/k8s-events` endpoint and UI events table displaying real-time Pod lifecycle events (`Scheduled`, `Pulled`, `Created`, `Started`, `OOMKilled`, `CrashLoopBackOff`) directly in active training views.
- **1-Click K8s Pod Eviction / Termination:** Added `POST /api/v1/tasks/{study_id}/kill-pod` endpoint with interactive UI button `💥 Desalojar Pod K8s` to immediately evict stuck or frozen training pods (`gracePeriodSeconds: 0`).
- **Cluster-Wide Stale K8s Pod Purge:** Added `POST /api/v1/cluster/k8s/purge-stale-pods` endpoint and UI maintenance button to purge pods in `Failed`, `Evicted`, or `Terminating` states, freeing GPU allocations and hostPath directory locks.
- **K8s Node Conditions Monitor:** Implemented per-node health tracking for Kubernetes pressure taints (`DiskPressure`, `MemoryPressure`, `PIDPressure`, `Ready`) to prevent sudden training pod evictions.
- **NVIDIA Device Plugin K8s Telemetry:** Visualized `nvidia.com/gpu` Allocatable vs Capacity metrics per node, with alerts for offline or degraded device plugins.
- **Dynamic PyTorch Shared Memory Allocator (`/dev/shm`):** Added `shm_size_gb` setting to node resource controls and schemas to properly size `emptyDir` memory limits and eliminate PyTorch DataLoader bus errors.
- **Dozzle K8s Web UI Deep Links:** Embedded direct links to live node-level and pod-level Dozzle streams (`http://{worker_ip}:8888`).

### Changed
- Bumped project version to `1.9.0` across backend, frontend, Docker Compose, and documentation.

## [1.8.0] - 2026-10-21

### Added
- **Clean & Intelligent Celery Queue Architecture:** Overhauled waitlist inspection with 5 human-readable KPI metric cards (`wyolo_gpu_queue`, `gpus_high`, `gpus_low`, Node-Targeted, Backlog ETA), suppressing technical queues (`managers`, `*.pidbox`) and empty node queues.
- **Task Re-router & Re-queue:** Added `POST /api/v1/tasks/queues/{task_id}/reassign` enabling instant reassignment of tasks stuck in private worker node queues directly to the shared public pool (`wyolo_gpu_queue`) or another node.
- **Backlog Clearance Estimator & Queue Jam Alert:** Real-time computation of backlog clearance duration based on active worker throughput, paired with proactive detection of queue stalls when tasks are waiting while nodes are paused/offline, including a 1-click "▶️ Reanudar Todos los Nodos" button.
- **Remote Invoker Operations:** Added endpoints `POST /api/v1/invokers/{worker_ip}/restart-service` and `POST /api/v1/invokers/{worker_ip}/prune-docker` with interactive UI controls for remote Celery daemon reboot and container disk space reclamation.
- **Live NVML GPU Telemetry:** Added GPU temperature (°C), live power consumption (Watts vs TDP), and CUDA compute utilization (%) to physical hardware cards with thermal alert badges.
- **1-Click Cluster Smoke Test:** Added `POST /api/v1/cluster/smoke-test` and Operations Center readiness matrix validating Samba CIFS mounts, MinIO S3 accessibility, and GPU availability across all online nodes.
- **Author Waitlist Breakdown & Filtering:** Aggregated pending tasks by submitting researcher with interactive filtering controls.

### Changed
- Bumped project version to `1.8.0` across backend, frontend, Docker Compose, and documentation.

## [1.7.0] - 2026-10-21

### Added
- **Live Task Log Streaming:** Added `/api/v1/tasks/{study_id}/logs` endpoint and UI log stream viewers for both active runs and historical studies, eliminating the need to SSH into worker nodes to inspect executor output.
- **GPU Process & Zombie Leak Monitor:** Added `/api/v1/invokers/{worker_ip}/processes` and `/api/v1/invokers/{worker_ip}/kill-process/{pid}` with automated detection of compute processes retaining GPU VRAM >24h without active training, including 1-click administrative termination.
- **Celery Queue Manager & Priority Switcher:** Added `/api/v1/tasks/queues`, `/promote`, and `/delete` endpoints with UI queue management cards allowing inspection and priority promotion of pending jobs across `gpus_high`, `gpus_medium`, and `gpus_low`.
- **Epoch-Level Granular Telemetry:** Extracted epoch-level progress (`epoch`, `total_epochs`, `loss`, `top1`, `eta_seconds`) to render live progress bars at single-epoch resolution.
- **Post-Mortem Root Cause Diagnostics:** Added `/api/v1/tasks/{study_id}/diagnostics` with pattern matching for CUDA OOM, Samba dataset mount failures, and container abnormal exits (code 1), accompanied by remediation guides.
- **Orchestration Runtime Badges:** Detected and visualized `[☸️ Kubernetes (RKE2/K3s)]` vs `[🐳 Docker Standalone]` nodes in inventory cards.
- **Tasks View Reconnection:** Reconnected and modernized `tasks_view.py` as `📋 Tasks & Queues Monitor` in `app.py` sidebar navigation.

### Changed
- Bumped project version to `1.7.0` across backend and frontend packages.

## [1.6.0] - 2026-10-07

### Changed
- Split the monolith into two WPipe microservices: `api/` (FastAPI) and `ui/` (Streamlit), each with its own `Dockerfile`, `requirements.txt` and WPipe orchestrator (`main.py`, `dto/`, `states/`).
- Centralized the service version in `backend.__version__` and `frontend.__version__`.
- Test suites split into `tests/api` and `tests/ui`, executed inside Docker.

### Added
- API startup pipeline: `LoadApiSettings` -> `CheckRedisConnection` -> `SeedAdminUser` -> `ServeApi`.
- UI startup pipeline: `LoadUiSettings` -> `WaitForApi` -> `LaunchStreamlit`.
- `docker-compose.yml` with healthchecks, private network and ordered startup.
- `Makefile` (setup, build, up, down, logs, test, coverage, push, dev), `.dockerignore` and `control_host.env.example`.
- Docker Hub images `wisrovi/train_service:cluster_admin_api_v1.6.0` and `wisrovi/train_service:cluster_admin_ui_v1.6.0`.

### Removed
- Root-level single-image `Dockerfile` and `requirements.txt` (replaced by per-service files).

## [1.5.1] - 2026-10-07

### Changed
- Translated the entire user interface (all 10 views, login, navigation, metrics, tables, buttons, notifications and exported reports) into professional English.
- Translated backend messages surfaced in the UI (watchdog alerts, smart dispatcher reasons, node diagnostics, FinOps audit entries, webhook notifications) into English.
- History filters now accept the `All` sentinel while remaining backward compatible with `Todos`.

### Fixed
- The `URGENT` dispatch priority label now sends `URGENT` to the API instead of the unrecognized `URGENTE` value.

## [1.5.0] - 2026-10-07

### Added
- Rebranded and reorganized the suite as **NeuralForge Cluster Admin** implementing Single Responsibility Principle across 10 dedicated operational views.
- Deep Storage & Volume Inspector (`/cluster/storage/inspect`) auditing shared Samba CIFS dataset volumes, MinIO S3 bucket quotas, and dynamic I/O latency metrics.
- FinOps & Energy Management (`/cluster/finops`, `/cluster/finops/rate`) with real-time electricity expense tracking in EUR by GPU model, configurable tariffs, and Green AI carbon certificates.
- Administrative Security & Audit Logging (`/cluster/audit/logs`) establishing an immutable Redis audit trail for limit adjustments, node state changes, dispatches, and operator sessions with CSV export.
- Cluster Capabilities & Scientific Catalog (`/cluster/capabilities`) providing governance for the 12 post-training R&D modules (Grad-CAM, Adversarial Attacks, Uncertainty Quantification, UMAP) mapped to peer-reviewed paper submissions.
- Dockerized unit test suite passing 100% with 77% total code coverage.

## [1.4.0] - 2026-10-07

### Added
- Deep node connectivity diagnostics (`/invokers/{worker_ip}/diagnose`) with TCP socket probing to SSH port 22 and live Celery inspection.
- Green AI energy monitoring (`/cluster/green-ai`) tracking cumulative kWh, CO2e emissions based on GPU TDP, equivalent tree offsets, and img/W efficiency.
- Task priority scheduling (`URGENT`, `NORMAL`, `BATCH`) in the smart dispatcher and Celery task payload metadata.
- Proactive watchdog scanner (`/cluster/watchdog/check-and-alert`) with instant webhook alerts to Discord, Slack and Telegram upon critical failures.
- Head-to-Head study comparison (`/tasks/compare`) in history view contrasting architectures, epochs, batch sizes, and accuracy metrics.
- 1-Click Study Reproducibility manifest (`/tasks/{study_id}/reproducibility`) generating exact `docker run` commands, configuration YAMLs and SHA256 hashes.
- Preloaded seamless authentication flow for immediate operator access.
- Expanded dockerized unit test suite reaching 75% total code coverage and 100% test pass rate.

## [1.3.0] - 2026-10-07

### Added
- Modular 6-view navigation architecture decongesting the previous 4-tab interface (`Centro de Operaciones`, `Nodos Invoker`, `Despacho y Tareas`, `Historial y Optuna`, `Rendimiento de GPUs`, `Mantenimiento y Ajustes`).
- Smart Dispatcher (`/recommend-node`) with "Recomendar Mejor Nodo" automated selector optimizing VRAM balance and workload distribution.
- GPU Benchmarks and Throughput Leaderboard (`/gpu-benchmarks`) comparing empirical inference/training speeds and 100-epoch projections.
- Hourly and daily Workload Trends (`/trends`) visualized using interactive Vega/Altair charts detecting cluster peak hours.
- Cluster Housekeeping and Redis Purge (`/housekeeping/preview`, `/housekeeping/purge`) safely reclaiming memory from stale/failed studies.
- 1-Click Study Report Exporter generating formatted Markdown (`.md`) and flattened tabular CSV (`.csv`) downloads directly from history.
- Cyber / Operations Deck dark visual styling with monospace telemetry readouts and cyan borders.
- Full suite of dockerized tests achieving 100% pass rate and 72% overall code coverage.

## [1.2.0] - 2026-10-07

### Added
- Real-time Celery watchdog probe via `active_queues()` eliminating false positive zombie alerts.
- Dedicated storage health monitoring for Samba CIFS and MinIO S3 in the cluster overview.
- Comprehensive VRAM model database supporting RTX 3050 OEM, GTX 1650/1660, RTX 2000 series, and Enterprise GPUs (A2000, A4000, A5000, A6000).
- Server Rack Grid topology view with visual hardware utilization bars and cards.
- Advanced node filtering (All, Active Only, Paused Only, Draining) with GPU model and minimum VRAM dropdowns.
- Batch action controls (`Pause Visible 4h`, `Resume Visible`) for filtered invoker sets.
- 1-Click Resource Presets (`Maximum 90%`, `Balanced 50%`, `Silent 25%`) on invoker cards.
- External webhook notifications supporting Discord, Slack, and Telegram with test dispatcher.
- Dynamic training duration estimator (ETA) and throughput calculator in the quick test launcher.

### Fixed
- Fixed watchdog zombie false positives caused by startup timestamp comparisons.
- Fixed `unknown` VRAM reporting on OEM GPUs and non-standard strings.
- Fixed duration estimator API parameter binding.

## [1.1.0] - 2026-10-07

### Added
- Initial smart VRAM resolution mapping for GeForce 30/40 series.
- Public queue state banner and graceful drain controls.
- Advanced search and filtering on tasks history table.
- 1-Click test training dispatcher for fast node verification.
- Optuna learning curves and trial progression plotting.
- Cluster health latency and offline node detection.

## [1.0.0] - 2026-10-07

### Added
- Initial release of NeuralForge Cluster Control platform.
- FastAPI REST backend with JWT authentication and Redis persistence.
- Automatic admin seeding (`wisrovi:wyoloservice`).
- Dynamic resource limits adjustment (`MAX_GPU`, RAM, CPU cores).
- Streamlit interactive frontend.
- Dockerized unit test suite and coverage reporting (`python:3.10-slim`).
