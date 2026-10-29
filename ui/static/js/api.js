/**
 * NeuralForge Cluster Admin v3.1.8 — REST Client
 * Communicates directly with FastAPI backend on :8001
 */

class ClusterApiClient {
  constructor() {
    this.tokenKey = "neuralforge_auth_token";
    this.userKey = "neuralforge_auth_user";
    this.baseUrl = this.resolveApiUrl();
  }

  resolveApiUrl() {
    if (window.__CLUSTER_CONFIG__ && window.__CLUSTER_CONFIG__.apiUrl) {
      return window.__CLUSTER_CONFIG__.apiUrl.replace(/\/$/, "");
    }
    const hostname = window.location.hostname || "localhost";
    return `http://${hostname}:8001`;
  }

  getToken() {
    return localStorage.getItem(this.tokenKey);
  }

  setToken(token) {
    localStorage.setItem(this.tokenKey, token);
  }

  clearToken() {
    localStorage.removeItem(this.tokenKey);
    localStorage.removeItem(this.userKey);
  }

  getUser() {
    const userStr = localStorage.getItem(this.userKey);
    try {
      return userStr ? JSON.parse(userStr) : null;
    } catch (e) {
      return null;
    }
  }

  setUser(user) {
    localStorage.setItem(this.userKey, JSON.stringify(user));
  }

