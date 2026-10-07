"""Main Streamlit entrypoint for NeuralForge Cluster Admin."""

import streamlit as st

from frontend.api_client import ClusterApiClient
from frontend.views.audit_view import render_audit
from frontend.views.benchmarks_view import render_benchmarks
from frontend.views.capabilities_view import render_capabilities
from frontend.views.dispatch_view import render_dispatch
from frontend.views.finops_view import render_finops
from frontend.views.history_view import render_history
from frontend.views.invokers_view import render_invokers
from frontend.views.login_view import render_login
from frontend.views.overview_view import render_overview
from frontend.views.settings_view import render_settings
from frontend.views.storage_view import render_storage


# Page Configuration
st.set_page_config(
    page_title="NeuralForge Cluster Admin",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialize API client
api_client = ClusterApiClient()

# Check authentication state
if not st.session_state.get("authenticated", False):
    render_login(api_client)
else:
    token = st.session_state.get("token", "")
    username = st.session_state.get("username", "admin")

    # Sidebar Navigation and User Info
    with st.sidebar:
        st.markdown(
            """
            <div style="display: flex; align-items: center; margin-bottom: 20px;">
                <span style="font-size: 2.2em; margin-right: 10px;">🧠</span>
                <div>
                    <h3 style="margin: 0; padding: 0;">NeuralForge</h3>
                    <p style="color: #6c757d; margin: 0; font-size: 0.85em;">Cluster Admin Platform <span style="background-color: #3b82f6; color: white; padding: 2px 6px; border-radius: 4px; font-size: 0.8em; font-weight: bold;">v1.5.0</span></p>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.caption(f"👤 Conectado como: **{username}** (Admin)")

        page = st.radio(
            "Navegación:",
            [
                "📊 Centro de Operaciones",
                "⚙️ Nodos e Invokers",
                "🚀 Despacho & Scheduler",
                "📁 Almacenamiento y Volúmenes",
                "📈 Historial de Trabajos",
                "🏆 Benchmarks de GPUs",
                "🌿 FinOps y Energía (Green AI)",
                "🔬 Capacidades del Clúster",
                "📜 Auditoría y Seguridad",
                "🛠️ Mantenimiento y Ajustes",
            ],
            index=0,
            label_visibility="collapsed",
        )

        st.divider()

        if st.button("🚪 Cerrar Sesión", use_container_width=True, type="secondary"):
            st.session_state["authenticated"] = False
            st.session_state["token"] = None
            st.session_state["username"] = None
            st.rerun()

    # Route to selected page
    if page == "📊 Centro de Operaciones":
        render_overview(api_client, token)
    elif page == "⚙️ Nodos e Invokers":
        render_invokers(api_client, token)
    elif page == "🚀 Despacho & Scheduler":
        render_dispatch(api_client, token)
    elif page == "📁 Almacenamiento y Volúmenes":
        render_storage(api_client, token)
    elif page == "📈 Historial de Trabajos":
        render_history(api_client, token)
    elif page == "🏆 Benchmarks de GPUs":
        render_benchmarks(api_client, token)
    elif page == "🌿 FinOps y Energía (Green AI)":
        render_finops(api_client, token)
    elif page == "🔬 Capacidades del Clúster":
        render_capabilities(api_client, token)
    elif page == "📜 Auditoría y Seguridad":
        render_audit(api_client, token)
    elif page == "🛠️ Mantenimiento y Ajustes":
        render_settings(api_client, token)
