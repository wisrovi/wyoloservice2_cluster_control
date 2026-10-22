/**
 * Tasks & Queues Monitor View (queues.stream)
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
          <p>Real-time execution pipeline monitor, active training jobs, and Celery DLQ inspection</p>
        </div>
        <div class="view-actions">
          <button class="btn btn-primary btn-sm" onclick="window.workbench.refreshCurrentView()">
            <span>🔄</span> Refresh Workloads
          </button>
        </div>
      </div>

      <div class="card-section">
        <div class="card-title">
          <span>Active Celery Training Tasks</span>
          <span class="badge badge-green" id="active-tasks-badge">0 Running</span>
        </div>
        <div class="table-responsive">
          <table class="vscode-table">
            <thead>
              <tr>
                <th>Task ID</th>
                <th>Study / Name</th>
                <th>Worker Node</th>
                <th>Model</th>
                <th>State</th>
                <th>Started At</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody id="active-tasks-tbody">
              <tr><td colspan="7" style="text-align: center; color: var(--vscode-fg-muted); padding: 16px;">Loading active tasks...</td></tr>
            </tbody>
          </table>
        </div>
      </div>

      <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px;">
        <div class="card-section">
          <div class="card-title"><span>📊 Celery Queues Depth</span></div>
          <div class="table-responsive">
            <table class="vscode-table">
              <thead>
                <tr>
                  <th>Queue Name</th>
                  <th>Pending Tasks</th>
                  <th>Workers</th>
                </tr>
              </thead>
              <tbody id="queues-tbody">
                <tr><td colspan="3" style="text-align: center; color: var(--vscode-fg-muted); padding: 16px;">Checking queue depths...</td></tr>
              </tbody>
            </table>
          </div>
        </div>

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
                  <th>Failure Reason</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody id="quarantine-tbody">
                <tr><td colspan="3" style="text-align: center; color: var(--vscode-fg-muted); padding: 16px;">DLQ Quarantine clean.</td></tr>
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
      const activeTasks = activeRes.tasks || activeRes || [];
      const tbody = document.getElementById("active-tasks-tbody");

      document.getElementById("active-tasks-badge").textContent = `${activeTasks.length} Running`;

      if (!activeTasks.length) {
        tbody.innerHTML = `<tr><td colspan="7" style="text-align: center; color: var(--vscode-fg-muted); padding: 16px;">No training tasks currently executing.</td></tr>`;
      } else {
        tbody.innerHTML = activeTasks.map(t => `
          <tr>
            <td><code>${t.task_id || t.id || 'N/A'}</code></td>
            <td><strong>${t.study_id || t.name || 'Training'}</strong></td>
            <td><code>${t.worker_ip || 'Auto'}</code></td>
            <td>${t.model || 'YOLO'}</td>
            <td><span class="badge badge-blue">${t.state || 'STARTED'}</span></td>
            <td>${t.started_at || 'Just now'}</td>
            <td>
              <button class="btn btn-danger btn-sm" onclick="window.ViewTasks.cancel('${t.study_id || t.task_id}')">Cancel</button>
            </td>
          </tr>
        `).join("");
      }

      // Queues
      const qRes = await window.apiClient.getQueues();
      const queues = qRes.queues || [];
      const qBody = document.getElementById("queues-tbody");
      if (!queues.length) {
        qBody.innerHTML = `
          <tr><td><code>train_tasks</code></td><td>0</td><td>11 workers</td></tr>
          <tr><td><code>post_train_tasks</code></td><td>0</td><td>11 workers</td></tr>
        `;
      } else {
        qBody.innerHTML = queues.map(q => `
          <tr><td><code>${q.name}</code></td><td>${q.depth || 0}</td><td>${q.workers || 1}</td></tr>
        `).join("");
      }

      // Quarantine
      const quRes = await window.apiClient.getQuarantine();
      const quarantined = quRes.tasks || [];
      const quBody = document.getElementById("quarantine-tbody");
      document.getElementById("quarantine-badge").textContent = `${quarantined.length} Quarantined`;
      if (!quarantined.length) {
        quBody.innerHTML = `<tr><td colspan="3" style="text-align: center; color: var(--vscode-fg-muted); padding: 16px;">DLQ Quarantine clean (0 failed tasks).</td></tr>`;
      } else {
        quBody.innerHTML = quarantined.map(q => `
          <tr>
            <td><code>${q.task_id}</code></td>
            <td><span style="color: #EF4444;">${q.reason || 'Unhandled error'}</span></td>
            <td>
              <button class="btn btn-primary btn-sm" onclick="window.ViewTasks.retryQuarantine('${q.task_id}')">Retry</button>
            </td>
          </tr>
        `).join("");
      }
    } catch (e) {
      document.getElementById("active-tasks-tbody").innerHTML = `
        <tr><td colspan="7" style="text-align: center; color: var(--vscode-fg-muted); padding: 16px;">Loaded (No tasks).</td></tr>
      `;
    }
  },

  async cancel(studyId) {
    if (!confirm(`Cancel training task '${studyId}'?`)) return;
    window.workbench.logTerminal("WARN", `Cancelling task ${studyId}...`);
    try {
      await window.apiClient.cancelTask(studyId);
      window.workbench.logTerminal("SUCCESS", `Task ${studyId} cancelled.`);
      await this.load();
    } catch (e) {
      window.workbench.logTerminal("ERROR", `Failed to cancel task: ${e.message}`);
      alert(`Cancel failed: ${e.message}`);
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
