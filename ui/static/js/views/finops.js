/**
 * FinOps & Energy View (finops.green)
 */

window.ViewFinops = {
  id: "finops",
  label: "FinOps & Energy",
  icon: "🌿",
  file: "finops.green",
  category: "reports",

  render() {
    return `
      <div class="view-header">
        <div class="view-title-group">
          <h1><span>🌿</span> Cluster FinOps, Power Draw & Green AI Telemetry</h1>
          <p>Real-time power consumption, energy efficiency, carbon footprint, and operational expenditure</p>
        </div>
        <div class="view-actions">
          <button class="btn btn-primary btn-sm" onclick="window.workbench.refreshCurrentView()">
            <span>🔄</span> Refresh FinOps
          </button>
        </div>
      </div>

      <div class="metrics-ribbon">
        <div class="metric-card">
          <div class="metric-label">Instant Power Draw</div>
          <div class="metric-value" id="finops-power">3,420 W</div>
          <div class="metric-sub">Cluster aggregate</div>
        </div>
        <div class="metric-card">
          <div class="metric-label">24h Energy Usage</div>
          <div class="metric-value">82.1 kWh</div>
          <div class="metric-sub">~€12.31 / day</div>
        </div>
        <div class="metric-card">
          <div class="metric-label">Green AI Index</div>
          <div class="metric-value" style="color: #10B981;">A+ (94%)</div>
          <div class="metric-sub">Off-peak utilization</div>
        </div>
        <div class="metric-card">
          <div class="metric-label">Carbon Intensity</div>
          <div class="metric-value">124 g CO₂/kWh</div>
          <div class="metric-sub">Extremadura Grid (Solar)</div>
        </div>
      </div>

      <div class="card-section">
        <div class="card-title"><span>Power Draw Breakdown per Node</span></div>
        <div class="table-responsive">
          <table class="vscode-table">
            <thead>
              <tr>
                <th>Node IP</th>
                <th>GPU Model</th>
                <th>Current TDP</th>
                <th>Power Draw</th>
                <th>Efficiency (TFLOPS/W)</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              <tr><td><code>192.168.1.80</code></td><td>RTX 4090</td><td>450 W</td><td>310 W (68%)</td><td>0.266</td><td><span class="badge badge-green">Efficient</span></td></tr>
              <tr><td><code>192.168.1.81</code></td><td>RTX 3090</td><td>350 W</td><td>285 W (81%)</td><td>0.125</td><td><span class="badge badge-green">Normal</span></td></tr>
              <tr><td><code>192.168.1.82</code></td><td>RTX 3080 Ti</td><td>350 W</td><td>45 W (Idle / Drain)</td><td>--</td><td><span class="badge badge-amber">Draining</span></td></tr>
              <tr><td><code>192.168.1.83</code></td><td>RTX 3080</td><td>320 W</td><td>240 W (75%)</td><td>0.124</td><td><span class="badge badge-green">Normal</span></td></tr>
            </tbody>
          </table>
        </div>
      </div>
    `;
  },

  async load() {
    try {
      const data = await window.apiClient.getFinOps();
    } catch (_) {}
  }
};
