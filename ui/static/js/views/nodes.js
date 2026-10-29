/**
 * Nodes & Invokers Management View (nodes.invokers)
 * Complete hardware telemetry, GPU sharing allocation, temporal/perpetual pause controls, and live process inspection
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
          <p>Configure resource caps (VRAM %, RAM, CPU), manage temporal/perpetual pause and drain states, inspect live GPU processes, and trigger maintenance</p>
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

      <!-- Filter & Batch Toolbar -->
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
            <button class="btn btn-secondary btn-sm" onclick="window.ViewNodes.batchPause(true, 'temporal', 4.0)" title="Temporarily pause all nodes for 4 hours">
              ⏸️ Pause 4h (All)
            </button>
            <button class="btn btn-secondary btn-sm" onclick="window.ViewNodes.batchPauseUntilPrompt()" title="Pausar todos los nodos hasta una hora fija (ej. 18:30)">
              ⏰ Pausa Hasta... (All)
            </button>
            <button class="btn btn-secondary btn-sm" onclick="window.ViewNodes.batchPause(true, 'perpetual')" title="Pause all nodes indefinitely">
              ⏹️ Pause Indef. (All)
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
                <th>State & Pause Mode</th>
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

      <!-- Pause Options Modal Overlay (Temporal vs Perpetual) -->
      <div id="pause-modal" style="display: none; position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; background: rgba(0,0,0,0.6); z-index: 6000; justify-content: center; align-items: center;">
        <div style="width: 480px; max-width: 90vw; background: var(--vscode-bg-sidebar); border: 1px solid var(--vscode-border-light); border-radius: 6px; padding: 20px; box-shadow: 0 8px 30px rgba(0,0,0,0.8);">
          <div style="font-size: 14px; font-weight: 600; color: var(--vscode-fg-bright); margin-bottom: 12px; display: flex; justify-content: space-between; align-items: center;">
            <span id="pause-modal-title">⏸️ Configurar Pausa del Nodo</span>
            <span style="cursor: pointer; color: var(--vscode-fg-muted); font-size: 16px;" onclick="document.getElementById('pause-modal').style.display='none'">✕</span>
          </div>
          <input type="hidden" id="pause-node-ip">

          <p style="font-size: 12px; color: var(--vscode-fg-muted); margin-bottom: 14px;">
            Al pausar el nodo, se desconecta de las colas públicas globales. Selecciona si la pausa es temporal o indefinida:
          </p>

          <div class="form-group">
            <label class="form-label" style="font-weight: 600;">Modo de Pausa:</label>
            <div style="display: flex; flex-direction: column; gap: 10px; margin-top: 6px;">
              <div id="card-pause-temporal" onclick="window.ViewNodes.selectPauseMode('temporal')" style="display: flex; align-items: flex-start; gap: 10px; cursor: pointer; padding: 12px; background: rgba(0, 122, 204, 0.15); border-radius: 6px; border: 2px solid #007ACC; transition: all 0.2s;">
                <input type="radio" id="radio-pause-temporal" name="pause-mode" value="temporal" checked style="margin-top: 3px; cursor: pointer;" onchange="window.ViewNodes.selectPauseMode('temporal')">
                <div style="flex: 1;">
                  <div style="font-weight: 600; color: var(--vscode-fg-bright);">⏱️ Pausa Temporal (Reanudación Automática)</div>
                  <div style="font-size: 11px; color: var(--vscode-fg-muted); margin-top: 2px;">
                    El nodo se reactiva automáticamente al vencer el temporizador configurable.
                  </div>
                </div>
              </div>

              <div id="card-pause-perpetual" onclick="window.ViewNodes.selectPauseMode('perpetual')" style="display: flex; align-items: flex-start; gap: 10px; cursor: pointer; padding: 12px; background: #252526; border-radius: 6px; border: 1px solid #3c3c3c; opacity: 0.8; transition: all 0.2s;">
                <input type="radio" id="radio-pause-perpetual" name="pause-mode" value="perpetual" style="margin-top: 3px; cursor: pointer;" onchange="window.ViewNodes.selectPauseMode('perpetual')">
                <div style="flex: 1;">
                  <div style="font-weight: 600; color: var(--vscode-fg-bright);">⏹️ Pausa Perpetua / Indefinida</div>
                  <div style="font-size: 11px; color: var(--vscode-fg-muted); margin-top: 2px;">
                    Permanece pausado indefinidamente hasta que un operador presione manualmente Reanudar.
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div class="form-group" id="pause-hours-container" style="margin-top: 14px;">
            <label class="form-label">Duración de la Pausa Temporal:</label>
            <div style="display: flex; gap: 6px; margin-bottom: 8px;">
              <button type="button" class="btn btn-secondary btn-sm" onclick="window.ViewNodes.setPauseHours(1)">1h</button>
              <button type="button" class="btn btn-secondary btn-sm" onclick="window.ViewNodes.setPauseHours(2)">2h</button>
              <button type="button" class="btn btn-secondary btn-sm" onclick="window.ViewNodes.setPauseHours(4)">4h</button>
              <button type="button" class="btn btn-secondary btn-sm" onclick="window.ViewNodes.setPauseHours(8)">8h</button>
              <button type="button" class="btn btn-secondary btn-sm" onclick="window.ViewNodes.setPauseHours(24)">24h</button>
            </div>
            <div style="display: flex; align-items: center; gap: 8px;">
              <input type="number" id="pause-hours-input" class="form-control" min="0.5" max="168" step="0.5" value="4.0" style="width: 100px;" oninput="window.ViewNodes.onHoursChange()">
              <span style="font-size: 12px; color: var(--vscode-fg-muted);">horas</span>
            </div>
            <div style="margin-top: 10px; padding-top: 10px; border-top: 1px dashed var(--vscode-border-light);">
              <label class="form-label" style="font-size: 12px;">O pausar hasta hora fija (HH:MM):</label>
              <div style="display: flex; align-items: center; gap: 8px;">
                <input type="text" id="pause-until-time-input" class="form-control" placeholder="18:30" style="width: 100px;">
                <span style="font-size: 11px; color: var(--vscode-fg-muted);">(ej. 18:30 — reanuda automáticamente a esa hora)</span>
              </div>
            </div>
          </div>

          <div style="display: flex; justify-content: flex-end; gap: 8px; margin-top: 18px;">
            <button class="btn btn-secondary btn-sm" onclick="document.getElementById('pause-modal').style.display='none'">Cancelar</button>
            <button id="pause-confirm-btn" class="btn btn-primary btn-sm" onclick="window.ViewNodes.confirmPause()">⏱️ Confirmar Pausa Temporal (4h)</button>
          </div>
        </div>
      </div>

      <!-- Resource Limits Modal Overlay -->
      <div id="limits-modal" style="display: none; position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; background: rgba(0,0,0,0.7); z-index: 6000; justify-content: center; align-items: center;">
        <div style="width: 520px; max-width: 92vw; background: var(--vscode-bg-sidebar); border: 1px solid var(--vscode-border-light); border-radius: 8px; padding: 22px; box-shadow: 0 12px 40px rgba(0,0,0,0.85);">
          <div style="font-size: 15px; font-weight: 600; color: var(--vscode-fg-bright); margin-bottom: 12px; display: flex; justify-content: space-between; align-items: center;">
            <span id="limits-modal-title">⚙️ Ajustar Límites de Cómputo</span>
            <span style="cursor: pointer; color: var(--vscode-fg-muted); font-size: 18px;" onclick="document.getElementById('limits-modal').style.display='none'">✕</span>
          </div>
          <input type="hidden" id="limits-node-ip">

          <!-- Hardware Physical Capacity Card -->
          <div id="limits-physical-card" style="background: rgba(255,255,255,0.03); border: 1px solid rgba(56, 189, 248, 0.25); border-radius: 6px; padding: 10px 14px; margin-bottom: 14px;">
            <div style="font-size: 12px; font-weight: 600; color: var(--vscode-fg-bright); margin-bottom: 6px; display: flex; justify-content: space-between; align-items: center;">
              <span>Capacidad Física Real del Nodo (Hardware + Swap)</span>
              <span id="limits-hostname-badge" class="badge badge-blue"></span>
            </div>
            <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 6px; font-size: 11px; color: var(--vscode-fg-muted);">
              <div>🖥️ CPU: <b id="limits-phys-cpu" style="color: #38BDF8;">-</b></div>
              <div>💾 RAM: <b id="limits-phys-ram" style="color: #38BDF8;">-</b></div>
              <div>🔄 SWAP: <b id="limits-phys-swap" style="color: #38BDF8;">-</b></div>
              <div>🎮 GPU: <b id="limits-phys-gpu" style="color: #38BDF8;">-</b></div>
            </div>
          </div>

          <!-- Quick Presets -->
          <div style="margin-bottom: 14px;">
            <div style="font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px; color: var(--vscode-fg-muted); margin-bottom: 6px; font-weight: 600;">Perfiles Rápidos Sugeridos:</div>
            <div style="display: flex; gap: 6px;">
              <button type="button" class="btn btn-secondary btn-sm" style="flex: 1; font-size: 11px; padding: 5px 4px;" onclick="window.ViewNodes.applyLimitPreset('safe')" title="Ideal si trabajas en este PC: deja CPU y RAM libres">🛡️ Protegido (PC)</button>
              <button type="button" class="btn btn-secondary btn-sm" style="flex: 1; font-size: 11px; padding: 5px 4px;" onclick="window.ViewNodes.applyLimitPreset('balanced')" title="50% de recursos asignados al entrenamiento">⚖️ Equilibrado (50%)</button>
              <button type="button" class="btn btn-secondary btn-sm" style="flex: 1; font-size: 11px; padding: 5px 4px;" onclick="window.ViewNodes.applyLimitPreset('max')" title="Máximo seguro reservando recursos mínimos para el SO">🚀 Máximo Seguro</button>
            </div>
          </div>

          <!-- VRAM Limit Slider -->
          <div class="form-group" style="margin-bottom: 12px;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
              <label class="form-label" style="margin-bottom: 0;">Límite VRAM GPU (Autobatch %):</label>
              <span id="limits-gpu-pct-val" style="font-weight: 600; color: #38BDF8;">30%</span>
            </div>
            <input type="range" id="limits-max-gpu" class="form-control" min="10" max="100" step="5" value="30" oninput="window.ViewNodes.updateLimitDisplays()">
            <div style="font-size: 11px; color: var(--vscode-fg-muted); margin-top: 2px;">Determina la fracción de VRAM para PyTorch y el cálculo de batch size.</div>
          </div>

          <!-- RAM Limit Slider -->
          <div class="form-group" style="margin-bottom: 12px;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
              <label class="form-label" style="margin-bottom: 0;">Límite de RAM para el Entrenamiento:</label>
              <span id="limits-ram-val" style="font-weight: 600; color: #38BDF8;">6 GB</span>
            </div>
            <input type="range" id="limits-max-ram-slider" class="form-control" min="2" max="32" step="1" value="6" oninput="window.ViewNodes.updateLimitDisplays()">
            <div style="display: flex; justify-content: space-between; font-size: 11px; color: var(--vscode-fg-muted); margin-top: 2px;">
              <span id="limits-ram-host-free">Reserva para el Escritorio: -</span>
              <span id="limits-ram-max-label">Tope físico: -</span>
            </div>
          </div>

          <!-- CPU Cores Slider -->
          <div class="form-group" style="margin-bottom: 12px;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
              <label class="form-label" style="margin-bottom: 0;">Cores de CPU Asignados:</label>
              <span id="limits-cpu-val" style="font-weight: 600; color: #38BDF8;">2.0 cores</span>
            </div>
            <input type="range" id="limits-max-cpu" class="form-control" min="1" max="16" step="0.5" value="2" oninput="window.ViewNodes.updateLimitDisplays()">
            <div style="display: flex; justify-content: space-between; font-size: 11px; color: var(--vscode-fg-muted); margin-top: 2px;">
              <span id="limits-cpu-host-free">Cores para el Escritorio: -</span>
              <span id="limits-cpu-max-label">Tope físico: -</span>
            </div>
          </div>

          <!-- SHM Limit Slider -->
          <div class="form-group" style="margin-bottom: 12px;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
              <label class="form-label" style="margin-bottom: 0;">Memoria Compartida (/dev/shm):</label>
              <span id="limits-shm-val" style="font-weight: 600; color: #38BDF8;">8.0 GiB</span>
            </div>
            <input type="range" id="limits-shm" class="form-control" min="2" max="64" step="2" value="8" oninput="window.ViewNodes.updateLimitDisplays()">
            <div style="display: flex; justify-content: space-between; font-size: 11px; color: var(--vscode-fg-muted); margin-top: 2px;">
              <span>Para workers de PyTorch DataLoader</span>
              <span id="limits-shm-max-label">Respaldado por RAM + Swap</span>
            </div>
          </div>

          <!-- Interactive Warning Banner -->
          <div id="limits-warning-box" style="display: none; background: rgba(239, 68, 68, 0.15); border: 1px solid rgba(239, 68, 68, 0.4); border-radius: 6px; padding: 8px 12px; margin-top: 10px; font-size: 11px; color: #FCA5A5;">
            ⚠️ <b>Riesgo de Cuelgue:</b> Has asignado casi la totalidad de CPU o RAM. Si estás usando este equipo interactivamente, el escritorio podría congelarse.
          </div>

          <div style="display: flex; justify-content: flex-end; gap: 8px; margin-top: 18px;">
            <button class="btn btn-secondary btn-sm" onclick="document.getElementById('limits-modal').style.display='none'">Cancelar</button>
            <button class="btn btn-primary btn-sm" onclick="window.ViewNodes.saveLimits()">💾 Guardar Límites en Redis</button>
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

      // Status & Pause Mode Badges
      const pauseState = node.pause_state || "active";
      const pauseUntil = node.pause_until || "";

      let statusBadge = `<span class="badge badge-green">🟢 Active</span>`;
      let pauseActionsHtml = `
        <button class="btn btn-secondary btn-sm" onclick="window.ViewNodes.openPauseModal('${ip}', '${escapeHtml(hostname)}')">
          ⏸️ Pausar...
        </button>
      `;

      if (pauseState === "draining") {
        statusBadge = `<span class="badge badge-amber" style="background: rgba(239, 68, 68, 0.2); color: #EF4444; border: 1px solid rgba(239, 68, 68, 0.4);">🛡️ Draining</span>`;
        pauseActionsHtml = `<button class="btn btn-sm" style="background: #10B981; color: white;" onclick="window.ViewNodes.toggleDrain('${ip}', false)">✅ Undrain</button>`;
      } else if (pauseState === "paused_temporal") {
        const remainingStr = formatRemainingTime(pauseUntil);
        const timePart = pauseUntil.includes("T") ? pauseUntil.split("T")[1].substring(0, 5) : pauseUntil;
        statusBadge = `<span class="badge badge-amber" title="Pausa Temporal hasta: ${pauseUntil}">⏱️ Pausa (${timePart || remainingStr})</span>`;
        pauseActionsHtml = `<button class="btn btn-sm" style="background: #10B981; color: white;" onclick="window.ViewNodes.resumeNode('${ip}')">▶️ Reanudar</button>`;
      } else if (pauseState === "paused_perpetual") {
        statusBadge = `<span class="badge badge-red" style="background: rgba(239, 68, 68, 0.2); color: #EF4444; border: 1px solid rgba(239, 68, 68, 0.4);" title="Pausado indefinidamente">⏹️ Pausa Indef.</span>`;
        pauseActionsHtml = `<button class="btn btn-sm" style="background: #10B981; color: white;" onclick="window.ViewNodes.resumeNode('${ip}')">▶️ Reanudar</button>`;
      } else if (pauseState.includes("pause")) {
        const remainingStr = formatRemainingTime(pauseUntil);
        const timePart = pauseUntil.includes("T") ? pauseUntil.split("T")[1].substring(0, 5) : pauseUntil;
        statusBadge = `<span class="badge badge-amber" title="Pausa Temporal hasta: ${pauseUntil}">⏱️ Pausa (${timePart || remainingStr})</span>`;
        pauseActionsHtml = `<button class="btn btn-sm" style="background: #10B981; color: white;" onclick="window.ViewNodes.resumeNode('${ip}')">▶️ Reanudar</button>`;
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
            <div><code style="font-size: 11px;">RAM: ${escapeHtml(maxRam)} | SHM: ${shmGb}G</code></div>
            <div style="font-size: 11px; color: var(--vscode-fg-muted);">Host: ${escapeHtml(ramTotalStr)} | ${maxCpu} Cores</div>
          </td>
          <td>
            <div style="display: flex; flex-wrap: wrap; gap: 4px;">
              ${pauseActionsHtml}
              ${drainBtn}
              <button class="btn btn-secondary btn-sm" onclick="window.ViewNodes.openLimitsModal('${ip}')">
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

  selectPauseMode(mode) {
    const radioTemporal = document.getElementById("radio-pause-temporal");
    const radioPerpetual = document.getElementById("radio-pause-perpetual");
    const cardTemporal = document.getElementById("card-pause-temporal");
    const cardPerpetual = document.getElementById("card-pause-perpetual");
    const hoursContainer = document.getElementById("pause-hours-container");
    const confirmBtn = document.getElementById("pause-confirm-btn");
    const hours = parseFloat(document.getElementById("pause-hours-input")?.value) || 4.0;

    if (mode === "perpetual") {
      if (radioPerpetual) radioPerpetual.checked = true;
      if (radioTemporal) radioTemporal.checked = false;
      if (cardPerpetual) {
        cardPerpetual.style.border = "2px solid #EF4444";
        cardPerpetual.style.background = "rgba(239, 68, 68, 0.15)";
        cardPerpetual.style.opacity = "1";
      }
      if (cardTemporal) {
        cardTemporal.style.border = "1px solid #3c3c3c";
        cardTemporal.style.background = "#252526";
        cardTemporal.style.opacity = "0.7";
      }
      if (hoursContainer) hoursContainer.style.display = "none";
      if (confirmBtn) {
        confirmBtn.className = "btn btn-danger btn-sm";
        confirmBtn.innerHTML = "⏹️ Confirmar Pausa Perpetua (Indefinida)";
      }
    } else {
      if (radioTemporal) radioTemporal.checked = true;
      if (radioPerpetual) radioPerpetual.checked = false;
      if (cardTemporal) {
        cardTemporal.style.border = "2px solid #007ACC";
        cardTemporal.style.background = "rgba(0, 122, 204, 0.15)";
        cardTemporal.style.opacity = "1";
      }
      if (cardPerpetual) {
        cardPerpetual.style.border = "1px solid #3c3c3c";
        cardPerpetual.style.background = "#252526";
        cardPerpetual.style.opacity = "0.7";
      }
      if (hoursContainer) hoursContainer.style.display = "block";
      if (confirmBtn) {
        confirmBtn.className = "btn btn-primary btn-sm";
        confirmBtn.innerHTML = `⏱️ Confirmar Pausa Temporal (${hours}h)`;
      }
    }
  },

  setPauseHours(hours) {
    const input = document.getElementById("pause-hours-input");
    if (input) input.value = hours;
    this.onHoursChange();
  },

  onHoursChange() {
    const radioPerpetual = document.getElementById("radio-pause-perpetual");
    if (!radioPerpetual || !radioPerpetual.checked) {
      const hours = parseFloat(document.getElementById("pause-hours-input")?.value) || 4.0;
      const confirmBtn = document.getElementById("pause-confirm-btn");
      if (confirmBtn) {
        confirmBtn.innerHTML = `⏱️ Confirmar Pausa Temporal (${hours}h)`;
      }
    }
  },

  openPauseModal(ip, hostname) {
    document.getElementById("pause-node-ip").value = ip;
    document.getElementById("pause-modal-title").textContent = `⏸️ Configurar Pausa: ${hostname} (${ip})`;
    const hoursInput = document.getElementById("pause-hours-input");
    if (hoursInput) hoursInput.value = "4.0";
    const untilInput = document.getElementById("pause-until-time-input");
    if (untilInput) untilInput.value = "";
    this.selectPauseMode("temporal");
    document.getElementById("pause-modal").style.display = "flex";
  },

  async confirmPause() {
    const ip = document.getElementById("pause-node-ip").value;
    const isPerpetual = document.getElementById("radio-pause-perpetual")?.checked;
    const mode = isPerpetual ? "perpetual" : "temporal";
    const hours = parseFloat(document.getElementById("pause-hours-input")?.value) || 4.0;
    const untilTimeVal = document.getElementById("pause-until-time-input")?.value?.trim() || null;

    if (mode === "temporal" && untilTimeVal) {
      if (!/^([01]?[0-9]|2[0-3]):[0-5][0-9]$/.test(untilTimeVal)) {
        alert("El formato de hora debe ser HH:MM (por ejemplo, 18:30)");
        return;
      }
    }

    const desc = mode === "perpetual" 
      ? "Perpetua (Indefinida)" 
      : (untilTimeVal ? `Temporal (hasta las ${untilTimeVal})` : `Temporal (${hours}h)`);
    window.workbench.logTerminal("WARN", `Aplicando pausa ${desc} al nodo ${ip}...`);

    try {
      await window.apiClient.pauseInvoker(ip, true, mode, hours, untilTimeVal);
      window.workbench.logTerminal("SUCCESS", `Pausa ${desc} configurada exitosamente en ${ip}.`);
      document.getElementById("pause-modal").style.display = "none";
      await this.load();
    } catch (e) {
      window.workbench.logTerminal("ERROR", `Error pausando ${ip}: ${e.message}`);
      alert(`Error al pausar: ${e.message}`);
    }
  },

  async resumeNode(ip) {
    window.workbench.logTerminal("INFO", `Reanudando nodo ${ip}...`);
    try {
      await window.apiClient.pauseInvoker(ip, false);
      window.workbench.logTerminal("SUCCESS", `Nodo ${ip} reanudado exitosamente.`);
      await this.load();
    } catch (e) {
      window.workbench.logTerminal("ERROR", `Error reanudando ${ip}: ${e.message}`);
      alert(`Error al reanudar: ${e.message}`);
    }
  },

  async toggleDrain(ip, shouldDrain) {
    const action = shouldDrain ? "DRAIN" : "UNDRAIN";
    const confirmMsg = shouldDrain
      ? `¿Estás seguro de que deseas DRENAR el nodo ${ip}?\nEsto cancelará las colas públicas, desalojará entrenamientos activos con SIGKILL y no aceptará más tareas.`
      : `¿Reanudar el nodo ${ip} y quitar drenado?`;

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

  async batchPause(shouldPause, mode = "temporal", hours = 4.0) {
    const actionStr = shouldPause
      ? (mode === "temporal" ? `PAUSA TEMPORAL (${hours}h)` : "PAUSA PERPETUA")
      : "REANUDAR";

    if (!confirm(`¿Estás seguro de que deseas ejecutar ${actionStr} en todos los nodos invoker?`)) return;

    window.workbench.logTerminal("WARN", `Ejecutando ${actionStr} en lote...`);
    try {
      for (const node of this.invokersData) {
        const ip = node.worker_ip || node.ip;
        if (ip) {
          await window.apiClient.pauseInvoker(ip, shouldPause, mode, hours);
        }
      }
      window.workbench.logTerminal("SUCCESS", `Completado ${actionStr} en todos los nodos.`);
      await this.load();
    } catch (e) {
      window.workbench.logTerminal("ERROR", `Error en pausa por lote: ${e.message}`);
      alert(`Error en pausa por lote: ${e.message}`);
    }
  },

  async batchPauseUntilPrompt() {
    const defaultTime = "18:30";
    const untilTime = prompt("Introduce la hora de reanudación automática (HH:MM):", defaultTime);
    if (!untilTime) return;
    const trimmed = untilTime.trim();
    if (!/^([01]?[0-9]|2[0-3]):[0-5][0-9]$/.test(trimmed)) {
      alert("El formato debe ser HH:MM (por ejemplo, 18:30)");
      return;
    }
    if (!confirm(`¿Confirmas pausar TODOS los nodos invoker hasta las ${trimmed}?`)) return;

    window.workbench.logTerminal("WARN", `Pausando todos los nodos hasta las ${trimmed}...`);
    try {
      for (const node of this.invokersData) {
        const ip = node.worker_ip || node.ip;
        if (ip) {
          await window.apiClient.pauseInvoker(ip, true, "temporal", 4.0, trimmed);
        }
      }
      window.workbench.logTerminal("SUCCESS", `Completada pausa hasta las ${trimmed} en todos los nodos.`);
      await this.load();
    } catch (e) {
      window.workbench.logTerminal("ERROR", `Error en pausa por lote hasta hora: ${e.message}`);
      alert(`Error en pausa por lote: ${e.message}`);
    }
  },

  openLimitsModal(ip) {
    const node = (this.invokersData || []).find(n => (n.worker_ip || n.ip) === ip) || {};
    const physical = node.physical || {};
    const limits = node.limits || {};
    const hostname = node.hostname || ip;

    // Physical limits detection
    const physCores = parseInt(physical.cpu_cores) || 8;
    let physRamGb = 16;
    if (physical.ram_total) {
      const m = String(physical.ram_total).match(/(\d+)/);
      if (m) physRamGb = parseInt(m[1]);
    }
    let physSwapGb = 32;
    if (physical.swap_total) {
      const sm = String(physical.swap_total).match(/(\d+)/);
      if (sm) physSwapGb = parseInt(sm[1]);
    }
    const gpuModel = physical.gpu_model || "NVIDIA GPU";
    const gpuVram = physical.gpu_memory_total || "N/A";

    this.currentEditingNode = {
      ip,
      hostname,
      physCores,
      physRamGb,
      physSwapGb,
      gpuModel,
      gpuVram,
    };

    document.getElementById("limits-node-ip").value = ip;
    document.getElementById("limits-modal-title").textContent = `⚙️ Ajustar Límites: ${hostname} (${ip})`;
    document.getElementById("limits-hostname-badge").textContent = hostname;
    document.getElementById("limits-phys-cpu").textContent = `${physCores} Cores`;
    document.getElementById("limits-phys-ram").textContent = `${physRamGb} GB`;
    document.getElementById("limits-phys-swap").textContent = `${physSwapGb} GB`;
    document.getElementById("limits-phys-gpu").textContent = `${gpuModel.replace("NVIDIA GeForce ", "")} (${gpuVram.split(" ")[0]} MiB)`;

    // Configure CPU slider boundaries based strictly on physical hardware
    const cpuSlider = document.getElementById("limits-max-cpu");
    cpuSlider.min = 1;
    cpuSlider.max = physCores;
    cpuSlider.step = physCores <= 8 ? 0.5 : 1;
    const currentCpu = limits.max_cpu_cores !== undefined ? parseFloat(limits.max_cpu_cores) : Math.min(2, physCores);
    cpuSlider.value = Math.min(currentCpu, physCores);
    document.getElementById("limits-cpu-max-label").textContent = `Tope físico: ${physCores} cores`;

    // Configure RAM slider boundaries based strictly on physical hardware
    const ramSlider = document.getElementById("limits-max-ram-slider");
    ramSlider.min = 2;
    ramSlider.max = physRamGb;
    ramSlider.step = 1;
    let currentRam = 6;
    if (limits.max_ram) {
      const rm = String(limits.max_ram).match(/(\d+)/);
      if (rm) currentRam = parseInt(rm[1]);
    }
    ramSlider.value = Math.min(currentRam, physRamGb);
    document.getElementById("limits-ram-max-label").textContent = `Tope físico: ${physRamGb} GB`;

    // Configure GPU slider
    const currentGpu = limits.max_gpu_percent !== undefined ? parseFloat(limits.max_gpu_percent) : 30;
    document.getElementById("limits-max-gpu").value = Math.max(10, Math.min(100, currentGpu));

    // Configure SHM slider (backed by RAM + Swap, up to 64 GB)
    const shmSlider = document.getElementById("limits-shm");
    shmSlider.min = 2;
    const maxSafeShm = Math.min(64, Math.max(32, physRamGb + physSwapGb));
    shmSlider.max = maxSafeShm;
    shmSlider.step = 2;
    const currentShm = limits.shm_size_gb !== undefined ? parseFloat(limits.shm_size_gb) : 8;
    shmSlider.value = Math.min(currentShm, maxSafeShm);
    document.getElementById("limits-shm-max-label").textContent = `RAM+Swap: ${physRamGb + physSwapGb} GB`;

    this.updateLimitDisplays();
    document.getElementById("limits-modal").style.display = "flex";
  },

  updateLimitDisplays() {
    if (!this.currentEditingNode) return;
    const { physCores, physRamGb } = this.currentEditingNode;

    const gpuVal = document.getElementById("limits-max-gpu").value;
    const ramVal = parseInt(document.getElementById("limits-max-ram-slider").value);
    const cpuVal = parseFloat(document.getElementById("limits-max-cpu").value);
    const shmVal = parseFloat(document.getElementById("limits-shm").value);

    document.getElementById("limits-gpu-pct-val").textContent = `${gpuVal}%`;
    document.getElementById("limits-ram-val").textContent = `${ramVal} GB`;
    document.getElementById("limits-cpu-val").textContent = `${cpuVal} cores`;
    document.getElementById("limits-shm-val").textContent = `${shmVal} GiB`;

    // Remaining host calculation
    const freeCores = Math.max(0, physCores - cpuVal);
    const freeRam = Math.max(0, physRamGb - ramVal);

    const cpuHostFreeEl = document.getElementById("limits-cpu-host-free");
    cpuHostFreeEl.textContent = `Libre para SO: ${freeCores} cores`;
    cpuHostFreeEl.style.color = freeCores < 2 ? "#EF4444" : "#10B981";

    const ramHostFreeEl = document.getElementById("limits-ram-host-free");
    ramHostFreeEl.textContent = `Libre para SO: ${freeRam} GB`;
    ramHostFreeEl.style.color = freeRam < 4 ? "#EF4444" : "#10B981";

    // Warning trigger
    const warningBox = document.getElementById("limits-warning-box");
    if (freeCores < 1.5 || freeRam < 3) {
      warningBox.style.display = "block";
    } else {
      warningBox.style.display = "none";
    }
  },

  applyLimitPreset(type) {
    if (!this.currentEditingNode) return;
    const { physCores, physRamGb } = this.currentEditingNode;

    if (type === "safe") {
      // Safe Workstation profile: Keep computer fluid for desktop dev
      document.getElementById("limits-max-gpu").value = 30;
      document.getElementById("limits-max-cpu").value = Math.min(2, Math.max(1, physCores - 4));
      document.getElementById("limits-max-ram-slider").value = Math.min(6, Math.max(4, Math.floor(physRamGb * 0.4)));
      document.getElementById("limits-shm").value = Math.min(8, Math.max(2, Math.floor(physRamGb * 0.25)));
    } else if (type === "balanced") {
      // 50% Balanced profile
      document.getElementById("limits-max-gpu").value = 50;
      document.getElementById("limits-max-cpu").value = Math.max(1, Math.floor(physCores * 0.5));
      document.getElementById("limits-max-ram-slider").value = Math.max(4, Math.floor(physRamGb * 0.5));
      document.getElementById("limits-shm").value = Math.min(16, Math.max(4, Math.floor(physRamGb * 0.25)));
    } else if (type === "max") {
      // Safe Maximum (Night / Dedicated mode): Reserve 2 cores & 4GB for host
      document.getElementById("limits-max-gpu").value = 90;
      document.getElementById("limits-max-cpu").value = Math.max(1, physCores - 2);
      document.getElementById("limits-max-ram-slider").value = Math.max(4, physRamGb - 4);
      document.getElementById("limits-shm").value = Math.min(32, Math.max(4, Math.floor(physRamGb * 0.4)));
    }
    this.updateLimitDisplays();
  },

  async saveLimits() {
    const ip = document.getElementById("limits-node-ip").value;
    const maxGpuPct = parseFloat(document.getElementById("limits-max-gpu").value);
    const maxRamGb = parseInt(document.getElementById("limits-max-ram-slider").value);
    const maxCpu = parseFloat(document.getElementById("limits-max-cpu").value);
    const shmGb = parseFloat(document.getElementById("limits-shm").value);

    if (this.currentEditingNode) {
      const { physCores, physRamGb } = this.currentEditingNode;
      if (maxCpu > physCores) {
        alert(`Error: No puedes asignar ${maxCpu} cores porque el equipo solo cuenta con ${physCores} cores físicos.`);
        return;
      }
      if (maxRamGb > physRamGb) {
        alert(`Error: No puedes asignar ${maxRamGb} GB de RAM porque el equipo solo tiene ${physRamGb} GB físicos.`);
        return;
      }
    }

    const maxRamStr = `${maxRamGb}g`;

    try {
      window.workbench.logTerminal("INFO", `Guardando límites de recursos para ${ip}: GPU=${maxGpuPct}%, RAM=${maxRamStr}, CPU=${maxCpu} Cores, SHM=${shmGb}GiB...`);
      await window.apiClient.updateInvokerLimits(ip, {
        max_gpu_percent: maxGpuPct,
        max_ram: maxRamStr,
        max_cpu_cores: maxCpu,
        shm_size_gb: shmGb,
      });
      window.workbench.logTerminal("SUCCESS", `Límites guardados en Redis para ${ip}.`);
      document.getElementById("limits-modal").style.display = "none";
      await this.load();
    } catch (e) {
      window.workbench.logTerminal("ERROR", `Fallo al guardar límites para ${ip}: ${e.message}`);
      alert(`Error al guardar límites: ${e.message}`);
    }
  },

  async openProcessesModal(ip, hostname) {
    const modal = document.getElementById("processes-modal");
    const title = document.getElementById("processes-modal-title");
    const summary = document.getElementById("processes-modal-summary");
    const tbody = document.getElementById("processes-tbody");

    title.textContent = `🔍 Live GPU Compute Processes & Zombie Monitor: ${hostname} (${ip})`;
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
