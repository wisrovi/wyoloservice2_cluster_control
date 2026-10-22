/**
 * Settings & Maintenance View (settings.json)
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
          <h1><span>🛠️</span> Cluster Settings & Operational Configurations</h1>
          <p>Manage alert webhooks, security credentials, maintenance mode, and local workstation caches</p>
        </div>
        <div class="view-actions">
          <button class="btn btn-primary btn-sm" onclick="window.workbench.refreshCurrentView()">
            <span>🔄</span> Reload Settings
          </button>
        </div>
      </div>

      <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
        <!-- Left: Webhooks & Alerts -->
        <div class="card-section">
          <div class="card-title"><span>🔔 Alert Webhooks (Discord / Slack)</span></div>
          <div class="form-group">
            <label class="form-label">Incoming Webhook URL:</label>
            <input type="text" id="setting-webhook-url" class="form-control" placeholder="https://discord.com/api/webhooks/..." value="">
          </div>
          <div style="display: flex; gap: 8px;">
            <button class="btn btn-secondary" onclick="window.ViewSettings.testWebhook()">
              <span>🔔</span> Send Test Webhook Alert
            </button>
          </div>
          <div id="webhook-test-result" style="display: none; margin-top: 10px; font-size: 11px;"></div>
        </div>

        <!-- Right: Security & Password -->
        <div class="card-section">
          <div class="card-title"><span>🔑 Security & Password</span></div>
          <form onsubmit="event.preventDefault(); window.ViewSettings.changePassword();">
            <div class="form-group">
              <label class="form-label">Current Password:</label>
              <input type="password" id="pw-old" class="form-control" required>
            </div>
            <div class="form-group">
              <label class="form-label">New Password:</label>
              <input type="password" id="pw-new" class="form-control" required>
            </div>
            <button type="submit" class="btn btn-primary">Update Admin Password</button>
          </form>
        </div>
      </div>

      <div class="card-section">
        <div class="card-title"><span>🛑 Global Maintenance Mode</span></div>
        <p style="font-size: 12px; color: var(--vscode-fg-muted); margin-bottom: 12px;">
          When maintenance mode is active, the cluster stops accepting new Celery tasks from the UI, API, or external agents. Running tasks are allowed to finish or can be drained gracefully.
        </p>
        <div style="display: flex; gap: 8px;">
          <button class="btn btn-danger" onclick="alert('Maintenance mode activated across cluster.')">
            <span>🛑</span> Activate Maintenance Mode
          </button>
          <button class="btn btn-secondary" onclick="window.workbench.logout()">
            <span>🚪</span> Log Out Operator Session
          </button>
        </div>
      </div>
    `;
  },

  async load() {},

  async testWebhook() {
    const url = document.getElementById("setting-webhook-url").value.trim();
    const resEl = document.getElementById("webhook-test-result");
    resEl.style.display = "block";
    resEl.style.color = "var(--vscode-fg-muted)";
    resEl.textContent = "Dispatching test alert notification...";

    try {
      const res = await window.apiClient.testWebhook(url || null);
      resEl.style.color = "#10B981";
      resEl.textContent = "Webhook test notification delivered successfully!";
      window.workbench.logTerminal("SUCCESS", "Webhook test alert delivered.");
    } catch (e) {
      resEl.style.color = "#EF4444";
      resEl.textContent = `Webhook test failed: ${e.message}`;
      window.workbench.logTerminal("ERROR", `Webhook test failed: ${e.message}`);
    }
  },

  async changePassword() {
    const oldPw = document.getElementById("pw-old").value;
    const newPw = document.getElementById("pw-new").value;

    try {
      window.workbench.logTerminal("INFO", "Updating admin password...");
      await window.apiClient.changePassword(oldPw, newPw);
      window.workbench.logTerminal("SUCCESS", "Password updated successfully.");
      alert("Password changed successfully!");
      document.getElementById("pw-old").value = "";
      document.getElementById("pw-new").value = "";
    } catch (e) {
      window.workbench.logTerminal("ERROR", `Failed to change password: ${e.message}`);
      alert(`Password update failed: ${e.message}`);
    }
  }
};
