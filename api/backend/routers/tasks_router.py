"""Tasks and trials monitoring endpoints."""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status

from backend.auth import get_current_user
from backend.redis_client import ClusterRepository
from backend.schemas import (
    K8sPodEventsResponse,
    KillPodResponse,
    PromoteTaskRequest,
    QuarantineActionResponse,
    QuarantineListResponse,
    QueueStatusResponse,
    QuickLaunchRequest,
    ReassignTaskRequest,
    ReproducibilityResponse,
    StudyCompareRequest,
    StudyCompareResponse,
    SweepActionResponse,
    SweepsListResponse,
    TaskDiagnosticsResponse,
    TaskLogsResponse,
)


router = APIRouter(prefix="/api/v1/tasks", tags=["Tasks"])


@router.get("/active", response_model=List[Dict[str, Any]])
async def get_active_tasks(current_user: str = Depends(get_current_user)):
    """Retrieves all currently active trials and training runs across the cluster."""
    repo = ClusterRepository()
    return repo.list_active_tasks()


@router.get("/history", response_model=List[Dict[str, Any]])
async def get_task_history(
    limit: int = Query(50, ge=1, le=200),
    search: Optional[str] = Query(None, description="Search term for study ID, study name, dataset or model"),
    author: Optional[str] = Query(None, description="Filter by study author / submitter"),
    worker_ip: Optional[str] = Query(None, description="Filter by destination invoker node IP"),
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status: running, completed, failed"),
    current_user: str = Depends(get_current_user),
):
    """Retrieves recent studies and training history with multi-field filtering."""
    repo = ClusterRepository()
    return repo.list_all_studies(
        limit=limit,
        search=search,
        author=author,
        worker_ip=worker_ip,
        status=status_filter,
    )


@router.post("/compare", response_model=StudyCompareResponse)
async def compare_studies(
    payload: StudyCompareRequest,
    current_user: str = Depends(get_current_user),
):
    """Performs side-by-side head-to-head comparison of multiple training studies."""
    repo = ClusterRepository()
    return repo.compare_studies(payload.study_ids)


@router.get("/{study_id}/reproducibility", response_model=ReproducibilityResponse)
async def get_study_reproducibility(
    study_id: str,
    current_user: str = Depends(get_current_user),
):
    """Returns reproducible docker run command and YAML manifest for study."""
    repo = ClusterRepository()
    return repo.get_study_reproducibility(study_id)


@router.get("/{study_id}/metrics", response_model=List[Dict[str, Any]])
async def get_study_metrics(
    study_id: str,
    current_user: str = Depends(get_current_user),
):
    """Returns trial metrics progression for Optuna Plotly visualization."""
    repo = ClusterRepository()
    return repo.get_study_trials_metrics(study_id)


@router.post("/quick-launch")
async def quick_launch_task(
    payload: QuickLaunchRequest,
    current_user: str = Depends(get_current_user),
):
    """Launches a quick 1-trial test job to verify node/cluster execution."""
    repo = ClusterRepository()
    result = repo.quick_launch_test(
        worker_ip=payload.worker_ip,
        user=current_user,
        model=payload.model,
        dataset=payload.dataset,
        epochs=payload.epochs,
        priority=payload.priority,
        task=payload.task,
        imgsz=payload.imgsz,
        batch_size=payload.batch_size,
    )
    return {
        "status": "success",
        "message": f"Quick test '{result['study_name']}' [{payload.priority.upper()}] dispatched to queue '{result['target_queue']}'",
        "data": result,
    }


@router.post("/{study_id}/cancel")
async def cancel_task(study_id: str, current_user: str = Depends(get_current_user)):
    """Cancels a currently executing study / training trial."""
    repo = ClusterRepository()
    success = repo.cancel_study(study_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to cancel study {study_id}",
        )
    return {
        "status": "success",
        "message": f"Study {study_id} marked as cancelled and stop broadcast sent.",
    }


# --- Queue Inspection & Priority Management ---

@router.get("/queues", response_model=QueueStatusResponse)
async def get_celery_queues(current_user: str = Depends(get_current_user)):
    """Inspects pending jobs across Celery queues (gpus_high, gpus_medium, gpus_low, etc.)."""
    repo = ClusterRepository()
    return repo.get_celery_queues()


@router.post("/queues/{task_id}/promote")
async def promote_celery_task(
    task_id: str,
    payload: PromoteTaskRequest = PromoteTaskRequest(),
    current_user: str = Depends(get_current_user),
):
    """Promotes a queued task to a higher priority queue."""
    repo = ClusterRepository()
    res = repo.promote_celery_task(task_id, target_queue=payload.target_queue, user=current_user)
    if res.get("status") == "error":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=res.get("message", "Task not found in queues"),
        )
    return res


