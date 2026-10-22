/**
 * NeuralForge Cluster Admin v3.1.0 — VSCode Workbench Core Application
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

    this.openTabs = ["overview", "nodes", "dispatch"];
    this.activeViewId = "overview";
    this.activeMenu = null;
    this.panelCollapsed = false;
    this.pollInterval = null;

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

    this.logTerminal("SUCCESS", "NeuralForge Cluster Admin v3.1.0 Workbench initialized.");
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
    container.innerHTML = this.openTabs.map(viewId => {
      const view = this.views[viewId];
      if (!view) return "";
      const isActive = viewId === this.activeViewId;
      return `
        <div class="editor-tab ${isActive ? 'active' : ''}" onclick="window.workbench.switchView('${viewId}')">
          <span class="tab-icon">${view.icon}</span>
          <span class="tab-label">${view.label}</span>
          <span class="tab-close" onclick="event.stopPropagation(); window.workbench.closeTab('${viewId}')" title="Cerrar pestaña">✕</span>
        </div>
      `;
    }).join("");
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
  toggleCommandPalette() {
    const overlay = document.getElementById("palette-overlay");
    const isShowing = overlay.classList.contains("show");
    if (isShowing) {
      this.closeCommandPalette();
    } else {
      overlay.classList.add("show");
      const input = document.getElementById("palette-search");
      input.value = "";
      input.focus();
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

    const items = [
      // Views
      ...Object.keys(this.views).map(id => {
        const v = this.views[id];
        return {
          type: "view",
          id: id,
          title: `${v.icon} Ir a Vista: ${v.label}`,
          subtitle: `cluster_control / ${v.category} / ${v.file}`,
          action: () => this.switchView(id),
        };
      }),
      // Actions
      {
        type: "action",
        title: "📥 Acción: Broadcast Docker Pull",
        subtitle: "Triggers docker pull across all invoker nodes in cluster",
        action: () => this.broadcastDockerPullPrompt(),
      },
      {
        type: "action",
        title: "💻 Acción: Alternar Terminal / Output Panel",
        subtitle: "Shortcut: Ctrl+J",
        action: () => this.toggleBottomPanel(),
      },
      {
        type: "action",
        title: "🔄 Acción: Recargar Telemetría del Cluster",
        subtitle: "Fetch latest metrics from FastAPI backend",
        action: () => this.refreshCurrentView(),
      },
      {
        type: "action",
        title: "⚡ Acción: Quick Launch Training Workload",
        subtitle: "Dispatch YOLO training job to Celery",
        action: () => this.switchView("dispatch"),
      },
      {
        type: "action",
        title: "🚪 Acción: Cerrar Sesión (Logout)",
        subtitle: "Clear JWT authorization token",
        action: () => this.logout(),
      },
    ];

    const filtered = items.filter(it =>
      it.title.toLowerCase().includes(q) || it.subtitle.toLowerCase().includes(q)
    );

    list.innerHTML = filtered.map((it, idx) => `
      <li class="palette-item ${idx === 0 ? 'active' : ''}" data-idx="${idx}" onclick="window.workbench.runPaletteAction(${idx})">
        <div>
          <div style="font-weight: 500;">${it.title}</div>
          <div class="palette-item-desc">${it.subtitle}</div>
        </div>
        <kbd style="font-size: 10px; color: var(--vscode-fg-muted);">Enter</kbd>
      </li>
    `).join("");

    this.paletteActions = filtered;
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
  startBackgroundTelemetry() {
    if (this.pollInterval) clearInterval(this.pollInterval);
    this.pollInterval = setInterval(async () => {
      try {
        const start = performance.now();
        const health = await window.apiClient.getHealth();
        const latency = Math.round(performance.now() - start);

        const latencyEl = document.getElementById("status-latency");
        if (latencyEl) latencyEl.textContent = `🔄 ${latency}ms`;

        const healthEl = document.getElementById("status-health");
        if (healthEl) healthEl.textContent = `🟢 Healthy`;
      } catch (_) {
        const healthEl = document.getElementById("status-health");
        if (healthEl) healthEl.textContent = `🔴 API Offline`;
      }
    }, 12000);
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
