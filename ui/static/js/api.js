/**
 * NeuralForge Cluster Admin v3.0.0 — REST Client
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
  async getInvoker(ip) {
    return this.request(`/api/v1/invokers/${encodeURIComponent(ip)}`);
  }

  async updateInvokerLimits(ip, limits) {
    return this.request(`/api/v1/invokers/${encodeURIComponent(ip)}/limits`, {
      method: "PUT",
      body: JSON.stringify(limits),
    });
  }

  async drainInvoker(ip, drain = true) {
    return this.request(`/api/v1/invokers/${encodeURIComponent(ip)}/drain`, {
      method: "POST",
      body: JSON.stringify({ drain }),
    });
  }

  async pauseInvoker(ip, paused = true) {
    return this.request(`/api/v1/invokers/${encodeURIComponent(ip)}/pause`, {
      method: "POST",
      body: JSON.stringify({ paused }),
    });
  }

  async pruneDocker(ip) {
    return this.request(`/api/v1/invokers/${encodeURIComponent(ip)}/prune-docker`, {
      method: "POST",
    });
  }

  // --- Tasks & Queues ---
  async getActiveTasks() {
    return this.request("/api/v1/tasks/active");
  }

  async getTaskHistory(limit = 50) {
    return this.request(`/api/v1/tasks/history?limit=${limit}`);
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

  async getQueues() {
    return this.request("/api/v1/tasks/queues");
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
}

window.apiClient = new ClusterApiClient();
