# NeuralForge Cluster Admin - REST API service (FastAPI + WPipe startup pipeline)
FROM python:3.10-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app \
    API_HOST=0.0.0.0 \
    API_PORT=8001

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

COPY api/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY api/ ./

EXPOSE 8001

HEALTHCHECK --interval=15s --timeout=5s --start-period=20s --retries=5 \
    CMD curl -fsS "http://localhost:${API_PORT}/health" || exit 1

CMD ["python", "main.py"]
