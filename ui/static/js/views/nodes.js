/**
 * Nodes & Invokers Management View (nodes.invokers)
 */

window.ViewNodes = {
  id: "nodes",
  label: "Nodes & Invokers",
  icon: "⚙️",
  file: "nodes.invokers",
  category: "hardware",

  render() {
    return `
      <div class="view-header">
        <div class="view-title-group">
          <h1><span>⚙️</span> Invoker Hardware Nodes & GPU Allocations</h1>
          <p>Manage cluster workers, configure resource limits, trigger graceful drain, and broadcast Docker pulls</p>
        </div>
        <div class="view-actions">
          <button class="btn btn-secondary btn-sm" onclick="window.workbench.broadcastDockerPullPrompt()">
            <span>📥</span> Broadcast Docker Pull
          </button>
          <button class="btn btn-primary btn-sm" onclick="window.workbench.refreshCurrentView()">
            <span>🔄</span> Refresh Nodes
          </button>
        </div>
      </div>

      <div class="card-section">
        <div class="card-title">
          <span>Active Invoker Nodes (Celery & Worker Fleet)</span>
          <span style="font-size: 11px; color: var(--vscode-fg-muted);">Real-time Telemetry via Redis</span>
        </div>
        <div class="table-responsive">
          <table class="vscode-table" id="invokers-table">
            <thead>
              <tr>
                <th>Status</th>
                <th>Worker IP</th>
                <th>Hostname</th>
                <th>GPU Model</th>
                <th>VRAM (Alloc / Total)</th>
                <th>Max GPU Limit</th>
                <th>RAM Limit</th>
                <th>Drain State</th>
                <th>Node Actions</th>
              </tr>
            </thead>
            <tbody id="invokers-tbody">
              <tr><td colspan="9" style="text-align: center; color: var(--vscode-fg-muted); padding: 20px;">Fetching invoker nodes...</td></tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Resource Limits Modal Overlay -->
      <div id="limits-modal" style="display: none; position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; background: rgba(0,0,0,0.6); z-index: 6000; justify-content: center; align-items: center;">
        <div style="width: 440px; background: var(--vscode-bg-sidebar); border: 1px solid var(--vscode-border-light); border-radius: 6px; padding: 20px; box-shadow: 0 8px 30px rgba(0,0,0,0.8);">
          <div style="font-size: 14px; font-weight: 600; color: var(--vscode-fg-bright); margin-bottom: 12px; display: flex; justify-content: space-between; align-items: center;">
            <span id="limits-modal-title">⚙️ Configure Node Limits</span>
            <span style="cursor: pointer; color: var(--vscode-fg-muted);" onclick="document.getElementById('limits-modal').style.display='none'">✕</span>
          </div>
          <input type="hidden" id="limits-node-ip">
          <div class="form-group">
            <label class="form-label">MAX_GPU (Concurrent training processes per GPU):</label>
            <input type="number" id="limits-max-gpu" class="form-control" min="1" max="8">
          </div>
          <div class="form-group">
            <label class="form-label">MAX_CONCURRENT_TASKS:</label>
            <input type="number" id="limits-max-tasks" class="form-control" min="1" max="16">
          </div>
          <div style="display: flex; justify-content: flex-end; gap: 8px; margin-top: 16px;">
            <button class="btn btn-secondary btn-sm" onclick="document.getElementById('limits-modal').style.display='none'">Cancel</button>
            <button class="btn btn-primary btn-sm" onclick="window.ViewNodes.saveLimits()">Save Limits</button>
          </div>
        </div>
      </div>
    `;
  },

  async load() {
    try {
      const overview = await window.apiClient.getOverview();
      const nodes = overview.invokers || overview.workers || [];
      const tbody = document.getElementById("invokers-tbody");

      if (!nodes.length) {
        tbody.innerHTML = `<tr><td colspan="9" style="text-align: center; color: var(--vscode-fg-muted); padding: 20px;">No invokers reported.</td></tr>`;
        return;
      }

      tbody.innerHTML = nodes.map(node => {
        const ip = node.ip || node.worker_ip || "Unknown";
        const hostname = node.hostname || ip;
        const gpus = node.gpus || [];
        const gpuName = gpus[0]?.name || node.gpu_name || "NVIDIA GPU";
        const vramUsed = gpus.reduce((acc, g) => acc + (g.memory_used_mb || 0), 0);
        const vramTotal = gpus.reduce((acc, g) => acc + (g.memory_total_mb || 0), 0) || 1;
        const vramPct = Math.round((vramUsed / vramTotal) * 100);

        const isDraining = !!node.is_draining;
        const isOnline = node.is_online !== false;

        let statusBadge = `<span class="badge badge-green">Online</span>`;
        if (isDraining) statusBadge = `<span class="badge badge-amber">Draining</span>`;
        else if (!isOnline) statusBadge = `<span class="badge badge-red">Offline</span>`;

        let drainBtn = isDraining
          ? `<button class="btn btn-sm" style="background: #10B981; color: white;" onclick="window.ViewNodes.toggleDrain('${ip}', false)"><span>✅</span> Undrain</button>`
          : `<button class="btn btn-danger btn-sm" onclick="window.ViewNodes.toggleDrain('${ip}', true)"><span>⚠️</span> Drain</button>`;

        return `
          <tr>
            <td>${statusBadge}</td>
            <td><code style="font-family: var(--vscode-mono-family); font-weight: 600;">${ip}</code></td>
            <td>${hostname}</td>
            <td>${gpuName}</td>
            <td>
              <span style="font-family: var(--vscode-mono-family); font-size: 11px;">${vramUsed} / ${vramTotal} MB (${vramPct}%)</span>
            </td>
            <td><code>${node.max_gpu || 1}</code></td>
            <td><code>${node.ram_limit_gb || 'Unset'}</code></td>
            <td>
              ${isDraining ? '<span class="badge badge-amber">DRAINING</span>' : '<span class="badge badge-green">Active</span>'}
            </td>
            <td>
              <div style="display: flex; gap: 4px;">
                ${drainBtn}
                <button class="btn btn-secondary btn-sm" onclick="window.ViewNodes.openLimitsModal('${ip}', ${node.max_gpu || 1}, ${node.max_concurrent_tasks || 2})">Limits</button>
                <button class="btn btn-secondary btn-sm" onclick="window.ViewNodes.pruneDocker('${ip}')">Prune</button>
              </div>
            </td>
          </tr>
        `;
      }).join("");
    } catch (e) {
      document.getElementById("invokers-tbody").innerHTML = `
        <tr><td colspan="9" style="text-align: center; color: var(--vscode-btn-danger); padding: 20px;">
          Failed to load invokers: ${e.message}
        </td></tr>
      `;
    }
  },

  async toggleDrain(ip, shouldDrain) {
    const action = shouldDrain ? "DRAIN" : "UNDRAIN";
    const confirmMsg = shouldDrain
      ? `Are you sure you want to DRAIN node ${ip}?\nThis will stop scheduling new training tasks on this node and terminate running containers.`
      : `Resume scheduling on node ${ip}?`;

    if (!confirm(confirmMsg)) return;

    window.workbench.logTerminal("WARN", `Triggering ${action} for node ${ip}...`);
    try {
      const res = await window.apiClient.drainInvoker(ip, shouldDrain);
      window.workbench.logTerminal("SUCCESS", `Node ${ip} ${action} applied: ${JSON.stringify(res)}`);
      await this.load();
    } catch (e) {
      window.workbench.logTerminal("ERROR", `Failed to ${action} node ${ip}: ${e.message}`);
      alert(`Error applying drain: ${e.message}`);
    }
  },

  openLimitsModal(ip, maxGpu, maxTasks) {
    document.getElementById("limits-node-ip").value = ip;
    document.getElementById("limits-modal-title").textContent = `⚙️ Configure Limits: ${ip}`;
    document.getElementById("limits-max-gpu").value = maxGpu || 1;
    document.getElementById("limits-max-tasks").value = maxTasks || 2;
    document.getElementById("limits-modal").style.display = "flex";
  },

  async saveLimits() {
    const ip = document.getElementById("limits-node-ip").value;
    const maxGpu = parseInt(document.getElementById("limits-max-gpu").value, 10);
    const maxTasks = parseInt(document.getElementById("limits-max-tasks").value, 10);

    try {
      window.workbench.logTerminal("INFO", `Updating limits for ${ip}: MAX_GPU=${maxGpu}, MAX_TASKS=${maxTasks}...`);
      await window.apiClient.updateInvokerLimits(ip, { max_gpu: maxGpu, max_concurrent_tasks: maxTasks });
      window.workbench.logTerminal("SUCCESS", `Limits updated for ${ip}`);
      document.getElementById("limits-modal").style.display = "none";
      await this.load();
    } catch (e) {
      window.workbench.logTerminal("ERROR", `Failed to update limits for ${ip}: ${e.message}`);
      alert(`Failed to save limits: ${e.message}`);
    }
  },

  async pruneDocker(ip) {
    if (!confirm(`Prune dangling Docker images and stopped containers on node ${ip}?`)) return;
    try {
      window.workbench.logTerminal("INFO", `Pruning Docker on node ${ip}...`);
      const res = await window.apiClient.pruneDocker(ip);
      window.workbench.logTerminal("SUCCESS", `Docker prune on ${ip} completed: ${JSON.stringify(res)}`);
      alert(`Docker prune succeeded on ${ip}`);
    } catch (e) {
      window.workbench.logTerminal("ERROR", `Docker prune on ${ip} failed: ${e.message}`);
      alert(`Docker prune failed: ${e.message}`);
    }
  }
};
