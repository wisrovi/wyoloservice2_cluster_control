/**
 * Storage Infrastructure, CIFS Volumes & MinIO S3 View (storage.volumes)
 * Displays shared Samba CIFS dataset volumes, disk space, MinIO S3 buckets, and path validation.
 */

window.ViewStorage = {
  id: "storage",
  label: "Storage & Volumes",
  icon: "📁",
  file: "storage.volumes",
  category: "storage",

  render() {
    return `
      <div class="view-header">
        <div class="view-title-group">
          <h1><span>📁</span> Storage Infrastructure, CIFS Volumes & MinIO S3</h1>
          <p>Shared Samba CIFS datasets volume, disk capacity, MinIO S3 artifact buckets, and path integrity</p>
        </div>
        <div class="view-actions">
          <button class="btn btn-primary btn-sm" onclick="window.ViewStorage.load()">
            <span>🔄</span> Refresh Storage
          </button>
        </div>
      </div>

      <!-- Metrics Ribbon -->
      <div class="metrics-ribbon">
        <div class="metric-card">
          <div class="metric-label">Total Mapped Capacity</div>
          <div class="metric-value" id="storage-total-cap">0.0 GB</div>
          <div class="metric-sub" id="storage-free-sub">0.0 GB available</div>
        </div>
        <div class="metric-card">
          <div class="metric-label">Samba CIFS Volume</div>
          <div class="metric-value" id="storage-samba-status" style="color: #10B981;">Online</div>
          <div class="metric-sub">/home/yolo/shared (Samba)</div>
        </div>
        <div class="metric-card">
          <div class="metric-label">MinIO S3 Buckets</div>
          <div class="metric-value" id="storage-minio-count" style="color: #007ACC;">4 Active</div>
          <div class="metric-sub">Checkpoints & MLflow Artifacts</div>
        </div>
        <div class="metric-card">
          <div class="metric-label">Storage Health</div>
          <div class="metric-value" id="storage-overall-status" style="color: #10B981;">HEALTHY</div>
          <div class="metric-sub">Low I/O Latency (&lt; 2ms)</div>
        </div>
      </div>

      <!-- Section 1: Shared Storage Volumes & Disk Capacity -->
      <div class="card-section" style="margin-bottom: 20px;">
        <div class="card-title">
          <span>🖥️ Mapped Storage Volumes & Disk Utilization</span>
        </div>
        <div class="table-responsive">
          <table class="vscode-table">
            <thead>
              <tr>
                <th>Volume Name</th>
                <th>Mount Point</th>
                <th>Usage (Used / Total)</th>
                <th>Capacity Bar</th>
                <th>Latency</th>
                <th>Access Mode</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody id="storage-volumes-tbody">
              <tr><td colspan="7" style="text-align: center; color: var(--vscode-fg-muted); padding: 16px;">Scanning storage volumes...</td></tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Section 2: MinIO S3 Object Storage Buckets -->
      <div class="card-section" style="margin-bottom: 20px;">
        <div class="card-title">
          <span>🪣 MinIO S3 Object Storage Buckets</span>
        </div>
        <div class="table-responsive">
          <table class="vscode-table">
            <thead>
              <tr>
                <th>Bucket Name</th>
                <th>Objects Count</th>
                <th>Stored Size</th>
                <th>Purpose / Artifact Type</th>
                <th>Read/Write Status</th>
              </tr>
            </thead>
            <tbody id="storage-minio-tbody">
              <tr><td colspan="5" style="text-align: center; color: var(--vscode-fg-muted); padding: 16px;">Checking MinIO S3 buckets...</td></tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Section 3: Dataset Path Integrity Inspector -->
      <div class="card-section" style="margin-bottom: 20px;">
        <div class="card-title"><span>🔍 Dataset Path Integrity Inspector</span></div>
        <p style="font-size: 12px; color: var(--vscode-fg-muted); margin-bottom: 12px;">
          Test accessibility and valid layout of datasets on the shared filesystem before submitting tasks.
        </p>
        <div style="display: flex; gap: 8px; margin-bottom: 12px;">
          <input type="text" id="dataset-check-path" class="form-control" placeholder="/wyolo/control_server/datasets/my_dataset" value="/wyolo/control_server/datasets">
          <button class="btn btn-primary" onclick="window.ViewStorage.validateDataset()">
            <span>🔍</span> Validate Path
          </button>
        </div>
        <div id="dataset-validate-result" style="display: none; padding: 12px; border-radius: 4px; font-family: var(--vscode-mono-family); font-size: 12px;"></div>
      </div>

      <!-- Section 4: Detected Datasets on Storage -->
      <div class="card-section">
        <div class="card-title"><span>📂 Detected Datasets on Storage</span></div>
        <div class="table-responsive">
          <table class="vscode-table">
            <thead>
              <tr>
                <th>Dataset Name / Folder</th>
                <th>Format</th>
                <th>Status</th>
                <th>Quick Actions</th>
              </tr>
            </thead>
            <tbody id="datasets-tbody">
              <tr><td colspan="4" style="text-align: center; color: var(--vscode-fg-muted); padding: 16px;">Scanning available datasets...</td></tr>
            </tbody>
          </table>
        </div>
      </div>
    `;
  },

  async load() {
    try {
      const inspect = await window.apiClient.getStorageInspect();
      const volumes = inspect?.volumes || [];
      const minio = inspect?.minio_buckets || [];

      // Update Ribbon
      let totGb = 0;
      let freeGb = 0;
      volumes.forEach(v => {
        totGb += v.total_gb || 0;
        freeGb += v.free_gb || 0;
      });

      document.getElementById("storage-total-cap").textContent = `${totGb.toFixed(1)} GB`;
      document.getElementById("storage-free-sub").textContent = `${freeGb.toFixed(1)} GB available`;
      document.getElementById("storage-minio-count").textContent = `${minio.length} Buckets`;
      
      const overall = inspect?.overall_status || "healthy";
      const statusEl = document.getElementById("storage-overall-status");
      if (statusEl) {
        statusEl.textContent = overall.toUpperCase();
        statusEl.style.color = overall === "healthy" ? "#10B981" : "#F59E0B";
      }

      // Render Volumes Table
      const vTbody = document.getElementById("storage-volumes-tbody");
      if (vTbody) {
        if (!volumes.length) {
          vTbody.innerHTML = `<tr><td colspan="7" style="text-align: center; color: var(--vscode-fg-muted); padding: 16px;">No volumes reported.</td></tr>`;
        } else {
          vTbody.innerHTML = volumes.map(v => {
            const pct = v.percent_used || 0;
            return `
              <tr>
                <td><strong>${v.name}</strong></td>
                <td><code>${v.mount_path}</code></td>
                <td><strong>${v.used_gb} GB</strong> / ${v.total_gb} GB</td>
                <td>
                  <div style="display: flex; align-items: center; gap: 8px;">
                    <div style="flex: 1; min-width: 80px; height: 6px; background: #333; border-radius: 3px; overflow: hidden;">
                      <div style="width: ${pct}%; height: 100%; background: ${pct > 85 ? '#EF4444' : '#007ACC'};"></div>
                    </div>
                    <span style="font-size: 11px; width: 40px;">${pct}%</span>
                  </div>
                </td>
                <td><code>${v.latency_ms ? v.latency_ms + ' ms' : '< 1ms'}</code></td>
                <td><span class="badge badge-blue">${v.permissions || 'read/write'}</span></td>
                <td><span class="badge badge-green">${v.status || 'Online'}</span></td>
              </tr>
            `;
          }).join("");
        }
      }

      // Render MinIO Table
      const mTbody = document.getElementById("storage-minio-tbody");
      if (mTbody) {
        if (!minio.length) {
          mTbody.innerHTML = `<tr><td colspan="5" style="text-align: center; color: var(--vscode-fg-muted); padding: 16px;">No MinIO buckets found.</td></tr>`;
        } else {
          mTbody.innerHTML = minio.map(b => `
            <tr>
              <td><code><strong>${b.name}</strong></code></td>
              <td>${b.objects_count || 0} objects</td>
              <td><strong>${b.size_mb ? (b.size_mb >= 1024 ? (b.size_mb/1024).toFixed(2) + ' GB' : b.size_mb + ' MB') : '0 MB'}</strong></td>
              <td style="color: var(--vscode-fg-muted); font-size: 11px;">${b.name.includes("checkpoint") ? "Model weights & best.pt" : (b.name.includes("mlflow") ? "MLflow metrics & parameters" : "Generated reports & XAI visuals")}</td>
              <td><span class="badge badge-green">${b.status || 'Active'}</span></td>
            </tr>
          `).join("");
        }
      }

      // Render Datasets Table
      const datasets = await window.apiClient.getDatasetsAvailable();
      const dItems = datasets?.datasets || [];
      const dTbody = document.getElementById("datasets-tbody");

      if (dTbody) {
        if (!dItems.length) {
          dTbody.innerHTML = `<tr><td colspan="4" style="text-align: center; color: var(--vscode-fg-muted); padding: 16px;">No datasets detected on Samba share.</td></tr>`;
        } else {
          dTbody.innerHTML = dItems.map(d => {
            const dName = typeof d === 'string' ? d : (d.name || d.path || 'dataset');
            const dPath = typeof d === 'string' ? d : (d.path || `/wyolo/control_server/datasets/${dName}`);
            return `
              <tr>
                <td><strong>${dName}</strong><br><span style="font-size: 10px; color: var(--vscode-fg-muted);"><code>${dPath}</code></span></td>
                <td><span class="badge badge-blue">YOLO Format</span></td>
                <td><span class="badge badge-green">Ready</span></td>
                <td>
                  <button class="btn btn-secondary btn-sm" onclick="window.ViewStorage.quickValidate('${dPath}')">
                    🔍 Inspect & Validate
                  </button>
                </td>
              </tr>
            `;
          }).join("");
        }
      }
    } catch (e) {
      window.workbench.logTerminal("ERROR", `Failed to load storage telemetry: ${e.message}`);
    }
  },

  async validateDataset() {
    const path = document.getElementById("dataset-check-path").value.trim();
    if (!path) return;
    const resEl = document.getElementById("dataset-validate-result");
    resEl.style.display = "block";
    resEl.style.backgroundColor = "#2D2D2D";
    resEl.style.color = "var(--vscode-fg-primary)";
    resEl.textContent = `Validating dataset path: ${path}...`;

    try {
      const res = await window.apiClient.validateDataset(path);
      resEl.style.backgroundColor = "rgba(16, 185, 129, 0.15)";
      resEl.style.border = "1px solid rgba(16, 185, 129, 0.3)";
      resEl.style.color = "#10B981";
      resEl.innerHTML = `✅ <strong>[VALID]</strong> Dataset path exists and is accessible.<br>Details: <code>${JSON.stringify(res, null, 2)}</code>`;
      window.workbench.logTerminal("SUCCESS", `Dataset validation passed for: ${path}`);
    } catch (e) {
      resEl.style.backgroundColor = "rgba(239, 68, 68, 0.15)";
      resEl.style.border = "1px solid rgba(239, 68, 68, 0.3)";
      resEl.style.color = "#EF4444";
      resEl.textContent = `[INVALID] Error checking path: ${e.message}`;
      window.workbench.logTerminal("ERROR", `Dataset validation error: ${e.message}`);
    }
  },

  quickValidate(path) {
    document.getElementById("dataset-check-path").value = path;
    this.validateDataset();
  }
};
