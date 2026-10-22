/**
 * Cluster Administration, Governance & Maintenance View (settings.json)
 * Features: Bulk Limit Adjustment, Day/Night Scheduler Policy, Diagnostic Support Bundle,
 * Redis Housekeeping & Memory Purge, Webhook Alerting, Watchdog scans, and Security.
 */

window.ViewSettings = {
  id: "settings",
  label: "Settings",
  icon: "🛠️",
  file: "settings.json",
  category: "config",

  render() {
    return `
      <div class="view-header">
        <div class="view-title-group">
          <h1><span>🛠️</span> Cluster Settings & Operational Governance</h1>
          <p>Global resource quotas, Day/Night scheduling policies, diagnostic support bundle, Redis housekeeping, and webhook alerts</p>
        </div>
        <div class="view-actions">
          <button class="btn btn-primary btn-sm" onclick="window.ViewSettings.load()">
            <span>🔄</span> Reload Settings
          </button>
        </div>
      </div>

      <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 20px;">
        <!-- Top Left: Bulk Limit Adjustment -->
        <div class="card-section">
          <div class="card-title"><span>🌐 Bulk Resource Adjustment (Cluster-Wide)</span></div>
          <p style="font-size: 12px; color: var(--vscode-fg-muted); margin-bottom: 12px;">
            Apply a uniform MAX_GPU percentage and container RAM limit to every invoker node across the cluster in a single atomic action.
          </p>
          <div class="form-group">
            <label class="form-label" style="display: flex; justify-content: space-between;">
              <span>Global MAX_GPU Cap:</span>
              <span id="bulk-gpu-label" style="font-weight: 600; color: #007ACC;">50%</span>
            </label>
            <input type="range" id="bulk-gpu-slider" min="10" max="100" step="5" value="50" style="width: 100%; accent-color: #007ACC;" oninput="document.getElementById('bulk-gpu-label').textContent = this.value + '%'">
          </div>
          <div class="form-group">
            <label class="form-label">Container Default RAM (e.g. 16g, 24g):</label>
            <input type="text" id="bulk-ram-input" class="form-control" value="16g">
          </div>
          <button class="btn btn-primary" onclick="window.ViewSettings.applyBulkLimits()">
            <span>🚀</span> Apply Quotas to Entire Cluster
          </button>
        </div>

        <!-- Top Right: Diagnostic Support Bundle Exporter -->
        <div class="card-section">
          <div class="card-title"><span>📦 Diagnostic Support Bundle Exporter (1-Click)</span></div>
          <p style="font-size: 12px; color: var(--vscode-fg-muted); margin-bottom: 12px;">
            Export a comprehensive JSON diagnostic blackbox capturing cluster overview, invokers conditions, queues depth, DLQ items, and recent audit logs for offline debugging.
          </p>
          <div style="padding: 12px; background: #252526; border-radius: 4px; margin-bottom: 14px; font-size: 11px; color: var(--vscode-fg-muted);">
            <div>• Full invokers snapshot with NVML and thermals</div>
            <div>• Active workloads and trial progression telemetry</div>
            <div>• Chronological admin audit logs trail</div>
          </div>
          <button class="btn btn-primary" onclick="window.ViewSettings.downloadSupportBundle()">
            <span>📥</span> Generate & Download Support Bundle (.json)
          </button>
        </div>
      </div>

      <!-- Second Row: Scheduler Policy & Redis Housekeeping -->
      <div style="display: grid; grid-template-columns: 1.2fr 0.8fr; gap: 20px; margin-bottom: 20px;">
        <!-- Day/Night Automated Scheduler Policy -->
        <div class="card-section">
          <div class="card-title">
            <span>⏰ Day / Night Automated Scheduler Policy</span>
            <span class="badge badge-blue" id="settings-sched-mode">LOADING</span>
          </div>
          <p style="font-size: 12px; color: var(--vscode-fg-muted); margin-bottom: 12px;">
            Configure quiet office hours limits and uncapped high-throughput night and weekend execution.
          </p>

          <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 12px;">
            <label style="display: flex; align-items: center; gap: 8px; font-size: 12px; cursor: pointer;">
              <input type="checkbox" id="sched-enabled" checked> Enable Automated Schedule
            </label>
            <label style="display: flex; align-items: center; gap: 8px; font-size: 12px; cursor: pointer;">
              <input type="checkbox" id="sched-weekend" checked> Weekend Full Throttle (95%)
            </label>
          </div>

          <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 12px;">
            <div class="form-group">
              <label class="form-label">Office Start Hour (0-23):</label>
              <input type="number" id="sched-office-start" class="form-control" value="9" min="0" max="23">
            </div>
            <div class="form-group">
              <label class="form-label">Office End Hour (0-23):</label>
              <input type="number" id="sched-office-end" class="form-control" value="18" min="0" max="23">
            </div>
          </div>

          <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 14px;">
            <div class="form-group">
              <label class="form-label">Office Max GPU Cap (%):</label>
              <input type="number" id="sched-office-gpu" class="form-control" value="25" min="10" max="100" step="5">
            </div>
            <div class="form-group">
              <label class="form-label">Nighttime Max GPU Cap (%):</label>
              <input type="number" id="sched-night-gpu" class="form-control" value="90" min="10" max="100" step="5">
            </div>
          </div>

          <div style="display: flex; gap: 8px;">
            <button class="btn btn-primary" onclick="window.ViewSettings.saveSchedulerPolicy()">
              <span>💾</span> Save Policy Settings
            </button>
            <button class="btn btn-secondary" onclick="window.ViewSettings.applySchedulerProfileNow()">
              <span>⚡</span> Apply Active Profile Now
            </button>
          </div>
        </div>

        <!-- Redis Housekeeping & Maintenance -->
        <div class="card-section">
          <div class="card-title"><span>🧹 Redis Memory Housekeeping</span></div>
          <p style="font-size: 12px; color: var(--vscode-fg-muted); margin-bottom: 12px;">
            Inspect memory in use and purge stale failed or cancelled studies and temporary telemetry keys.
          </p>

          <div style="display: flex; flex-direction: column; gap: 10px; margin-bottom: 16px;">
            <div style="display: flex; justify-content: space-between; padding: 8px 12px; background: #252526; border-radius: 4px;">
              <span style="color: var(--vscode-fg-muted);">Redis Memory in Use:</span>
              <strong id="hk-mem-val" style="color: var(--vscode-fg-bright);">Loading...</strong>
            </div>
            <div style="display: flex; justify-content: space-between; padding: 8px 12px; background: #252526; border-radius: 4px;">
              <span style="color: var(--vscode-fg-muted);">Stale Studies Detected:</span>
              <strong id="hk-stale-val" style="color: #F59E0B;">0</strong>
            </div>
            <div style="display: flex; justify-content: space-between; padding: 8px 12px; background: #252526; border-radius: 4px;">
              <span style="color: var(--vscode-fg-muted);">Reclaimable RAM:</span>
              <strong id="hk-reclaim-val" style="color: #10B981;">0 KB</strong>
            </div>
          </div>

          <button class="btn btn-secondary" style="width: 100%;" onclick="window.ViewSettings.purgeStaleStudies()">
            <span>🧹</span> Purge Stale Studies Now
          </button>
        </div>
      </div>

      <!-- Third Row: Webhook Alerts & Security -->
      <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
        <!-- Alert Webhooks -->
        <div class="card-section">
          <div class="card-title"><span>🔔 Alert Webhooks (Discord / Slack)</span></div>
          <div class="form-group">
            <label class="form-label">Incoming Webhook URL:</label>
            <input type="text" id="setting-webhook-url" class="form-control" placeholder="https://discord.com/api/webhooks/..." value="">
          </div>
          <label style="display: flex; align-items: center; gap: 8px; font-size: 12px; margin-bottom: 12px; cursor: pointer;">
            <input type="checkbox" id="setting-webhook-enabled" checked> Enable Automatic Event Notifications
          </label>

          <div style="display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 12px;">
            <button class="btn btn-primary btn-sm" onclick="window.ViewSettings.saveWebhook()">
              <span>💾</span> Save Webhook
            </button>
            <button class="btn btn-secondary btn-sm" onclick="window.ViewSettings.testWebhook()">
              <span>🔔</span> Send Test Alert
            </button>
            <button class="btn btn-secondary btn-sm" onclick="window.ViewSettings.runWatchdogScan()">
              <span>⚡</span> Run Watchdog Scan
            </button>
          </div>

          <div style="display: flex; gap: 8px; align-items: center; border-top: 1px solid var(--vscode-border-light); padding-top: 10px;">
            <select id="setting-rich-event" class="form-control form-control-sm" style="flex: 1;">
              <option value="study_completed">Event: Study Completed</option>
              <option value="pod_evicted">Event: Pod Evicted / Drained</option>
              <option value="queue_stall">Event: Queue Stall</option>
            </select>
            <button class="btn btn-secondary btn-sm" onclick="window.ViewSettings.testRichEmbed()">
              <span>🎨</span> Test Rich Card
            </button>
          </div>
        </div>

        <!-- Security & Password -->
        <div class="card-section">
          <div class="card-title"><span>🔑 Security & Password</span></div>
          <form onsubmit="event.preventDefault(); window.ViewSettings.changePassword();">
            <div class="form-group">
              <label class="form-label">Current Operator Password:</label>
              <input type="password" id="pw-old" class="form-control" required>
            </div>
            <div class="form-group">
              <label class="form-label">New Password:</label>
              <input type="password" id="pw-new" class="form-control" required>
            </div>
            <div class="form-group">
              <label class="form-label">Confirm New Password:</label>
              <input type="password" id="pw-confirm" class="form-control" required>
            </div>
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <button type="submit" class="btn btn-primary">Update Admin Password</button>
              <button type="button" class="btn btn-danger btn-sm" onclick="window.workbench.logout()">
                <span>🚪</span> Log Out
              </button>
            </div>
          </form>
        </div>
      </div>
    `;
  },

  async load() {
    // 1. Load Webhook config
    try {
      const wh = await window.apiClient.getWebhookConfig();
      if (wh) {
        const urlInput = document.getElementById("setting-webhook-url");
        const enCheck = document.getElementById("setting-webhook-enabled");
        if (urlInput) urlInput.value = wh.webhook_url || "";
        if (enCheck) enCheck.checked = wh.enabled !== false;
      }
    } catch (_) {}

    // 2. Load Scheduler Policy
    try {
      const sp = await window.apiClient.getSchedulerPolicy();
      const policy = sp?.policy || sp || {};
      const mode = sp?.current_mode || "normal";

      const modeEl = document.getElementById("settings-sched-mode");
      if (modeEl) modeEl.textContent = `${mode.toUpperCase()} ACTIVE`;

      const en = document.getElementById("sched-enabled");
      const wk = document.getElementById("sched-weekend");
      const st = document.getElementById("sched-office-start");
      const end = document.getElementById("sched-office-end");
      const oGpu = document.getElementById("sched-office-gpu");
      const nGpu = document.getElementById("sched-night-gpu");

      if (en) en.checked = policy.enabled !== false;
      if (wk) wk.checked = policy.weekend_full_throttle !== false;
      if (st) st.value = policy.office_start_hour ?? 9;
      if (end) end.value = policy.office_end_hour ?? 18;
      if (oGpu) oGpu.value = policy.office_max_gpu_percent ?? 25;
      if (nGpu) nGpu.value = policy.night_max_gpu_percent ?? 90;
    } catch (_) {}

    // 3. Load Housekeeping Preview
    try {
      const hk = await window.apiClient.getHousekeepingPreview();
      const memEl = document.getElementById("hk-mem-val");
      const staleEl = document.getElementById("hk-stale-val");
      const recEl = document.getElementById("hk-reclaim-val");

      if (memEl) memEl.textContent = hk?.redis_memory_human || "N/A";
      if (staleEl) staleEl.textContent = `${hk?.stale_failed_studies_count || 0} studies`;
      if (recEl) recEl.textContent = `~${hk?.estimated_reclaimed_kb || 0} KB`;
    } catch (_) {}
  },

  async applyBulkLimits() {
    const gpu = parseFloat(document.getElementById("bulk-gpu-slider").value);
    const ram = document.getElementById("bulk-ram-input").value.trim() || "16g";

    if (!confirm(`Apply global MAX_GPU: ${gpu}% and RAM: ${ram} across ALL cluster invoker nodes?`)) return;

    window.workbench.logTerminal("WARN", `Applying bulk limits across cluster: MAX_GPU=${gpu}%, RAM=${ram}...`);
    try {
      const res = await window.apiClient.batchUpdateLimits(gpu, ram);
      window.workbench.logTerminal("SUCCESS", `Bulk limits applied: ${res.message || 'Done'}`);
      alert(`Bulk limits successfully applied to cluster!`);
    } catch (e) {
      window.workbench.logTerminal("ERROR", `Bulk limits error: ${e.message}`);
      alert(`Failed to apply bulk limits: ${e.message}`);
    }
  },

  async downloadSupportBundle() {
    window.workbench.logTerminal("INFO", "Generating diagnostic support bundle...");
    try {
      const bundle = await window.apiClient.getSupportBundle();
      const jsonStr = JSON.stringify(bundle, null, 2);
      const filename = `${bundle.bundle_id || 'neuralforge-support-bundle'}.json`;

      const blob = new Blob([jsonStr], { type: "application/json" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);

      window.workbench.logTerminal("SUCCESS", `Diagnostic support bundle generated: ${filename}`);
    } catch (e) {
      window.workbench.logTerminal("ERROR", `Failed to generate support bundle: ${e.message}`);
      alert(`Error generating support bundle: ${e.message}`);
    }
  },

  async saveSchedulerPolicy() {
    const enabled = document.getElementById("sched-enabled").checked;
    const weekend = document.getElementById("sched-weekend").checked;
    const startHour = parseInt(document.getElementById("sched-office-start").value, 10);
    const endHour = parseInt(document.getElementById("sched-office-end").value, 10);
    const officeGpu = parseFloat(document.getElementById("sched-office-gpu").value);
    const nightGpu = parseFloat(document.getElementById("sched-night-gpu").value);

    const payload = {
      enabled: enabled,
      office_start_hour: startHour,
      office_end_hour: endHour,
      office_max_gpu_percent: officeGpu,
      night_max_gpu_percent: nightGpu,
      weekend_full_throttle: weekend,
    };

    window.workbench.logTerminal("INFO", "Saving Day/Night scheduler policy...");
    try {
      await window.apiClient.setSchedulerPolicy(payload);
      window.workbench.logTerminal("SUCCESS", "Scheduler policy saved in Redis.");
      alert("Scheduler policy saved successfully!");
      await this.load();
    } catch (e) {
      window.workbench.logTerminal("ERROR", `Failed to save policy: ${e.message}`);
      alert(`Failed to save policy: ${e.message}`);
    }
  },

  async applySchedulerProfileNow() {
    window.workbench.logTerminal("WARN", "Applying active scheduler profile to all cluster nodes...");
    try {
      const res = await window.apiClient.applySchedulerPolicy();
      window.workbench.logTerminal("SUCCESS", `Applied profile: ${res.message || 'Done'}`);
      alert(`Profile applied to cluster nodes!`);
      await this.load();
    } catch (e) {
      window.workbench.logTerminal("ERROR", `Error applying profile: ${e.message}`);
      alert(`Failed to apply profile: ${e.message}`);
    }
  },

  async purgeStaleStudies() {
    if (!confirm("Are you sure you want to PURGE all stale and failed study temporary keys from Redis?")) return;
    window.workbench.logTerminal("WARN", "Purging stale failed studies from Redis...");
    try {
      const res = await window.apiClient.purgeHousekeeping();
      window.workbench.logTerminal("SUCCESS", `Purge completed: ${res.message || 'Done'}`);
      alert(`Housekeeping completed: ${res.message || 'Stale records purged'}`);
      await this.load();
    } catch (e) {
      window.workbench.logTerminal("ERROR", `Purge error: ${e.message}`);
      alert(`Purge failed: ${e.message}`);
    }
  },

  async saveWebhook() {
    const url = document.getElementById("setting-webhook-url").value.trim();
    const enabled = document.getElementById("setting-webhook-enabled").checked;

    window.workbench.logTerminal("INFO", "Saving webhook configuration...");
    try {
      await window.apiClient.saveWebhookConfig(url, enabled);
      window.workbench.logTerminal("SUCCESS", "Webhook configuration saved in Redis.");
      alert("Webhook configuration saved!");
    } catch (e) {
      window.workbench.logTerminal("ERROR", `Failed to save webhook: ${e.message}`);
      alert(`Failed to save webhook: ${e.message}`);
    }
  },

  async testWebhook() {
    const url = document.getElementById("setting-webhook-url").value.trim();
    window.workbench.logTerminal("INFO", "Sending test alert notification...");
    try {
      await window.apiClient.testWebhook(url || null);
      window.workbench.logTerminal("SUCCESS", "Test alert delivered successfully.");
      alert("Test alert sent to webhook!");
    } catch (e) {
      window.workbench.logTerminal("ERROR", `Webhook test failed: ${e.message}`);
      alert(`Webhook test failed: ${e.message}`);
    }
  },

  async testRichEmbed() {
    const eventType = document.getElementById("setting-rich-event")?.value || "study_completed";
    const url = document.getElementById("setting-webhook-url")?.value.trim();
    window.workbench.logTerminal("INFO", `Sending test rich embed alert: ${eventType}...`);
    try {
      const res = await window.apiClient.testRichWebhook(eventType, url || null);
      window.workbench.logTerminal("SUCCESS", `Rich embed delivered: ${res.message || 'Done'}`);
      alert(`Rich embed alert sent for '${eventType}'!`);
    } catch (e) {
      window.workbench.logTerminal("ERROR", `Rich embed error: ${e.message}`);
      alert(`Rich embed failed: ${e.message}`);
    }
  },

  async runWatchdogScan() {
    window.workbench.logTerminal("INFO", "Triggering proactive cluster watchdog health scan...");
    try {
      const res = await window.apiClient.triggerWatchdogAlert();
      const count = res.alerts_detected ? res.alerts_detected.length : 0;
      if (count > 0) {
        window.workbench.logTerminal("WARN", `Watchdog detected ${count} alerts: ${res.alerts_detected.join(", ")}`);
        alert(`Watchdog scan completed: ${count} alerts found and dispatched!`);
      } else {
        window.workbench.logTerminal("SUCCESS", "Watchdog: Cluster is fully healthy. No alerts triggered.");
        alert("Cluster is fully healthy! No alerts detected.");
      }
    } catch (e) {
      window.workbench.logTerminal("ERROR", `Watchdog error: ${e.message}`);
      alert(`Watchdog scan error: ${e.message}`);
    }
  },

  async changePassword() {
    const oldPw = document.getElementById("pw-old").value;
    const newPw = document.getElementById("pw-new").value;
    const confirmPw = document.getElementById("pw-confirm").value;

    if (newPw !== confirmPw) {
      alert("New passwords do not match.");
      return;
    }
    if (newPw.length < 6) {
      alert("New password must be at least 6 characters long.");
      return;
    }

    window.workbench.logTerminal("INFO", "Updating operator password...");
    try {
      await window.apiClient.changePassword(oldPw, newPw);
      window.workbench.logTerminal("SUCCESS", "Operator password updated successfully in Redis.");
      alert("Password updated successfully!");
      document.getElementById("pw-old").value = "";
      document.getElementById("pw-new").value = "";
      document.getElementById("pw-confirm").value = "";
    } catch (e) {
      window.workbench.logTerminal("ERROR", `Failed to change password: ${e.message}`);
      alert(`Password change failed: ${e.message}`);
    }
  }
};
