"""Cluster settings and account management view for Streamlit application."""

import streamlit as st
from frontend.api_client import ClusterApiClient


def render_settings(api_client: ClusterApiClient, token: str):
    """Renders global cluster batch controls and user account settings."""
    st.title("🛠️ Configuración Global del Cluster y Cuenta")

    col_batch, col_account = st.columns(2, gap="large")

    with col_batch:
        with st.container(border=True):
            st.subheader("🌐 Ajuste Masivo de Límites (Cluster-Wide)")
            st.caption("Aplica un porcentaje uniforme de MAX_GPU a todos los nodos invoker del cluster.")

            batch_gpu = st.slider("MAX_GPU Global para todos los nodos (%)", min_value=10, max_value=100, value=30, step=5)
            batch_ram = st.text_input("RAM por defecto para todos los nodos", value="16g")

            if st.button("🚀 Aplicar a Todo el Cluster", type="primary"):
                try:
                    res = api_client.batch_update_limits(
                        token=token,
                        max_gpu_percent=float(batch_gpu),
                        max_ram=batch_ram,
                    )
                    st.success(res.get("message", "Límites aplicados al cluster"))
                except Exception as be:
                    st.error(f"Error en actualización masiva: {be}")

    with col_account:
        with st.container(border=True):
            st.subheader("🔒 Cambiar Contraseña")
            st.caption(f"Usuario actual: **{st.session_state.get('username', 'wisrovi')}**")

            with st.form("change_pwd_form"):
                current_pwd = st.text_input("Contraseña Actual", type="password")
                new_pwd = st.text_input("Nueva Contraseña", type="password")
                confirm_pwd = st.text_input("Confirmar Nueva Contraseña", type="password")
                submit_pwd = st.form_submit_button("Actualizar Contraseña")

                if submit_pwd:
                    if not current_pwd or not new_pwd:
                        st.error("Rellena todos los campos.")
                    elif new_pwd != confirm_pwd:
                        st.error("Las contraseñas nuevas no coinciden.")
                    elif len(new_pwd) < 6:
                        st.error("La nueva contraseña debe tener al menos 6 caracteres.")
                    else:
                        try:
                            api_client.change_password(token, current_pwd, new_pwd)
                            st.success("✅ Contraseña actualizada exitosamente en Redis.")
                        except Exception as ce:
                            st.error(f"Error: {ce}")

    st.markdown("---")
    with st.container(border=True):
        st.subheader("🔔 Notificaciones Webhook (Discord / Slack / Telegram)")
        st.caption("Recibe alertas automáticas en canales externos cuando un nodo falle, se desconecte o un entrenamiento termine.")

        # Load current webhook config
        try:
            current_wh = api_client.get_webhook_config(token)
        except Exception:
            current_wh = {"webhook_url": "", "enabled": False}

        col_wh1, col_wh2 = st.columns([3, 1], gap="medium")
        with col_wh1:
            wh_url = st.text_input(
                "URL del Webhook (Discord / Slack / Telegram HTTP POST)",
                value=current_wh.get("webhook_url", ""),
                placeholder="https://discord.com/api/webhooks/... o https://hooks.slack.com/services/...",
            )
            wh_enabled = st.checkbox(
                "Activar alertas automáticas de eventos del clúster",
                value=current_wh.get("enabled", False),
            )
        with col_wh2:
            st.write(" ")
            st.write(" ")
            if st.button("💾 Guardar Webhook", type="primary", use_container_width=True):
                try:
                    res = api_client.save_webhook_config(token, webhook_url=wh_url, enabled=wh_enabled)
                    st.success(res.get("message", "Configuración de Webhook guardada exitosamente."))
                except Exception as we:
                    st.error(f"Error guardando Webhook: {we}")

            if st.button("🔔 Enviar Notificación de Prueba", use_container_width=True):
                try:
                    res_test = api_client.test_webhook(token)
                    st.info(res_test.get("message", "Prueba enviada."))
                except Exception as te:
                    st.error(f"Error probando Webhook: {te}")

    st.markdown("---")
    with st.container(border=True):
        st.subheader("🧹 Saneamiento y Mantenimiento de Redis (Cluster Housekeeping)")
        st.caption("Inspecciona y purga estudios fallidos, cancelados o claves temporales obsoletas para optimizar la memoria de Redis.")

        try:
            hk_preview = api_client.get_housekeeping_preview(token)
            stale_count = hk_preview.get("stale_failed_studies_count", 0)
            stale_ids = hk_preview.get("stale_study_ids", [])
            mem_human = hk_preview.get("redis_memory_human", "N/A")
            reclaimed_kb = hk_preview.get("estimated_reclaimed_kb", 0)

            col_hk1, col_hk2, col_hk3 = st.columns([1.5, 1.5, 2], gap="medium")
            with col_hk1:
                st.metric(label="💾 Memoria en Uso (Redis)", value=mem_human)
            with col_hk2:
                st.metric(
                    label="🗑️ Estudios Obsoletos Detectados",
                    value=stale_count,
                    delta=f"~{reclaimed_kb} KB recuperables",
                    delta_color="inverse" if stale_count > 0 else "off",
                )
            with col_hk3:
                st.write(" ")
                if st.button("🧹 Purgar Estudios Obsoletos Ahora", type="secondary", use_container_width=True, disabled=(stale_count == 0)):
                    try:
                        res_purge = api_client.purge_housekeeping(token)
                        st.success(res_purge.get("message", "Purgado completado."))
                        st.rerun()
                    except Exception as pe:
                        st.error(f"Error en purgado: {pe}")

            if stale_ids:
                with st.expander(f"Ver lista de {len(stale_ids)} estudios marcados para saneamiento"):
                    for sid in stale_ids:
                        st.write(f"• `{sid}` (failed / cancelled)")
        except Exception as he:
            st.caption(f"No se pudo cargar el asistente de mantenimiento: {he}")
