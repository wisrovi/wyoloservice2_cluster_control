/**
 * Dispatch & Scheduler View (dispatch.yaml)
 */

window.ViewDispatch = {
  id: "dispatch",
  label: "Dispatch & Scheduler",
  icon: "🚀",
  file: "dispatch.yaml",
  category: "workloads",

  render() {
    return `
      <div class="view-header">
        <div class="view-title-group">
          <h1><span>🚀</span> Workload Dispatcher & Automated Scheduling</h1>
          <p>Submit training workloads to Celery and configure cluster-wide Day/Night throttling policies</p>
        </div>
        <div class="view-actions">
          <button class="btn btn-primary btn-sm" onclick="window.workbench.refreshCurrentView()">
            <span>🔄</span> Refresh Scheduler
          </button>
        </div>
      </div>

      <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
        <!-- Left: Quick Launch Form -->
        <div class="card-section">
          <div class="card-title"><span>⚡ Quick Launch Training Workload</span></div>
          <form id="quick-launch-form" onsubmit="event.preventDefault(); window.ViewDispatch.submitQuickLaunch();">
            <div class="form-group">
              <label class="form-label">Study / Project Name:</label>
              <input type="text" id="ql-study-name" class="form-control" placeholder="yolov8_defect_detection_v1" required>
            </div>
            <div class="form-group">
              <label class="form-label">Dataset Path (Samba CIFS):</label>
              <input type="text" id="ql-dataset-path" class="form-control" value="/wyolo/control_server/datasets/industrial_parts" required>
            </div>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
              <div class="form-group">
                <label class="form-label">Model Architecture:</label>
                <select id="ql-model" class="form-control">
                  <option value="yolov8n.pt">yolov8n.pt (Nano)</option>
                  <option value="yolov8s.pt">yolov8s.pt (Small)</option>
                  <option value="yolov8m.pt" selected>yolov8m.pt (Medium)</option>
                  <option value="yolov8l.pt">yolov8l.pt (Large)</option>
                  <option value="yolov8x.pt">yolov8x.pt (X-Large)</option>
                  <option value="yolo11m.pt">yolo11m.pt (YOLO11)</option>
                </select>
              </div>
              <div class="form-group">
                <label class="form-label">Epochs:</label>
                <input type="number" id="ql-epochs" class="form-control" value="100" min="1" max="1000">
              </div>
            </div>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
              <div class="form-group">
                <label class="form-label">Batch Size:</label>
                <input type="number" id="ql-batch" class="form-control" value="16" min="1" max="128">
              </div>
              <div class="form-group">
                <label class="form-label">Target Invoker Node:</label>
                <select id="ql-target-node" class="form-control">
                  <option value="">Auto-Assign (Least Loaded)</option>
                </select>
              </div>
            </div>
            <button type="submit" class="btn btn-primary" style="width: 100%; margin-top: 8px;">
              <span>🚀</span> Dispatch Workload to Celery
            </button>
          </form>
        </div>

        <!-- Right: Day / Night Scheduler Policy -->
        <div class="card-section">
          <div class="card-title">
            <span>🌙 Day / Night Throttling Policy</span>
            <span class="badge badge-blue" id="policy-current-mode">Normal Policy</span>
          </div>
          <p style="font-size: 12px; color: var(--vscode-fg-muted); margin-bottom: 14px;">
            Dynamic cluster resource scaling automatically caps training workload allocation during daytime office hours and uncaps maximum throughput during nighttime off-peak hours.
          </p>

          <div style="display: flex; flex-direction: column; gap: 12px;">
            <div style="padding: 12px; background: #2D2D2D; border-radius: 4px; border-left: 3px solid #007ACC;">
              <div style="font-weight: 600; font-size: 13px; color: var(--vscode-fg-bright);">☀️ Daytime Mode (08:00 - 20:00)</div>
              <div style="font-size: 11px; color: var(--vscode-fg-muted); margin-top: 2px;">
                Capped at 25% GPU / RAM usage to reserve compute for interactive developers and production inference.
              </div>
            </div>

            <div style="padding: 12px; background: #2D2D2D; border-radius: 4px; border-left: 3px solid #10B981;">
              <div style="font-weight: 600; font-size: 13px; color: var(--vscode-fg-bright);">🌙 Nighttime Mode (20:00 - 08:00)</div>
              <div style="font-size: 11px; color: var(--vscode-fg-muted); margin-top: 2px;">
                Uncapped at 95% GPU capacity for high-throughput batch training and Optuna hyperparameter sweeps.
              </div>
            </div>

            <div class="form-group" style="margin-top: 8px;">
              <label class="form-label">Manual Policy Override:</label>
              <div style="display: flex; gap: 8px;">
                <button class="btn btn-secondary" onclick="window.ViewDispatch.applyPolicy('day')">Force Day (25% Cap)</button>
                <button class="btn btn-secondary" onclick="window.ViewDispatch.applyPolicy('night')">Force Night (95% Max)</button>
                <button class="btn btn-secondary" onclick="window.ViewDispatch.applyPolicy('auto')">Auto Schedule</button>
              </div>
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
      const select = document.getElementById("ql-target-node");

      select.innerHTML = '<option value="">Auto-Assign (Least Loaded)</option>' +
        nodes.map(n => {
          const ip = n.ip || n.worker_ip;
          return `<option value="${ip}">${n.hostname || ip} (${ip})</option>`;
        }).join("");

      const policy = await window.apiClient.getSchedulerPolicy();
      if (policy && policy.mode) {
        document.getElementById("policy-current-mode").textContent = `${policy.mode.toUpperCase()} ACTIVE`;
      }
    } catch (_) {}
  },

  async submitQuickLaunch() {
    const studyName = document.getElementById("ql-study-name").value.trim();
    const datasetPath = document.getElementById("ql-dataset-path").value.trim();
    const model = document.getElementById("ql-model").value;
    const epochs = parseInt(document.getElementById("ql-epochs").value, 10);
    const batch = parseInt(document.getElementById("ql-batch").value, 10);
    const targetNode = document.getElementById("ql-target-node").value;

    const payload = {
      study_id: studyName,
      dataset_path: datasetPath,
      model: model,
      epochs: epochs,
      batch_size: batch,
      worker_ip: targetNode || null,
    };

    window.workbench.logTerminal("INFO", `Dispatching quick launch workload: ${studyName}...`);
    try {
      const res = await window.apiClient.quickLaunch(payload);
      window.workbench.logTerminal("SUCCESS", `Workload dispatched successfully: Task ID ${res.task_id || res.id}`);
      alert(`Workload '${studyName}' dispatched successfully!`);
      window.workbench.switchView("tasks");
    } catch (e) {
      window.workbench.logTerminal("ERROR", `Failed to dispatch workload: ${e.message}`);
      alert(`Dispatch failed: ${e.message}`);
    }
  },

  async applyPolicy(mode) {
    window.workbench.logTerminal("INFO", `Setting scheduler policy to: ${mode}...`);
    try {
      await window.apiClient.setSchedulerPolicy({ mode });
      window.workbench.logTerminal("SUCCESS", `Scheduler policy updated to: ${mode}`);
      document.getElementById("policy-current-mode").textContent = `${mode.toUpperCase()} ACTIVE`;
    } catch (e) {
      window.workbench.logTerminal("ERROR", `Failed to set scheduler policy: ${e.message}`);
      alert(`Failed to set policy: ${e.message}`);
    }
  }
};
