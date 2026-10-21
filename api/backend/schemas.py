"""Pydantic request and response schemas for Cluster Control API."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


# --- Auth Schemas ---

class LoginRequest(BaseModel):
    username: str = Field(..., json_schema_extra={"example": "wisrovi"})
    password: str = Field(..., json_schema_extra={"example": "wyoloservice"})


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    username: str


class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str


class UserResponse(BaseModel):
    username: str
    authenticated: bool = True


# --- Invoker Schemas ---

class InvokerLimitsUpdate(BaseModel):
    max_gpu_percent: Optional[float] = Field(None, ge=5.0, le=100.0, description="Max GPU/VRAM % (5-100)")
    max_ram: Optional[str] = Field(None, description="Max RAM allocation string (e.g. 16g, 24g)")
    max_cpu_cores: Optional[float] = Field(None, ge=1.0, le=128.0, description="Max CPU cores allocated to executor")


class InvokerPauseRequest(BaseModel):
    action: str = Field(..., pattern="^(pause|resume)$", description="'pause' or 'resume'")
    mode: str = Field("temporal", pattern="^(temporal|perpetual)$", description="'temporal' or 'perpetual'")
    hours: float = Field(4.0, ge=0.5, le=168.0, description="Hours for temporal pause")


class BatchLimitsUpdate(BaseModel):
    max_gpu_percent: Optional[float] = Field(None, ge=5.0, le=100.0)
    max_ram: Optional[str] = None
    max_cpu_cores: Optional[float] = None
    worker_ips: Optional[List[str]] = Field(None, description="Optional target IPs; if empty, applies to all online")


class PhysicalSpecs(BaseModel):
    gpu_model: str
    gpu_count: int
    gpu_memory_total: str
    ram_total: str
    cpu_cores: str


class LimitSpecs(BaseModel):
    max_gpu_percent: float
    max_ram: str
    max_cpu_cores: float


class InvokerDetailResponse(BaseModel):
    worker_ip: str
    hostname: str
    status: str
    pause_state: str
    pause_until: str
    orchestration_runtime: Optional[str] = "Docker Standalone"
    physical: PhysicalSpecs
    limits: LimitSpecs
    last_seen: str
    updated_at: str


# --- Tasks Schemas ---

class TaskResponse(BaseModel):
    study_id: str
    study_name: Optional[str] = None
    author: Optional[str] = None
    status: str
    model: str
    task_type: str
    invoker: str
    destination_node: Optional[str] = None
    worker_ip: Optional[str] = None
    dataset: Optional[str] = None
    progress: Dict[str, Any]
    active_trial: Optional[Dict[str, Any]]
    start_time: Optional[str]
    error: Optional[Dict[str, Any]]


class QuickLaunchRequest(BaseModel):
    worker_ip: Optional[str] = Field(None, description="Target invoker IP; if empty, routed to public wyolo_gpu_queue")
    model: str = Field("yolov8n-cls.pt", description="YOLO base model")
    dataset: str = Field("/examples/colorball.v8i.multiclass/", description="Dataset path")
    epochs: int = Field(1, ge=1, le=10, description="Verification epochs")
    priority: str = Field("NORMAL", description="Task priority: URGENT, NORMAL, or BATCH")


class DrainRequest(BaseModel):
    reason: Optional[str] = Field("Maintenance", description="Reason for draining node")


# --- Overview Schema ---

class WebhookConfigRequest(BaseModel):
    webhook_url: str = Field(..., description="Webhook endpoint URL (Discord, Telegram, Slack, generic)")
    enabled: bool = Field(True, description="Whether notifications are enabled")


class ClusterHealthResponse(BaseModel):
    redis_status: str
    redis_latency_ms: float
    total_nodes: int
    healthy_nodes: int
    zombie_nodes: List[str]
    storage_samba: str = "healthy"
    storage_minio: str = "healthy"
    timestamp: str


class ClusterOverviewResponse(BaseModel):
    total_nodes: int
    online_nodes: int
    active_nodes: int
    paused_nodes: int
    total_gpus: int
    active_trials_count: int
    invokers: List[Dict[str, Any]]
    timestamp: str


# --- Smart Dispatch & Benchmark Schemas ---

class SmartDispatchRecommendation(BaseModel):
    target_ip: str
    hostname: str
    gpu_model: str
    vram_total: str
    score: float
    reason: str


class GpuBenchmarkItem(BaseModel):
    gpu_model: str
    completed_studies_count: int
    avg_throughput_img_s: float
    avg_epoch_seconds: float
    estimated_100_epochs_min: float
    sample_workers: List[str]


class GpuLeaderboardResponse(BaseModel):
    benchmarks: List[GpuBenchmarkItem]
    updated_at: str


# --- Housekeeping & Trends Schemas ---

class HousekeepingPreviewResponse(BaseModel):
    stale_failed_studies_count: int
    stale_study_ids: List[str]
    redis_memory_human: str
    estimated_reclaimed_kb: int


class HousekeepingPurgeResponse(BaseModel):
    purged_studies_count: int
    status: str
    message: str


class WorkloadTrendsResponse(BaseModel):
    hourly_distribution: Dict[str, int]
    daily_distribution: Dict[str, int]
    busiest_hour: str
    total_analyzed: int


# --- v1.4.0 Optimization Schemas ---

class NodeDiagnosticResponse(BaseModel):
    worker_ip: str
    hostname: str
    status: str
    ping_ok: bool
    ssh_port_open: bool
    celery_active: bool
    latency_ms: Optional[float]
    diagnostic_summary: str
    suggested_actions: List[str]


class GreenAiMetricsResponse(BaseModel):
    total_training_hours: float
    estimated_kwh: float
    estimated_co2_kg: float
    trees_offset_equivalent: float
    avg_efficiency_img_per_watt: float
    gpu_breakdown: List[Dict[str, Any]]
    calculation_basis: str


class StudyCompareRequest(BaseModel):
    study_ids: List[str] = Field(..., min_length=2, max_length=5, description="List of study IDs to compare (2 to 5)")


class StudyCompareResponse(BaseModel):
    studies: List[Dict[str, Any]]
    common_model: Optional[str]
    best_study_id: Optional[str]
    comparison_summary: str


class WatchdogAlertResponse(BaseModel):
    status: str
    alerts_detected: List[str]
    webhook_sent: bool
    details: Dict[str, Any]
    timestamp: str


class ReproducibilityResponse(BaseModel):
    study_id: str
    docker_run_command: str
    training_yaml: str
    sha256_fingerprint: str
    generated_at: str


# --- Cluster Admin v1.5.0 Schemas ---

class StorageVolumeInfo(BaseModel):
    name: str
    mount_path: str
    status: str
    total_gb: float
    used_gb: float
    free_gb: float
    percent_used: float
    latency_ms: Optional[float]
    permissions: str = "read/write"


class MinioBucketInfo(BaseModel):
    name: str
    objects_count: int
    size_mb: float
    status: str


class ClusterStorageResponse(BaseModel):
    volumes: List[StorageVolumeInfo]
    minio_buckets: List[MinioBucketInfo]
    overall_status: str
    last_checked: str


class ElectricityRateUpdate(BaseModel):
    rate_eur_per_kwh: float = Field(0.18, ge=0.01, le=2.0, description="Cost in EUR per kWh")
    currency: str = Field("EUR", description="Currency symbol")


class FinOpsReportResponse(BaseModel):
    total_kwh: float
    rate_eur_per_kwh: float
    total_cost_eur: float
    currency: str
    gpu_cost_breakdown: List[Dict[str, Any]]
    projected_monthly_cost_eur: float
    timestamp: str


class AuditLogEntry(BaseModel):
    event_id: str
    timestamp: str
    user: str
    action: str
    target: str
    details: str
    status: str = "success"


class AuditLogResponse(BaseModel):
    logs: List[AuditLogEntry]
    total_events: int


class ClusterCapabilityModule(BaseModel):
    module_id: str
    name: str
    category: str
    description: str
    enabled: bool
    research_tier: str


class ClusterCapabilitiesResponse(BaseModel):
    modules: List[ClusterCapabilityModule]
    docker_image: str
    total_modules: int
    active_modules: int


# --- Cluster Admin v1.7.0 Enhanced Schemas ---

class GpuProcessInfo(BaseModel):
    pid: int
    name: str
    vram_used_mb: float
    elapsed: str
    is_zombie: bool = False
    zombie_reason: Optional[str] = None


class NodeGpuProcessesResponse(BaseModel):
    worker_ip: str
    hostname: str
    gpu_model: str
    total_vram_mb: float
    used_vram_mb: float
    free_vram_mb: float
    processes: List[GpuProcessInfo]
    has_zombies: bool = False


class KillProcessResponse(BaseModel):
    status: str
    message: str
    pid: int
    worker_ip: str


class QueuedTaskInfo(BaseModel):
    task_id: str
    study_id: Optional[str] = None
    study_name: Optional[str] = None
    author: Optional[str] = None
    model: Optional[str] = None
    dataset: Optional[str] = None
    priority: str = "low"
    queue_name: str
    queued_at: Optional[str] = None


class QueueStatusResponse(BaseModel):
    queues: Dict[str, int]
    total_queued: int
    tasks: List[QueuedTaskInfo]


class PromoteTaskRequest(BaseModel):
    target_queue: str = Field("gpus_high", description="Target priority queue (e.g. gpus_high, gpus_medium)")


class TaskDiagnosticsResponse(BaseModel):
    study_id: str
    status: str
    error: Optional[str] = None
    root_cause: Optional[str] = None
    suggested_action: Optional[str] = None
    timestamp: Optional[str] = None


class TaskLogsResponse(BaseModel):
    study_id: str
    worker_ip: Optional[str] = None
    source: str
    logs: List[str]
    total_lines: int


