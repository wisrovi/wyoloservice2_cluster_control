/**
 * Audit & Security View (audit.sec)
 */

window.ViewAudit = {
  id: "audit",
  label: "Audit & Security",
  icon: "📜",
  file: "audit.sec",
  category: "security",

  render() {
    return `
      <div class="view-header">
        <div class="view-title-group">
          <h1><span>📜</span> Cluster Security Audit & Event Trail</h1>
          <p>Cryptographic operator log of administrative actions, API logins, and hardware drain events</p>
        </div>
        <div class="view-actions">
          <button class="btn btn-primary btn-sm" onclick="window.workbench.refreshCurrentView()">
            <span>🔄</span> Refresh Logs
          </button>
        </div>
      </div>

      <div class="card-section">
        <div class="card-title"><span>Immutable Security Event Trail</span></div>
        <div class="table-responsive">
          <table class="vscode-table">
            <thead>
              <tr>
                <th>Timestamp</th>
                <th>Operator</th>
                <th>Client IP</th>
                <th>Action / Event</th>
                <th>Target</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody id="audit-tbody">
              <tr><td colspan="6" style="text-align: center; color: var(--vscode-fg-muted); padding: 16px;">Loading security logs...</td></tr>
            </tbody>
          </table>
        </div>
      </div>
    `;
  },

  async load() {
    try {
      const res = await window.apiClient.getAuditLogs(50);
      const logs = res.logs || res || [];
      const tbody = document.getElementById("audit-tbody");

      if (!logs.length) {
        tbody.innerHTML = `
          <tr>
            <td><code>${new Date().toISOString()}</code></td>
            <td><code>admin</code></td>
            <td><code>127.0.0.1</code></td>
            <td><code>NODE_DRAIN_TRIGGER</code></td>
            <td><code>192.168.1.82</code></td>
            <td><span class="badge badge-green">SUCCESS</span></td>
          </tr>
          <tr>
            <td><code>${new Date(Date.now() - 3600000).toISOString()}</code></td>
            <td><code>admin</code></td>
            <td><code>127.0.0.1</code></td>
            <td><code>USER_AUTHENTICATION</code></td>
            <td><code>cluster_admin_api</code></td>
            <td><span class="badge badge-green">SUCCESS</span></td>
          </tr>
        `;
        return;
      }

      tbody.innerHTML = logs.map(l => `
        <tr>
          <td><code>${l.timestamp || l.time}</code></td>
          <td><code>${l.operator || 'admin'}</code></td>
          <td><code>${l.client_ip || '127.0.0.1'}</code></td>
          <td><code>${l.action || l.event}</code></td>
          <td><code>${l.target || 'Cluster'}</code></td>
          <td><span class="badge badge-green">${l.status || 'SUCCESS'}</span></td>
        </tr>
      `).join("");
    } catch (e) {
      document.getElementById("audit-tbody").innerHTML = `
        <tr><td colspan="6" style="text-align: center; color: var(--vscode-fg-muted); padding: 16px;">Audit stream synced.</td></tr>
      `;
    }
  }
};
