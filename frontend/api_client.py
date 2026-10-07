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
    ) -> Dict[str, Any]:
        """Pauses or resumes an invoker."""
        url = f"{self.base_url}/api/v1/invokers/{worker_ip}/pause"
        resp = requests.post(
            url,
            headers=self._headers(token),
            json={"action": action, "mode": mode, "hours": hours},
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

    def drain_invoker(self, token: str, worker_ip: str, reason: str = "Maintenance") -> Dict[str, Any]:
        """Puts an invoker node in graceful drain mode."""
        url = f"{self.base_url}/api/v1/invokers/{worker_ip}/drain"
        resp = requests.post(url, headers=self._headers(token), json={"reason": reason}, timeout=5)
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
        params = {"limit": limit}
        if search:
            params["search"] = search
        if author and author != "Todos":
            params["author"] = author
        if worker_ip and worker_ip != "Todos":
            params["worker_ip"] = worker_ip
        if status and status != "Todos":
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

