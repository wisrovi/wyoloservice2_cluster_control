"""Invokers management view with interactive resource sliders, filters, presets, and pause controls."""

import re
import streamlit as st
from frontend.api_client import ClusterApiClient


def render_invokers(api_client: ClusterApiClient, token: str):
    """Renders the invokers management view with multi-field filters, presets and controls."""
    st.title("⚙️ Invoker Resource Management")
    st.caption("Adjust GPU, RAM, and CPU limits in real time, apply predefined profiles, and manage queues.")

    try:
        invokers = api_client.list_invokers(token)
    except Exception as e:
        st.error(f"Failed to load invokers: {e}")
        return

    if not invokers:
        st.warning("No registered invoker nodes were found.")
        return

    # --- ADVANCED FILTER TOOLBAR ---
    st.markdown("#### 🔍 Node Filters & Search")

    col_s1, col_s2 = st.columns([2, 2])
    with col_s1:
        search_query = st.text_input(
            "Text search",
            value="",
            placeholder="Search by IP, hostname, or GPU...",
            key="inv_search_input",
            label_visibility="collapsed",
        ).strip().lower()

    with col_s2:
        status_pill = st.radio(
            "Filter by status:",
            options=["🔘 All", "🟢 Active Only", "⏸️ Paused Only", "🛡️ Draining"],
            horizontal=True,
            key="inv_status_pill",
            label_visibility="collapsed",
        )

    # Extract dynamic choices
    all_gpus = sorted(list({inv.get("physical", {}).get("gpu_model", "Unknown") for inv in invokers if inv.get("physical", {}).get("gpu_model")}))
    gpu_options = ["All GPUs"] + all_gpus

    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        sel_gpu = st.selectbox("GPU Model", options=gpu_options, key="inv_gpu_filter")
    with col_f2:
        sel_vram = st.selectbox("Minimum VRAM", options=["Any", "≥ 8 GB", "≥ 12 GB", "≥ 24 GB"], key="inv_vram_filter")
    with col_f3:
        sort_by = st.selectbox(
            "Sort nodes by",
            options=["IP (Ascending)", "Hostname", "Most VRAM", "Most RAM", "Most CPU"],
            key="inv_sort_filter",
        )

    # Filtering logic
    filtered = invokers

    # Status filter
    if status_pill == "🟢 Active Only":
        filtered = [i for i in filtered if i.get("pause_state") == "active"]
    elif status_pill == "⏸️ Paused Only":
        filtered = [i for i in filtered if "pause" in i.get("pause_state", "")]
    elif status_pill == "🛡️ Draining":
        filtered = [i for i in filtered if i.get("pause_state") == "draining"]

    # GPU Model filter
    if sel_gpu != "All GPUs":
        filtered = [i for i in filtered if i.get("physical", {}).get("gpu_model") == sel_gpu]

    # VRAM filter
    if sel_vram != "Any":
        min_gb = 8.0 if "8" in sel_vram else (12.0 if "12" in sel_vram else 24.0)
        vram_matched = []
        for i in filtered:
            v_str = str(i.get("physical", {}).get("gpu_memory_total", ""))
            # Extract number of GB or MiB
            m_gb = re.search(r"(\d+(\.\d+)?)\s*gb", v_str.lower())
            m_mib = re.search(r"(\d+)\s*mib", v_str.lower())
            gb_val = 0.0
            if m_gb:
                gb_val = float(m_gb.group(1))
            elif m_mib:
                gb_val = float(m_mib.group(1)) / 1024.0
            if gb_val >= min_gb:
                vram_matched.append(i)
        filtered = vram_matched

    # Text search
    if search_query:
        filtered = [
            i for i in filtered
            if search_query in i.get("worker_ip", "").lower()
            or search_query in i.get("hostname", "").lower()
            or search_query in i.get("physical", {}).get("gpu_model", "").lower()
        ]

    # Sorting logic
    def get_sort_key(node):
        if sort_by == "Hostname":
            return node.get("hostname", "")
        if sort_by == "Most VRAM":
            v_str = str(node.get("physical", {}).get("gpu_memory_total", ""))
            m = re.search(r"(\d+)", v_str)
            return -(int(m.group(1)) if m else 0)
        if sort_by == "Most CPU":
            c_str = str(node.get("physical", {}).get("cpu_cores", "0"))
            return -(float(c_str) if c_str.replace(".", "", 1).isdigit() else 0.0)
        # Default: IP
        return node.get("worker_ip", "")

    filtered = sorted(filtered, key=get_sort_key)

    # Header and Batch Actions
    col_cnt, col_b1, col_b2 = st.columns([2, 1, 1])
    with col_cnt:
        st.write(f"Showing **{len(filtered)}** of **{len(invokers)}** invoker nodes.")
    with col_b1:
        if st.button("⏸️ Pause Visible (4h)", help="Temporarily pause all currently listed nodes"):
            for f_inv in filtered:
                try:
                    api_client.set_pause(token, f_inv["worker_ip"], action="pause", mode="temporal", hours=4.0)
                except Exception:
                    pass
            st.success(f"Paused {len(filtered)} nodes.")
            st.rerun()
    with col_b2:
        if st.button("▶️ Resume Visible", help="Resume task consumption on all listed nodes"):
            for f_inv in filtered:
                try:
                    api_client.set_pause(token, f_inv["worker_ip"], action="resume")
                except Exception:
                    pass
            st.success(f"Resumed {len(filtered)} nodes.")
            st.rerun()

    st.divider()

    # --- NODE CARDS ---
    for idx, inv in enumerate(filtered):
        worker_ip = inv.get("worker_ip", "unknown")
        hostname = inv.get("hostname", "unknown")
        physical = inv.get("physical", {})
        limits = inv.get("limits", {})
        pause_state = inv.get("pause_state", "active")

        # Color-coded icon
        status_icon = "🟢" if pause_state == "active" else ("🟡" if "paused" in pause_state else "🛡️")
        expander_title = f"{status_icon} {hostname} ({worker_ip}) — {physical.get('gpu_model', 'N/A')}"

        with st.expander(expander_title, expanded=(len(filtered) == 1 or idx == 0)):
            col_info, col_controls = st.columns([1, 1], gap="medium")

            with col_info:
                st.markdown("#### 🖥️ Detected Physical Hardware")
                st.write(f"• **GPU Model:** `{physical.get('gpu_model', 'N/A')}`")
                st.write(f"• **GPU Count:** `{physical.get('gpu_count', 0)}`")
                st.write(f"• **Total VRAM:** `{physical.get('gpu_memory_total', 'N/A')}`")
                st.write(f"• **Total RAM:** `{physical.get('ram_total', 'N/A')}`")
                st.write(f"• **Physical CPU Cores:** `{physical.get('cpu_cores', 'N/A')}`")
                st.caption(f"Last sync: {inv.get('updated_at', 'N/A')}")

                # Status Banner
                st.markdown("##### ⏯️ Public Queue Status & Control")
                if pause_state == "active":
                    st.success("🟢 **PUBLIC QUEUE ACTIVE** — Consuming global and private tasks.")
                elif "paused" in pause_state and inv.get("pause_until"):
                    st.warning(f"🟡 **TEMPORARILY PAUSED** — Until `{inv.get('pause_until')}`. Serving private queue only.")
                elif pause_state == "draining":
                    st.info("🛡️ **DRAINING** — Waiting for the active task to finish before pausing.")
                else:
                    st.error("🔴 **PAUSED INDEFINITELY** — Public queue disabled. Serving private queue only.")

                # Action Buttons
                col_p1, col_p2, col_p3, col_p4, col_p5 = st.columns(5)
                with col_p1:
                    if st.button("▶️ Resume", key=f"btn_res_{worker_ip}", use_container_width=True):
                        try:
                            api_client.set_pause(token, worker_ip, action="resume")
                            st.success(f"Node {worker_ip} resumed.")
                            st.rerun()
                        except Exception as pe:
                            st.error(f"Error: {pe}")
                with col_p2:
                    if st.button("⏸️ 4h", key=f"btn_p4_{worker_ip}", use_container_width=True):
                        try:
                            api_client.set_pause(token, worker_ip, action="pause", mode="temporal", hours=4.0)
                            st.success(f"Node {worker_ip} paused for 4 hours.")
                            st.rerun()
                        except Exception as pe:
                            st.error(f"Error: {pe}")
                with col_p3:
                    if st.button("⏹️ Indef.", key=f"btn_pind_{worker_ip}", use_container_width=True):
                        try:
                            api_client.set_pause(token, worker_ip, action="pause", mode="perpetual")
                            st.warning(f"Node {worker_ip} paused indefinitely.")
                            st.rerun()
                        except Exception as pe:
                            st.error(f"Error: {pe}")
                with col_p4:
                    if st.button("🛡️ Drain", key=f"btn_drain_{worker_ip}", use_container_width=True):
                        try:
                            api_client.drain_invoker(token, worker_ip, reason="Manual graceful drain")
                            st.info(f"Node {worker_ip} is draining.")
                            st.rerun()
                        except Exception as de:
                            st.error(f"Failed to drain node: {de}")
                with col_p5:
                    if st.button("🔍 Diagnose", key=f"btn_diag_{worker_ip}", use_container_width=True, help="SSH socket test and Celery presence check"):
                        try:
                            diag = api_client.diagnose_invoker(token, worker_ip)
                            st.session_state[f"diag_res_{worker_ip}"] = diag
                            st.rerun()
                        except Exception as dge:
                            st.error(f"Diagnostics failed: {dge}")

                if f"diag_res_{worker_ip}" in st.session_state:
                    diag = st.session_state[f"diag_res_{worker_ip}"]
                    status_badge = "🟢 HEALTHY" if diag["status"] == "healthy" else ("🟡 CELERY DOWN" if diag["status"] == "celery_offline" else "🔴 UNREACHABLE")
                    with st.expander(f"🩺 Diagnostic Report: {status_badge} (Latency: {diag.get('latency_ms', 'N/A')} ms)", expanded=True):
                        st.markdown(f"**Overall Status:** `{diag['status'].upper()}` | **SSH Port 22:** `{'Open ✅' if diag['ssh_port_open'] else 'Closed ❌'}` | **Celery Queue:** `{'Active ✅' if diag['celery_active'] else 'No response ❌'}`")
                        st.info(f"📝 {diag['diagnostic_summary']}")
                        if diag.get("suggested_actions"):
                            st.markdown("**Suggested Actions:**")
                            for act in diag["suggested_actions"]:
                                st.markdown(f"- `{act}`")

            with col_controls:
                st.markdown("#### ⚡ Dynamic Resource Allocation")

                # Quick Presets Buttons
                st.caption("Quick Allocation Profiles:")
                col_pre1, col_pre2, col_pre3 = st.columns(3)
                try:
                    total_cores = float(physical.get("cpu_cores", 8))
                except Exception:
                    total_cores = 8.0

                with col_pre1:
                    if st.button("🚀 Maximum", key=f"preset_max_{worker_ip}", use_container_width=True, help="90% VRAM, full RAM, maximum cores"):
                        api_client.update_limits(token, worker_ip, max_gpu_percent=90.0, max_ram="32g", max_cpu_cores=total_cores)
                        st.success("Maximum profile applied.")
                        st.rerun()
                with col_pre2:
                    if st.button("⚖️ Balanced", key=f"preset_bal_{worker_ip}", use_container_width=True, help="50% VRAM, 16g RAM, 4 cores"):
                        api_client.update_limits(token, worker_ip, max_gpu_percent=50.0, max_ram="16g", max_cpu_cores=min(4.0, total_cores))
                        st.success("Balanced profile applied.")
                        st.rerun()
                with col_pre3:
                    if st.button("🍃 Quiet", key=f"preset_quiet_{worker_ip}", use_container_width=True, help="25% VRAM, 8g RAM, 2 cores"):
                        api_client.update_limits(token, worker_ip, max_gpu_percent=25.0, max_ram="8g", max_cpu_cores=min(2.0, total_cores))
                        st.success("Quiet profile applied.")
                        st.rerun()

                current_max_gpu = float(limits.get("max_gpu_percent", 30.0))
                new_max_gpu = st.slider(
                    "VRAM Percentage (MAX_GPU %)",
                    min_value=10,
                    max_value=100,
                    value=int(current_max_gpu),
                    step=5,
                    key=f"slider_gpu_{worker_ip}",
                )

                current_max_ram = str(limits.get("max_ram", "16g"))
                new_max_ram = st.text_input(
                    "Container RAM Limit",
                    value=current_max_ram,
                    key=f"input_ram_{worker_ip}",
                )

                current_cores = min(float(limits.get("max_cpu_cores", total_cores - 1)), total_cores)
                new_max_cores = st.slider(
                    "CPU Cores Allocated to Container",
                    min_value=1.0,
                    max_value=max(total_cores, 1.0),
                    value=float(current_cores),
                    step=0.5,
                    key=f"slider_cpu_{worker_ip}",
                )

                if st.button("💾 Save Limits to Redis", key=f"btn_save_{worker_ip}", type="primary", use_container_width=True):
                    try:
                        api_client.update_limits(
                            token=token,
                            worker_ip=worker_ip,
                            max_gpu_percent=float(new_max_gpu),
                            max_ram=new_max_ram,
                            max_cpu_cores=float(new_max_cores),
                        )
                        st.success(f"✅ Saved for {worker_ip} (GPU={new_max_gpu}%, RAM={new_max_ram}, CPU={new_max_cores})")
                        st.rerun()
                    except Exception as se:
                        st.error(f"Failed to save limits: {se}")
