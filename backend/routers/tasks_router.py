"""Tasks and trials monitoring endpoints."""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status

from backend.auth import get_current_user
from backend.redis_client import ClusterRepository
from backend.schemas import (
    QuickLaunchRequest,
    ReproducibilityResponse,
    StudyCompareRequest,
    StudyCompareResponse,
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
