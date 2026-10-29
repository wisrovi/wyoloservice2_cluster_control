/**
 * NeuralForge Cluster Admin v3.1.8 — VSCode Workbench Core Application
 * Full-width, zero-latency desktop workbench replica
 */

class VSCodeWorkbench {
  constructor() {
    this.views = {
      overview: window.ViewOverview,
      nodes: window.ViewNodes,
      storage: window.ViewStorage,
      dispatch: window.ViewDispatch,
      tasks: window.ViewTasks,
      history: window.ViewHistory,
      benchmarks: window.ViewBenchmarks,
      finops: window.ViewFinops,
      capabilities: window.ViewCapabilities,
      audit: window.ViewAudit,
      settings: window.ViewSettings,
    };

    this.openTabs = [
      "overview",
      "nodes",
      "dispatch",
      "tasks",
      "storage",
      "capabilities",
      "benchmarks",
      "finops",
      "audit",
      "history",
      "settings",
    ];
    this.activeViewId = "overview";
    this.activeMenu = null;
    this.panelCollapsed = true;
    this.pollInterval = null;
    this.cachedInvokers = [];
    this.cachedActiveTasks = [];
    this.cachedQueuedTasks = [];

    this.init();
  }

  init() {
    this.bindEvents();
    this.renderTabs();
    this.renderViewContainer();

    // Check Auth
    if (!window.apiClient.isAuthenticated()) {
      this.showAuthOverlay();
    } else {
      this.hideAuthOverlay();
      this.switchView(this.activeViewId);
      this.startBackgroundTelemetry();
    }

    this.logTerminal("SUCCESS", "NeuralForge Cluster Admin v3.1.8 Workbench initialized.");
    this.logTerminal("INFO", `Connected to API: ${window.apiClient.baseUrl}`);
  }

