/**
 * Cluster GPU Benchmarks & Throughput Leaderboard View (benchmarks.gpu)
 * Live performance profiles, measured image throughput, epoch duration, and node mapping.
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
          <p>Empirical performance analysis, tensor operations throughput, and measured 100-epoch training benchmarks</p>
        </div>
        <div class="view-actions">
          <button class="btn btn-primary btn-sm" onclick="window.ViewBenchmarks.load()">
            <span>🔄</span> Refresh Benchmarks
          </button>
        </div>
      </div>

      <div class="metrics-ribbon">
        <div class="metric-card">
          <div class="metric-label">Top Measured Throughput</div>
          <div class="metric-value" id="bench-top-tput" style="color: #10B981;">128.5 img/s</div>
          <div class="metric-sub">NVIDIA RTX 4090</div>
        </div>
        <div class="metric-card">
          <div class="metric-label">Fastest 100-Epoch Duration</div>
          <div class="metric-value" id="bench-fastest-time" style="color: #007ACC;">7.0 min</div>
          <div class="metric-sub">4.2s per epoch</div>
        </div>
        <div class="metric-card">
          <div class="metric-label">Benchmarked Hardware Classes</div>
          <div class="metric-value" id="bench-gpu-classes">6 Models</div>
          <div class="metric-sub">Empirically profiled</div>
        </div>
        <div class="metric-card">
          <div class="metric-label">Total Completed Studies</div>
          <div class="metric-value" id="bench-total-studies">349 Studies</div>
          <div class="metric-sub">Historical test baseline</div>
        </div>
      </div>

      <div class="card-section">
        <div class="card-title">
          <span>GPU Architecture Performance Rankings</span>
          <span class="badge badge-blue" id="bench-updated-badge">Empirical</span>
        </div>
        <div class="table-responsive">
          <table class="vscode-table">
            <thead>
              <tr>
                <th style="width: 50px;">Rank</th>
                <th>GPU Model & Architecture</th>
                <th>Avg Throughput (img/s)</th>
                <th>Avg Epoch Time</th>
                <th>Est. 100 Epochs</th>
                <th>Benchmark Sample Studies</th>
                <th>Deployed Nodes (Cluster Equipment)</th>
              </tr>
            </thead>
            <tbody id="benchmarks-tbody">
              <tr><td colspan="7" style="text-align: center; color: var(--vscode-fg-muted); padding: 16px;">Loading empirical benchmark data...</td></tr>
            </tbody>
          </table>
        </div>
      </div>
    `;
  },

  async load() {
    const tbody = document.getElementById("benchmarks-tbody");
    try {
      const data = await window.apiClient.getGpuBenchmarks();
      const list = data?.benchmarks || [];

      if (!list.length) {
        tbody.innerHTML = `<tr><td colspan="7" style="text-align: center; color: var(--vscode-fg-muted); padding: 16px;">No empirical benchmark profiles available.</td></tr>`;
        return;
      }

      // Update summary cards
      const topTput = Math.max(...list.map(b => b.avg_throughput_img_s || 0));
      const fastest = Math.min(...list.map(b => b.estimated_100_epochs_min || 999));
      const totalStudies = list.reduce((acc, b) => acc + (b.completed_studies_count || 0), 0);

      document.getElementById("bench-top-tput").textContent = `${topTput.toFixed(1)} img/s`;
      document.getElementById("bench-fastest-time").textContent = `${fastest.toFixed(1)} min`;
      document.getElementById("bench-gpu-classes").textContent = `${list.length} Models`;
      document.getElementById("bench-total-studies").textContent = `${totalStudies} Studies`;
      if (data.updated_at) {
        document.getElementById("bench-updated-badge").textContent = `Updated: ${data.updated_at.split(" ")[0]}`;
      }

      const medals = ["🥇 #1", "🥈 #2", "🥉 #3", "#4", "#5", "#6", "#7"];

      tbody.innerHTML = list.map((b, idx) => {
        const medal = medals[idx] || `#${idx + 1}`;
        const workers = (b.sample_workers || []).map(ip => `<code>${ip}</code>`).join(", ") || '<span style="color: var(--vscode-fg-muted);">Unassigned</span>';

        return `
          <tr style="${idx === 0 ? 'background: rgba(16, 185, 129, 0.08); font-weight: 500;' : ''}">
            <td style="font-weight: 600; color: ${idx === 0 ? '#10B981' : 'inherit'};">${medal}</td>
            <td>
              <div style="font-weight: 600; color: var(--vscode-fg-bright);">${b.gpu_model}</div>
            </td>
            <td>
              <span style="color: #10B981; font-weight: 600;">${b.avg_throughput_img_s} img/s</span>
            </td>
            <td><code>${b.avg_epoch_seconds}s</code> / epoch</td>
            <td><strong>~${b.estimated_100_epochs_min} min</strong></td>
            <td><span class="badge badge-blue">${b.completed_studies_count} studies</span></td>
            <td>${workers}</td>
          </tr>
        `;
      }).join("");
    } catch (e) {
      tbody.innerHTML = `<tr><td colspan="7" style="text-align: center; color: var(--vscode-btn-danger); padding: 16px;">Failed to load benchmarks: ${e.message}</td></tr>`;
    }
  }
};
