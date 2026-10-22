/**
 * GPU Benchmarks View (benchmarks.gpu)
 */

window.ViewBenchmarks = {
  id: "benchmarks",
  label: "GPU Benchmarks",
  icon: "🏆",
  file: "benchmarks.gpu",
  category: "reports",

  render() {
    return `
      <div class="view-header">
        <div class="view-title-group">
          <h1><span>🏆</span> Cluster GPU Benchmarks & Throughput Leaderboard</h1>
          <p>Compute performance analysis, tensor operations throughput, and memory bandwidth rankings</p>
        </div>
        <div class="view-actions">
          <button class="btn btn-primary btn-sm" onclick="window.workbench.refreshCurrentView()">
            <span>🔄</span> Refresh Benchmarks
          </button>
        </div>
      </div>

      <div class="metrics-ribbon">
        <div class="metric-card">
          <div class="metric-label">Cluster Total FP32 TFLOPS</div>
          <div class="metric-value">648.2</div>
          <div class="metric-sub">Theoretical peak</div>
        </div>
        <div class="metric-card">
          <div class="metric-label">Aggregated VRAM Bandwidth</div>
          <div class="metric-value">14.2 TB/s</div>
          <div class="metric-sub">PCIe Gen4 / GDDR6X</div>
        </div>
        <div class="metric-card">
          <div class="metric-label">Average Batch Latency</div>
          <div class="metric-value">12.4 ms</div>
          <div class="metric-sub">YOLOv8 FP16</div>
        </div>
      </div>

      <div class="card-section">
        <div class="card-title"><span>Node Compute Leaderboard</span></div>
        <div class="table-responsive">
          <table class="vscode-table">
            <thead>
              <tr>
                <th>Rank</th>
                <th>Node IP</th>
                <th>GPU Model</th>
                <th>FP32 TFLOPS</th>
                <th>Tensor Cores</th>
                <th>Inference FPS (Batch 32)</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody id="benchmarks-tbody">
              <tr><td>🥇 #1</td><td><code>192.168.1.80</code></td><td>NVIDIA RTX 4090</td><td>82.6 TFLOPS</td><td>512 (4th Gen)</td><td>4,120 fps</td><td><span class="badge badge-green">Online</span></td></tr>
              <tr><td>🥈 #2</td><td><code>192.168.1.81</code></td><td>NVIDIA RTX 3090</td><td>35.6 TFLOPS</td><td>328 (3rd Gen)</td><td>2,450 fps</td><td><span class="badge badge-green">Online</span></td></tr>
              <tr><td>🥉 #3</td><td><code>192.168.1.82</code></td><td>NVIDIA RTX 3080 Ti</td><td>34.1 TFLOPS</td><td>320 (3rd Gen)</td><td>2,380 fps</td><td><span class="badge badge-amber">Draining</span></td></tr>
              <tr><td>#4</td><td><code>192.168.1.83</code></td><td>NVIDIA RTX 3080</td><td>29.8 TFLOPS</td><td>272 (3rd Gen)</td><td>2,100 fps</td><td><span class="badge badge-green">Online</span></td></tr>
              <tr><td>#5</td><td><code>192.168.1.84</code></td><td>NVIDIA RTX 3070</td><td>20.3 TFLOPS</td><td>184 (3rd Gen)</td><td>1,420 fps</td><td><span class="badge badge-green">Online</span></td></tr>
            </tbody>
          </table>
        </div>
      </div>
    `;
  },

  async load() {
    try {
      const data = await window.apiClient.getGpuBenchmarks();
      // Benchmarks loaded
    } catch (_) {}
  }
};
