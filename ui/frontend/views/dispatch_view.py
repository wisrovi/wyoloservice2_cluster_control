"""Task Dispatcher and Active Training monitor view for NeuralForge Cluster Control."""

import streamlit as st
from frontend.api_client import ClusterApiClient


def render_dispatch(api_client: ClusterApiClient, token: str):
    """Renders smart task dispatcher, duration estimator, and active training progress."""
    st.title("🚀 Smart Dispatch & Active Tasks")
    st.caption("Launch training jobs with smart node recommendations and monitor active tasks in real time.")

    current_user = st.session_state.get("username", "wisrovi")

    # --- Section 1: Smart Task Dispatcher ---
    with st.container(border=True):
        st.subheader("⚡ Smart Training Launcher")
        st.caption("Configure the model and dataset. Dispatch to a specific queue or let the system select the optimal node.")

        # Row 1: Model & Dataset configuration
        col_m1, col_m2, col_m3 = st.columns([1.5, 2.5, 1])
        with col_m1:
            model_options = [
                "yolov8n-cls.pt",
                "yolo26n-cls.pt",
                "yolov8s-cls.pt",
                "yolov8m-cls.pt",
                "yolov8x-cls.pt",
            ]
            selected_model = st.selectbox("YOLO Model", options=model_options, index=0, key="dispatch_model_sel")
        with col_m2:
            dataset_path = st.text_input("Samba Dataset Path", value="/examples/colorball.v8i.multiclass/", key="dispatch_dataset_input")
        with col_m3:
            epochs = st.number_input("Epochs", min_value=1, max_value=200, value=2, step=1, key="dispatch_epochs_input")

        # Row 2: Smart Recommendation Button & Destination Selection
        try:
            invokers_list = api_client.list_invokers(token)
            inv_options = ["wyolo_gpu_queue (Global Public Queue)"] + [f"{i['worker_ip']} ({i['hostname']})" for i in invokers_list]
        except Exception:
            inv_options = ["wyolo_gpu_queue (Global Public Queue)"]

        col_smart, col_queue = st.columns([1.5, 2.5], gap="medium")

        # Session state for recommended target
        if "recommended_target" not in st.session_state:
            st.session_state["recommended_target"] = inv_options[0]

        with col_smart:
            st.write(" ")
            if st.button("🪄 Recommend Best Node", type="secondary", use_container_width=True):
                try:
                    rec = api_client.recommend_node(token, selected_model)
                    rec_ip = rec.get("target_ip")
                    rec_host = rec.get("hostname")
                    rec_reason = rec.get("reason", "")
                    rec_score = rec.get("score", 0)

                    # Find matching option in list
                    match_found = False
                    for opt in inv_options:
                        if rec_ip in opt:
                            st.session_state["recommended_target"] = opt
                            match_found = True
                            break

                    if not match_found and rec_ip == "wyolo_gpu_queue":
                        st.session_state["recommended_target"] = inv_options[0]

                    st.toast(f"Recommended node: {rec_host} (Score: {rec_score:.0f})", icon="🪄")
                    st.info(f"💡 **Recommendation ({rec_host}):** {rec_reason}")
                except Exception as re:
                    st.warning(f"Could not compute a recommendation: {re}")

        col_target, col_prio = st.columns([2.5, 1.5])
        with col_target:
            target_selection = st.selectbox(
                "Target Node / Queue",
                options=inv_options,
                index=inv_options.index(st.session_state["recommended_target"]) if st.session_state["recommended_target"] in inv_options else 0,
                key="dispatch_target_queue_sel",
            )
        with col_prio:
            priority_label = st.selectbox(
                "Execution Priority",
                options=["⚡ NORMAL", "🔥 URGENT", "📦 BATCH"],
                index=0,
                key="dispatch_priority_sel",
            )
            priority_val = priority_label.split(" ")[-1]

        # Parse target IP
        target_ip = None
        if "(" in target_selection:
            target_ip = target_selection.split(" ")[0].strip()

        # Dynamic Duration Estimator (ETA)
        try:
            eta = api_client.estimate_duration(token, selected_model, int(epochs), dataset_path)
            est_min = eta.get("estimated_duration_min", 0.0)
            rec_gpu = eta.get("recommended_gpu", "GPU")
            tput = eta.get("estimated_throughput_img_s", 0)
            st.info(f"⏱️ **Estimated Duration (ETA):** ~**{est_min:.1f} min** ({est_min/60:.2f}h) | Estimated throughput: ~{tput} img/s | Suggested GPU: `{rec_gpu}` | Priority: `{priority_val}`")
        except Exception:
            pass

        # Dispatch button
        if st.button("🚀 Dispatch Training Now", type="primary", use_container_width=True):
            try:
                res = api_client.quick_launch_task(
                    token=token,
                    worker_ip=target_ip,
                    model=selected_model,
                    dataset=dataset_path,
                    epochs=int(epochs),
                    priority=priority_val,
                )
                study_created = res.get("data", {}).get("study_name", "New Study")
                target_q = res.get("data", {}).get("target_queue", "wyolo_gpu_queue")
                st.success(f"✅ Study '{study_created}' [{priority_val}] successfully dispatched to queue '{target_q}'!")
                st.rerun()
            except Exception as qe:
                st.error(f"Failed to dispatch study: {qe}")

    st.markdown("---")

    # --- Section 2: Active Training Monitor ---
    st.subheader("⚡ Training Jobs Running on the Cluster")
    st.caption("Monitor trial progress and stop runs when needed.")

    try:
        active_tasks = api_client.list_active_tasks(token)
    except Exception as ae:
        st.error(f"Failed to load active tasks: {ae}")
        active_tasks = []

    if not active_tasks:
        st.info("No training jobs are currently running.")
    else:
        for task in active_tasks:
            study_id = task.get("study_id")
            study_name = task.get("study_name", study_id)
            author = task.get("author", "Unknown")
            dest_node = task.get("destination_node", task.get("invoker", "wyolo_gpu_queue"))
            model = task.get("model", "N/A")
            start_time = task.get("start_time", "N/A")
            progress = task.get("progress", {})
            completed_trials = progress.get("completed_trials", 0)
            total_trials = progress.get("total_trials", 1)

            with st.container(border=True):
                col_t1, col_t2 = st.columns([3, 1])
                with col_t1:
                    st.markdown(f"### 🎯 `{study_name}`")
                    st.write(f"• **Submitted by:** `{author}` | **Assigned Node:** `{dest_node}`")
                    st.write(f"• **Model:** `{model}` | **Dataset:** `{task.get('dataset', 'N/A')}`")
                    st.write(f"• **Started:** `{start_time}` | **Study ID:** `{study_id}`")

                    if total_trials > 0:
                        pct = min(completed_trials / total_trials, 1.0)
                        st.progress(pct, text=f"Trial Progress: {completed_trials}/{total_trials} ({int(pct*100)}%)")

                    # Epoch-level granular progress
                    epoch_prog = task.get("epoch_progress")
                    if epoch_prog:
                        curr_ep = epoch_prog.get("epoch", 0)
                        tot_ep = max(epoch_prog.get("total_epochs", 1), 1)
                        ep_pct = min(curr_ep / tot_ep, 1.0)
                        ep_text = f"Epoch {curr_ep}/{tot_ep}"
                        if epoch_prog.get("loss") is not None:
                            ep_text += f" | Loss: {epoch_prog.get('loss'):.4f}"
                        if epoch_prog.get("top1") is not None:
                            ep_text += f" | Top-1: {epoch_prog.get('top1')*100:.1f}%"
                        st.progress(ep_pct, text=ep_text)

                with col_t2:
                    st.write(" ")
                    st.write(" ")
                    if st.button("🛑 Cancel Study", key=f"btn_cancel_{study_id}", type="secondary", use_container_width=True):
                        try:
                            api_client.cancel_task(token, study_id)
                            st.warning(f"Cancellation signal sent for {study_id}.")
                            st.rerun()
                        except Exception as ce:
                            st.error(f"Failed to cancel study: {ce}")

                # Live Logs and Diagnostics expanders
                col_exp1, col_exp2 = st.columns(2)
                with col_exp1:
                    with st.expander(f"📄 Live Logs ({study_id[:8]}...)", expanded=False):
                        try:
                            logs_res = api_client.get_task_logs(token, study_id, limit=50)
                            log_lines = logs_res.get("logs", logs_res.get("lines", []))
                            if log_lines:
                                st.code("\n".join(log_lines), language="log")
                            else:
                                st.caption("No log stream lines recorded yet.")
                        except Exception as le:
                            st.caption(f"Could not load logs: {le}")

                with col_exp2:
                    with st.expander(f"🩺 Diagnostics ({study_id[:8]}...)", expanded=False):
                        try:
                            diag_res = api_client.get_task_diagnostics(token, study_id)
                            st.write(f"**Status:** `{diag_res.get('status')}`")
                            st.write(f"**Root Cause:** {diag_res.get('root_cause', 'N/A')}")
                            s_act = diag_res.get("suggested_action")
                            if s_act:
                                st.info(f"💡 **Suggested Action:**\n{s_act}")
                        except Exception as de:
                            st.caption(f"Diagnostics unavailable: {de}")

    st.markdown("---")

    # --- Section 3: Celery Queues & Waitlist Manager ---
    st.subheader("📋 Celery Task Queues & Waitlist Manager")
    st.caption("Inspect pending tasks across priority queues, promote urgent jobs, or purge stale waitlist items.")

    try:
        queues_data = api_client.get_celery_queues(token)
        q_counts = queues_data.get("queues", {})
        total_queued = queues_data.get("total_queued", 0)
        pending_tasks = queues_data.get("tasks", [])

        # Priority Queue Metric Cards
        cols_q = st.columns(max(len(q_counts), 1))
        for idx, (q_name, count) in enumerate(q_counts.items()):
            if idx < len(cols_q):
                with cols_q[idx]:
                    st.metric(label=f"Queue: {q_name}", value=count)

        if not pending_tasks:
            st.info("No pending tasks currently waiting in Celery queues.")
        else:
            st.markdown(f"##### Pending Tasks in Waitlist ({len(pending_tasks)} / Total Queued: {total_queued})")
            for t in pending_tasks:
                tid = t.get("task_id", "N/A")
                t_study = t.get("study_name", tid)
                t_author = t.get("author", "Unknown")
                t_prio = t.get("priority", "NORMAL")
                t_queue = t.get("queue", "wyolo_gpu_queue")
                t_model = t.get("model", "N/A")

                with st.container(border=True):
                    col_pt1, col_pt2, col_pt3 = st.columns([3, 1, 1])
                    with col_pt1:
                        st.markdown(f"**`{t_study}`** | Priority: `{t_prio}` | Queue: `{t_queue}`")
                        st.caption(f"Task ID: `{tid}` | Author: `{t_author}` | Model: `{t_model}`")
                    with col_pt2:
                        if t_queue != "gpus_high":
                            if st.button("⚡ Promote to HIGH", key=f"prom_{tid}", use_container_width=True):
                                try:
                                    res = api_client.promote_celery_task(token, tid, target_queue="gpus_high")
                                    st.success(f"Task promoted to gpus_high: {res.get('status')}")
                                    st.rerun()
                                except Exception as pe:
                                    st.error(f"Promotion failed: {pe}")
                    with col_pt3:
                        if st.button("🗑️ Purge", key=f"del_{tid}", type="secondary", use_container_width=True):
                            try:
                                res = api_client.delete_celery_task(token, tid)
                                st.warning(f"Task purged from queue: {res.get('status')}")
                                st.rerun()
                            except Exception as de:
                                st.error(f"Purge failed: {de}")
    except Exception as qe:
        st.error(f"Failed to load Celery queues: {qe}")

