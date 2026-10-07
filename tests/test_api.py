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
    - Verifies that both return HTTP 401 Unauthorized status.
    """
    resp_invokers = client.get("/api/v1/invokers")
    assert resp_invokers.status_code == 401, "Expected 401 Unauthorized for unauthenticated access to /api/v1/invokers"

    resp_overview = client.get("/api/v1/cluster/overview")
    assert resp_overview.status_code == 401, "Expected 401 Unauthorized for unauthenticated access to /api/v1/cluster/overview"
