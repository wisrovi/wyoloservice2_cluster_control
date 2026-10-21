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

    # --- Image Synchronization & Broadcast Pull (v2.0.0) ---
    with st.expander("📦 Cluster Docker/K8s Image Synchronization & Broadcast Pull", expanded=False):
        st.caption("Verifica las versiones de imagen desplegadas en cada nodo invoker y ejecuta un pull simultáneo en lote (excluyendo automáticamente al NAS manager).")
        col_img1, col_img2 = st.columns([3, 1])
        with col_img1:
            target_pull_img = st.text_input(
                "Target Docker Image",
                value="wisrovi/train_service:worker_executor_v1.0.0",
                key="input_target_pull_img",
            )
        with col_img2:
            st.write(" ")
            btn_broadcast = st.button("🚀 Broadcast Pull", key="btn_broadcast_pull", type="primary", use_container_width=True)

        if btn_broadcast:
            try:
                b_res = api_client.trigger_broadcast_docker_pull(token, target_image=target_pull_img)
                st.success(b_res.get("message", "Broadcast pull dispatched"))
                st.rerun()
            except Exception as be:
                st.error(f"Error en broadcast pull: {be}")

        try:
            img_status = api_client.get_cluster_images_status(token, target_image=target_pull_img)
            col_is1, col_is2 = st.columns(2)
            with col_is1:
                st.metric("Nodos Sincronizados", f"{img_status.get('synchronized_nodes', 0)} / {img_status.get('total_nodes', 0)}")
            with col_is2:
                st.metric("Tag Esperado", img_status.get("latest_tag", "latest"))

            nodes_data = img_status.get("nodes", [])
            if nodes_data:
                import pandas as pd
                df_nodes = pd.DataFrame(nodes_data)
                st.dataframe(df_nodes, use_container_width=True, hide_index=True)
        except Exception as ie:
            st.caption(f"No se pudo consultar el estado de imágenes: {ie}")


    st.divider()

    # --- NODE CARDS ---
    for idx, inv in enumerate(filtered):
        worker_ip = inv.get("worker_ip", "unknown")
        hostname = inv.get("hostname", "unknown")
        physical = inv.get("physical", {})
        limits = inv.get("limits", {})
        pause_state = inv.get("pause_state", "active")

        # Color-coded icon and runtime badge
        status_icon = "🟢" if pause_state == "active" else ("🟡" if "paused" in pause_state else "🛡️")
        runtime_badge = "☸️ K8s" if "Kubernetes" in inv.get("orchestration_runtime", "") else "🐳 Docker"
        expander_title = f"{status_icon} {hostname} ({worker_ip}) [{runtime_badge}] — {physical.get('gpu_model', 'N/A')}"

        with st.expander(expander_title, expanded=(len(filtered) == 1 or idx == 0)):
            col_info, col_controls = st.columns([1, 1], gap="medium")

            with col_info:
                st.markdown("#### 🖥️ Detected Physical Hardware")
                st.write(f"• **GPU Model:** `{physical.get('gpu_model', 'N/A')}`")
                st.write(f"• **GPU Count:** `{physical.get('gpu_count', 0)}`")
                st.write(f"• **Total VRAM:** `{physical.get('gpu_memory_total', 'N/A')}`")
                st.write(f"• **Total RAM:** `{physical.get('ram_total', 'N/A')}`")
                st.write(f"• **Physical CPU Cores:** `{physical.get('cpu_cores', 'N/A')}`")
                st.write(f"• **Orchestration Runtime:** `{inv.get('orchestration_runtime', 'Docker Standalone')}`")
                st.caption(f"Last sync: {inv.get('updated_at', 'N/A')}")

                # NVML Live GPU Telemetry
                temp_c = physical.get("gpu_temp_c")
                power_w = physical.get("gpu_power_watts")
                tdp_w = physical.get("gpu_tdp_watts")
                util_pct = physical.get("gpu_compute_util_pct")

                if temp_c is not None or power_w is not None or util_pct is not None:
                    st.markdown("##### 🌡️ NVML Telemetría en Vivo")
                    col_nv1, col_nv2, col_nv3 = st.columns(3)
                    with col_nv1:
                        t_val = temp_c if temp_c is not None else 0.0
                        t_color = "🟢" if t_val < 70 else ("🟡" if t_val < 80 else "🔴")
                        st.metric("Temperatura", f"{t_val:.1f} °C", delta=f"{t_color} Normal" if t_val < 75 else f"{t_color} Caliente", delta_color="off")
                    with col_nv2:
                        p_val = power_w if power_w is not None else 0.0
                        tdp_val = tdp_w if tdp_w is not None else 250.0
                        st.metric("Potencia (Watts)", f"{p_val:.0f} W / {tdp_val:.0f} W", help="Consumo vs Límite TDP")
                    with col_nv3:
                        u_val = util_pct if util_pct is not None else 0.0
                        st.metric("Cómputo GPU", f"{u_val:.0f}%", help="Utilización de núcleos CUDA")

                # Kubernetes Node Status & Conditions
                k8s_cond = inv.get("k8s_conditions") or {}
                k8s_gpu = inv.get("k8s_gpu_plugin") or {}
                if k8s_cond or k8s_gpu:
                    st.markdown("##### ☸️ Estado Kubernetes del Nodo")
                    col_k1, col_k2, col_k3 = st.columns(3)
                    with col_k1:
                        k_ready = k8s_cond.get("ready", True)
                        st.write(f"• **K8s Node:** {'🟢 Ready' if k_ready else '🔴 NotReady'}")
                    with col_k2:
                        d_press = k8s_cond.get("disk_pressure", False)
                        m_press = k8s_cond.get("memory_pressure", False)
                        press_str = "🟢 Normal" if (not d_press and not m_press) else ("⚠️ DiskPressure" if d_press else "⚠️ MemPressure")
                        st.write(f"• **Presión:** `{press_str}`")
                    with col_k3:
                        g_alloc = k8s_gpu.get("allocatable", 1)
                        g_cap = k8s_gpu.get("capacity", 1)
                        st.write(f"• **GPU Plugin:** `{g_alloc}/{g_cap} Allocatable`")

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

                # Remote Node Maintenance
                st.markdown("##### 🛠️ Mantenimiento Remoto")
                col_rem1, col_rem2 = st.columns(2)
                with col_rem1:
                    if st.button("🔄 Reiniciar Servicio", key=f"btn_restart_{worker_ip}", use_container_width=True, help="Reinicia el daemon de wyoloservice2_invoker mediante Celery"):
                        try:
                            r_res = api_client.restart_node_service(token, worker_ip)
                            st.info(r_res.get("message", "Señal enviada"))
                        except Exception as re_e:
                            st.error(f"Error: {re_e}")
                with col_rem2:
                    if st.button("🧹 Prune Docker", key=f"btn_prune_{worker_ip}", use_container_width=True, help="Ejecuta docker system prune -f para liberar espacio en disco"):
                        try:
                            p_res = api_client.prune_node_docker(token, worker_ip)
                            st.success(p_res.get("message", "Docker saneado"))
                        except Exception as pr_e:
                            st.error(f"Error: {pr_e}")
                st.caption(f"🔗 [🌐 Abrir Dozzle K8s de este Nodo](http://{worker_ip}:8888)")

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

                current_shm = float(limits.get("shm_size_gb", 8.0))
                new_shm = st.slider(
                    "PyTorch Shared Memory (/dev/shm GiB)",
                    min_value=2.0,
                    max_value=64.0,
                    value=float(current_shm),
                    step=2.0,
                    key=f"slider_shm_{worker_ip}",
                    help="Memoria compartida en emptyDir para DataLoader de YOLO; previene 'Bus error (core dumped)'",
                )

                if st.button("💾 Save Limits to Redis", key=f"btn_save_{worker_ip}", type="primary", use_container_width=True):
                    try:
                        api_client.update_limits(
                            token=token,
                            worker_ip=worker_ip,
                            max_gpu_percent=float(new_max_gpu),
                            max_ram=new_max_ram,
                            max_cpu_cores=float(new_max_cores),
                            shm_size_gb=float(new_shm),
                        )
                        st.success(f"✅ Saved for {worker_ip} (GPU={new_max_gpu}%, RAM={new_max_ram}, CPU={new_max_cores}, SHM={new_shm}GiB)")
                        st.rerun()
                    except Exception as se:
                        st.error(f"Failed to save limits: {se}")

            # --- Live GPU Compute Processes & Zombie Monitor ---
            with st.expander(f"🔍 Live GPU Processes & Zombie Monitor ({worker_ip})", expanded=False):
                try:
                    proc_info = api_client.get_node_gpu_processes(token, worker_ip)
                    if proc_info.get("has_zombies") or proc_info.get("zombie_alert"):
                        st.error(
                            "🚨 **CRITICAL ZOMBIE PROCESS ALERT!** One or more processes have held VRAM for >24h "
                            "without active training. Terminate them below to avoid CUDA Out-Of-Memory (OOM) errors."
                        )
                    procs = proc_info.get("processes", [])
                    if not procs:
                        st.info("No active compute processes using GPU VRAM on this node.")
                    else:
                        st.write(f"**Total Active Processes:** `{len(procs)}`")
                        for p in procs:
                            col_pinfo, col_pact = st.columns([4, 1])
                            with col_pinfo:
                                z_tag = "⚠️ **[ZOMBIE LEAK]**" if p.get("is_zombie") else "⚡ **[ACTIVE]**"
                                p_name = p.get("name") or p.get("process_name", "N/A")
                                vram = p.get("vram_used_mb") or p.get("used_memory_mb", 0)
                                elapsed = p.get("elapsed") or p.get("elapsed_time", "N/A")
                                st.markdown(
                                    f"{z_tag} **PID:** `{p.get('pid')}` | **Name:** `{p_name}` | "
                                    f"**VRAM:** `{vram:.0f} MB` | **Elapsed:** `{elapsed}`"
                                )
                            with col_pact:
                                if st.button("🛑 Kill PID", key=f"kill_{worker_ip}_{p.get('pid')}", help="Terminate process"):
                                    try:
                                        res = api_client.kill_node_gpu_process(token, worker_ip, p.get("pid"))
                                        st.success(res.get("message", "Signal sent"))
                                        st.rerun()
                                    except Exception as ke:
                                        st.error(f"Failed to kill process: {ke}")
                except Exception as pe:
                    st.caption(f"GPU process telemetry unavailable: {pe}")
