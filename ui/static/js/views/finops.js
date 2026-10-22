/**
 * Cluster FinOps, Power Draw & Green AI View (finops.green)
 * Features: Live power draw, accumulated cost, billing rate update (€/kWh),
 * GPU cost breakdown, carbon footprint, and solar offset metrics.
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
          <h1><span>🌿</span> Cluster FinOps, Energy & Green AI Governance</h1>
          <p>Real-time electricity consumption, cost projections (€/month), billing rate governance, and carbon footprint</p>
        </div>
        <div class="view-actions">
          <button class="btn btn-primary btn-sm" onclick="window.ViewFinops.load()">
            <span>🔄</span> Refresh FinOps
          </button>
        </div>
      </div>

      <!-- Metrics Ribbon -->
      <div class="metrics-ribbon">
        <div class="metric-card">
          <div class="metric-label">Accumulated Electricity Cost</div>
          <div class="metric-value" id="finops-total-cost" style="color: #10B981;">0.00 €</div>
          <div class="metric-sub" id="finops-energy-sub">0.00 kWh consumed</div>
        </div>
        <div class="metric-card">
          <div class="metric-label">Projected Monthly Cost</div>
          <div class="metric-value" id="finops-projected-cost">0.00 € / mo</div>
          <div class="metric-sub">Based on cluster run-rate</div>
        </div>
        <div class="metric-card">
          <div class="metric-label">Carbon Footprint (CO₂e)</div>
          <div class="metric-value" id="finops-carbon" style="color: #007ACC;">0.0 kg</div>
          <div class="metric-sub" id="finops-trees-sub">~0 trees offset equivalent</div>
        </div>
        <div class="metric-card">
          <div class="metric-label">Active Electricity Rate</div>
          <div class="metric-value" id="finops-rate-display">0.180 €/kWh</div>
          <div class="metric-sub">Contracted utility baseline</div>
        </div>
      </div>

      <!-- Billing Rate Adjustment Toolbar -->
      <div class="card-section" style="margin-bottom: 20px; padding: 12px 16px;">
        <div style="display: flex; flex-wrap: wrap; gap: 12px; align-items: center; justify-content: space-between;">
          <div style="font-size: 12px; color: var(--vscode-fg-bright); font-weight: 500;">
            ⚡ Update Electricity Billing Rate (€/kWh):
          </div>
          <div style="display: flex; gap: 8px; align-items: center;">
            <input type="number" id="finops-rate-input" class="form-control form-control-sm" value="0.18" step="0.01" min="0.01" max="2.00" style="width: 100px;">
            <button class="btn btn-primary btn-sm" onclick="window.ViewFinops.updateRate()">
              <span>💾</span> Save Rate & Recalculate
            </button>
          </div>
        </div>
      </div>

      <!-- GPU Model Cost Breakdown -->
      <div class="card-section">
        <div class="card-title">
          <span>🖥️ Consumption & Electricity Cost Breakdown by GPU Architecture</span>
        </div>
        <div class="table-responsive">
          <table class="vscode-table">
            <thead>
              <tr>
                <th>GPU Model</th>
                <th>Cumulative Compute Hours</th>
                <th>Energy Consumed (kWh)</th>
                <th>Estimated Cost (€)</th>
                <th>Share of Cluster Power</th>
              </tr>
            </thead>
            <tbody id="finops-gpu-tbody">
              <tr><td colspan="5" style="text-align: center; color: var(--vscode-fg-muted); padding: 16px;">Computing FinOps telemetry...</td></tr>
            </tbody>
          </table>
        </div>
      </div>
    `;
  },

  async load() {
    try {
      const finops = await window.apiClient.getFinOps();
      const green = await window.apiClient.getGreenAi();

      const totalKwh = finops?.total_kwh || green?.estimated_kwh || 0;
      const rate = finops?.rate_eur_per_kwh || 0.18;
      const totalCost = finops?.total_cost_eur || (totalKwh * rate);
      const projected = finops?.projected_monthly_cost_eur || 0;
      const carbon = green?.carbon_kg_co2e || (totalKwh * 0.25);
      const trees = green?.trees_equivalent || (carbon / 21.0);

      document.getElementById("finops-total-cost").textContent = `${totalCost.toFixed(2)} €`;
      document.getElementById("finops-energy-sub").textContent = `${totalKwh.toFixed(2)} kWh consumed`;
      document.getElementById("finops-projected-cost").textContent = `${projected.toFixed(2)} € / mo`;
      document.getElementById("finops-carbon").textContent = `${carbon.toFixed(2)} kg CO₂`;
      document.getElementById("finops-trees-sub").textContent = `~${trees.toFixed(1)} trees offset equivalent`;
      document.getElementById("finops-rate-display").textContent = `${rate.toFixed(3)} €/kWh`;
      document.getElementById("finops-rate-input").value = rate;

      // Table breakdown
      const breakdown = finops?.gpu_cost_breakdown || [];
      const tbody = document.getElementById("finops-gpu-tbody");

      if (!breakdown.length) {
        tbody.innerHTML = `<tr><td colspan="5" style="text-align: center; color: var(--vscode-fg-muted); padding: 16px;">No GPU workloads recorded yet.</td></tr>`;
        return;
      }

      tbody.innerHTML = breakdown.map(g => {
        const kwh = g.total_kwh || 0;
        const pct = totalKwh > 0 ? ((kwh / totalKwh) * 100).toFixed(1) : 0;

        return `
          <tr>
            <td><strong>${g.gpu_model}</strong></td>
            <td><code>${(g.total_hours || 0).toFixed(1)} hrs</code></td>
            <td>${kwh.toFixed(2)} kWh</td>
            <td style="color: #10B981; font-weight: 600;">${(g.estimated_cost_eur || 0).toFixed(2)} €</td>
            <td>
              <div style="display: flex; align-items: center; gap: 8px;">
                <div style="flex: 1; height: 6px; background: #333; border-radius: 3px; overflow: hidden;">
                  <div style="width: ${pct}%; height: 100%; background: #007ACC;"></div>
                </div>
                <span style="font-size: 11px; width: 45px; text-align: right;">${pct}%</span>
              </div>
            </td>
          </tr>
        `;
      }).join("");
    } catch (e) {
      document.getElementById("finops-gpu-tbody").innerHTML = `
        <tr><td colspan="5" style="text-align: center; color: var(--vscode-btn-danger); padding: 16px;">
          Error retrieving FinOps report: ${e.message}
        </td></tr>
      `;
    }
  },

  async updateRate() {
    const rate = parseFloat(document.getElementById("finops-rate-input").value);
    if (isNaN(rate) || rate <= 0) {
      alert("Please enter a valid electricity rate (e.g. 0.18).");
      return;
    }

    window.workbench.logTerminal("INFO", `Updating cluster electricity rate to: ${rate} €/kWh...`);
    try {
      await window.apiClient.updateFinopsRate(rate);
      window.workbench.logTerminal("SUCCESS", `Electricity rate updated to ${rate} €/kWh.`);
      alert(`Electricity rate updated to ${rate} €/kWh!`);
      await this.load();
    } catch (e) {
      window.workbench.logTerminal("ERROR", `Failed to update electricity rate: ${e.message}`);
      alert(`Error updating rate: ${e.message}`);
    }
  }
};
