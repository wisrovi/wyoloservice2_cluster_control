"""Cluster overview endpoints."""

from fastapi import APIRouter, Depends

from backend.auth import get_current_user
from backend.redis_client import ClusterRepository
from backend.schemas import ClusterHealthResponse, ClusterOverviewResponse


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
