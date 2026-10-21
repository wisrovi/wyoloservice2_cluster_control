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
    assert "storage_samba" in health_data
    assert "storage_minio" in health_data

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

    # 6. Webhook Configuration & Testing
    resp_wh_get = client.get("/api/v1/cluster/webhook", headers=headers)
    assert resp_wh_get.status_code == 200, f"Expected 200, got {resp_wh_get.status_code}"
    assert "webhook_url" in resp_wh_get.json()

    resp_wh_post = client.post(
        "/api/v1/cluster/webhook",
        headers=headers,
        json={"webhook_url": "https://discord.com/api/webhooks/test", "enabled": True},
    )
    assert resp_wh_post.status_code == 200
    assert resp_wh_post.json().get("webhook_url") == "https://discord.com/api/webhooks/test"
    assert resp_wh_post.json().get("enabled") is True

    resp_wh_test = client.post("/api/v1/cluster/webhook/test", headers=headers)
    assert resp_wh_test.status_code == 200
    assert "status" in resp_wh_test.json()

    # 7. Training Duration Estimator (ETA)
    resp_eta = client.get("/api/v1/cluster/estimate-duration?model=yolov8n-cls.pt&epochs=2&dataset_size=500", headers=headers)
    assert resp_eta.status_code == 200, f"Expected 200, got {resp_eta.status_code}"
    eta_data = resp_eta.json()
    assert "estimated_duration_min" in eta_data
    assert "recommended_gpu" in eta_data
    assert "estimated_throughput_img_s" in eta_data

    # 8. Smart Dispatcher Recommendation
    resp_rec = client.get("/api/v1/cluster/recommend-node?model=yolov8n-cls.pt", headers=headers)
    assert resp_rec.status_code == 200, f"Expected 200, got {resp_rec.status_code}"
    rec_data = resp_rec.json()
    assert "target_ip" in rec_data
    assert "hostname" in rec_data
    assert "score" in rec_data
    assert "reason" in rec_data

    # 9. GPU Benchmarks & Leaderboard
    resp_bench = client.get("/api/v1/cluster/gpu-benchmarks", headers=headers)
    assert resp_bench.status_code == 200, f"Expected 200, got {resp_bench.status_code}"
    bench_data = resp_bench.json()
    assert "benchmarks" in bench_data
    assert len(bench_data["benchmarks"]) > 0
    assert "avg_throughput_img_s" in bench_data["benchmarks"][0]

    # 10. Housekeeping Preview & Purge
    resp_hk_prev = client.get("/api/v1/cluster/housekeeping/preview", headers=headers)
    assert resp_hk_prev.status_code == 200, f"Expected 200, got {resp_hk_prev.status_code}"
    hk_data = resp_hk_prev.json()
    assert "stale_failed_studies_count" in hk_data
    assert "redis_memory_human" in hk_data

    resp_hk_purge = client.post("/api/v1/cluster/housekeeping/purge", headers=headers)
    assert resp_hk_purge.status_code == 200, f"Expected 200, got {resp_hk_purge.status_code}"
    assert resp_hk_purge.json().get("status") == "success"

    # 11. Workload Trends
    resp_trends = client.get("/api/v1/cluster/trends", headers=headers)
    assert resp_trends.status_code == 200, f"Expected 200, got {resp_trends.status_code}"
    trends_data = resp_trends.json()
    assert "hourly_distribution" in trends_data
    assert "busiest_hour" in trends_data

    # 12. v1.4.0 Deep Node Connectivity Diagnostic
    resp_diag = client.get("/api/v1/invokers/192.168.1.68/diagnose", headers=headers)
    assert resp_diag.status_code == 200, f"Expected 200, got {resp_diag.status_code}"
    diag_data = resp_diag.json()
    assert "status" in diag_data
    assert "diagnostic_summary" in diag_data
    assert "suggested_actions" in diag_data

    # 13. v1.4.0 Green AI & Energy Metrics
    resp_green = client.get("/api/v1/cluster/green-ai", headers=headers)
    assert resp_green.status_code == 200, f"Expected 200, got {resp_green.status_code}"
    green_data = resp_green.json()
    assert "estimated_kwh" in green_data
    assert "estimated_co2_kg" in green_data
    assert "gpu_breakdown" in green_data

    # 14. v1.4.0 Proactive Watchdog Check & Alert
    resp_wd_alert = client.post("/api/v1/cluster/watchdog/check-and-alert", headers=headers)
    assert resp_wd_alert.status_code == 200, f"Expected 200, got {resp_wd_alert.status_code}"
    assert "alerts_detected" in resp_wd_alert.json()

    # 15. v1.4.0 Quick Launch with Priority
    resp_quick_prio = client.post(
        "/api/v1/tasks/quick-launch",
        headers=headers,
        json={"model": "yolov8n-cls.pt", "priority": "URGENT", "epochs": 1},
    )
    assert resp_quick_prio.status_code == 200, f"Expected 200, got {resp_quick_prio.status_code}"
    study_id = resp_quick_prio.json()["data"]["study_id"]

    # 16. v1.4.0 Study Reproducibility Manifest
    resp_repro = client.get(f"/api/v1/tasks/{study_id}/reproducibility", headers=headers)
    assert resp_repro.status_code == 200, f"Expected 200, got {resp_repro.status_code}"
    repro_data = resp_repro.json()
    assert "docker_run_command" in repro_data
    assert "training_yaml" in repro_data
    assert "sha256_fingerprint" in repro_data

    # 17. v1.4.0 Head-to-Head Study Comparison
    resp_compare = client.post(
        "/api/v1/tasks/compare",
        headers=headers,
        json={"study_ids": [study_id, study_id]},
    )
    assert resp_compare.status_code == 200, f"Expected 200, got {resp_compare.status_code}"
    comp_data = resp_compare.json()
    assert "studies" in comp_data
    assert "comparison_summary" in comp_data

    # 18. v1.5.0 Cluster Storage Admin
    resp_storage = client.get("/api/v1/cluster/storage/inspect", headers=headers)
    assert resp_storage.status_code == 200, f"Expected 200, got {resp_storage.status_code}"
    storage_data = resp_storage.json()
    assert "volumes" in storage_data
    assert "minio_buckets" in storage_data

    # 19. v1.5.0 FinOps Report & Electricity Rate
    resp_finops = client.get("/api/v1/cluster/finops", headers=headers)
    assert resp_finops.status_code == 200, f"Expected 200, got {resp_finops.status_code}"
    finops_data = resp_finops.json()
    assert "total_cost_eur" in finops_data
    assert "rate_eur_per_kwh" in finops_data

    resp_rate = client.post("/api/v1/cluster/finops/rate", headers=headers, json={"rate_eur_per_kwh": 0.22})
    assert resp_rate.status_code == 200, f"Expected 200, got {resp_rate.status_code}"
    assert resp_rate.json()["rate_eur_per_kwh"] == 0.22

    # 20. v1.5.0 Audit Logs
    resp_audit = client.get("/api/v1/cluster/audit/logs?limit=10", headers=headers)
    assert resp_audit.status_code == 200, f"Expected 200, got {resp_audit.status_code}"
    audit_data = resp_audit.json()
    assert "logs" in audit_data
    assert len(audit_data["logs"]) > 0

    # 21. v1.5.0 Capabilities Catalog
    resp_caps = client.get("/api/v1/cluster/capabilities", headers=headers)
    assert resp_caps.status_code == 200, f"Expected 200, got {resp_caps.status_code}"
    caps_data = resp_caps.json()
    assert "modules" in caps_data
    assert caps_data["total_modules"] >= 5

    # 22. v1.7.0 Celery Task Queues Inspection
    resp_queues = client.get("/api/v1/tasks/queues", headers=headers)
    assert resp_queues.status_code == 200, f"Expected 200, got {resp_queues.status_code}"
    queues_data = resp_queues.json()
    assert "queues" in queues_data
    assert "total_queued" in queues_data

    # 23. v1.7.0 Task Queue Management (Promote & Delete)
    resp_promote = client.post(
        "/api/v1/tasks/queues/non-existent-task-id/promote",
        headers=headers,
        json={"target_queue": "gpus_high"},
    )
    assert resp_promote.status_code in [200, 404]

    resp_del_task = client.delete("/api/v1/tasks/queues/non-existent-task-id", headers=headers)
    assert resp_del_task.status_code in [200, 404]

    # 24. v1.7.0 Live Task Logs
    resp_logs = client.get(f"/api/v1/tasks/{study_id}/logs?limit=50", headers=headers)
    assert resp_logs.status_code == 200, f"Expected 200, got {resp_logs.status_code}"
    logs_data = resp_logs.json()
    assert "study_id" in logs_data
    assert "logs" in logs_data

    # 25. v1.7.0 Post-Mortem Root Cause Diagnostics
    resp_task_diag = client.get(f"/api/v1/tasks/{study_id}/diagnostics", headers=headers)
    assert resp_task_diag.status_code == 200, f"Expected 200, got {resp_task_diag.status_code}"
    task_diag_data = resp_task_diag.json()
    assert "study_id" in task_diag_data
    assert "status" in task_diag_data
    assert "root_cause" in task_diag_data
    assert "suggested_action" in task_diag_data

    # 26. v1.7.0 Node GPU Process Breakdown & Zombie Detection
    resp_proc = client.get("/api/v1/invokers/192.168.1.68/processes", headers=headers)
    assert resp_proc.status_code == 200, f"Expected 200, got {resp_proc.status_code}"
    proc_data = resp_proc.json()
    assert "worker_ip" in proc_data
    assert "processes" in proc_data
    assert "has_zombies" in proc_data

    # 27. v1.7.0 Kill Rogue GPU Process on Node
    resp_kill = client.post("/api/v1/invokers/192.168.1.68/kill-process/99999", headers=headers)
    assert resp_kill.status_code == 200, f"Expected 200, got {resp_kill.status_code}"
    kill_data = resp_kill.json()
    assert "worker_ip" in kill_data
    assert "pid" in kill_data
    assert "status" in kill_data

    # 28. v1.8.0 Reassign Task Queue
    resp_reassign = client.post(
        "/api/v1/tasks/queues/non-existent-task-id/reassign",
        headers=headers,
        json={"target_queue": "wyolo_gpu_queue"},
    )
    assert resp_reassign.status_code in [200, 404]

    # Verify enhanced queue fields
    assert "global_queues" in queues_data
    assert "node_queues" in queues_data
    assert "author_breakdown" in queues_data
    assert "backlog_eta_minutes" in queues_data
    assert "jam_alert" in queues_data

    # 29. v1.8.0 Remote Node Service Restart
    resp_restart = client.post("/api/v1/invokers/192.168.1.68/restart-service", headers=headers)
    assert resp_restart.status_code == 200, f"Expected 200, got {resp_restart.status_code}"
    restart_data = resp_restart.json()
    assert restart_data["operation"] == "restart_service"
    assert "status" in restart_data

    # 30. v1.8.0 Remote Node Docker Prune
    resp_prune = client.post("/api/v1/invokers/192.168.1.68/prune-docker", headers=headers)
    assert resp_prune.status_code == 200, f"Expected 200, got {resp_prune.status_code}"
    prune_data = resp_prune.json()
    assert prune_data["operation"] == "docker_prune"
    assert "status" in prune_data

    # 31. v1.8.0 Cluster Smoke Test
    resp_smoke = client.post("/api/v1/cluster/smoke-test", headers=headers)
    assert resp_smoke.status_code == 200, f"Expected 200, got {resp_smoke.status_code}"
    smoke_data = resp_smoke.json()
    assert "status" in smoke_data
    assert "total_nodes" in smoke_data
    assert "dispatched_nodes" in smoke_data
    assert "results" in smoke_data


