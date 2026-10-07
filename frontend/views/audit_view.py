"""Audit trail and security governance view for NeuralForge Cluster Admin."""

import pandas as pd
import streamlit as st
from frontend.api_client import ClusterApiClient


def render_audit(api_client: ClusterApiClient, token: str):
    """Renders the Cluster Audit Trail, Security and Administrative Events dashboard."""
    st.markdown("## 📜 Auditoría y Registro de Seguridad")
    st.caption("Trazabilidad inmutable de todas las acciones administrativas realizadas en el clúster (cambios de límites, pausas, drenados, purgas).")

    tab_timeline, tab_security = st.tabs([
        "🕒 Timeline de Operaciones Administrativas",
        "🔒 Sesiones y Estado de Seguridad",
    ])

    # --- TAB 1: Audit Timeline ---
    with tab_timeline:
        col_ctrl1, col_ctrl2 = st.columns([3, 1])
        with col_ctrl1:
            st.markdown("#### 📋 Registro Cronológico de Eventos")
        with col_ctrl2:
            limit_events = st.selectbox("Mostrar últimos:", [20, 50, 100], index=1, key="sel_audit_limit")

        try:
            audit_data = api_client.get_audit_logs(token, limit=limit_events)
            logs = audit_data.get("logs", [])
        except Exception as e:
            st.error(f"Error cargando registros de auditoría: {e}")
            logs = []

        if not logs:
            st.info("No se han registrado eventos administrativos todavía.")
        else:
            table_events = []
            for ev in logs:
                st_icon = "🟢" if ev.get("status") == "success" else ("🟡" if ev.get("status") == "warning" else "🔴")
                table_events.append({
                    "Estado": f"{st_icon} {ev.get('status', 'success').upper()}",
                    "Timestamp": ev.get("timestamp"),
                    "Operador": ev.get("user"),
                    "Acción": ev.get("action"),
                    "Destino": ev.get("target"),
                    "Detalle de la Operación": ev.get("details"),
                    "Event ID": ev.get("event_id"),
                })

            df_events = pd.DataFrame(table_events)
            st.dataframe(df_events, use_container_width=True, hide_index=True)

            col_dw1, col_dw2 = st.columns([1, 3])
            with col_dw1:
                csv_export = df_events.to_csv(index=False)
                st.download_button(
                    label="📥 Exportar Log de Auditoría (.csv)",
                    data=csv_export,
                    file_name="cluster_admin_audit_trail.csv",
                    mime="text/csv",
                    use_container_width=True,
                )

    # --- TAB 2: Security & Sessions ---
    with tab_security:
        st.markdown("#### 🔒 Gobernanza y Políticas de Seguridad del Clúster")
        col_sec1, col_sec2 = st.columns(2)

        with col_sec1:
            with st.container(border=True):
                st.subheader("🛡️ Políticas de Control de Acceso")
                st.markdown("- **Protocolo de Autenticación:** `Bearer JWT (HS256)` con clave segura.")
                st.markdown("- **Persistencia de Tokens:** Almacén seguro en Redis con expiración automática.")
                st.markdown("- **Canal de Notificaciones:** Webhook HTTPS con validación TLS.")
                st.markdown("- **Aislamiento de Workers:** Contenedores Docker efímeros en red aislada.")

        with col_sec2:
            with st.container(border=True):
                st.subheader("👤 Sesión Actual de Operador")
                user_logged = st.session_state.get("username", "wisrovi")
                st.markdown(f"- **Usuario Identificado:** `{user_logged}`")
                st.markdown("- **Rol en el Clúster:** `Cluster SuperAdmin / Architect`")
                st.markdown("- **Nivel de Privilegios:** `Full Control (RW)`")
                st.markdown("- **Estado de Conexión:** `🟢 Activa y Verificada`")
