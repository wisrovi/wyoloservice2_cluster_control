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
