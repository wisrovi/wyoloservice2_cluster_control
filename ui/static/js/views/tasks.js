/**
 * Tasks & Queues Monitor View (queues.stream)
 * Real-time active trials, Celery queues, Optuna sweeps, and DLQ Quarantine
 */

window.ViewTasks = {
  id: "tasks",
  label: "Tasks & Queues",
  icon: "📋",
  file: "queues.stream",
  category: "workloads",

  render() {
    return `
      <div class="view-header">
        <div class="view-title-group">
          <h1><span>📋</span> Workload Tasks, Celery Queues & Quarantine</h1>
          <p>Real-time execution pipeline monitor, active training jobs, Celery backlog, and DLQ quarantine inspector</p>
        </div>
        <div class="view-actions">
          <button class="btn btn-secondary btn-sm" onclick="window.workbench.switchView('dispatch')">
            <span>⚡</span> Dispatch Workload
          </button>
          <button class="btn btn-primary btn-sm" onclick="window.workbench.refreshCurrentView()">
            <span>🔄</span> Refresh Workloads
          </button>
        </div>
      </div>

      <!-- Active Tasks Section -->
      <div class="card-section" style="margin-bottom: 20px;">
        <div class="card-title">
          <span>⚡ Active Training Jobs & Live Trials</span>
          <span class="badge badge-blue" id="active-tasks-badge">0 Running</span>
        </div>
        <div class="table-responsive">
          <table class="vscode-table">
            <thead>
              <tr>
                <th>Study / Workload Name</th>
                <th>Author</th>
                <th>Assigned Node</th>
                <th>Model</th>
                <th>Epoch / Trial Progress</th>
                <th>K8s Pod & Phase</th>
                <th>Logs & Diagnostics</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody id="active-tasks-tbody">
              <tr><td colspan="8" style="text-align: center; color: var(--vscode-fg-muted); padding: 16px;">Loading active tasks...</td></tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Queues and Quarantine Grid -->
      <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px;">
        <!-- Celery Queues -->
        <div class="card-section">
          <div class="card-title">
            <span>📊 Celery Queues & Backlog Depth</span>
            <span class="badge badge-green" id="queues-summary-badge">Healthy</span>
          </div>
          <div class="table-responsive">
            <table class="vscode-table">
              <thead>
                <tr>
                  <th>Queue Name</th>
                  <th>Type</th>
                  <th>Backlog Depth</th>
                  <th>Target Workers</th>
                </tr>
              </thead>
              <tbody id="queues-tbody">
                <tr><td colspan="4" style="text-align: center; color: var(--vscode-fg-muted); padding: 16px;">Checking queue depths...</td></tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- DLQ Quarantine -->
        <div class="card-section">
          <div class="card-title">
            <span>☣️ Dead Letter Queue (DLQ) Quarantine</span>
            <span class="badge badge-amber" id="quarantine-badge">0 Quarantined</span>
          </div>
          <div class="table-responsive">
            <table class="vscode-table">
              <thead>
                <tr>
                  <th>Task ID</th>
                  <th>Study</th>
                  <th>Failure Reason</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody id="quarantine-tbody">
                <tr><td colspan="4" style="text-align: center; color: var(--vscode-fg-muted); padding: 16px;">DLQ Quarantine clean (0 poisonous tasks).</td></tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    `;
  },

  async load() {
    try {
      const activeRes = await window.apiClient.getActiveTasks();
      const activeTasks = Array.isArray(activeRes) ? activeRes : (activeRes.tasks || []);
      const tbody = document.getElementById("active-tasks-tbody");

      document.getElementById("active-tasks-badge").textContent = `${activeTasks.length} Running`;

      if (!activeTasks.length) {
        tbody.innerHTML = `<tr><td colspan="8" style="text-align: center; color: var(--vscode-fg-muted); padding: 16px;">No training workloads currently executing.</td></tr>`;
      } else {
        tbody.innerHTML = activeTasks.map(t => {
          const studyName = t.study_name || t.study_id || "Training";
          const author = t.author || "Operator";
          const nodeStr = t.destination_node || t.worker_ip || "Auto";
          const model = t.model || "yolo";
          const trialsProg = t.progress ? `${t.progress.completed_trials || 0} / ${t.progress.total_trials || 0} trials` : "1 trial";
          const epochsProg = t.epoch_progress ? `${t.epoch_progress.current_epoch || 0}/${t.epoch_progress.total_epochs || 300} epochs` : "";
          const podName = t.k8s_pod_name || "Pod";
          const podPhase = t.k8s_pod_phase || "Running";
          const dozzleUrl = t.dozzle_url || (t.worker_ip ? `http://${t.worker_ip}:8888` : null);

          let dozzleBtn = dozzleUrl
            ? `<a href="${dozzleUrl}" target="_blank" class="btn btn-secondary btn-sm" style="text-decoration: none;">📺 Dozzle</a>`
            : "";

          return `
            <tr>
              <td>
                <div style="font-weight: 600;">${escapeHtml(studyName)}</div>
                <div style="font-size: 10px; color: var(--vscode-fg-muted); font-family: var(--vscode-mono-family);">${escapeHtml(t.study_id || '')}</div>
              </td>
              <td><span style="color: var(--vscode-fg-muted); font-size: 12px;">${escapeHtml(author)}</span></td>
              <td><code>${escapeHtml(nodeStr)}</code></td>
              <td><span class="badge badge-blue">${escapeHtml(model)}</span></td>
              <td>
                <div style="font-weight: 600; color: #10B981;">${escapeHtml(trialsProg)}</div>
                <div style="font-size: 11px; color: var(--vscode-fg-muted);">${escapeHtml(epochsProg)}</div>
              </td>
              <td>
                <span class="badge ${podPhase === 'Running' ? 'badge-green' : 'badge-amber'}">
                  ${escapeHtml(podName)} (${escapeHtml(podPhase)})
                </span>
              </td>
              <td>
                <div style="display: flex; gap: 4px;">
                  ${dozzleBtn}
                  <button class="btn btn-secondary btn-sm" onclick="window.ViewTasks.viewLogs('${t.study_id}')">📜 Logs</button>
                </div>
              </td>
              <td>
                <button class="btn btn-danger btn-sm" onclick="window.ViewTasks.cancel('${t.study_id}')">
                  🛑 Cancel
                </button>
              </td>
            </tr>
          `;
        }).join("");
      }

      // Queues
      try {
        const qRes = await window.apiClient.getQueues();
        const qBody = document.getElementById("queues-tbody");
        const globalQueues = qRes.global_queues || {};
        const nodeQueues = qRes.node_queues || {};

        let queueRows = [];
        for (const [qName, depth] of Object.entries(globalQueues)) {
          queueRows.push(`
            <tr>
              <td><code>${escapeHtml(qName)}</code></td>
              <td><span class="badge badge-blue">Global Public</span></td>
              <td><strong style="color: ${depth > 0 ? '#F59E0B' : 'inherit'};">${depth}</strong></td>
              <td>All Online Nodes</td>
            </tr>
          `);
        }

        for (const [qName, depth] of Object.entries(nodeQueues)) {
          queueRows.push(`
            <tr>
              <td><code>${escapeHtml(qName)}</code></td>
              <td><span class="badge badge-green">Private Node</span></td>
              <td><strong style="color: ${depth > 0 ? '#F59E0B' : 'inherit'};">${depth}</strong></td>
              <td>Node ${escapeHtml(qName)}</td>
            </tr>
          `);
        }

        if (!queueRows.length) {
          queueRows.push(`
            <tr><td><code>wyolo_gpu_queue</code></td><td><span class="badge badge-blue">Global Public</span></td><td>0</td><td>13 workers</td></tr>
            <tr><td><code>gpus_high</code></td><td><span class="badge badge-blue">Priority High</span></td><td>0</td><td>13 workers</td></tr>
            <tr><td><code>gpus_medium</code></td><td><span class="badge badge-blue">Priority Normal</span></td><td>0</td><td>13 workers</td></tr>
            <tr><td><code>gpus_low</code></td><td><span class="badge badge-blue">Priority Low</span></td><td>0</td><td>13 workers</td></tr>
          `);
        }

        qBody.innerHTML = queueRows.join("");
      } catch (_) {}

      // Quarantine
      try {
        const quRes = await window.apiClient.getQuarantine();
        const quarantined = Array.isArray(quRes) ? quRes : (quRes.tasks || []);
        const quBody = document.getElementById("quarantine-tbody");
        document.getElementById("quarantine-badge").textContent = `${quarantined.length} Quarantined`;

        if (!quarantined.length) {
          quBody.innerHTML = `<tr><td colspan="4" style="text-align: center; color: var(--vscode-fg-muted); padding: 16px;">DLQ Quarantine clean (0 failed tasks).</td></tr>`;
        } else {
          quBody.innerHTML = quarantined.map(q => `
            <tr>
              <td><code>${escapeHtml(q.task_id || q.id)}</code></td>
              <td><strong>${escapeHtml(q.study_name || q.study_id || 'Unknown')}</strong></td>
              <td><span style="color: #EF4444; font-size: 11px;">${escapeHtml(q.reason || q.error || 'Fatal Error')}</span></td>
              <td>
                <button class="btn btn-primary btn-sm" onclick="window.ViewTasks.retryQuarantine('${q.task_id || q.id}')">Retry</button>
              </td>
            </tr>
          `).join("");
        }
      } catch (_) {}

    } catch (e) {
      document.getElementById("active-tasks-tbody").innerHTML = `
        <tr><td colspan="8" style="text-align: center; color: var(--vscode-btn-danger); padding: 16px;">
          Failed to load workloads: ${e.message}
        </td></tr>
      `;
    }
  },

  async cancel(studyId) {
    if (!confirm(`Cancel training workload '${studyId}'? This will terminate running containers across invokers.`)) return;
    window.workbench.logTerminal("WARN", `Cancelling training workload ${studyId}...`);
    try {
      await window.apiClient.cancelTask(studyId);
      window.workbench.logTerminal("SUCCESS", `Workload ${studyId} cancelled.`);
      await this.load();
    } catch (e) {
      window.workbench.logTerminal("ERROR", `Failed to cancel workload: ${e.message}`);
      alert(`Cancel failed: ${e.message}`);
    }
  },

  async viewLogs(studyId) {
    window.workbench.logTerminal("INFO", `Fetching execution logs for study ${studyId}...`);
    try {
      const logs = await window.apiClient.request(`/api/v1/tasks/${encodeURIComponent(studyId)}/logs`);
      const logText = logs.logs || logs.output || JSON.stringify(logs, null, 2);
      window.workbench.logTerminal("INFO", `--- LOGS FOR ${studyId} ---`);
      logText.split("\n").slice(-25).forEach(line => {
        if (line.trim()) window.workbench.logTerminal("INFO", line);
      });
      window.workbench.logTerminal("INFO", `--- END LOGS ---`);
      if (window.workbench.panelCollapsed) {
        window.workbench.toggleBottomPanel();
      }
    } catch (e) {
      window.workbench.logTerminal("ERROR", `Failed to retrieve logs: ${e.message}`);
    }
  },

  async retryQuarantine(taskId) {
    window.workbench.logTerminal("INFO", `Retrying quarantined task ${taskId}...`);
    try {
      await window.apiClient.retryQuarantine(taskId);
      window.workbench.logTerminal("SUCCESS", `Task ${taskId} re-queued.`);
      await this.load();
    } catch (e) {
      window.workbench.logTerminal("ERROR", `Retry failed: ${e.message}`);
    }
  }
};
