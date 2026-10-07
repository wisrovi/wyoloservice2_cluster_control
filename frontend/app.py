"""Main Streamlit entrypoint for wyoloservice2_cluster_control."""

import streamlit as st

from frontend.api_client import ClusterApiClient
from frontend.views.invokers_view import render_invokers
from frontend.views.login_view import render_login
from frontend.views.overview_view import render_overview
from frontend.views.settings_view import render_settings
from frontend.views.tasks_view import render_tasks


# Page Configuration
st.set_page_config(
    page_title="NeuralForge Cluster Control",
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
                    <p style="color: #6c757d; margin: 0; font-size: 0.85em;">Cluster Control Platform <span style="background-color: #3b82f6; color: white; padding: 2px 6px; border-radius: 4px; font-size: 0.8em; font-weight: bold;">v1.2.0</span></p>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.caption(f"👤 Conectado como: **{username}**")

        page = st.radio(
            "Navegación:",
            ["📊 Resumen", "⚙️ Nodos Invoker", "🚀 Entrenamientos", "🛠️ Configuración Global"],
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
    if page == "📊 Resumen":
        render_overview(api_client, token)
    elif page == "⚙️ Nodos Invoker":
        render_invokers(api_client, token)
    elif page == "🚀 Entrenamientos":
        render_tasks(api_client, token)
    elif page == "🛠️ Configuración Global":
        render_settings(api_client, token)
