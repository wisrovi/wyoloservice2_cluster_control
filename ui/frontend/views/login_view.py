"""Login view for Streamlit application with VSCode Workbench styling."""

import streamlit as st
from frontend.api_client import ClusterApiClient
from frontend.styles import apply_custom_theme


def render_login(api_client: ClusterApiClient):
    """Renders the authentication portal with VSCode Workbench styling."""
    apply_custom_theme()

    col1, col2, col3 = st.columns([1, 1.8, 1])

    with col2:
        st.markdown(
            """
            <div style="text-align: center; margin-top: 3.5rem; margin-bottom: 2rem;">
                <div style="display: inline-flex; align-items: center; justify-content: center; width: 64px; height: 64px; border-radius: 12px; background: #007ACC; font-size: 2.2rem; box-shadow: 0 0 24px rgba(0, 122, 204, 0.4); margin-bottom: 1rem;">
                    🧠
                </div>
                <h1 style="font-size: 2.2rem; font-weight: 700; margin: 0; color: #FFFFFF; letter-spacing: -0.01em;">NeuralForge</h1>
                <p style="color: #858585; font-size: 1.0rem; margin-top: 6px; font-weight: 500;">
                    Visual Studio Code Workbench for Distributed AI Cluster Orchestration
                </p>
                <div style="display: inline-flex; gap: 6px; margin-top: 8px;">
                    <span style="background: #252526; color: #60A5FA; border: 1px solid #3C3C3C; font-size: 0.72rem; font-weight: 700; padding: 2px 7px; border-radius: 3px;">☸️ K8s / Docker</span>
                    <span style="background: #252526; color: #34D399; border: 1px solid #3C3C3C; font-size: 0.72rem; font-weight: 700; padding: 2px 7px; border-radius: 3px;">⚡ 22 GPUs</span>
                    <span style="background: #252526; color: #007ACC; border: 1px solid #3C3C3C; font-size: 0.72rem; font-weight: 700; padding: 2px 7px; border-radius: 3px;">VSCode v2.2.0</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        with st.container(border=True):
            st.markdown(
                """
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; border-bottom: 1px solid #2B2B2B; padding-bottom: 8px;">
                    <span style="font-size: 0.95rem; font-weight: 700; color: #FFFFFF;">Sign in to Workbench</span>
                    <span style="font-size: 0.72rem; color: #10B981; font-weight: 700; background: rgba(16, 185, 129, 0.12); padding: 2px 6px; border-radius: 3px; border: 1px solid rgba(16, 185, 129, 0.25);">CLUSTER ONLINE</span>
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
                submitted = st.form_submit_button("🚀 Enter VSCode Workbench", use_container_width=True, type="primary")

                if submitted:
                    user_val = username.strip() if username else "wisrovi"
                    pass_val = password.strip() if password else "wyoloservice"
                    try:
                        res = api_client.login(username=user_val, password=pass_val)
                        st.session_state["authenticated"] = True
                        st.session_state["token"] = res["access_token"]
                        st.session_state["username"] = res["username"]
                        st.success(f"Identity confirmed. Welcome, {res['username']}!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Authentication failed: {e}")

        st.caption("🔒 Encrypted session managed via SHA-256 salted tokens in Redis `cluster:auth:users`.")
