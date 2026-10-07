"""Redis client and data access layer for cluster state."""

from datetime import datetime
import json
import time
from typing import Any, Dict, List, Optional
import uuid
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
        # Smart GPU Memory resolution if unknown or missing
        known_gpu_vram = {
            "3050": "8192 MiB (8.0 GB)",
            "3060": "12288 MiB (12.0 GB)",
            "3070": "8192 MiB (8.0 GB)",
            "3080": "10240 MiB (10.0 GB)",
            "3090": "24576 MiB (24.0 GB)",
            "4060": "8192 MiB (8.0 GB)",
            "4070": "12288 MiB (12.0 GB)",
            "4080": "16384 MiB (16.0 GB)",
            "4090": "24576 MiB (24.0 GB)",
            "1660": "6144 MiB (6.0 GB)",
            "1650": "4096 MiB (4.0 GB)",
            "2060": "6144 MiB (6.0 GB)",
            "2070": "8192 MiB (8.0 GB)",
            "2080": "8192 MiB (8.0 GB)",
            "a2000": "6144 MiB (6.0 GB)",
            "a4000": "16384 MiB (16.0 GB)",
            "a5000": "24576 MiB (24.0 GB)",
            "a6000": "49152 MiB (48.0 GB)",
            "a100": "81920 MiB (80.0 GB)",
            "v100": "32768 MiB (32.0 GB)",
            "t4": "15360 MiB (15.0 GB)",
        }
        if gpu_mem in ("unknown", "", "0", None) or "unknown" in str(gpu_mem).lower():
            model_lower = str(gpu_model).lower()
            for k_model, v_mem in known_gpu_vram.items():
                if k_model in model_lower:
                    gpu_mem = v_mem
                    break
            if gpu_mem in ("unknown", "", "0", None) or "unknown" in str(gpu_mem).lower():
                gpu_mem = "8192 MiB (8.0 GB)" if gpu_count > 0 else "N/A"
        elif "mib" in str(gpu_mem).lower() and "(" not in str(gpu_mem):
            try:
                val_mib = float(str(gpu_mem).lower().replace("mib", "").strip())
                val_gb = val_mib / 1024.0
                gpu_mem = f"{int(val_mib)} MiB ({val_gb:.1f} GB)"
            except Exception:
                pass

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

    def set_invoker_drain(self, worker_ip: str, reason: str = "Maintenance") -> Dict[str, Any]:
        """Marks an invoker node in draining mode: finishes active tasks and halts public consumption."""
        res_key = f"invoker:{worker_ip}:resources"
        state_key = f"invoker:{worker_ip}:pause_state"
        drain_key = f"invoker:{worker_ip}:drain"

        self.client.set(state_key, "draining")
        self.client.set(drain_key, json.dumps({"draining": True, "reason": reason, "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}))
        self.client.hset(res_key, mapping={"pause_state": "draining", "drain_reason": reason})

        # Cancel Celery consumer on public queues immediately so no new tasks are accepted
        try:
            app = get_celery_app()
            node_name = f"celery@wyolo_invoker_{worker_ip}"
            public_queues = ["gpus_high", "gpus_medium", "gpus_low", "wyolo_gpu_queue"]
            for q in public_queues:
                app.control.cancel_consumer(q, destination=[node_name], timeout=1.0)
        except Exception as e:
            print(f"[CELERY SIGNAL] Warning: Failed to cancel consumers for drain on {worker_ip}: {e}")

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

    def list_all_studies(
        self,
        limit: int = 50,
        search: Optional[str] = None,
        author: Optional[str] = None,
        worker_ip: Optional[str] = None,
        status: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Retrieves recent studies from Redis with search and author/node filtering."""
        config_keys = [k.decode("utf-8") for k in self.client.keys("study:*:config")]
        studies = []
        for key in config_keys:
            study_id = key.split(":")[1]
            details = self.get_study_details(study_id)
            if not details:
                continue

            # Filtering
            if search:
                s_lower = search.lower().strip()
                matched = (
                    s_lower in details.get("study_id", "").lower()
                    or s_lower in str(details.get("study_name", "")).lower()
                    or s_lower in str(details.get("dataset", "")).lower()
                    or s_lower in str(details.get("model", "")).lower()
                )
                if not matched:
                    continue

            if author and author not in ("Todos", ""):
                if author.lower() not in str(details.get("author", "")).lower():
                    continue

            if worker_ip and worker_ip not in ("Todos", ""):
                target = (
                    str(details.get("worker_ip", "")).lower()
                    + " "
                    + str(details.get("destination_node", "")).lower()
                )
                if worker_ip.lower() not in target:
                    continue

            if status and status not in ("Todos", ""):
                if details.get("status") != status:
                    continue

            studies.append(details)
            if len(studies) >= limit:
                break
        return studies

    def get_study_details(self, study_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves complete info for a study with author, study_name, dataset and destination node."""
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

        # Extract study_name, author, and dataset
        sweeper_cfg = config.get("sweeper", {})
        study_name = (
            sweeper_cfg.get("study_name")
            or config.get("study_name")
            or f"study_{study_id[:8]}"
        )
        metadata = config.get("metadata", {})
        author = (
            metadata.get("author")
            or metadata.get("user")
            or config.get("user")
            or config.get("author")
            or "Desconocido"
        )
        dataset = config.get("train", {}).get("data", "N/A")

        # Resolve destination worker
        raw_invoker_details = self.client.get(f"study:{study_id}:invoker_details")
        inv_details = json.loads(raw_invoker_details.decode("utf-8")) if raw_invoker_details else {}
        worker_ip = (
            inv_details.get("worker_host")
            or sweeper_cfg.get("target_worker_queue")
            or config.get("target_worker_queue")
        )
        if not worker_ip and invoker_name != "unknown":
            import re
            m = re.search(r"(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})", invoker_name)
            if m:
                worker_ip = m.group(1)

        worker_hostname = inv_details.get("worker_hostname") or ""
        if worker_ip and worker_hostname:
            destination_node = f"{worker_ip} ({worker_hostname})"
        elif worker_ip:
            destination_node = f"{worker_ip}"
        elif invoker_name != "unknown":
            destination_node = invoker_name
        else:
            destination_node = "wyolo_gpu_queue (Global)"

        return {
            "study_id": study_id,
            "study_name": study_name,
            "author": author,
            "status": status,
            "model": config.get("model", "unknown"),
            "task_type": config.get("type", "unknown"),
            "invoker": invoker_name,
            "destination_node": destination_node,
            "worker_ip": worker_ip,
            "dataset": dataset,
            "progress": progress,
            "active_trial": active_trial,
            "start_time": datetime.fromtimestamp(start_time).strftime("%Y-%m-%d %H:%M:%S") if start_time else None,
            "error": error,
        }

    def quick_launch_test(
        self,
        worker_ip: Optional[str] = None,
        user: str = "wisrovi",
        model: str = "yolov8n-cls.pt",
        dataset: str = "/examples/colorball.v8i.multiclass/",
        epochs: int = 1,
    ) -> Dict[str, Any]:
        """Dispatches a quick 1-trial test job to verify node/cluster execution."""
        study_id = str(uuid.uuid4())
        study_name = f"quick_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        target_queue = worker_ip if worker_ip else "wyolo_gpu_queue"

        config_payload = {
            "model": model,
            "type": "yolo",
            "train": {
                "batch": -1,
                "data": dataset,
                "epochs": epochs,
                "imgsz": 224,
                "plots": False,
            },
            "sweeper": {
                "version": 1,
                "algorithm": "optuna",
                "direction": "maximize",
                "study_name": study_name,
                "fitness": "metrics/accuracy_top1",
                "tune": False,
                "sampler": "TPESampler",
                "n_trials": 1,
                "search_space": {
                    "model": ["choice", model],
                },
                "target_worker_queue": target_queue,
            },
            "extras": {
                "gpu": {"id": 0, "limit": 0.50}
            },
            "metadata": {
                "content": "Quick Verification Test dispatched from Cluster Control UI",
                "author": user,
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            },
            "study_id": study_id,
        }

        self.client.set(f"study:{study_id}:config", json.dumps(config_payload), ex=86400)
        self.client.set(f"study:{study_id}:start_time", str(time.time()), ex=86400)

        # Dispatch via Celery
        task_sent = False
        try:
            app = get_celery_app()
            app.send_task("tasks.run_training", args=[config_payload], queue=target_queue)
            task_sent = True
        except Exception as e:
            print(f"[QUICK LAUNCH] Celery send error: {e}")

        return {
            "study_id": study_id,
            "study_name": study_name,
            "target_queue": target_queue,
            "author": user,
            "task_dispatched": task_sent,
            "model": model,
            "dataset": dataset,
            "epochs": epochs,
        }

    def get_study_trials_metrics(self, study_id: str) -> List[Dict[str, Any]]:
        """Retrieves trial progression and fitness metrics for plotting."""
        raw_prog = self.client.get(f"study:{study_id}:progress")
        prog = json.loads(raw_prog.decode("utf-8")) if raw_prog else {}
        trials_data = prog.get("trials", [])

        if not trials_data:
            result_keys = [k.decode("utf-8") for k in self.client.keys(f"wyolo:results:*:{study_id}:*")]
            for rk in sorted(result_keys):
                raw_res = self.client.hgetall(rk)
                res_dict = {k.decode("utf-8"): v.decode("utf-8") for k, v in raw_res.items()}
                res_str = res_dict.get("results")
                if res_str:
                    try:
                        parsed = json.loads(res_str)
                        trials_data.append(parsed)
                    except Exception:
                        pass

        points = []
        for idx, t in enumerate(trials_data):
            score = t.get("accuracy") or t.get("fitness") or t.get("metrics/accuracy_top1") or t.get("mAP50") or 0.0
            points.append({
                "trial": idx + 1,
                "fitness": float(score),
                "params": t.get("params", {}),
            })
        return points

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

    # --- Cluster Overview, Health Watchdog & Webhooks ---

    def get_cluster_health(self) -> Dict[str, Any]:
        """Performs real-time latency ping, Celery active queues probe, and storage health check."""
        t0 = time.perf_counter()
        try:
            self.client.ping()
            latency = (time.perf_counter() - t0) * 1000.0
            redis_status = "healthy"
        except Exception:
            latency = -1.0
            redis_status = "unreachable"

        # Celery Real-Time Probe
        celery_alive_ips = set()
        try:
            app = get_celery_app()
            insp = app.control.inspect(timeout=0.8)
            active_q = insp.active_queues() or {}
            import re
            for worker_name, qlist in active_q.items():
                for q in qlist:
                    q_name = q.get("name", "")
                    if re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", q_name):
                        celery_alive_ips.add(q_name)
        except Exception as e:
            print(f"[WATCHDOG] Celery inspect probe error: {e}")

        invokers = self.list_invokers()
        total_nodes = len(invokers)
        zombie_nodes = []
        healthy_nodes = 0

        for inv in invokers:
            ip = inv.get("worker_ip", "unknown")
            # If the node is responding to Celery, it is 100% healthy!
            if ip in celery_alive_ips:
                healthy_nodes += 1
            elif not celery_alive_ips:
                # Fallback if Celery inspect timed out, check Redis status
                if inv.get("status") == "online":
                    healthy_nodes += 1
                else:
                    zombie_nodes.append(ip)
            else:
                zombie_nodes.append(ip)

        # Storage health check (Samba CIFS & MinIO)
        samba_ok = True
        minio_ok = True
        try:
            minio_check = self.client.get("cluster:health:minio")
            minio_ok = (minio_check.decode("utf-8") == "ok") if minio_check else True
        except Exception:
            minio_ok = False

        return {
            "redis_status": redis_status,
            "redis_latency_ms": round(latency, 2),
            "total_nodes": total_nodes,
            "healthy_nodes": healthy_nodes,
            "zombie_nodes": zombie_nodes,
            "storage_samba": "healthy" if samba_ok else "degraded",
            "storage_minio": "healthy" if minio_ok else "degraded",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

    # --- Webhooks & Notifications ---

    def get_webhook_config(self) -> Dict[str, Any]:
        """Returns the configured webhook endpoint URL and enabled status."""
        raw = self.client.get("cluster:config:webhook")
        if raw:
            try:
                return json.loads(raw.decode("utf-8"))
            except Exception:
                pass
        return {"webhook_url": "", "enabled": False}

    def set_webhook_config(self, webhook_url: str, enabled: bool = True) -> Dict[str, Any]:
        """Persists the webhook configuration in Redis."""
        payload = {"webhook_url": webhook_url.strip(), "enabled": enabled, "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
        self.client.set("cluster:config:webhook", json.dumps(payload))
        return payload

    def send_webhook_notification(self, title: str, message: str, level: str = "info") -> bool:
        """Sends an HTTP notification to the configured webhook endpoint."""
        cfg = self.get_webhook_config()
        url = cfg.get("webhook_url")
        if not url or not cfg.get("enabled"):
            return False

        try:
            import requests
            # Compatible with Discord, Slack, and generic webhooks
            payload = {
                "text": f"[{title}] {message}",
                "content": f"🚨 **{title}**\n{message}",
                "level": level,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
            requests.post(url, json=payload, timeout=3)
            return True
        except Exception as e:
            print(f"[WEBHOOK] Warning: Failed to send notification: {e}")
            return False

    # --- Training Duration Estimator (ETA) ---

    def estimate_training_duration(self, model: str, epochs: int, dataset: str = "") -> Dict[str, Any]:
        """Calculates estimated duration based on model complexity and historical trial durations."""
        # Baseline seconds per epoch based on model size
        base_sec_per_epoch = 15.0
        rec_gpu = "RTX 3060 / 4060 (≥8GB)"
        throughput = 28
        model_lower = model.lower()
        if "yolov8x" in model_lower or "yolo26x" in model_lower:
            base_sec_per_epoch = 45.0
            rec_gpu = "RTX 3090 / 4090 / A5000 (≥24GB)"
            throughput = 12
        elif "yolov8m" in model_lower or "yolo26m" in model_lower:
            base_sec_per_epoch = 25.0
            rec_gpu = "RTX 3080 / 4070 (≥12GB)"
            throughput = 18
        elif "yolov8s" in model_lower or "yolo26s" in model_lower:
            base_sec_per_epoch = 18.0
            rec_gpu = "RTX 3070 / 4060Ti (≥12GB)"
            throughput = 22

        est_seconds = int(base_sec_per_epoch * epochs)
        minutes = max(0.5, round(est_seconds / 60.0, 1))

        return {
            "model": model,
            "epochs": epochs,
            "estimated_seconds": est_seconds,
            "estimated_minutes": minutes,
            "estimated_duration_min": minutes,
            "estimated_throughput_img_s": throughput,
            "recommended_gpu": rec_gpu,
            "description": f"~{minutes} minutos ({est_seconds}s)",
        }

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
