"""Invokers management view with interactive resource sliders, filters, presets, and pause controls."""

import re
import streamlit as st
from frontend.api_client import ClusterApiClient


def render_invokers(api_client: ClusterApiClient, token: str):
    """Renders the invokers management view with multi-field filters, presets and controls."""
    st.title("⚙️ Gestión y Asignación de Recursos de Invokers")
    st.caption("Modifica en tiempo real los límites de GPU, RAM y CPU, aplica perfiles predefinidos y gestiona colas.")

    try:
        invokers = api_client.list_invokers(token)
    except Exception as e:
        st.error(f"Error cargando invokers: {e}")
        return

    if not invokers:
        st.warning("No se encontraron nodos invoker registrados.")
        return

    # --- ADVANCED FILTER TOOLBAR ---
    st.markdown("#### 🔍 Filtros y Búsqueda de Nodos")

    col_s1, col_s2 = st.columns([2, 2])
    with col_s1:
        search_query = st.text_input(
            "Búsqueda por texto",
            value="",
            placeholder="Buscar por IP, Hostname o GPU...",
            key="inv_search_input",
            label_visibility="collapsed",
        ).strip().lower()

    with col_s2:
        status_pill = st.radio(
            "Filtrar por estado:",
            options=["🔘 Todos", "🟢 Solo Activos", "⏸️ Solo Pausados", "🛡️ En Drenado"],
            horizontal=True,
            key="inv_status_pill",
            label_visibility="collapsed",
        )

    # Extract dynamic choices
    all_gpus = sorted(list({inv.get("physical", {}).get("gpu_model", "Desconocida") for inv in invokers if inv.get("physical", {}).get("gpu_model")}))
    gpu_options = ["Todas las GPUs"] + all_gpus

    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        sel_gpu = st.selectbox("Modelo de GPU", options=gpu_options, key="inv_gpu_filter")
    with col_f2:
        sel_vram = st.selectbox("VRAM Mínima", options=["Todas", "≥ 8 GB", "≥ 12 GB", "≥ 24 GB"], key="inv_vram_filter")
    with col_f3:
        sort_by = st.selectbox(
            "Ordenar nodos por",
            options=["IP Ascendente", "Hostname", "Mayor VRAM", "Mayor RAM", "Mayor CPU"],
            key="inv_sort_filter",
        )

    # Filtering logic
    filtered = invokers

    # Status filter
    if status_pill == "🟢 Solo Activos":
        filtered = [i for i in filtered if i.get("pause_state") == "active"]
    elif status_pill == "⏸️ Solo Pausados":
        filtered = [i for i in filtered if "pause" in i.get("pause_state", "")]
    elif status_pill == "🛡️ En Drenado":
        filtered = [i for i in filtered if i.get("pause_state") == "draining"]

    # GPU Model filter
    if sel_gpu != "Todas las GPUs":
        filtered = [i for i in filtered if i.get("physical", {}).get("gpu_model") == sel_gpu]

    # VRAM filter
    if sel_vram != "Todas":
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
        if sort_by == "Mayor VRAM":
            v_str = str(node.get("physical", {}).get("gpu_memory_total", ""))
            m = re.search(r"(\d+)", v_str)
            return -(int(m.group(1)) if m else 0)
        if sort_by == "Mayor CPU":
            c_str = str(node.get("physical", {}).get("cpu_cores", "0"))
            return -(float(c_str) if c_str.replace(".", "", 1).isdigit() else 0.0)
        # Default: IP
        return node.get("worker_ip", "")

    filtered = sorted(filtered, key=get_sort_key)

    # Header and Batch Actions
    col_cnt, col_b1, col_b2 = st.columns([2, 1, 1])
    with col_cnt:
        st.write(f"Mostrando **{len(filtered)}** de **{len(invokers)}** nodos invoker.")
    with col_b1:
        if st.button("⏸️ Pausar Visibles (4h)", help="Pone en pausa temporal todos los nodos listados actualmente"):
            for f_inv in filtered:
                try:
                    api_client.set_pause(token, f_inv["worker_ip"], action="pause", mode="temporal", hours=4.0)
                except Exception:
                    pass
            st.success(f"Pausados {len(filtered)} nodos.")
            st.rerun()
    with col_b2:
        if st.button("▶️ Reanudar Visibles", help="Reanuda el consumo en todos los nodos listados"):
            for f_inv in filtered:
                try:
                    api_client.set_pause(token, f_inv["worker_ip"], action="resume")
                except Exception:
                    pass
            st.success(f"Reanudados {len(filtered)} nodos.")
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
                st.markdown("#### 🖥️ Hardware Físico Detectado")
                st.write(f"• **Modelo GPU:** `{physical.get('gpu_model', 'N/A')}`")
                st.write(f"• **Cantidad GPUs:** `{physical.get('gpu_count', 0)}`")
                st.write(f"• **VRAM Total:** `{physical.get('gpu_memory_total', 'N/A')}`")
                st.write(f"• **RAM Total:** `{physical.get('ram_total', 'N/A')}`")
                st.write(f"• **Cores CPU Físicos:** `{physical.get('cpu_cores', 'N/A')}`")
                st.caption(f"Última sincronización: {inv.get('updated_at', 'N/A')}")

                # Status Banner
                st.markdown("##### ⏯️ Control y Estado de Colas Públicas")
                if pause_state == "active":
                    st.success("🟢 **COLA PÚBLICA ACTIVA** — Consumiendo tareas globales y privadas.")
                elif "paused" in pause_state and inv.get("pause_until"):
                    st.warning(f"🟡 **PAUSA TEMPORAL** — Hasta `{inv.get('pause_until')}`. Solo atiende cola privada.")
                elif pause_state == "draining":
                    st.info("🛡️ **MODO DRENADO (DRAINING)** — Esperando a finalizar la tarea activa para pausar.")
                else:
                    st.error("🔴 **PAUSA INDEFINIDA** — Cola pública desactivada. Solo atiende cola privada.")

                # Action Buttons
                col_p1, col_p2, col_p3, col_p4 = st.columns(4)
                with col_p1:
                    if st.button("▶️ Reanudar", key=f"btn_res_{worker_ip}", use_container_width=True):
                        try:
                            api_client.set_pause(token, worker_ip, action="resume")
                            st.success(f"Nodo {worker_ip} reanudado.")
                            st.rerun()
                        except Exception as pe:
                            st.error(f"Error: {pe}")
                with col_p2:
                    if st.button("⏸️ Pausa 4h", key=f"btn_p4_{worker_ip}", use_container_width=True):
                        try:
                            api_client.set_pause(token, worker_ip, action="pause", mode="temporal", hours=4.0)
                            st.success(f"Nodo {worker_ip} pausado por 4 horas.")
                            st.rerun()
                        except Exception as pe:
                            st.error(f"Error: {pe}")
                with col_p3:
                    if st.button("⏹️ Indefinida", key=f"btn_pind_{worker_ip}", use_container_width=True):
                        try:
                            api_client.set_pause(token, worker_ip, action="pause", mode="perpetual")
                            st.warning(f"Nodo {worker_ip} pausado indefinidamente.")
                            st.rerun()
                        except Exception as pe:
                            st.error(f"Error: {pe}")
                with col_p4:
                    if st.button("🛡️ Drenar", key=f"btn_drain_{worker_ip}", use_container_width=True):
                        try:
                            api_client.drain_invoker(token, worker_ip, reason="Manual graceful drain")
                            st.info(f"Nodo {worker_ip} en drenado.")
                            st.rerun()
                        except Exception as de:
                            st.error(f"Error drenando: {de}")

            with col_controls:
                st.markdown("#### ⚡ Asignación de Recursos Dinámicos")

                # Quick Presets Buttons
                st.caption("Perfiles Rápidos de Asignación:")
                col_pre1, col_pre2, col_pre3 = st.columns(3)
                try:
                    total_cores = float(physical.get("cpu_cores", 8))
                except Exception:
                    total_cores = 8.0

                with col_pre1:
                    if st.button("🚀 Máximo", key=f"preset_max_{worker_ip}", use_container_width=True, help="90% VRAM, RAM completa, Cores máximos"):
                        api_client.update_limits(token, worker_ip, max_gpu_percent=90.0, max_ram="32g", max_cpu_cores=total_cores)
                        st.success("Perfil Máximo aplicado.")
                        st.rerun()
                with col_pre2:
                    if st.button("⚖️ Equilibrado", key=f"preset_bal_{worker_ip}", use_container_width=True, help="50% VRAM, 16g RAM, 4 cores"):
                        api_client.update_limits(token, worker_ip, max_gpu_percent=50.0, max_ram="16g", max_cpu_cores=min(4.0, total_cores))
                        st.success("Perfil Equilibrado aplicado.")
                        st.rerun()
                with col_pre3:
                    if st.button("🍃 Silencioso", key=f"preset_quiet_{worker_ip}", use_container_width=True, help="25% VRAM, 8g RAM, 2 cores"):
                        api_client.update_limits(token, worker_ip, max_gpu_percent=25.0, max_ram="8g", max_cpu_cores=min(2.0, total_cores))
                        st.success("Perfil Silencioso aplicado.")
                        st.rerun()

                current_max_gpu = float(limits.get("max_gpu_percent", 30.0))
                new_max_gpu = st.slider(
                    "Porcentaje de VRAM (MAX_GPU %)",
                    min_value=10,
                    max_value=100,
                    value=int(current_max_gpu),
                    step=5,
                    key=f"slider_gpu_{worker_ip}",
                )

                current_max_ram = str(limits.get("max_ram", "16g"))
                new_max_ram = st.text_input(
                    "Límite de RAM para el Contenedor",
                    value=current_max_ram,
                    key=f"input_ram_{worker_ip}",
                )

                current_cores = min(float(limits.get("max_cpu_cores", total_cores - 1)), total_cores)
                new_max_cores = st.slider(
                    "Cores de CPU Asignados al Contenedor",
                    min_value=1.0,
                    max_value=max(total_cores, 1.0),
                    value=float(current_cores),
                    step=0.5,
                    key=f"slider_cpu_{worker_ip}",
                )

                if st.button("💾 Guardar Límites en Redis", key=f"btn_save_{worker_ip}", type="primary", use_container_width=True):
                    try:
                        api_client.update_limits(
                            token=token,
                            worker_ip=worker_ip,
                            max_gpu_percent=float(new_max_gpu),
                            max_ram=new_max_ram,
                            max_cpu_cores=float(new_max_cores),
                        )
                        st.success(f"✅ Guardado para {worker_ip} (GPU={new_max_gpu}%, RAM={new_max_ram}, CPU={new_max_cores})")
                        st.rerun()
                    except Exception as se:
                        st.error(f"Error guardando límites: {se}")
