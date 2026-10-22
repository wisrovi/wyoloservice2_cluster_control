# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
