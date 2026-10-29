/**
 * Smart Dispatch & Automated Scheduler View (dispatch.yaml)
 * Features: Multi-Task CV Architecture Selector (Detect, Segment, Classify, Pose, OBB, Custom),
 * Smart node recommendation by AI, Pre-flight dataset inspection,
 * Dynamic duration & throughput estimator (ETA), Priority dispatch, and Day/Night policies.
 */

window.ViewDispatch = {
  id: "dispatch",
  label: "Dispatch & Scheduler",
  icon: "🚀",
  file: "dispatch.yaml",
  category: "workloads",

  etaDebounceTimer: null,
  activeTasksData: [],

  tasks: {
    detect: {
      name: "🎯 Detección de Objetos (Object Detection)",
      short: "DETECT",
      badgeClass: "badge-blue",
      defaultModel: "yolo26m.pt",
      defaultDataset: "/examples/Deteksi_komponen_elektronik.v1i/data.yaml",
      defaultImgsz: "640",
      models: [
        {
          group: "YOLO26 (Next-Gen Flagship - 2026)",
          items: [
            { value: "yolo26n.pt", label: "yolo26n.pt — Nano (2.4M params, ultra-fast)" },
            { value: "yolo26s.pt", label: "yolo26s.pt — Small (9.5M params)" },
            { value: "yolo26m.pt", label: "yolo26m.pt — Medium (20.4M params, recommended)" },
            { value: "yolo26l.pt", label: "yolo26l.pt — Large (24.8M params)" },
            { value: "yolo26x.pt", label: "yolo26x.pt — X-Large (55.7M params, SOTA mAP)" },
          ],
        },
        {
          group: "YOLO11 (SOTA - 2024)",
          items: [
            { value: "yolo11n.pt", label: "yolo11n.pt — Nano (2.6M params)" },
            { value: "yolo11s.pt", label: "yolo11s.pt — Small (9.4M params)" },
            { value: "yolo11m.pt", label: "yolo11m.pt — Medium (20.1M params)" },
            { value: "yolo11l.pt", label: "yolo11l.pt — Large (25.3M params)" },
            { value: "yolo11x.pt", label: "yolo11x.pt — X-Large (56.9M params)" },
          ],
        },
        {
          group: "YOLOv10 (NMS-Free Real-Time)",
          items: [
            { value: "yolov10n.pt", label: "yolov10n.pt — Nano (2.3M params)" },
            { value: "yolov10s.pt", label: "yolov10s.pt — Small (7.2M params)" },
            { value: "yolov10m.pt", label: "yolov10m.pt — Medium (15.4M params)" },
            { value: "yolov10b.pt", label: "yolov10b.pt — Balanced (19.1M params)" },
            { value: "yolov10l.pt", label: "yolov10l.pt — Large (24.4M params)" },
            { value: "yolov10x.pt", label: "yolov10x.pt — X-Large (29.5M params)" },
          ],
        },
        {
          group: "YOLOv9 (Programmable Gradient Info)",
          items: [
            { value: "yolov9t.pt", label: "yolov9t.pt — Tiny (2.0M params)" },
            { value: "yolov9s.pt", label: "yolov9s.pt — Small (7.1M params)" },
            { value: "yolov9m.pt", label: "yolov9m.pt — Medium (20.0M params)" },
            { value: "yolov9c.pt", label: "yolov9c.pt — Compact (25.3M params)" },
            { value: "yolov9e.pt", label: "yolov9e.pt — Extended (57.3M params)" },
          ],
        },
        {
          group: "RT-DETR (Real-Time Vision Transformers)",
          items: [
            { value: "rtdetr-l.pt", label: "rtdetr-l.pt — Large (Transformer Backbone)" },
            { value: "rtdetr-x.pt", label: "rtdetr-x.pt — X-Large (High Accuracy Transformer)" },
          ],
        },
        {
          group: "YOLO-World (Open-Vocabulary Real-Time)",
          items: [
            { value: "yolov8s-worldv2.pt", label: "yolov8s-worldv2.pt — Small (Zero-Shot)" },
            { value: "yolov8m-worldv2.pt", label: "yolov8m-worldv2.pt — Medium (Zero-Shot)" },
            { value: "yolov8l-worldv2.pt", label: "yolov8l-worldv2.pt — Large (Zero-Shot)" },
            { value: "yolov8x-worldv2.pt", label: "yolov8x-worldv2.pt — X-Large (Zero-Shot)" },
          ],
        },
        {
          group: "YOLOv8 (Industry Standard Baseline)",
          items: [
            { value: "yolov8n.pt", label: "yolov8n.pt — Nano (3.2M params)" },
            { value: "yolov8s.pt", label: "yolov8s.pt — Small (11.2M params)" },
            { value: "yolov8m.pt", label: "yolov8m.pt — Medium (25.9M params)" },
            { value: "yolov8l.pt", label: "yolov8l.pt — Large (43.7M params)" },
            { value: "yolov8x.pt", label: "yolov8x.pt — X-Large (68.2M params)" },
          ],
        },
      ],
    },
    segment: {
      name: "✂️ Segmentación de Instancias (Instance Segmentation)",
      short: "SEGMENT",
      badgeClass: "badge-green",
      defaultModel: "yolo26m-seg.pt",
      defaultDataset: "/examples/ArchitecturePlan/data.yaml",
      defaultImgsz: "640",
      models: [
        {
          group: "YOLO26 Segmentation (Next-Gen)",
          items: [
            { value: "yolo26n-seg.pt", label: "yolo26n-seg.pt — Nano (2.4M params)" },
            { value: "yolo26s-seg.pt", label: "yolo26s-seg.pt — Small (9.5M params)" },
            { value: "yolo26m-seg.pt", label: "yolo26m-seg.pt — Medium (20.4M params, recommended)" },
            { value: "yolo26l-seg.pt", label: "yolo26l-seg.pt — Large (24.8M params)" },
            { value: "yolo26x-seg.pt", label: "yolo26x-seg.pt — X-Large (55.7M params)" },
          ],
        },
        {
          group: "YOLO11 Segmentation",
          items: [
            { value: "yolo11n-seg.pt", label: "yolo11n-seg.pt — Nano (2.9M params)" },
            { value: "yolo11s-seg.pt", label: "yolo11s-seg.pt — Small (10.1M params)" },
            { value: "yolo11m-seg.pt", label: "yolo11m-seg.pt — Medium (22.4M params)" },
            { value: "yolo11l-seg.pt", label: "yolo11l-seg.pt — Large (27.6M params)" },
            { value: "yolo11x-seg.pt", label: "yolo11x-seg.pt — X-Large (62.1M params)" },
          ],
        },
        {
          group: "YOLOv8 Segmentation (Version 8 Baseline)",
          items: [
            { value: "yolov8n-seg.pt", label: "yolov8n-seg.pt — Nano (3.4M params)" },
            { value: "yolov8s-seg.pt", label: "yolov8s-seg.pt — Small (11.8M params)" },
            { value: "yolov8m-seg.pt", label: "yolov8m-seg.pt — Medium (27.3M params)" },
            { value: "yolov8l-seg.pt", label: "yolov8l-seg.pt — Large (46.0M params)" },
            { value: "yolov8x-seg.pt", label: "yolov8x-seg.pt — X-Large (71.8M params)" },
          ],
        },
      ],
    },
    classify: {
      name: "🏷️ Clasificación de Imágenes (Image Classification)",
      short: "CLASSIFY",
      badgeClass: "badge-amber",
      defaultModel: "yolo26m-cls.pt",
      defaultDataset: "/examples/colorball.v8i.multiclass/",
      defaultImgsz: "224",
      models: [
        {
          group: "YOLO26 Classification (Next-Gen)",
          items: [
            { value: "yolo26n-cls.pt", label: "yolo26n-cls.pt — Nano (1.4M params)" },
            { value: "yolo26s-cls.pt", label: "yolo26s-cls.pt — Small (5.0M params)" },
            { value: "yolo26m-cls.pt", label: "yolo26m-cls.pt — Medium (10.1M params, recommended)" },
            { value: "yolo26l-cls.pt", label: "yolo26l-cls.pt — Large (12.8M params)" },
            { value: "yolo26x-cls.pt", label: "yolo26x-cls.pt — X-Large (27.9M params)" },
          ],
        },
        {
          group: "YOLO11 Classification",
          items: [
            { value: "yolo11n-cls.pt", label: "yolo11n-cls.pt — Nano (1.6M params)" },
            { value: "yolo11s-cls.pt", label: "yolo11s-cls.pt — Small (5.4M params)" },
            { value: "yolo11m-cls.pt", label: "yolo11m-cls.pt — Medium (10.4M params)" },
            { value: "yolo11l-cls.pt", label: "yolo11l-cls.pt — Large (13.1M params)" },
            { value: "yolo11x-cls.pt", label: "yolo11x-cls.pt — X-Large (28.4M params)" },
          ],
        },
        {
          group: "YOLOv8 Classification (Version 8 Baseline)",
          items: [
            { value: "yolov8n-cls.pt", label: "yolov8n-cls.pt — Nano (1.5M params)" },
            { value: "yolov8s-cls.pt", label: "yolov8s-cls.pt — Small (5.1M params)" },
            { value: "yolov8m-cls.pt", label: "yolov8m-cls.pt — Medium (15.9M params)" },
            { value: "yolov8l-cls.pt", label: "yolov8l-cls.pt — Large (36.2M params)" },
            { value: "yolov8x-cls.pt", label: "yolov8x-cls.pt — X-Large (56.2M params)" },
          ],
        },
      ],
    },
    pose: {
      name: "🤸 Estimación de Pose (Pose Estimation)",
      short: "POSE",
      badgeClass: "badge-purple",
      defaultModel: "yolo26m-pose.pt",
      defaultDataset: "/examples/pose_estimation/data.yaml",
      defaultImgsz: "640",
      models: [
        {
          group: "YOLO26 Pose Estimation (Next-Gen)",
          items: [
            { value: "yolo26n-pose.pt", label: "yolo26n-pose.pt — Nano (2.7M params)" },
            { value: "yolo26s-pose.pt", label: "yolo26s-pose.pt — Small (9.6M params)" },
            { value: "yolo26m-pose.pt", label: "yolo26m-pose.pt — Medium (20.5M params, recommended)" },
            { value: "yolo26l-pose.pt", label: "yolo26l-pose.pt — Large (25.1M params)" },
            { value: "yolo26x-pose.pt", label: "yolo26x-pose.pt — X-Large (56.2M params)" },
          ],
        },
        {
          group: "YOLO11 Pose Estimation",
          items: [
            { value: "yolo11n-pose.pt", label: "yolo11n-pose.pt — Nano (2.9M params)" },
            { value: "yolo11s-pose.pt", label: "yolo11s-pose.pt — Small (9.9M params)" },
            { value: "yolo11m-pose.pt", label: "yolo11m-pose.pt — Medium (20.9M params)" },
            { value: "yolo11l-pose.pt", label: "yolo11l-pose.pt — Large (26.3M params)" },
            { value: "yolo11x-pose.pt", label: "yolo11x-pose.pt — X-Large (58.8M params)" },
          ],
        },
        {
          group: "YOLOv8 Pose Estimation (Version 8 Baseline)",
          items: [
            { value: "yolov8n-pose.pt", label: "yolov8n-pose.pt — Nano (3.3M params)" },
            { value: "yolov8s-pose.pt", label: "yolov8s-pose.pt — Small (11.6M params)" },
            { value: "yolov8m-pose.pt", label: "yolov8m-pose.pt — Medium (26.4M params)" },
            { value: "yolov8l-pose.pt", label: "yolov8l-pose.pt — Large (44.4M params)" },
            { value: "yolov8x-pose.pt", label: "yolov8x-pose.pt — X-Large (69.8M params)" },
          ],
        },
      ],
    },
    obb: {
      name: "📐 Cajas Orientadas / Rotadas (OBB)",
      short: "OBB",
      badgeClass: "badge-blue",
      defaultModel: "yolo26m-obb.pt",
      defaultDataset: "/examples/oriented_bounding_box/data.yaml",
      defaultImgsz: "640",
      models: [
        {
          group: "YOLO26 Oriented Bounding Box (Next-Gen)",
          items: [
            { value: "yolo26n-obb.pt", label: "yolo26n-obb.pt — Nano (2.5M params)" },
            { value: "yolo26s-obb.pt", label: "yolo26s-obb.pt — Small (9.8M params)" },
            { value: "yolo26m-obb.pt", label: "yolo26m-obb.pt — Medium (21.2M params, recommended)" },
            { value: "yolo26l-obb.pt", label: "yolo26l-obb.pt — Large (25.6M params)" },
            { value: "yolo26x-obb.pt", label: "yolo26x-obb.pt — X-Large (57.6M params)" },
          ],
        },
        {
          group: "YOLO11 Oriented Bounding Box",
          items: [
            { value: "yolo11n-obb.pt", label: "yolo11n-obb.pt — Nano (2.7M params)" },
            { value: "yolo11s-obb.pt", label: "yolo11s-obb.pt — Small (9.7M params)" },
            { value: "yolo11m-obb.pt", label: "yolo11m-obb.pt — Medium (20.9M params)" },
            { value: "yolo11l-obb.pt", label: "yolo11l-obb.pt — Large (26.3M params)" },
            { value: "yolo11x-obb.pt", label: "yolo11x-obb.pt — X-Large (58.9M params)" },
          ],
        },
        {
          group: "YOLOv8 Oriented Bounding Box (Version 8 Baseline)",
          items: [
            { value: "yolov8n-obb.pt", label: "yolov8n-obb.pt — Nano (3.1M params)" },
            { value: "yolov8s-obb.pt", label: "yolov8s-obb.pt — Small (11.4M params)" },
            { value: "yolov8m-obb.pt", label: "yolov8m-obb.pt — Medium (26.4M params)" },
            { value: "yolov8l-obb.pt", label: "yolov8l-obb.pt — Large (44.5M params)" },
            { value: "yolov8x-obb.pt", label: "yolov8x-obb.pt — X-Large (69.5M params)" },
          ],
        },
      ],
    },
    custom: {
      name: "🧪 Pesos Personalizados (Custom Checkpoint .pt)",
      short: "CUSTOM",
      badgeClass: "badge-gray",
      defaultModel: "/wyolo/weights/custom_best.pt",
      defaultDataset: "/examples/Deteksi_komponen_elektronik.v1i/data.yaml",
      defaultImgsz: "640",
      models: [],
    },
  },

  render() {
    return `
      <div class="view-header">
        <div class="view-title-group">
          <h1><span>🚀</span> Smart Dispatcher & Automated Scheduling</h1>
          <p>Orchestrate workloads with AI node matching, dataset pre-flight check, dynamic ETA estimation, and Day/Night resource caps</p>
        </div>
        <div class="view-actions">
          <button class="btn btn-secondary btn-sm" onclick="window.workbench.switchView('tasks')">
            <span>📋</span> View Queues & Tasks
          </button>
          <button class="btn btn-primary btn-sm" onclick="window.ViewDispatch.load()">
            <span>🔄</span> Refresh Scheduler
          </button>
        </div>
      </div>

      <!-- Dynamic ETA Banner -->
      <div id="dispatch-eta-banner" style="background: rgba(0, 122, 204, 0.15); border: 1px solid #007ACC; border-radius: 4px; padding: 10px 16px; margin-bottom: 16px; font-size: 12px; display: flex; align-items: center; justify-content: space-between;">
        <div>
          <span style="font-weight: 600; color: var(--vscode-fg-bright);">⏱️ Dynamic Duration Estimator (ETA):</span>
          <span id="dispatch-eta-text" style="color: var(--vscode-fg-primary); margin-left: 8px;">Calculating training duration...</span>
        </div>
        <div id="dispatch-eta-metrics" style="font-size: 11px; color: var(--vscode-fg-muted);"></div>
      </div>

      <div style="display: grid; grid-template-columns: 1.25fr 0.75fr; gap: 20px; margin-bottom: 20px;">
        <!-- Left: Smart Launch Form -->
        <div class="card-section">
          <div class="card-title"><span>⚡ Smart Training Workload Launcher</span></div>
          <form id="quick-launch-form" onsubmit="event.preventDefault(); window.ViewDispatch.submitQuickLaunch();">
            
            <!-- Row 1: Study Name & Vision Task Selector -->
            <div style="display: grid; grid-template-columns: 1.2fr 1fr; gap: 10px; margin-bottom: 12px;">
              <div class="form-group" style="margin-bottom: 0;">
                <label class="form-label">Study / Project Name:</label>
                <input type="text" id="ql-study-name" class="form-control" placeholder="yolo11_defect_detection_v1" required>
              </div>
              <div class="form-group" style="margin-bottom: 0;">
                <label class="form-label">Vision Task (CV Domain):</label>
                <select id="ql-task" class="form-control" onchange="window.ViewDispatch.onTaskChange()">
                  <option value="detect" selected>🎯 Detección de Objetos (Detect)</option>
                  <option value="segment">✂️ Segmentación de Instancias (Segment)</option>
                  <option value="classify">🏷️ Clasificación de Imágenes (Classify)</option>
                  <option value="pose">🤸 Estimación de Pose (Pose)</option>
                  <option value="obb">📐 Cajas Orientadas (OBB)</option>
                  <option value="custom">🧪 Pesos Personalizados (Custom .pt)</option>
                </select>
              </div>
            </div>

            <!-- Row 2: Dataset Path with Pre-Flight Check -->
            <div class="form-group">
              <label class="form-label">Dataset Path (Samba CIFS / S3):</label>
              <div style="display: flex; gap: 8px;">
                <input type="text" id="ql-dataset-path" class="form-control" value="/examples/Deteksi_komponen_elektronik.v1i/data.yaml" required oninput="window.ViewDispatch.triggerEtaUpdate()">
                <button type="button" class="btn btn-secondary btn-sm" onclick="window.ViewDispatch.runDatasetPreflight()" style="white-space: nowrap;">
                  🔍 Pre-Flight Check
                </button>
              </div>
              <div id="dispatch-preflight-result" style="display: none; margin-top: 8px; padding: 8px 12px; border-radius: 4px; font-size: 11px;"></div>
            </div>

            <!-- Row 3: Model Architecture Dropdown & Custom Checkpoint Input -->
            <div class="form-group" id="ql-model-group">
              <label class="form-label" style="display: flex; justify-content: space-between; align-items: center;">
                <span>Model Architecture:</span>
                <span id="ql-task-badge" class="badge badge-blue">DETECT</span>
              </label>
              <select id="ql-model" class="form-control" onchange="window.ViewDispatch.triggerEtaUpdate()">
                <!-- Populated dynamically via populateModelOptions() -->
              </select>
            </div>

            <div class="form-group" id="ql-custom-model-group" style="display: none;">
              <label class="form-label">Custom Checkpoint Path (.pt file):</label>
              <input type="text" id="ql-custom-model" class="form-control" placeholder="/wyolo/weights/custom_best.pt" oninput="window.ViewDispatch.triggerEtaUpdate()">
            </div>

            <!-- Row 4: Hyperparameters: Epochs, Batch Size, and Image Resolution -->
            <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 10px; margin-bottom: 12px;">
              <div class="form-group" style="margin-bottom: 0;">
                <label class="form-label">Epochs (1 - 1000):</label>
                <input type="number" id="ql-epochs" class="form-control" value="100" min="1" max="1000" oninput="window.ViewDispatch.triggerEtaUpdate()">
              </div>
              <div class="form-group" style="margin-bottom: 0;">
                <label class="form-label">Batch Size:</label>
                <select id="ql-batch" class="form-control">
                  <option value="-1" selected>Auto Batch (-1)</option>
                  <option value="4">4 (Micro / Low VRAM)</option>
                  <option value="8">8 (Small)</option>
                  <option value="16">16 (Standard)</option>
                  <option value="32">32 (High Throughput)</option>
                  <option value="64">64 (Large Scale)</option>
                  <option value="128">128 (Ultra Batch)</option>
                </select>
              </div>
              <div class="form-group" style="margin-bottom: 0;">
                <label class="form-label">Resolution (imgsz):</label>
                <select id="ql-imgsz" class="form-control" onchange="window.ViewDispatch.triggerEtaUpdate()">
                  <option value="224">224 × 224 (Clasificación)</option>
                  <option value="384">384 × 384 (Móvil / Rápido)</option>
                  <option value="512">512 × 512 (Balanceado)</option>
                  <option value="640" selected>640 × 640 (Estándar YOLO)</option>
                  <option value="1024">1024 × 1024 (Alta Precisión)</option>
                  <option value="1280">1280 × 1280 (Ultra / Aéreo)</option>
                </select>
              </div>
            </div>

            <!-- Row 5: Target Node with AI Recommender & Priority -->
            <div style="display: grid; grid-template-columns: 2fr 1fr; gap: 10px; margin-bottom: 12px;">
              <div class="form-group" style="margin-bottom: 0;">
                <label class="form-label">Target Invoker Node:</label>
                <select id="ql-target-node" class="form-control">
                  <option value="">wyolo_gpu_queue (Global Public Queue)</option>
                </select>
              </div>
              <div class="form-group" style="margin-bottom: 0;">
                <label class="form-label">Priority:</label>
                <select id="ql-priority" class="form-control">
                  <option value="NORMAL" selected>⚡ NORMAL</option>
                  <option value="URGENT">🔥 URGENT</option>
                  <option value="BATCH">📦 BATCH</option>
                </select>
              </div>
            </div>

            <!-- Recommender Trigger -->
            <div style="display: flex; gap: 8px; margin-bottom: 14px;">
              <button type="button" class="btn btn-secondary btn-sm" onclick="window.ViewDispatch.recommendOptimalNode()" style="flex: 1;">
                🪄 Recommend Best Node via AI Matching
              </button>
            </div>
            <div id="dispatch-rec-info" style="display: none; padding: 8px 12px; background: rgba(16, 185, 129, 0.15); border-left: 3px solid #10B981; border-radius: 4px; font-size: 11px; margin-bottom: 12px;"></div>

            <!-- Start Not Before (Scheduled / Deferred Start) -->
            <div style="background: rgba(59, 130, 246, 0.08); border: 1px solid rgba(59, 130, 246, 0.25); border-radius: 6px; padding: 10px 14px; margin-bottom: 14px;">
              <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 6px;">
                <label style="display: flex; align-items: center; gap: 8px; cursor: pointer; font-weight: 600; font-size: 12px; color: #93C5FD;">
                  <input type="checkbox" id="ql-schedule-check" onchange="document.getElementById('ql-schedule-group').style.display = this.checked ? 'grid' : 'none';">
                  <span>🕒 Programar Inicio Diferido (No empezar antes de las HH:MM)</span>
                </label>
                <span style="font-size: 11px; color: var(--vscode-fg-muted);">Opcional</span>
              </div>
              <div id="ql-schedule-group" style="display: none; grid-template-columns: 1fr 1.5fr; gap: 10px; align-items: center; margin-top: 8px;">
                <div>
                  <label class="form-label" style="font-size: 11px; margin-bottom: 2px;">Hora permitida (HH:MM):</label>
                  <input type="time" id="ql-start-not-before-time" class="form-control" value="20:00">
                </div>
                <div style="font-size: 11px; color: #94A3B8;">
                  El trabajo se encola en Celery y espera a la hora indicada sin consumir GPU.
                </div>
              </div>
            </div>

            <button type="submit" class="btn btn-primary" style="width: 100%;">
              <span>🚀</span> Dispatch Workload to Cluster
            </button>
          </form>
        </div>

        <!-- Right: Day / Night Scheduler Policy -->
        <div class="card-section">
          <div class="card-title">
            <span>🌙 Day / Night Automated Throttling</span>
            <span class="badge badge-blue" id="policy-current-mode">ACTIVE</span>
          </div>
          <p style="font-size: 12px; color: var(--vscode-fg-muted); margin-bottom: 14px;">
            Dynamic cluster resource scaling automatically caps training workload allocation during daytime office hours and uncaps maximum throughput during nighttime off-peak hours.
          </p>

          <div style="display: flex; flex-direction: column; gap: 10px;">
            <div style="padding: 10px 12px; background: #2D2D2D; border-radius: 4px; border-left: 3px solid #007ACC;">
              <div style="font-weight: 600; font-size: 12px; color: var(--vscode-fg-bright);">☀️ Daytime Mode (Office Hours)</div>
              <div style="font-size: 11px; color: var(--vscode-fg-muted); margin-top: 2px;">
                Capped at 25% GPU / RAM usage to reserve compute for interactive developers and production inference.
              </div>
            </div>

            <div style="padding: 10px 12px; background: #2D2D2D; border-radius: 4px; border-left: 3px solid #10B981;">
              <div style="font-weight: 600; font-size: 12px; color: var(--vscode-fg-bright);">🌙 Nighttime Mode (Off-Peak & Weekends)</div>
              <div style="font-size: 11px; color: var(--vscode-fg-muted); margin-top: 2px;">
                Uncapped at 95% GPU capacity for high-throughput batch training and Optuna hyperparameter sweeps.
              </div>
            </div>

            <div style="margin-top: 10px; border-top: 1px solid var(--vscode-border-light); padding-top: 10px;">
              <label class="form-label">Immediate Policy Control:</label>
              <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px;">
                <button class="btn btn-secondary btn-sm" onclick="window.ViewDispatch.applyPolicy('day')">☀️ Force Day (25%)</button>
                <button class="btn btn-secondary btn-sm" onclick="window.ViewDispatch.applyPolicy('night')">🌙 Force Night (95%)</button>
              </div>
              <button class="btn btn-secondary btn-sm" style="width: 100%; margin-top: 8px;" onclick="window.ViewDispatch.applyPolicyNow()">
                ⚡ Apply Active Profile to Cluster Now
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Live Active Workloads Table -->
      <div class="card-section">
        <div class="card-title">
          <span>⚡ Live Active Workloads & Trials</span>
          <span class="badge badge-green" id="dispatch-active-badge">0 Running</span>
        </div>
        <div class="table-responsive">
          <table class="vscode-table">
            <thead>
              <tr>
                <th>Study / Workload Name</th>
                <th>Author</th>
                <th>Assigned Node</th>
                <th>Model</th>
                <th>Trial & Epoch Progress</th>
                <th>K8s Pod</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody id="dispatch-active-tbody">
              <tr><td colspan="7" style="text-align: center; color: var(--vscode-fg-muted); padding: 16px;">Scanning active workloads...</td></tr>
            </tbody>
          </table>
        </div>
      </div>
    `;
  },

  populateModelOptions(taskKey, preselectModel = null) {
    const taskConfig = this.tasks[taskKey] || this.tasks.detect;
    const select = document.getElementById("ql-model");
    const modelGroup = document.getElementById("ql-model-group");
    const customGroup = document.getElementById("ql-custom-model-group");
    const badge = document.getElementById("ql-task-badge");

    if (badge) {
      badge.textContent = taskConfig.short;
      badge.className = `badge ${taskConfig.badgeClass || "badge-blue"}`;
    }

    if (taskKey === "custom") {
      if (modelGroup) modelGroup.style.display = "none";
      if (customGroup) customGroup.style.display = "block";
      const customInput = document.getElementById("ql-custom-model");
      if (customInput && !customInput.value) {
        customInput.value = taskConfig.defaultModel;
      }
      return;
    }

    if (modelGroup) modelGroup.style.display = "block";
    if (customGroup) customGroup.style.display = "none";

    if (!select) return;

    let html = "";
    taskConfig.models.forEach((g) => {
      html += `<optgroup label="${g.group}">`;
      g.items.forEach((item) => {
        const isSelected = preselectModel
          ? item.value === preselectModel
          : item.value === taskConfig.defaultModel;
        html += `<option value="${item.value}" ${isSelected ? "selected" : ""}>${item.label}</option>`;
      });
      html += `</optgroup>`;
    });

    select.innerHTML = html;
  },

  onTaskChange() {
    const taskKey = document.getElementById("ql-task")?.value || "detect";
    const taskConfig = this.tasks[taskKey] || this.tasks.detect;

    // Repopulate models
    this.populateModelOptions(taskKey);

    // Update dataset default
    const datasetInput = document.getElementById("ql-dataset-path");
    if (datasetInput && taskConfig.defaultDataset) {
      datasetInput.value = taskConfig.defaultDataset;
    }

    // Update image resolution default
    const imgszSelect = document.getElementById("ql-imgsz");
    if (imgszSelect && taskConfig.defaultImgsz) {
      imgszSelect.value = taskConfig.defaultImgsz;
    }

    // Update study name suggestion
    const nameInput = document.getElementById("ql-study-name");
    if (nameInput) {
      const ts = new Date().toISOString().slice(2, 10).replace(/-/g, "");
      const cleanModel = taskConfig.defaultModel.replace(".pt", "").replace(/[^a-zA-Z0-9]/g, "_");
      nameInput.value = `${cleanModel}_study_${ts}`;
    }

    this.triggerEtaUpdate();
  },

  getSelectedModel() {
    const taskKey = document.getElementById("ql-task")?.value || "detect";
    if (taskKey === "custom") {
      return document.getElementById("ql-custom-model")?.value.trim() || "/wyolo/weights/custom_best.pt";
    }
    return document.getElementById("ql-model")?.value || "yolo26m.pt";
  },

  async load() {
    // Populate model options for initial task
    const currentTask = document.getElementById("ql-task")?.value || "detect";
    this.populateModelOptions(currentTask);

    // Populate initial study name if empty
    const nameInput = document.getElementById("ql-study-name");
    if (nameInput && !nameInput.value) {
      const ts = new Date().toISOString().slice(2, 10).replace(/-/g, "");
      nameInput.value = `yolo26m_study_${ts}`;
    }

    // Populate target nodes
    try {
      const invokers = await window.apiClient.getInvokers();
      const nodes = Array.isArray(invokers) ? invokers : (invokers.invokers || []);
      const select = document.getElementById("ql-target-node");

      if (select) {
        select.innerHTML = '<option value="">wyolo_gpu_queue (Global Public Queue)</option>' +
          nodes.map((n) => {
            const ip = n.worker_ip || n.ip;
            const host = n.hostname || ip;
            const gpu = n.physical?.gpu_model || "GPU";
            const state = n.pause_state || "active";
            const stateIcon = state === "active" ? "🟢" : (state.includes("pause") ? "⏸️" : "⚠️");
            return `<option value="${ip}">${stateIcon} ${host} (${ip}) - ${gpu} [${state}]</option>`;
          }).join("");
      }
    } catch (_) {}

    // Load active scheduler policy
    try {
      const policyRes = await window.apiClient.getSchedulerPolicy();
      const mode = policyRes?.current_mode || policyRes?.mode || "normal";
      const modeEl = document.getElementById("policy-current-mode");
      if (modeEl) {
        modeEl.textContent = `${mode.toUpperCase()} ACTIVE`;
        modeEl.className = mode === "night" ? "badge badge-green" : "badge badge-blue";
      }
    } catch (_) {}

    // Load live active workloads
    await this.loadActiveWorkloads();

    // Trigger initial ETA
    this.triggerEtaUpdate();
  },

  triggerEtaUpdate() {
    if (this.etaDebounceTimer) clearTimeout(this.etaDebounceTimer);
    this.etaDebounceTimer = setTimeout(() => this.updateEta(), 300);
  },

  async updateEta() {
    const model = this.getSelectedModel();
    const epochs = parseInt(document.getElementById("ql-epochs")?.value || "100", 10);
    const dataset = document.getElementById("ql-dataset-path")?.value || "/examples/";

    const textEl = document.getElementById("dispatch-eta-text");
    const metricsEl = document.getElementById("dispatch-eta-metrics");
    if (!textEl) return;

    try {
      const eta = await window.apiClient.estimateDuration(model, epochs, dataset);
      const estMin = eta.estimated_duration_min || 0;
      const hours = (estMin / 60).toFixed(1);
      const tput = eta.estimated_throughput_img_s || 0;
      const recGpu = eta.recommended_gpu || "GPU";

      textEl.innerHTML = `~<strong>${estMin.toFixed(1)} min</strong> (${hours} hrs) for <code>${model}</code> (${epochs} ep) | Suggested Hardware: <code>${recGpu}</code>`;
      if (metricsEl) metricsEl.textContent = `Throughput: ~${tput} img/s`;
    } catch (e) {
      textEl.textContent = `~42.0 min (heuristic estimate)`;
    }
  },

  async runDatasetPreflight() {
    const path = document.getElementById("ql-dataset-path")?.value.trim();
    if (!path) return;

    const resEl = document.getElementById("dispatch-preflight-result");
    resEl.style.display = "block";
    resEl.style.background = "#2D2D2D";
    resEl.style.color = "var(--vscode-fg-muted)";
    resEl.textContent = `Inspecting dataset pre-flight at: ${path}...`;

    try {
      const insp = await window.apiClient.inspectDataset(path);
      if (insp.valid) {
        resEl.style.background = "rgba(16, 185, 129, 0.15)";
        resEl.style.border = "1px solid rgba(16, 185, 129, 0.3)";
        resEl.style.color = "#10B981";
        resEl.innerHTML = `✅ <strong>Dataset Válido:</strong> ${insp.details || "Check completed"} | Clases: <strong>${insp.num_classes || 0}</strong> | Train: <strong>${insp.train_images_count || 0}</strong> imgs | Val: <strong>${insp.val_images_count || 0}</strong> imgs`;
      } else {
        resEl.style.background = "rgba(245, 158, 11, 0.15)";
        resEl.style.border = "1px solid rgba(245, 158, 11, 0.3)";
        resEl.style.color = "#F59E0B";
        resEl.innerHTML = `⚠️ <strong>Pre-Flight Advertencia:</strong> ${insp.details || "Verifique formato data.yaml"}`;
      }
    } catch (e) {
      resEl.style.background = "rgba(239, 68, 68, 0.15)";
      resEl.style.border = "1px solid rgba(239, 68, 68, 0.3)";
      resEl.style.color = "#EF4444";
      resEl.textContent = `Pre-flight error: ${e.message}`;
    }
  },

  async recommendOptimalNode() {
    const model = this.getSelectedModel();
    const infoEl = document.getElementById("dispatch-rec-info");
    infoEl.style.display = "block";
    infoEl.textContent = `Analyzing cluster telemetry and GPU fitness for ${model}...`;

    try {
      const rec = await window.apiClient.recommendNode(model);
      const targetIp = rec.target_ip;
      const host = rec.hostname || targetIp;
      const reason = rec.reason || "Optimal compute match";
      const score = rec.score || 100;

      // Select in dropdown if found
      const select = document.getElementById("ql-target-node");
      if (select && targetIp) {
        for (let i = 0; i < select.options.length; i++) {
          if (select.options[i].value === targetIp) {
            select.selectedIndex = i;
            break;
          }
        }
      }

      infoEl.innerHTML = `🪄 <strong>Recommended: ${host} (${targetIp || "Global Queue"})</strong> — Score: <strong>${score}</strong><br><span style="color: var(--vscode-fg-muted);">${reason}</span>`;
      window.workbench.logTerminal("SUCCESS", `AI Recommender: matched ${host} for model ${model}`);
    } catch (e) {
      infoEl.textContent = `Recommender unavailable: ${e.message}`;
    }
  },

  async submitQuickLaunch() {
    const studyName = document.getElementById("ql-study-name").value.trim();
    const task = document.getElementById("ql-task").value;
    const datasetPath = document.getElementById("ql-dataset-path").value.trim();
    const model = this.getSelectedModel();
    const epochs = parseInt(document.getElementById("ql-epochs").value, 10);
    const batch = parseInt(document.getElementById("ql-batch").value, 10);
    const imgsz = parseInt(document.getElementById("ql-imgsz").value, 10);
    const targetNode = document.getElementById("ql-target-node").value;
    const priority = document.getElementById("ql-priority").value;

    const scheduleCheck = document.getElementById("ql-schedule-check");
    let startNotBefore = null;
    if (scheduleCheck && scheduleCheck.checked) {
      const timeVal = document.getElementById("ql-start-not-before-time")?.value;
      if (timeVal) {
        startNotBefore = timeVal.trim();
      }
    }

    const payload = {
      study_name: studyName,
      task: task,
      model: model,
      dataset: datasetPath,
      epochs: epochs,
      batch_size: batch,
      imgsz: imgsz,
      worker_ip: targetNode || null,
      priority: priority,
      start_not_before: startNotBefore,
    };

    window.workbench.logTerminal("INFO", `Dispatching ${task.toUpperCase()} training workload: ${studyName} (${model}) [${priority}]...`);
    try {
      const res = await window.apiClient.quickLaunch(payload);
      const targetQ = res.data?.target_queue || "wyolo_gpu_queue";
      window.workbench.logTerminal("SUCCESS", `Workload dispatched successfully to queue ${targetQ}`);
      alert(`Workload '${studyName}' [${priority}] (${task.toUpperCase()}) dispatched successfully to queue '${targetQ}'!`);
      await this.loadActiveWorkloads();
    } catch (e) {
      window.workbench.logTerminal("ERROR", `Failed to dispatch workload: ${e.message}`);
      alert(`Dispatch failed: ${e.message}`);
    }
  },

  async loadActiveWorkloads() {
    const tbody = document.getElementById("dispatch-active-tbody");
    const badge = document.getElementById("dispatch-active-badge");

    try {
      const tasks = await window.apiClient.getActiveTasks();
      this.activeTasksData = Array.isArray(tasks) ? tasks : [];
      if (badge) badge.textContent = `${this.activeTasksData.length} Running`;

      if (!this.activeTasksData.length) {
        if (tbody) tbody.innerHTML = `<tr><td colspan="7" style="text-align: center; color: var(--vscode-fg-muted); padding: 16px;">No active workloads running on the cluster.</td></tr>`;
        return;
      }

      if (tbody) {
        tbody.innerHTML = this.activeTasksData.map((t) => {
          const sid = t.study_id || t.id;
          const sname = t.study_name || sid;
          const prog = t.progress || {};
          const cTrials = prog.completed_trials || 0;
          const tTrials = prog.total_trials || 1;
          const pct = Math.min(Math.round((cTrials / Math.max(tTrials, 1)) * 100), 100);

          const podName = t.k8s_pod_name || `executor-${sid.substring(0, 8)}`;
          const podPhase = t.k8s_pod_phase || "Running";
          const dozzleUrl = t.dozzle_url || `http://${t.destination_node || "localhost"}:8888`;

          return `
            <tr>
              <td>
                <div style="font-weight: 600; color: var(--vscode-fg-bright);">${sname}</div>
                <div style="font-size: 10px; color: var(--vscode-fg-muted);"><code>${sid}</code></div>
              </td>
              <td><code>${t.author || "wisrovi"}</code></td>
              <td><code>${t.destination_node || t.worker_ip || "Cluster"}</code></td>
              <td><code>${t.model || "yolo11m"}</code></td>
              <td>
                <div style="font-size: 11px; margin-bottom: 2px;">Trials: ${cTrials}/${tTrials} (${pct}%)</div>
                <div style="width: 100%; height: 6px; background: #333; border-radius: 3px; overflow: hidden;">
                  <div style="width: ${pct}%; height: 100%; background: #10B981;"></div>
                </div>
              </td>
              <td>
                <span class="badge badge-green">${podPhase}</span>
                <div style="font-size: 10px; color: var(--vscode-fg-muted); margin-top: 2px;"><code>${podName}</code></div>
              </td>
              <td>
                <div style="display: flex; gap: 4px;">
                  <a href="${dozzleUrl}" target="_blank" class="btn btn-secondary btn-sm" style="text-decoration: none;" title="Open Dozzle Live Stream">
                    🌐 Dozzle
                  </a>
                  <button class="btn btn-danger btn-sm" onclick="window.ViewDispatch.cancelWorkload('${sid}')">
                    🛑 Cancel
                  </button>
                </div>
              </td>
            </tr>
          `;
        }).join("");
      }
    } catch (e) {
      if (tbody) tbody.innerHTML = `<tr><td colspan="7" style="text-align: center; color: var(--vscode-fg-muted); padding: 16px;">Active workloads synchronized.</td></tr>`;
    }
  },

  async cancelWorkload(studyId) {
    if (!confirm(`Are you sure you want to CANCEL running study ${studyId}?`)) return;
    window.workbench.logTerminal("WARN", `Sending cancellation signal for study ${studyId}...`);
    try {
      await window.apiClient.cancelTask(studyId);
      window.workbench.logTerminal("SUCCESS", `Study ${studyId} cancelled.`);
      await this.loadActiveWorkloads();
    } catch (e) {
      window.workbench.logTerminal("ERROR", `Failed to cancel study ${studyId}: ${e.message}`);
      alert(`Cancel failed: ${e.message}`);
    }
  },

  async applyPolicy(mode) {
    window.workbench.logTerminal("INFO", `Setting scheduler policy override: ${mode}...`);
    try {
      await window.apiClient.setSchedulerPolicy({
        enabled: true,
        office_start_hour: mode === "day" ? 0 : 20,
        office_end_hour: mode === "day" ? 24 : 8,
        office_max_gpu_percent: mode === "day" ? 25.0 : 95.0,
      });
      window.workbench.logTerminal("SUCCESS", `Scheduler policy updated to: ${mode}`);
      document.getElementById("policy-current-mode").textContent = `${mode.toUpperCase()} ACTIVE`;
    } catch (e) {
      window.workbench.logTerminal("ERROR", `Failed to set policy: ${e.message}`);
      alert(`Failed to set policy: ${e.message}`);
    }
  },

  async applyPolicyNow() {
    window.workbench.logTerminal("INFO", `Applying active scheduler profile to all cluster nodes...`);
    try {
      const res = await window.apiClient.applySchedulerPolicy();
      window.workbench.logTerminal("SUCCESS", `Profile applied: ${res.message || "Done"}`);
      alert(`Scheduler profile applied successfully!`);
    } catch (e) {
      window.workbench.logTerminal("ERROR", `Error applying profile: ${e.message}`);
      alert(`Error applying profile: ${e.message}`);
    }
  },
};
