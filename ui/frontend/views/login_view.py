"""Login view for Streamlit application with Enterprise 5-Star styling."""

import streamlit as st
from frontend.api_client import ClusterApiClient
from frontend.styles import apply_custom_theme


def render_login(api_client: ClusterApiClient):
    """Renders the authentication portal with enterprise styling."""
    apply_custom_theme()

    col1, col2, col3 = st.columns([1, 1.8, 1])

    with col2:
        st.markdown(
            """
            <div style="text-align: center; margin-top: 3.5rem; margin-bottom: 2rem;">
                <div style="display: inline-flex; align-items: center; justify-content: center; width: 68px; height: 68px; border-radius: 18px; background: linear-gradient(135deg, #3B82F6 0%, #1D4ED8 100%); font-size: 2.2rem; box-shadow: 0 0 30px rgba(59, 130, 246, 0.4); margin-bottom: 1rem;">
                    🧠
                </div>
                <h1 style="font-size: 2.4rem; font-weight: 800; margin: 0; color: #FFFFFF; letter-spacing: -0.02em;">NeuralForge</h1>
                <p style="color: #94A3B8; font-size: 1.05rem; margin-top: 6px; font-weight: 500;">
                    Enterprise Distributed AI Cluster & Resource Orchestrator
                </p>
                <div style="display: inline-flex; gap: 8px; margin-top: 10px;">
                    <span style="background: rgba(59, 130, 246, 0.12); color: #60A5FA; border: 1px solid rgba(59, 130, 246, 0.25); font-size: 0.75rem; font-weight: 700; padding: 3px 8px; border-radius: 6px;">☸️ K8s / Docker</span>
                    <span style="background: rgba(16, 185, 129, 0.12); color: #34D399; border: 1px solid rgba(16, 185, 129, 0.25); font-size: 0.75rem; font-weight: 700; padding: 3px 8px; border-radius: 6px;">⚡ 22 GPUs</span>
                    <span style="background: rgba(139, 92, 246, 0.12); color: #A78BFA; border: 1px solid rgba(139, 92, 246, 0.25); font-size: 0.75rem; font-weight: 700; padding: 3px 8px; border-radius: 6px;">🔒 JWT Secured</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        with st.container(border=True):
            st.markdown(
                """
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                    <h3 style="margin: 0; font-size: 1.25rem; font-weight: 700; color: #FFFFFF;">Operator Authentication</h3>
                    <span style="font-size: 0.75rem; color: #10B981; font-weight: 700; background: rgba(16, 185, 129, 0.1); padding: 3px 8px; border-radius: 6px; border: 1px solid rgba(16, 185, 129, 0.2);">GATEWAY READY</span>
                </div>
                """,
                unsafe_allow_html=True,
            )

            with st.form("login_form", clear_on_submit=False):
                username = st.text_input(
                    "Operator Username",
                    value=st.session_state.get("login_user_input", "wisrovi"),
                    placeholder="Enter your cluster username",
                    key="login_user_input",
                )
                password = st.text_input(
                    "Security Key / Password",
                    type="password",
                    value=st.session_state.get("login_pass_input", "wyoloservice"),
                    placeholder="••••••••••••",
                    key="login_pass_input",
                )
                submitted = st.form_submit_button("🚀 Enter Operations Console", use_container_width=True, type="primary")

                if submitted:
                    user_val = username.strip() if username else "wisrovi"
                    pass_val = password.strip() if password else "wyoloservice"
                    try:
                        res = api_client.login(username=user_val, password=pass_val)
                        st.session_state["authenticated"] = True
                        st.session_state["token"] = res["access_token"]
                        st.session_state["username"] = res["username"]
                        st.success(f"Identity confirmed. Welcome back, {res['username']}!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Authentication failed: {e}")

        st.caption("🔒 Encrypted session managed via SHA-256 salted tokens in Redis `cluster:auth:users`.")

