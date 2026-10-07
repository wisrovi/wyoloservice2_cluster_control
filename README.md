# 🎛️ NeuralForge Cluster Control (`wyoloservice2_cluster_control`)

![Version](https://img.shields.io/badge/version-1.3.0-blue.svg)
![Status](https://img.shields.io/badge/status-active-success.svg)
![Python](https://img.shields.io/badge/python-3.10-blue.svg)
![Docker](https://img.shields.io/badge/docker-ready-2496ED.svg?logo=docker)

> Centralized cluster administration, live telemetry dashboard, and dynamic hardware resource allocation platform (FastAPI + Streamlit) for the `train_service2` ecosystem.

---

## 🛠️ Tecnologías y Librerías Clave

Este microservicio combina un backend API de alto rendimiento con una interfaz gráfica interactiva y reactiva:

*   **FastAPI (v0.110+):** Framework asíncrono para el API Gateway RESTful con documentación interactiva Swagger/OpenAPI (`/docs`).
*   **Streamlit (v1.32+):** Framework frontend en Python para la interfaz visual de monitoreo, controles por nodo (sliders de VRAM, RAM, CPU) y gestión en tiempo real.
*   **Redis (v5.0+):** Almacén de datos persistente en memoria para la telemetría física (`physical_*`), límites asignados (`limits_*`), credenciales seguras de operadores (`cluster:auth:users`) y configuración de alertas webhook.
*   **Celery (v5.3+):** Protocolo de comunicación para inspección en tiempo real de colas activas (`active_queues`) y emisión de señales (`cancel_consumer`, `add_consumer`, `stop_study`) hacia los invokers y managers.
*   **PyJWT & Cryptography:** Generación, firma y verificación de tokens de acceso Bearer JWT para proteger las operaciones del cluster.
*   **Pydantic (v2.6+):** Validación estricta de esquemas de datos y serialización de modelos de hardware, tareas y webhooks.
*   **Pytest & Pytest-Cov:** Suite de pruebas unitarias automatizadas y cálculo de cobertura de código ejecutadas dentro de contenedores Docker.
*   **Uvicorn:** Servidor ASGI de nivel de producción para el backend FastAPI.

---

## 🗺️ Arquitectura del Sistema

```mermaid
flowchart TD
    subgraph UI_Layer [Frontend Layer - Streamlit :8501]
        Login[🔐 Login View] --> Dashboard[📊 Cluster Overview & Rack Grid]
        Dashboard --> InvokerView[⚙️ Nodos Invoker & Presets]
        Dashboard --> TasksView[🚀 Monitor de Entrenamientos & ETA]
        Dashboard --> SettingsView[🛠️ Configuración Global, Password & Webhooks]
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
*   **Cambio de Contraseña:** El usuario puede actualizar su contraseña directamente desde la pestaña de **Configuración Global** de la interfaz.

---

## 🚀 Despliegue y Ejecución

### 1. Ejecución Local Directa

```bash
# Instalar dependencias
pip install -r requirements.txt

# Iniciar backend FastAPI y frontend Streamlit simultáneamente
./start.sh
```

Los servicios quedarán disponibles en:
*   **Interfaz de Usuario (Streamlit):** [http://localhost:8501](http://localhost:8501)
*   **Backend API (FastAPI Swagger Docs):** [http://localhost:8001/docs](http://localhost:8001/docs)

### 2. Ejecución mediante Docker

```bash
# Construir la imagen Docker
docker build -t wisrovi/wyoloservice2_cluster_control:v1.2.0 .

# Ejecutar el contenedor
docker run -d \
  --name wyolo_cluster_control \
  -p 8001:8001 \
  -p 8501:8501 \
  -e CONTROL_HOST=192.168.10.252 \
  -e REDIS_PORT=23437 \
  wisrovi/wyoloservice2_cluster_control:v1.2.0
```

---

## 🧪 Pruebas Unitarias y Cobertura

Cumpliendo con los estándares de calidad del ecosistema, todas las pruebas unitarias se ejecutan dentro de un contenedor Docker aislado (`python:3.10-slim`):

### Ejecutar Pruebas Unitarias
```bash
./run_tests.sh
```

### Calcular Cobertura de Código
```bash
./coverage.sh
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
| `GET` | `/api/v1/cluster/trends` | Distribución horaria y diaria de carga de trabajo (Workload Trends) | Sí |
| `GET` | `/api/v1/cluster/housekeeping/preview` | Inspección de memoria Redis y conteo de estudios fallidos obsoletos | Sí |
| `POST` | `/api/v1/cluster/housekeeping/purge` | Purga segura de estudios y claves efímeras huérfanas en Redis | Sí |
| `GET` | `/api/v1/invokers` | Lista invokers con hardware y límites | Sí |
| `GET` | `/api/v1/invokers/{ip}` | Detalle completo de un invoker | Sí |
| `PUT` | `/api/v1/invokers/{ip}/limits` | Modifica `max_gpu_percent`, `max_ram` y `max_cpu_cores` | Sí |
| `POST` | `/api/v1/invokers/{ip}/pause` | Pausa o reanuda la cola pública de un invoker | Sí |
| `POST` | `/api/v1/invokers/{ip}/drain` | Pone el nodo en modo drenado (finaliza tareas y pausa) | Sí |
| `POST` | `/api/v1/invokers/batch-limits` | Actualiza límites en lote en todo el cluster | Sí |
| `GET` | `/api/v1/tasks/active` | Lista entrenamientos en ejecución en tiempo real | Sí |
| `GET` | `/api/v1/tasks/history` | Historial de estudios con filtros (search, autor, nodo, status) | Sí |
| `POST` | `/api/v1/tasks/quick-launch` | Lanzador rápido de 1-click para pruebas de validación | Sí |
| `GET` | `/api/v1/tasks/{id}/metrics` | Métricas de trials para curvas de aprendizaje Optuna | Sí |
| `POST` | `/api/v1/tasks/{id}/cancel` | Cancela un entrenamiento y emite señal de parada | Sí |

---

## 👨‍💻 Autor & Licencia

*   **Autor:** William Steve Rodriguez Villamizar (`wisrovi`)
*   **Email:** `wisrovi.rodriguez@gmail.com`
*   **Licencia:** PolyForm Noncommercial License 1.0.0. Ver [LICENSE](LICENSE) y [COMMERCIAL.md](COMMERCIAL.md).

---

## 📝 Changelog

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