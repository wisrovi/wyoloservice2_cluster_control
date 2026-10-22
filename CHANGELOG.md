# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [3.1.1] - 2026-10-22

### Added
- **Multi-Task Computer Vision Architecture Selector in Smart Dispatcher (`dispatch.js`):**
  - **Vision Task Selector (CV Domain):**
    - 🎯 Object Detection (`detect`): YOLO11 (n/s/m/l/x), YOLOv10 (n/s/m/b/l/x), YOLOv9 (t/s/m/c/e), YOLOv8 (n/s/m/l/x), YOLOv5u (nu/su/mu/lu/xu).
    - ✂️ Instance Segmentation (`segment`): YOLO11-seg (n/s/m/l/x), YOLOv8-seg (n/s/m/l/x), YOLOv5u-seg (n/s/m).
    - 🏷️ Image Classification (`classify`): YOLO11-cls (n/s/m/l/x), YOLOv8-cls (n/s/m/l/x), YOLO26-cls (n/s).
    - 🤸 Pose Estimation (`pose`): YOLO11-pose (n/s/m/l/x), YOLOv8-pose (n/s/m/l/x).
    - 📐 Oriented Bounding Box (`obb`): YOLO11-obb (n/s/m/l/x), YOLOv8-obb (n/s/m/l/x).
    - 🧪 Custom Checkpoints (`custom`): Support for typing arbitrary `.pt` checkpoint file paths.
  - **Dynamic Task Synchronization:**
    - Switching vision task automatically switches default suggested dataset, resolution (`imgsz`), model list, task badge, and study naming pattern.
  - **Enhanced Hyperparameter Configuration:**
    - Batch size selector with AutoBatch (`-1`), 4, 8, 16, 32, 64, 128.
    - Image resolution selector (`imgsz`): 224, 384, 512, 640, 1024, 1280.
    - Training epochs expanded from `le=10` up to `le=1000` in backend schema and UI.
  - **Backend Intelligent Auto-Configuration:**
    - `QuickLaunchRequest` now accepts `task`, `imgsz`, and `batch_size`.
    - Auto-detection of task from model name if omitted, auto-assignment of fitness metrics (`metrics/mAP50(B)` for detect/obb, `metrics/mAP50(M)` for segment, `metrics/mAP50-95(P)` for pose, `metrics/accuracy_top1` for classification).
    - Duration estimator expanded to support all model families with task-dependent compute multipliers.

### Changed
- Bumped project version to `3.1.1` across backend, frontend, server, Docker Compose, and documentation.

## [3.1.0] - 2026-10-22

### Added
- **Complete Feature Suite & Live Telemetry Across All Workbench Views:**
  - **📈 Job History & Optuna Analytics Studio (`history.js`):**
    - Multi-field filters: search query, author dropdown, node dropdown, status filter, limit selector, and "👤 My studies only" checkbox.
    - Comprehensive Study Inspector Modal: Full metadata, Reproducibility Manifest (with 1-click Docker run and YAML copy buttons), Root Cause Diagnostics with suggested actions, and live execution logs.
    - Optuna Learning Curves: Responsive SVG fitness progression chart across trials, best value badge, and full iterations table.
    - Head-to-Head Comparison: Side-by-side matrix for comparing 2 to 5 studies.
    - Report Exporter: Instant JSON and Markdown report generation with browser download.
  - **🚀 Smart Workload Dispatcher & Launcher (`dispatch.js`):**
    - Pre-flight Dataset Checker: Validates dataset path against Samba CIFS, class counts, and train/val image split before dispatch.
    - AI Node Recommender: Evaluates cluster telemetry and selects the optimal invoker with score and rationale.
    - Dynamic Duration Estimator (ETA): Real-time calculation of estimated duration, image throughput (img/s), and suggested GPU.
    - Dynamic Target Node Dropdown: Populated from live API data.
    - Live Active Workloads Table: Trial progress bars, K8s Pod status, Dozzle links, and cancel buttons.
  - **🛠️ Cluster Administration & Operational Governance (`settings.js`):**
    - Bulk Limit Adjustment: Apply uniform MAX_GPU % and RAM quotas across all invoker nodes in one atomic operation.
    - Day/Night Automated Scheduler Policy: Configure office hours (quiet mode) vs night/weekend full throttle (95%), with "Apply Profile Now" trigger.
    - Diagnostic Support Bundle: 1-click generation and download of complete cluster JSON blackbox bundle.
    - Redis Housekeeping: Real-time memory in use counter and 1-click purge of stale failed/cancelled studies.
    - Webhooks & Watchdog: Save webhook, send test alert, test rich embed cards, and run proactive watchdog scan.
  - **🏆 GPU Benchmarks & Leaderboard (`benchmarks.js`):**
    - Dynamically bound to `/api/v1/cluster/gpu-benchmarks` with top throughput, fastest 100-epoch time, and deployed cluster nodes per GPU.
  - **🌿 FinOps & Green AI Governance (`finops.js`):**
    - Live power draw, accumulated cost, projected monthly cost, carbon footprint (CO2e), and interactive electricity rate update (€/kWh).
  - **🔬 Hardware Compute Matrix & R&D Catalog (`capabilities.js`):**
    - Catalog of the 12 official worker R&D post-train modules and CUDA architecture precision matrix.
  - **📁 Storage Infrastructure & MinIO S3 (`storage.js`):**
    - Dynamic Samba CIFS disk capacity and latency, MinIO S3 object buckets, and dataset validation.

