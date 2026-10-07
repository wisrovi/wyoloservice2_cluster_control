"""Cluster capabilities and R&D module governance view for NeuralForge Cluster Admin."""

import pandas as pd
import streamlit as st
from frontend.api_client import ClusterApiClient


def render_capabilities(api_client: ClusterApiClient, token: str):
    """Renders the Cluster Capabilities and R&D Extension Module catalog dashboard."""
    st.markdown("## 🔬 Cluster Capabilities & Extensions")
    st.caption("Official catalog of training engines, R&D modules (XAI, robustness, uncertainty) and post-processing pipelines available on the executors.")

    tab_modules, tab_docker, tab_research = st.tabs([
        "🧩 R&D Module Catalog",
        "🐳 Worker Docker Images",
        "📚 Scientific Paper Alignment",
    ])

    try:
        caps = api_client.get_cluster_capabilities(token)
    except Exception as e:
        st.error(f"Error retrieving cluster capabilities: {e}")
        caps = {"modules": [], "docker_image": "unknown", "total_modules": 0, "active_modules": 0}

    modules = caps.get("modules", [])
    docker_image = caps.get("docker_image", "wisrovi/train_service:worker_executor_v1.0.0")

    # --- TAB 1: R&D Modules Catalog ---
    with tab_modules:
        col_m1, col_m2 = st.columns([3, 1])
        with col_m1:
            st.markdown("#### 🛠️ Post-Training Modules Enabled on the Cluster")
        with col_m2:
            st.metric("Active Modules", f"{caps.get('active_modules', 0)} / {caps.get('total_modules', 0)}")

        if not modules:
            st.info("No capability modules have been loaded.")
        else:
            for mod in modules:
                with st.container(border=True):
                    col_mod1, col_mod2 = st.columns([3, 1])
                    with col_mod1:
                        st.markdown(f"### `{mod.get('module_id')}` — {mod.get('name')}")
                        st.caption(f"Category: **{mod.get('category')}** | Research target: **{mod.get('research_tier')}**")
                        st.write(mod.get("description"))
                    with col_mod2:
                        st.write(" ")
                        st.success("🟢 ENABLED")
                        st.caption("Available in base image")

    # --- TAB 2: Docker Worker Images ---
    with tab_docker:
        st.markdown("#### 🐳 Executor Containers on Invoker Nodes")
        with st.container(border=True):
            st.subheader("📦 Worker Executor Base Image")
            st.code(docker_image, language="bash")
            st.markdown("- **GPU Support:** `NVIDIA Container Toolkit (CUDA 12.1 + cuDNN 8)`")
            st.markdown("- **Supported Base Models:** `YOLOv8`, `YOLOv11`, `YOLO26` (Classification, Detection, Segmentation, OBB, Pose)")
            st.markdown("- **Inference Accelerators:** `PyTorch 2.2`, `TensorRT 8.6`, `ONNXRuntime-GPU`")
            st.markdown("- **Storage Integration:** Automatic Samba CIFS mount at `/wyolo/dataset` and output to MinIO")

    # --- TAB 3: Scientific Research Mapping ---
    with tab_research:
        st.markdown("#### 📚 R&D Mapping & Potential Publications")
        st.caption("The worker's 12 research modules form the basis of 7 potential scientific papers for top-tier venues (MLSys, CVPR, NeurIPS, ICML).")

        papers_data = [
            {"Paper": "Paper 1 (MLSys)", "Tentative Title": "Quantitative Validation of Visual Explanations in Real-Time Object Detectors", "Key Modules": "XAI-01, QuantitativeXAIValidator"},
            {"Paper": "Paper 2 (CVPR)", "Tentative Title": "Adversarial Robustness and Sensor Degradation Benchmarking in YOLO Models", "Key Modules": "ADV-02, RobustnessNoiseEvaluator"},
            {"Paper": "Paper 3 (NeurIPS)", "Tentative Title": "Uncertainty Quantification in Real-Time Edge Vision via Monte Carlo Dropout", "Key Modules": "UNC-03, UncertaintyQuantifier"},
            {"Paper": "Paper 4 (ICML)", "Tentative Title": "Predicting Deployment Accuracy under Domain Shift without Target Labels", "Key Modules": "DOM-04, CrossDomainGeneralizer"},
            {"Paper": "Paper 5 (ICCV)", "Tentative Title": "Latent Manifold Topology as an Early Diagnostic of Detector Failures", "Key Modules": "LAT-05, FeatureRepresentationAnalyzer"},
        ]
        st.dataframe(pd.DataFrame(papers_data), use_container_width=True, hide_index=True)
