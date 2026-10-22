# 🎛️ NeuralForge Cluster Admin (`wyoloservice2_cluster_control`)

![Version](https://img.shields.io/badge/version-3.1.8-blue.svg)
![Status](https://img.shields.io/badge/status-active-success.svg)
![Python](https://img.shields.io/badge/python-3.10-blue.svg)
![Docker](https://img.shields.io/badge/docker-ready-2496ED.svg?logo=docker)

> Enterprise-grade centralized cluster administration, live telemetry dashboard, and dynamic hardware resource allocation platform (FastAPI + Static VSCode Workbench SPA) engineered with 100% authentic Visual Studio Code Monaco Workbench architecture for the `train_service2` ecosystem.

---

## 🛠️ Tecnologías y Librerías Clave

Este microservicio combina un backend API de alto rendimiento con una interfaz gráfica interactiva, estática y reactiva:

*   **FastAPI (v0.110+):** Framework asíncrono para el API Gateway RESTful con documentación interactiva Swagger/OpenAPI (`/docs`).
*   **Static VSCode Workbench SPA (HTML5 + CSS3 + Vanilla JS):** Frontend de ultra alto rendimiento (0ms client latency, < 80MB de imagen Docker, < 10MB de RAM) replicando al píxel la arquitectura del workbench de Visual Studio Code: Titlebar de 35px (`#181818`), barra de menú superior con menús desplegables auténticos (**Archivo**, **Editar**, **Ver**, **Ir**, **Ejecutar**, **Terminal**, **Ayuda**), Command Center / Quick Open `Ctrl+P` flotante, barra de pestañas interactivas multi-editor, migas de pan breadcrumbs, drawer inferior colapsable para consola/terminal (`Ctrl+J`) y barra de estado permanente de 24px (`#007ACC`).
*   **Redis (v5.0+):** Almacén de datos persistente en memoria para la telemetría física (`physical_*`), límites asignados (`limits_*`), credenciales seguras de operadores (`cluster:auth:users`), políticas de scheduling y dead-letter queue (`cluster:dlq:tasks`).
*   **Celery (v5.3+):** Protocolo de comunicación para inspección en tiempo real de colas activas (`active_queues`), emisiones de señales hacia invokers y difusión masiva de imágenes (`force_docker_pull`).
*   **Optuna & Hyperparameter Sweeps:** Agrupación y supervisión de barridos multi-trial, cálculo de convergencia métrica y cancelación en lote.
*   **PyJWT & Cryptography:** Generación, firma y verificación de tokens de acceso Bearer JWT para proteger las operaciones del cluster.
*   **Pydantic (v2.6+):** Validación estricta de esquemas de datos y serialización de modelos de hardware, tareas y webhooks.
*   **Pytest & Pytest-Cov:** Suite de pruebas unitarias automatizadas y cálculo de cobertura de código ejecutadas dentro de contenedores Docker.
*   **Uvicorn:** Servidor ASGI de nivel de producción para el backend FastAPI.
*   **WPipe (v2.5.13):** Orquestación del arranque de cada microservicio (`main.py` + `dto/` + `states/`) con pasos tipados y desacoplados.
*   **Docker & Docker Compose:** Dos imágenes independientes (API y UI) orquestadas con healthchecks y red privada.
*   **Kubernetes Pods & Dozzle:** Soporte nativo para orquestación de Pods efímeros en K8s (RKE2/K3s) con fijado `spec.nodeName`, `emptyDir` para `/dev/shm`, límites `nvidia.com/gpu` y transmisión de logs a Dozzle.

---

## 🗺️ Arquitectura del Sistema

```mermaid
flowchart TD
    subgraph UI_Layer [Frontend Layer - VSCode Workbench SPA :8501]
        Login[🔐 Login Overlay] --> Workbench[💻 Monaco Desktop Workbench]
        Workbench --> TopMenubar[📑 Titlebar Menubar: Archivo | Editar | Ver | Ejecutar...]
        Workbench --> CommandPalette[🔍 Command Center Ctrl+P]
        Workbench --> EditorTabs[📑 Multi-Editor Tabs & Breadcrumbs]
        Workbench --> TerminalPanel[💻 Collapsible Bottom Terminal Panel Ctrl+J]
    end

    subgraph API_Layer [API Gateway - FastAPI :8001]
        AuthRouter["/api/v1/auth/*"]
        InvokersRouter["/api/v1/invokers/*"]
        TasksRouter["/api/v1/tasks/*"]
        OverviewRouter["/api/v1/cluster/*"]
    end

    subgraph Data_Layer [Master Control Host 192.168.10.252]
        R[(Redis :23437)]
        CB[Celery Broker]
        Samba[(📂 Samba CIFS)]
        MinIO[(🪣 MinIO S3)]
    end

    subgraph Workers_Layer [Distributed Invoker Workers]
        Inv1[Invoker 192.168.1.68]
        Inv2[Invoker 192.168.1.72]
        InvN[Invoker N...]
    end

    Login -.->|POST /auth/login| AuthRouter
    Workbench -.->|REST 0ms latency| API_Layer
    InvokerView -.->|PUT /invokers/{ip}/limits| InvokersRouter
    InvokerView -.->|POST /invokers/{ip}/pause| InvokersRouter
    TasksView -.->|GET /tasks/active| TasksRouter
    TasksView -.->|GET /cluster/estimate-duration| OverviewRouter
    Dashboard -.->|GET /cluster/overview| OverviewRouter
    Dashboard -.->|GET /cluster/health| OverviewRouter
    SettingsView -.->|POST /cluster/webhook| OverviewRouter

    AuthRouter <-->|cluster:auth:users| R
    InvokersRouter <-->|invoker:IP:resources| R
    InvokersRouter -.->|Celery control signals| CB
    OverviewRouter -.->|Celery active_queues probe| CB
    OverviewRouter -.->|Storage ping| Samba
    OverviewRouter -.->|Storage ping| MinIO
    TasksRouter <-->|study:*| R

    Inv1 <-->|Consulta y Aplica MAX_GPU, RAM, CPU| R
    Inv2 <-->|Consulta y Aplica MAX_GPU, RAM, CPU| R
    InvN <-->|Consulta y Aplica MAX_GPU, RAM, CPU| R
```

---

## 🔐 Seguridad y Autenticación Inicial

El sistema cuenta con autenticación obligatoria tanto en la API como en Streamlit:

*   **Auto-Seed en el Arranque:** Al arrancar el servidor backend por primera vez, si el usuario administrador no existe en Redis, se genera automáticamente:
    *   **Usuario:** `wisrovi`
    *   **Contraseña:** `wyoloservice`
*   **Persistencia:** Las credenciales se guardan con hash criptográfico y sal única (`salt$sha256`) en la clave de Redis `cluster:auth:users`.
*   **Tokens:** Al iniciar sesión se emite un token JWT con validez de 24 horas.
*   **Cambio de Contraseña:** El usuario puede actualizar su contraseña directamente desde la vista **🛠️ Maintenance & Settings** de la interfaz.

---

## 📂 Estructura del Proyecto (Arquitectura WPipe)

API e interfaz viven en carpetas propias. Cada una es un microservicio independiente con su `Dockerfile`, `requirements.txt` y un orquestador WPipe (`main.py` + `dto/` + `states/`):

```text
wyoloservice2_cluster_control/
├── api/                         # 🔌 REST API service (FastAPI)
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── main.py                  # WPipe pipeline entrypoint
│   ├── dto/api_startup_context.py
│   ├── states/                  # LoadApiSettings, CheckRedisConnection, SeedAdminUser, ServeApi
│   └── backend/                 # FastAPI app, routers, schemas, Redis/Celery client, auth
├── ui/                          # 🖥️ Streamlit UI service
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── main.py                  # WPipe pipeline entrypoint
│   ├── dto/ui_startup_context.py
│   ├── states/                  # LoadUiSettings, WaitForApi, LaunchStreamlit
│   └── frontend/                # Streamlit app, API client and 10 admin views
├── tests/api/  tests/ui/        # Dockerized pytest suites
├── docker-compose.yml           # API + UI stack with healthchecks
├── Makefile                     # build / up / down / logs / test / push
├── control_host.env.example     # Runtime configuration template
└── start.sh                     # Local dev launcher (without Docker)
```

### Pipelines de arranque WPipe

```mermaid
flowchart LR
    subgraph API ["api/main.py - cluster_admin_api"]
        A1[LoadApiSettings] --> A2[CheckRedisConnection] --> A3[SeedAdminUser] --> A4["ServeApi (Uvicorn :8001)"]
    end
    subgraph UI ["ui/main.py - cluster_admin_ui"]
        U1[LoadUiSettings] --> U2["WaitForApi (/health)"] --> U3["LaunchStreamlit (:8501)"]
    end
    A4 -. healthcheck .-> U2
    U3 -->|REST + JWT| A4
```

---

## 🚀 Despliegue y Ejecución

### 1. Docker Compose (recomendado)

```bash
make setup     # crea control_host.env desde control_host.env.example (editar credenciales)
make up        # construye y levanta API + UI con healthchecks
make ps        # estado de los contenedores
make logs      # logs en vivo
make down      # detiene el stack
```

| Servicio | Contenedor | Imagen Docker Hub | Puerto |
| :--- | :--- | :--- | :--- |
| API | `neuralforge_cluster_admin_api` | `wisrovi/train_service:cluster_admin_api_v1.6.0` | `8001` |
| UI | `neuralforge_cluster_admin_ui` | `wisrovi/train_service:cluster_admin_ui_v1.6.0` | `8501` |

La UI espera a que la API esté *healthy* antes de arrancar (`depends_on: service_healthy`) y se comunica con ella por la red interna `cluster_admin_network` (`http://cluster_admin_api:8001`).

Publicar las imágenes en Docker Hub:

```bash
make build && make push
```

### 2. Ejecución local sin Docker (desarrollo)

```bash
pip install -r api/requirements.txt -r ui/requirements.txt
make dev       # equivalente a ./start.sh
```

Los servicios quedarán disponibles en:
*   **Interfaz de Usuario (Streamlit):** [http://localhost:8501](http://localhost:8501)
*   **Backend API (FastAPI Swagger Docs):** [http://localhost:8001/docs](http://localhost:8001/docs)

---

## 🧪 Pruebas Unitarias y Cobertura

Cumpliendo con los estándares de calidad del ecosistema, todas las pruebas unitarias se ejecutan dentro de un contenedor Docker aislado (`python:3.10-slim`):

### Ejecutar Pruebas Unitarias
```bash
make test      # o ./run_tests.sh  (tests/api con PYTHONPATH=api, tests/ui con PYTHONPATH=ui)
```

### Calcular Cobertura de Código
```bash
make coverage  # o ./coverage.sh
```

---

## 📋 Endpoints Principales de la API

| Método | Endpoint | Descripción | Requiere Auth |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/v1/auth/login` | Inicia sesión y retorna token JWT | No |
| `GET` | `/api/v1/auth/me` | Retorna el usuario autenticado | Sí |
| `POST` | `/api/v1/auth/change-password` | Actualiza la contraseña en Redis | Sí |
| `GET` | `/api/v1/cluster/overview` | KPIs y estado general del cluster | Sí |
| `GET` | `/api/v1/cluster/health` | Watchdog de latencia Redis, Celery probe, Samba y MinIO | Sí |
| `GET` | `/api/v1/cluster/webhook` | Consulta configuración de webhooks de alerta | Sí |
| `POST` | `/api/v1/cluster/webhook` | Guarda URL de Webhook y estado activo | Sí |
| `POST` | `/api/v1/cluster/webhook/test` | Emite notificación de prueba vía Webhook | Sí |
| `GET` | `/api/v1/cluster/estimate-duration` | Estimador dinámico de duración y throughput (ETA) | Sí |
| `GET` | `/api/v1/cluster/recommend-node` | Smart Dispatcher: recomendación inteligente de nodo óptimo | Sí |
| `GET` | `/api/v1/cluster/gpu-benchmarks` | Leaderboard de rendimiento de GPUs y throughput empírico | Sí |
| `GET` | `/api/v1/cluster/green-ai` | Métricas de consumo energético (kWh), huella CO₂e y eficiencia | Sí |
| `POST` | `/api/v1/cluster/watchdog/check-and-alert` | Escaneo proactivo de salud y emisión de alertas a Webhooks | Sí |
| `GET` | `/api/v1/cluster/trends` | Distribución horaria y diaria de carga de trabajo (Workload Trends) | Sí |
| `GET` | `/api/v1/cluster/housekeeping/preview` | Inspección de memoria Redis y conteo de estudios fallidos obsoletos | Sí |
| `POST` | `/api/v1/cluster/housekeeping/purge` | Purga segura de estudios y claves efímeras huérfanas en Redis | Sí |
| `GET` | `/api/v1/invokers` | Lista invokers con hardware y límites | Sí |
| `GET` | `/api/v1/invokers/{ip}` | Detalle completo de un invoker | Sí |
| `GET` | `/api/v1/invokers/{ip}/processes` | Procesos GPU activos por nodo con alerta de procesos zombies | Sí |
| `POST` | `/api/v1/invokers/{ip}/kill-process/{pid}` | Terminación remota de un proceso rogue/zombie en el nodo | Sí |
| `GET` | `/api/v1/invokers/{ip}/diagnose` | Diagnóstico profundo de conectividad física, SSH puerto 22 y Celery | Sí |
| `PUT` | `/api/v1/invokers/{ip}/limits` | Modifica `max_gpu_percent`, `max_ram` y `max_cpu_cores` | Sí |
| `POST` | `/api/v1/invokers/{ip}/pause` | Pausa o reanuda la cola pública de un invoker | Sí |
| `POST` | `/api/v1/invokers/{ip}/drain` | Pone el nodo en modo drenado (finaliza tareas y pausa) | Sí |
| `POST` | `/api/v1/invokers/{ip}/restart-service` | Reinicio remoto del servicio Celery del nodo invoker | Sí |
| `POST` | `/api/v1/invokers/{ip}/prune-docker` | Limpieza remota de imágenes y contenedores huérfanos (`docker system prune`) | Sí |
| `POST` | `/api/v1/cluster/smoke-test` | Smoke test integral 1-click validando CIFS, S3 y GPUs de todos los nodos | Sí |
| `GET` | `/api/v1/cluster/storage/inspect` | Inspección profunda de almacenamiento: CIFS/Samba, MinIO S3 y latencias I/O | Sí |
| `GET` | `/api/v1/cluster/finops` | Análisis FinOps de costes eléctricos reales (€), kWh por GPU y proyecciones | Sí |
| `POST` | `/api/v1/cluster/finops/rate` | Configuración de tarifa eléctrica dinámica (€/kWh) con registro de auditoría | Sí |
| `GET` | `/api/v1/cluster/audit/logs` | Registro inmutable de auditoría administrativa (`cluster:audit:logs`) | Sí |
| `GET` | `/api/v1/cluster/capabilities` | Catálogo de capacidades del clúster y los 12 módulos de I+D (XAI, CVPR, NeurIPS) | Sí |
| `GET` | `/api/v1/tasks/queues` | Inspección en tiempo real de colas Celery y lista de espera de tareas | Sí |
| `POST` | `/api/v1/tasks/queues/{id}/reassign` | Reasignación inmediata de una tarea privada a la cola global pública | Sí |
| `POST` | `/api/v1/tasks/queues/{id}/promote` | Promoción de prioridad de una tarea en cola Celery a HIGH | Sí |
| `DELETE` | `/api/v1/tasks/queues/{id}` | Purga/eliminación de una tarea en cola Celery antes de su inicio | Sí |
| `GET` | `/api/v1/tasks/active` | Lista entrenamientos en ejecución en tiempo real | Sí |
| `GET` | `/api/v1/tasks/history` | Historial de estudios con filtros (search, autor, nodo, status) | Sí |
| `POST` | `/api/v1/tasks/compare` | Comparador Head-to-Head directo entre 2 a 5 estudios | Sí |
| `GET` | `/api/v1/tasks/{id}/reproducibility` | Generador de comando Docker y manifiesto YAML reproducible | Sí |
| `POST` | `/api/v1/tasks/quick-launch` | Lanzador rápido con soporte de prioridad (NORMAL, URGENT, BATCH) | Sí |
| `GET` | `/api/v1/tasks/{id}/metrics` | Métricas de trials para curvas de aprendizaje Optuna | Sí |
| `GET` | `/api/v1/tasks/{id}/logs` | Streaming de logs de entrenamiento en vivo o históricos | Sí |
| `GET` | `/api/v1/tasks/{id}/k8s-events` | Inspección de eventos de ciclo de vida del Pod en Kubernetes | Sí |
| `POST` | `/api/v1/tasks/{id}/kill-pod` | Desalojo forzoso e inmediato del Pod en Kubernetes (`gracePeriodSeconds: 0`) | Sí |
| `POST` | `/api/v1/cluster/k8s/purge-stale-pods` | Purgado de pods huérfanos/fallidos en Kubernetes para liberar recursos | Sí |
| `GET` | `/api/v1/tasks/{id}/diagnostics` | Diagnóstico automatizado post-mortem de causa raíz (OOM, datasets, exit 1) | Sí |
| `POST` | `/api/v1/tasks/{id}/cancel` | Cancela un entrenamiento y emite señal de parada | Sí |
| `GET` | `/api/v1/tasks/sweeps` | Agrupación y métricas de convergencia de barridos Optuna | Sí |
| `POST` | `/api/v1/tasks/sweeps/{name}/cancel` | Cancelación en lote de todos los trials activos de un sweep | Sí |
| `GET` | `/api/v1/tasks/quarantine` | Inspección de tareas aisladas en Dead Letter Queue (DLQ) | Sí |
| `POST` | `/api/v1/tasks/quarantine/{id}/retry` | Reintentar y desbloquear tarea aislada en DLQ | Sí |
| `DELETE` | `/api/v1/tasks/quarantine/{id}` | Purga permanente de tarea venenosa de la DLQ | Sí |
| `GET` | `/api/v1/cluster/images/status` | Matriz de versiones y digests Docker/K8s por nodo invoker | Sí |
| `POST` | `/api/v1/cluster/images/broadcast-pull` | Difusión broadcast de pull de imagen (excluyendo NAS manager) | Sí |
| `GET` | `/api/v1/cluster/datasets/inspect` | Pre-flight check y validación de `data.yaml`, splits y clases | Sí |
| `POST` | `/api/v1/cluster/datasets/validate` | Validación instantánea de dataset previa a despacho | Sí |
| `GET` | `/api/v1/cluster/datasets/available` | Auto-descubrimiento de datasets en disco local y montajes Samba | Sí |
| `GET` | `/api/v1/cluster/scheduler/policy` | Consulta de política y modo activo Day/Night Scheduler | Sí |
| `POST` | `/api/v1/cluster/scheduler/policy` | Configuración de política horaria (modo silencioso vs potencia) | Sí |
| `POST` | `/api/v1/cluster/scheduler/apply-policy` | Aplicación forzada e inmediata del perfil horario activo al clúster | Sí |
| `GET` | `/api/v1/cluster/support-bundle` | Exportador de caja negra diagnóstica en JSON descargable (1-Click) | Sí |
| `POST` | `/api/v1/cluster/webhook/test-rich` | Disparo y prueba de alertas ricas embed en Discord/Slack | Sí |

---

## 👨‍💻 Autor & Licencia

*   **Autor:** William Steve Rodriguez Villamizar (`wisrovi`)
*   **Email:** `wisrovi.rodriguez@gmail.com`
*   **Licencia:** PolyForm Noncommercial License 1.0.0. Ver [LICENSE](LICENSE) y [COMMERCIAL.md](COMMERCIAL.md).

---

## 📝 Changelog

*   **v3.1.8 (2026-10-22):**
    *   **Corrección en Validación de Datasets y Ampliación de Tests Unitarios:**
        *   Corrección en la vista de almacenamiento (`storage.js`) para evaluar explícitamente el atributo `res.valid`, mostrando avisos de advertencia en color ámbar `⚠️ [INVALID]` cuando una ruta o estructura no sea accesible.
        *   Ampliación de la suite de pruebas unitarias (`tests/api/test_api.py`) con cobertura para la cancelación en lote de tareas en cola (`batch-delete`) y la validación de datasets.
        *   Alineación de versiones y marcas estáticas en modales, overlay de autenticación y diálogos de información a la v3.1.8.
*   **v3.1.7 (2026-10-22):**
    *   **Cancelación en Lote y Notificación Visual de Tareas en Espera:**
        *   Incorporación de banner toast visual reactivo (`#overview-queued-toast` y `#tasks-queued-toast`) para confirmación inmediata al cancelar tareas en cola.
        *   Incorporación del botón **"🗑️ Cancelar Filtradas (N)"** permitiendo purgar en lote todas las tareas que coincidan con la búsqueda activa en un solo clic.
        *   Endpoint de backend `POST /api/v1/tasks/queues/batch-delete` con soporte de supresión atómica de múltiples tareas Celery.
        *   Corrección en resolución dinámica de colas (`_get_all_candidate_queues`): eliminación exitosa de tareas asignadas a colas privadas de nodos (`192.168.1.68`, etc.) y bindings dinámicos.
*   **v3.1.6 (2026-10-22):**
    *   **Filtrado Multicriterio y Paginación en Frontend para Tareas en Espera (`overview.js` y `tasks.js`):**
        *   Barra de filtros integrada en tiempo real en la sección **"⏳ Queued Workloads & Celery Backlog (En Espera)"** del panel principal `Overview` y en **"⏳ Detailed Waiting Queue & Celery Backlog (Tareas en Espera)"** de `Tasks & Queues`.
        *   Búsqueda instantánea por texto en todos los campos (nombre de estudio, ID de tarea, autor, modelo, ruta del dataset o cola destino).
        *   Filtros desplegables por Cola/Nodo de destino (poblado dinámicamente según las colas existentes), Prioridad (`NORMAL`, `HIGH`) y Modelo.
        *   Paginación interactiva en el frontend con selector de elementos por página (`5`, `10`, `25`, `50`), botones de navegación `◀ Anterior` / `Siguiente ▶`, contador de páginas (`Pág. X / Y`) e indicador de rango de tareas visibles frente al total.
        *   Botón para limpiar filtros (`✕ Limpiar`) y botón para refrescar en caliente (`🔄 Refrescar`).
*   **v3.1.5 (2026-10-22):**
    *   **Robustez en Modal de Pausa y Ejecución de Pausa Perpetua (`nodes.js`):**
        *   Eliminación del fallo de propagación de eventos de click en etiquetas anidadas mediante tarjetas interactivas accionables (`card-pause-temporal` y `card-pause-perpetual`) con selectores directos por JS (`selectPauseMode`).
        *   Retroalimentación visual activa (bordes resaltados en azul vs rojo según el modo seleccionado).
        *   Actualización dinámica del botón de confirmación (`#pause-confirm-btn`) indicando textualmente el modo exacto y duración antes de pulsar (`⏱️ Confirmar Pausa Temporal (Xh)` vs `⏹️ Confirmar Pausa Perpetua (Indefinida)`).
        *   Diferenciación visual entre `⏹️ Pausa Indef.` (insignia roja de alerta) y `⏱️ Pausa Temp` (insignia ámbar con contador de tiempo restante) en la topología de nodos de `Nodes` y del dashboard `Overview`.
*   **v3.1.4 (2026-10-22):**
    *   **Visibilidad Completa de Tareas en Cola (Queued Workloads):** Incorporación de la tabla interactiva de tareas en espera en la vista principal `Overview` (directamente debajo de las tareas activas) y en la vista `Tasks & Queues`, mostrando `study_name`, nodo de destino, modelo, autor, prioridad y acciones de gestión en tiempo real (promover a alta prioridad, reasignar cola y cancelar).
    *   **Fallback para Estudios Heredados en Redis:** Extracción resiliente de metadatos y configuración de estudios creados por el manager en `wyolo:request:*` para alimentar los paneles de telemetría sin pérdida de fidelidad.
*   **v3.1.3 (2026-10-22):**
    *   **Persistencia de Nombre Personalizado de Estudio:** Integración del campo `study_name` en el esquema `QuickLaunchRequest`, API router y cliente Redis, asegurando que el nombre del proyecto digitado por el operador se preserve íntegramente en la configuración del barrido de Optuna y en la carga de Celery.
*   **v3.1.2 (2026-10-22):**
    *   **Incorporación Total de YOLO26 en Todos los Dominios:** Modelos YOLO26 (`yolo26n`, `yolo26s`, `yolo26m`, `yolo26l`, `yolo26x`) disponibles de forma nativa para Detección, Segmentación, Clasificación, Pose y Cajas Orientadas (OBB).
    *   **Inclusión de Modelos SOTA Adicionales (≥ v8):** Integración de **RT-DETR** (`rtdetr-l.pt`, `rtdetr-x.pt` con enrutamiento automático `"type": "rtdetr"`) y **YOLO-World v2** para detección de vocabulario abierto zero-shot.
    *   **Depuración Completa de Modelos Obsoletos (< v8):** Eliminación total de YOLOv5 y YOLOv5u de todas las listas de selección y heurísticas, estableciendo YOLOv8 como versión base mínima admitida.
*   **v3.1.1 (2026-10-22):**
    *   **Selector Multitarea de Visión por Computador en Smart Dispatcher (`dispatch.js`):**
        *   **Selector de Dominio CV:** Detección de Objetos (`detect`), Segmentación de Instancias (`segment`), Clasificación de Imágenes (`classify`), Estimación de Pose (`pose`), Cajas Orientadas (`obb`) y Pesos Personalizados (`custom`).
        *   **Catálogo Extendido de Modelos:** Integración completa de familias YOLO11 (n/s/m/l/x), YOLOv10 (n/s/m/b/l/x), YOLOv9 (t/s/m/c/e), YOLOv8 (n/s/m/l/x), YOLOv5u (nu/su/mu/lu/xu), YOLO26 experimental y soporte para pesos externos `.pt`.
        *   **Sincronización Inteligente de Parámetros:** Ajuste automático de dataset recomendado, resolución (`imgsz` de 224 a 1280), métricas de fitness Optuna (`mAP50(B)`, `mAP50(M)`, `mAP50-95(P)`, `accuracy_top1`) y selector de AutoBatch (`-1`).
        *   **Ampliación de Épocas de Entrenamiento:** Soporte completo de 1 a 1000 épocas tanto en el esquema FastAPI como en la interfaz y estimador ETA.
*   **v3.1.0 (2026-10-22):**
    *   **Suite Completa de Funcionalidades y Telemetría en Vivo (100% Cobertura):**
        *   **📈 Historial y Estudio de Analítica Optuna (`history.js`):** Filtros dinámicos (autor, nodo, estado, límite, "Mis estudios"), modal de inspección con Manifiesto de Reproducibilidad (comando `docker run` y YAML copiables en 1 clic), Diagnóstico de Causa Raíz con recomendaciones, Visor de Logs en vivo, Curvas de Aprendizaje de Optuna interactivas en SVG, Comparador Frente a Frente de 2 a 5 estudios, y Exportador de Reportes a Markdown y JSON.
        *   **🚀 Lanzador Inteligente de Tareas (`dispatch.js`):** Validación Pre-Vuelo de Dataset contra Samba CIFS, Recomendador de Nodos por IA con puntuación, Estimador Dinámico de Duración (ETA) y throughput (img/s), selector de prioridades (NORMAL, URGENT, BATCH) y monitor de entrenamientos activos con cancelación directa.
        *   **🛠️ Ajustes y Gobernanza Operacional (`settings.js`):** Ajuste de límites en lote (`MAX_GPU %` y RAM) en todo el clúster con 1 clic, Políticas Horarias Automatizadas Día/Noche con botón de aplicación forzada, Exportador de "Caja Negra" Diagnostic Support Bundle (.json) en 1 clic, Mantenimiento y Purga de Estudios Obsoletos de Redis, y canales de alertas Webhook y Watchdog.
        *   **🏆 Benchmarks de GPUs en Vivo (`benchmarks.js`):** Leaderboard dinámico conectado al endpoint del clúster con throughput real y mapeo de hardware desplegado.
        *   **🌿 FinOps y Green AI (`finops.js`):** Monitorización de kWh reales, costes acumulados, proyecciones mensuales, huella de carbono CO2e y actualización interactiva de tarifa eléctrica (€/kWh).
        *   **🔬 Catálogo R&D y Capacidades (`capabilities.js`):** Visualización de los 12 módulos de investigación y matriz de arquitecturas y precisiones CUDA (FP32/FP16/BF16/FP8).
        *   **📁 Almacenamiento y MinIO S3 (`storage.js`):** Lectura dinámica de volúmenes Samba compartidos, latencias I/O, estado de buckets MinIO S3 y validador de rutas.
*   **v3.0.2 (2026-10-22):**
    *   **Soporte Integral para Pausa Temporal y Perpetua:** Incorporación en el backend y la interfaz SPA VSCode Workbench de modalidades completas de pausa:
        *   **⏱️ Pausa Temporal con Horas Configurables:** Permite detener el consumo de tareas públicas en invokers por un periodo determinado mediante botones directos (1h, 2h, 4h, 8h, 24h) o entrada personalizada.
        *   **Motor de Expiración Automática en Redis:** Validación en tiempo real de `pause_until` que reanuda el nodo y reconecta los consumidores Celery automáticamente al cumplirse el tiempo.
        *   **⏹️ Pausa Perpetua / Indefinida:** Modo de pausa indefinida que aisla el nodo de las colas públicas globales hasta que el operador decida reanudarlo manualmente.
        *   **Modal Interactivo de Configuración de Pausa:** Diálogo contextual en `nodes.js` con selectores radio y temporizador visible.
        *   **Etiquetas y Cuenta Regresiva en Vivo:** Semáforos visuales (`⏱️ Pausa Temp (Xh Ym)`, `⏹️ Pausa Indef.`) y cálculo dinámico de tiempo restante en la tabla de nodos.
        *   **Controles en Lote Actualizados:** Nuevos botones `⏸️ Pause 4h (All)`, `⏹️ Pause Indef. (All)` y `▶️ Resume All`.
*   **v3.0.1 (2026-10-22):**
    *   **Restauración Integral de Telemetría Real y Asignación de GPUs:** Extracción y representación fiel de los datos de hardware NVML y Redis en Operations Center y Nodes & Invokers:
        *   **Tabla de Entrenamientos Activos en Vivo:** Visualización directa de las tareas en ejecución (`Tattoo_detector`, `Cesped_detector_v2`) con autor, nodo asignado, modelo, dataset, progreso de trials y estado de Pod K8s.
        *   **Estados de Nodos y Filtros Rápidos:** Semáforos claros (`🟢 Active`, `⏸️ Paused`, `🛡️ Draining`) y barra de botones de filtrado instantáneo (`🔘 Todos`, `🟢 Solo Activos`, `⏸️ Solo Pausados`, `🛡️ En Drenado`) con 0ms de latencia.
        *   **GPU Compartida vs GPU Total:** Desglose visual de GPUs asignadas por K8s vs capacidad total, junto con el porcentaje de tope compartido de VRAM (`MAX_GPU %`).
        *   **VRAM Total y Termales NVML:** Lectura de VRAM real (`gpu_memory_total`), uso de cómputo GPU (`%`), potencia en vatios (`W vs TDP`) y temperatura en grados Celsius.
        *   **Límites de RAM y Memoria Host:** Comparativa clara entre el límite asignado al contenedor (`max_ram`) y la memoria física del host (`ram_total`).
        *   **Monitor de Procesos GPU y Procesos Zombi (`🔍 Procs`):** Modal interactivo para inspeccionar procesos en ejecución por PID en cada nodo y botón para terminación forzada (`🛑 Kill PID`).
        *   **Controles en Lote:** Botones para pausar y reanudar todos los nodos del clúster con un solo clic.
*   **v3.0.0 (2026-10-22):**
    *   **Eliminación Total de Streamlit & SPA Estática VSCode Workbench:** Reemplazo integral de Streamlit por una Single Page Application (SPA) nativa en HTML5/CSS3/Vanilla JS que replica al píxel el workbench de Visual Studio Code (`.part.titlebar`, barra de menús clásica Archivo/Editar/Ver/Ir/Ejecutar/Terminal/Ayuda, Command Center flotante `Ctrl+P`, pestañas multi-editor, consola inferior colapsable `Ctrl+J` y barra de estado permanente `007ACC`).
    *   **Arquitectura de Latencia Cero (0ms Client-Side):** Comunicación directa con el backend FastAPI (`:8001`), eliminando por completo las re-ejecuciones pesadas de Python por cada clic, desconexiones de WebSockets y parches sobre el Shadow DOM.
    *   **Servidor Estático Ultraligero y WPipe:** Integración en `ui/main.py` de `LaunchWorkbench` (`ui/server.py`) sirviendo archivos estáticos con resolución dinámica de API `/config.js` y healthcheck en tiempo real `/health`.
    *   **Huella Mínima en Contenedores:** Reducción drástica del tamaño de la imagen Docker de ~581MB a < 80MB, y consumo de RAM en ejecución de ~150MB a < 10MB.
*   **v2.3.2 (2026-10-22):**
    *   **Barra Superior REA VSCode y Workspace Completo (100% Viewport):** Alineación de tokens y reglas CSS exactas del workbench de VSCode (`.part.titlebar`, `.menubar-menu-button`, `.command-center`). Se eliminó la barra lateral redundante para liberar el 100% del ancho de pantalla para el editor de vistas, pestañas activas y barra de estado.
*   **v2.3.1 (2026-10-22):**
    *   **Barra Superior de Menú Clásico VSCode:** Integración de barra superior auténtica al píxel 0 de la ventana (ocultando el encabezado en blanco de Streamlit) con menús horizontales contextuales: **Archivo**, **Editar**, **Ver**, **Ejecutar**, **Terminal** y **Ayuda**, Command Center central (`Ctrl+P`) y resumen de estado y operador en la esquina superior derecha.
    *   **Barra Lateral Optimizada y Descongestiona:** Eliminación de los acordeones y columnas comprimidas que sobrecargaban la barra lateral. Reemplazo por un explorador limpio y amplio organizado en tres bloques (`TOPOLOGÍA & CLÚSTER`, `CARGAS DE TRABAJO`, `GOBERNANZA & FINOPS`) con iconos destacados y acceso en 1 solo clic.
*   **v2.3.0 (2026-10-22):**
    *   **Resolución Dinámica de Nombres de Celery:** Descubrimiento en tiempo real de los hostnames exactos de los trabajadores Celery mediante inspección de `active_queues`, metadatos de heartbeat y fallback de recursos, solucionando la pérdida silenciosa de señales causada por nombres estáticos.
    *   **Drenado de Nodos con Desalojo Inmediato de Cargas:** Soporte para `evict=True` en `/api/v1/invokers/{ip}/drain`. Cancela colas públicas y privadas en el nodo, activa la bandera `invoker:{ip}:cancel_active` en Redis, identifica todas las tareas y estudios activos en el nodo, emite cancelaciones dobles (`:cancel` y `:cancelled`) y revoca las tareas de Celery con `SIGKILL`.
    *   **Cancelación Completa de Estudios:** Actualización de `cancel_study` para propagar claves `:cancel` y `:cancelled` y revocar proactivamente las tareas de Celery en ejecución asociadas al estudio en cualquier nodo del clúster.
*   **v2.2.0 (2026-10-22):**
    *   **Arquitectura Organizacional VSCode Workbench:** Reorganización completa de la interfaz de administración del clúster adoptando el patrón estructural de Visual Studio Code obtenido mediante ingeniería inversa (REA).
    *   **Activity Bar & Primary Sidebar:** Barra vertical de actividades con 5 dominios de alto nivel (`EXPLORER`, `RUN & DISPATCH`, `TASKS & QUEUES`, `TELEMETRY & SPECS`, `ADMIN & SECURITY`) con conmutación dinámica de árbol de archivos y etiquetas de extensión (`.cluster`, `.yaml`, `.stream`, `.spec`, `.json`).
    *   **Command Center & Quick Open (`Ctrl+P`):** Buscador interactivo superior que permite saltar de forma instantánea a cualquiera de las 11 vistas, nodos o cargas de trabajo del clúster.
    *   **Barra de Pestañas Multi-Editor:** Sistema de pestañas con iconos, indicador de pestaña activa con borde `#007ACC` y soporte para cerrar o alternar vistas recientes.
    *   **Navegación Breadcrumbs:** Barra de contexto jerárquico (`neuralforge-cluster › activity › file › status`) para orientación espacial inmediata.
    *   **Panel Inferior Colapsable:** Drawer inferior estilo consola con pestañas `OUTPUT`, `TERMINAL`, `PROBLEMS (0)` y `DEBUG CONSOLE` con logs en monospace, comandos rápidos y telemetría de fallos.
    *   **Status Bar Azul VSCode:** Barra de estado permanente de 24px al pie de página mostrando rama git (`⑂ main*`), sincronización, contadores de problemas (`⨂ 0  ⚠ 0`), GPUs en línea y versión de backend.
    *   **Tokens y Paleta Dark+:** Variables CSS y tipografía (`Plus Jakarta Sans` y `JetBrains Mono`) ajustadas al tema Dark+ oficial de VSCode (`#1E1E1E`, `#252526`, `#333333`, `#007ACC`, `#3C3C3C`).
*   **v2.1.0 (2026-10-21):**
    *   **Rediseño Visual Enterprise 5 Estrellas:** Reingeniería visual completa basada en Glassmorphism de alta gama con fuentes `Plus Jakarta Sans` y `JetBrains Mono`, gradientes sutiles y micro-interacciones.
    *   **Motor de Estilos Centralizado (`ui/frontend/styles.py`):** Inyección de variables CSS avanzadas, tarjetas métricas con bordes superiores luminiscentes y elevación al pasar el cursor (`hover lift`), pestañas segmentadas sin subrayados toscos y botones primarios con sombra difusa.
    *   **Top HUD Ribbon & Cluster Pulse:** Barra superior que resume en vivo el estado y latencia de Redis, GPUs totales asignables, invokers en línea y estado de tejidos de almacenamiento CIFS y MinIO.
    *   **Sidebar Ejecutivo:** Barra lateral oscura con logotipo y monograma cerebral luminiscente, indicador de pulso continuo (`🟢 CLUSTER ACTIVE`), chip de versión y tarjeta de perfil de operador con avatar y rol.
    *   **Portal de Seguridad y Acceso (Login Portal):** Pantalla de inicio de sesión inspirada en consolas de computación de alto rendimiento con insignias de verificación criptográfica y botones de acceso rápido para operadores.
*   **v2.0.0 (2026-10-21):**
    *   **Agregador de Barridos Optuna (`/tasks/sweeps`, `/cancel`):** Agrupación jerárquica de trials por estudio de hiperparámetros, tracking de métrica líder global (`mAP50`) y cancelación masiva de trials en ejecución.
    *   **Sincronización de Imágenes y Broadcast Pull (`/cluster/images/*`):** Matriz de versiones y tags de imágenes Docker/K8s en cada invoker con botón de difusión broadcast 1-click, excluyendo estrictamente al manager (`celery@NAS_Train_service`).
    *   **Pre-Flight Check de Datasets & Auto-Descubrimiento Samba (`/cluster/datasets/*`):** Verificación proactiva de `data.yaml`, recuento de clases (`nc`), comprobación de particiones `train/` y `val/` y conteo de imágenes antes de permitir el encolamiento de trabajos.
    *   **Gestión de Cuarentena y Dead Letter Queue - DLQ (`/tasks/quarantine/*`):** Aislamiento automático de tareas venenosas o con fallos críticos repetidos (CUDA device-side asserts, NaN loss, OOM) con opciones de reintento o purga definitiva.
    *   **Programador Horario Automatizado Día / Noche (`/cluster/scheduler/*`):** Control de perfiles con modo silencioso en horas de oficina (09:00–18:30 con límite de 25% GPU) y máxima potencia nocturna y fines de semana (90% GPU).
    *   **Exportador de Diagnostic Support Bundle (Caja Negra 1-Click):** Descarga de paquete JSON unificado con inventario de nodos, estado de colas, eventos K8s, registros de auditoría y telemetría de hardware para soporte offline.
    *   **Notificaciones Webhook Ricas (Embeds):** Plantillas formateadas para Discord y Slack ante finalización de estudios, desalojo de pods y atascos en colas Celery.
*   **v1.9.0 (2026-10-21):**
    *   **Gestión de Pods de Kubernetes (`/tasks/{id}/k8s-events`, `/kill-pod`):** Inspección de eventos de ciclo de vida del Pod (`Scheduled`, `Pulled`, `Created`, `Started`, `OOMKilled`, `CrashLoopBackOff`) y botón en 1-click `💥 Desalojar Pod K8s` para terminación inmediata con `gracePeriodSeconds: 0`.
    *   **Limpieza de Pods Huérfanos/Fallidos (`/cluster/k8s/purge-stale-pods`):** Recolección de basura administrativa para eliminar pods en estados fallidos o desalojados y liberar locks de GPU.
    *   **Monitoreo de Condiciones de Nodo K8s:** Semáforo de presiones de Kubernetes (`DiskPressure`, `MemoryPressure`, `PIDPressure`, `Ready`) para prevenir desalojos sorpresivos.
    *   **Telemetría del NVIDIA Device Plugin:** Visualización de GPUs asignables vs capacidad total de Kubernetes (`nvidia.com/gpu`).
    *   **Asignador Dinámico de Memoria Compartida (`/dev/shm`):** Control deslizante para ajustar el `sizeLimit` del `emptyDir` de memoria en el Pod, erradicando fallos de bus en los DataLoaders de YOLO.
    *   **Integración con Dozzle K8s:** Enlaces directos a las transmisiones de logs de cada nodo (`http://{worker_ip}:8888`).
*   **v1.8.0 (2026-10-21):**
    *   **Gestión Inteligente de Colas Celery:** Rediseño comprensible en 5 tarjetas KPI (`wyolo_gpu_queue`, `gpus_high`, `gpus_low`, encoladas a nodos y tiempo estimado de backlog ETA), eliminando colas técnicas ruidosas (`managers`, `*.pidbox`) y ocultando nodos sin carga.
    *   **Reasignador Inmediato de Tareas (`/tasks/queues/{id}/reassign`):** Botón `🔀 A Cola Pública` que transfiere tareas retenidas en colas privadas de nodos hacia la cola global pública para su consumo por cualquier trabajador disponible.
    *   **Estimador de Vaciado de Backlog y Detector de Atascos (Jam Alert):** Alerta proactiva cuando existen tareas en espera mientras los nodos están pausados o desconectados, con botón `▶️ Reanudar Todos los Nodos`.
    *   **Mantenimiento Remoto de Nodos (`/invokers/{ip}/restart-service`, `/prune-docker`):** Botones administrativos para reinicio del servicio de Celery y ejecución de `docker system prune` para liberar espacio en disco remotamente.
    *   **Telemetría NVML en Vivo:** Visualización de temperatura (°C), consumo de potencia (Watts vs TDP) y porcentaje de utilización de cómputo GPU con indicadores semafóricos.
    *   **Smoke Test del Clúster en 1-Click (`/cluster/smoke-test`):** Validación integral y matriz de estado probando conectividad CIFS Samba, MinIO S3 y GPUs operativas en todos los nodos.
    *   **Desglose y Filtrado por Autor en Lista de Espera:** Agrupación y filtro dinámico por investigador.
*   **v1.7.0 (2026-10-21):**
    *   **Live Task Log Viewer (`/tasks/{study_id}/logs`):** Transmisión de logs de entrenamiento en tiempo real directamente desde la interfaz web (evita accesos manuales por SSH a nodos de cálculo).
    *   **Monitoreo de Procesos GPU y Detección de Zombies (`/invokers/{ip}/processes`):** Desglose detallado de procesos que consumen VRAM por GPU (`nvidia-smi`), banderas de alerta para procesos zombies inactivos por más de 24h y botón de terminación administrativa en 1-click.
    *   **Gestor de Colas Celery y Conmutador de Prioridades (`/tasks/queues`):** Inspección en tiempo real de tareas en espera en colas (`gpus_high`, `gpus_medium`, `gpus_low`, colas privadas), con botones para promover prioridad a HIGH o purgar tareas antes de ejecutarse.
    *   **Telemetría Granular a Nivel de Época:** Extracción y representación en barras de progreso en tiempo real de época actual, épocas totales, loss actual y precisión Top-1.
    *   **Diagnóstico Post-Mortem de Causa Raíz (`/tasks/{study_id}/diagnostics`):** Diagnóstico automatizado de fallos en entrenamientos (detección de CUDA Out-Of-Memory OOM, fallos de montaje Samba CIFS, salidas anómalas de contenedor) con guías de remediación.
    *   **Distinción de Runtime de Orquestación:** Identificación visual de nodos ejecutándose bajo `[☸️ Kubernetes (RKE2/K3s)]` vs `[🐳 Docker Standalone]` en las tarjetas de inventario.
    *   **Reconexión y Modernización de `tasks_view.py`:** Incorporación de la vista completa de gestión de colas, logs y diagnóstico dentro de la navegación principal de `app.py`.
*   **v1.6.0 (2026-10-07):**
    *   **Arquitectura WPipe de microservicios:** API (`api/`) e interfaz (`ui/`) separadas en carpetas propias, cada una con `Dockerfile`, `requirements.txt` y orquestador WPipe (`main.py`, `dto/`, `states/`).
    *   **Docker Compose + Makefile:** Stack con healthchecks, red privada y arranque ordenado (la UI espera a la API). Imágenes `wisrovi/train_service:cluster_admin_api_v1.6.0` y `wisrovi/train_service:cluster_admin_ui_v1.6.0`.
    *   **Configuración externa:** `control_host.env.example` para Redis, JWT y credenciales del administrador.
    *   **Versión única:** `__version__` centralizado en los paquetes `backend` y `frontend` (API, Swagger y barra lateral).
    *   Tests en Docker: 23/23 pasando (nuevas suites para los pipelines WPipe de API y UI).
*   **v1.5.1 (2026-10-07):**
    *   **Interfaz 100% en inglés profesional:** Traducción completa de las 10 vistas (navegación, login, títulos, métricas, tablas, botones, mensajes y reportes exportados) y de los mensajes del backend mostrados en la UI (alertas del watchdog, razones del Smart Dispatcher, diagnósticos, auditoría FinOps, webhooks).
    *   **Corrección de prioridad en despacho:** La etiqueta `🔥 URGENT` ahora envía `URGENT` al API (antes enviaba `URGENTE`, no reconocido por el esquema).
    *   Filtros de historial aceptan el centinela `All` (compatibilidad retroactiva con `Todos`).
    *   Tests contenerizados en Docker: 7/7 pasando.
*   **v1.5.0 (2026-10-07):**
    *   **Evolución a NeuralForge Cluster Admin:** Reestructuración de la suite bajo el principio de responsabilidad única (Single Responsibility Principle) en 10 vistas operativas dedicadas.
    *   **Almacenamiento y Volúmenes (`/cluster/storage/inspect`):** Monitoreo integral de montajes Samba CIFS para datasets, cuotas y métricas de objetos en buckets de MinIO S3, y pruebas dinámicas de latencia I/O.
    *   **FinOps y Energía - Green AI (`/cluster/finops`, `/cluster/finops/rate`):** Seguimiento de gasto en EUR por modelo de GPU según tarifas configurables (€/kWh), proyección mensual y certificado de neutralidad de carbono.
    *   **Auditoría y Seguridad Administrativa (`/cluster/audit/logs`):** Registro inmutable en Redis con trazabilidad de cambios de límites, pausas, drenados, despachos y sesiones, exportable a CSV.
    *   **Catálogo de Capacidades del Clúster (`/cluster/capabilities`):** Gobernanza y estado de los 12 módulos de I+D del ecosistema (XAI Grad-CAM/Eigen-CAM, ataques adversariales, cuantificación de incertidumbre, generalización de dominio) vinculados a papers científicos.
    *   Tests contenerizados en Docker con 100% de éxito y 77% de cobertura de código.
*   **v1.4.0 (2026-10-07):**
    *   **Diagnóstico Profundo de Nodos:** Endpoint `/invokers/{ip}/diagnose` y botón interactivo `🔍 Diagnosticar` que verifica socket SSH en puerto 22, presencia activa en Celery y provee sugerencias de auto-healing.
    *   **Green AI & Eficiencia Energética:** Endpoint `/cluster/green-ai` que cuantifica kWh consumidos, emisiones de CO₂e según TDP de GPU, árboles equivalentes compensados y velocidad por vatio (`img/W`).
    *   **Sistema de Prioridades en Despacho:** Soporte para niveles de prioridad (`⚡ NORMAL`, `🔥 URGENTE`, `📦 BATCH`) en el despachador de tareas y persistencia en configuración de estudio.
    *   **Watchdog Activo Proactivo:** Endpoint `/cluster/watchdog/check-and-alert` con escaneo proactivo bajo demanda y disparo instantáneo de alertas estructuradas a Webhooks (Discord, Slack, Telegram).
    *   **Comparador Head-to-Head:** Nueva pestaña en Historial con endpoint `/tasks/compare` para contrastar side-by-side de 2 a 5 estudios determinando automáticamente el modelo con mejor precisión y rendimiento.
    *   **Manifiesto de Reproducción en 1-Click:** Endpoint `/tasks/{id}/reproducibility` que genera el comando exacto `docker run ...` y archivo `training.yaml` con huella criptográfica SHA256 para réplica exacta de experimentos.
    *   Tests contenerizados en Docker con 100% de aprobación y cobertura incrementada al 75%.
*   **v1.3.0 (2026-10-07):**
    *   **Arquitectura de Navegación Descongestionada en 6 Vistas:** Desacoplamiento de la interfaz previa de 4 pestañas hacia 6 vistas independientes y reactivas: `📊 Centro de Operaciones`, `⚙️ Nodos Invoker`, `🚀 Despacho y Tareas`, `📈 Historial y Optuna`, `🏆 Rendimiento de GPUs` y `🛠️ Mantenimiento y Ajustes`.
    *   **Despacho Inteligente de Tareas (Smart Dispatcher):** Endpoint `/recommend-node` y selector asistido "🪄 Recomendar Mejor Nodo" basado en requerimientos de VRAM del modelo YOLO seleccionado, carga actual del nodo y heurística de balance para no saturar GPUs de alta gama.
    *   **Leaderboard de Rendimiento de GPUs:** Endpoint `/gpu-benchmarks` y panel visual con throughput empírico (img/s) y tiempo estimado por 100 épocas en GPUs RTX 4090, 4060, 3060, 3050 OEM y GTX 1650.
    *   **Tendencias de Carga de Trabajo (Workload Trends):** Gráficos horarios interactivos en Vega/Altair que identifican horas pico y valles de entrenamiento en el clúster.
    *   **Cluster Housekeeping & Purga de Redis:** Inspección de memoria usada de Redis y eliminación segura de estudios fallidos o huérfanos con liberación estimada de memoria.
    *   **Exportador de Informes de Estudios (1-Click Exporter):** Generación y descarga directa en formatos Markdown estructurado (`.md`) y tabla plana (`.csv`) desde la vista de Historial y Optuna.
    *   **Estética Cyber / Operations Deck:** Inyección de tipografías monospace, bordes con sutil resplandor cian y acentos oscuros de centro de operaciones.
    *   Tests unitarios en Docker pasando al 100% y 72% de cobertura de código.
*   **v1.2.0 (2026-10-07):**
    *   **Watchdog Basado en Celery en Vivo:** Inspección activa mediante `active_queues()` de Celery que reporta con precisión milimétrica los 12 invokers saludables en línea y detecta de inmediato el único nodo desconectado (`192.168.1.77`), erradicando falsos positivos de nodos zombies.
    *   **Monitoreo de Almacenamiento:** Integración de tarjetas de estado para Samba CIFS y MinIO S3 dentro del Watchdog de Salud.
    *   **Resolución Completa de VRAM:** Incorporación de RTX 3050 OEM, GTX 1650/1660, series RTX 2000 y GPUs Enterprise (A2000, A4000, A5000, A6000), garantizando que ningún nodo reporte "unknown".
    *   **Topología Visual de Servidores (Rack Grid):** Selector interactivo entre Tabla Resumen y Cuadrícula visual de Servidores con barras de consumo y especificaciones de hardware.
    *   **Filtros Avanzados y Acciones en Lote en Nodos:** Filtros por estado (`Todos`, `Solo Activos`, `Solo Pausados`, `En Drenado`), por modelo de GPU, por VRAM mínima (`≥8GB`, `≥12GB`, `≥24GB`), ordenación y botones de pausa/reanudación en lote.
    *   **Perfiles Rápidos de Recursos (Presets 1-Click):** Botones `🚀 Máximo (90%)`, `⚖️ Equilibrado (50%)` y `🍃 Silencioso (25%)` por nodo.
    *   **Sistema de Webhooks de Alerta:** Configuración y envío de notificaciones automáticas para Discord, Slack y Telegram.
    *   **Estimador Dinámico de Duración (ETA):** Cálculo en tiempo real de tiempo de entrenamiento, throughput estimado y GPU sugerida antes de despachar tareas.
    *   Tests unitarios en Docker pasando al 100% y 70% de cobertura total de código.
*   **v1.1.0 (2026-10-07):**
    *   Corrección de resolución de VRAM inicial.
    *   Banner de estado de colas públicas (Activa, Pausa, Drenado).
    *   Filtros en historial de estudios y selector `👤 Solo mis estudios`.
    *   Lanzador rápido de pruebas de verificación.
    *   Curvas de aprendizaje de Optuna.
*   **v1.0.0 (2026-10-07):**
    *   Lanzamiento inicial de la plataforma de control del cluster.
    *   Backend FastAPI con autenticación JWT y persistencia en Redis.
    *   Auto-inicialización (seed) de credenciales `wisrovi:wyoloservice`.
    *   Gestión dinámica de recursos (`MAX_GPU`, RAM, CPU cores).
    *   Frontend Streamlit interactivo.

---

<sub>Generated by WPipe MCP by wisrovi</sub>