  isAuthenticated() {
    return !!this.getToken();
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseUrl}${endpoint}`;
    const headers = {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    };

    const token = this.getToken();
    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }

    const start = performance.now();
    try {
      const response = await fetch(url, {
        ...options,
        headers,
      });

      const elapsed = Math.round(performance.now() - start);

      if (response.status === 401 && !endpoint.includes("/auth/login")) {
        this.clearToken();
        if (window.workbench) {
          window.workbench.showAuthOverlay("Session expired. Please log in again.");
        }
        throw new Error("Unauthorized");
      }

      if (!response.ok) {
        let errorMsg = `HTTP ${response.status}: ${response.statusText}`;
        try {
          const errorData = await response.json();
          if (errorData.detail) errorMsg = errorData.detail;
        } catch (_) {}
        if (window.workbench) {
          window.workbench.logTerminal("ERROR", `${options.method || "GET"} ${endpoint} failed (${elapsed}ms): ${errorMsg}`);
        }
        throw new Error(errorMsg);
      }

      const data = await response.json();
      if (window.workbench && !endpoint.includes("/health")) {
        window.workbench.logTerminal("INFO", `${options.method || "GET"} ${endpoint} [200 OK] (${elapsed}ms)`);
      }
      return data;
    } catch (err) {
      const elapsed = Math.round(performance.now() - start);
      if (window.workbench && !endpoint.includes("/health")) {
        window.workbench.logTerminal("ERROR", `Request error ${endpoint} (${elapsed}ms): ${err.message}`);
      }
      throw err;
    }
  }

  // --- Auth Endpoints ---
  async login(username, password) {
    const data = await this.request("/api/v1/auth/login", {
      method: "POST",
      body: JSON.stringify({ username, password }),
    });
    if (data.access_token) {
      this.setToken(data.access_token);
      this.setUser({ username, role: "admin" });
    }
    return data;
  }

  async getMe() {
    return this.request("/api/v1/auth/me");
  }

  async changePassword(oldPassword, newPassword) {
    return this.request("/api/v1/auth/change-password", {
      method: "POST",
      body: JSON.stringify({ old_password: oldPassword, new_password: newPassword }),
    });
  }

  // --- Overview & Cluster ---
  async getOverview() {
    return this.request("/api/v1/cluster/overview");
  }

  async getHealth() {
    return this.request("/api/v1/cluster/health");
  }

  async getGpuBenchmarks() {
    return this.request("/api/v1/cluster/gpu-benchmarks");
  }

  async getFinOps() {
    return this.request("/api/v1/cluster/finops");
  }

  async getGreenAi() {
    return this.request("/api/v1/cluster/green-ai");
  }

  async getCapabilities() {
    return this.request("/api/v1/cluster/capabilities");
  }

  async getAuditLogs(limit = 100) {
    return this.request(`/api/v1/cluster/audit/logs?limit=${limit}`);
  }

  async getStorageInspect() {
    return this.request("/api/v1/cluster/storage/inspect");
  }

  async getDatasetsAvailable() {
    return this.request("/api/v1/cluster/datasets/available");
  }

  async validateDataset(path) {
    return this.request("/api/v1/cluster/datasets/validate", {
      method: "POST",
      body: JSON.stringify({ dataset_path: path }),
    });
  }

  async getSchedulerPolicy() {
    return this.request("/api/v1/cluster/scheduler/policy");
  }

  async setSchedulerPolicy(policy) {
    return this.request("/api/v1/cluster/scheduler/policy", {
      method: "POST",
      body: JSON.stringify(policy),
    });
  }

  async broadcastDockerPull(imageTag = null) {
    return this.request("/api/v1/cluster/images/broadcast-pull", {
      method: "POST",
      body: JSON.stringify({ image: imageTag }),
    });
  }

  async testWebhook(webhookUrl = null) {
    return this.request("/api/v1/cluster/webhook/test", {
      method: "POST",
      body: JSON.stringify({ webhook_url: webhookUrl }),
    });
  }

  // --- Invokers ---
  async getInvokers() {
    return this.request("/api/v1/invokers");
  }

  async getInvoker(ip) {
    return this.request(`/api/v1/invokers/${encodeURIComponent(ip)}`);
  }

  async updateInvokerLimits(ip, limits) {
    return this.request(`/api/v1/invokers/${encodeURIComponent(ip)}/limits`, {
      method: "PUT",
      body: JSON.stringify(limits),
    });
  }

  async drainInvoker(ip, drain = true, reason = "Maintenance", evict = true) {
    if (drain) {
      return this.request(`/api/v1/invokers/${encodeURIComponent(ip)}/drain`, {
        method: "POST",
        body: JSON.stringify({ reason, evict }),
      });
    } else {
      // Undraining is performed by calling resume
      return this.pauseInvoker(ip, false);
    }
  }

  async pauseInvoker(ip, pause = true, mode = "perpetual", hours = 4.0, until_time = null) {
    const payload = pause
      ? { action: "pause", mode: mode, hours: hours }
      : { action: "resume" };
    if (pause && until_time) {
      payload.until_time = until_time;
    }
    return this.request(`/api/v1/invokers/${encodeURIComponent(ip)}/pause`, {
      method: "POST",
      body: JSON.stringify(payload),
    });
  }

  async getNodeProcesses(ip) {
    return this.request(`/api/v1/invokers/${encodeURIComponent(ip)}/processes`);
  }

  async killNodeProcess(ip, pid) {
    return this.request(`/api/v1/invokers/${encodeURIComponent(ip)}/kill-process/${encodeURIComponent(pid)}`, {
      method: "POST",
    });
  }

  async pruneDocker(ip) {
    return this.request(`/api/v1/invokers/${encodeURIComponent(ip)}/prune-docker`, {
      method: "POST",
    });
  }

  async restartNodeService(ip) {
    return this.request(`/api/v1/invokers/${encodeURIComponent(ip)}/restart-service`, {
      method: "POST",
    });
  }

  // --- Tasks & Queues ---
  // --- Tasks & History ---
  async getActiveTasks() {
    return this.request("/api/v1/tasks/active");
  }

  async getTaskHistory(limit = 50, search = null, author = null, workerIp = null, status = null) {
    let url = `/api/v1/tasks/history?limit=${limit}`;
    if (search) url += `&search=${encodeURIComponent(search)}`;
    if (author && author !== "All") url += `&author=${encodeURIComponent(author)}`;
    if (workerIp && workerIp !== "All") url += `&worker_ip=${encodeURIComponent(workerIp)}`;
    if (status && status !== "All") url += `&status=${encodeURIComponent(status)}`;
    return this.request(url);
  }

  async cancelTask(studyId) {
    return this.request(`/api/v1/tasks/${encodeURIComponent(studyId)}/cancel`, {
      method: "POST",
    });
  }

  async quickLaunch(payload) {
    return this.request("/api/v1/tasks/quick-launch", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  }

  async getStudyReproducibility(studyId) {
    return this.request(`/api/v1/tasks/${encodeURIComponent(studyId)}/reproducibility`);
  }

  async getStudyMetrics(studyId) {
    return this.request(`/api/v1/tasks/${encodeURIComponent(studyId)}/metrics`);
  }

  async getTaskLogs(studyId, limit = 200) {
    return this.request(`/api/v1/tasks/${encodeURIComponent(studyId)}/logs?limit=${limit}`);
  }

  async getTaskDiagnostics(studyId) {
    return this.request(`/api/v1/tasks/${encodeURIComponent(studyId)}/diagnostics`);
  }

  async compareStudies(studyIds) {
    return this.request("/api/v1/tasks/compare", {
      method: "POST",
      body: JSON.stringify({ study_ids: studyIds }),
    });
  }

  async getQueues() {
    return this.request("/api/v1/tasks/queues");
  }

  async getQueuedTasks() {
    try {
      const data = await this.getQueues();
      return Array.isArray(data?.tasks) ? data.tasks : [];
    } catch (_) {
      return [];
    }
  }

  async promoteQueuedTask(taskId, targetQueue = "gpus_high") {
    return this.request(`/api/v1/tasks/queues/${encodeURIComponent(taskId)}/promote`, {
      method: "POST",
      body: JSON.stringify({ target_queue: targetQueue }),
    });
  }

  async reassignQueuedTask(taskId, targetQueue = "wyolo_gpu_queue") {
    return this.request(`/api/v1/tasks/queues/${encodeURIComponent(taskId)}/reassign`, {
      method: "POST",
      body: JSON.stringify({ target_queue: targetQueue }),
    });
  }

  async deleteQueuedTask(taskId) {
    return this.request(`/api/v1/tasks/queues/${encodeURIComponent(taskId)}`, {
      method: "DELETE",
    });
  }

  async deleteQueuedTasksBatch(taskIds) {
    return this.request("/api/v1/tasks/queues/batch-delete", {
      method: "POST",
      body: JSON.stringify({ task_ids: taskIds }),
    });
  }

  async getSweeps() {
    return this.request("/api/v1/tasks/sweeps");
  }

  async getQuarantine() {
    return this.request("/api/v1/tasks/quarantine");
  }

  async retryQuarantine(taskId) {
    return this.request(`/api/v1/tasks/quarantine/${encodeURIComponent(taskId)}/retry`, {
      method: "POST",
    });
  }

  // --- Smart Dispatch & Pre-flight ---
  async inspectDataset(path) {
    return this.request(`/api/v1/cluster/datasets/inspect?dataset_path=${encodeURIComponent(path)}`);
  }

  async recommendNode(model = "yolov8n-cls.pt") {
    return this.request(`/api/v1/cluster/recommend-node?model=${encodeURIComponent(model)}`);
  }

  async estimateDuration(model = "yolov8n-cls.pt", epochs = 1, dataset = "/examples/") {
    return this.request(`/api/v1/cluster/estimate-duration?model=${encodeURIComponent(model)}&epochs=${epochs}&dataset=${encodeURIComponent(dataset)}`);
  }

  // --- Settings & Batch Governance ---
  async batchUpdateLimits(maxGpuPercent, maxRam) {
    return this.request("/api/v1/invokers/batch-limits", {
      method: "POST",
      body: JSON.stringify({ max_gpu_percent: maxGpuPercent, max_ram: maxRam }),
    });
  }

  async applySchedulerPolicy() {
    return this.request("/api/v1/cluster/scheduler/apply-policy", {
      method: "POST",
    });
  }

  async getSupportBundle() {
    return this.request("/api/v1/cluster/support-bundle");
  }

  async getHousekeepingPreview() {
    return this.request("/api/v1/cluster/housekeeping/preview");
  }

  async purgeHousekeeping() {
    return this.request("/api/v1/cluster/housekeeping/purge", {
      method: "POST",
    });
  }

  async getWebhookConfig() {
    return this.request("/api/v1/cluster/webhook");
  }

  async saveWebhookConfig(webhookUrl, enabled = true) {
    return this.request("/api/v1/cluster/webhook", {
      method: "POST",
      body: JSON.stringify({ webhook_url: webhookUrl, enabled }),
    });
  }

  async testRichWebhook(eventType = "study_completed", webhookUrl = null) {
    return this.request("/api/v1/cluster/webhook/test-rich", {
      method: "POST",
      body: JSON.stringify({ event_type: eventType, webhook_url: webhookUrl }),
    });
  }

  async triggerWatchdogAlert() {
    return this.request("/api/v1/cluster/watchdog/check-and-alert", {
      method: "POST",
    });
  }

  async updateFinopsRate(rateEur) {
    return this.request("/api/v1/cluster/finops/rate", {
      method: "POST",
      body: JSON.stringify({ rate_eur_per_kwh: rateEur }),
    });
  }
}

window.apiClient = new ClusterApiClient();
