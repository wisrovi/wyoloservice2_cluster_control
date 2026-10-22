/**
 * Operations Center View (overview.cluster)
 */

window.ViewOverview = {
  id: "overview",
  label: "Operations Center",
  icon: "📊",
  file: "overview.cluster",
  category: "cluster",
  queuedData: [],
  queuedPage: 1,
  queuedPageSize: 5,

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
        <div class="metric-card">
          <div class="metric-label">Queued Backlog</div>
          <div class="metric-value" id="metric-queued" style="color: #F59E0B;">--</div>
          <div class="metric-sub" id="metric-queued-sub">Pending in Celery</div>
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

      <!-- Queued Workloads & Backlog Table -->
      <div class="card-section" style="margin-bottom: 20px;">
        <div class="card-title">
          <div style="display: flex; align-items: center; gap: 8px;">
            <span>⏳ Queued Workloads & Celery Backlog (En Espera)</span>
            <span class="badge badge-amber" id="queued-workloads-badge">0 Queued</span>
          </div>
          <div style="display: flex; align-items: center; gap: 8px;">
            <button class="btn btn-secondary btn-sm" onclick="window.ViewOverview.refreshQueues()" title="Refrescar tareas en cola">
              <span>🔄</span> Refrescar
            </button>
            <button class="btn btn-secondary btn-sm" onclick="window.workbench.switchView('tasks')">
              <span>📋</span> Open Tasks & Queues
            </button>
          </div>
        </div>

        <!-- Filter Bar -->
        <div style="display: flex; flex-wrap: wrap; gap: 8px; align-items: center; margin-bottom: 12px; background: rgba(0,0,0,0.15); padding: 8px 12px; border-radius: 4px; border: 1px solid var(--vscode-border-light);">
          <div style="flex: 1; min-width: 180px;">
            <input type="text" id="overview-queued-search" class="form-control form-control-sm" placeholder="🔍 Filtrar por estudio, tarea, autor, dataset..." oninput="window.ViewOverview.onQueuedFilterChange()" style="width: 100%;">
          </div>

          <select id="overview-queued-filter-queue" class="form-control form-control-sm" style="width: 160px;" onchange="window.ViewOverview.onQueuedFilterChange()">
            <option value="All">Todas las Colas / Nodos</option>
          </select>

          <select id="overview-queued-filter-priority" class="form-control form-control-sm" style="width: 130px;" onchange="window.ViewOverview.onQueuedFilterChange()">
            <option value="All">Todas Prioridades</option>
            <option value="NORMAL">NORMAL</option>
            <option value="HIGH">HIGH</option>
          </select>

          <select id="overview-queued-filter-model" class="form-control form-control-sm" style="width: 130px;" onchange="window.ViewOverview.onQueuedFilterChange()">
            <option value="All">Todos los Modelos</option>
          </select>

          <select id="overview-queued-page-size" class="form-control form-control-sm" style="width: 95px;" onchange="window.ViewOverview.onQueuedPageSizeChange()">
            <option value="5" selected>5 por pág</option>
            <option value="10">10 por pág</option>
            <option value="25">25 por pág</option>
            <option value="50">50 por pág</option>
          </select>

          <button class="btn btn-secondary btn-sm" onclick="window.ViewOverview.clearQueuedFilters()" title="Limpiar filtros">
            ✕ Limpiar
          </button>
        </div>

        <div class="table-responsive">
          <table class="vscode-table">
            <thead>
              <tr>
                <th>Study / Project Name</th>
                <th>Author</th>
                <th>Target Queue / Node</th>
                <th>Model</th>
                <th>Dataset Path</th>
                <th>Priority</th>
                <th>Queued At</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody id="overview-queued-tasks-body">
              <tr><td colspan="8" style="text-align: center; color: var(--vscode-fg-muted); padding: 16px;">Scanning queued workloads...</td></tr>
            </tbody>
          </table>
        </div>

        <!-- Pagination Bar -->
        <div id="overview-queued-pagination" style="display: flex; justify-content: space-between; align-items: center; margin-top: 10px; font-size: 12px; color: var(--vscode-fg-muted); padding: 4px 6px;">
          <div id="overview-queued-page-info">Mostrando 0 de 0</div>
          <div style="display: flex; gap: 6px; align-items: center;">
            <button class="btn btn-secondary btn-sm" id="overview-queued-btn-prev" onclick="window.ViewOverview.changeQueuedPage(-1)">◀ Anterior</button>
            <span id="overview-queued-page-number" style="font-weight: 600; color: var(--vscode-fg-bright); padding: 0 4px;">Pág. 1 / 1</span>
            <button class="btn btn-secondary btn-sm" id="overview-queued-btn-next" onclick="window.ViewOverview.changeQueuedPage(1)">Siguiente ▶</button>
          </div>
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

      // 2. Render Queued Workloads & Backlog
      let totalQueuedCount = 0;
      try {
        const qRes = await window.apiClient.getQueues();
        this.queuedData = qRes.tasks || [];
        totalQueuedCount = qRes.total_queued !== undefined ? qRes.total_queued : this.queuedData.length;
      } catch (_) {}

      const metricQueued = document.getElementById("metric-queued");
      const metricQueuedSub = document.getElementById("metric-queued-sub");
      if (metricQueued) metricQueued.textContent = totalQueuedCount;
      if (metricQueuedSub) metricQueuedSub.textContent = `${this.queuedData.length} Visible Tasks`;

      this.populateQueuedDropdowns(this.queuedData);
      this.renderQueuedTable();

      // 3. Render Nodes Topology
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
        } else if (pauseState === "paused_perpetual") {
          stateBadge = `<span class="badge badge-red" style="background: rgba(239, 68, 68, 0.2); color: #EF4444; border: 1px solid rgba(239, 68, 68, 0.4);" title="Pausa indefinida">⏹️ Pausa Indef.</span>`;
        } else if (pauseState.includes("pause")) {
          const remainingStr = typeof formatRemainingTime === "function" ? formatRemainingTime(node.pause_until) : "";
          stateBadge = `<span class="badge badge-amber" title="Pausa temporal hasta: ${node.pause_until || ''}">⏱️ Pausa Temp ${remainingStr ? '(' + remainingStr + ')' : ''}</span>`;
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

  populateQueuedDropdowns(tasks) {
    const queueSel = document.getElementById("overview-queued-filter-queue");
    const modelSel = document.getElementById("overview-queued-filter-model");

    if (queueSel) {
      const curr = queueSel.value || "All";
      const queues = Array.from(new Set(tasks.map(t => t.queue_name || "wyolo_gpu_queue"))).filter(Boolean).sort();
      queueSel.innerHTML = `<option value="All">Todas las Colas / Nodos</option>` +
        queues.map(q => `<option value="${escapeHtml(q)}">${escapeHtml(q)}</option>`).join("");
      queueSel.value = queues.includes(curr) ? curr : "All";
    }

    if (modelSel) {
      const curr = modelSel.value || "All";
      const models = Array.from(new Set(tasks.map(t => t.model || "yolo"))).filter(Boolean).sort();
      modelSel.innerHTML = `<option value="All">Todos los Modelos</option>` +
        models.map(m => `<option value="${escapeHtml(m)}">${escapeHtml(m)}</option>`).join("");
      modelSel.value = models.includes(curr) ? curr : "All";
    }
  },

  onQueuedFilterChange() {
    this.queuedPage = 1;
    this.renderQueuedTable();
  },

  onQueuedPageSizeChange() {
    const sel = document.getElementById("overview-queued-page-size");
    this.queuedPageSize = parseInt(sel?.value || "5", 10);
    this.queuedPage = 1;
    this.renderQueuedTable();
  },

  clearQueuedFilters() {
    const searchInput = document.getElementById("overview-queued-search");
    const queueSel = document.getElementById("overview-queued-filter-queue");
    const prioSel = document.getElementById("overview-queued-filter-priority");
    const modelSel = document.getElementById("overview-queued-filter-model");

    if (searchInput) searchInput.value = "";
    if (queueSel) queueSel.value = "All";
    if (prioSel) prioSel.value = "All";
    if (modelSel) modelSel.value = "All";

    this.queuedPage = 1;
    this.renderQueuedTable();
  },

  changeQueuedPage(delta) {
    this.queuedPage += delta;
    this.renderQueuedTable();
  },

  renderQueuedTable() {
    const tbody = document.getElementById("overview-queued-tasks-body");
    const pageInfo = document.getElementById("overview-queued-page-info");
    const pageNumber = document.getElementById("overview-queued-page-number");
    const btnPrev = document.getElementById("overview-queued-btn-prev");
    const btnNext = document.getElementById("overview-queued-btn-next");
    const badge = document.getElementById("queued-workloads-badge");

    if (!tbody) return;

    const q = (document.getElementById("overview-queued-search")?.value || "").toLowerCase().trim();
    const queueFilter = document.getElementById("overview-queued-filter-queue")?.value || "All";
    const prioFilter = document.getElementById("overview-queued-filter-priority")?.value || "All";
    const modelFilter = document.getElementById("overview-queued-filter-model")?.value || "All";

    const filtered = (this.queuedData || []).filter(t => {
      if (queueFilter !== "All" && (t.queue_name || "wyolo_gpu_queue") !== queueFilter) return false;
      if (prioFilter !== "All" && ((t.priority || "NORMAL").toUpperCase()) !== prioFilter) return false;
      if (modelFilter !== "All" && (t.model || "yolo") !== modelFilter) return false;
      if (q) {
        const text = [
          t.study_name || "",
          t.task_id || "",
          t.author || "",
          t.model || "",
          t.dataset || "",
          t.queue_name || ""
        ].join(" ").toLowerCase();
        if (!text.includes(q)) return false;
      }
      return true;
    });

    const totalCount = (this.queuedData || []).length;
    const filteredCount = filtered.length;

    if (badge) {
      badge.textContent = `${totalCount} Queued` + (filteredCount !== totalCount ? ` (${filteredCount} filtrados)` : "");
    }

    if (!filteredCount) {
      tbody.innerHTML = `<tr><td colspan="8" style="text-align: center; color: var(--vscode-fg-muted); padding: 16px;">
        ${totalCount === 0 ? "No hay cargas de trabajo esperando en colas actualmente." : "No hay tareas en cola que coincidan con los filtros aplicados."}
      </td></tr>`;
      if (pageInfo) pageInfo.textContent = `Mostrando 0 de ${totalCount} tareas`;
      if (pageNumber) pageNumber.textContent = "Pág. 1 / 1";
      if (btnPrev) btnPrev.disabled = true;
      if (btnNext) btnNext.disabled = true;
      return;
    }

    const totalPages = Math.ceil(filteredCount / this.queuedPageSize) || 1;
    if (this.queuedPage > totalPages) this.queuedPage = totalPages;
    if (this.queuedPage < 1) this.queuedPage = 1;

    const startIdx = (this.queuedPage - 1) * this.queuedPageSize;
    const endIdx = Math.min(startIdx + this.queuedPageSize, filteredCount);
    const pagedTasks = filtered.slice(startIdx, endIdx);

    if (pageInfo) {
      pageInfo.textContent = `Mostrando ${startIdx + 1}–${endIdx} de ${filteredCount} tareas` +
        (filteredCount !== totalCount ? ` (filtradas de ${totalCount} en total)` : "");
    }
    if (pageNumber) pageNumber.textContent = `Pág. ${this.queuedPage} / ${totalPages}`;
    if (btnPrev) btnPrev.disabled = (this.queuedPage <= 1);
    if (btnNext) btnNext.disabled = (this.queuedPage >= totalPages);

    tbody.innerHTML = pagedTasks.map(t => {
      const studyName = t.study_name || t.task_id || "Queued Job";
      const author = t.author || "Unknown";
      const qName = t.queue_name || "wyolo_gpu_queue";
      const isNodeQueue = qName.includes(".") || qName.startsWith("192.") || qName.startsWith("worker");
      const qBadge = isNodeQueue
        ? `<span class="badge badge-green" title="Direct Node Queue">${escapeHtml(qName)}</span>`
        : `<span class="badge badge-blue" title="Public Celery Queue">${escapeHtml(qName)}</span>`;
      const model = t.model || "yolo";
      const dataset = t.dataset || "N/A";
      const prio = (t.priority || "NORMAL").toUpperCase();
      const prioBadge = prio === "HIGH"
        ? `<span class="badge badge-amber">${prio}</span>`
        : `<span class="badge badge-blue">${prio}</span>`;
      const queuedAt = t.queued_at || "Recently";

      return `
        <tr>
          <td>
            <div><strong>${escapeHtml(studyName)}</strong></div>
            <div style="font-size: 10px; color: var(--vscode-fg-muted); font-family: var(--vscode-mono-family);">${escapeHtml(t.task_id || '')}</div>
          </td>
          <td><span style="color: var(--vscode-fg-muted); font-size: 12px;">${escapeHtml(author)}</span></td>
          <td>${qBadge}</td>
          <td><span class="badge badge-blue">${escapeHtml(model)}</span></td>
          <td style="max-width: 220px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;" title="${escapeHtml(dataset)}">
            <code>${escapeHtml(dataset)}</code>
          </td>
          <td>${prioBadge}</td>
          <td><span style="font-size: 11px; color: var(--vscode-fg-muted);">${escapeHtml(queuedAt)}</span></td>
          <td>
            <button class="btn btn-danger btn-sm" onclick="window.ViewOverview.cancelQueuedTask('${t.task_id}')" title="Cancelar y eliminar de cola">
              🗑️ Cancel
            </button>
          </td>
        </tr>
      `;
    }).join("");
  },

  async refreshQueues() {
    try {
      const qRes = await window.apiClient.getQueues();
      this.queuedData = qRes.tasks || [];
      const totalQueuedCount = qRes.total_queued !== undefined ? qRes.total_queued : this.queuedData.length;
      const metricQueued = document.getElementById("metric-queued");
      const metricQueuedSub = document.getElementById("metric-queued-sub");
      if (metricQueued) metricQueued.textContent = totalQueuedCount;
      if (metricQueuedSub) metricQueuedSub.textContent = `${this.queuedData.length} Visible Tasks`;
      this.populateQueuedDropdowns(this.queuedData);
      this.renderQueuedTable();
    } catch (e) {
      window.workbench?.logTerminal("WARN", `Error actualizando colas: ${e.message}`);
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
  },

  async cancelQueuedTask(taskId) {
    if (!confirm(`Cancel and remove queued task '${taskId}' from queue?`)) return;
    window.workbench.logTerminal("WARN", `Removing queued task ${taskId}...`);
    try {
      await window.apiClient.deleteQueuedTask(taskId);
      window.workbench.logTerminal("SUCCESS", `Queued task ${taskId} removed successfully.`);
      await this.load();
    } catch (e) {
      window.workbench.logTerminal("ERROR", `Failed to remove queued task: ${e.message}`);
      alert(`Remove failed: ${e.message}`);
    }
  }
};

function formatRemainingTime(pauseUntil) {
  if (!pauseUntil) return "Temp";
  const num = parseFloat(pauseUntil);
  if (!isNaN(num) && num > 1000000000) {
    const diffSec = num - (Date.now() / 1000);
    if (diffSec <= 0) return "Expirando";
    const hours = Math.floor(diffSec / 3600);
    const mins = Math.floor((diffSec % 3600) / 60);
    if (hours > 0) return `${hours}h ${mins}m`;
    return `${mins}m`;
  }
  return String(pauseUntil);
}
