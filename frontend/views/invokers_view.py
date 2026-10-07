"""Invokers management view with interactive resource sliders and pause controls."""

import streamlit as st
from frontend.api_client import ClusterApiClient


def render_invokers(api_client: ClusterApiClient, token: str):
    """Renders the invokers management and dynamic resource tuning view."""
    st.title("⚙️ Gestión y Asignación de Recursos de Invokers")
    st.caption("Modifica en tiempo real el porcentaje de GPU (MAX_GPU), RAM y CPU por nodo sin detener contenedores.")

    try:
        invokers = api_client.list_invokers(token)
    except Exception as e:
        st.error(f"Error cargando invokers: {e}")
        return

    if not invokers:
        st.warning("No se encontraron nodos invoker registrados.")
        return

    # Search filter
    search_query = st.text_input(
        "🔍 Filtrar por IP o Hostname",
        value="",
        placeholder="ej. 192.168.1.68 o worker-cima",
    ).strip().lower()

    filtered_invokers = [
        inv for inv in invokers
        if search_query in inv.get("worker_ip", "").lower()
        or search_query in inv.get("hostname", "").lower()
        or search_query in inv.get("physical", {}).get("gpu_model", "").lower()
    ]

    st.write(f"Mostrando **{len(filtered_invokers)}** de **{len(invokers)}** nodos invoker.")
    st.divider()

    for idx, inv in enumerate(filtered_invokers):
        worker_ip = inv.get("worker_ip", "unknown")
        hostname = inv.get("hostname", "unknown")
        physical = inv.get("physical", {})
        limits = inv.get("limits", {})
        pause_state = inv.get("pause_state", "active")

        # Color-coded header
        status_icon = "🟢" if pause_state == "active" else "⏸️"
        expander_title = f"{status_icon} {hostname} ({worker_ip}) — {physical.get('gpu_model', 'N/A')}"

        with st.expander(expander_title, expanded=(len(filtered_invokers) == 1 or idx == 0)):
            col_info, col_controls = st.columns([1, 1], gap="medium")

            with col_info:
                st.markdown("#### 🖥️ Hardware Físico Detectado")
                st.write(f"• **Modelo GPU:** `{physical.get('gpu_model', 'N/A')}`")
                st.write(f"• **Cantidad GPUs:** `{physical.get('gpu_count', 0)}`")
                st.write(f"• **VRAM Total:** `{physical.get('gpu_memory_total', 'N/A')}`")
                st.write(f"• **RAM Total:** `{physical.get('ram_total', 'N/A')}`")
                st.write(f"• **Cores CPU Físicos:** `{physical.get('cpu_cores', 'N/A')}`")
                st.write(f"• **Estado de Colas:** `{pause_state}`")
                if inv.get("pause_until"):
                    st.write(f"• **Pausa Temporal Hasta:** `{inv.get('pause_until')}`")
                st.caption(f"Última sincronización: {inv.get('updated_at', 'N/A')}")

                # Pause & Resume quick action buttons
                st.markdown("##### ⏯️ Control de Colas Públicas")
                col_p1, col_p2, col_p3 = st.columns(3)
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
                    if st.button("⏹️ Pausa Indefinida", key=f"btn_pind_{worker_ip}", use_container_width=True):
                        try:
                            api_client.set_pause(token, worker_ip, action="pause", mode="perpetual")
                            st.warning(f"Nodo {worker_ip} pausado indefinidamente.")
                            st.rerun()
                        except Exception as pe:
                            st.error(f"Error: {pe}")

            with col_controls:
                st.markdown("#### ⚡ Límites Asignados para Entrenamientos")

                current_max_gpu = float(limits.get("max_gpu_percent", 30.0))
                new_max_gpu = st.slider(
                    "Porcentaje de VRAM para YOLO Autobatch (MAX_GPU %)",
                    min_value=10,
                    max_value=100,
                    value=int(current_max_gpu),
                    step=5,
                    key=f"slider_gpu_{worker_ip}",
                    help="Determina el valor batch asignado automáticamente a los modelos durante el entrenamiento.",
                )

                current_max_ram = str(limits.get("max_ram", "16g"))
                new_max_ram = st.text_input(
                    "Límite de Memoria RAM para el Contenedor",
                    value=current_max_ram,
                    key=f"input_ram_{worker_ip}",
                    help="Ejemplo: 16g, 24g, 32g",
                )

                try:
                    total_cores = float(physical.get("cpu_cores", 8))
                except Exception:
                    total_cores = 8.0

                current_cores = min(float(limits.get("max_cpu_cores", total_cores - 1)), total_cores)
                new_max_cores = st.slider(
                    "Cores de CPU Asignados al Contenedor",
                    min_value=1.0,
                    max_value=max(total_cores, 1.0),
                    value=float(current_cores),
                    step=0.5,
                    key=f"slider_cpu_{worker_ip}",
                    help="Número de cores de CPU para afinidad del executor.",
                )

                if st.button("💾 Guardar Cambios en Redis", key=f"btn_save_{worker_ip}", type="primary", use_container_width=True):
                    try:
                        api_client.update_limits(
                            token=token,
                            worker_ip=worker_ip,
                            max_gpu_percent=float(new_max_gpu),
                            max_ram=new_max_ram,
                            max_cpu_cores=float(new_max_cores),
                        )
                        st.success(f"✅ ¡Configuración guardada en Redis para {worker_ip}! (MAX_GPU={new_max_gpu}%, RAM={new_max_ram}, CPU={new_max_cores})")
                        st.rerun()
                    except Exception as se:
                        st.error(f"Error guardando límites: {se}")
