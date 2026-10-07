"""Redis client and data access layer for cluster state."""

from datetime import datetime
import json
import time
from typing import Any, Dict, List, Optional
from celery import Celery
import redis

from backend.config import settings


_redis_pool: Optional[redis.ConnectionPool] = None


def get_redis_client() -> redis.Redis:
    """Returns a connected Redis client instance."""
    global _redis_pool
    if _redis_pool is None:
        _redis_pool = redis.ConnectionPool.from_url(
            settings.REDIS_URL,
            decode_responses=False,
            socket_timeout=5,
            socket_connect_timeout=5,
        )
    return redis.Redis(connection_pool=_redis_pool)


def get_celery_app() -> Celery:
    """Returns a Celery application instance configured with the cluster broker."""
    return Celery("cluster_control", broker=settings.REDIS_URL, backend=settings.REDIS_URL)


class ClusterRepository:
    """Repository handling all Redis read/write operations for the cluster."""

    def __init__(self, client: Optional[redis.Redis] = None):
        self.client = client or get_redis_client()

    # --- Invokers Management ---

    def list_invokers(self) -> List[Dict[str, Any]]:
        """Lists all known invoker nodes, combining physical resources and limits."""
        # Find all invoker keys
        resource_keys = [k.decode("utf-8") for k in self.client.keys("invoker:*:resources")]
        version_keys = [k.decode("utf-8") for k in self.client.keys("invoker:*:version")]

        # Collect unique IPs
        ips = set()
        for k in resource_keys:
            parts = k.split(":")
            if len(parts) >= 3:
                ips.add(parts[1])
        for k in version_keys:
            parts = k.split(":")
            if len(parts) >= 3:
                ips.add(parts[1])

        invokers = []
        for ip in sorted(ips):
            invoker_data = self.get_invoker(ip)
            if invoker_data:
                invokers.append(invoker_data)
        return invokers

    def get_invoker(self, worker_ip: str) -> Optional[Dict[str, Any]]:
        """Returns details for a single invoker node."""
        res_key = f"invoker:{worker_ip}:resources"
        raw_res = self.client.hgetall(res_key)
        res = {k.decode("utf-8"): v.decode("utf-8") for k, v in raw_res.items()} if raw_res else {}

        # Also inspect legacy version key if present
        ver_key = f"invoker:{worker_ip}:version"
        raw_ver = self.client.get(ver_key)
        ver_data = json.loads(raw_ver.decode("utf-8")) if raw_ver else {}

        # Pause state check
        pause_state_key = f"invoker:{worker_ip}:pause_state"
        pause_until_key = f"invoker:{worker_ip}:pause_until"
        pause_state_raw = self.client.get(pause_state_key)
        pause_state = pause_state_raw.decode("utf-8") if pause_state_raw else res.get("pause_state", "active")
        pause_until_raw = self.client.get(pause_until_key)
        pause_until = pause_until_raw.decode("utf-8") if pause_until_raw else res.get("pause_until", "")

        hostname = res.get("hostname") or ver_data.get("worker_hostname") or f"worker-{worker_ip}"
        gpu_model = res.get("physical_gpu_model") or ver_data.get("worker_gpu_model") or "unknown"
        gpu_count = int(res.get("physical_gpu_count") or ver_data.get("worker_gpu_count") or 0)
        gpu_mem = res.get("physical_gpu_memory_total") or ver_data.get("worker_gpu_memory") or "unknown"
        ram_total = res.get("physical_ram_total") or ver_data.get("executor_allocated_ram") or "unknown"
        cpu_cores = res.get("physical_cpu_cores") or ver_data.get("worker_cpu_cores") or "unknown"

        # Check last seen or status
        status = res.get("status") or ver_data.get("status") or "online"
        last_seen = res.get("last_seen") or ver_data.get("startup_time") or datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Limits
        max_gpu = float(res.get("max_gpu_percent", 30.0))
        max_ram = res.get("max_ram", ram_total)
        max_cpu_cores = float(res.get("max_cpu_cores", 4.0))

        return {
            "worker_ip": worker_ip,
            "hostname": hostname,
            "status": status,
            "pause_state": pause_state,
            "pause_until": pause_until,
            "physical": {
                "gpu_model": gpu_model,
                "gpu_count": gpu_count,
                "gpu_memory_total": gpu_mem,
                "ram_total": ram_total,
                "cpu_cores": cpu_cores,
            },
            "limits": {
                "max_gpu_percent": max_gpu,
                "max_ram": max_ram,
                "max_cpu_cores": max_cpu_cores,
            },
            "last_seen": last_seen,
            "updated_at": res.get("updated_at", last_seen),
        }

    def update_invoker_limits(
        self,
        worker_ip: str,
        max_gpu_percent: Optional[float] = None,
        max_ram: Optional[str] = None,
        max_cpu_cores: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Updates dynamic resource limits for a specific invoker node."""
        res_key = f"invoker:{worker_ip}:resources"
        payload = {"updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
        if max_gpu_percent is not None:
            payload["max_gpu_percent"] = str(max_gpu_percent)
        if max_ram is not None:
            payload["max_ram"] = str(max_ram)
        if max_cpu_cores is not None:
            payload["max_cpu_cores"] = str(max_cpu_cores)

        self.client.hset(res_key, mapping=payload)
        return self.get_invoker(worker_ip) or {}

    def set_invoker_pause(
        self,
        worker_ip: str,
        action: str,
        mode: str = "temporal",
        hours: float = 4.0,
    ) -> Dict[str, Any]:
        """Pauses or resumes an invoker node and sends Celery signals."""
        state_key = f"invoker:{worker_ip}:pause_state"
        until_key = f"invoker:{worker_ip}:pause_until"
        res_key = f"invoker:{worker_ip}:resources"

        if action == "pause":
            if mode == "temporal":
                pause_until = time.time() + (hours * 3600)
                self.client.set(state_key, "paused_temporal")
                self.client.set(until_key, str(pause_until))
                self.client.hset(res_key, mapping={"pause_state": "paused_temporal", "pause_until": str(pause_until)})
            else:
                self.client.set(state_key, "paused_perpetual")
                self.client.delete(until_key)
                self.client.hset(res_key, mapping={"pause_state": "paused_perpetual", "pause_until": ""})
        else:
            self.client.set(state_key, "active")
            self.client.delete(until_key)
            self.client.hset(res_key, mapping={"pause_state": "active", "pause_until": ""})

        # Send Celery control signal to cancel/add consumers
        try:
            app = get_celery_app()
            node_name = f"celery@wyolo_invoker_{worker_ip}"
            public_queues = ["gpus_high", "gpus_medium", "gpus_low"]
            for q in public_queues:
                if action == "pause":
                    app.control.cancel_consumer(q, destination=[node_name], timeout=1.0)
                else:
                    app.control.add_consumer(q, destination=[node_name], timeout=1.0)
        except Exception as e:
            print(f"[CELERY SIGNAL] Warning: Failed to send Celery signal to {worker_ip}: {e}")

        return self.get_invoker(worker_ip) or {}

    # --- Tasks Management ---

    def list_active_tasks(self) -> List[Dict[str, Any]]:
        """Retrieves currently active training trials and studies from Redis."""
        active_keys = [k.decode("utf-8") for k in self.client.keys("study:*:active_trial")]
        tasks = []
        for key in active_keys:
            parts = key.split(":")
            if len(parts) >= 3:
                study_id = parts[1]
                task_data = self.get_study_details(study_id)
                if task_data:
                    tasks.append(task_data)
        return tasks

    def list_all_studies(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Retrieves recent studies from Redis."""
        config_keys = [k.decode("utf-8") for k in self.client.keys("study:*:config")]
        studies = []
        for key in config_keys[:limit]:
            study_id = key.split(":")[1]
            details = self.get_study_details(study_id)
            if details:
                studies.append(details)
        return studies

    def get_study_details(self, study_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves complete info for a study."""
        raw_config = self.client.get(f"study:{study_id}:config")
        config = json.loads(raw_config.decode("utf-8")) if raw_config else {}

        raw_progress = self.client.get(f"study:{study_id}:progress")
        progress = json.loads(raw_progress.decode("utf-8")) if raw_progress else {}

        raw_invoker = self.client.get(f"study:{study_id}:invoker")
        invoker_name = raw_invoker.decode("utf-8") if raw_invoker else "unknown"

        raw_active_trial = self.client.get(f"study:{study_id}:active_trial")
        active_trial = json.loads(raw_active_trial.decode("utf-8")) if raw_active_trial else None

        raw_start = self.client.get(f"study:{study_id}:start_time")
        start_time = float(raw_start.decode("utf-8")) if raw_start else None

        raw_error = self.client.get(f"study:{study_id}:error")
        error = json.loads(raw_error.decode("utf-8")) if raw_error else None

        status = "running" if active_trial else ("failed" if error else "completed")

        return {
            "study_id": study_id,
            "status": status,
            "model": config.get("model", "unknown"),
            "task_type": config.get("type", "unknown"),
            "invoker": invoker_name,
            "progress": progress,
            "active_trial": active_trial,
            "start_time": datetime.fromtimestamp(start_time).strftime("%Y-%m-%d %H:%M:%S") if start_time else None,
            "error": error,
        }

    def cancel_study(self, study_id: str) -> bool:
        """Cancels a running study and notifies Celery workers."""
        self.client.set(f"study:{study_id}:cancelled", "true", ex=86400)
        self.client.delete(f"study:{study_id}:active_trial")
        try:
            app = get_celery_app()
            app.control.broadcast("stop_study", arguments={"study_id": study_id})
        except Exception:
            pass
        return True

    # --- Cluster Overview ---

    def get_cluster_overview(self) -> Dict[str, Any]:
        """Calculates aggregated metrics across the cluster."""
        invokers = self.list_invokers()
        active_tasks = self.list_active_tasks()

        total_nodes = len(invokers)
        online_nodes = sum(1 for i in invokers if i.get("status") == "online")
        paused_nodes = sum(1 for i in invokers if i.get("pause_state") != "active")
        active_nodes = total_nodes - paused_nodes

        total_gpus = sum(i.get("physical", {}).get("gpu_count", 0) for i in invokers)

        return {
            "total_nodes": total_nodes,
            "online_nodes": online_nodes,
            "active_nodes": active_nodes,
            "paused_nodes": paused_nodes,
            "total_gpus": total_gpus,
            "active_trials_count": len(active_tasks),
            "invokers": invokers,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
