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
