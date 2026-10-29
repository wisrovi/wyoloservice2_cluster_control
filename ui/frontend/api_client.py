"""HTTP client for communicating with the Cluster Control FastAPI backend."""

import os
from typing import Any, Dict, List, Optional
import requests


API_BASE_URL = os.getenv("CLUSTER_API_URL", "http://localhost:8001")


class ClusterApiClient:
    """Client wrapper providing authentication and API communication."""

    def __init__(self, base_url: str = API_BASE_URL):
        self.base_url = base_url.rstrip("/")

    def _headers(self, token: Optional[str] = None) -> Dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        return headers

    def login(self, username: str, password: str) -> Dict[str, Any]:
        """Authenticates with backend and returns access token response."""
        url = f"{self.base_url}/api/v1/auth/login"
        resp = requests.post(url, json={"username": username, "password": password}, timeout=5)
        if resp.status_code == 200:
            return resp.json()
        raise ValueError(resp.json().get("detail", "Error authenticating"))

    def change_password(self, token: str, current_password: str, new_password: str) -> Dict[str, Any]:
        """Changes user password."""
        url = f"{self.base_url}/api/v1/auth/change-password"
        resp = requests.post(
            url,
            headers=self._headers(token),
            json={"current_password": current_password, "new_password": new_password},
            timeout=5,
        )
        if resp.status_code == 200:
            return resp.json()
        raise ValueError(resp.json().get("detail", "Error changing password"))

    def get_overview(self, token: str) -> Dict[str, Any]:
        """Fetches cluster overview metrics."""
        url = f"{self.base_url}/api/v1/cluster/overview"
        resp = requests.get(url, headers=self._headers(token), timeout=5)
        if resp.status_code == 200:
            return resp.json()
        raise ValueError(resp.json().get("detail", "Error fetching overview"))

    def list_invokers(self, token: str) -> List[Dict[str, Any]]:
        """Lists all invokers with hardware and limits."""
        url = f"{self.base_url}/api/v1/invokers"
        resp = requests.get(url, headers=self._headers(token), timeout=5)
        if resp.status_code == 200:
            return resp.json()
        raise ValueError(resp.json().get("detail", "Error listing invokers"))

    def update_limits(
        self,
        token: str,
        worker_ip: str,
        max_gpu_percent: Optional[float] = None,
        max_ram: Optional[str] = None,
        max_cpu_cores: Optional[float] = None,
        shm_size_gb: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Updates limits for an invoker node."""
        url = f"{self.base_url}/api/v1/invokers/{worker_ip}/limits"
        payload = {}
        if max_gpu_percent is not None:
            payload["max_gpu_percent"] = max_gpu_percent
        if max_ram is not None:
            payload["max_ram"] = max_ram
        if max_cpu_cores is not None:
            payload["max_cpu_cores"] = max_cpu_cores
        if shm_size_gb is not None:
            payload["shm_size_gb"] = shm_size_gb

        resp = requests.put(url, headers=self._headers(token), json=payload, timeout=5)
        if resp.status_code == 200:
            return resp.json()
        raise ValueError(resp.json().get("detail", "Error updating limits"))

    def set_pause(
        self,
        token: str,
        worker_ip: str,
        action: str,
        mode: str = "temporal",
        hours: float = 4.0,
        until_time: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Pauses or resumes an invoker."""
        url = f"{self.base_url}/api/v1/invokers/{worker_ip}/pause"
        payload = {"action": action, "mode": mode, "hours": hours}
        if until_time:
            payload["until_time"] = until_time
        resp = requests.post(
            url,
            headers=self._headers(token),
            json=payload,
            timeout=5,
        )
        if resp.status_code == 200:
            return resp.json()
        raise ValueError(resp.json().get("detail", f"Error executing {action}"))

    def batch_update_limits(
        self,
        token: str,
        max_gpu_percent: Optional[float] = None,
        max_ram: Optional[str] = None,
        max_cpu_cores: Optional[float] = None,
        worker_ips: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Batch updates limits across multiple invokers."""
        url = f"{self.base_url}/api/v1/invokers/batch-limits"
        payload = {}
        if max_gpu_percent is not None:
            payload["max_gpu_percent"] = max_gpu_percent
        if max_ram is not None:
            payload["max_ram"] = max_ram
        if max_cpu_cores is not None:
            payload["max_cpu_cores"] = max_cpu_cores
        if worker_ips is not None:
            payload["worker_ips"] = worker_ips

        resp = requests.post(url, headers=self._headers(token), json=payload, timeout=5)
        if resp.status_code == 200:
            return resp.json()
        raise ValueError(resp.json().get("detail", "Error batch updating limits"))

    def drain_invoker(self, token: str, worker_ip: str, reason: str = "Maintenance", evict: bool = True) -> Dict[str, Any]:
        """Puts an invoker node in graceful drain mode with workload eviction."""
        url = f"{self.base_url}/api/v1/invokers/{worker_ip}/drain"
        resp = requests.post(url, headers=self._headers(token), json={"reason": reason, "evict": evict}, timeout=8)
        if resp.status_code == 200:
            return resp.json()
        raise ValueError(resp.json().get("detail", f"Error draining invoker {worker_ip}"))

    def get_cluster_health(self, token: str) -> Dict[str, Any]:
        """Fetches cluster health watchdog metrics."""
        url = f"{self.base_url}/api/v1/cluster/health"
        resp = requests.get(url, headers=self._headers(token), timeout=5)
        if resp.status_code == 200:
            return resp.json()
        raise ValueError(resp.json().get("detail", "Error fetching health watchdog"))

    def list_active_tasks(self, token: str) -> List[Dict[str, Any]]:
        """Retrieves active tasks."""
        url = f"{self.base_url}/api/v1/tasks/active"
        resp = requests.get(url, headers=self._headers(token), timeout=5)
        if resp.status_code == 200:
            return resp.json()
        raise ValueError(resp.json().get("detail", "Error fetching active tasks"))

    def list_task_history(
        self,
        token: str,
        limit: int = 50,
        search: Optional[str] = None,
        author: Optional[str] = None,
        worker_ip: Optional[str] = None,
        status: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Retrieves task history with multi-field filtering."""
        # "All" is the UI sentinel meaning "no filter" ("Todos" kept for backward compatibility).
        all_sentinels = ("All", "Todos")
        params = {"limit": limit}
        if search:
            params["search"] = search
        if author and author not in all_sentinels:
            params["author"] = author
        if worker_ip and worker_ip not in all_sentinels:
            params["worker_ip"] = worker_ip
        if status and status not in all_sentinels:
            params["status"] = status

        url = f"{self.base_url}/api/v1/tasks/history"
        resp = requests.get(url, headers=self._headers(token), params=params, timeout=5)
        if resp.status_code == 200:
            return resp.json()
        raise ValueError(resp.json().get("detail", "Error fetching task history"))

    def quick_launch_task(
        self,
        token: str,
        worker_ip: Optional[str] = None,
        model: str = "yolov8n-cls.pt",
        dataset: str = "/examples/colorball.v8i.multiclass/",
        epochs: int = 1,
        priority: str = "NORMAL",
    ) -> Dict[str, Any]:
        """Dispatches a quick 1-trial verification task with priority."""
        url = f"{self.base_url}/api/v1/tasks/quick-launch"
        payload = {
            "worker_ip": worker_ip,
            "model": model,
            "dataset": dataset,
            "epochs": epochs,
            "priority": priority.upper(),
        }
        resp = requests.post(url, headers=self._headers(token), json=payload, timeout=5)
        if resp.status_code == 200:
            return resp.json()
        raise ValueError(resp.json().get("detail", "Error dispatching quick task"))

    def get_study_metrics(self, token: str, study_id: str) -> List[Dict[str, Any]]:
        """Retrieves trial metrics for Optuna plotting."""
        url = f"{self.base_url}/api/v1/tasks/{study_id}/metrics"
        resp = requests.get(url, headers=self._headers(token), timeout=5)
        if resp.status_code == 200:
            return resp.json()
        raise ValueError(resp.json().get("detail", f"Error fetching metrics for study {study_id}"))

    def cancel_task(self, token: str, study_id: str) -> Dict[str, Any]:
        """Cancels a running study."""
        url = f"{self.base_url}/api/v1/tasks/{study_id}/cancel"
        resp = requests.post(url, headers=self._headers(token), timeout=5)
        if resp.status_code == 200:
            return resp.json()
        raise ValueError(resp.json().get("detail", f"Error cancelling task {study_id}"))

    def get_webhook_config(self, token: str) -> Dict[str, Any]:
        """Gets webhook configuration."""
        url = f"{self.base_url}/api/v1/cluster/webhook"
        resp = requests.get(url, headers=self._headers(token), timeout=5)
        if resp.status_code == 200:
            return resp.json()
        raise ValueError(resp.json().get("detail", "Error getting webhook config"))

    def save_webhook_config(self, token: str, webhook_url: str, enabled: bool = True) -> Dict[str, Any]:
        """Saves webhook configuration."""
        url = f"{self.base_url}/api/v1/cluster/webhook"
        resp = requests.post(url, headers=self._headers(token), json={"webhook_url": webhook_url, "enabled": enabled}, timeout=5)
        if resp.status_code == 200:
            return resp.json()
        raise ValueError(resp.json().get("detail", "Error saving webhook config"))

    def test_webhook(self, token: str) -> Dict[str, Any]:
        """Sends test notification via webhook."""
        url = f"{self.base_url}/api/v1/cluster/webhook/test"
        resp = requests.post(url, headers=self._headers(token), timeout=5)
        if resp.status_code == 200:
            return resp.json()
        raise ValueError(resp.json().get("detail", "Error sending test webhook"))

    def estimate_duration(self, token: str, model: str, epochs: int, dataset: str = "") -> Dict[str, Any]:
        """Estimates training duration."""
        url = f"{self.base_url}/api/v1/cluster/estimate-duration"
        params = {"model": model, "epochs": epochs, "dataset": dataset}
        resp = requests.get(url, headers=self._headers(token), params=params, timeout=5)
        if resp.status_code == 200:
            return resp.json()
        raise ValueError(resp.json().get("detail", "Error estimating duration"))

    def recommend_node(self, token: str, model: str = "yolov8n-cls.pt") -> Dict[str, Any]:
        """Requests smart dispatch recommendation for target model."""
        url = f"{self.base_url}/api/v1/cluster/recommend-node"
        params = {"model": model}
        resp = requests.get(url, headers=self._headers(token), params=params, timeout=5)
        if resp.status_code == 200:
            return resp.json()
        raise ValueError(resp.json().get("detail", "Error getting node recommendation"))

    def get_gpu_benchmarks(self, token: str) -> Dict[str, Any]:
        """Retrieves GPU benchmark profiles and throughput numbers."""
        url = f"{self.base_url}/api/v1/cluster/gpu-benchmarks"
        resp = requests.get(url, headers=self._headers(token), timeout=5)
        if resp.status_code == 200:
            return resp.json()
        raise ValueError(resp.json().get("detail", "Error getting GPU benchmarks"))

    def get_housekeeping_preview(self, token: str) -> Dict[str, Any]:
        """Retrieves housekeeping preview of stale studies and memory."""
        url = f"{self.base_url}/api/v1/cluster/housekeeping/preview"
        resp = requests.get(url, headers=self._headers(token), timeout=5)
        if resp.status_code == 200:
            return resp.json()
        raise ValueError(resp.json().get("detail", "Error getting housekeeping preview"))

    def purge_housekeeping(self, token: str) -> Dict[str, Any]:
        """Executes purge of stale and failed studies from Redis."""
        url = f"{self.base_url}/api/v1/cluster/housekeeping/purge"
        resp = requests.post(url, headers=self._headers(token), timeout=10)
        if resp.status_code == 200:
            return resp.json()
        raise ValueError(resp.json().get("detail", "Error executing housekeeping purge"))

    def get_workload_trends(self, token: str) -> Dict[str, Any]:
        """Retrieves cluster workload trends by hour and day."""
        url = f"{self.base_url}/api/v1/cluster/trends"
        resp = requests.get(url, headers=self._headers(token), timeout=5)
        if resp.status_code == 200:
            return resp.json()
        raise ValueError(resp.json().get("detail", "Error getting workload trends"))

    # --- v1.4.0 Optimization Client Methods ---

    def diagnose_invoker(self, token: str, worker_ip: str) -> Dict[str, Any]:
        """Performs deep socket and Celery connectivity diagnostic on invoker node."""
        url = f"{self.base_url}/api/v1/invokers/{worker_ip}/diagnose"
        resp = requests.get(url, headers=self._headers(token), timeout=5)
        if resp.status_code == 200:
            return resp.json()
        raise ValueError(resp.json().get("detail", f"Error diagnosing invoker {worker_ip}"))

    def get_green_ai_metrics(self, token: str) -> Dict[str, Any]:
        """Fetches Green AI energy consumption (kWh) and CO2e metrics."""
        url = f"{self.base_url}/api/v1/cluster/green-ai"
        resp = requests.get(url, headers=self._headers(token), timeout=5)
        if resp.status_code == 200:
            return resp.json()
        raise ValueError(resp.json().get("detail", "Error getting Green AI metrics"))

    def trigger_watchdog_alert(self, token: str) -> Dict[str, Any]:
        """Runs on-demand watchdog scan and triggers alert notifications."""
        url = f"{self.base_url}/api/v1/cluster/watchdog/check-and-alert"
        resp = requests.post(url, headers=self._headers(token), timeout=5)
        if resp.status_code == 200:
            return resp.json()
        raise ValueError(resp.json().get("detail", "Error triggering watchdog check"))

    def compare_studies(self, token: str, study_ids: List[str]) -> Dict[str, Any]:
        """Performs head-to-head comparison between 2 to 5 studies."""
        url = f"{self.base_url}/api/v1/tasks/compare"
        resp = requests.post(url, headers=self._headers(token), json={"study_ids": study_ids}, timeout=5)
        if resp.status_code == 200:
            return resp.json()
        raise ValueError(resp.json().get("detail", "Error comparing studies"))

    def get_study_reproducibility(self, token: str, study_id: str) -> Dict[str, Any]:
        """Fetches reproducible Docker command and YAML manifest for study."""
        url = f"{self.base_url}/api/v1/tasks/{study_id}/reproducibility"
        resp = requests.get(url, headers=self._headers(token), timeout=5)
        if resp.status_code == 200:
            return resp.json()
        raise ValueError(resp.json().get("detail", f"Error getting reproducibility manifest for {study_id}"))

    # --- Cluster Admin v1.5.0 Client Methods ---

    def get_storage_admin(self, token: str) -> Dict[str, Any]:
        """Inspects Samba CIFS and MinIO S3 cluster storage volumes."""
        url = f"{self.base_url}/api/v1/cluster/storage/inspect"
        resp = requests.get(url, headers=self._headers(token), timeout=5)
        if resp.status_code == 200:
            return resp.json()
        raise ValueError(resp.json().get("detail", "Error inspecting cluster storage"))

    def get_finops_report(self, token: str) -> Dict[str, Any]:
        """Fetches cluster electricity costs and FinOps breakdown in EUR."""
        url = f"{self.base_url}/api/v1/cluster/finops"
        resp = requests.get(url, headers=self._headers(token), timeout=5)
        if resp.status_code == 200:
            return resp.json()
        raise ValueError(resp.json().get("detail", "Error getting FinOps report"))

    def update_electricity_rate(self, token: str, rate: float) -> Dict[str, Any]:
        """Updates the electricity billing rate per kWh in EUR."""
        url = f"{self.base_url}/api/v1/cluster/finops/rate"
        resp = requests.post(url, headers=self._headers(token), json={"rate_eur_per_kwh": rate}, timeout=5)
        if resp.status_code == 200:
            return resp.json()
        raise ValueError(resp.json().get("detail", "Error updating electricity rate"))

    def get_audit_logs(self, token: str, limit: int = 50) -> Dict[str, Any]:
        """Retrieves chronological audit trail of administrative operations."""
        url = f"{self.base_url}/api/v1/cluster/audit/logs"
        resp = requests.get(url, headers=self._headers(token), params={"limit": limit}, timeout=5)
        if resp.status_code == 200:
            return resp.json()
        raise ValueError(resp.json().get("detail", "Error getting audit logs"))

    def get_cluster_capabilities(self, token: str) -> Dict[str, Any]:
        """Retrieves official catalog of 12 R&D modules and worker capabilities."""
        url = f"{self.base_url}/api/v1/cluster/capabilities"
        resp = requests.get(url, headers=self._headers(token), timeout=5)
        if resp.status_code == 200:
            return resp.json()
        raise ValueError(resp.json().get("detail", "Error getting cluster capabilities"))

    # --- Cluster Admin v1.7.0 Client Methods ---

    def get_node_gpu_processes(self, token: str, worker_ip: str) -> Dict[str, Any]:
        """Fetches live GPU compute processes and zombie indicators for a worker node."""
        url = f"{self.base_url}/api/v1/invokers/{worker_ip}/processes"
        resp = requests.get(url, headers=self._headers(token), timeout=5)
        if resp.status_code == 200:
            return resp.json()
        raise ValueError(resp.json().get("detail", f"Error getting GPU processes for {worker_ip}"))

    def kill_node_gpu_process(self, token: str, worker_ip: str, pid: int) -> Dict[str, Any]:
        """Terminates a rogue or zombie GPU process on an invoker node."""
        url = f"{self.base_url}/api/v1/invokers/{worker_ip}/kill-process/{pid}"
        resp = requests.post(url, headers=self._headers(token), timeout=10)
        if resp.status_code == 200:
            return resp.json()
        raise ValueError(resp.json().get("detail", f"Error killing process {pid} on {worker_ip}"))

    def get_celery_queues(self, token: str) -> Dict[str, Any]:
        """Fetches Celery task queues inspection across priority queues."""
        url = f"{self.base_url}/api/v1/tasks/queues"
        resp = requests.get(url, headers=self._headers(token), timeout=5)
        if resp.status_code == 200:
            return resp.json()
        raise ValueError(resp.json().get("detail", "Error fetching Celery queues"))

    def promote_celery_task(self, token: str, task_id: str, target_queue: str = "gpus_high") -> Dict[str, Any]:
        """Promotes a pending Celery task to a higher priority queue."""
        url = f"{self.base_url}/api/v1/tasks/queues/{task_id}/promote"
        resp = requests.post(url, headers=self._headers(token), json={"target_queue": target_queue}, timeout=5)
        if resp.status_code == 200:
            return resp.json()
        raise ValueError(resp.json().get("detail", f"Error promoting task {task_id}"))

    def delete_celery_task(self, token: str, task_id: str) -> Dict[str, Any]:
        """Removes a pending task from the Celery queue."""
        url = f"{self.base_url}/api/v1/tasks/queues/{task_id}"
        resp = requests.delete(url, headers=self._headers(token), timeout=5)
        if resp.status_code == 200:
            return resp.json()
        raise ValueError(resp.json().get("detail", f"Error deleting task {task_id}"))

    def get_task_logs(self, token: str, study_id: str, limit: int = 100) -> Dict[str, Any]:
        """Fetches live streaming logs for an active or completed training task."""
        url = f"{self.base_url}/api/v1/tasks/{study_id}/logs"
        resp = requests.get(url, headers=self._headers(token), params={"limit": limit}, timeout=5)
        if resp.status_code == 200:
            return resp.json()
        raise ValueError(resp.json().get("detail", f"Error fetching logs for {study_id}"))

    def get_task_diagnostics(self, token: str, study_id: str) -> Dict[str, Any]:
        """Fetches automated post-mortem root cause diagnostic for a task."""
        url = f"{self.base_url}/api/v1/tasks/{study_id}/diagnostics"
        resp = requests.get(url, headers=self._headers(token), timeout=5)
        if resp.status_code == 200:
            return resp.json()
        raise ValueError(resp.json().get("detail", f"Error fetching diagnostics for {study_id}"))

    # --- Cluster Admin v1.8.0 Client Methods ---

    def reassign_celery_task(self, token: str, task_id: str, target_queue: str = "wyolo_gpu_queue") -> Dict[str, Any]:
        """Moves a queued task from any queue to a target queue (e.g. wyolo_gpu_queue)."""
        url = f"{self.base_url}/api/v1/tasks/queues/{task_id}/reassign"
        resp = requests.post(url, headers=self._headers(token), json={"target_queue": target_queue}, timeout=5)
        if resp.status_code == 200:
            return resp.json()
        raise ValueError(resp.json().get("detail", f"Error reassigning task {task_id}"))

    def restart_node_service(self, token: str, worker_ip: str) -> Dict[str, Any]:
        """Sends an administrative restart signal to the remote invoker worker service."""
        url = f"{self.base_url}/api/v1/invokers/{worker_ip}/restart-service"
        resp = requests.post(url, headers=self._headers(token), timeout=10)
        if resp.status_code == 200:
            return resp.json()
        raise ValueError(resp.json().get("detail", f"Error restarting service on {worker_ip}"))

    def prune_node_docker(self, token: str, worker_ip: str) -> Dict[str, Any]:
        """Triggers a remote Docker prune on the invoker node to reclaim disk space."""
        url = f"{self.base_url}/api/v1/invokers/{worker_ip}/prune-docker"
        resp = requests.post(url, headers=self._headers(token), timeout=15)
        if resp.status_code == 200:
            return resp.json()
        raise ValueError(resp.json().get("detail", f"Error pruning docker on {worker_ip}"))

    def run_cluster_smoke_test(self, token: str) -> Dict[str, Any]:
        """Executes a 1-click comprehensive smoke test across all online invoker nodes."""
        url = f"{self.base_url}/api/v1/cluster/smoke-test"
        resp = requests.post(url, headers=self._headers(token), timeout=15)
        if resp.status_code == 200:
            return resp.json()
        raise ValueError(resp.json().get("detail", "Error running cluster smoke test"))

    # --- Kubernetes Pod Management Client Methods (v1.9.0) ---

    def get_task_k8s_events(self, token: str, study_id: str) -> Dict[str, Any]:
        """Retrieves live Kubernetes pod lifecycle events for an active study."""
        url = f"{self.base_url}/api/v1/tasks/{study_id}/k8s-events"
        resp = requests.get(url, headers=self._headers(token), timeout=5)
        if resp.status_code == 200:
            return resp.json()
        raise ValueError(resp.json().get("detail", f"Error fetching K8s events for {study_id}"))

    def kill_task_pod(self, token: str, study_id: str) -> Dict[str, Any]:
        """Dispatches an immediate K8s Pod eviction / termination signal."""
        url = f"{self.base_url}/api/v1/tasks/{study_id}/kill-pod"
        resp = requests.post(url, headers=self._headers(token), timeout=10)
        if resp.status_code == 200:
            return resp.json()
        raise ValueError(resp.json().get("detail", f"Error evicting pod for {study_id}"))

    def purge_stale_k8s_pods(self, token: str) -> Dict[str, Any]:
        """Triggers cluster-wide garbage collection of stale/evicted/failed K8s pods."""
        url = f"{self.base_url}/api/v1/cluster/k8s/purge-stale-pods"
        resp = requests.post(url, headers=self._headers(token), timeout=15)
        if resp.status_code == 200:
            return resp.json()
        raise ValueError(resp.json().get("detail", "Error purging stale K8s pods"))

    # --- Enterprise Cluster Suite Client Methods (v2.0.0) ---

    def list_optuna_sweeps(self, token: str) -> Dict[str, Any]:
        """Fetches all aggregated Optuna sweeps with convergence and trial stats."""
        url = f"{self.base_url}/api/v1/tasks/sweeps"
        resp = requests.get(url, headers=self._headers(token), timeout=8)
        if resp.status_code == 200:
            return resp.json()
        raise ValueError(resp.json().get("detail", "Error fetching Optuna sweeps"))

    def cancel_optuna_sweep(self, token: str, sweep_name: str) -> Dict[str, Any]:
        """Cancels all active trials running under a sweep."""
        url = f"{self.base_url}/api/v1/tasks/sweeps/{sweep_name}/cancel"
        resp = requests.post(url, headers=self._headers(token), timeout=10)
        if resp.status_code == 200:
            return resp.json()
        raise ValueError(resp.json().get("detail", f"Error cancelling sweep {sweep_name}"))

    def get_cluster_images_status(
        self,
        token: str,
        target_image: str = "wisrovi/train_service:worker_executor_v1.0.0",
    ) -> Dict[str, Any]:
        """Fetches Docker / K8s image digest and tag synchronization status across all cluster invokers."""
        url = f"{self.base_url}/api/v1/cluster/images/status"
        resp = requests.get(url, headers=self._headers(token), params={"target_image": target_image}, timeout=8)
        if resp.status_code == 200:
            return resp.json()
        raise ValueError(resp.json().get("detail", "Error fetching cluster images status"))

    def trigger_broadcast_docker_pull(
        self,
        token: str,
        target_image: str = "wisrovi/train_service:worker_executor_v1.0.0",
    ) -> Dict[str, Any]:
        """Triggers broadcast docker pull across all workers (strictly excluding NAS manager)."""
        url = f"{self.base_url}/api/v1/cluster/images/broadcast-pull"
        resp = requests.post(url, headers=self._headers(token), params={"target_image": target_image}, timeout=20)
        if resp.status_code == 200:
            return resp.json()
        raise ValueError(resp.json().get("detail", "Error triggering broadcast docker pull"))

    def inspect_dataset(self, token: str, dataset_path: str) -> Dict[str, Any]:
        """Performs pre-flight check on dataset path (classes, splits, YAML)."""
        url = f"{self.base_url}/api/v1/cluster/datasets/inspect"
        resp = requests.get(url, headers=self._headers(token), params={"dataset_path": dataset_path}, timeout=10)
        if resp.status_code == 200:
            return resp.json()
        raise ValueError(resp.json().get("detail", f"Error inspecting dataset at {dataset_path}"))

    def list_available_datasets(self, token: str, base_path: str = "/examples") -> Dict[str, Any]:
        """Discovers datasets available on local filesystem or mounted Samba shares."""
        url = f"{self.base_url}/api/v1/cluster/datasets/available"
        resp = requests.get(url, headers=self._headers(token), params={"base_path": base_path}, timeout=10)
        if resp.status_code == 200:
            return resp.json()
        raise ValueError(resp.json().get("detail", "Error discovering datasets"))

    def list_quarantined_tasks(self, token: str) -> Dict[str, Any]:
        """Retrieves dead-letter queue (DLQ) quarantined tasks."""
        url = f"{self.base_url}/api/v1/tasks/quarantine"
        resp = requests.get(url, headers=self._headers(token), timeout=8)
        if resp.status_code == 200:
            return resp.json()
        raise ValueError(resp.json().get("detail", "Error fetching quarantined tasks"))

    def retry_quarantined_task(self, token: str, task_id: str) -> Dict[str, Any]:
        """Re-enqueues a quarantined task."""
        url = f"{self.base_url}/api/v1/tasks/quarantine/{task_id}/retry"
        resp = requests.post(url, headers=self._headers(token), timeout=10)
        if resp.status_code == 200:
            return resp.json()
        raise ValueError(resp.json().get("detail", f"Error retrying task {task_id}"))

    def purge_quarantined_task(self, token: str, task_id: str) -> Dict[str, Any]:
        """Permanently deletes a task from the DLQ."""
        url = f"{self.base_url}/api/v1/tasks/quarantine/{task_id}"
        resp = requests.delete(url, headers=self._headers(token), timeout=10)
        if resp.status_code == 200:
            return resp.json()
        raise ValueError(resp.json().get("detail", f"Error purging task {task_id}"))

    def get_scheduler_policy(self, token: str) -> Dict[str, Any]:
        """Retrieves automated Day/Night scheduler policy and active mode."""
        url = f"{self.base_url}/api/v1/cluster/scheduler/policy"
        resp = requests.get(url, headers=self._headers(token), timeout=5)
        if resp.status_code == 200:
            return resp.json()
        raise ValueError(resp.json().get("detail", "Error fetching scheduler policy"))

    def set_scheduler_policy(self, token: str, policy: Dict[str, Any]) -> Dict[str, Any]:
        """Updates Day/Night automated scheduler policy."""
        url = f"{self.base_url}/api/v1/cluster/scheduler/policy"
        resp = requests.post(url, headers=self._headers(token), json=policy, timeout=10)
        if resp.status_code == 200:
            return resp.json()
        raise ValueError(resp.json().get("detail", "Error updating scheduler policy"))

    def apply_scheduler_policy(self, token: str) -> Dict[str, Any]:
        """Immediately applies active scheduler policy limits to cluster."""
        url = f"{self.base_url}/api/v1/cluster/scheduler/apply-policy"
        resp = requests.post(url, headers=self._headers(token), timeout=15)
        if resp.status_code == 200:
            return resp.json()
        raise ValueError(resp.json().get("detail", "Error applying scheduler policy"))

    def get_support_bundle(self, token: str) -> Dict[str, Any]:
        """Exports diagnostic black-box support bundle."""
        url = f"{self.base_url}/api/v1/cluster/support-bundle"
        resp = requests.get(url, headers=self._headers(token), timeout=15)
        if resp.status_code == 200:
            return resp.json()
        raise ValueError(resp.json().get("detail", "Error exporting support bundle"))

    def test_rich_webhook(
        self,
        token: str,
        event_type: str = "study_completed",
        webhook_url: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Tests rich Discord/Slack embed notification delivery."""
        url = f"{self.base_url}/api/v1/cluster/webhook/test-rich"
        payload = {"event_type": event_type}
        if webhook_url:
            payload["webhook_url"] = webhook_url
        resp = requests.post(url, headers=self._headers(token), json=payload, timeout=10)
        if resp.status_code == 200:
            return resp.json()
        raise ValueError(resp.json().get("detail", "Error testing rich webhook"))





