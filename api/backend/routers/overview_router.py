"""Cluster overview endpoints."""

from fastapi import APIRouter, Depends, Query

from backend.auth import get_current_user
from backend.redis_client import ClusterRepository
from backend.schemas import (
    AuditLogResponse,
    AvailableDatasetsResponse,
    BroadcastPullResponse,
    ClusterCapabilitiesResponse,
    ClusterHealthResponse,
    ClusterImagesResponse,
    ClusterOverviewResponse,
    ClusterStorageResponse,
    DatasetInspectionResponse,
    DatasetValidationRequest,
    ElectricityRateUpdate,
    FinOpsReportResponse,
    GreenAiMetricsResponse,
    K8sPurgeResponse,
    RichWebhookResponse,
    RichWebhookTestRequest,
    SchedulerPolicy,
    SchedulerPolicyResponse,
    SmokeTestResponse,
    SupportBundleResponse,
    WatchdogAlertResponse,
    WebhookConfigRequest,
)


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
        title="Cluster Notification Test",
        message=f"Test notification successfully sent by operator {current_user}.",
        level="info",
    )
    return {
        "status": "success" if success else "failed",
        "message": "Notification sent" if success else "Failed to send notification or webhook is disabled",
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


@router.get("/green-ai", response_model=GreenAiMetricsResponse)
async def get_green_ai_metrics(current_user: str = Depends(get_current_user)):
    """Calculates cluster carbon footprint (kg CO2e) and cumulative energy consumption (kWh)."""
    repo = ClusterRepository()
    return repo.get_green_ai_metrics()


@router.post("/watchdog/check-and-alert", response_model=WatchdogAlertResponse)
async def check_and_alert_watchdog(current_user: str = Depends(get_current_user)):
    """Runs proactive health check and fires webhook notifications if critical alerts detected."""
    repo = ClusterRepository()
    return repo.check_and_trigger_watchdog_alerts()


# --- Cluster Admin Endpoints ---

@router.get("/storage/inspect", response_model=ClusterStorageResponse)
async def get_cluster_storage_admin(current_user: str = Depends(get_current_user)):
    """Admin inspect of cluster storage volumes, disk capacity and MinIO S3 buckets."""
    repo = ClusterRepository()
    return repo.get_cluster_storage_admin()


@router.get("/finops", response_model=FinOpsReportResponse)
async def get_cluster_finops_report(current_user: str = Depends(get_current_user)):
    """Cluster FinOps report calculating electricity costs in EUR and projected expenses."""
    repo = ClusterRepository()
    return repo.get_cluster_finops()


@router.post("/finops/rate")
async def update_electricity_rate(
    payload: ElectricityRateUpdate,
    current_user: str = Depends(get_current_user),
):
    """Updates the electricity billing rate per kWh in Redis."""
    repo = ClusterRepository()
    return repo.set_electricity_rate(rate_eur_per_kwh=payload.rate_eur_per_kwh, user=current_user)


@router.get("/audit/logs", response_model=AuditLogResponse)
async def get_audit_logs(
    limit: int = Query(50, ge=1, le=200),
    current_user: str = Depends(get_current_user),
):
    """Retrieves chronological audit trail of all cluster administrative operations."""
    repo = ClusterRepository()
    logs = repo.get_admin_audit_logs(limit=limit)
    return {"logs": logs, "total_events": len(logs)}


@router.get("/capabilities", response_model=ClusterCapabilitiesResponse)
async def get_cluster_capabilities(current_user: str = Depends(get_current_user)):
    """Admin catalog of official R&D modules, execution engines and extension tiers."""
    repo = ClusterRepository()
    return repo.get_cluster_capabilities()


@router.post("/smoke-test", response_model=SmokeTestResponse)
async def run_cluster_smoke_test(current_user: str = Depends(get_current_user)):
    """Executes a 1-click comprehensive smoke test across all online invoker nodes."""
    repo = ClusterRepository()
    return repo.run_cluster_smoke_test(user=current_user)


@router.post("/k8s/purge-stale-pods", response_model=K8sPurgeResponse)
async def purge_stale_k8s_pods(current_user: str = Depends(get_current_user)):
    """Purges stale, failed, evicted, or terminating K8s pods across all invokers."""
    repo = ClusterRepository()
    return repo.purge_stale_k8s_pods(user=current_user)


# --- Enterprise Management Suite Endpoints (v2.0.0) ---

@router.get("/images/status", response_model=ClusterImagesResponse)
async def get_cluster_images_status(
    target_image: str = Query("wisrovi/train_service:worker_executor_v1.0.0"),
    current_user: str = Depends(get_current_user),
):
    """Returns Docker/K8s image synchronization status across all cluster invokers."""
    repo = ClusterRepository()
    return repo.get_cluster_images_status(target_image=target_image)


@router.post("/images/broadcast-pull", response_model=BroadcastPullResponse)
async def broadcast_docker_pull(
    target_image: str = Query("wisrovi/train_service:worker_executor_v1.0.0"),
    current_user: str = Depends(get_current_user),
):
    """Triggers cluster-wide broadcast docker pull strictly excluding the NAS manager."""
    repo = ClusterRepository()
    return repo.trigger_broadcast_docker_pull(target_image=target_image, user=current_user)


@router.get("/datasets/inspect", response_model=DatasetInspectionResponse)
async def inspect_dataset(
    dataset_path: str = Query(..., description="Path to dataset directory"),
    current_user: str = Depends(get_current_user),
):
    """Pre-flight check for dataset directory validating data.yaml, class counts, and train/val splits."""
    repo = ClusterRepository()
    return repo.inspect_dataset(dataset_path=dataset_path)


@router.post("/datasets/validate", response_model=DatasetInspectionResponse)
async def validate_dataset(
    payload: DatasetValidationRequest,
    current_user: str = Depends(get_current_user),
):
    """Validates dataset path and splits prior to study dispatch."""
    repo = ClusterRepository()
    return repo.inspect_dataset(dataset_path=payload.dataset_path)


@router.get("/datasets/available", response_model=AvailableDatasetsResponse)
async def get_available_datasets(
    base_path: str = Query("/examples"),
    current_user: str = Depends(get_current_user),
):
    """Discovers available datasets on local filesystem and CIFS mounts."""
    repo = ClusterRepository()
    return repo.list_available_datasets(base_path=base_path)


@router.get("/scheduler/policy", response_model=SchedulerPolicyResponse)
async def get_scheduler_policy(current_user: str = Depends(get_current_user)):
    """Retrieves the Day/Night automated scheduler policy and active mode."""
    repo = ClusterRepository()
    return repo.get_scheduler_policy()


@router.post("/scheduler/policy", response_model=SchedulerPolicyResponse)
async def update_scheduler_policy(
    payload: SchedulerPolicy,
    current_user: str = Depends(get_current_user),
):
    """Configures and saves Day/Night scheduling profiles in Redis."""
    repo = ClusterRepository()
    return repo.set_scheduler_policy(payload.model_dump(), user=current_user)


@router.post("/scheduler/apply-policy")
async def apply_scheduler_policy(current_user: str = Depends(get_current_user)):
    """Enforces current day/night schedule profile across all target invoker nodes immediately."""
    repo = ClusterRepository()
    return repo.apply_scheduler_policy(user=current_user)


@router.get("/support-bundle", response_model=SupportBundleResponse)
async def get_support_bundle(current_user: str = Depends(get_current_user)):
    """Generates an exportable JSON diagnostic support bundle for offline debugging."""
    repo = ClusterRepository()
    return repo.generate_support_bundle(user=current_user)


@router.post("/webhook/test-rich", response_model=RichWebhookResponse)
async def test_rich_webhook(
    payload: RichWebhookTestRequest,
    current_user: str = Depends(get_current_user),
):
    """Tests rich Discord/Slack embed notification delivery."""
    repo = ClusterRepository()
    return repo.send_rich_webhook(event_type=payload.event_type, webhook_url=payload.webhook_url)





