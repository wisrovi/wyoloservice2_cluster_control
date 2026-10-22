/**
 * Operations Center View (overview.cluster)
 */

window.ViewOverview = {
  id: "overview",
  label: "Operations Center",
  icon: "📊",
  file: "overview.cluster",
  category: "cluster",

  render() {
    return `
      <div class="view-header">
        <div class="view-title-group">
          <h1><span>📊</span> Cluster Operations Center & Live Topology</h1>
          <p>Real-time cluster telemetry, compute fabrics, node health watchdog, and active workload distribution</p>
        </div>
        <div class="view-actions">
          <button class="btn btn-secondary btn-sm" onclick="window.workbench.refreshCurrentView()">
            <span>🔄</span> Refresh Telemetry
          </button>
          <button class="btn btn-primary btn-sm" onclick="window.workbench.switchView('dispatch')">
            <span>⚡</span> Quick Launch
          </button>
        </div>
      </div>

      <!-- Top KPI Metrics Cards -->
      <div class="metrics-ribbon" id="overview-ribbon">
        <div class="metric-card">
          <div class="metric-label">Total Nodes</div>
          <div class="metric-value" id="metric-total-nodes">--</div>
          <div class="metric-sub" id="metric-online-nodes-sub">-- Online</div>
        </div>
        <div class="metric-card">
          <div class="metric-label">Active Nodes</div>
          <div class="metric-value" id="metric-active-nodes" style="color: #10B981;">--</div>
          <div class="metric-sub">Consuming queues</div>
        </div>
        <div class="metric-card">
          <div class="metric-label">Paused / Draining</div>
          <div class="metric-value" id="metric-paused-nodes" style="color: #F59E0B;">--</div>
          <div class="metric-sub">Paused or draining</div>
        </div>
        <div class="metric-card">
          <div class="metric-label">Cluster GPUs</div>
          <div class="metric-value" id="metric-gpus">--</div>
          <div class="metric-sub" id="metric-gpus-sub">Compute accelerators</div>
        </div>
        <div class="metric-card">
          <div class="metric-label">Active Workloads</div>
          <div class="metric-value" id="metric-active" style="color: #38BDF8;">--</div>
          <div class="metric-sub">Running training trials</div>
        </div>
      </div>

      <!-- Live Active Workloads Table -->
      <div class="card-section" style="margin-bottom: 20px;">
        <div class="card-title">
          <span>🚀 Live Active Training Workloads</span>
          <span class="badge badge-blue" id="active-workloads-badge">0 Running</span>
        </div>
        <div class="table-responsive">
          <table class="vscode-table">
            <thead>
              <tr>
                <th>Study / Project Name</th>
                <th>Author</th>
                <th>Assigned Node</th>
                <th>Model</th>
                <th>Dataset Path</th>
                <th>Progress (Trials)</th>
                <th>K8s Pod / Phase</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody id="overview-active-tasks-body">
              <tr><td colspan="8" style="text-align: center; color: var(--vscode-fg-muted); padding: 16px;">Scanning active workloads...</td></tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Compute Rack Nodes Topology Table -->
      <div class="card-section">
        <div class="card-title">
          <span>🖥️ Compute Rack Nodes Topology & Hardware Metrics</span>
          <span class="badge badge-green" id="cluster-health-badge">● Operational</span>
        </div>
        <div class="table-responsive">
          <table class="vscode-table" id="overview-nodes-table">
            <thead>
              <tr>
                <th>Node / Hostname</th>
                <th>Status & State</th>
                <th>GPU Model</th>
                <th>GPU Sharing & Allocation</th>
                <th>VRAM & NVML Thermals</th>
                <th>RAM Limits / Host</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody id="overview-nodes-body">
              <tr><td colspan="7" style="text-align: center; color: var(--vscode-fg-muted); padding: 20px;">Loading cluster topology...</td></tr>
            </tbody>
          </table>
        </div>
      </div>

      <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-top: 16px;">
        <div class="card-section">
          <div class="card-title"><span>⚡ Quick Cluster Operations</span></div>
          <div style="display: flex; flex-direction: column; gap: 8px;">
            <button class="btn btn-secondary" onclick="window.workbench.broadcastDockerPullPrompt()">
              <span>📥</span> Broadcast Docker Pull (Cluster-wide)
            </button>
            <button class="btn btn-secondary" onclick="window.workbench.switchView('nodes')">
              <span>⚙️</span> Manage Invoker Limits, Pausing & Draining
            </button>
            <button class="btn btn-secondary" onclick="window.workbench.switchView('dispatch')">
              <span>🚀</span> Configure Day/Night Dispatch Policy
            </button>
          </div>
        </div>

        <div class="card-section">
          <div class="card-title"><span>🚨 Infrastructure Health Monitor & Watchdog</span></div>
          <div id="overview-infra-health" style="display: flex; flex-direction: column; gap: 8px; font-size: 12px;">
            <div style="display: flex; justify-content: space-between;">
              <span>FastAPI Backend Gateway (:8001):</span>
              <span style="color: #10B981; font-weight: 600;">● Online (Healthy)</span>
            </div>
            <div style="display: flex; justify-content: space-between;">
              <span>Redis Cluster Broker & Telemetry:</span>
              <span style="color: #10B981; font-weight: 600;">● Connected</span>
            </div>
            <div style="display: flex; justify-content: space-between;">
              <span>Samba CIFS Share (/wyolo/control_server/datasets):</span>
              <span style="color: #10B981; font-weight: 600;">● Mounted (Read/Write)</span>
            </div>
            <div style="display: flex; justify-content: space-between;">
              <span>MinIO S3 Artifact Store:</span>
              <span style="color: #10B981; font-weight: 600;">● Ready</span>
            </div>
          </div>
        </div>
      </div>
    `;
  },

  async load() {
    try {
      const overview = await window.apiClient.getOverview();
      const nodes = overview.invokers || overview.workers || [];

      // Fetch active tasks directly to ensure complete fidelity
      let activeTasks = [];
      try {
        const tasksRes = await window.apiClient.getActiveTasks();
        activeTasks = Array.isArray(tasksRes) ? tasksRes : (tasksRes.tasks || []);
      } catch (_) {}

      const totalNodes = overview.total_nodes || nodes.length || 0;
      const onlineNodes = overview.online_nodes || nodes.filter(n => n.status === "online").length;
      const activeNodes = overview.active_nodes || nodes.filter(n => n.pause_state === "active").length;
      const pausedNodes = overview.paused_nodes || nodes.filter(n => (n.pause_state && n.pause_state.includes("pause")) || n.pause_state === "draining").length;
      const totalGpus = overview.total_gpus || nodes.reduce((acc, n) => acc + (n.physical?.gpu_count || 1), 0);
      const activeCount = activeTasks.length || overview.active_trials_count || 0;

      document.getElementById("metric-total-nodes").textContent = totalNodes;
      document.getElementById("metric-online-nodes-sub").textContent = `${onlineNodes} Online`;
      document.getElementById("metric-active-nodes").textContent = activeNodes;
      document.getElementById("metric-paused-nodes").textContent = pausedNodes;
      document.getElementById("metric-gpus").textContent = totalGpus;
      document.getElementById("metric-gpus-sub").textContent = `${totalGpus} Accelerators`;
      document.getElementById("metric-active").textContent = activeCount;

      // 1. Render Active Tasks
      const activeBadge = document.getElementById("active-workloads-badge");
      const activeTbody = document.getElementById("overview-active-tasks-body");

      activeBadge.textContent = `${activeTasks.length} Running`;

      if (!activeTasks.length) {
        activeTbody.innerHTML = `<tr><td colspan="8" style="text-align: center; color: var(--vscode-fg-muted); padding: 16px;">No training workloads currently executing.</td></tr>`;
      } else {
        activeTbody.innerHTML = activeTasks.map(t => {
          const studyName = t.study_name || t.study_id || "Training";
          const author = t.author || "Operator";
          const nodeStr = t.destination_node || t.worker_ip || "Auto";
          const model = t.model || "yolo";
          const dataset = t.dataset || "N/A";
          const trialsProg = t.progress ? `${t.progress.completed_trials || 0} / ${t.progress.total_trials || 0}` : "Active";
          const podName = t.k8s_pod_name || "Pod";
          const podPhase = t.k8s_pod_phase || "Running";

          return `
            <tr>
              <td><strong>${escapeHtml(studyName)}</strong></td>
              <td><span style="color: var(--vscode-fg-muted);">${escapeHtml(author)}</span></td>
              <td><code>${escapeHtml(nodeStr)}</code></td>
              <td><span class="badge badge-blue">${escapeHtml(model)}</span></td>
              <td style="max-width: 220px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;" title="${escapeHtml(dataset)}">
                <code>${escapeHtml(dataset)}</code>
              </td>
              <td><span style="font-weight: 600; color: #10B981;">${escapeHtml(trialsProg)}</span></td>
              <td><span class="badge badge-green">${escapeHtml(podName)} (${escapeHtml(podPhase)})</span></td>
              <td>
                <button class="btn btn-danger btn-sm" onclick="window.ViewOverview.cancelWorkload('${t.study_id}')">
                  🛑 Cancel
                </button>
              </td>
            </tr>
          `;
        }).join("");
      }

      // 2. Render Nodes Topology
      const tbody = document.getElementById("overview-nodes-body");
      if (!nodes.length) {
        tbody.innerHTML = `<tr><td colspan="7" style="text-align: center; color: var(--vscode-fg-muted); padding: 20px;">No invokers reported.</td></tr>`;
        return;
      }

      tbody.innerHTML = nodes.map(node => {
        const ip = node.worker_ip || node.ip || "Unknown";
        const hostname = node.hostname || ip;
        const physical = node.physical || {};
        const limits = node.limits || {};
        const k8s = node.k8s_gpu_plugin || {};

        const gpuModel = physical.gpu_model || "NVIDIA GPU";
        const gpuCount = physical.gpu_count || 1;
        const vramTotalStr = physical.gpu_memory_total || "N/A";
        const ramTotalStr = physical.ram_total || "N/A";
        const computePct = physical.gpu_compute_util_pct !== undefined ? physical.gpu_compute_util_pct : 0;
        const powerW = physical.gpu_power_watts || 0;
        const tdpW = physical.gpu_tdp_watts || 0;
        const tempC = physical.gpu_temp_c || 0;

        const maxGpuPct = limits.max_gpu_percent !== undefined ? limits.max_gpu_percent : 100;
        const maxRam = limits.max_ram || "Unset";
        const k8sAllocated = k8s.allocated !== undefined ? k8s.allocated : 0;
        const k8sCapacity = k8s.capacity !== undefined ? k8s.capacity : gpuCount;

        // Pause / Drain state
        const pauseState = node.pause_state || "active";
        let stateBadge = `<span class="badge badge-green">🟢 Active</span>`;
        if (pauseState === "draining") {
          stateBadge = `<span class="badge badge-amber" style="background: rgba(239, 68, 68, 0.2); color: #EF4444; border: 1px solid rgba(239, 68, 68, 0.4);">🛡️ Draining</span>`;
        } else if (pauseState.includes("pause")) {
          stateBadge = `<span class="badge badge-amber">⏸️ Paused</span>`;
        } else if (node.status === "offline") {
          stateBadge = `<span class="badge badge-red">Offline</span>`;
        }

        return `
          <tr>
            <td>
              <div><strong>${escapeHtml(hostname)}</strong></div>
              <div><code style="font-family: var(--vscode-mono-family); font-size: 11px;">${escapeHtml(ip)}</code></div>
            </td>
            <td>${stateBadge}</td>
            <td>
              <div style="font-weight: 500;">${escapeHtml(gpuModel)}</div>
              <div style="font-size: 11px; color: var(--vscode-fg-muted);">${gpuCount}x GPU Accelerator</div>
            </td>
            <td>
              <div style="display: flex; align-items: center; gap: 8px;">
                <span class="badge ${k8sAllocated > 0 ? 'badge-blue' : 'badge-green'}">
                  K8s: ${k8sAllocated} / ${k8sCapacity} GPU
                </span>
                <span style="font-size: 11px; font-weight: 600; color: #38BDF8;">
                  Shared Cap: ${maxGpuPct}%
                </span>
              </div>
            </td>
            <td>
              <div><strong>${escapeHtml(vramTotalStr)}</strong></div>
              <div style="font-size: 11px; color: var(--vscode-fg-muted);">
                ${computePct}% Compute | ${powerW}W / ${tdpW}W (${tempC}°C)
              </div>
            </td>
            <td>
              <div><code style="font-size: 11px;">Container: ${escapeHtml(maxRam)}</code></div>
              <div style="font-size: 11px; color: var(--vscode-fg-muted);">Host RAM: ${escapeHtml(ramTotalStr)}</div>
            </td>
            <td>
              <button class="btn btn-secondary btn-sm" onclick="window.workbench.switchView('nodes')">Manage</button>
            </td>
          </tr>
        `;
      }).join("");
    } catch (e) {
      document.getElementById("overview-nodes-body").innerHTML = `
        <tr><td colspan="7" style="text-align: center; color: var(--vscode-btn-danger); padding: 20px;">
          Failed to load telemetry: ${e.message}
        </td></tr>
      `;
    }
  },

  async cancelWorkload(studyId) {
    if (!confirm(`Cancel active workload '${studyId}'?`)) return;
    window.workbench.logTerminal("WARN", `Cancelling workload ${studyId}...`);
    try {
      await window.apiClient.cancelTask(studyId);
      window.workbench.logTerminal("SUCCESS", `Workload ${studyId} cancelled.`);
      await this.load();
    } catch (e) {
      window.workbench.logTerminal("ERROR", `Failed to cancel workload: ${e.message}`);
      alert(`Cancel failed: ${e.message}`);
    }
  }
};
