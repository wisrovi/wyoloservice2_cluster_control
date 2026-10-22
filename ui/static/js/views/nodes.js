/**
 * Nodes & Invokers Management View (nodes.invokers)
 * Complete hardware telemetry, GPU sharing allocation, pause controls, and live process inspection
 */

window.ViewNodes = {
  id: "nodes",
  label: "Nodes & Invokers",
  icon: "⚙️",
  file: "nodes.invokers",
  category: "hardware",

  invokersData: [],
  activeFilterStatus: "all",
  activeFilterGpu: "all",
  searchQuery: "",

  render() {
    return `
      <div class="view-header">
        <div class="view-title-group">
          <h1><span>⚙️</span> Invoker Hardware Nodes & GPU Allocation Fabric</h1>
          <p>Configure resource caps (VRAM %, RAM, CPU), manage pause/drain states, inspect live GPU processes, and trigger maintenance</p>
        </div>
        <div class="view-actions">
          <button class="btn btn-secondary btn-sm" onclick="window.workbench.broadcastDockerPullPrompt()">
            <span>📥</span> Broadcast Pull
          </button>
          <button class="btn btn-primary btn-sm" onclick="window.workbench.refreshCurrentView()">
            <span>🔄</span> Refresh Nodes
          </button>
        </div>
      </div>

      <!-- Filter Toolbar -->
      <div class="card-section" style="margin-bottom: 16px; padding: 12px 16px;">
        <div style="display: flex; flex-wrap: wrap; gap: 12px; align-items: center; justify-content: space-between;">
          <div style="display: flex; gap: 8px; flex: 1; min-width: 280px; max-width: 400px;">
            <input type="text" id="inv-search-input" class="form-control" placeholder="Search by IP, hostname, or GPU model..." oninput="window.ViewNodes.onSearch(this.value)">
          </div>

          <!-- Status Filter Buttons -->
          <div style="display: flex; gap: 6px; align-items: center;" id="inv-status-filters">
            <button class="btn btn-sm btn-secondary active" id="filter-btn-all" onclick="window.ViewNodes.setStatusFilter('all')">
              🔘 All (<span id="cnt-all">0</span>)
            </button>
            <button class="btn btn-sm btn-secondary" id="filter-btn-active" onclick="window.ViewNodes.setStatusFilter('active')">
              🟢 Active (<span id="cnt-active">0</span>)
            </button>
            <button class="btn btn-sm btn-secondary" id="filter-btn-paused" onclick="window.ViewNodes.setStatusFilter('paused')">
              ⏸️ Paused (<span id="cnt-paused">0</span>)
            </button>
            <button class="btn btn-sm btn-secondary" id="filter-btn-draining" onclick="window.ViewNodes.setStatusFilter('draining')">
              🛡️ Draining (<span id="cnt-draining">0</span>)
            </button>
          </div>

          <!-- Batch Action Controls -->
          <div style="display: flex; gap: 6px;">
            <button class="btn btn-secondary btn-sm" onclick="window.ViewNodes.batchPause(true)" title="Pause public queues on all nodes">
              ⏸️ Pause All
            </button>
            <button class="btn btn-secondary btn-sm" onclick="window.ViewNodes.batchPause(false)" title="Resume task consumption on all nodes">
              ▶️ Resume All
            </button>
          </div>
        </div>
      </div>

      <!-- Main Invokers Table -->
      <div class="card-section">
        <div class="card-title">
          <span>Active Invoker Nodes & Dynamic Compute Allocations</span>
          <span style="font-size: 11px; color: var(--vscode-fg-muted);">Live Redis Heartbeats & NVML Telemetry</span>
        </div>
        <div class="table-responsive">
          <table class="vscode-table" id="invokers-table">
            <thead>
              <tr>
                <th>Node / Hostname</th>
                <th>State & Health</th>
                <th>GPU Model</th>
                <th>GPU Sharing vs Total</th>
                <th>VRAM & NVML Thermals</th>
                <th>RAM Limits & Host</th>
                <th>Node Actions</th>
              </tr>
            </thead>
            <tbody id="invokers-tbody">
              <tr><td colspan="7" style="text-align: center; color: var(--vscode-fg-muted); padding: 20px;">Fetching invoker nodes...</td></tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Resource Limits Modal Overlay -->
      <div id="limits-modal" style="display: none; position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; background: rgba(0,0,0,0.6); z-index: 6000; justify-content: center; align-items: center;">
        <div style="width: 480px; max-width: 90vw; background: var(--vscode-bg-sidebar); border: 1px solid var(--vscode-border-light); border-radius: 6px; padding: 20px; box-shadow: 0 8px 30px rgba(0,0,0,0.8);">
          <div style="font-size: 14px; font-weight: 600; color: var(--vscode-fg-bright); margin-bottom: 12px; display: flex; justify-content: space-between; align-items: center;">
            <span id="limits-modal-title">⚙️ Configure Compute Limits</span>
            <span style="cursor: pointer; color: var(--vscode-fg-muted);" onclick="document.getElementById('limits-modal').style.display='none'">✕</span>
          </div>
          <input type="hidden" id="limits-node-ip">

          <div class="form-group">
            <div style="display: flex; justify-content: space-between;">
              <label class="form-label">VRAM Sharing Cap (MAX_GPU %):</label>
              <span id="limits-gpu-pct-val" style="font-weight: 600; color: #38BDF8;">50%</span>
            </div>
            <input type="range" id="limits-max-gpu" class="form-control" min="10" max="100" step="5" value="50" oninput="document.getElementById('limits-gpu-pct-val').textContent = this.value + '%'">
            <div style="font-size: 11px; color: var(--vscode-fg-muted); margin-top: 3px;">
              Percentage of total GPU VRAM allocated to training containers.
            </div>
          </div>

          <div class="form-group">
            <label class="form-label">Container RAM Limit (e.g. 12g, 16g, 24g):</label>
            <input type="text" id="limits-max-ram" class="form-control" placeholder="12g">
            <div style="font-size: 11px; color: var(--vscode-fg-muted); margin-top: 3px;">
              Maximum system RAM allowed for the container before cgroup limits apply.
            </div>
          </div>

          <div class="form-group">
            <div style="display: flex; justify-content: space-between;">
              <label class="form-label">CPU Cores Allocated:</label>
              <span id="limits-cpu-val" style="font-weight: 600; color: #38BDF8;">8.0 cores</span>
            </div>
            <input type="range" id="limits-max-cpu" class="form-control" min="1" max="32" step="0.5" value="8" oninput="document.getElementById('limits-cpu-val').textContent = this.value + ' cores'">
          </div>

          <div class="form-group">
            <div style="display: flex; justify-content: space-between;">
              <label class="form-label">PyTorch Shared Memory (/dev/shm GiB):</label>
              <span id="limits-shm-val" style="font-weight: 600; color: #38BDF8;">8.0 GiB</span>
            </div>
            <input type="range" id="limits-shm" class="form-control" min="2" max="64" step="2" value="8" oninput="document.getElementById('limits-shm-val').textContent = this.value + ' GiB'">
            <div style="font-size: 11px; color: var(--vscode-fg-muted); margin-top: 3px;">
              Shared memory size in emptyDir to prevent PyTorch DataLoader Bus errors.
            </div>
          </div>

          <div style="display: flex; justify-content: flex-end; gap: 8px; margin-top: 18px;">
            <button class="btn btn-secondary btn-sm" onclick="document.getElementById('limits-modal').style.display='none'">Cancel</button>
            <button class="btn btn-primary btn-sm" onclick="window.ViewNodes.saveLimits()">Save Limits to Redis</button>
          </div>
        </div>
      </div>

      <!-- Live GPU Processes Modal Overlay -->
      <div id="processes-modal" style="display: none; position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; background: rgba(0,0,0,0.6); z-index: 6000; justify-content: center; align-items: center;">
        <div style="width: 720px; max-width: 95vw; background: var(--vscode-bg-sidebar); border: 1px solid var(--vscode-border-light); border-radius: 6px; padding: 20px; box-shadow: 0 8px 30px rgba(0,0,0,0.8);">
          <div style="font-size: 14px; font-weight: 600; color: var(--vscode-fg-bright); margin-bottom: 12px; display: flex; justify-content: space-between; align-items: center;">
            <span id="processes-modal-title">🔍 Live GPU Compute Processes & Zombie Monitor</span>
            <span style="cursor: pointer; color: var(--vscode-fg-muted);" onclick="document.getElementById('processes-modal').style.display='none'">✕</span>
          </div>
          <div id="processes-modal-summary" style="margin-bottom: 12px; font-size: 12px;"></div>
          <div class="table-responsive" style="max-height: 340px; overflow-y: auto;">
            <table class="vscode-table">
              <thead>
                <tr>
                  <th>PID</th>
                  <th>Process Name</th>
                  <th>VRAM Used</th>
                  <th>Elapsed / Started</th>
                  <th>Status</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody id="processes-tbody">
                <tr><td colspan="6" style="text-align: center; color: var(--vscode-fg-muted); padding: 16px;">Querying node processes...</td></tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    `;
  },

  async load() {
    try {
      const invokers = await window.apiClient.getInvokers();
      this.invokersData = Array.isArray(invokers) ? invokers : (invokers.invokers || []);
      this.updateCounts();
      this.renderTable();
    } catch (e) {
      document.getElementById("invokers-tbody").innerHTML = `
        <tr><td colspan="7" style="text-align: center; color: var(--vscode-btn-danger); padding: 20px;">
          Failed to load invokers: ${e.message}
        </td></tr>
      `;
    }
  },

  updateCounts() {
    const total = this.invokersData.length;
    const active = this.invokersData.filter(i => i.pause_state === "active").length;
    const paused = this.invokersData.filter(i => i.pause_state && i.pause_state.includes("pause")).length;
    const draining = this.invokersData.filter(i => i.pause_state === "draining").length;

    document.getElementById("cnt-all").textContent = total;
    document.getElementById("cnt-active").textContent = active;
    document.getElementById("cnt-paused").textContent = paused;
    document.getElementById("cnt-draining").textContent = draining;
  },

  onSearch(val) {
    this.searchQuery = val.trim().toLowerCase();
    this.renderTable();
  },

  setStatusFilter(status) {
    this.activeFilterStatus = status;
    document.querySelectorAll("#inv-status-filters .btn").forEach(b => b.classList.remove("active"));
    const activeBtn = document.getElementById(`filter-btn-${status}`);
    if (activeBtn) activeBtn.classList.add("active");
    this.renderTable();
  },

  renderTable() {
    const tbody = document.getElementById("invokers-tbody");
    let filtered = this.invokersData;

    // 1. Status Filter
    if (this.activeFilterStatus === "active") {
      filtered = filtered.filter(i => i.pause_state === "active");
    } else if (this.activeFilterStatus === "paused") {
      filtered = filtered.filter(i => i.pause_state && i.pause_state.includes("pause"));
    } else if (this.activeFilterStatus === "draining") {
      filtered = filtered.filter(i => i.pause_state === "draining");
    }

    // 2. Search Query
    if (this.searchQuery) {
      filtered = filtered.filter(i => {
        const ip = (i.worker_ip || i.ip || "").toLowerCase();
        const hostname = (i.hostname || "").toLowerCase();
        const gpu = (i.physical?.gpu_model || "").toLowerCase();
        return ip.includes(this.searchQuery) || hostname.includes(this.searchQuery) || gpu.includes(this.searchQuery);
      });
    }

    if (!filtered.length) {
      tbody.innerHTML = `<tr><td colspan="7" style="text-align: center; color: var(--vscode-fg-muted); padding: 20px;">No invoker nodes matched filter criteria.</td></tr>`;
      return;
    }

    tbody.innerHTML = filtered.map(node => {
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
      const maxCpu = limits.max_cpu_cores !== undefined ? limits.max_cpu_cores : "Auto";
      const shmGb = limits.shm_size_gb !== undefined ? limits.shm_size_gb : 8;

      const k8sAllocated = k8s.allocated !== undefined ? k8s.allocated : 0;
      const k8sCapacity = k8s.capacity !== undefined ? k8s.capacity : gpuCount;

      // Status Badges
      const pauseState = node.pause_state || "active";
      let statusBadge = `<span class="badge badge-green">🟢 Active</span>`;
      let pauseActionBtn = `<button class="btn btn-secondary btn-sm" onclick="window.ViewNodes.togglePause('${ip}', true)">⏸️ Pause</button>`;

      if (pauseState === "draining") {
        statusBadge = `<span class="badge badge-amber" style="background: rgba(239, 68, 68, 0.2); color: #EF4444; border: 1px solid rgba(239, 68, 68, 0.4);">🛡️ Draining</span>`;
        pauseActionBtn = `<button class="btn btn-sm" style="background: #10B981; color: white;" onclick="window.ViewNodes.toggleDrain('${ip}', false)">✅ Undrain</button>`;
      } else if (pauseState.includes("pause")) {
        statusBadge = `<span class="badge badge-amber">⏸️ Paused</span>`;
        pauseActionBtn = `<button class="btn btn-sm" style="background: #10B981; color: white;" onclick="window.ViewNodes.togglePause('${ip}', false)">▶️ Resume</button>`;
      } else if (node.status === "offline") {
        statusBadge = `<span class="badge badge-red">Offline</span>`;
      }

      let drainBtn = pauseState === "draining"
        ? ""
        : `<button class="btn btn-danger btn-sm" onclick="window.ViewNodes.toggleDrain('${ip}', true)">⚠️ Drain</button>`;

      return `
        <tr>
          <td>
            <div style="font-weight: 600;">${escapeHtml(hostname)}</div>
            <div><code style="font-family: var(--vscode-mono-family); font-size: 11px;">${escapeHtml(ip)}</code></div>
          </td>
          <td>
            <div>${statusBadge}</div>
            <div style="font-size: 10px; color: var(--vscode-fg-muted); margin-top: 3px;">${escapeHtml(node.orchestration_runtime || 'K8s')}</div>
          </td>
          <td>
            <div style="font-weight: 500;">${escapeHtml(gpuModel)}</div>
            <div style="font-size: 11px; color: var(--vscode-fg-muted);">${gpuCount}x GPU Accelerator</div>
          </td>
          <td>
            <div style="display: flex; flex-direction: column; gap: 3px;">
              <div style="display: flex; align-items: center; justify-content: space-between; font-size: 11px;">
                <span>K8s Alloc: <strong>${k8sAllocated} / ${k8sCapacity} GPU</strong></span>
                <span style="font-weight: 600; color: ${k8sAllocated > 0 ? '#38BDF8' : '#10B981'};">
                  ${k8sAllocated > 0 ? 'Allocated' : 'Available'}
                </span>
              </div>
              <div style="height: 5px; background: #3C3C3C; border-radius: 3px; overflow: hidden;">
                <div style="width: ${maxGpuPct}%; height: 100%; background: ${maxGpuPct > 80 ? '#EF4444' : '#007ACC'};"></div>
              </div>
              <div style="font-size: 10px; color: var(--vscode-fg-muted);">
                Shared VRAM Cap: <strong style="color: #38BDF8;">${maxGpuPct}%</strong>
              </div>
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
            <div style="font-size: 11px; color: var(--vscode-fg-muted);">Host: ${escapeHtml(ramTotalStr)} | ${maxCpu} Cores</div>
          </td>
          <td>
            <div style="display: flex; flex-wrap: wrap; gap: 4px;">
              ${pauseActionBtn}
              ${drainBtn}
              <button class="btn btn-secondary btn-sm" onclick="window.ViewNodes.openLimitsModal('${ip}', ${maxGpuPct}, '${maxRam}', ${typeof maxCpu === 'number' ? maxCpu : 8}, ${shmGb})">
                Limits
              </button>
              <button class="btn btn-secondary btn-sm" onclick="window.ViewNodes.openProcessesModal('${ip}', '${escapeHtml(hostname)}')">
                🔍 Procs
              </button>
              <button class="btn btn-secondary btn-sm" onclick="window.ViewNodes.pruneDocker('${ip}')">
                Prune
              </button>
            </div>
          </td>
        </tr>
      `;
    }).join("");
  },

  async togglePause(ip, shouldPause) {
    const actionStr = shouldPause ? "PAUSE" : "RESUME";
    window.workbench.logTerminal("WARN", `Triggering ${actionStr} for node ${ip}...`);
    try {
      await window.apiClient.pauseInvoker(ip, shouldPause);
      window.workbench.logTerminal("SUCCESS", `Node ${ip} ${actionStr} executed successfully.`);
      await this.load();
    } catch (e) {
      window.workbench.logTerminal("ERROR", `Failed to ${actionStr} node ${ip}: ${e.message}`);
      alert(`Error updating pause state: ${e.message}`);
    }
  },

  async toggleDrain(ip, shouldDrain) {
    const action = shouldDrain ? "DRAIN" : "UNDRAIN";
    const confirmMsg = shouldDrain
      ? `Are you sure you want to DRAIN node ${ip}?\nThis halts public queues, evicts active workloads immediately with SIGKILL, and halts new task scheduling.`
      : `Resume scheduling and undrain node ${ip}?`;

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

  async batchPause(shouldPause) {
    const actionStr = shouldPause ? "PAUSE ALL" : "RESUME ALL";
    if (!confirm(`Are you sure you want to ${actionStr} invoker nodes across the cluster?`)) return;

    window.workbench.logTerminal("WARN", `Executing ${actionStr} across cluster invokers...`);
    try {
      for (const node of this.invokersData) {
        const ip = node.worker_ip || node.ip;
        if (ip) {
          await window.apiClient.pauseInvoker(ip, shouldPause);
        }
      }
      window.workbench.logTerminal("SUCCESS", `Completed ${actionStr} across all nodes.`);
      await this.load();
    } catch (e) {
      window.workbench.logTerminal("ERROR", `Batch pause error: ${e.message}`);
      alert(`Batch pause error: ${e.message}`);
    }
  },

  openLimitsModal(ip, maxGpuPct, maxRam, maxCpu, shmGb) {
    document.getElementById("limits-node-ip").value = ip;
    document.getElementById("limits-modal-title").textContent = `⚙️ Configure Compute Limits: ${ip}`;
    document.getElementById("limits-max-gpu").value = maxGpuPct || 50;
    document.getElementById("limits-gpu-pct-val").textContent = `${maxGpuPct || 50}%`;
    document.getElementById("limits-max-ram").value = maxRam || "12g";
    document.getElementById("limits-max-cpu").value = maxCpu || 8;
    document.getElementById("limits-cpu-val").textContent = `${maxCpu || 8} cores`;
    document.getElementById("limits-shm").value = shmGb || 8;
    document.getElementById("limits-shm-val").textContent = `${shmGb || 8} GiB`;
    document.getElementById("limits-modal").style.display = "flex";
  },

  async saveLimits() {
    const ip = document.getElementById("limits-node-ip").value;
    const maxGpuPct = parseFloat(document.getElementById("limits-max-gpu").value);
    const maxRam = document.getElementById("limits-max-ram").value.trim();
    const maxCpu = parseFloat(document.getElementById("limits-max-cpu").value);
    const shmGb = parseFloat(document.getElementById("limits-shm").value);

    try {
      window.workbench.logTerminal("INFO", `Saving resource limits for ${ip}: GPU=${maxGpuPct}%, RAM=${maxRam}, CPU=${maxCpu}, SHM=${shmGb}GiB...`);
      await window.apiClient.updateInvokerLimits(ip, {
        max_gpu_percent: maxGpuPct,
        max_ram: maxRam,
        max_cpu_cores: maxCpu,
        shm_size_gb: shmGb,
      });
      window.workbench.logTerminal("SUCCESS", `Limits saved to Redis for ${ip}.`);
      document.getElementById("limits-modal").style.display = "none";
      await this.load();
    } catch (e) {
      window.workbench.logTerminal("ERROR", `Failed to save limits for ${ip}: ${e.message}`);
      alert(`Failed to save limits: ${e.message}`);
    }
  },

  async openProcessesModal(ip, hostname) {
    const modal = document.getElementById("processes-modal");
    const title = document.getElementById("processes-modal-title");
    const summary = document.getElementById("processes-modal-summary");
    const tbody = document.getElementById("processes-tbody");

    title.textContent = `🔍 Live GPU Processes & Zombie Monitor: ${hostname} (${ip})`;
    summary.innerHTML = `Querying NVML processes on <code>${ip}</code>...`;
    tbody.innerHTML = `<tr><td colspan="6" style="text-align: center; color: var(--vscode-fg-muted); padding: 16px;">Scanning GPU memory...</td></tr>`;
    modal.style.display = "flex";

    try {
      const data = await window.apiClient.getNodeProcesses(ip);
      const procs = data.processes || [];

      summary.innerHTML = `
        <div style="display: flex; gap: 16px; align-items: center;">
          <span>GPU: <strong>${escapeHtml(data.gpu_model || 'NVIDIA GPU')}</strong></span>
          <span>Total VRAM: <strong>${data.total_vram_mb || 0} MB</strong></span>
          <span>Used: <strong style="color: #38BDF8;">${data.used_vram_mb || 0} MB</strong></span>
          <span>Free: <strong style="color: #10B981;">${data.free_vram_mb || 0} MB</strong></span>
        </div>
      `;

      if (!procs.length) {
        tbody.innerHTML = `<tr><td colspan="6" style="text-align: center; color: var(--vscode-fg-muted); padding: 16px;">No active compute processes using GPU VRAM on this node.</td></tr>`;
        return;
      }

      tbody.innerHTML = procs.map(p => {
        const isZombie = !!p.is_zombie;
        const statusBadge = isZombie
          ? `<span class="badge badge-red">⚠️ ZOMBIE</span>`
          : `<span class="badge badge-green">⚡ ACTIVE</span>`;

        return `
          <tr>
            <td><code>${p.pid}</code></td>
            <td><strong>${escapeHtml(p.name || 'Process')}</strong></td>
            <td><code style="color: #38BDF8;">${Math.round(p.vram_used_mb || 0)} MB</code></td>
            <td>${escapeHtml(p.elapsed || 'N/A')}</td>
            <td>${statusBadge}</td>
            <td>
              <button class="btn btn-danger btn-sm" onclick="window.ViewNodes.killProcess('${ip}', ${p.pid})">
                🛑 Kill PID
              </button>
            </td>
          </tr>
        `;
      }).join("");
    } catch (e) {
      summary.innerHTML = `<span style="color: #EF4444;">Failed to fetch processes: ${escapeHtml(e.message)}</span>`;
      tbody.innerHTML = `<tr><td colspan="6" style="text-align: center; color: var(--vscode-fg-muted); padding: 16px;">Telemetry query failed.</td></tr>`;
    }
  },

  async killProcess(ip, pid) {
    if (!confirm(`Terminate process PID ${pid} on node ${ip}?`)) return;
    window.workbench.logTerminal("WARN", `Sending kill signal to PID ${pid} on node ${ip}...`);
    try {
      const res = await window.apiClient.killNodeProcess(ip, pid);
      window.workbench.logTerminal("SUCCESS", `Kill signal delivered to PID ${pid}: ${JSON.stringify(res)}`);
      alert(`Signal delivered to PID ${pid}`);
      this.openProcessesModal(ip, ip);
    } catch (e) {
      window.workbench.logTerminal("ERROR", `Failed to kill PID ${pid}: ${e.message}`);
      alert(`Kill error: ${e.message}`);
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
