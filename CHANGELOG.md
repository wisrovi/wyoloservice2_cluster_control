# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