  // --- Keyboard Shortcuts & Global Events ---
  bindEvents() {
    // Keyboard shortcuts
    window.addEventListener("keydown", (e) => {
      // Ctrl+P or Cmd+P: Command Palette
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "p") {
        e.preventDefault();
        this.toggleCommandPalette();
      }
      // Ctrl+J: Toggle Bottom Panel
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "j") {
        e.preventDefault();
        this.toggleBottomPanel();
      }
      // Esc: Close any menu or modal
      if (e.key === "Escape") {
        this.closeAllMenus();
        this.closeCommandPalette();
        const limitsModal = document.getElementById("limits-modal");
        if (limitsModal) limitsModal.style.display = "none";
      }
      // Alt+F: Archivo menu
      if (e.altKey && e.key.toLowerCase() === "f") {
        e.preventDefault();
        this.toggleMenu("menu-file");
      }
      // Alt+V: Ver menu
      if (e.altKey && e.key.toLowerCase() === "v") {
        e.preventDefault();
        this.toggleMenu("menu-view");
      }
    });

    // Close menus on outside click
    window.addEventListener("click", (e) => {
      if (!e.target.closest(".menubar-menu-button") && !e.target.closest(".dropdown-menu")) {
        this.closeAllMenus();
      }
    });

    // Command palette filter
    const paletteInput = document.getElementById("palette-search");
    if (paletteInput) {
      paletteInput.addEventListener("input", (e) => {
        this.filterCommandPalette(e.target.value);
      });
      paletteInput.addEventListener("keydown", (e) => {
        this.handlePaletteNav(e);
      });
    }
  }

  // --- Auth & Session ---
  showAuthOverlay(errorMsg = null) {
    const overlay = document.getElementById("auth-overlay");
    const errBox = document.getElementById("auth-error-box");
    if (errorMsg) {
      errBox.textContent = errorMsg;
      errBox.classList.add("show");
    } else {
      errBox.classList.remove("show");
    }
    overlay.classList.add("show");
    document.getElementById("auth-username").focus();
  }

  hideAuthOverlay() {
    document.getElementById("auth-overlay").classList.remove("show");
  }

  async handleLogin(username, password) {
    const errBox = document.getElementById("auth-error-box");
    errBox.classList.remove("show");
    try {
      this.logTerminal("INFO", `Authenticating operator: ${username}...`);
      await window.apiClient.login(username, password);
      this.hideAuthOverlay();
      this.logTerminal("SUCCESS", `Authentication successful. Session granted.`);
      this.switchView(this.activeViewId);
      this.startBackgroundTelemetry();
    } catch (e) {
      errBox.textContent = `Login failed: ${e.message || 'Invalid credentials'}`;
      errBox.classList.add("show");
      this.logTerminal("ERROR", `Login failed for ${username}: ${e.message}`);
    }
  }

  logout() {
    window.apiClient.clearToken();
    this.logTerminal("WARN", "Operator logged out. Session cleared.");
    this.showAuthOverlay("Logged out successfully.");
  }

  // --- Menubar & Dropdowns ---
  toggleMenu(menuId) {
    const menuEl = document.getElementById(menuId);
    const btnEl = document.querySelector(`[data-menu="${menuId}"]`);
    const isShowing = menuEl.classList.contains("show");

    this.closeAllMenus();

    if (!isShowing) {
      menuEl.classList.add("show");
      if (btnEl) btnEl.classList.add("active");
      this.activeMenu = menuId;
    }
  }

  handleMenuHover(menuId) {
    if (this.activeMenu && this.activeMenu !== menuId) {
      this.toggleMenu(menuId);
    }
  }

  closeAllMenus() {
    document.querySelectorAll(".dropdown-menu").forEach(m => m.classList.remove("show"));
    document.querySelectorAll(".menubar-menu-button").forEach(b => b.classList.remove("active"));
    this.activeMenu = null;
  }

  // --- Tab Management ---
  renderTabs() {
    const container = document.getElementById("tabs-container");
    if (!container) return;

    const activeCount = this.cachedActiveTasks?.length || 0;
    const queuedCount = this.cachedQueuedTasks?.length || 0;
    const totalJobs = activeCount + queuedCount;

    const totalNodes = this.cachedInvokers?.length || 0;
    const onlineNodes = this.cachedInvokers?.filter(n => n.state === 'active').length || 0;

    const sections = [
      {
        title: "Centro de Control",
        views: [
          { id: "overview", label: "Operations Hub", icon: "📊", hint: "KPIs, Topología y Estado en vivo" },
        ],
      },
      {
        title: "Entrenamientos & Trabajos",
        views: [
          { id: "dispatch", label: "Lanzar Entrenamiento", icon: "🚀", hint: "Smart Launcher (YOLO, Datasets, Horarios)" },
          { id: "tasks", label: "Gestión de Trabajos", icon: "📋", hint: "Activos, Cola & Historial", badge: totalJobs > 0 ? `${activeCount} activos` : null, badgeClass: activeCount > 0 ? "badge-blue" : "badge-amber" },
        ],
      },
      {
        title: "Infraestructura Física",
        views: [
          { id: "nodes", label: "Nodos & GPUs", icon: "⚙️", hint: "Límites VRAM/RAM/CPU, Pausas & NVML", badge: totalNodes > 0 ? `${onlineNodes}/${totalNodes}` : null, badgeClass: "badge-green" },
          { id: "storage", label: "Almacenamiento & Datasets", icon: "💾", hint: "Montajes Samba CIFS & MinIO S3" },
        ],
      },
      {
        title: "Inteligencia & Rendimiento",
        views: [
          { id: "benchmarks", label: "GPU Benchmarks", icon: "🏆", hint: "Throughput Leaderboard (img/s)" },
          { id: "finops", label: "FinOps & Energía", icon: "🌿", hint: "Consumo kWh, Costes (€) & CO2e" },
          { id: "capabilities", label: "Capacidades I+D", icon: "⚡", hint: "12 Módulos de Investigación (XAI, CVPR)" },
        ],
      },
      {
        title: "Gobernanza & Sistema",
        views: [
          { id: "audit", label: "Auditoría & Seguridad", icon: "📜", hint: "Registro inmutable de operaciones" },
          { id: "history", label: "Historial de Estudios", icon: "📈", hint: "Analítica Optuna & Comparador" },
          { id: "settings", label: "Ajustes del Sistema", icon: "🛠️", hint: "Webhooks, Mantenimiento & Contraseña" },
        ],
      },
    ];

    container.innerHTML = sections.map(sec => `
      <div class="nav-section-title">${sec.title}</div>
      <div class="nav-group">
        ${sec.views.map(v => {
          const isActive = v.id === this.activeViewId;
          return `
            <div class="nav-item ${isActive ? 'active' : ''}" onclick="window.workbench.switchView('${v.id}')">
              <span class="nav-icon">${v.icon}</span>
              <div class="nav-content">
                <div class="nav-row">
                  <span class="nav-label">${v.label}</span>
                  ${v.badge ? `<span class="nav-badge ${v.badgeClass || 'badge-blue'}">${v.badge}</span>` : ''}
                </div>
                <div class="nav-hint">${v.hint}</div>
              </div>
            </div>
          `;
        }).join("")}
      </div>
    `).join("");
  }

  openTab(viewId) {
    if (!this.openTabs.includes(viewId)) {
      this.openTabs.push(viewId);
    }
    this.switchView(viewId);
  }

  closeTab(viewId) {
    this.openTabs = this.openTabs.filter(id => id !== viewId);
    if (this.activeViewId === viewId) {
      const nextId = this.openTabs[this.openTabs.length - 1] || "overview";
      if (!this.openTabs.includes(nextId)) this.openTabs.push(nextId);
      this.switchView(nextId);
    } else {
      this.renderTabs();
    }
  }

  // --- Views & Navigation ---
  renderViewContainer() {
    const container = document.getElementById("views-container");
    container.innerHTML = Object.keys(this.views).map(id => {
      const view = this.views[id];
      return `<div id="view-pane-${id}" class="view-pane">${view.render()}</div>`;
    }).join("");
  }

  async switchView(viewId) {
    if (!this.views[viewId]) return;
    this.closeAllMenus();

    if (!this.openTabs.includes(viewId)) {
      this.openTabs.push(viewId);
    }
    this.activeViewId = viewId;
    this.renderTabs();

    // Toggle active view pane
    document.querySelectorAll(".view-pane").forEach(p => p.classList.remove("active"));
    const activePane = document.getElementById(`view-pane-${viewId}`);
    if (activePane) {
      activePane.classList.add("active");
    }

    // Update breadcrumbs
    const view = this.views[viewId];
    document.getElementById("breadcrumb-category").textContent = view.category || "cluster";
    document.getElementById("breadcrumb-file").textContent = view.file || `${viewId}.cluster`;
    document.getElementById("breadcrumb-current").textContent = `${view.icon} ${view.label}`;

    // Load view data
    if (typeof view.load === "function") {
      try {
        await view.load();
      } catch (e) {
        this.logTerminal("ERROR", `Failed to load view ${viewId}: ${e.message}`);
      }
    }
  }

  async refreshCurrentView() {
    const view = this.views[this.activeViewId];
    if (view && typeof view.load === "function") {
      this.logTerminal("INFO", `Refreshing view: ${view.label}...`);
      await view.load();
      this.logTerminal("SUCCESS", `View ${view.label} updated.`);
    }
  }

  // --- Bottom Panel (Terminal / Output) ---
  toggleBottomPanel() {
    const panel = document.getElementById("part-panel");
    this.panelCollapsed = !this.panelCollapsed;
    if (this.panelCollapsed) {
      panel.classList.add("collapsed");
    } else {
      panel.classList.remove("collapsed");
    }
  }

  clearTerminal() {
    document.getElementById("terminal-body").innerHTML = "";
    this.logTerminal("INFO", "Terminal buffer cleared.");
  }

  logTerminal(tag, message) {
    const body = document.getElementById("terminal-body");
    if (!body) return;
    const time = new Date().toTimeString().split(" ")[0];
    const row = document.createElement("div");
    row.className = "log-entry";
    row.innerHTML = `
      <span class="log-time">[${time}]</span>
      <span class="log-tag ${tag}">[${tag}]</span>
      <span class="log-msg">${escapeHtml(message)}</span>
    `;
    body.appendChild(row);
    body.scrollTop = body.scrollHeight;
  }

  // --- Command Palette (Ctrl+P / F1) ---
  async toggleCommandPalette() {
    const overlay = document.getElementById("palette-overlay");
    const isShowing = overlay.classList.contains("show");
    if (isShowing) {
      this.closeCommandPalette();
    } else {
      overlay.classList.add("show");
      const input = document.getElementById("palette-search");
      input.value = "";
      input.focus();
      if (!this.cachedInvokers.length) {
        await this.fetchLiveTelemetryData();
      }
      this.filterCommandPalette("");
    }
  }

  closeCommandPalette() {
    const overlay = document.getElementById("palette-overlay");
    overlay.classList.remove("show");
  }

  filterCommandPalette(query) {
    const list = document.getElementById("palette-list");
    const q = query.toLowerCase().trim();

    let items = [];

    // 1. Quick Actions & Intent Shortcuts
    const quickActions = [
      {
        category: "⚡ ACCIONES RÁPIDAS",
        title: "🚀 Lanzar nuevo entrenamiento (Quick Launch)",
        subtitle: "Configurar modelo YOLO, dataset, horario diferido y despachar a Celery",
        action: () => this.switchView("dispatch"),
        keywords: ["lanzar", "entrenar", "launch", "dispatch", "nuevo", "yolo", "train", "start"],
      },
      {
        category: "⚡ ACCIONES RÁPIDAS",
        title: "⚙️ Ajustar límites de hardware de los nodos (VRAM, RAM, CPU, SHM)",
        subtitle: "Configurar topes de recursos para evitar colapsos",
        action: () => this.switchView("nodes"),
        keywords: ["limites", "hardware", "ram", "cpu", "gpu", "vram", "shm", "memoria", "recursos"],
      },
      {
        category: "⚡ ACCIONES RÁPIDAS",
        title: "⏸️ Gestionar Pausas y Recursos de Invokers (Vista de Nodos)",
        subtitle: "Configurar pausas temporales (horas/hora fija) o perpetuas por cada nodo",
        action: () => this.switchView("nodes"),
        keywords: ["pausar", "pausa", "pause", "reanudar", "resume", "invoker", "nodos"],
      },
      {
        category: "⚡ ACCIONES RÁPIDAS",
        title: "📥 Broadcast Docker Pull en todo el clúster",
        subtitle: "Descargar la última imagen Docker en todos los invokers en paralelo",
        action: () => this.broadcastDockerPullPrompt(),
        keywords: ["broadcast", "pull", "docker", "actualizar", "imagen", "descargar"],
      },
      {
        category: "⚡ ACCIONES RÁPIDAS",
        title: "💻 Abrir panel de Logs y Terminal en vivo (Ctrl+J)",
        subtitle: "Consola ANSI en tiempo real con diagnóstico de eventos",
        action: () => this.toggleBottomPanel(),
        keywords: ["terminal", "logs", "output", "consola", "registro"],
      },
      {
        category: "⚡ ACCIONES RÁPIDAS",
        title: "💾 Inspeccionar almacenamiento Samba CIFS y MinIO S3",
        subtitle: "Verificar latencia I/O y disponibilidad de volúmenes de datasets",
        action: () => this.switchView("storage"),
        keywords: ["storage", "almacenamiento", "samba", "cifs", "minio", "s3", "disco", "dataset", "datasets"],
      },
      {
        category: "⚡ ACCIONES RÁPIDAS",
        title: "🌿 Ver costes de energía, consumo kWh y FinOps",
        subtitle: "Monitor de gasto eléctrico en euros y huella de carbono CO2e",
        action: () => this.switchView("finops"),
        keywords: ["finops", "energia", "coste", "costes", "luz", "electricidad", "kwh", "dinero", "precio"],
      },
      {
        category: "⚡ ACCIONES RÁPIDAS",
        title: "🏆 Ver Leaderboard de rendimiento de GPUs (Benchmarks)",
        subtitle: "Throughput empírico en img/s y ranking de tarjetas gráficas",
        action: () => this.switchView("benchmarks"),
        keywords: ["benchmark", "benchmarks", "ranking", "rendimiento", "throughput", "fps", "velocidad"],
      },
      {
        category: "⚡ ACCIONES RÁPIDAS",
        title: "🔑 Cambiar contraseña de operador",
        subtitle: "Actualizar credenciales de acceso seguras en Redis",
        action: () => this.switchView("settings"),
        keywords: ["password", "contraseña", "clave", "seguridad", "cambiar", "usuario"],
      },
      {
        category: "⚡ ACCIONES RÁPIDAS",
        title: "🔔 Configurar webhooks y alertas (Discord / Slack)",
        subtitle: "Recibir avisos ante fallos o finalización de entrenamientos",
        action: () => this.switchView("settings"),
        keywords: ["webhook", "alertas", "notificaciones", "discord", "slack", "telegram"],
      },
    ];

    const matchedActions = quickActions.filter(a => {
      if (!q) return true;
      const text = (a.title + " " + a.subtitle + " " + (a.keywords || []).join(" ")).toLowerCase();
      return text.includes(q);
    });
    items.push(...matchedActions);

    // 2. Search Live Hardware Nodes
    if (Array.isArray(this.cachedInvokers) && this.cachedInvokers.length) {
      const nodeItems = this.cachedInvokers.filter(n => {
        if (!q) return false;
        const ip = n.worker_ip || n.ip || '';
        const host = n.hostname || '';
        const gpu = n.physical?.gpu_model || n.gpu_model || '';
        const state = n.pause_state || n.status || '';
        const text = `${ip} ${host} ${gpu} ${state}`.toLowerCase();
        return text.includes(q);
      }).map(n => {
        const ip = n.worker_ip || n.ip || '';
        const host = n.hostname || ip;
        const gpu = n.physical?.gpu_model || n.gpu_model || 'GPU';
        const vramCap = n.limits?.max_gpu_percent || n.max_gpu_percent || 30;
        const ram = n.limits?.max_ram || n.max_ram || '6g';
        const cores = n.limits?.max_cpu_cores || n.max_cpu_cores || 2;
        const isPaused = (n.pause_state === 'paused');
        return {
          category: "🖥️ NODOS & GPUS",
          title: `Nodo: ${host} (${ip}) — ${gpu}`,
          subtitle: `Estado: ${isPaused ? '⏸️ Pausado' : '🟢 Activo'} • VRAM: ${vramCap}% • RAM: ${ram} • Cores: ${cores}`,
          action: () => {
            this.switchView("nodes");
            setTimeout(() => {
              const input = document.getElementById("inv-search-input");
              if (input) {
                input.value = ip;
                window.ViewNodes?.onSearch(ip);
              }
            }, 150);
          },
        };
      });
      items.push(...nodeItems);
    }

    // 3. Search Live Active Training Tasks
    if (Array.isArray(this.cachedActiveTasks) && this.cachedActiveTasks.length) {
      const taskItems = this.cachedActiveTasks.filter(t => {
        if (!q) return false;
        const text = `${t.study_name || ''} ${t.model || ''} ${t.author || ''} ${t.worker_ip || ''}`.toLowerCase();
        return text.includes(q);
      }).map(t => {
        const ep = t.epoch_progress;
        const progressStr = ep && ep.total_epochs > 0 
          ? `Epoch ${ep.current_epoch}/${ep.total_epochs} (${ep.percent || 0}%)`
          : (t.progress?.total_trials ? `Trial ${t.progress.completed_trials || 0}/${t.progress.total_trials}` : 'En ejecución');
        return {
          category: "🔥 TRABAJOS EN EJECUCIÓN",
          title: `Trabajo: ${t.study_name} (${t.model || 'YOLO'})`,
          subtitle: `Nodo: ${t.worker_ip || t.assigned_node || 'N/A'} • Autor: ${t.author || 'N/A'} • ${progressStr}`,
          action: () => {
            this.switchView("tasks");
          },
        };
      });
      items.push(...taskItems);
    }

    // 3b. Search Queued Tasks
    if (Array.isArray(this.cachedQueuedTasks) && this.cachedQueuedTasks.length) {
      const queuedItems = this.cachedQueuedTasks.filter(t => {
        if (!q) return false;
        const text = `${t.study_name || ''} ${t.model || ''} ${t.author || ''} ${t.queue || ''}`.toLowerCase();
        return text.includes(q);
      }).map(t => ({
        category: "⏳ COLA DE ESPERA",
        title: `En Cola: ${t.study_name || t.id} (${t.model || 'YOLO'})`,
        subtitle: `Cola: ${t.queue || 'wyolo_gpu_queue'} • Autor: ${t.author || 'N/A'}`,
        action: () => {
          this.switchView("tasks");
        },
      }));
      items.push(...queuedItems);
    }

    // 4. Primary Views
    const viewItems = Object.keys(this.views).map(id => {
      const v = this.views[id];
      return {
        category: "🧭 VISTAS DEL SISTEMA",
        title: `${v.icon} Ir a: ${v.label}`,
        subtitle: `Sección principal: ${v.category || 'cluster'} / ${id}`,
        action: () => this.switchView(id),
        keywords: [v.label.toLowerCase(), id, v.category || ""],
      };
    }).filter(v => {
      if (!q) return true;
      return v.title.toLowerCase().includes(q) || v.keywords.some(k => k.includes(q));
    });
    items.push(...viewItems);

    list.innerHTML = items.map((it, idx) => `
      <li class="palette-item ${idx === 0 ? 'active' : ''}" data-idx="${idx}" onclick="window.workbench.runPaletteAction(${idx})">
        <div style="flex: 1;">
          <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 2px;">
            <span style="font-weight: 600; color: #F8FAFC;">${it.title}</span>
            ${it.category ? `<span class="palette-category-badge">${it.category}</span>` : ''}
          </div>
          <div class="palette-item-desc" style="font-size: 11px; color: #94A3B8;">${it.subtitle}</div>
        </div>
        <kbd style="font-size: 10px; color: #64748B; margin-left: 12px;">↵</kbd>
      </li>
    `).join("");

    this.paletteActions = items;
  }

  runPaletteAction(idx) {
    const item = this.paletteActions && this.paletteActions[idx];
    if (item && typeof item.action === "function") {
      this.closeCommandPalette();
      item.action();
    }
  }

  handlePaletteNav(e) {
    const items = document.querySelectorAll(".palette-item");
    if (!items.length) return;

    let activeIdx = -1;
    items.forEach((it, idx) => {
      if (it.classList.contains("active")) activeIdx = idx;
    });

    if (e.key === "ArrowDown") {
      e.preventDefault();
      const nextIdx = (activeIdx + 1) % items.length;
      items.forEach(it => it.classList.remove("active"));
      items[nextIdx].classList.add("active");
      items[nextIdx].scrollIntoView({ block: "nearest" });
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      const prevIdx = (activeIdx - 1 + items.length) % items.length;
      items.forEach(it => it.classList.remove("active"));
      items[prevIdx].classList.add("active");
      items[prevIdx].scrollIntoView({ block: "nearest" });
    } else if (e.key === "Enter") {
      e.preventDefault();
      if (activeIdx >= 0) {
        this.runPaletteAction(activeIdx);
      }
    }
  }

  openCommand(cmd) {
    if (cmd === "quick_launch") {
      this.switchView("dispatch");
    }
  }

  async broadcastDockerPullPrompt() {
    const tag = prompt("Broadcast Docker Pull across all invokers.\nEnter image tag or leave empty for default:", "wisrovi/train_service:worker_executor_v1.0.0");
    if (tag === null) return;
    this.logTerminal("WARN", `Triggering broadcast docker pull for: ${tag}...`);
    try {
      const res = await window.apiClient.broadcastDockerPull(tag || null);
      this.logTerminal("SUCCESS", `Broadcast pull triggered across nodes: ${JSON.stringify(res)}`);
      alert(`Broadcast pull dispatched successfully!`);
    } catch (e) {
      this.logTerminal("ERROR", `Broadcast pull failed: ${e.message}`);
      alert(`Broadcast pull error: ${e.message}`);
    }
  }

  // --- Telemetry Polling ---
  async fetchLiveTelemetryData() {
    try {
      const [nodes, tasks, queued] = await Promise.allSettled([
        window.apiClient.getInvokers(),
        window.apiClient.getActiveTasks(),
        window.apiClient.getQueuedTasks(),
      ]);

      if (nodes.status === "fulfilled" && Array.isArray(nodes.value)) {
        this.cachedInvokers = nodes.value;
      }
      if (tasks.status === "fulfilled" && Array.isArray(tasks.value)) {
        this.cachedActiveTasks = tasks.value;
      }
      if (queued.status === "fulfilled" && Array.isArray(queued.value)) {
        this.cachedQueuedTasks = queued.value;
      }

      // Update sidebar nav badges dynamically without disrupting UI
      this.renderTabs();
    } catch (_) {}
  }

  startBackgroundTelemetry() {
    this.fetchLiveTelemetryData();
    if (this.pollInterval) clearInterval(this.pollInterval);
    this.pollInterval = setInterval(async () => {
      try {
        const start = performance.now();
        await this.fetchLiveTelemetryData();
        const health = await window.apiClient.getHealth();
        const latency = Math.round(performance.now() - start);

        const latencyEl = document.getElementById("status-latency");
        if (latencyEl) latencyEl.textContent = `⚡ ${latency}ms`;

        const healthEl = document.getElementById("status-health");
        if (healthEl) healthEl.textContent = `Cluster Healthy`;
      } catch (_) {
        const healthEl = document.getElementById("status-health");
        if (healthEl) healthEl.textContent = `API Offline`;
      }
    }, 10000);
  }
}

function escapeHtml(str) {
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

window.addEventListener("DOMContentLoaded", () => {
  window.workbench = new VSCodeWorkbench();
});
