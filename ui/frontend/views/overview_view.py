"""Cluster overview view for Streamlit application."""

import pandas as pd
import streamlit as st
from frontend.api_client import ClusterApiClient
from frontend.styles import render_cluster_pulse_bar, render_page_header


def render_overview(api_client: ClusterApiClient, token: str):
    """Renders the executive cluster overview dashboard, watchdog, and workload trends."""
    render_page_header(
        title="Operations Center & Topology",
        subtitle="Real-time cluster telemetry, compute fabrics, node health watchdog, and workload distribution.",
        badge_text="Executive Dashboard",
    )

    try:
        data = api_client.get_overview(token)
    except Exception as e:
        st.error(f"Failed to load cluster overview: {e}")
        return

    # Real-Time Cluster Pulse HUD Bar
    try:
        health = api_client.get_cluster_health(token)
    except Exception:
        health = None

    render_cluster_pulse_bar(data, health)

    # Top KPI Metrics Cards
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric(label="🖥️ Total Nodes", value=data.get("total_nodes", 0))
    with col2:
        st.metric(label="🟢 Active Nodes", value=data.get("active_nodes", 0))
    with col3:
        st.metric(label="⏸️ Paused Nodes", value=data.get("paused_nodes", 0))
    with col4:
        st.metric(label="⚡ Total GPUs", value=data.get("total_gpus", 0))
    with col5:
        st.metric(label="🚀 Active Tasks", value=data.get("active_trials_count", 0))

    st.divider()

    # --- Cluster Health & Watchdog Section ---
    st.subheader("🚨 Cluster Health Monitor & Watchdog")
    if health:
        col_h1, col_h2, col_h3, col_h4, col_h5 = st.columns(5)
        with col_h1:
            st.metric(
                label="📡 Redis Broker",
                value="OK" if health.get("redis_status") == "healthy" else "ERROR",
                delta=f"{health.get('redis_latency_ms', 0)} ms latency",
                delta_color="normal" if health.get("redis_status") == "healthy" else "inverse",
            )
        with col_h2:
            st.metric(
                label="🩺 Healthy Nodes",
                value=f"{health.get('healthy_nodes', 0)} / {health.get('total_nodes', 0)}",
            )
        with col_h3:
            zombies = health.get("zombie_nodes", [])
            st.metric(
                label="⚠️ Disconnected Nodes",
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
            st.warning(f"⚠️ Nodes not responding to Celery broadcast: {', '.join(zombies)}")
        else:
            st.success("✅ All invokers are reporting periodic heartbeats and active Celery queues.")

    # --- 1-Click Cluster Smoke Test & K8s Maintenance ---
    col_st1, col_st2 = st.columns(2)
    with col_st1:
        with st.expander("🧪 Cluster Smoke Test (1-Click)", expanded=False):
            st.caption("Verifica conectividad CIFS Samba, acceso MinIO S3 y disponibilidad de GPU en todos los nodos online.")
            if st.button("🚀 Iniciar Smoke Test", key="btn_run_smoke_test", type="primary", use_container_width=True):
                try:
                    with st.spinner("Ejecutando smoke test en los nodos del cluster..."):
                        res_smoke = api_client.run_cluster_smoke_test(token)
                        st.session_state["cluster_smoke_result"] = res_smoke
                        st.rerun()
                except Exception as s_err:
                    st.error(f"Error ejecutando smoke test: {s_err}")

            if "cluster_smoke_result" in st.session_state:
                smoke_data = st.session_state["cluster_smoke_result"]
                s_stat = smoke_data.get("status", "unknown").upper()
                s_total = smoke_data.get("total_nodes", 0)
                dispatched = smoke_data.get("dispatched_nodes", [])
                s_badge = "🟢 PASADO" if s_stat == "SUCCESS" else "🔴 FALLIDO"
                st.write(f"**Resultado:** `{s_badge}` | **Nodos:** `{len(dispatched)}/{s_total}`")

                det_rows = smoke_data.get("results", [])
                if det_rows:
                    df_smoke = pd.DataFrame(det_rows)
                    st.dataframe(df_smoke[["worker_ip", "gpu_model", "status", "latency_ms"]], use_container_width=True, hide_index=True)

    with col_st2:
        with st.expander("☸️ Mantenimiento de Pods Kubernetes", expanded=False):
            st.caption("Limpia pods huérfanos, desalojados (Evicted) o en estado Terminating para liberar locks de GPU y hostPath.")
            if st.button("🧹 Purgar Pods Huérfanos/Fallidos K8s", key="btn_purge_k8s_pods", use_container_width=True, help="Elimina pods en fase Failed o Evicted"):
                try:
                    p_res = api_client.purge_stale_k8s_pods(token)
                    st.success(f"✅ {p_res.get('details', 'Pods purgados')}")
                    st.caption(f"Pods liberados: {', '.join(p_res.get('purged_pods', []))}")
                except Exception as pe:
                    st.error(f"Error purgando pods: {pe}")
            st.caption("ℹ️ Nota: Los invokers de wyolo crean pods efímeros con tolerancias para 'disk-pressure' y 'memory-pressure'.")

    st.divider()

    # --- Cluster Workload Trends (Proposal 4) ---
    st.subheader("📈 Workload Distribution & Trends")
    st.caption("Hourly frequency of training jobs dispatched across the ecosystem.")
    try:
        trends = api_client.get_workload_trends(token)
        hourly = trends.get("hourly_distribution", {})
        busiest = trends.get("busiest_hour", "14:00")
        total_runs = trends.get("total_analyzed", 0)

        col_tr1, col_tr2 = st.columns([1, 3], gap="medium")
        with col_tr1:
            st.metric(label="🔥 Cluster Peak Hour", value=busiest)
            st.write(f"• **Studies Processed:** `{total_runs}`")
            st.caption("Recommendation: schedule large Optuna sweeps during off-peak hours to reduce turnaround time.")
        with col_tr2:
            if hourly:
                df_trends = pd.DataFrame(list(hourly.items()), columns=["Hour", "Studies"]).set_index("Hour")
                st.bar_chart(df_trends, height=180)
    except Exception as te:
        st.caption(f"Unable to compute workload trends: {te}")

    # --- Green AI & Carbon Footprint Section ---
    try:
        green = api_client.get_green_ai_metrics(token)
        st.divider()
        st.subheader("🌿 Energy Efficiency & Carbon Footprint (Green AI)")
        st.caption("Cumulative estimate of energy consumption and emissions based on hardware TDP and compute hours.")

        col_g1, col_g2, col_g3, col_g4 = st.columns(4)
        with col_g1:
            st.metric("⚡ Energy Consumed", f"{green.get('estimated_kwh', 0.0)} kWh")
        with col_g2:
            st.metric("🌱 CO₂e Emissions", f"{green.get('estimated_co2_kg', 0.0)} kg")
        with col_g3:
            st.metric("🌳 Equivalent Trees", f"{green.get('trees_offset_equivalent', 0.0)} offset")
        with col_g4:
            st.metric("🚀 Average Efficiency", f"{green.get('avg_efficiency_img_per_watt', 0.45)} img/W")

        with st.expander("📊 View Energy Breakdown by GPU Model"):
            gpu_breakdown = green.get("gpu_breakdown", [])
            if gpu_breakdown:
                st.dataframe(pd.DataFrame(gpu_breakdown), use_container_width=True, hide_index=True)
            st.caption(f"Calculation basis: {green.get('calculation_basis')}")
    except Exception as ge:
        st.caption(f"Unable to compute Green AI metrics: {ge}")

    st.divider()

    # --- Invoker Distribution Section ---
    col_v1, col_v2 = st.columns([2, 1])
    with col_v1:
        st.subheader("🖥️ Invoker Node Distribution")
    with col_v2:
        view_mode = st.radio(
            "View mode:",
            options=["📋 Summary Table", "🗺️ Server Rack Grid"],
            horizontal=True,
            label_visibility="collapsed",
            key="overview_view_mode",
        )

    invokers = data.get("invokers", [])
    if not invokers:
        st.info("No registered invokers have been detected in Redis yet.")
        return

    if view_mode == "📋 Summary Table":
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
            badge = "🟢 Active" if state == "active" else f"⏸️ {state}"

            table_data.append({
                "Worker IP": ip,
                "Hostname": hostname,
                "GPU Model": gpu_info,
                "Total VRAM": vram_info,
                "Allocated MAX_GPU": max_gpu,
                "Allocated RAM": max_ram,
                "Allocated CPU": max_cpu,
                "Queue Status": badge,
            })
        st.dataframe(table_data, use_container_width=True, hide_index=True)

    else:
        # Rack Grid View
        st.caption("Visual cluster topology with allocated load:")
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

                state_color = "#10B981" if state == "active" else ("#F59E0B" if "pause" in state else "#3B82F6")
                pulse_cls = "pulse-green" if state == "active" else ("pulse-amber" if "pause" in state else "pulse-blue")

                with st.container(border=True):
                    st.markdown(
                        f"""
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                            <div style="display: flex; align-items: center; gap: 6px;">
                                <span class="pulse-dot {pulse_cls}"></span>
                                <span style="font-weight: 700; color: #FFFFFF; font-size: 1.05rem;">{hostname}</span>
                            </div>
                            <span style="background: rgba(255,255,255,0.06); color: {state_color}; border: 1px solid rgba(255,255,255,0.1); font-size: 0.7rem; font-weight: 700; padding: 2px 6px; border-radius: 4px; text-transform: uppercase;">
                                {state}
                            </span>
                        </div>
                        <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.8rem; color: #94A3B8; margin-bottom: 8px;">
                            {ip} &nbsp;•&nbsp; <span style="color: #60A5FA;">{gpu_model}</span>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                    st.write(f"• **Physical VRAM:** `{vram_total}`")
                    st.progress(min(max_gpu_pct / 100.0, 1.0), text=f"Max VRAM Limit: {int(max_gpu_pct)}%")
                    st.markdown(
                        f"""
                        <div style="display: flex; gap: 6px; margin-top: 8px;">
                            <span style="background: rgba(15, 23, 42, 0.7); border: 1px solid rgba(255,255,255,0.06); padding: 3px 8px; border-radius: 6px; font-size: 0.75rem; color: #E2E8F0; font-family: monospace;">RAM: {max_ram}</span>
                            <span style="background: rgba(15, 23, 42, 0.7); border: 1px solid rgba(255,255,255,0.06); padding: 3px 8px; border-radius: 6px; font-size: 0.75rem; color: #E2E8F0; font-family: monospace;">CPU: {max_cpu} cores</span>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