### Changed
- Bumped project version to `3.1.0` across backend, frontend, server, Docker Compose, and documentation.

## [3.0.2] - 2026-10-22

### Added
- **Temporal & Perpetual Pause Dual Support:** Added comprehensive support for both pause modalities across backend and VSCode Workbench frontend:
  - **⏱️ Pausa Temporal:** Allows operators to pause task consumption on invokers for a specified duration (quick chips for 1h, 2h, 4h, 8h, 24h, plus custom float input).
  - **Auto-Expiration Engine:** Backend checks `pause_until` unix epoch timestamp on telemetry refresh and automatically restores Celery queue consumption once the interval elapses.
  - **⏹️ Pausa Perpetua / Indefinida:** Indefinite pause mode that disconnects public queues (`gpus_high`, `gpus_medium`, `gpus_low`, `wyolo_gpu_queue`) until explicit manual resumption.
  - **Interactive Pause Modal:** Intuitive modal overlay in `nodes.js` providing clear visual selection between temporal with duration selector and perpetual mode.
  - **Live Table Status & Real-Time Countdown:** Added human-readable badges (`⏱️ Pausa Temp (Xh Ym)`, `⏹️ Pausa Indef.`) and live countdown calculation in `nodes.js`.
  - **Batch Duration Controls:** Toolbar updated with `⏸️ Pause 4h (All)`, `⏹️ Pause Indef. (All)`, and `▶️ Resume All`.
- **Dockerized Unit Tests:** Added test coverage for temporal pause, perpetual pause, and node resumption in `tests/api/test_api.py`.

### Changed
- Bumped project version to `3.0.2` across backend, frontend, server, Docker Compose, and documentation.

## [3.0.1] - 2026-10-22

### Added
- **Complete Hardware Telemetry & GPU Allocation Restoration:** Restored full fidelity of real hardware telemetry across Operations Center (`overview.js`) and Nodes & Invokers (`nodes.js`):
  - **Live Active Workloads Table:** Fixed active workloads counter and mounted real-time active training trials table with study name, author, assigned node, model, dataset path, trial/epoch progress, and K8s pod name.
  - **Node Pause & Drain States:** Added prominent state badges (`🟢 Active`, `⏸️ Paused`, `🛡️ Draining`) and an interactive filter toolbar (`🔘 All`, `🟢 Active Only`, `⏸️ Paused Only`, `🛡️ Draining`) with 0ms client-side filtering.
  - **GPU Sharing vs Total Capacity:** Added dedicated compute allocation column displaying K8s allocated GPUs vs total GPU capacity and VRAM sharing cap (`MAX_GPU %`) with visual progress bar.
  - **VRAM & NVML Thermals:** Extracted real physical VRAM total, compute utilization percentage, and live power draw vs TDP with GPU temperature.
  - **RAM Limits & Host Memory:** Displayed container limit (`max_ram`) alongside host system total RAM and allocated CPU cores.
  - **Live GPU Processes & Zombie Monitor:** Added interactive modal (`🔍 Procs`) allowing real-time inspection of running GPU PIDs, process names, VRAM usage, and one-click termination (`🛑 Kill PID`).
  - **Batch Node Controls:** Added one-click `⏸️ Pause All` and `▶️ Resume All` operations.

### Changed
- Bumped project version to `3.0.1` across backend, frontend, server, and documentation.

## [3.0.0] - 2026-10-22

