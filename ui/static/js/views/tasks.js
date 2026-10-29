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
  queuedData: [],
  queuedPage: 1,
  queuedPageSize: 10,

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
          <div style="display: flex; align-items: center; gap: 8px;">
            <span>⏳ Detailed Waiting Queue & Celery Backlog (Tareas en Espera)</span>
            <span class="badge badge-amber" id="queued-tasks-badge">0 Queued</span>
          </div>
          <button class="btn btn-secondary btn-sm" onclick="window.ViewTasks.refreshQueues()" title="Refrescar tareas en cola">
            <span>🔄</span> Refrescar
          </button>
        </div>

        <!-- Filter Bar -->
        <div style="display: flex; flex-wrap: wrap; gap: 8px; align-items: center; margin-bottom: 12px; background: rgba(0,0,0,0.15); padding: 8px 12px; border-radius: 4px; border: 1px solid var(--vscode-border-light);">
          <div style="flex: 1; min-width: 180px;">
            <input type="text" id="tasks-queued-search" class="form-control form-control-sm" placeholder="🔍 Filtrar por estudio, tarea, autor, dataset..." oninput="window.ViewTasks.onQueuedFilterChange()" style="width: 100%;">
          </div>

          <select id="tasks-queued-filter-queue" class="form-control form-control-sm" style="width: 160px;" onchange="window.ViewTasks.onQueuedFilterChange()">
            <option value="All">Todas las Colas / Nodos</option>
          </select>

          <select id="tasks-queued-filter-priority" class="form-control form-control-sm" style="width: 130px;" onchange="window.ViewTasks.onQueuedFilterChange()">
            <option value="All">Todas Prioridades</option>
            <option value="NORMAL">NORMAL</option>
            <option value="HIGH">HIGH</option>
          </select>

          <select id="tasks-queued-filter-model" class="form-control form-control-sm" style="width: 130px;" onchange="window.ViewTasks.onQueuedFilterChange()">
            <option value="All">Todos los Modelos</option>
          </select>

          <select id="tasks-queued-page-size" class="form-control form-control-sm" style="width: 95px;" onchange="window.ViewTasks.onQueuedPageSizeChange()">
            <option value="5">5 por pág</option>
            <option value="10" selected>10 por pág</option>
            <option value="25">25 por pág</option>
            <option value="50">50 por pág</option>
          </select>

          <button class="btn btn-secondary btn-sm" onclick="window.ViewTasks.clearQueuedFilters()" title="Limpiar filtros">
            ✕ Limpiar
          </button>

          <button id="tasks-btn-cancel-filtered" class="btn btn-danger btn-sm" style="display: none;" onclick="window.ViewTasks.cancelAllFilteredQueued()" title="Cancelar y eliminar de la cola todas las tareas que coinciden con los filtros actuales">
            🗑️ Cancelar Filtradas (0)
          </button>
        </div>

        <!-- Feedback Toast Banner -->
        <div id="tasks-queued-toast" style="display: none; padding: 10px 14px; border-radius: 4px; margin-bottom: 12px; font-size: 13px; align-items: center; justify-content: space-between;"></div>

        <div class="table-responsive">
          <table class="vscode-table">
            <thead>
              <tr>
                <th>Study / Workload Name</th>
                <th>Author</th>
                <th>Target Queue / Node</th>
                <th>Model & Task</th>
                <th>Training Specs</th>
                <th>Dataset Path</th>
                <th>Priority</th>
                <th>Queued At</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody id="queued-tasks-tbody">
              <tr><td colspan="9" style="text-align: center; color: var(--vscode-fg-muted); padding: 16px;">Loading queued tasks...</td></tr>
            </tbody>
          </table>
        </div>

        <!-- Pagination Bar -->
        <div id="tasks-queued-pagination" style="display: flex; justify-content: space-between; align-items: center; margin-top: 10px; font-size: 12px; color: var(--vscode-fg-muted); padding: 4px 6px;">
          <div id="tasks-queued-page-info">Mostrando 0 de 0</div>
          <div style="display: flex; gap: 6px; align-items: center;">
            <button class="btn btn-secondary btn-sm" id="tasks-queued-btn-prev" onclick="window.ViewTasks.changeQueuedPage(-1)">◀ Anterior</button>
            <span id="tasks-queued-page-number" style="font-weight: 600; color: var(--vscode-fg-bright); padding: 0 4px;">Pág. 1 / 1</span>
            <button class="btn btn-secondary btn-sm" id="tasks-queued-btn-next" onclick="window.ViewTasks.changeQueuedPage(1)">Siguiente ▶</button>
          </div>
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
        this.queuedData = qRes.tasks || [];
        const totalQueued = qRes.total_queued !== undefined ? qRes.total_queued : this.queuedData.length;

        const qBadge = document.getElementById("queued-tasks-badge");
        if (qBadge) qBadge.textContent = `${totalQueued} Queued`;

        this.populateQueuedDropdowns(this.queuedData);
        this.renderQueuedTable();

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

  showQueuedToast(type, message) {
    const toast = document.getElementById("tasks-queued-toast");
    if (!toast) return;
    toast.style.display = "flex";
    if (type === "success") {
      toast.style.background = "rgba(16, 185, 129, 0.15)";
      toast.style.border = "1px solid #10B981";
      toast.style.color = "#10B981";
    } else {
      toast.style.background = "rgba(239, 68, 68, 0.15)";
      toast.style.border = "1px solid #EF4444";
      toast.style.color = "#EF4444";
    }
    toast.innerHTML = `
      <span>${escapeHtml(message)}</span>
      <span style="cursor: pointer; font-weight: bold; margin-left: 12px;" onclick="document.getElementById('tasks-queued-toast').style.display='none'">✕</span>
    `;
    setTimeout(() => {
      if (toast) toast.style.display = "none";
    }, 6000);
  },

  async deleteTask(taskId, studyName = "") {
    const label = studyName ? `'${studyName}' (${taskId.slice(0, 8)}...)` : `'${taskId}'`;
    if (!confirm(`¿Estás seguro de que deseas cancelar y eliminar de la cola la tarea ${label}?`)) return;

    const btn = document.getElementById(`btn-tasks-del-${taskId}`);
    if (btn) {
      btn.disabled = true;
      btn.textContent = "⏳...";
    }
    window.workbench.logTerminal("WARN", `Deleting task ${taskId} from Celery queues...`);

    try {
      await window.apiClient.deleteQueuedTask(taskId);
      window.workbench.logTerminal("SUCCESS", `Task ${taskId} deleted successfully.`);
      this.showQueuedToast("success", `✅ Tarea ${label} eliminada de la cola exitosamente.`);
      await this.refreshQueues();
    } catch (e) {
      window.workbench.logTerminal("ERROR", `Deletion failed: ${e.message}`);
      this.showQueuedToast("error", `❌ Error al eliminar tarea ${label}: ${e.message}`);
      if (btn) {
        btn.disabled = false;
        btn.textContent = "🗑️ Delete";
      }
    }
  },

  async cancelAllFilteredQueued() {
    const q = (document.getElementById("tasks-queued-search")?.value || "").toLowerCase().trim();
    const queueFilter = document.getElementById("tasks-queued-filter-queue")?.value || "All";
    const prioFilter = document.getElementById("tasks-queued-filter-priority")?.value || "All";
    const modelFilter = document.getElementById("tasks-queued-filter-model")?.value || "All";

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

    if (!filtered.length) {
      alert("No hay tareas que coincidan con los filtros actuales.");
      return;
    }

    const filterDesc = q ? `'${q}'` : (queueFilter !== "All" ? `cola '${queueFilter}'` : "los filtros seleccionados");
    if (!confirm(`¿Estás seguro de que deseas cancelar y eliminar de la cola TODAS las ${filtered.length} tareas que coinciden con ${filterDesc}?`)) {
      return;
    }

    const btn = document.getElementById("tasks-btn-cancel-filtered");
    if (btn) {
      btn.disabled = true;
      btn.textContent = "⏳ Cancelando lote...";
    }

    window.workbench.logTerminal("WARN", `Cancelando en lote ${filtered.length} tareas filtradas...`);
    const taskIds = filtered.map(t => t.task_id);

    try {
      const res = await window.apiClient.deleteQueuedTasksBatch(taskIds);
      const deletedCount = res.deleted_count !== undefined ? res.deleted_count : taskIds.length;
      window.workbench.logTerminal("SUCCESS", `Lote completado: ${deletedCount} tareas eliminadas.`);
      this.showQueuedToast("success", `✅ Se cancelaron y eliminaron ${deletedCount} tareas de la cola exitosamente.`);
      await this.refreshQueues();
    } catch (e) {
      window.workbench.logTerminal("ERROR", `Error en cancelación por lote: ${e.message}`);
      this.showQueuedToast("error", `❌ Error al cancelar tareas en lote: ${e.message}`);
    } finally {
      if (btn) {
        btn.disabled = false;
      }
    }
  },

  populateQueuedDropdowns(tasks) {
    const queueSel = document.getElementById("tasks-queued-filter-queue");
    const modelSel = document.getElementById("tasks-queued-filter-model");

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
    const sel = document.getElementById("tasks-queued-page-size");
    this.queuedPageSize = parseInt(sel?.value || "10", 10);
    this.queuedPage = 1;
    this.renderQueuedTable();
  },

  clearQueuedFilters() {
    const searchInput = document.getElementById("tasks-queued-search");
    const queueSel = document.getElementById("tasks-queued-filter-queue");
    const prioSel = document.getElementById("tasks-queued-filter-priority");
    const modelSel = document.getElementById("tasks-queued-filter-model");

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
    const tbody = document.getElementById("queued-tasks-tbody");
    const pageInfo = document.getElementById("tasks-queued-page-info");
    const pageNumber = document.getElementById("tasks-queued-page-number");
    const btnPrev = document.getElementById("tasks-queued-btn-prev");
    const btnNext = document.getElementById("tasks-queued-btn-next");
    const badge = document.getElementById("queued-tasks-badge");

    if (!tbody) return;

    const q = (document.getElementById("tasks-queued-search")?.value || "").toLowerCase().trim();
    const queueFilter = document.getElementById("tasks-queued-filter-queue")?.value || "All";
    const prioFilter = document.getElementById("tasks-queued-filter-priority")?.value || "All";
    const modelFilter = document.getElementById("tasks-queued-filter-model")?.value || "All";

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

    const hasFilter = !!(q || queueFilter !== "All" || prioFilter !== "All" || modelFilter !== "All");
    const btnCancelFiltered = document.getElementById("tasks-btn-cancel-filtered");
    if (btnCancelFiltered) {
      if (hasFilter && filteredCount > 0) {
        btnCancelFiltered.style.display = "inline-flex";
        btnCancelFiltered.textContent = `🗑️ Cancelar Filtradas (${filteredCount})`;
      } else {
        btnCancelFiltered.style.display = "none";
      }
    }

    if (badge) {
      badge.textContent = `${totalCount} Queued` + (filteredCount !== totalCount ? ` (${filteredCount} filtrados)` : "");
    }

    if (!filteredCount) {
      tbody.innerHTML = `<tr><td colspan="9" style="text-align: center; color: var(--vscode-fg-muted); padding: 16px;">
        ${totalCount === 0 ? "No workloads currently waiting in queues." : "No hay tareas en espera que coincidan con los filtros aplicados."}
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
      const targetBadge = isNodeQueue
        ? `<span class="badge badge-green" title="Direct Node Queue">${escapeHtml(qName)}</span>`
        : `<span class="badge badge-blue" title="Public Celery Queue">${escapeHtml(qName)}</span>`;
      const model = t.model || "yolo";
      const taskType = t.task_type ? `<div style="font-size: 10px; color: var(--vscode-fg-muted); text-transform: uppercase;">${escapeHtml(t.task_type)}</div>` : "";
      const dataset = t.dataset || "N/A";
      const epochs = t.epochs !== undefined && t.epochs !== null ? `${t.epochs} eps` : "N/A eps";
      const batchSize = t.batch_size !== undefined && t.batch_size !== null ? (t.batch_size === -1 ? "auto batch" : `b:${t.batch_size}`) : "";
      const imgsz = t.imgsz ? `sz:${t.imgsz}` : "";
      const specsSummary = [epochs, batchSize, imgsz].filter(Boolean).join(" • ");
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
          <td>
            <div style="font-weight: 500; color: var(--vscode-fg-bright); font-size: 12px;">👤 ${escapeHtml(author)}</div>
          </td>
          <td>${targetBadge}</td>
          <td>
            <span class="badge badge-blue">${escapeHtml(model)}</span>
            ${taskType}
          </td>
          <td>
            <div style="font-size: 11px; font-weight: 600; color: #4EC9B0;">${escapeHtml(specsSummary)}</div>
            ${t.fitness ? `<div style="font-size: 10px; color: var(--vscode-fg-muted);">${escapeHtml(t.fitness)}</div>` : ''}
          </td>
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
              <button class="btn btn-danger btn-sm" id="btn-tasks-del-${t.task_id}" onclick="window.ViewTasks.deleteTask('${t.task_id}', '${escapeHtml(studyName)}')" title="Delete from Queue">
                🗑️ Delete
              </button>
            </div>
          </td>
        </tr>
      `;
    }).join("");
  },

  async refreshQueues() {
    try {
      const qRes = await window.apiClient.getQueues();
      this.queuedData = qRes.tasks || [];
      const totalQueued = qRes.total_queued !== undefined ? qRes.total_queued : this.queuedData.length;
      const qBadge = document.getElementById("queued-tasks-badge");
      if (qBadge) qBadge.textContent = `${totalQueued} Queued`;
      this.populateQueuedDropdowns(this.queuedData);
      this.renderQueuedTable();
    } catch (e) {
      window.workbench?.logTerminal("WARN", `Error actualizando colas: ${e.message}`);
    }
  }
};
