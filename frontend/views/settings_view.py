"""Cluster settings and account management view for Streamlit application."""

import streamlit as st
from frontend.api_client import ClusterApiClient


def render_settings(api_client: ClusterApiClient, token: str):
    """Renders global cluster batch controls and user account settings."""
    st.title("🛠️ Global Cluster & Account Settings")

    col_batch, col_account = st.columns(2, gap="large")

    with col_batch:
        with st.container(border=True):
            st.subheader("🌐 Bulk Limit Adjustment (Cluster-Wide)")
            st.caption("Apply a uniform MAX_GPU percentage to every invoker node in the cluster.")

            batch_gpu = st.slider("Global MAX_GPU for all nodes (%)", min_value=10, max_value=100, value=30, step=5)
            batch_ram = st.text_input("Default RAM for all nodes", value="16g")

            if st.button("🚀 Apply to Entire Cluster", type="primary"):
                try:
                    res = api_client.batch_update_limits(
                        token=token,
                        max_gpu_percent=float(batch_gpu),
                        max_ram=batch_ram,
                    )
                    st.success(res.get("message", "Limits applied to the cluster."))
                except Exception as be:
                    st.error(f"Bulk update failed: {be}")

    with col_account:
        with st.container(border=True):
            st.subheader("🔒 Change Password")
            st.caption(f"Current user: **{st.session_state.get('username', 'wisrovi')}**")

            with st.form("change_pwd_form"):
                current_pwd = st.text_input("Current Password", type="password")
                new_pwd = st.text_input("New Password", type="password")
                confirm_pwd = st.text_input("Confirm New Password", type="password")
                submit_pwd = st.form_submit_button("Update Password")

                if submit_pwd:
                    if not current_pwd or not new_pwd:
                        st.error("Please fill in all fields.")
                    elif new_pwd != confirm_pwd:
                        st.error("The new passwords do not match.")
                    elif len(new_pwd) < 6:
                        st.error("The new password must be at least 6 characters long.")
                    else:
                        try:
                            api_client.change_password(token, current_pwd, new_pwd)
                            st.success("✅ Password successfully updated in Redis.")
                        except Exception as ce:
                            st.error(f"Error: {ce}")

    st.markdown("---")
    with st.container(border=True):
        st.subheader("🔔 Webhook Notifications (Discord / Slack / Telegram)")
        st.caption("Receive automatic alerts on external channels when a node fails, goes offline, or a training run finishes.")

        # Load current webhook config
        try:
            current_wh = api_client.get_webhook_config(token)
        except Exception:
            current_wh = {"webhook_url": "", "enabled": False}

        col_wh1, col_wh2 = st.columns([3, 1], gap="medium")
        with col_wh1:
            wh_url = st.text_input(
                "Webhook URL (Discord / Slack / Telegram HTTP POST)",
                value=current_wh.get("webhook_url", ""),
                placeholder="https://discord.com/api/webhooks/... or https://hooks.slack.com/services/...",
            )
            wh_enabled = st.checkbox(
                "Enable automatic cluster event alerts",
                value=current_wh.get("enabled", False),
            )
        with col_wh2:
            st.write(" ")
            st.write(" ")
            if st.button("💾 Save Webhook", type="primary", use_container_width=True):
                try:
                    res = api_client.save_webhook_config(token, webhook_url=wh_url, enabled=wh_enabled)
                    st.success(res.get("message", "Webhook configuration saved successfully."))
                except Exception as we:
                    st.error(f"Failed to save webhook: {we}")

            if st.button("🔔 Send Test Notification", use_container_width=True):
                try:
                    res_test = api_client.test_webhook(token)
                    st.info(res_test.get("message", "Test notification sent."))
                except Exception as te:
                    st.error(f"Webhook test failed: {te}")

            if st.button("⚡ Run Watchdog & Alert Now", use_container_width=True, help="Scan cluster health and send alerts if any failures are found"):
                try:
                    res_wd = api_client.trigger_watchdog_alert(token)
                    alerts = res_wd.get("alerts_detected", [])
                    if alerts:
                        st.warning(f"⚠️ Alerts detected ({len(alerts)}): {'; '.join(alerts)}")
                        if res_wd.get("webhook_sent"):
                            st.success("Notification sent to the configured webhook.")
                    else:
                        st.success("🟢 Cluster fully healthy. No pending alerts.")
                except Exception as wde:
                    st.error(f"Watchdog run failed: {wde}")

    st.markdown("---")
    with st.container(border=True):
        st.subheader("🧹 Redis Cleanup & Maintenance (Cluster Housekeeping)")
        st.caption("Inspect and purge failed or cancelled studies and stale temporary keys to optimize Redis memory usage.")

        try:
            hk_preview = api_client.get_housekeeping_preview(token)
            stale_count = hk_preview.get("stale_failed_studies_count", 0)
            stale_ids = hk_preview.get("stale_study_ids", [])
            mem_human = hk_preview.get("redis_memory_human", "N/A")
            reclaimed_kb = hk_preview.get("estimated_reclaimed_kb", 0)

            col_hk1, col_hk2, col_hk3 = st.columns([1.5, 1.5, 2], gap="medium")
            with col_hk1:
                st.metric(label="💾 Memory in Use (Redis)", value=mem_human)
            with col_hk2:
                st.metric(
                    label="🗑️ Stale Studies Detected",
                    value=stale_count,
                    delta=f"~{reclaimed_kb} KB reclaimable",
                    delta_color="inverse" if stale_count > 0 else "off",
                )
            with col_hk3:
                st.write(" ")
                if st.button("🧹 Purge Stale Studies Now", type="secondary", use_container_width=True, disabled=(stale_count == 0)):
                    try:
                        res_purge = api_client.purge_housekeeping(token)
                        st.success(res_purge.get("message", "Purge completed."))
                        st.rerun()
                    except Exception as pe:
                        st.error(f"Purge failed: {pe}")

            if stale_ids:
                with st.expander(f"View the {len(stale_ids)} studies flagged for cleanup"):
                    for sid in stale_ids:
                        st.write(f"• `{sid}` (failed / cancelled)")
        except Exception as he:
            st.caption(f"Could not load the maintenance assistant: {he}")
