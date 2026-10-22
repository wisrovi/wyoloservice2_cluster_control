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

      <!-- Detailed Queued Workloads Section -->
      <div class="card-section" style="margin-bottom: 20px;">
        <div class="card-title">
          <span>⏳ Detailed Waiting Queue & Celery Backlog (Tareas en Espera)</span>
          <span class="badge badge-amber" id="queued-tasks-badge">0 Queued</span>
        </div>
        <div class="table-responsive">
          <table class="vscode-table">
            <thead>
              <tr>
                <th>Study / Workload Name</th>
                <th>Author</th>
                <th>Target Queue / Node</th>
                <th>Model</th>
                <th>Dataset Path</th>
                <th>Priority</th>
                <th>Queued At</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody id="queued-tasks-tbody">
              <tr><td colspan="8" style="text-align: center; color: var(--vscode-fg-muted); padding: 16px;">Loading queued tasks...</td></tr>
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

      // Queues & Backlog
      try {
        const qRes = await window.apiClient.getQueues();
        const queuedTasks = qRes.tasks || [];
        const totalQueued = qRes.total_queued !== undefined ? qRes.total_queued : queuedTasks.length;

        // Render Detailed Queued Tasks Table
        const qBadge = document.getElementById("queued-tasks-badge");
        if (qBadge) qBadge.textContent = `${totalQueued} Queued`;

        const qTasksBody = document.getElementById("queued-tasks-tbody");
        if (qTasksBody) {
          if (!queuedTasks.length) {
            qTasksBody.innerHTML = `<tr><td colspan="8" style="text-align: center; color: var(--vscode-fg-muted); padding: 16px;">No workloads currently waiting in queues.</td></tr>`;
          } else {
            qTasksBody.innerHTML = queuedTasks.map(t => {
              const studyName = t.study_name || t.task_id || "Queued Job";
              const author = t.author || "Unknown";
              const qName = t.queue_name || "wyolo_gpu_queue";
              const isNodeQueue = qName.includes(".") || qName.startsWith("192.") || qName.startsWith("worker");
              const targetBadge = isNodeQueue
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
                  <td>${targetBadge}</td>
                  <td><span class="badge badge-blue">${escapeHtml(model)}</span></td>
                  <td style="max-width: 200px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;" title="${escapeHtml(dataset)}">
                    <code>${escapeHtml(dataset)}</code>
                  </td>
                  <td>${prioBadge}</td>
                  <td><span style="font-size: 11px; color: var(--vscode-fg-muted);">${escapeHtml(queuedAt)}</span></td>
                  <td>
                    <div style="display: flex; gap: 4px;">
                      <button class="btn btn-secondary btn-sm" onclick="window.ViewTasks.promoteTask('${t.task_id}')" title="Promote to High Priority Queue">
                        ⬆️ High
                      </button>
                      <button class="btn btn-secondary btn-sm" onclick="window.ViewTasks.reassignTask('${t.task_id}')" title="Reassign Target Queue">
                        ➡️ Reassign
                      </button>
                      <button class="btn btn-danger btn-sm" onclick="window.ViewTasks.deleteTask('${t.task_id}')" title="Delete from Queue">
                        🗑️ Delete
                      </button>
                    </div>
                  </td>
                </tr>
              `;
            }).join("");
          }
        }

        // Render Summary Queues
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
  },

  async promoteTask(taskId) {
    window.workbench.logTerminal("INFO", `Promoting task ${taskId} to gpus_high queue...`);
    try {
      await window.apiClient.promoteQueuedTask(taskId, "gpus_high");
      window.workbench.logTerminal("SUCCESS", `Task ${taskId} promoted to HIGH priority.`);
      await this.load();
    } catch (e) {
      window.workbench.logTerminal("ERROR", `Promotion failed: ${e.message}`);
      alert(`Promotion failed: ${e.message}`);
    }
  },

  async reassignTask(taskId) {
    const target = prompt(`Enter target queue or worker IP for task ${taskId}:`, "wyolo_gpu_queue");
    if (!target || !target.trim()) return;
    window.workbench.logTerminal("INFO", `Reassigning task ${taskId} to queue '${target.trim()}'...`);
    try {
      await window.apiClient.reassignQueuedTask(taskId, target.trim());
      window.workbench.logTerminal("SUCCESS", `Task ${taskId} reassigned to '${target.trim()}'.`);
      await this.load();
    } catch (e) {
      window.workbench.logTerminal("ERROR", `Reassignment failed: ${e.message}`);
      alert(`Reassign failed: ${e.message}`);
    }
  },

  async deleteTask(taskId) {
    if (!confirm(`Are you sure you want to cancel and delete task ${taskId} from the queue?`)) return;
    window.workbench.logTerminal("WARN", `Deleting task ${taskId} from Celery queues...`);
    try {
      await window.apiClient.deleteQueuedTask(taskId);
      window.workbench.logTerminal("SUCCESS", `Task ${taskId} deleted successfully.`);
      await this.load();
    } catch (e) {
      window.workbench.logTerminal("ERROR", `Deletion failed: ${e.message}`);
      alert(`Delete failed: ${e.message}`);
    }
  }
};
