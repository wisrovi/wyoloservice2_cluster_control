"""Tasks and trials monitoring endpoints."""

from typing import Any, Dict, List
from fastapi import APIRouter, Depends, HTTPException, Query, status

from backend.auth import get_current_user
from backend.redis_client import ClusterRepository


router = APIRouter(prefix="/api/v1/tasks", tags=["Tasks"])


@router.get("/active", response_model=List[Dict[str, Any]])
async def get_active_tasks(current_user: str = Depends(get_current_user)):
    """Retrieves all currently active trials and training runs across the cluster."""
    repo = ClusterRepository()
    return repo.list_active_tasks()


@router.get("/history", response_model=List[Dict[str, Any]])
async def get_task_history(
    limit: int = Query(50, ge=1, le=200),
    current_user: str = Depends(get_current_user),
):
    """Retrieves recent studies and training history."""
    repo = ClusterRepository()
    return repo.list_all_studies(limit=limit)


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
