"""Invoker nodes management endpoints."""

from typing import Any, Dict, List
from fastapi import APIRouter, Depends, HTTPException, status

from backend.auth import get_current_user
from backend.redis_client import ClusterRepository, get_redis_client
from backend.schemas import (
    BatchLimitsUpdate,
    InvokerDetailResponse,
    InvokerLimitsUpdate,
    InvokerPauseRequest,
)


router = APIRouter(prefix="/api/v1/invokers", tags=["Invokers"])


@router.get("", response_model=List[Dict[str, Any]])
async def list_invokers(current_user: str = Depends(get_current_user)):
    """Lists all invoker nodes with physical telemetry and dynamic limits."""
    repo = ClusterRepository()
    return repo.list_invokers()


@router.get("/{worker_ip}")
async def get_invoker_detail(worker_ip: str, current_user: str = Depends(get_current_user)):
    """Returns detailed information for a single invoker node."""
    repo = ClusterRepository()
    data = repo.get_invoker(worker_ip)
    if not data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Invoker {worker_ip} not found",
        )
    return data


@router.put("/{worker_ip}/limits")
async def update_limits(
    worker_ip: str,
    payload: InvokerLimitsUpdate,
    current_user: str = Depends(get_current_user),
):
    """Updates dynamic resource limits (MAX_GPU %, RAM, CPU cores) for an invoker node."""
    repo = ClusterRepository()
    existing = repo.get_invoker(worker_ip)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Invoker {worker_ip} not found",
        )

    updated = repo.update_invoker_limits(
        worker_ip=worker_ip,
        max_gpu_percent=payload.max_gpu_percent,
        max_ram=payload.max_ram,
        max_cpu_cores=payload.max_cpu_cores,
    )
    return {
        "status": "success",
        "message": f"Updated limits for invoker {worker_ip}",
        "data": updated,
    }


@router.post("/{worker_ip}/pause")
async def pause_or_resume(
    worker_ip: str,
    payload: InvokerPauseRequest,
    current_user: str = Depends(get_current_user),
):
    """Pauses (temporal / perpetual) or resumes public task consumption on an invoker node."""
    repo = ClusterRepository()
    existing = repo.get_invoker(worker_ip)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Invoker {worker_ip} not found",
        )

    updated = repo.set_invoker_pause(
        worker_ip=worker_ip,
        action=payload.action,
        mode=payload.mode,
        hours=payload.hours,
    )
    return {
        "status": "success",
        "message": f"Executed '{payload.action}' on invoker {worker_ip}",
        "data": updated,
    }


@router.post("/batch-limits")
async def batch_update_limits(
    payload: BatchLimitsUpdate,
    current_user: str = Depends(get_current_user),
):
    """Updates dynamic limits across multiple or all online invokers at once."""
    repo = ClusterRepository()
    all_invokers = repo.list_invokers()
    target_ips = payload.worker_ips or [i["worker_ip"] for i in all_invokers]

    updated_count = 0
    for ip in target_ips:
        repo.update_invoker_limits(
            worker_ip=ip,
            max_gpu_percent=payload.max_gpu_percent,
            max_ram=payload.max_ram,
            max_cpu_cores=payload.max_cpu_cores,
        )
        updated_count += 1

    return {
        "status": "success",
        "message": f"Successfully updated limits on {updated_count} invoker nodes",
        "target_ips": target_ips,
    }
