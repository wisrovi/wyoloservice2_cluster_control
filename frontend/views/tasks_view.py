"""Tasks and trials monitoring view for Streamlit application."""

import pandas as pd
import streamlit as st
from frontend.api_client import ClusterApiClient


def render_tasks(api_client: ClusterApiClient, token: str):
    """Renders active training trials, filtered historical studies, and Optuna metrics."""
    st.title("🚀 Training & Task Monitoring")
    st.caption("Monitor training jobs in real time, filter by submitter or node, and analyze Optuna trials.")

    current_user = st.session_state.get("username", "wisrovi")

    # --- Quick Job Dispatcher Expander ---
    with st.expander("⚡ Quick Verification Test Launcher (1-Click Test)", expanded=False):
        st.write("Dispatch a minimal training run (1–5 epochs) to validate a node's connectivity, GPU, Samba, and MinIO.")
        col_q1, col_q2, col_q3, col_q4 = st.columns([1.5, 1.2, 2, 1])

        # Get invoker list for destination queue selection
        try:
            invokers_list = api_client.list_invokers(token)
            inv_options = ["wyolo_gpu_queue (Global Public Queue)"] + [f"{i['worker_ip']} ({i['hostname']})" for i in invokers_list]
        except Exception:
            inv_options = ["wyolo_gpu_queue (Global Public Queue)"]

        with col_q1:
            selected_dest = st.selectbox("Target Node / Queue", options=inv_options, key="quick_target_queue")
            # Parse IP if specific node
            target_ip = None
            if "(" in selected_dest:
                target_ip = selected_dest.split(" ")[0].strip()

        with col_q2:
            quick_model = st.selectbox("Base YOLO Model", options=["yolov8n-cls.pt", "yolo26n-cls.pt", "yolov8s-cls.pt"], key="quick_model_sel")

        with col_q3:
            quick_dataset = st.text_input("Dataset Path (Samba)", value="/examples/colorball.v8i.multiclass/", key="quick_data_input")

        with col_q4:
            quick_epochs = st.number_input("Epochs", min_value=1, max_value=5, value=1, step=1, key="quick_epochs_input")

        # Dynamic Training Duration Estimator (ETA)
        try:
            eta_res = api_client.estimate_duration(
                token=token,
                model=quick_model,
                epochs=int(quick_epochs),
                dataset=quick_dataset,
            )
            est_min = eta_res.get("estimated_duration_min", 0.0)
            rec_gpu = eta_res.get("recommended_gpu", "GPU")
            throughput = eta_res.get("estimated_throughput_img_s", 0)
            st.info(f"⏱️ **Estimated Duration (ETA):** ~**{est_min:.1f} min** ({est_min/60:.2f}h) | Estimated throughput: ~{throughput} img/s | Suggested GPU: `{rec_gpu}`")
        except Exception as ee:
            st.warning(f"Could not estimate duration: {ee}")

        if st.button("🚀 Dispatch Test Now", type="primary", use_container_width=True):
            try:
                res = api_client.quick_launch_task(
                    token=token,
                    worker_ip=target_ip,
                    model=quick_model,
                    dataset=quick_dataset,
                    epochs=int(quick_epochs),
                )
                st.success(f"✅ Test '{res['data']['study_name']}' successfully sent to queue '{res['data']['target_queue']}'!")
                st.rerun()
            except Exception as qe:
                st.error(f"Failed to dispatch test: {qe}")

    tab_history, tab_active, tab_metrics = st.tabs([
        "📜 Study History & Search",
        "⚡ Active Running Tasks",
        "📈 Metrics & Learning Curves (Optuna)",
    ])

    # --- TAB 1: Historical Studies with Advanced Filters ---
    with tab_history:
        st.markdown("#### 🔍 Advanced Search Filters")

        # Row 1: Search query & quick 'Only My Studies' toggle
        col_s1, col_s2 = st.columns([3, 1])
        with col_s1:
            search_query = st.text_input(
                "Text search",
                placeholder="Search by study name, study ID, dataset, or model...",
                key="tasks_search_input",
                label_visibility="collapsed",
            )
        with col_s2:
            only_mine = st.checkbox("👤 My studies only", value=False, key="cb_only_mine", help="Show only tasks submitted by you")

        # Retrieve a broad set of studies to extract filter choices dynamically
        try:
            raw_history = api_client.list_task_history(token, limit=100)
        except Exception as he:
            st.error(f"Failed to load study history: {he}")
            raw_history = []

        # Extract available authors and destination nodes
        all_authors = sorted(list({h.get("author", "Unknown") for h in raw_history if h.get("author")}))
        author_options = ["All"] + all_authors

        all_nodes = sorted(list({h.get("destination_node", "N/A") for h in raw_history if h.get("destination_node")}))
        node_options = ["All"] + all_nodes

        # Row 2: Secondary filter dropdowns
        col_f1, col_f2, col_f3, col_f4 = st.columns(4)
        with col_f1:
            sel_author = st.selectbox("Submitter / Author", options=author_options, key="filter_author")
        with col_f2:
            sel_node = st.selectbox("Assigned Node", options=node_options, key="filter_node")
        with col_f3:
            sel_status = st.selectbox("Status", options=["All", "running", "completed", "failed"], key="filter_status")
        with col_f4:
            limit_val = st.selectbox("Record Limit", options=[20, 50, 100], index=1, key="filter_limit")

        # Apply client-side filters
        filtered_history = raw_history

        if only_mine:
            filtered_history = [
                h for h in filtered_history
                if current_user.lower() in str(h.get("author", "")).lower()
            ]
        elif sel_author != "All":
            filtered_history = [
                h for h in filtered_history
                if sel_author.lower() in str(h.get("author", "")).lower()
            ]

        if sel_node != "All":
            filtered_history = [
                h for h in filtered_history
                if sel_node.lower() in str(h.get("destination_node", "")).lower()
            ]

        if sel_status != "All":
            filtered_history = [
                h for h in filtered_history
                if h.get("status") == sel_status
            ]

        if search_query:
            sq = search_query.lower().strip()
            filtered_history = [
                h for h in filtered_history
                if sq in str(h.get("study_name", "")).lower()
                or sq in str(h.get("study_id", "")).lower()
                or sq in str(h.get("dataset", "")).lower()
                or sq in str(h.get("model", "")).lower()
            ]

        filtered_history = filtered_history[:limit_val]

        st.caption(f"Showing {len(filtered_history)} of {len(raw_history)} studies registered in Redis:")

        if not filtered_history:
            st.info("No studies match the search criteria.")
        else:
            table_data = []
            for h in filtered_history:
                st_icon = "🟢" if h.get("status") == "completed" else ("⚡" if h.get("status") == "running" else "🔴")
                table_data.append({
                    "Status": f"{st_icon} {h.get('status')}",
                    "Study Name": h.get("study_name", h.get("study_id")),
                    "Submitted By": h.get("author", "Unknown"),
                    "Target Node": h.get("destination_node", "wyolo_gpu_queue"),
                    "Model": h.get("model", "N/A"),
                    "Dataset": h.get("dataset", "N/A"),
                    "Started": h.get("start_time", "N/A"),
                    "Study ID": h.get("study_id"),
                })

            st.dataframe(
                pd.DataFrame(table_data),
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Study Name": st.column_config.TextColumn(width="medium"),
                    "Submitted By": st.column_config.TextColumn(width="medium"),
                    "Target Node": st.column_config.TextColumn(width="medium"),
                    "Dataset": st.column_config.TextColumn(width="large"),
                }
            )

            # Detail inspect box
            st.markdown("##### 🔍 Inspect Study Details")
            study_choices = [f"{h.get('study_name')} ({h.get('study_id')[:8]})" for h in filtered_history]
            selected_inspect = st.selectbox("Select a study to view its full configuration:", options=study_choices)
            if selected_inspect:
                # Find corresponding study
                selected_idx = study_choices.index(selected_inspect)
                target_study = filtered_history[selected_idx]
                col_d1, col_d2 = st.columns([1, 1])
                with col_d1:
                    st.write(f"• **Full Study ID:** `{target_study.get('study_id')}`")
                    st.write(f"• **Author / Submitter:** `{target_study.get('author')}`")
                    st.write(f"• **Node / Host:** `{target_study.get('destination_node')}`")
                    st.write(f"• **Dataset:** `{target_study.get('dataset')}`")
                with col_d2:
                    st.write(f"• **Model:** `{target_study.get('model')}`")
                    st.write(f"• **Status:** `{target_study.get('status')}`")
                    st.write(f"• **Start Date:** `{target_study.get('start_time')}`")
                    if target_study.get("error"):
                        st.error(f"Recorded error: {target_study.get('error')}")

    # --- TAB 2: Active Tasks in Progress ---
    with tab_active:
        try:
            active_tasks = api_client.list_active_tasks(token)
        except Exception as e:
            st.error(f"Failed to load active tasks: {e}")
            active_tasks = []

        if not active_tasks:
            st.info("No training jobs are currently running on the cluster.")
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
                        st.markdown(f"### 🎯 Study: `{study_name}`")
                        st.write(f"• **Submitted by:** `{author}` | **Assigned Node:** `{dest_node}`")
                        st.write(f"• **Model:** `{model}` | **Dataset:** `{task.get('dataset', 'N/A')}`")
                        st.write(f"• **Started:** `{start_time}` | **Study ID:** `{study_id}`")

                        if total_trials > 0:
                            pct = min(completed_trials / total_trials, 1.0)
                            st.progress(pct, text=f"Trial Progress: {completed_trials}/{total_trials} ({int(pct*100)}%)")
                    with col_t2:
                        st.write(" ")
                        st.write(" ")
                        if st.button("🛑 Cancel Study", key=f"btn_cancel_{study_id}", type="secondary"):
                            try:
                                api_client.cancel_task(token, study_id)
                                st.warning(f"Cancellation signal sent for {study_id}.")
                                st.rerun()
                            except Exception as ce:
                                st.error(f"Failed to cancel: {ce}")

    # --- TAB 3: Optuna Metrics & Learning Curves ---
    with tab_metrics:
        st.markdown("#### 📈 Learning Curves & Trial Evolution (Optuna)")
        st.caption("Visualize the objective metric (Accuracy / Fitness / mAP50) across trials.")

        if not raw_history:
            st.info("No studies available to plot metrics.")
        else:
            study_metric_choices = {
                f"{h.get('study_name', h.get('study_id'))} [{h.get('status')}]": h.get("study_id")
                for h in raw_history
            }
            selected_metric_label = st.selectbox(
                "Select the study to analyze:",
                options=list(study_metric_choices.keys()),
                key="sel_study_metric",
            )
            selected_metric_id = study_metric_choices[selected_metric_label]

            try:
                metrics_points = api_client.get_study_metrics(token, selected_metric_id)
            except Exception as me:
                st.error(f"Failed to fetch Optuna metrics: {me}")
                metrics_points = []

            if not metrics_points:
                st.info(f"Study `{selected_metric_id}` has not recorded any metric points in Redis yet.")
            else:
                df_metrics = pd.DataFrame(metrics_points)
                best_val = df_metrics["fitness"].max()
                best_trial_row = df_metrics[df_metrics["fitness"] == best_val].iloc[0]

                col_m1, col_m2 = st.columns([1, 3])
                with col_m1:
                    st.metric(label="🏆 Best Value (Fitness / Acc)", value=f"{best_val:.4f}")
                    st.write(f"• **Best Trial:** `#{int(best_trial_row['trial'])}`")
                    st.write(f"• **Total Recorded Trials:** `{len(df_metrics)}`")
                with col_m2:
                    st.line_chart(df_metrics.set_index("trial")["fitness"])

                with st.expander("📊 View Full Trials & Parameters Table"):
                    st.dataframe(df_metrics, use_container_width=True, hide_index=True)
