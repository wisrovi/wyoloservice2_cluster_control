"""Login view for Streamlit application."""

import streamlit as st
from frontend.api_client import ClusterApiClient


def render_login(api_client: ClusterApiClient):
    """Renders the authentication form."""
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.markdown(
            """
            <div style="text-align: center; margin-top: 50px; margin-bottom: 30px;">
                <h1>🧠 NeuralForge Cluster Admin</h1>
                <p style="color: #6c757d; font-size: 1.1em;">
                    Distributed Invoker Orchestration & Dynamic Resource Manager
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        with st.container(border=True):
            st.subheader("🔐 Sign In")
            st.caption("Enter your cluster access credentials.")

            with st.form("login_form", clear_on_submit=False):
                username = st.text_input(
                    "Username",
                    value=st.session_state.get("login_user_input", "wisrovi"),
                    placeholder="Enter your username",
                    key="login_user_input",
                )
                password = st.text_input(
                    "Password",
                    type="password",
                    value=st.session_state.get("login_pass_input", "wyoloservice"),
                    placeholder="••••••••",
                    key="login_pass_input",
                )
                submitted = st.form_submit_button("🚀 Access Dashboard", use_container_width=True)

                if submitted:
                    user_val = username.strip() if username else "wisrovi"
                    pass_val = password.strip() if password else "wyoloservice"
                    try:
                        res = api_client.login(username=user_val, password=pass_val)
                        st.session_state["authenticated"] = True
                        st.session_state["token"] = res["access_token"]
                        st.session_state["username"] = res["username"]
                        st.success(f"Welcome, {res['username']}! Loading dashboard...")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Authentication failed: {e}")
