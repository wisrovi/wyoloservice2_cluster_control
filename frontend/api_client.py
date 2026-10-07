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

    def list_active_tasks(self, token: str) -> List[Dict[str, Any]]:
        """Retrieves active tasks."""
        url = f"{self.base_url}/api/v1/tasks/active"
        resp = requests.get(url, headers=self._headers(token), timeout=5)
        if resp.status_code == 200:
            return resp.json()
        raise ValueError(resp.json().get("detail", "Error fetching active tasks"))

    def list_task_history(self, token: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Retrieves task history."""
        url = f"{self.base_url}/api/v1/tasks/history?limit={limit}"
        resp = requests.get(url, headers=self._headers(token), timeout=5)
        if resp.status_code == 200:
            return resp.json()
        raise ValueError(resp.json().get("detail", "Error fetching task history"))

    def cancel_task(self, token: str, study_id: str) -> Dict[str, Any]:
        """Cancels a running study."""
        url = f"{self.base_url}/api/v1/tasks/{study_id}/cancel"
        resp = requests.post(url, headers=self._headers(token), timeout=5)
        if resp.status_code == 200:
            return resp.json()
        raise ValueError(resp.json().get("detail", f"Error cancelling task {study_id}"))
