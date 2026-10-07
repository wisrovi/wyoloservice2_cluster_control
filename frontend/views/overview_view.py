"""Cluster overview view for Streamlit application."""

import streamlit as st
from frontend.api_client import ClusterApiClient


def render_overview(api_client: ClusterApiClient, token: str):
    """Renders the executive cluster overview dashboard and watchdog."""
    st.title("📊 Resumen del Cluster y Topología")
    st.caption("Visión general en tiempo real del estado de los nodos invoker, almacenamiento y tareas.")

    try:
        data = api_client.get_overview(token)
    except Exception as e:
        st.error(f"Error cargando el resumen del cluster: {e}")
        return

    # Top KPI Metrics Cards
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric(label="🖥️ Nodos Totales", value=data.get("total_nodes", 0))
    with col2:
        st.metric(label="🟢 Nodos Activos", value=data.get("active_nodes", 0))
    with col3:
        st.metric(label="⏸️ Nodos en Pausa", value=data.get("paused_nodes", 0))
    with col4:
        st.metric(label="⚡ GPUs Totales", value=data.get("total_gpus", 0))
    with col5:
        st.metric(label="🚀 Tareas Activas", value=data.get("active_trials_count", 0))

    st.divider()

    # --- Cluster Health & Watchdog Section ---
    st.subheader("🚨 Monitor de Salud y Watchdog del Clúster")
    try:
        health = api_client.get_cluster_health(token)
        col_h1, col_h2, col_h3, col_h4, col_h5 = st.columns(5)
        with col_h1:
            st.metric(
                label="📡 Broker Redis",
                value="OK" if health.get("redis_status") == "healthy" else "ERROR",
                delta=f"{health.get('redis_latency_ms', 0)} ms latencia",
                delta_color="normal" if health.get("redis_status") == "healthy" else "inverse",
            )
        with col_h2:
            st.metric(
                label="🩺 Nodos Saludables",
                value=f"{health.get('healthy_nodes', 0)} / {health.get('total_nodes', 0)}",
            )
        with col_h3:
            zombies = health.get("zombie_nodes", [])
            st.metric(
                label="⚠️ Nodos Desconectados",
                value=len(zombies),
                delta_color="inverse" if zombies else "normal",
            )
        with col_h4:
            st.metric(
                label="📂 Samba CIFS",
                value="ONLINE" if health.get("storage_samba") == "healthy" else "DEGRADED",
            )
        with col_h5:
            st.metric(
                label="🪣 MinIO S3",
                value="ONLINE" if health.get("storage_minio") == "healthy" else "DEGRADED",
            )

        if zombies:
            st.warning(f"⚠️ Nodos no respondiendo a Celery broadcast: {', '.join(zombies)}")
        else:
            st.success("✅ Todos los invokers reportan latidos periódicos y colas Celery activas.")
    except Exception as he:
        st.caption(f"No se pudo cargar el watchdog de salud: {he}")

    st.divider()

    # View Mode Switcher
    col_v1, col_v2 = st.columns([2, 1])
    with col_v1:
        st.subheader("🖥️ Distribución de Nodos Invoker")
    with col_v2:
        view_mode = st.radio(
            "Modo de vista:",
            options=["📋 Tabla Resumen", "🗺️ Cuadrícula de Servidores (Rack Grid)"],
            horizontal=True,
            label_visibility="collapsed",
            key="overview_view_mode",
        )

    invokers = data.get("invokers", [])
    if not invokers:
        st.info("No se han detectado invokers registrados en Redis todavía.")
        return

    if view_mode == "📋 Tabla Resumen":
        table_data = []
        for inv in invokers:
            ip = inv.get("worker_ip", "unknown")
            hostname = inv.get("hostname", "unknown")
            gpu_info = f"{inv.get('physical', {}).get('gpu_model', 'N/A')} ({inv.get('physical', {}).get('gpu_count', 0)})"
            vram_info = inv.get("physical", {}).get("gpu_memory_total", "N/A")
            max_gpu = f"{inv.get('limits', {}).get('max_gpu_percent', 30)}%"
            max_ram = inv.get("limits", {}).get("max_ram", "N/A")
            max_cpu = f"{inv.get('limits', {}).get('max_cpu_cores', 'N/A')} cores"
            state = inv.get("pause_state", "active")
            badge = "🟢 Activo" if state == "active" else f"⏸️ {state}"

            table_data.append({
                "IP Worker": ip,
                "Hostname": hostname,
                "Modelo GPU": gpu_info,
                "VRAM Total": vram_info,
                "MAX_GPU Asignado": max_gpu,
                "RAM Asignada": max_ram,
                "CPU Asignado": max_cpu,
                "Estado Colas": badge,
            })
        st.dataframe(table_data, use_container_width=True, hide_index=True)

    else:
        # Rack Grid View
        st.caption("Topología visual del clúster con carga asignada:")
        cols = st.columns(3)
        for idx, inv in enumerate(invokers):
            with cols[idx % 3]:
                ip = inv.get("worker_ip", "unknown")
                hostname = inv.get("hostname", "unknown")
                state = inv.get("pause_state", "active")
                gpu_model = inv.get("physical", {}).get("gpu_model", "GPU")
                vram_total = inv.get("physical", {}).get("gpu_memory_total", "N/A")
                max_gpu_pct = float(inv.get("limits", {}).get("max_gpu_percent", 30))
                max_ram = inv.get("limits", {}).get("max_ram", "16g")
                max_cpu = inv.get("limits", {}).get("max_cpu_cores", 4.0)

                icon = "🟢" if state == "active" else ("🟡" if "paused" in state else "🛡️")
                with st.container(border=True):
                    st.markdown(f"##### {icon} `{hostname}`")
                    st.caption(f"IP: `{ip}` | {gpu_model}")
                    st.write(f"• **VRAM:** `{vram_total}`")
                    st.progress(min(max_gpu_pct / 100.0, 1.0), text=f"VRAM Límite: {int(max_gpu_pct)}%")
                    st.write(f"• **RAM:** `{max_ram}` | **CPU:** `{max_cpu} cores`")
