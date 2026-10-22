/**
 * Cluster Capabilities & R&D Modules Catalog View (capabilities.spec)
 * Displays the 12 research-grade I+D modules, hardware compute matrix, and CUDA precision capabilities.
 */

window.ViewCapabilities = {
  id: "capabilities",
  label: "Capabilities",
  icon: "🔬",
  file: "capabilities.spec",
  category: "hardware",

  render() {
    return `
      <div class="view-header">
        <div class="view-title-group">
          <h1><span>🔬</span> Compute Capabilities & Official R&D Catalog</h1>
          <p>Official research modules, automated post-train analytics, CUDA compute architectures, and precision support</p>
        </div>
        <div class="view-actions">
          <button class="btn btn-primary btn-sm" onclick="window.ViewCapabilities.load()">
            <span>🔄</span> Refresh Capabilities
          </button>
        </div>
      </div>

      <div class="metrics-ribbon">
        <div class="metric-card">
          <div class="metric-label">Official R&D Modules</div>
          <div class="metric-value" id="cap-total-modules" style="color: #10B981;">12 Active</div>
          <div class="metric-sub">Post-train research pipeline</div>
        </div>
        <div class="metric-card">
          <div class="metric-label">Worker Executor Image</div>
          <div class="metric-value" id="cap-docker-img" style="font-size: 13px;">worker_executor:v1.0.0</div>
          <div class="metric-sub">Dockerized runtime engine</div>
        </div>
        <div class="metric-card">
          <div class="metric-label">Published Research Tiers</div>
          <div class="metric-value" style="color: #007ACC;">7 Top-Tier Papers</div>
          <div class="metric-sub">MLSys, CVPR, NeurIPS, ICML</div>
        </div>
        <div class="metric-card">
          <div class="metric-label">Supported Precisions</div>
          <div class="metric-value">FP32, FP16, BF16, FP8</div>
          <div class="metric-sub">PyTorch AMP & FlashAttention</div>
        </div>
      </div>

      <!-- Section 1: Official R&D Modules Catalog -->
      <div class="card-section" style="margin-bottom: 20px;">
        <div class="card-title">
          <span>🧠 Worker Post-Train R&D Modules Catalog (Automatic Pipeline)</span>
          <span class="badge badge-green">Production Ready</span>
        </div>
        <div class="table-responsive">
          <table class="vscode-table">
            <thead>
              <tr>
                <th style="width: 80px;">ID</th>
                <th>Module Name</th>
                <th>Research Category</th>
                <th>Target Venue / Paper</th>
                <th>Description</th>
                <th style="width: 80px;">Status</th>
              </tr>
            </thead>
            <tbody id="capabilities-modules-tbody">
              <tr><td colspan="6" style="text-align: center; color: var(--vscode-fg-muted); padding: 16px;">Loading official R&D modules catalog...</td></tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Section 2: Hardware Architecture & Precision Support -->
      <div class="card-section">
        <div class="card-title"><span>🖥️ Cluster Hardware Family & Precision Matrix</span></div>
        <div class="table-responsive">
          <table class="vscode-table">
            <thead>
              <tr>
                <th>Hardware Family</th>
                <th>Compute Arch</th>
                <th>FP32</th>
                <th>FP16 (AMP)</th>
                <th>BF16</th>
                <th>FP8 (Transformer Engine)</th>
                <th>FlashAttention 2</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td><strong>Ada Lovelace (RTX 4090 / 4060 Ti)</strong></td>
                <td><code>sm_89</code></td>
                <td><span class="badge badge-green">Supported</span></td>
                <td><span class="badge badge-green">Supported</span></td>
                <td><span class="badge badge-green">Supported</span></td>
                <td><span class="badge badge-green">Supported</span></td>
                <td><span class="badge badge-green">Enabled</span></td>
              </tr>
              <tr>
                <td><strong>Ampere (RTX 3060 Ti / 3060 / 3050 OEM)</strong></td>
                <td><code>sm_86</code></td>
                <td><span class="badge badge-green">Supported</span></td>
                <td><span class="badge badge-green">Supported</span></td>
                <td><span class="badge badge-green">Supported</span></td>
                <td><span class="badge badge-amber">Emulated</span></td>
                <td><span class="badge badge-green">Enabled</span></td>
              </tr>
              <tr>
                <td><strong>Turing (GTX 1650)</strong></td>
                <td><code>sm_75</code></td>
                <td><span class="badge badge-green">Supported</span></td>
                <td><span class="badge badge-green">Supported</span></td>
                <td><span class="badge badge-amber">Emulated</span></td>
                <td><span class="badge badge-red">N/A</span></td>
                <td><span class="badge badge-amber">Fallback</span></td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    `;
  },

  async load() {
    try {
      const cap = await window.apiClient.getCapabilities();
      const modules = cap?.modules || [];

      if (cap?.total_modules) {
        document.getElementById("cap-total-modules").textContent = `${cap.active_modules || cap.total_modules} Active`;
      }
      if (cap?.docker_image) {
        document.getElementById("cap-docker-img").textContent = cap.docker_image.split("/").pop();
      }

      const tbody = document.getElementById("capabilities-modules-tbody");
      if (!modules.length) {
        tbody.innerHTML = `<tr><td colspan="6" style="text-align: center; color: var(--vscode-fg-muted); padding: 16px;">No modules loaded.</td></tr>`;
        return;
      }

      tbody.innerHTML = modules.map(m => `
        <tr>
          <td><span class="badge badge-blue"><code>${m.module_id}</code></span></td>
          <td><strong>${m.name}</strong></td>
          <td><code>${m.category}</code></td>
          <td><span style="color: #007ACC; font-weight: 500;">${m.research_tier || 'Production'}</span></td>
          <td style="font-size: 11px; color: var(--vscode-fg-muted);">${m.description}</td>
          <td><span class="badge badge-green">Enabled</span></td>
        </tr>
      `).join("");
    } catch (e) {
      document.getElementById("capabilities-modules-tbody").innerHTML = `
        <tr><td colspan="6" style="text-align: center; color: var(--vscode-btn-danger); padding: 16px;">
          Failed to load capabilities: ${e.message}
        </td></tr>
      `;
    }
  }
};
