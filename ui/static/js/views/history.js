/**
 * Workload & Training Job Execution History (history.log)
 * Features: Multi-field filters, Optuna curves, Head-to-Head comparison,
 * Reproducibility manifest, Diagnostics, and Live execution logs.
 */

window.ViewHistory = {
  id: "history",
  label: "Job History",
  icon: "📈",
  file: "history.log",
  category: "reports",

  activeTab: "history", // "history" | "metrics" | "compare" | "export"
  historyData: [],
  selectedStudyId: null,
  comparisonStudies: [],

  render() {
    return `
      <div class="view-header">
        <div class="view-title-group">
          <h1><span>📈</span> Workload & Training Job Execution History</h1>
          <p>Audit trail of executed studies, Optuna convergence curves, head-to-head comparison, and reproducibility manifests</p>
        </div>
        <div class="view-actions">
          <button class="btn btn-primary btn-sm" onclick="window.ViewHistory.load()">
            <span>🔄</span> Refresh History
          </button>
        </div>
      </div>

      <!-- Navigation Sub-Tabs -->
      <div style="display: flex; gap: 4px; border-bottom: 1px solid var(--vscode-border-light); margin-bottom: 16px;">
        <button id="htab-btn-history" class="btn btn-sm ${this.activeTab === 'history' ? 'btn-primary' : 'btn-secondary'}" onclick="window.ViewHistory.switchTab('history')">
          📜 History & Search
        </button>
        <button id="htab-btn-metrics" class="btn btn-sm ${this.activeTab === 'metrics' ? 'btn-primary' : 'btn-secondary'}" onclick="window.ViewHistory.switchTab('metrics')">
          📈 Learning Curves (Optuna)
        </button>
        <button id="htab-btn-compare" class="btn btn-sm ${this.activeTab === 'compare' ? 'btn-primary' : 'btn-secondary'}" onclick="window.ViewHistory.switchTab('compare')">
          🔬 Head-to-Head Comparison
        </button>
        <button id="htab-btn-export" class="btn btn-sm ${this.activeTab === 'export' ? 'btn-primary' : 'btn-secondary'}" onclick="window.ViewHistory.switchTab('export')">
          📥 Report Exporter
        </button>
      </div>

      <!-- TAB 1: HISTORY & SEARCH -->
      <div id="htab-pane-history" style="display: ${this.activeTab === 'history' ? 'block' : 'none'};">
        <!-- Filter Toolbar -->
        <div class="card-section" style="margin-bottom: 16px; padding: 12px 16px;">
          <div style="display: flex; flex-wrap: wrap; gap: 10px; align-items: center; justify-content: space-between;">
            <div style="display: flex; gap: 8px; flex: 1; min-width: 250px;">
              <input type="text" id="hist-search-input" class="form-control form-control-sm" placeholder="Search by study name, ID, dataset, or model..." oninput="window.ViewHistory.applyFilters()">
              <label style="display: flex; align-items: center; gap: 6px; font-size: 11px; cursor: pointer; white-space: nowrap; color: var(--vscode-fg-bright);">
                <input type="checkbox" id="hist-only-mine" onchange="window.ViewHistory.applyFilters()"> 👤 My studies only
              </label>
            </div>

            <div style="display: flex; flex-wrap: wrap; gap: 8px;">
              <select id="hist-filter-author" class="form-control form-control-sm" style="width: 140px;" onchange="window.ViewHistory.applyFilters()">
                <option value="All">All Authors</option>
              </select>
              <select id="hist-filter-node" class="form-control form-control-sm" style="width: 150px;" onchange="window.ViewHistory.applyFilters()">
                <option value="All">All Nodes</option>
              </select>
              <select id="hist-filter-status" class="form-control form-control-sm" style="width: 130px;" onchange="window.ViewHistory.applyFilters()">
                <option value="All">All Statuses</option>
                <option value="completed">Completed</option>
                <option value="running">Running</option>
                <option value="failed">Failed</option>
              </select>
              <select id="hist-filter-limit" class="form-control form-control-sm" style="width: 90px;" onchange="window.ViewHistory.load()">
                <option value="20">20 rec</option>
                <option value="50" selected>50 rec</option>
                <option value="100">100 rec</option>
              </select>
            </div>
          </div>
        </div>

        <!-- History Table -->
        <div class="card-section">
          <div class="card-title">
            <span>Historical Workloads</span>
            <span class="badge badge-blue" id="hist-count-badge">0 Studies</span>
          </div>
          <div class="table-responsive">
            <table class="vscode-table">
              <thead>
                <tr>
                  <th style="width: 30px;">#</th>
                  <th>Study Name & ID</th>
                  <th>Submitter</th>
                  <th>Node</th>
                  <th>Model & Dataset</th>
                  <th>Status</th>
                  <th>Started</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody id="history-tbody">
                <tr><td colspan="8" style="text-align: center; color: var(--vscode-fg-muted); padding: 16px;">Loading training history...</td></tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- TAB 2: OPTUNA LEARNING CURVES -->
      <div id="htab-pane-metrics" style="display: ${this.activeTab === 'metrics' ? 'block' : 'none'};">
        <div class="card-section" style="margin-bottom: 16px; padding: 12px 16px;">
          <div style="display: flex; gap: 12px; align-items: center;">
            <label class="form-label" style="margin: 0; white-space: nowrap; font-weight: 600;">Select Study:</label>
            <select id="metrics-study-selector" class="form-control" style="flex: 1;" onchange="window.ViewHistory.loadOptunaMetrics(this.value)">
              <option value="">-- Choose a study to analyze --</option>
            </select>
          </div>
        </div>

        <div id="metrics-content-area">
          <div class="card-section" style="text-align: center; padding: 40px; color: var(--vscode-fg-muted);">
            Select a study above or click "📈 Curves" on any row in the history table to plot Optuna learning curves.
          </div>
        </div>
      </div>

      <!-- TAB 3: HEAD-TO-HEAD COMPARISON -->
      <div id="htab-pane-compare" style="display: ${this.activeTab === 'compare' ? 'block' : 'none'};">
        <div class="card-section" style="margin-bottom: 16px;">
          <div class="card-title"><span>Select Studies to Compare (2 to 5):</span></div>
          <div id="compare-selection-checkboxes" style="display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 8px; margin: 10px 0;">
            <div style="color: var(--vscode-fg-muted); font-size: 12px;">Loading available studies...</div>
          </div>
          <button class="btn btn-primary btn-sm" onclick="window.ViewHistory.runHeadToHeadComparison()">
            <span>🔬</span> Compare Selected Studies
          </button>
        </div>

        <div id="compare-results-container"></div>
      </div>

      <!-- TAB 4: REPORT EXPORTER -->
      <div id="htab-pane-export" style="display: ${this.activeTab === 'export' ? 'block' : 'none'};">
        <div class="card-section">
          <div class="card-title"><span>📥 Export Study Report</span></div>
          <div style="display: grid; grid-template-columns: 2fr 1fr; gap: 16px; margin: 12px 0;">
            <div class="form-group">
              <label class="form-label">Study to Export:</label>
              <select id="export-study-selector" class="form-control">
                <option value="">-- Choose a study --</option>
              </select>
            </div>
            <div class="form-group">
              <label class="form-label">Format:</label>
              <select id="export-format-selector" class="form-control">
                <option value="markdown">Markdown (.md)</option>
                <option value="json">JSON (.json)</option>
              </select>
            </div>
          </div>
          <button class="btn btn-primary" onclick="window.ViewHistory.exportStudyReport()">
            <span>💾</span> Generate & Download Report
          </button>
          <div id="export-preview-area" style="margin-top: 16px; display: none;">
            <label class="form-label">Report Preview:</label>
            <pre id="export-preview-code" style="background: #1E1E1E; border: 1px solid var(--vscode-border-light); padding: 12px; border-radius: 4px; max-height: 350px; overflow-y: auto; font-size: 11px;"></pre>
          </div>
        </div>
      </div>

      <!-- Study Details Inspector Modal -->
      <div id="study-inspect-modal" style="display: none; position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; background: rgba(0,0,0,0.7); z-index: 6000; justify-content: center; align-items: center;">
        <div style="width: 850px; max-width: 95vw; max-height: 90vh; background: var(--vscode-bg-sidebar); border: 1px solid var(--vscode-border-light); border-radius: 6px; padding: 20px; box-shadow: 0 8px 30px rgba(0,0,0,0.8); display: flex; flex-direction: column;">
          
          <div style="font-size: 15px; font-weight: 600; color: var(--vscode-fg-bright); margin-bottom: 12px; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid var(--vscode-border-light); padding-bottom: 8px;">
            <span id="study-modal-title">🔍 Study Details Inspector</span>
            <span style="cursor: pointer; color: var(--vscode-fg-muted); font-size: 16px;" onclick="document.getElementById('study-inspect-modal').style.display='none'">✕</span>
          </div>

          <div style="overflow-y: auto; flex: 1; padding-right: 6px;">
            <!-- Metadata Grid -->
            <div id="study-modal-meta" style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; background: #252526; padding: 12px; border-radius: 4px; margin-bottom: 14px; font-size: 12px;"></div>

            <!-- Diagnostics Expander -->
            <div id="study-modal-diag-container" style="margin-bottom: 12px;">
              <details style="background: #252526; border: 1px solid var(--vscode-border-light); border-radius: 4px; padding: 10px;">
                <summary style="font-weight: 600; cursor: pointer; color: #F59E0B;">🩺 Root Cause Failure Diagnostics</summary>
                <div id="study-modal-diag-body" style="margin-top: 10px; font-size: 12px;"></div>
              </details>
            </div>

            <!-- Reproducibility Manifest -->
            <div style="margin-bottom: 12px;">
              <details open style="background: #252526; border: 1px solid var(--vscode-border-light); border-radius: 4px; padding: 10px;">
                <summary style="font-weight: 600; cursor: pointer; color: #007ACC;">📋 Reproducibility Manifest (Docker Command & YAML)</summary>
                <div id="study-modal-repro-body" style="margin-top: 10px; font-size: 12px;"></div>
              </details>
            </div>

            <!-- Task Execution Logs -->
            <div style="margin-bottom: 12px;">
              <details style="background: #252526; border: 1px solid var(--vscode-border-light); border-radius: 4px; padding: 10px;">
                <summary style="font-weight: 600; cursor: pointer; color: var(--vscode-fg-bright);">📄 Task Execution Logs</summary>
                <pre id="study-modal-logs-body" style="margin-top: 10px; background: #181818; padding: 12px; border-radius: 4px; font-size: 11px; max-height: 250px; overflow-y: auto;"></pre>
              </details>
            </div>
          </div>

          <div style="display: flex; justify-content: flex-end; margin-top: 12px; padding-top: 8px; border-top: 1px solid var(--vscode-border-light);">
            <button class="btn btn-secondary btn-sm" onclick="document.getElementById('study-inspect-modal').style.display='none'">Cerrar</button>
          </div>
        </div>
      </div>
    `;
  },

  switchTab(tab) {
    this.activeTab = tab;
    ["history", "metrics", "compare", "export"].forEach(t => {
      const btn = document.getElementById(`htab-btn-${t}`);
      const pane = document.getElementById(`htab-pane-${t}`);
      if (btn) btn.className = `btn btn-sm ${t === tab ? 'btn-primary' : 'btn-secondary'}`;
      if (pane) pane.style.display = t === tab ? "block" : "none";
    });

    if (tab === "compare") {
      this.renderCompareCheckboxes();
    }
  },

  async load() {
    const limitEl = document.getElementById("hist-filter-limit");
    const limit = limitEl ? parseInt(limitEl.value) : 50;

    try {
      const res = await window.apiClient.getTaskHistory(limit);
      this.historyData = Array.isArray(res) ? res : (res.history || res.tasks || []);
      this.populateFilterDropdowns();
      this.applyFilters();
      this.populateStudySelectors();
    } catch (e) {
      document.getElementById("history-tbody").innerHTML = `
        <tr><td colspan="8" style="text-align: center; color: var(--vscode-btn-danger); padding: 16px;">
          Failed to load history: ${e.message}
        </td></tr>
      `;
    }
  },

  populateFilterDropdowns() {
    const authors = Array.from(new Set(this.historyData.map(h => h.author || "wisrovi"))).sort();
    const nodes = Array.from(new Set(this.historyData.map(h => h.destination_node || h.worker_ip || "wyolo_gpu_queue"))).sort();

    const authSel = document.getElementById("hist-filter-author");
    if (authSel) {
      const curr = authSel.value;
      authSel.innerHTML = `<option value="All">All Authors</option>` + authors.map(a => `<option value="${a}">${a}</option>`).join("");
      authSel.value = curr || "All";
    }

    const nodeSel = document.getElementById("hist-filter-node");
    if (nodeSel) {
      const curr = nodeSel.value;
      nodeSel.innerHTML = `<option value="All">All Nodes</option>` + nodes.map(n => `<option value="${n}">${n}</option>`).join("");
      nodeSel.value = curr || "All";
    }
  },

  populateStudySelectors() {
    const options = this.historyData.map(h => {
      const sid = h.study_id || h.id || "";
      const sname = h.study_name || sid;
      return `<option value="${sid}">${sname} (${sid.substring(0, 8)}) [${h.status || 'completed'}]</option>`;
    }).join("");

    const metricSel = document.getElementById("metrics-study-selector");
    if (metricSel) metricSel.innerHTML = `<option value="">-- Choose a study to analyze --</option>` + options;

    const exportSel = document.getElementById("export-study-selector");
    if (exportSel) exportSel.innerHTML = `<option value="">-- Choose a study --</option>` + options;
  },

  applyFilters() {
    const q = (document.getElementById("hist-search-input")?.value || "").toLowerCase().trim();
    const onlyMine = document.getElementById("hist-only-mine")?.checked || false;
    const author = document.getElementById("hist-filter-author")?.value || "All";
    const node = document.getElementById("hist-filter-node")?.value || "All";
    const status = document.getElementById("hist-filter-status")?.value || "All";

    const user = window.apiClient.getUser()?.username || "wisrovi";

    let filtered = this.historyData.filter(h => {
      if (onlyMine && !(h.author || "").toLowerCase().includes(user.toLowerCase())) return false;
      if (author !== "All" && (h.author || "") !== author) return false;
      if (node !== "All" && (h.destination_node || h.worker_ip || "") !== node) return false;
      if (status !== "All" && (h.status || "").toLowerCase() !== status.toLowerCase()) return false;
      if (q) {
        const text = `${h.study_name || ''} ${h.study_id || ''} ${h.dataset || ''} ${h.model || ''}`.toLowerCase();
        if (!text.includes(q)) return false;
      }
      return true;
    });

    document.getElementById("hist-count-badge").textContent = `${filtered.length} Studies`;

    const tbody = document.getElementById("history-tbody");
    if (!filtered.length) {
      tbody.innerHTML = `<tr><td colspan="8" style="text-align: center; color: var(--vscode-fg-muted); padding: 16px;">No recorded studies match the criteria.</td></tr>`;
      return;
    }

    tbody.innerHTML = filtered.map((h, idx) => {
      const sid = h.study_id || h.id || "";
      const sname = h.study_name || sid;
      const st = (h.status || "completed").toLowerCase();
      const badge = st === "completed"
        ? '<span class="badge badge-green">Completed</span>'
        : (st === "running" ? '<span class="badge badge-blue">Running</span>' : '<span class="badge badge-red">Failed</span>');

      return `
        <tr>
          <td><span style="color: var(--vscode-fg-muted); font-size: 11px;">#${idx + 1}</span></td>
          <td>
            <div style="font-weight: 600; color: var(--vscode-fg-bright);">${sname}</div>
            <div style="font-size: 10px; color: var(--vscode-fg-muted);"><code>${sid.substring(0, 16)}...</code></div>
          </td>
          <td><code>${h.author || 'wisrovi'}</code></td>
          <td><code>${h.destination_node || h.worker_ip || 'Cluster'}</code></td>
          <td>
            <div style="font-weight: 500;">${h.model || 'yolov8m'}</div>
            <div style="font-size: 10px; color: var(--vscode-fg-muted);">${h.dataset || 'Dataset'}</div>
          </td>
          <td>${badge}</td>
          <td style="font-size: 11px;">${h.start_time || h.completed_at || 'Recent'}</td>
          <td>
            <div style="display: flex; gap: 4px;">
              <button class="btn btn-secondary btn-sm" onclick="window.ViewHistory.openStudyModal('${sid}')">
                🔍 Details
              </button>
              <button class="btn btn-secondary btn-sm" onclick="window.ViewHistory.quickCurves('${sid}')">
                📈 Curves
              </button>
            </div>
          </td>
        </tr>
      `;
    }).join("");
  },

  async openStudyModal(studyId) {
    const study = this.historyData.find(h => (h.study_id || h.id) === studyId);
    if (!study) return;

    const modal = document.getElementById("study-inspect-modal");
    document.getElementById("study-modal-title").textContent = `🔍 Study Inspector: ${study.study_name || studyId}`;

    const meta = document.getElementById("study-modal-meta");
    meta.innerHTML = `
      <div><strong>Study ID:</strong> <code>${studyId}</code></div>
      <div><strong>Submitter:</strong> <code>${study.author || 'wisrovi'}</code></div>
      <div><strong>Assigned Node:</strong> <code>${study.destination_node || study.worker_ip || 'Cluster'}</code></div>
      <div><strong>Model:</strong> <code>${study.model || 'N/A'}</code></div>
      <div><strong>Dataset:</strong> <code>${study.dataset || 'N/A'}</code></div>
      <div><strong>Status:</strong> <span style="font-weight: 600;">${study.status || 'Completed'}</span></div>
      <div><strong>Started:</strong> ${study.start_time || 'N/A'}</div>
      <div><strong>Completed:</strong> ${study.completed_at || 'N/A'}</div>
    `;

    // Load reproducibility manifest
    const reproBody = document.getElementById("study-modal-repro-body");
    reproBody.innerHTML = `<span style="color: var(--vscode-fg-muted);">Fetching reproducibility manifest...</span>`;
    try {
      const repro = await window.apiClient.getStudyReproducibility(studyId);
      reproBody.innerHTML = `
        <div style="margin-bottom: 8px; color: var(--vscode-fg-muted); font-size: 11px;">
          SHA256 Fingerprint: <code>${repro.sha256_fingerprint || 'N/A'}</code> | Generated: ${repro.generated_at || 'Now'}
        </div>
        <div style="margin-bottom: 8px;">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
            <strong style="color: var(--vscode-fg-bright);">Docker Run Command:</strong>
            <button class="btn btn-secondary btn-sm" onclick="navigator.clipboard.writeText(document.getElementById('repro-docker-cmd').innerText); alert('Docker command copied!');">📋 Copy</button>
          </div>
          <pre id="repro-docker-cmd" style="background: #181818; padding: 8px; border-radius: 4px; overflow-x: auto; color: #10B981; font-size: 11px;">${repro.docker_run_command || 'docker run --rm ...'}</pre>
        </div>
        <div>
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
            <strong style="color: var(--vscode-fg-bright);">YAML Configuration:</strong>
            <button class="btn btn-secondary btn-sm" onclick="navigator.clipboard.writeText(document.getElementById('repro-yaml-cmd').innerText); alert('YAML copied!');">📋 Copy</button>
          </div>
          <pre id="repro-yaml-cmd" style="background: #181818; padding: 8px; border-radius: 4px; overflow-x: auto; font-size: 11px;">${repro.training_yaml || '# No YAML content available'}</pre>
        </div>
      `;
    } catch (e) {
      reproBody.innerHTML = `<div style="color: var(--vscode-fg-muted);">Reproducibility manifest unavailable: ${e.message}</div>`;
    }

    // Load diagnostics
    const diagBody = document.getElementById("study-modal-diag-body");
    diagBody.innerHTML = `<span style="color: var(--vscode-fg-muted);">Analyzing execution trace...</span>`;
    try {
      const diag = await window.apiClient.getTaskDiagnostics(studyId);
      diagBody.innerHTML = `
        <div style="margin-bottom: 6px;"><strong>Status:</strong> <code>${diag.status || 'OK'}</code></div>
        <div style="margin-bottom: 6px;"><strong>Root Cause:</strong> ${diag.root_cause || 'No abnormal termination detected.'}</div>
        ${diag.suggested_action ? `<div style="padding: 8px; background: rgba(0, 122, 204, 0.15); border-left: 3px solid #007ACC; border-radius: 4px; margin: 6px 0;"><strong>💡 Suggested Action:</strong> ${diag.suggested_action}</div>` : ''}
        ${diag.error ? `<pre style="background: #181818; color: #EF4444; padding: 8px; border-radius: 4px; margin-top: 6px; font-size: 11px;">${diag.error}</pre>` : ''}
      `;
    } catch (e) {
      diagBody.innerHTML = `<span style="color: var(--vscode-fg-muted);">Diagnostics unavailable: ${e.message}</span>`;
    }

    // Load logs
    const logsBody = document.getElementById("study-modal-logs-body");
    logsBody.textContent = "Loading logs...";
    try {
      const logsRes = await window.apiClient.getTaskLogs(studyId, 100);
      const lines = logsRes.logs || logsRes.lines || [];
      logsBody.textContent = lines.length ? lines.join("\n") : "No logs recorded for this study.";
    } catch (e) {
      logsBody.textContent = `Logs unavailable: ${e.message}`;
    }

    modal.style.display = "flex";
  },

  quickCurves(studyId) {
    this.switchTab("metrics");
    const sel = document.getElementById("metrics-study-selector");
    if (sel) sel.value = studyId;
    this.loadOptunaMetrics(studyId);
  },

  async loadOptunaMetrics(studyId) {
    if (!studyId) return;
    const area = document.getElementById("metrics-content-area");
    area.innerHTML = `<div class="card-section" style="padding: 24px; text-align: center; color: var(--vscode-fg-muted);">Retrieving Optuna trial progression metrics...</div>`;

    try {
      const points = await window.apiClient.getStudyMetrics(studyId);
      if (!points || !points.length) {
        area.innerHTML = `
          <div class="card-section" style="padding: 24px; text-align: center; color: var(--vscode-fg-muted);">
            Study <code>${studyId}</code> has not recorded trial metrics yet.
          </div>
        `;
        return;
      }

      const fitnessVals = points.map(p => parseFloat(p.fitness) || 0);
      const bestFitness = Math.max(...fitnessVals);
      const bestIdx = fitnessVals.indexOf(bestFitness);
      const bestTrial = points[bestIdx]?.trial ?? bestIdx;

      // Generate SVG Chart
      const width = 760;
      const height = 220;
      const pad = 40;
      const minF = Math.min(...fitnessVals);
      const maxF = Math.max(...fitnessVals, minF + 0.01);

      const polyPoints = points.map((p, idx) => {
        const x = pad + (idx / Math.max(points.length - 1, 1)) * (width - 2 * pad);
        const y = height - pad - ((p.fitness - minF) / (maxF - minF)) * (height - 2 * pad);
        return `${x.toFixed(1)},${y.toFixed(1)}`;
      }).join(" ");

      area.innerHTML = `
        <div class="metrics-ribbon" style="margin-bottom: 16px;">
          <div class="metric-card">
            <div class="metric-label">🏆 Best Objective Value (Fitness)</div>
            <div class="metric-value" style="color: #10B981;">${bestFitness.toFixed(4)}</div>
            <div class="metric-sub">Trial #${bestTrial}</div>
          </div>
          <div class="metric-card">
            <div class="metric-label">Completed Trials</div>
            <div class="metric-value">${points.length}</div>
            <div class="metric-sub">Optuna TPESampler</div>
          </div>
          <div class="metric-card">
            <div class="metric-label">Initial Baseline</div>
            <div class="metric-value">${fitnessVals[0]?.toFixed(4) || '0.0000'}</div>
            <div class="metric-sub">Trial #0</div>
          </div>
        </div>

        <div class="card-section" style="margin-bottom: 16px;">
          <div class="card-title"><span>📈 Fitness Progression Across Trials</span></div>
          <div style="background: #181818; padding: 12px; border-radius: 4px; overflow-x: auto;">
            <svg viewBox="0 0 ${width} ${height}" style="width: 100%; height: 220px;">
              <!-- Grid lines -->
              <line x1="${pad}" y1="${height - pad}" x2="${width - pad}" y2="${height - pad}" stroke="#333" stroke-width="1"/>
              <line x1="${pad}" y1="${pad}" x2="${width - pad}" y2="${pad}" stroke="#333" stroke-width="1" stroke-dasharray="4"/>
              
              <!-- Value labels -->
              <text x="${pad - 8}" y="${pad + 4}" fill="#888" font-size="10" text-anchor="end">${maxF.toFixed(3)}</text>
              <text x="${pad - 8}" y="${height - pad + 4}" fill="#888" font-size="10" text-anchor="end">${minF.toFixed(3)}</text>

              <!-- Polyline curve -->
              <polyline fill="none" stroke="#007ACC" stroke-width="2.5" points="${polyPoints}"/>

              <!-- Points -->
              ${points.map((p, idx) => {
                const x = pad + (idx / Math.max(points.length - 1, 1)) * (width - 2 * pad);
                const y = height - pad - ((p.fitness - minF) / (maxF - minF)) * (height - 2 * pad);
                const isBest = idx === bestIdx;
                return `
                  <circle cx="${x.toFixed(1)}" cy="${y.toFixed(1)}" r="${isBest ? 5 : 3}" fill="${isBest ? '#10B981' : '#007ACC'}">
                    <title>Trial #${p.trial}: Fitness ${p.fitness.toFixed(4)}</title>
                  </circle>
                `;
              }).join("")}
            </svg>
          </div>
        </div>

        <div class="card-section">
          <div class="card-title"><span>Trial Iterations & Parameters Table</span></div>
          <div class="table-responsive" style="max-height: 250px; overflow-y: auto;">
            <table class="vscode-table">
              <thead>
                <tr>
                  <th>Trial #</th>
                  <th>Fitness (Objective)</th>
                  <th>Learning Rate (lr0)</th>
                  <th>Weight Decay</th>
                  <th>Batch Size</th>
                  <th>State</th>
                </tr>
              </thead>
              <tbody>
                ${points.map((p, i) => `
                  <tr style="${i === bestIdx ? 'background: rgba(16, 185, 129, 0.1); font-weight: 600;' : ''}">
                    <td>#${p.trial ?? i} ${i === bestIdx ? '🏆' : ''}</td>
                    <td style="color: ${i === bestIdx ? '#10B981' : 'inherit'};">${(p.fitness || 0).toFixed(4)}</td>
                    <td><code>${p.params?.lr0 || '0.01'}</code></td>
                    <td><code>${p.params?.weight_decay || '0.0005'}</code></td>
                    <td>${p.params?.batch || '16'}</td>
                    <td><span class="badge badge-green">COMPLETE</span></td>
                  </tr>
                `).join("")}
              </tbody>
            </table>
          </div>
        </div>
      `;
    } catch (e) {
      area.innerHTML = `<div class="card-section" style="color: var(--vscode-btn-danger); padding: 16px;">Failed to load metrics: ${e.message}</div>`;
    }
  },

  renderCompareCheckboxes() {
    const container = document.getElementById("compare-selection-checkboxes");
    if (!container) return;

    if (!this.historyData.length) {
      container.innerHTML = `<div style="color: var(--vscode-fg-muted); font-size: 12px;">No recorded studies available.</div>`;
      return;
    }

    container.innerHTML = this.historyData.slice(0, 15).map((h, i) => {
      const sid = h.study_id || h.id;
      const sname = h.study_name || sid;
      const checked = i < 2 ? "checked" : "";
      return `
        <label style="display: flex; align-items: center; gap: 8px; font-size: 11px; cursor: pointer; padding: 6px 10px; background: #252526; border-radius: 4px;">
          <input type="checkbox" class="compare-checkbox" value="${sid}" ${checked}>
          <div style="overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">
            <strong>${sname}</strong> (${sid.substring(0, 8)})
          </div>
        </label>
      `;
    }).join("");
  },

  async runHeadToHeadComparison() {
    const checkboxes = Array.from(document.querySelectorAll(".compare-checkbox:checked")).map(cb => cb.value);
    const container = document.getElementById("compare-results-container");

    if (checkboxes.length < 2 || checkboxes.length > 5) {
      alert("Please select between 2 and 5 studies to compare.");
      return;
    }

    container.innerHTML = `<div class="card-section" style="padding: 20px; text-align: center; color: var(--vscode-fg-muted);">Running side-by-side comparison...</div>`;

    try {
      const res = await window.apiClient.compareStudies(checkboxes);
      const studies = res.studies || res.comparison || [];

      if (!studies.length) {
        container.innerHTML = `<div class="card-section" style="padding: 20px; color: var(--vscode-fg-muted);">No comparison data returned.</div>`;
        return;
      }

      container.innerHTML = `
        <div class="card-section" style="margin-top: 16px;">
          <div class="card-title"><span>Side-by-Side Comparison Matrix</span></div>
          <div class="table-responsive">
            <table class="vscode-table">
              <thead>
                <tr>
                  <th style="width: 180px;">Metric / Property</th>
                  ${studies.map(s => `<th><strong>${s.study_name || s.study_id.substring(0, 12)}</strong></th>`).join("")}
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td><strong>Model Architecture</strong></td>
                  ${studies.map(s => `<td><code>${s.model || 'yolov8m'}</code></td>`).join("")}
                </tr>
                <tr>
                  <td><strong>Best Objective (Fitness)</strong></td>
                  ${studies.map(s => `<td style="color: #10B981; font-weight: 600;">${s.best_fitness ? s.best_fitness.toFixed(4) : 'N/A'}</td>`).join("")}
                </tr>
                <tr>
                  <td><strong>Completed Trials</strong></td>
                  ${studies.map(s => `<td>${s.total_trials || 1}</td>`).join("")}
                </tr>
                <tr>
                  <td><strong>Assigned Node</strong></td>
                  ${studies.map(s => `<td><code>${s.destination_node || s.worker_ip || 'Cluster'}</code></td>`).join("")}
                </tr>
                <tr>
                  <td><strong>Dataset</strong></td>
                  ${studies.map(s => `<td style="font-size: 11px;">${s.dataset || 'N/A'}</td>`).join("")}
                </tr>
                <tr>
                  <td><strong>Execution Status</strong></td>
                  ${studies.map(s => `<td><span class="badge badge-green">${s.status || 'COMPLETED'}</span></td>`).join("")}
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      `;
    } catch (e) {
      container.innerHTML = `<div class="card-section" style="color: var(--vscode-btn-danger); padding: 16px;">Comparison error: ${e.message}</div>`;
    }
  },

  async exportStudyReport() {
    const studyId = document.getElementById("export-study-selector")?.value;
    const format = document.getElementById("export-format-selector")?.value || "markdown";

    if (!studyId) {
      alert("Please select a study to export.");
      return;
    }

    const study = this.historyData.find(h => (h.study_id || h.id) === studyId);
    let content = "";
    let mime = "text/plain";
    let filename = `${studyId}_report.${format === 'json' ? 'json' : 'md'}`;

    if (format === "json") {
      content = JSON.stringify(study, null, 2);
      mime = "application/json";
    } else {
      content = `# NeuralForge Training Study Report: ${study?.study_name || studyId}\n\n` +
        `- **Study ID:** \`${studyId}\`\n` +
        `- **Author:** ${study?.author || 'wisrovi'}\n` +
        `- **Assigned Node:** ${study?.destination_node || 'Cluster'}\n` +
        `- **Model:** ${study?.model || 'N/A'}\n` +
        `- **Dataset:** ${study?.dataset || 'N/A'}\n` +
        `- **Status:** ${study?.status || 'Completed'}\n` +
        `- **Started:** ${study?.start_time || 'N/A'}\n` +
        `- **Completed:** ${study?.completed_at || 'N/A'}\n\n` +
        `Generated by NeuralForge Cluster Admin v3.1.0\n`;
      mime = "text/markdown";
    }

    const previewArea = document.getElementById("export-preview-area");
    const previewCode = document.getElementById("export-preview-code");
    if (previewArea && previewCode) {
      previewArea.style.display = "block";
      previewCode.textContent = content;
    }

    // Trigger file download
    const blob = new Blob([content], { type: mime });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    window.workbench.logTerminal("SUCCESS", `Exported study report to ${filename}`);
  }
};
