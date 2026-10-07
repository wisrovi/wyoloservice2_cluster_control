# NeuralForge Cluster Admin - Streamlit UI service (WPipe startup pipeline)
FROM python:3.10-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app \
    STREAMLIT_PORT=8501 \
    STREAMLIT_ADDRESS=0.0.0.0 \
    CLUSTER_API_URL=http://cluster_admin_api:8001

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

COPY ui/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY ui/ ./

EXPOSE 8501

HEALTHCHECK --interval=15s --timeout=5s --start-period=30s --retries=5 \
    CMD curl -fsS "http://localhost:${STREAMLIT_PORT}/_stcore/health" || exit 1

CMD ["python", "main.py"]
