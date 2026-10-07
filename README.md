# 🎛️ NeuralForge Cluster Control (`wyoloservice2_cluster_control`)

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Status](https://img.shields.io/badge/status-active-success.svg)
![Python](https://img.shields.io/badge/python-3.10-blue.svg)
![Docker](https://img.shields.io/badge/docker-ready-2496ED.svg?logo=docker)

> Centralized cluster administration, live telemetry dashboard, and dynamic hardware resource allocation platform (FastAPI + Streamlit) for the `train_service2` ecosystem.

---

## 🛠️ Tecnologías y Librerías Clave

Este microservicio combina un backend API de alto rendimiento con una interfaz gráfica interactiva y reactiva:

*   **FastAPI (v0.110+):** Framework asíncrono para el API Gateway RESTful con documentación interactiva Swagger/OpenAPI (`/docs`).
*   **Streamlit (v1.32+):** Framework frontend en Python para la interfaz visual de monitoreo, controles por nodo (sliders de VRAM, RAM, CPU) y gestión en tiempo real.
*   **Redis (v5.0+):** Almacén de datos persistente en memoria para la telemetría física (`physical_*`), límites asignados (`limits_*`) y credenciales seguras de operadores (`cluster:auth:users`).
*   **Celery (v5.3+):** Protocolo de comunicación y emisión de señales (`cancel_consumer`, `add_consumer`, `stop_study`) hacia los invokers y managers.
*   **PyJWT & Cryptography:** Generación, firma y verificación de tokens de acceso Bearer JWT para proteger las operaciones del cluster.
*   **Pydantic (v2.6+):** Validación estricta de esquemas de datos y serialización de modelos de hardware y tareas.
*   **Pytest & Pytest-Cov:** Suite de pruebas unitarias automatizadas y cálculo de cobertura de código ejecutadas dentro de contenedores Docker.
*   **Uvicorn:** Servidor ASGI de nivel de producción para el backend FastAPI.

---

## 🗺️ Arquitectura del Sistema

```mermaid
flowchart TD
    subgraph UI_Layer [Frontend Layer - Streamlit :8501]
        Login[🔐 Login View] --> Dashboard[📊 Cluster Overview]
        Dashboard --> InvokerView[⚙️ Nodos Invoker]
        Dashboard --> TasksView[🚀 Monitor de Entrenamientos]
        Dashboard --> SettingsView[🛠️ Configuración Global & Password]
    end

    subgraph API_Layer [API Gateway - FastAPI :8000]
        AuthRouter["/api/v1/auth/*"]
        InvokersRouter["/api/v1/invokers/*"]
        TasksRouter["/api/v1/tasks/*"]
        OverviewRouter["/api/v1/cluster/*"]
    end

    subgraph Data_Layer [Master Control Host 192.168.10.252]
        R[(Redis :23437)]
        CB[Celery Broker]
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
    Dashboard -.->|GET /cluster/overview| OverviewRouter

    AuthRouter <-->|cluster:auth:users| R
    InvokersRouter <-->|invoker:IP:resources| R
    InvokersRouter -.->|cancel_consumer / add_consumer| CB
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
*   **Backend API (FastAPI Swagger Docs):** [http://localhost:8000/docs](http://localhost:8000/docs)

### 2. Ejecución mediante Docker

```bash
# Construir la imagen Docker
docker build -t wisrovi/wyoloservice2_cluster_control:v1.0.0 .

# Ejecutar el contenedor
docker run -d \
  --name wyolo_cluster_control \
  -p 8000:8000 \
  -p 8501:8501 \
  -e CONTROL_HOST=192.168.10.252 \
  -e REDIS_PORT=23437 \
  wisrovi/wyoloservice2_cluster_control:v1.0.0
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
| `GET` | `/api/v1/invokers` | Lista invokers con hardware y límites | Sí |
| `GET` | `/api/v1/invokers/{ip}` | Detalle completo de un invoker | Sí |
| `PUT` | `/api/v1/invokers/{ip}/limits` | Modifica `max_gpu_percent`, `max_ram` y `max_cpu_cores` | Sí |
| `POST` | `/api/v1/invokers/{ip}/pause` | Pausa o reanuda la cola pública de un invoker | Sí |
| `POST` | `/api/v1/invokers/batch-limits` | Actualiza límites en lote en todo el cluster | Sí |
| `GET` | `/api/v1/tasks/active` | Lista entrenamientos en ejecución en tiempo real | Sí |
| `POST` | `/api/v1/tasks/{id}/cancel` | Cancela un entrenamiento y emite señal de parada | Sí |

---

## 👨‍💻 Autor & Licencia

*   **Autor:** William Steve Rodriguez Villamizar (`wisrovi`)
*   **Email:** `wisrovi.rodriguez@gmail.com`
*   **Licencia:** PolyForm Noncommercial License 1.0.0. Ver [LICENSE](LICENSE) y [COMMERCIAL.md](COMMERCIAL.md).

---

## 📝 Changelog

*   **v1.0.0 (2026-10-07):**
    *   Lanzamiento inicial de la plataforma de control del cluster.
    *   Backend FastAPI con autenticación JWT y persistencia en Redis.
    *   Auto-inicialización (seed) de credenciales `wisrovi:wyoloservice`.
    *   Gestión dinámica de recursos (`MAX_GPU`, RAM, CPU cores) sin reiniciar contenedores.
    *   Control interactivo de pausas de colas públicas y monitoreo de tareas activas.
    *   Frontend Streamlit con vistas de Overview, Invokers, Tasks y Settings.
    *   Tests unitarios y medición de cobertura dockerizados con `python:3.10-slim`.