"""Unit tests for FastAPI endpoints in wyoloservice2_cluster_control.

This module validates:
1. Root '/' endpoint returns service information and docs URL.
2. '/health' endpoint returns status 'ok'.
3. Protected endpoints (e.g. '/api/v1/invokers', '/api/v1/cluster/overview') reject unauthenticated requests with 401 Unauthorized.
"""

import pytest
from fastapi.testclient import TestClient
from backend.app import app


@pytest.fixture
def client():
    """Provides a TestClient instance for the FastAPI application."""
    with TestClient(app) as test_client:
        yield test_client


def test_root_endpoint(client):
    """Validates the root metadata endpoint.

    What it tests:
    - Sends a GET request to '/'.
    - Confirms that the status code is 200 OK.
    - Confirms the JSON body includes service name and operational status.
    """
    response = client.get("/")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    data = response.json()
    assert data.get("service") == "wyoloservice2_cluster_control"
    assert data.get("status") == "operational"


def test_health_endpoint(client):
    """Validates the health check probe endpoint.

    What it tests:
    - Sends a GET request to '/health'.
    - Confirms that the response code is 200 OK and status is 'ok'.
    """
    response = client.get("/health")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    assert response.json() == {"status": "ok"}


def test_protected_endpoints_require_auth(client):
    """Validates that cluster control and telemetry endpoints are protected.

    What it tests:
    - Attempts to call '/api/v1/invokers' without an Authorization header.
    - Attempts to call '/api/v1/cluster/overview' without an Authorization header.
    - Attempts to call '/api/v1/cluster/health' without an Authorization header.
    - Attempts to call '/api/v1/tasks/quick-launch' without an Authorization header.
    - Verifies that all return HTTP 401 Unauthorized status.
    """
    resp_invokers = client.get("/api/v1/invokers")
    assert resp_invokers.status_code == 401, "Expected 401 Unauthorized for unauthenticated access to /api/v1/invokers"

    resp_overview = client.get("/api/v1/cluster/overview")
    assert resp_overview.status_code == 401, "Expected 401 Unauthorized for unauthenticated access to /api/v1/cluster/overview"

    resp_health = client.get("/api/v1/cluster/health")
    assert resp_health.status_code == 401, "Expected 401 Unauthorized for unauthenticated access to /api/v1/cluster/health"

    resp_quick = client.post("/api/v1/tasks/quick-launch", json={"model": "yolov8n-cls.pt"})
    assert resp_quick.status_code == 401, "Expected 401 Unauthorized for unauthenticated access to /api/v1/tasks/quick-launch"


def test_authenticated_cluster_endpoints(client):
    """Validates cluster control and watchdog endpoints with valid JWT token.

    What it tests:
    - Creates a valid JWT access token for user 'wisrovi'.
    - Calls '/api/v1/cluster/health' and asserts 200 OK and expected keys.
    - Calls '/api/v1/cluster/overview' and asserts 200 OK.
    - Calls '/api/v1/tasks/history' with search and status filters.
    - Calls '/api/v1/tasks/quick-launch' and asserts 200 OK with dispatched study payload.
    - Calls '/api/v1/tasks/{study_id}/metrics' and asserts 200 OK.
    """
    from datetime import timedelta
    from backend.auth import create_access_token

    token = create_access_token(data={"sub": "wisrovi"}, expires_delta=timedelta(minutes=15))
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Cluster Watchdog Healthcheck
    resp_health = client.get("/api/v1/cluster/health", headers=headers)
    assert resp_health.status_code == 200, f"Expected 200, got {resp_health.status_code}"
    health_data = resp_health.json()
    assert "redis_status" in health_data
    assert "redis_latency_ms" in health_data
    assert "healthy_nodes" in health_data
    assert "zombie_nodes" in health_data

    # 2. Cluster Overview
    resp_overview = client.get("/api/v1/cluster/overview", headers=headers)
    assert resp_overview.status_code == 200, f"Expected 200, got {resp_overview.status_code}"
    overview_data = resp_overview.json()
    assert "total_nodes" in overview_data
    assert "active_nodes" in overview_data

    # 3. Tasks History with Query Filters
    resp_hist = client.get("/api/v1/tasks/history?limit=10&status=completed&search=test", headers=headers)
    assert resp_hist.status_code == 200, f"Expected 200, got {resp_hist.status_code}"
    assert isinstance(resp_hist.json(), list)

    # 4. Quick Launch Test Dispatcher
    resp_quick = client.post(
        "/api/v1/tasks/quick-launch",
        headers=headers,
        json={
            "model": "yolov8n-cls.pt",
            "dataset": "/examples/colorball.v8i.multiclass/",
            "epochs": 1,
        },
    )
    assert resp_quick.status_code == 200, f"Expected 200, got {resp_quick.status_code}"
    quick_data = resp_quick.json()
    assert quick_data.get("status") == "success"
    assert "study_id" in quick_data.get("data", {})
    created_study_id = quick_data["data"]["study_id"]

    # 5. Study Metrics for Optuna Plots
    resp_metrics = client.get(f"/api/v1/tasks/{created_study_id}/metrics", headers=headers)
    assert resp_metrics.status_code == 200, f"Expected 200, got {resp_metrics.status_code}"
    assert isinstance(resp_metrics.json(), list)