@router.delete("/queues/{task_id}")
async def delete_celery_task(task_id: str, current_user: str = Depends(get_current_user)):
    """Cancels and removes a pending task from Celery queues before execution starts."""
    repo = ClusterRepository()
    res = repo.delete_celery_task(task_id, user=current_user)
    if res.get("status") == "error":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=res.get("message", "Task not found in queues"),
        )
    return res


@router.post("/queues/{task_id}/reassign")
async def reassign_celery_task(
    task_id: str,
    payload: ReassignTaskRequest = ReassignTaskRequest(),
    current_user: str = Depends(get_current_user),
):
    """Reassigns a queued task from any queue to a target queue (e.g. wyolo_gpu_queue or specific node)."""
    repo = ClusterRepository()
    res = repo.reassign_celery_task(task_id, target_queue=payload.target_queue, user=current_user)
    if res.get("status") == "not_found":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=res.get("message", "Task not found in queues"),
        )
    return res



# --- Live Logs & Diagnostics ---

@router.get("/{study_id}/logs", response_model=TaskLogsResponse)
async def get_task_logs(
    study_id: str,
    limit: int = Query(200, ge=10, le=1000),
    current_user: str = Depends(get_current_user),
):
    """Retrieves real-time training or post-mortem logs for a study."""
    repo = ClusterRepository()
    return repo.get_task_logs(study_id, limit=limit)


@router.get("/{study_id}/diagnostics", response_model=TaskDiagnosticsResponse)
async def get_task_diagnostics(
    study_id: str,
    current_user: str = Depends(get_current_user),
):
    """Analyzes study errors and provides actionable root-cause diagnostics."""
    repo = ClusterRepository()
    return repo.get_task_diagnostics(study_id)


# --- K8s Pod Lifecycle & Management Endpoints (v1.9.0) ---

@router.get("/{study_id}/k8s-events", response_model=K8sPodEventsResponse)
async def get_task_k8s_events(
    study_id: str,
    current_user: str = Depends(get_current_user),
):
    """Retrieves live Kubernetes pod lifecycle events (Scheduled, Pulled, Created, OOMKilled, BackOff)."""
    repo = ClusterRepository()
    return repo.get_task_k8s_events(study_id)


@router.post("/{study_id}/kill-pod", response_model=KillPodResponse)
async def kill_task_pod(
    study_id: str,
    current_user: str = Depends(get_current_user),
):
    """Dispatches an immediate K8s Pod eviction / termination signal (gracePeriodSeconds: 0)."""
    repo = ClusterRepository()
    return repo.kill_task_pod(study_id, user=current_user)


# --- Enterprise Sweeps & DLQ Quarantine Endpoints (v2.0.0) ---

@router.get("/sweeps", response_model=SweepsListResponse)
async def get_optuna_sweeps(current_user: str = Depends(get_current_user)):
    """Retrieves all aggregated Optuna sweeps, trials, and convergence metrics."""
    repo = ClusterRepository()
    return repo.list_optuna_sweeps()


@router.post("/sweeps/{sweep_name}/cancel", response_model=SweepActionResponse)
async def cancel_optuna_sweep(
    sweep_name: str,
    current_user: str = Depends(get_current_user),
):
    """Cancels all active trials running under a specific Optuna sweep."""
    repo = ClusterRepository()
    return repo.cancel_optuna_sweep(sweep_name, user=current_user)


@router.get("/quarantine", response_model=QuarantineListResponse)
async def get_quarantined_tasks(current_user: str = Depends(get_current_user)):
    """Retrieves tasks isolated in the Dead Letter Queue (DLQ)."""
    repo = ClusterRepository()
    return repo.list_quarantined_tasks()


@router.post("/quarantine/{task_id}/retry", response_model=QuarantineActionResponse)
async def retry_quarantined_task(
    task_id: str,
    current_user: str = Depends(get_current_user),
):
    """Releases a quarantined task from DLQ and reschedules it for execution."""
    repo = ClusterRepository()
    return repo.retry_quarantined_task(task_id, user=current_user)


@router.delete("/quarantine/{task_id}", response_model=QuarantineActionResponse)
async def purge_quarantined_task(
    task_id: str,
    current_user: str = Depends(get_current_user),
):
    """Permanently purges a poisoned task from the Dead Letter Queue."""
    repo = ClusterRepository()
    return repo.purge_quarantined_task(task_id, user=current_user)



