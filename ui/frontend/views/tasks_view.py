"""Tasks and trials monitoring view for Streamlit application."""

import pandas as pd
import streamlit as st
from frontend.api_client import ClusterApiClient


def render_tasks(api_client: ClusterApiClient, token: str):
    """Renders Celery queues, active training trials with epoch telemetry and live logs, historical studies, and Optuna metrics."""
    st.title("🚀 Training & Task Monitoring")
    st.caption("Monitor Celery queues, track active jobs with epoch-level telemetry and live logs, and diagnose past studies.")

    current_user = st.session_state.get("username", "wisrovi")

    # --- Quick Job Dispatcher Expander ---
    with st.expander("⚡ Quick Verification Test Launcher (1-Click Test)", expanded=False):
        st.write("Dispatch a minimal training run (1–5 epochs) to validate a node's connectivity, GPU, Samba, and MinIO.")
        col_q1, col_q2, col_q3, col_q4 = st.columns([1.5, 1.2, 2, 1])

        try:
            invokers_list = api_client.list_invokers(token)
            inv_options = ["wyolo_gpu_queue (Global Public Queue)"] + [f"{i['worker_ip']} ({i['hostname']})" for i in invokers_list]
        except Exception:
            inv_options = ["wyolo_gpu_queue (Global Public Queue)"]

        with col_q1:
            selected_dest = st.selectbox("Target Node / Queue", options=inv_options, key="tasks_quick_target_queue")
            target_ip = None
            if "(" in selected_dest:
                target_ip = selected_dest.split(" ")[0].strip()

        with col_q2:
            quick_model = st.selectbox("Base YOLO Model", options=["yolov8n-cls.pt", "yolo26n-cls.pt", "yolov8s-cls.pt"], key="tasks_quick_model_sel")

        with col_q3:
            quick_dataset = st.text_input("Dataset Path (Samba)", value="/examples/colorball.v8i.multiclass/", key="tasks_quick_data_input")

        with col_q4:
            quick_epochs = st.number_input("Epochs", min_value=1, max_value=5, value=1, step=1, key="tasks_quick_epochs_input")

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

        if st.button("🚀 Dispatch Test Now", type="primary", use_container_width=True, key="tasks_btn_dispatch"):
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

    tab_queues, tab_active, tab_history, tab_metrics = st.tabs([
        "📋 Celery Queues & Waitlist",
        "⚡ Active Tasks & Live Logs",
        "📜 Study History & Diagnostics",
        "📈 Optuna Curves & Metrics",
    ])

    # --- TAB 1: Celery Queues & Waitlist Manager ---
    with tab_queues:
        st.markdown("#### 📋 Gestión y Estado de Colas de Celery")
        st.caption("Inspecciona la lista de espera, reasigna tareas privadas a la cola pública global o promueve prioridades.")

        try:
            queues_data = api_client.get_celery_queues(token)
            total_queued = queues_data.get("total_queued", 0)
            global_queues = queues_data.get("global_queues", {})
            node_queues = queues_data.get("node_queues", {})
            author_breakdown = queues_data.get("author_breakdown", {})
            backlog_eta = queues_data.get("backlog_eta_minutes", 0.0)
            jam_alert = queues_data.get("jam_alert", False)
            jam_reason = queues_data.get("jam_reason")
            pending_tasks = queues_data.get("tasks", [])

            # Jam Alert Banner
            if jam_alert:
                st.error(f"🚨 **{jam_reason}**")
                col_j1, col_j2 = st.columns([3, 1])
                with col_j1:
                    st.caption("Los trabajos no pueden progresar si los nodos no están consumiendo la cola pública.")
                with col_j2:
                    if st.button("▶️ Reanudar Todos los Nodos", key="tview_jam_resume_all", use_container_width=True):
                        try:
                            inv_list = api_client.list_invokers(token)
                            for inv in inv_list:
                                api_client.set_pause(token, inv["worker_ip"], action="resume")
                            st.success("Se envió la señal de reanudación a todos los nodos.")
                            st.rerun()
                        except Exception as re_err:
                            st.error(f"Error reanudando nodos: {re_err}")

            # KPI Cards (Human-Readable)
            col_m1, col_m2, col_m3, col_m4, col_m5 = st.columns(5)
            with col_m1:
                st.metric(
                    label="⚡ Cola Pública Global",
                    value=f"{global_queues.get('wyolo_gpu_queue', 0)} tareas",
                    help="Cola compartida por defecto (wyolo_gpu_queue). Cualquier nodo invoker desocupado toma trabajos de aquí.",
                )
            with col_m2:
                st.metric(
                    label="🔥 Prioridad Alta",
                    value=f"{global_queues.get('gpus_high', 0)} tareas",
                    help="Cola prioritaria (gpus_high). Se atienden antes que cualquier trabajo normal.",
                )
            with col_m3:
                st.metric(
                    label="📦 Baja Prioridad",
                    value=f"{global_queues.get('gpus_low', 0)} tareas",
                    help="Cola en segundo plano (gpus_low). Se procesan en ventanas de baja utilización.",
                )
            with col_m4:
                node_q_sum = sum(node_queues.values())
                st.metric(
                    label="🎯 Encoladas a Nodos",
                    value=f"{node_q_sum} tareas",
                    help="Trabajos dirigidos exclusivamente a nodos específicos (ej. 192.168.1.72).",
                )
            with col_m5:
                eta_h = backlog_eta / 60.0
                st.metric(
                    label="⏳ Tiempo Backlog (ETA)",
                    value=f"~{eta_h:.1f} h" if eta_h >= 1.0 else f"~{backlog_eta:.0f} min",
                    help="Tiempo estimado para procesar todas las tareas en espera con los nodos activos actuales.",
                )

            # Show Node-targeted queues if any
            if node_queues:
                st.markdown("##### 🎯 Nodos con Trabajos Privados en Espera")
                cols_nq = st.columns(min(len(node_queues), 4))
                for idx, (nip, ncount) in enumerate(node_queues.items()):
                    with cols_nq[idx % len(cols_nq)]:
                        st.info(f"🖥️ **Nodo `{nip}`**: **{ncount}** tarea(s) exclusiva(s)")

            # Author Breakdown expander
            if author_breakdown:
                with st.expander(f"👥 Desglose de Espera por Autor ({len(author_breakdown)} investigadores)", expanded=False):
                    col_ab = st.columns(min(len(author_breakdown), 4))
                    for idx, (auth, a_cnt) in enumerate(author_breakdown.items()):
                        with col_ab[idx % len(col_ab)]:
                            st.markdown(f"👤 **{auth}**: `{a_cnt} tareas` ({a_cnt/max(total_queued, 1)*100:.0f}%)")

            st.divider()

            if not pending_tasks:
                st.info("No hay tareas pendientes en ninguna cola de Celery.")
            else:
                # Filter by Author if multiple
                all_authors = ["Todos"] + sorted(list({t.get("author", "Unknown") for t in pending_tasks if t.get("author")}))
                col_f_auth, col_f_info = st.columns([1.5, 3])
                with col_f_auth:
                    sel_auth = st.selectbox("Filtrar lista por autor:", options=all_authors, key="tview_filter_auth_waitlist")

                shown_tasks = pending_tasks
                if sel_auth != "Todos":
                    shown_tasks = [t for t in shown_tasks if t.get("author") == sel_auth]

                st.markdown(f"##### Lista de Espera Detallada ({len(shown_tasks)} mostradas / {total_queued} en total):")
                for t in shown_tasks:
                    tid = t.get("task_id", "N/A")
                    t_study = t.get("study_name", tid)
                    t_author = t.get("author", "Unknown")
                    t_prio = t.get("priority", "NORMAL")
                    t_queue = t.get("queue_name", t.get("queue", "wyolo_gpu_queue"))
                    t_model = t.get("model", "N/A")

                    with st.container(border=True):
                        col_pt1, col_pt2, col_pt3, col_pt4 = st.columns([2.5, 1, 1, 1])
                        with col_pt1:
                            st.markdown(f"**`{t_study}`** | Prioridad: `{t_prio}` | Cola actual: `{t_queue}`")
                            st.caption(f"Task ID: `{tid}` | Autor: `{t_author}` | Modelo: `{t_model}`")
                        with col_pt2:
                            if t_queue != "wyolo_gpu_queue":
                                if st.button("🔀 A Cola Pública", key=f"tview_pub_{tid}", help="Mueve a wyolo_gpu_queue para que cualquier nodo libre pueda tomarla", use_container_width=True):
                                    try:
                                        res = api_client.reassign_celery_task(token, tid, target_queue="wyolo_gpu_queue")
                                        st.success(res.get("message", "Reasignada"))
                                        st.rerun()
                                    except Exception as r_err:
                                        st.error(f"Error reasignando: {r_err}")
                        with col_pt3:
                            if t_queue != "gpus_high":
                                if st.button("⚡ Prioridad ALTA", key=f"tview_prom_{tid}", help="Promover a gpus_high", use_container_width=True):
                                    try:
                                        res = api_client.promote_celery_task(token, tid, target_queue="gpus_high")
                                        st.success(f"Promovida: {res.get('status')}")
                                        st.rerun()
                                    except Exception as pe:
                                        st.error(f"Error promoviendo: {pe}")
                        with col_pt4:
                            if st.button("🗑️ Purgar", key=f"tview_del_{tid}", type="secondary", use_container_width=True):
                                try:
                                    res = api_client.delete_celery_task(token, tid)
                                    st.warning(f"Purgada: {res.get('status')}")
                                    st.rerun()
                                except Exception as de:
                                    st.error(f"Error purgando: {de}")
        except Exception as qe:
            st.error(f"Error cargando colas de Celery: {qe}")

    # --- TAB 2: Active Tasks with Epoch Telemetry and Live Logs ---
    with tab_active:
        st.markdown("#### ⚡ Active Running Tasks")
        st.caption("Real-time progress bars at trial and epoch level, live log streaming, and study cancellation.")

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

                        # Granular epoch telemetry
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
                        if st.button("🛑 Cancel Study", key=f"tview_cancel_{study_id}", type="secondary", use_container_width=True):
                            try:
                                api_client.cancel_task(token, study_id)
                                st.warning(f"Cancellation signal sent for {study_id}.")
                                st.rerun()
                            except Exception as ce:
                                st.error(f"Failed to cancel: {ce}")

                    # Collapsible Live Logs Viewer
                    with st.expander(f"📄 Live Logs ({study_id[:8]}...)", expanded=False):
                        try:
                            logs_res = api_client.get_task_logs(token, study_id, limit=60)
                            lines = logs_res.get("logs", logs_res.get("lines", []))
                            if lines:
                                st.code("\n".join(lines), language="log")
                            else:
                                st.caption("No log stream lines recorded yet.")
                        except Exception as le:
                            st.caption(f"Could not load logs: {le}")

    # --- TAB 3: Study History & Diagnostics ---
    with tab_history:
        st.markdown("#### 🔍 Historical Studies & Diagnostics")

        col_s1, col_s2 = st.columns([3, 1])
        with col_s1:
            search_query = st.text_input(
                "Text search",
                placeholder="Search by study name, study ID, dataset, or model...",
                key="tview_search_input",
                label_visibility="collapsed",
            )
        with col_s2:
            only_mine = st.checkbox("👤 My studies only", value=False, key="tview_cb_only_mine")

        try:
            raw_history = api_client.list_task_history(token, limit=100)
        except Exception as he:
            st.error(f"Failed to load study history: {he}")
            raw_history = []

        all_authors = sorted(list({h.get("author", "Unknown") for h in raw_history if h.get("author")}))
        author_options = ["All"] + all_authors

        all_nodes = sorted(list({h.get("destination_node", "N/A") for h in raw_history if h.get("destination_node")}))
        node_options = ["All"] + all_nodes

        col_f1, col_f2, col_f3, col_f4 = st.columns(4)
        with col_f1:
            sel_author = st.selectbox("Submitter / Author", options=author_options, key="tview_filter_author")
        with col_f2:
            sel_node = st.selectbox("Assigned Node", options=node_options, key="tview_filter_node")
        with col_f3:
            sel_status = st.selectbox("Status", options=["All", "running", "completed", "failed"], key="tview_filter_status")
        with col_f4:
            limit_val = st.selectbox("Record Limit", options=[20, 50, 100], index=1, key="tview_filter_limit")

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
            )

            st.markdown("##### 🔍 Inspect Study Details & Diagnostics")
            study_choices = [f"{h.get('study_name', h.get('study_id'))} ({h.get('study_id')[:8]})" for h in filtered_history]
            selected_inspect = st.selectbox("Select a study to view details:", options=study_choices, key="tview_inspect_sel")
            if selected_inspect:
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

                # Diagnostics Expander
                with st.expander("🩺 Root Cause Diagnostics", expanded=(target_study.get("status") == "failed")):
                    try:
                        diag = api_client.get_task_diagnostics(token, target_study.get("study_id"))
                        st.write(f"**Diagnostic Status:** `{diag.get('status')}`")
                        st.markdown(f"**Root Cause:** {diag.get('root_cause', 'N/A')}")
                        s_act = diag.get("suggested_action")
                        if s_act:
                            st.info(f"💡 **Suggested Action:**\n{s_act}")
                    except Exception as d_err:
                        st.caption(f"Diagnostics unavailable: {d_err}")

                # Logs Expander
                with st.expander("📄 Study Execution Logs", expanded=False):
                    try:
                        log_res = api_client.get_task_logs(token, target_study.get("study_id"), limit=80)
                        lines = log_res.get("logs", log_res.get("lines", []))
                        if lines:
                            st.code("\n".join(lines), language="log")
                        else:
                            st.caption("No log lines stored for this study.")
                    except Exception as l_err:
                        st.caption(f"Logs unavailable: {l_err}")

    # --- TAB 4: Optuna Metrics & Learning Curves ---
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
                key="tview_sel_study_metric",
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
