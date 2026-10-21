"""Audit trail and security governance view for NeuralForge Cluster Admin."""

import pandas as pd
import streamlit as st
from frontend.api_client import ClusterApiClient
from frontend.styles import render_page_header


def render_audit(api_client: ClusterApiClient, token: str):
    """Renders the Cluster Audit Trail, Security and Administrative Events dashboard."""
    render_page_header(
        title="Audit Trail & Security Governance",
        subtitle="Immutable chronological ledger of all operator interventions, resource limit modifications, and security actions.",
        badge_text="Security Audit",
    )

    tab_timeline, tab_security = st.tabs([
        "🕒 Administrative Operations Timeline",
        "🔒 Sessions & Security Status",
    ])

    # --- TAB 1: Audit Timeline ---
    with tab_timeline:
        col_ctrl1, col_ctrl2 = st.columns([3, 1])
        with col_ctrl1:
            st.markdown("#### 📋 Chronological Event Log")
        with col_ctrl2:
            limit_events = st.selectbox("Show latest:", [20, 50, 100], index=1, key="sel_audit_limit")

        try:
            audit_data = api_client.get_audit_logs(token, limit=limit_events)
            logs = audit_data.get("logs", [])
        except Exception as e:
            st.error(f"Error loading audit records: {e}")
            logs = []

        if not logs:
            st.info("No administrative events have been recorded yet.")
        else:
            table_events = []
            for ev in logs:
                st_icon = "🟢" if ev.get("status") == "success" else ("🟡" if ev.get("status") == "warning" else "🔴")
                table_events.append({
                    "Status": f"{st_icon} {ev.get('status', 'success').upper()}",
                    "Timestamp": ev.get("timestamp"),
                    "Operator": ev.get("user"),
                    "Action": ev.get("action"),
                    "Target": ev.get("target"),
                    "Operation Details": ev.get("details"),
                    "Event ID": ev.get("event_id"),
                })

            df_events = pd.DataFrame(table_events)
            st.dataframe(df_events, use_container_width=True, hide_index=True)

            col_dw1, col_dw2 = st.columns([1, 3])
            with col_dw1:
                csv_export = df_events.to_csv(index=False)
                st.download_button(
                    label="📥 Export Audit Log (.csv)",
                    data=csv_export,
                    file_name="cluster_admin_audit_trail.csv",
                    mime="text/csv",
                    use_container_width=True,
                )

    # --- TAB 2: Security & Sessions ---
    with tab_security:
        st.markdown("#### 🔒 Cluster Security Governance & Policies")
        col_sec1, col_sec2 = st.columns(2)

        with col_sec1:
            with st.container(border=True):
                st.subheader("🛡️ Access Control Policies")
                st.markdown("- **Authentication Protocol:** `Bearer JWT (HS256)` with a secure key.")
                st.markdown("- **Token Persistence:** Secure Redis store with automatic expiration.")
                st.markdown("- **Notification Channel:** HTTPS webhook with TLS validation.")
                st.markdown("- **Worker Isolation:** Ephemeral Docker containers on an isolated network.")

        with col_sec2:
            with st.container(border=True):
                st.subheader("👤 Current Operator Session")
                user_logged = st.session_state.get("username", "wisrovi")
                st.markdown(f"- **Authenticated User:** `{user_logged}`")
                st.markdown("- **Cluster Role:** `Cluster SuperAdmin / Architect`")
                st.markdown("- **Privilege Level:** `Full Control (RW)`")
                st.markdown("- **Connection Status:** `🟢 Active & Verified`")
