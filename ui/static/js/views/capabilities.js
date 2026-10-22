/**
 * Cluster Capabilities View (capabilities.spec)
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
          <h1><span>🔬</span> Compute Capabilities & Hardware Matrix</h1>
          <p>NVIDIA CUDA compute architecture, TensorRT capabilities, FP16/BF16/FP8 precision support</p>
        </div>
        <div class="view-actions">
          <button class="btn btn-primary btn-sm" onclick="window.workbench.refreshCurrentView()">
            <span>🔄</span> Refresh Specs
          </button>
        </div>
      </div>

      <div class="card-section">
        <div class="card-title"><span>Hardware Support & Precision Matrix</span></div>
        <div class="table-responsive">
          <table class="vscode-table">
            <thead>
              <tr>
                <th>Hardware Family</th>
                <th>Compute Cap</th>
                <th>FP32</th>
                <th>FP16 (AMP)</th>
                <th>BF16</th>
                <th>FP8 (Transformer)</th>
                <th>FlashAttention 2</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td><strong>Ada Lovelace (RTX 4090)</strong></td>
                <td><code>sm_89</code></td>
                <td><span class="badge badge-green">Supported</span></td>
                <td><span class="badge badge-green">Supported</span></td>
                <td><span class="badge badge-green">Supported</span></td>
                <td><span class="badge badge-green">Supported</span></td>
                <td><span class="badge badge-green">Enabled</span></td>
              </tr>
              <tr>
                <td><strong>Ampere (RTX 3090 / 3080 Ti / 3080)</strong></td>
                <td><code>sm_86</code></td>
                <td><span class="badge badge-green">Supported</span></td>
                <td><span class="badge badge-green">Supported</span></td>
                <td><span class="badge badge-green">Supported</span></td>
                <td><span class="badge badge-amber">Emulated</span></td>
                <td><span class="badge badge-green">Enabled</span></td>
              </tr>
              <tr>
                <td><strong>Turing (RTX 2080 Ti / T4)</strong></td>
                <td><code>sm_75</code></td>
                <td><span class="badge badge-green">Supported</span></td>
                <td><span class="badge badge-green">Supported</span></td>
                <td><span class="badge badge-red">No</span></td>
                <td><span class="badge badge-red">No</span></td>
                <td><span class="badge badge-amber">Partial</span></td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    `;
  },

  async load() {
    try {
      await window.apiClient.getCapabilities();
    } catch (_) {}
  }
};