### Added
- **Streamlit Elimination & Static VSCode Workbench SPA:** Completely eliminated Streamlit from the frontend layer (`ui/`). Replaced with a high-performance, authentic Visual Studio Code Workbench Single Page Application (SPA) based on direct Reverse Engineering (REA) of the VSCode desktop application (`workbench.desktop.main.css`).
- **Zero-Latency Client Architecture:** The static SPA communicates directly with the FastAPI cluster control backend (`:8001`) with 0ms client-side latency, avoiding Python reruns, WebSocket overhead, and shadow DOM hacks.
- **Monaco Workbench Desktop DOM & CSS:** Faithful recreation of VSCode Dark+ desktop shell:
  - Fixed 35px TitleBar (`.part.titlebar`, `#181818`, bottom border `#2B2B2B`) with brand logo, authentic horizontal cascading menubar (**Archivo**, **Editar**, **Ver**, **Ir**, **Ejecutar**, **Terminal**, **Ayuda**), Command Center search pill (`Ctrl+P`), hardware status badges, and window controls.
  - Interactive multi-editor tabs strip (`.part.editor`, `#252526`) with tab close `✕`, active line indicator `#007ACC`, and quick actions.
  - Dynamic breadcrumbs trail (`.breadcrumbs`) reflecting the exact category and cluster file path.
  - 100% full-width editor viewport (`.part.content`) with all 11 cluster views rendered with high fidelity.
  - Collapsible bottom drawer (`.part.panel`) with tabs (`OUTPUT`, `TERMINAL`, `PROBLEMS`, `DEBUG CONSOLE`) streaming real-time ANSI-colored logs and API traces (`Ctrl+J`).
  - Fixed 24px bottom status bar (`.part.statusbar`, `#007ACC`) with git branch, latency gauge, health indicators, GPU tally, and connection details.
  - Floating fuzzy Command Palette modal (`Ctrl+P` / `F1`) with arrow navigation.
- **WPipe Static Server Integration:** Replaced `LaunchStreamlit` with lightweight `LaunchWorkbench` (`ui/server.py`) serving static assets, providing dynamic `/config.js` and sub-millisecond `/health` endpoints while preserving the WPipe pipeline orchestration.
- **Ultra-Lean Container Footprint:** Image size reduced from ~581 MB to < 80 MB, and runtime container RAM reduced from ~150 MB to < 10 MB.

### Changed
- Bumped project version to `3.0.0` across backend, frontend, and documentation.
- Streamlined `ui/requirements.txt` to remove Streamlit and Pandas dependencies.

## [2.3.2] - 2026-10-22

### Added
- **Reverse Engineered (REA) VSCode TitleBar:** Precision CSS alignment matching VSCode's desktop Electron shell (`.part.titlebar`, `.menubar-menu-button`, and `.command-center`) with exact dark tokens (`#181818`, `#252526`, `#3C3C3C`, `#007ACC`).
- **Full-Width Workspace (Sidebar Elimination):** Removed the redundant sidebar and side drawer controls, dedicating 100% of the viewport width to the workbench editor, top command bar, tabs strip, and status bar.

### Changed
- Bumped project version to `2.3.2` across backend, frontend, and documentation.

## [2.3.1] - 2026-10-22

### Added
- **Authentic Top Desktop Menu Bar:** Unified the top bar into a true VSCode-style header positioned directly at the top of the viewport (hiding the blank Streamlit header), featuring the classic horizontal menu: **Archivo**, **Editar**, **Ver**, **Ejecutar**, **Terminal**, and **Ayuda** with styled context-menu popovers and zero chevron arrows.
- **Streamlined Primary Sidebar Navigation:** Completely eliminated sidebar clutter by replacing cramped multi-column rails and nested open expanders with a clean, spacious single-column file explorer grouped into `TOPOLOGÍA & CLÚSTER`, `CARGAS DE TRABAJO`, and `GOBERNANZA & FINOPS`, with instant 1-click access and active state indicator.

### Changed
- Bumped project version to `2.3.1` across backend, frontend, and documentation.

## [2.3.0] - 2026-10-22

### Added
- **Dynamic Celery Worker Name Resolution:** Implemented `resolve_celery_worker_names` in `ClusterRepository` to dynamically discover authoritative worker hostnames via Celery inspect `active_queues`, heartbeat metadata, and fallback patterns, eliminating dropped signals caused by hardcoded names.
- **Graceful Drain with Active Workload Eviction:** Enhanced `POST /api/v1/invokers/{worker_ip}/drain` with `evict: bool = True` (default `True`). When draining an invoker, the cluster controller now:
  - Cancels public queues (`gpus_high`, `gpus_medium`, `gpus_low`, `wyolo_gpu_queue`) and the private node queue (`worker_ip`).
  - Sets node-level eviction flag `invoker:{worker_ip}:cancel_active` in Redis.
  - Automatically identifies all active Celery tasks and Optuna trials executing on the drained node, writing dual Redis cancellation keys (`wyolo:task:{id}:cancel`, `task:{id}:cancel`, `study:{id}:cancel`, `study:{id}:cancelled`) and revoking tasks immediately via Celery `revoke(terminate=True, signal='SIGKILL')`.
- **End-to-End Study Cancellation:** Updated `cancel_study` to emit both `:cancel` and `:cancelled` keys and proactively inspect and revoke active Celery tasks associated with the study across all cluster nodes.

### Changed
- Bumped project version to `2.3.0` across backend, frontend, and documentation.
- Updated Drain button in Streamlit Invokers view to explicitly trigger graceful drain with workload eviction.

## [2.2.0] - 2026-10-22
