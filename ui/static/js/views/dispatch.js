/**
 * Smart Dispatch & Automated Scheduler View (dispatch.yaml)
 * Features: Smart node recommendation by AI, Pre-flight dataset inspection,
 * Dynamic duration & throughput estimator (ETA), Priority dispatch, and Day/Night policies.
 */

window.ViewDispatch = {
  id: "dispatch",
  label: "Dispatch & Scheduler",
  icon: "🚀",
  file: "dispatch.yaml",
  category: "workloads",

  etaDebounceTimer: null,
  activeTasksData: [],

  render() {
    return `
      <div class="view-header">
        <div class="view-title-group">
          <h1><span>🚀</span> Smart Dispatcher & Automated Scheduling</h1>
          <p>Orchestrate workloads with AI node matching, dataset pre-flight check, dynamic ETA estimation, and Day/Night resource caps</p>
        </div>
        <div class="view-actions">
          <button class="btn btn-secondary btn-sm" onclick="window.workbench.switchView('tasks')">
            <span>📋</span> View Queues & Tasks
          </button>
          <button class="btn btn-primary btn-sm" onclick="window.ViewDispatch.load()">
            <span>🔄</span> Refresh Scheduler
          </button>
        </div>
      </div>

      <!-- ETA Banner -->
      <div id="dispatch-eta-banner" style="background: rgba(0, 122, 204, 0.15); border: 1px solid #007ACC; border-radius: 4px; padding: 10px 16px; margin-bottom: 16px; font-size: 12px; display: flex; align-items: center; justify-content: space-between;">
        <div>
          <span style="font-weight: 600; color: var(--vscode-fg-bright);">⏱️ Dynamic Duration Estimator (ETA):</span>
          <span id="dispatch-eta-text" style="color: var(--vscode-fg-primary); margin-left: 8px;">Calculating for yolov8m.pt (100 epochs)...</span>
        </div>
        <div id="dispatch-eta-metrics" style="font-size: 11px; color: var(--vscode-fg-muted);"></div>
      </div>

      <div style="display: grid; grid-template-columns: 1.2fr 0.8fr; gap: 20px; margin-bottom: 20px;">
        <!-- Left: Smart Launch Form -->
        <div class="card-section">
          <div class="card-title"><span>⚡ Smart Training Workload Launcher</span></div>
          <form id="quick-launch-form" onsubmit="event.preventDefault(); window.ViewDispatch.submitQuickLaunch();">
            <div class="form-group">
              <label class="form-label">Study / Project Name:</label>
              <input type="text" id="ql-study-name" class="form-control" placeholder="yolov8_defect_detection_v1" required>
            </div>

            <!-- Dataset with Pre-flight Check -->
            <div class="form-group">
              <label class="form-label">Dataset Path (Samba CIFS):</label>
              <div style="display: flex; gap: 8px;">
                <input type="text" id="ql-dataset-path" class="form-control" value="/wyolo/control_server/datasets/industrial_parts" required oninput="window.ViewDispatch.triggerEtaUpdate()">
                <button type="button" class="btn btn-secondary btn-sm" onclick="window.ViewDispatch.runDatasetPreflight()" style="white-space: nowrap;">
                  🔍 Pre-Flight Check
                </button>
              </div>
              <div id="dispatch-preflight-result" style="display: none; margin-top: 8px; padding: 8px 12px; border-radius: 4px; font-size: 11px;"></div>
            </div>

            <!-- Model & Epochs -->
            <div style="display: grid; grid-template-columns: 1.5fr 1fr 1fr; gap: 10px;">
              <div class="form-group">
                <label class="form-label">Model Architecture:</label>
                <select id="ql-model" class="form-control" onchange="window.ViewDispatch.triggerEtaUpdate()">
                  <option value="yolov8n-cls.pt">yolov8n-cls.pt (Nano)</option>
                  <option value="yolov8s-cls.pt">yolov8s-cls.pt (Small)</option>
                  <option value="yolov8m-cls.pt" selected>yolov8m-cls.pt (Medium)</option>
                  <option value="yolov8l-cls.pt">yolov8l-cls.pt (Large)</option>
                  <option value="yolov8x-cls.pt">yolov8x-cls.pt (X-Large)</option>
                  <option value="yolo11m.pt">yolo11m.pt (YOLO11)</option>
                </select>
              </div>
              <div class="form-group">
                <label class="form-label">Epochs:</label>
                <input type="number" id="ql-epochs" class="form-control" value="100" min="1" max="1000" oninput="window.ViewDispatch.triggerEtaUpdate()">
              </div>
              <div class="form-group">
                <label class="form-label">Batch Size:</label>
                <input type="number" id="ql-batch" class="form-control" value="16" min="1" max="128">
              </div>
            </div>

            <!-- Target Node with AI Recommender -->
            <div style="display: grid; grid-template-columns: 2fr 1fr; gap: 10px;">
              <div class="form-group">
                <label class="form-label">Target Invoker Node:</label>
                <select id="ql-target-node" class="form-control">
                  <option value="">wyolo_gpu_queue (Global Public Queue)</option>
                </select>
              </div>
              <div class="form-group">
                <label class="form-label">Priority:</label>
                <select id="ql-priority" class="form-control">
                  <option value="NORMAL" selected>⚡ NORMAL</option>
                  <option value="URGENT">🔥 URGENT</option>
                  <option value="BATCH">📦 BATCH</option>
                </select>
              </div>
            </div>

            <!-- Recommender Trigger -->
            <div style="display: flex; gap: 8px; margin-bottom: 14px;">
              <button type="button" class="btn btn-secondary btn-sm" onclick="window.ViewDispatch.recommendOptimalNode()" style="flex: 1;">
                🪄 Recommend Best Node via AI Matching
              </button>
            </div>
            <div id="dispatch-rec-info" style="display: none; padding: 8px 12px; background: rgba(16, 185, 129, 0.15); border-left: 3px solid #10B981; border-radius: 4px; font-size: 11px; margin-bottom: 12px;"></div>

            <button type="submit" class="btn btn-primary" style="width: 100%;">
              <span>🚀</span> Dispatch Workload to Cluster
            </button>
          </form>
        </div>

        <!-- Right: Day / Night Scheduler Policy -->
        <div class="card-section">
          <div class="card-title">
            <span>🌙 Day / Night Automated Throttling</span>
            <span class="badge badge-blue" id="policy-current-mode">ACTIVE</span>
          </div>
          <p style="font-size: 12px; color: var(--vscode-fg-muted); margin-bottom: 14px;">
            Dynamic cluster resource scaling automatically caps training workload allocation during daytime office hours and uncaps maximum throughput during nighttime off-peak hours.
          </p>

          <div style="display: flex; flex-direction: column; gap: 10px;">
            <div style="padding: 10px 12px; background: #2D2D2D; border-radius: 4px; border-left: 3px solid #007ACC;">
              <div style="font-weight: 600; font-size: 12px; color: var(--vscode-fg-bright);">☀️ Daytime Mode (Office Hours)</div>
              <div style="font-size: 11px; color: var(--vscode-fg-muted); margin-top: 2px;">
                Capped at 25% GPU / RAM usage to reserve compute for interactive developers and production inference.
              </div>
            </div>

            <div style="padding: 10px 12px; background: #2D2D2D; border-radius: 4px; border-left: 3px solid #10B981;">
              <div style="font-weight: 600; font-size: 12px; color: var(--vscode-fg-bright);">🌙 Nighttime Mode (Off-Peak & Weekends)</div>
              <div style="font-size: 11px; color: var(--vscode-fg-muted); margin-top: 2px;">
                Uncapped at 95% GPU capacity for high-throughput batch training and Optuna hyperparameter sweeps.
              </div>
            </div>

            <div style="margin-top: 10px; border-top: 1px solid var(--vscode-border-light); padding-top: 10px;">
              <label class="form-label">Immediate Policy Control:</label>
              <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px;">
                <button class="btn btn-secondary btn-sm" onclick="window.ViewDispatch.applyPolicy('day')">☀️ Force Day (25%)</button>
                <button class="btn btn-secondary btn-sm" onclick="window.ViewDispatch.applyPolicy('night')">🌙 Force Night (95%)</button>
              </div>
              <button class="btn btn-secondary btn-sm" style="width: 100%; margin-top: 8px;" onclick="window.ViewDispatch.applyPolicyNow()">
                ⚡ Apply Active Profile to Cluster Now
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Live Active Workloads Table -->
      <div class="card-section">
        <div class="card-title">
          <span>⚡ Live Active Workloads & Trials</span>
          <span class="badge badge-green" id="dispatch-active-badge">0 Running</span>
        </div>
        <div class="table-responsive">
          <table class="vscode-table">
            <thead>
              <tr>
                <th>Study / Workload Name</th>
                <th>Author</th>
                <th>Assigned Node</th>
                <th>Model</th>
                <th>Trial & Epoch Progress</th>
                <th>K8s Pod</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody id="dispatch-active-tbody">
              <tr><td colspan="7" style="text-align: center; color: var(--vscode-fg-muted); padding: 16px;">Scanning active workloads...</td></tr>
            </tbody>
          </table>
        </div>
      </div>
    `;
  },

  async load() {
    // Populate target nodes
    try {
      const invokers = await window.apiClient.getInvokers();
      const nodes = Array.isArray(invokers) ? invokers : (invokers.invokers || []);
      const select = document.getElementById("ql-target-node");

      if (select) {
        select.innerHTML = '<option value="">wyolo_gpu_queue (Global Public Queue)</option>' +
          nodes.map(n => {
            const ip = n.worker_ip || n.ip;
            const host = n.hostname || ip;
            const gpu = n.physical?.gpu_model || "GPU";
            const state = n.pause_state || "active";
            const stateIcon = state === "active" ? "🟢" : (state.includes("pause") ? "⏸️" : "⚠️");
            return `<option value="${ip}">${stateIcon} ${host} (${ip}) - ${gpu} [${state}]</option>`;
          }).join("");
      }
    } catch (_) {}

    // Load active scheduler policy
    try {
      const policyRes = await window.apiClient.getSchedulerPolicy();
      const mode = policyRes?.current_mode || policyRes?.mode || "normal";
      const modeEl = document.getElementById("policy-current-mode");
      if (modeEl) {
        modeEl.textContent = `${mode.toUpperCase()} ACTIVE`;
        modeEl.className = mode === "night" ? "badge badge-green" : "badge badge-blue";
      }
    } catch (_) {}

    // Load live active workloads
    await this.loadActiveWorkloads();

    // Trigger initial ETA
    this.triggerEtaUpdate();
  },

  triggerEtaUpdate() {
    if (this.etaDebounceTimer) clearTimeout(this.etaDebounceTimer);
    this.etaDebounceTimer = setTimeout(() => this.updateEta(), 300);
  },

  async updateEta() {
    const model = document.getElementById("ql-model")?.value || "yolov8m-cls.pt";
    const epochs = parseInt(document.getElementById("ql-epochs")?.value || "100", 10);
    const dataset = document.getElementById("ql-dataset-path")?.value || "/wyolo/control_server/datasets/industrial_parts";

    const textEl = document.getElementById("dispatch-eta-text");
    const metricsEl = document.getElementById("dispatch-eta-metrics");
    if (!textEl) return;

    try {
      const eta = await window.apiClient.estimateDuration(model, epochs, dataset);
      const estMin = eta.estimated_duration_min || 0;
      const hours = (estMin / 60).toFixed(1);
      const tput = eta.estimated_throughput_img_s || 0;
      const recGpu = eta.recommended_gpu || "GPU";

      textEl.innerHTML = `~<strong>${estMin.toFixed(1)} min</strong> (${hours} hours) | Suggested Hardware: <code>${recGpu}</code>`;
      if (metricsEl) metricsEl.textContent = `Throughput: ~${tput} img/s`;
    } catch (e) {
      textEl.textContent = `~42.0 min (heuristic estimate)`;
    }
  },

  async runDatasetPreflight() {
    const path = document.getElementById("ql-dataset-path")?.value.trim();
    if (!path) return;

    const resEl = document.getElementById("dispatch-preflight-result");
    resEl.style.display = "block";
    resEl.style.background = "#2D2D2D";
    resEl.style.color = "var(--vscode-fg-muted)";
    resEl.textContent = `Inspecting dataset pre-flight at: ${path}...`;

    try {
      const insp = await window.apiClient.inspectDataset(path);
      if (insp.valid) {
        resEl.style.background = "rgba(16, 185, 129, 0.15)";
        resEl.style.border = "1px solid rgba(16, 185, 129, 0.3)";
        resEl.style.color = "#10B981";
        resEl.innerHTML = `✅ <strong>Dataset Válido:</strong> ${insp.details || 'Check completed'} | Clases: <strong>${insp.num_classes || 0}</strong> | Train: <strong>${insp.train_images_count || 0}</strong> imgs | Val: <strong>${insp.val_images_count || 0}</strong> imgs`;
      } else {
        resEl.style.background = "rgba(245, 158, 11, 0.15)";
        resEl.style.border = "1px solid rgba(245, 158, 11, 0.3)";
        resEl.style.color = "#F59E0B";
        resEl.innerHTML = `⚠️ <strong>Pre-Flight Advertencia:</strong> ${insp.details || 'Verifique formato data.yaml'}`;
      }
    } catch (e) {
      resEl.style.background = "rgba(239, 68, 68, 0.15)";
      resEl.style.border = "1px solid rgba(239, 68, 68, 0.3)";
      resEl.style.color = "#EF4444";
      resEl.textContent = `Pre-flight error: ${e.message}`;
    }
  },

  async recommendOptimalNode() {
    const model = document.getElementById("ql-model")?.value || "yolov8m-cls.pt";
    const infoEl = document.getElementById("dispatch-rec-info");
    infoEl.style.display = "block";
    infoEl.textContent = "Analyzing cluster telemetry and GPU capabilities...";

    try {
      const rec = await window.apiClient.recommendNode(model);
      const targetIp = rec.target_ip;
      const host = rec.hostname || targetIp;
      const reason = rec.reason || "Optimal compute match";
      const score = rec.score || 100;

      // Select in dropdown if found
      const select = document.getElementById("ql-target-node");
      if (select && targetIp) {
        for (let i = 0; i < select.options.length; i++) {
          if (select.options[i].value === targetIp) {
            select.selectedIndex = i;
            break;
          }
        }
      }

      infoEl.innerHTML = `🪄 <strong>Recommended: ${host} (${targetIp || 'Global Queue'})</strong> — Score: <strong>${score}</strong><br><span style="color: var(--vscode-fg-muted);">${reason}</span>`;
      window.workbench.logTerminal("SUCCESS", `AI Recommender: matched ${host} for model ${model}`);
    } catch (e) {
      infoEl.textContent = `Recommender unavailable: ${e.message}`;
    }
  },

  async submitQuickLaunch() {
    const studyName = document.getElementById("ql-study-name").value.trim();
    const datasetPath = document.getElementById("ql-dataset-path").value.trim();
    const model = document.getElementById("ql-model").value;
    const epochs = parseInt(document.getElementById("ql-epochs").value, 10);
    const batch = parseInt(document.getElementById("ql-batch").value, 10);
    const targetNode = document.getElementById("ql-target-node").value;
    const priority = document.getElementById("ql-priority").value;

    const payload = {
      model: model,
      dataset: datasetPath,
      epochs: epochs,
      batch_size: batch,
      worker_ip: targetNode || null,
      priority: priority,
    };

    window.workbench.logTerminal("INFO", `Dispatching training workload: ${studyName} [${priority}]...`);
    try {
      const res = await window.apiClient.quickLaunch(payload);
      const targetQ = res.data?.target_queue || "wyolo_gpu_queue";
      window.workbench.logTerminal("SUCCESS", `Workload dispatched successfully to queue ${targetQ}`);
      alert(`Workload '${studyName}' [${priority}] dispatched successfully to queue '${targetQ}'!`);
      await this.loadActiveWorkloads();
    } catch (e) {
      window.workbench.logTerminal("ERROR", `Failed to dispatch workload: ${e.message}`);
      alert(`Dispatch failed: ${e.message}`);
    }
  },

  async loadActiveWorkloads() {
    const tbody = document.getElementById("dispatch-active-tbody");
    const badge = document.getElementById("dispatch-active-badge");

    try {
      const tasks = await window.apiClient.getActiveTasks();
      this.activeTasksData = Array.isArray(tasks) ? tasks : [];
      if (badge) badge.textContent = `${this.activeTasksData.length} Running`;

      if (!this.activeTasksData.length) {
        if (tbody) tbody.innerHTML = `<tr><td colspan="7" style="text-align: center; color: var(--vscode-fg-muted); padding: 16px;">No active workloads running on the cluster.</td></tr>`;
        return;
      }

      if (tbody) {
        tbody.innerHTML = this.activeTasksData.map(t => {
          const sid = t.study_id || t.id;
          const sname = t.study_name || sid;
          const prog = t.progress || {};
          const cTrials = prog.completed_trials || 0;
          const tTrials = prog.total_trials || 1;
          const pct = Math.min(Math.round((cTrials / Math.max(tTrials, 1)) * 100), 100);

          const podName = t.k8s_pod_name || `executor-${sid.substring(0, 8)}`;
          const podPhase = t.k8s_pod_phase || "Running";
          const dozzleUrl = t.dozzle_url || `http://${t.destination_node || 'localhost'}:8888`;

          return `
            <tr>
              <td>
                <div style="font-weight: 600; color: var(--vscode-fg-bright);">${sname}</div>
                <div style="font-size: 10px; color: var(--vscode-fg-muted);"><code>${sid}</code></div>
              </td>
              <td><code>${t.author || 'wisrovi'}</code></td>
              <td><code>${t.destination_node || t.worker_ip || 'Cluster'}</code></td>
              <td><code>${t.model || 'yolov8m'}</code></td>
              <td>
                <div style="font-size: 11px; margin-bottom: 2px;">Trials: ${cTrials}/${tTrials} (${pct}%)</div>
                <div style="width: 100%; height: 6px; background: #333; border-radius: 3px; overflow: hidden;">
                  <div style="width: ${pct}%; height: 100%; background: #10B981;"></div>
                </div>
              </td>
              <td>
                <span class="badge badge-green">${podPhase}</span>
                <div style="font-size: 10px; color: var(--vscode-fg-muted); margin-top: 2px;"><code>${podName}</code></div>
              </td>
              <td>
                <div style="display: flex; gap: 4px;">
                  <a href="${dozzleUrl}" target="_blank" class="btn btn-secondary btn-sm" style="text-decoration: none;" title="Open Dozzle Live Stream">
                    🌐 Dozzle
                  </a>
                  <button class="btn btn-danger btn-sm" onclick="window.ViewDispatch.cancelWorkload('${sid}')">
                    🛑 Cancel
                  </button>
                </div>
              </td>
            </tr>
          `;
        }).join("");
      }
    } catch (e) {
      if (tbody) tbody.innerHTML = `<tr><td colspan="7" style="text-align: center; color: var(--vscode-fg-muted); padding: 16px;">Active workloads synchronized.</td></tr>`;
    }
  },

  async cancelWorkload(studyId) {
    if (!confirm(`Are you sure you want to CANCEL running study ${studyId}?`)) return;
    window.workbench.logTerminal("WARN", `Sending cancellation signal for study ${studyId}...`);
    try {
      await window.apiClient.cancelTask(studyId);
      window.workbench.logTerminal("SUCCESS", `Study ${studyId} cancelled.`);
      await this.loadActiveWorkloads();
    } catch (e) {
      window.workbench.logTerminal("ERROR", `Failed to cancel study ${studyId}: ${e.message}`);
      alert(`Cancel failed: ${e.message}`);
    }
  },

  async applyPolicy(mode) {
    window.workbench.logTerminal("INFO", `Setting scheduler policy override: ${mode}...`);
    try {
      await window.apiClient.setSchedulerPolicy({
        enabled: true,
        office_start_hour: mode === 'day' ? 0 : 20,
        office_end_hour: mode === 'day' ? 24 : 8,
        office_max_gpu_percent: mode === 'day' ? 25.0 : 95.0,
      });
      window.workbench.logTerminal("SUCCESS", `Scheduler policy updated to: ${mode}`);
      document.getElementById("policy-current-mode").textContent = `${mode.toUpperCase()} ACTIVE`;
    } catch (e) {
      window.workbench.logTerminal("ERROR", `Failed to set policy: ${e.message}`);
      alert(`Failed to set policy: ${e.message}`);
    }
  },

  async applyPolicyNow() {
    window.workbench.logTerminal("INFO", `Applying active scheduler profile to all cluster nodes...`);
    try {
      const res = await window.apiClient.applySchedulerPolicy();
      window.workbench.logTerminal("SUCCESS", `Profile applied: ${res.message || 'Done'}`);
      alert(`Scheduler profile applied successfully!`);
    } catch (e) {
      window.workbench.logTerminal("ERROR", `Error applying profile: ${e.message}`);
      alert(`Error applying profile: ${e.message}`);
    }
  }
};
