"""Main Streamlit entrypoint for NeuralForge Cluster Admin."""

import streamlit as st

from frontend import __version__

from frontend.api_client import ClusterApiClient
from frontend.styles import apply_custom_theme
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
from frontend.views.tasks_view import render_tasks


# Page Configuration
st.set_page_config(
    page_title="NeuralForge Cluster Admin",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Apply 5-Star Enterprise Dark Glassmorphism Styling
apply_custom_theme()

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
            f"""
            <div style="background: linear-gradient(135deg, rgba(30, 41, 59, 0.7) 0%, rgba(15, 23, 42, 0.9) 100%); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 12px; padding: 14px 16px; margin-bottom: 20px; box-shadow: 0 4px 20px -2px rgba(0,0,0,0.4);">
                <div style="display: flex; align-items: center; gap: 12px;">
                    <div style="background: linear-gradient(135deg, #3B82F6 0%, #1D4ED8 100%); width: 40px; height: 40px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 1.4rem; box-shadow: 0 0 12px rgba(59, 130, 246, 0.4);">
                        🧠
                    </div>
                    <div>
                        <div style="font-size: 1.15rem; font-weight: 800; color: #FFFFFF; letter-spacing: -0.01em; line-height: 1.2;">NeuralForge</div>
                        <div style="display: flex; align-items: center; gap: 6px; margin-top: 3px;">
                            <span style="font-size: 0.72rem; color: #94A3B8; font-weight: 600; text-transform: uppercase;">Cluster Admin</span>
                            <span style="background: rgba(59, 130, 246, 0.2); color: #60A5FA; border: 1px solid rgba(59, 130, 246, 0.3); font-size: 0.68rem; font-weight: 700; padding: 1px 5px; border-radius: 4px;">v{__version__}</span>
                        </div>
                    </div>
                </div>
                <div style="display: flex; align-items: center; gap: 6px; margin-top: 12px; padding-top: 10px; border-top: 1px solid rgba(255,255,255,0.06);">
                    <span class="pulse-dot pulse-green"></span>
                    <span style="font-size: 0.72rem; font-weight: 700; color: #10B981; letter-spacing: 0.04em;">CLUSTER ACTIVE • 22 GPUS</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.caption("🧭 **NAVIGATION**")

        page = st.radio(
            "Navigation:",
            [
                "📊 Operations Center",
                "⚙️ Nodes & Invokers",
                "🚀 Dispatch & Scheduler",
                "📋 Tasks & Queues Monitor",
                "📁 Storage & Volumes",
                "📈 Job History",
                "🏆 GPU Benchmarks",
                "🌿 FinOps & Energy (Green AI)",
                "🔬 Cluster Capabilities",
                "📜 Audit & Security",
                "🛠️ Maintenance & Settings",
            ],
            index=0,
            label_visibility="collapsed",
        )

        st.divider()

        # User Profile Footer
        avatar_initial = username[:1].upper() if username else "A"
        st.markdown(
            f"""
            <div style="background: rgba(18, 24, 38, 0.6); border: 1px solid rgba(255,255,255,0.06); border-radius: 10px; padding: 10px 12px; margin-bottom: 12px; display: flex; align-items: center; gap: 10px;">
                <div style="width: 32px; height: 32px; border-radius: 50%; background: linear-gradient(135deg, #10B981 0%, #059669 100%); display: flex; align-items: center; justify-content: center; font-weight: 700; color: #FFFFFF; font-size: 0.9rem;">
                    {avatar_initial}
                </div>
                <div style="flex: 1; min-width: 0;">
                    <div style="font-size: 0.85rem; font-weight: 700; color: #FFFFFF; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">{username}</div>
                    <div style="font-size: 0.7rem; color: #94A3B8; text-transform: uppercase; font-weight: 600;">Cluster Operator</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button("🚪 Sign Out", use_container_width=True, type="secondary"):
            st.session_state["authenticated"] = False
            st.session_state["token"] = None
            st.session_state["username"] = None
            st.rerun()

    # Route to selected page
    if page == "📊 Operations Center":
        render_overview(api_client, token)
    elif page == "⚙️ Nodes & Invokers":
        render_invokers(api_client, token)
    elif page == "🚀 Dispatch & Scheduler":
        render_dispatch(api_client, token)
    elif page == "📋 Tasks & Queues Monitor":
        render_tasks(api_client, token)
    elif page == "📁 Storage & Volumes":
        render_storage(api_client, token)
    elif page == "📈 Job History":
        render_history(api_client, token)
    elif page == "🏆 GPU Benchmarks":
        render_benchmarks(api_client, token)
    elif page == "🌿 FinOps & Energy (Green AI)":
        render_finops(api_client, token)
    elif page == "🔬 Cluster Capabilities":
        render_capabilities(api_client, token)
    elif page == "📜 Audit & Security":
        render_audit(api_client, token)
    elif page == "🛠️ Maintenance & Settings":
        render_settings(api_client, token)
