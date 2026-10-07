"""Cluster overview view for Streamlit application."""

import streamlit as st
from frontend.api_client import ClusterApiClient


def render_overview(api_client: ClusterApiClient, token: str):
    """Renders the executive cluster overview dashboard."""
    st.title("📊 Resumen del Cluster")
    st.caption("Visión general en tiempo real del estado de los nodos invoker y tareas.")

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

    # Quick table breakdown
    st.subheader("📋 Estado Actual de Nodos Invoker")
    invokers = data.get("invokers", [])
    if not invokers:
        st.info("No se han detectado invokers registrados en Redis todavía.")
        return

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

    st.divider()

    # --- Cluster Health & Watchdog Section ---
    st.subheader("🚨 Monitor de Salud y Watchdog del Clúster")
    try:
        health = api_client.get_cluster_health(token)
        col_h1, col_h2, col_h3 = st.columns(3)
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
                label="🧟 Nodos Zombies (>3m inactivos)",
                value=len(zombies),
                delta_color="inverse" if zombies else "normal",
            )

        if zombies:
            st.warning(f"⚠️ Atención: Los siguientes nodos no han reportado latido en más de 3 minutos: {', '.join(zombies)}")
        else:
            st.success("✅ Todos los invokers reportan latidos periódicos y conectividad estable.")
    except Exception as he:
        st.caption(f"No se pudo cargar el watchdog de salud: {he}")
