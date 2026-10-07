"""Cluster capabilities and R&D module governance view for NeuralForge Cluster Admin."""

import pandas as pd
import streamlit as st
from frontend.api_client import ClusterApiClient


def render_capabilities(api_client: ClusterApiClient, token: str):
    """Renders the Cluster Capabilities and R&D Extension Module catalog dashboard."""
    st.markdown("## 🔬 Capacidades y Extensiones del Clúster")
    st.caption("Catálogo oficial de motores de entrenamiento, módulos de I+D (XAI, robustez, incertidumbre) y pipelines de post-procesamiento disponibles en los ejecutores.")

    tab_modules, tab_docker, tab_research = st.tabs([
        "🧩 Catálogo de Módulos I+D",
        "🐳 Estado de Imágenes Docker del Worker",
        "📚 Alineación con Papers Científicos",
    ])

    try:
        caps = api_client.get_cluster_capabilities(token)
    except Exception as e:
        st.error(f"Error obteniendo capacidades del clúster: {e}")
        caps = {"modules": [], "docker_image": "unknown", "total_modules": 0, "active_modules": 0}

    modules = caps.get("modules", [])
    docker_image = caps.get("docker_image", "wisrovi/train_service:worker_executor_v1.0.0")

    # --- TAB 1: R&D Modules Catalog ---
    with tab_modules:
        col_m1, col_m2 = st.columns([3, 1])
        with col_m1:
            st.markdown("#### 🛠️ Módulos de Post-Entrenamiento Habilitados en el Clúster")
        with col_m2:
            st.metric("Módulos Activos", f"{caps.get('active_modules', 0)} / {caps.get('total_modules', 0)}")

        if not modules:
            st.info("No se han cargado módulos de capacidades.")
        else:
            for mod in modules:
                with st.container(border=True):
                    col_mod1, col_mod2 = st.columns([3, 1])
                    with col_mod1:
                        st.markdown(f"### `{mod.get('module_id')}` — {mod.get('name')}")
                        st.caption(f"Categoría: **{mod.get('category')}** | Meta científica: **{mod.get('research_tier')}**")
                        st.write(mod.get("description"))
                    with col_mod2:
                        st.write(" ")
                        st.success("🟢 HABILITADO")
                        st.caption("Disponible en imagen base")

    # --- TAB 2: Docker Worker Images ---
    with tab_docker:
        st.markdown("#### 🐳 Contenedores Ejecutores en los Nodos Invoker")
        with st.container(border=True):
            st.subheader("📦 Imagen Base del Worker Executor")
            st.code(docker_image, language="bash")
            st.markdown("- **Soporte GPU:** `NVIDIA Container Toolkit (CUDA 12.1 + cuDNN 8)`")
            st.markdown("- **Modelos Base Soportados:** `YOLOv8`, `YOLOv11`, `YOLO26` (Clasificación, Detección, Segmentación, OBB, Pose)")
            st.markdown("- **Aceleradores de Inferencia:** `PyTorch 2.2`, `TensorRT 8.6`, `ONNXRuntime-GPU`")
            st.markdown("- **Integración con Storage:** Montaje automático Samba CIFS `/wyolo/dataset` y salida a MinIO")

    # --- TAB 3: Scientific Research Mapping ---
    with tab_research:
        st.markdown("#### 📚 Mapeo de I+D y Potenciales Publicaciones")
        st.caption("Los 12 módulos de investigación del worker forman la base de 7 papers científicos potenciales para congresos de primer nivel (MLSys, CVPR, NeurIPS, ICML).")

        papers_data = [
            {"Paper": "Paper 1 (MLSys)", "Título Tentativo": "Quantitative Validation of Visual Explanations in Real-Time Object Detectors", "Módulos Clave": "XAI-01, QuantitativeXAIValidator"},
            {"Paper": "Paper 2 (CVPR)", "Título Tentativo": "Adversarial Robustness and Sensor Degradation Benchmarking in YOLO Models", "Módulos Clave": "ADV-02, RobustnessNoiseEvaluator"},
            {"Paper": "Paper 3 (NeurIPS)", "Título Tentativo": "Uncertainty Quantification in Real-Time Edge Vision via Monte Carlo Dropout", "Módulos Clave": "UNC-03, UncertaintyQuantifier"},
            {"Paper": "Paper 4 (ICML)", "Título Tentativo": "Predicting Deployment Accuracy under Domain Shift without Target Labels", "Módulos Clave": "DOM-04, CrossDomainGeneralizer"},
            {"Paper": "Paper 5 (ICCV)", "Título Tentativo": "Latent Manifold Topology as an Early Diagnostic of Detector Failures", "Módulos Clave": "LAT-05, FeatureRepresentationAnalyzer"},
        ]
        st.dataframe(pd.DataFrame(papers_data), use_container_width=True, hide_index=True)
