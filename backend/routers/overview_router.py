"""Cluster overview endpoints."""

from fastapi import APIRouter, Depends, Query

from backend.auth import get_current_user
from backend.redis_client import ClusterRepository
from backend.schemas import ClusterHealthResponse, ClusterOverviewResponse, WebhookConfigRequest


router = APIRouter(prefix="/api/v1/cluster", tags=["Cluster"])


@router.get("/overview", response_model=ClusterOverviewResponse)
async def get_overview(current_user: str = Depends(get_current_user)):
    """Calculates cluster-wide metrics (nodes, GPUs, active trials, pause states)."""
    repo = ClusterRepository()
    return repo.get_cluster_overview()


@router.get("/health", response_model=ClusterHealthResponse)
async def get_cluster_health(current_user: str = Depends(get_current_user)):
    """Returns real-time health watchdog status: Redis latency, zombie nodes, and healthy count."""
    repo = ClusterRepository()
    return repo.get_cluster_health()


@router.get("/webhook")
async def get_webhook_config(current_user: str = Depends(get_current_user)):
    """Returns the current webhook configuration."""
    repo = ClusterRepository()
    return repo.get_webhook_config()


@router.post("/webhook")
async def save_webhook_config(
    payload: WebhookConfigRequest,
    current_user: str = Depends(get_current_user),
):
    """Saves webhook notification settings in Redis."""
    repo = ClusterRepository()
    return repo.set_webhook_config(webhook_url=payload.webhook_url, enabled=payload.enabled)


@router.post("/webhook/test")
async def test_webhook_notification(current_user: str = Depends(get_current_user)):
    """Dispatches a test notification to the configured webhook."""
    repo = ClusterRepository()
    success = repo.send_webhook_notification(
        title="Test de Notificación del Cluster",
        message=f"Prueba enviada correctamente por el operador {current_user}.",
        level="info",
    )
    return {
        "status": "success" if success else "failed",
        "message": "Notificación enviada" if success else "Fallo al enviar notificación o webhook deshabilitado",
    }


@router.get("/estimate-duration")
async def estimate_duration(
    model: str = Query("yolov8n-cls.pt"),
    epochs: int = Query(1, ge=1, le=500),
    dataset: str = Query("/examples/"),
    current_user: str = Depends(get_current_user),
):
    """Estimates training duration based on model complexity and epoch count."""
    repo = ClusterRepository()
    return repo.estimate_training_duration(model=model, epochs=epochs, dataset=dataset)


@router.get("/recommend-node")
async def recommend_node(
    model: str = Query("yolov8n-cls.pt"),
    current_user: str = Depends(get_current_user),
):
    """Smart dispatcher: recommends optimal invoker node based on workload and GPU fitness."""
    repo = ClusterRepository()
    return repo.recommend_smart_dispatch(model=model)


@router.get("/gpu-benchmarks")
async def get_gpu_benchmarks(current_user: str = Depends(get_current_user)):
    """Returns measured speed benchmarks and throughput comparison across GPU models."""
    repo = ClusterRepository()
    return repo.get_gpu_benchmarks()


@router.get("/housekeeping/preview")
async def housekeeping_preview(current_user: str = Depends(get_current_user)):
    """Inspects Redis memory and stale/failed studies ready for housekeeping."""
    repo = ClusterRepository()
    return repo.get_housekeeping_preview()


@router.post("/housekeeping/purge")
async def housekeeping_purge(current_user: str = Depends(get_current_user)):
    """Purges stale/failed study keys from Redis to reclaim memory."""
    repo = ClusterRepository()
    return repo.purge_housekeeping_studies()


@router.get("/trends")
async def get_workload_trends(current_user: str = Depends(get_current_user)):
    """Returns hourly and daily cluster workload distribution."""
    repo = ClusterRepository()
    return repo.get_workload_trends()
