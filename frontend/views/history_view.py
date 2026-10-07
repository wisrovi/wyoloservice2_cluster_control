"""Study History, Optuna Analytics, and Report Exporter view for NeuralForge Cluster Control."""

import json
import pandas as pd
import streamlit as st
from frontend.api_client import ClusterApiClient


def render_history(api_client: ClusterApiClient, token: str):
    """Renders historical study browser, Optuna trial curves, and 1-click report export."""
    st.title("📈 Study History, Metrics & Reports")
    st.caption("Advanced search, Optuna learning curves, and experiment report export.")

    current_user = st.session_state.get("username", "wisrovi")

    tab_history, tab_metrics, tab_compare, tab_export = st.tabs([
        "📜 History & Search",
        "📈 Learning Curves (Optuna)",
        "🔬 Head-to-Head Comparison",
        "📥 Report Exporter",
    ])

    # Fetch history
    try:
        raw_history = api_client.list_task_history(token, limit=100)
    except Exception as he:
        st.error(f"Failed to load study history: {he}")
        raw_history = []

    # --- TAB 1: History Search and Filters ---
    with tab_history:
        st.markdown("#### 🔍 Search Filters")

        col_s1, col_s2 = st.columns([3, 1])
        with col_s1:
            search_query = st.text_input(
                "Search",
                placeholder="Search by study name, study ID, dataset, or model...",
                key="hist_search_input",
                label_visibility="collapsed",
            )
        with col_s2:
            only_mine = st.checkbox("👤 My studies only", value=False, key="hist_cb_only_mine")

        all_authors = sorted(list({h.get("author", "Unknown") for h in raw_history if h.get("author")}))
        author_options = ["All"] + all_authors

        all_nodes = sorted(list({h.get("destination_node", "N/A") for h in raw_history if h.get("destination_node")}))
        node_options = ["All"] + all_nodes

        col_f1, col_f2, col_f3, col_f4 = st.columns(4)
        with col_f1:
            sel_author = st.selectbox("Submitter / Author", options=author_options, key="hist_filter_author")
        with col_f2:
            sel_node = st.selectbox("Assigned Node", options=node_options, key="hist_filter_node")
        with col_f3:
            sel_status = st.selectbox("Status", options=["All", "completed", "running", "failed"], key="hist_filter_status")
        with col_f4:
            limit_val = st.selectbox("Record Limit", options=[20, 50, 100], index=1, key="hist_filter_limit")

        # Filtering logic
        filtered = raw_history
        if only_mine:
            filtered = [h for h in filtered if current_user.lower() in str(h.get("author", "")).lower()]
        elif sel_author != "All":
            filtered = [h for h in filtered if sel_author.lower() in str(h.get("author", "")).lower()]

        if sel_node != "All":
            filtered = [h for h in filtered if sel_node.lower() in str(h.get("destination_node", "")).lower()]

        if sel_status != "All":
            filtered = [h for h in filtered if h.get("status") == sel_status]

        if search_query:
            sq = search_query.lower().strip()
            filtered = [
                h for h in filtered
                if sq in str(h.get("study_name", "")).lower()
                or sq in str(h.get("study_id", "")).lower()
                or sq in str(h.get("dataset", "")).lower()
                or sq in str(h.get("model", "")).lower()
            ]

        filtered = filtered[:limit_val]
        st.caption(f"Showing {len(filtered)} of {len(raw_history)} recorded studies:")

        if not filtered:
            st.info("No studies match the search criteria.")
        else:
            table_data = []
            for h in filtered:
                st_icon = "🟢" if h.get("status") == "completed" else ("⚡" if h.get("status") == "running" else "🔴")
                table_data.append({
                    "Status": f"{st_icon} {h.get('status')}",
                    "Study Name": h.get("study_name", h.get("study_id")),
                    "Submitter": h.get("author", "Unknown"),
                    "Target Node": h.get("destination_node", "wyolo_gpu_queue"),
                    "Model": h.get("model", "N/A"),
                    "Dataset": h.get("dataset", "N/A"),
                    "Started": h.get("start_time", "N/A"),
                    "Study ID": h.get("study_id"),
                })

            st.dataframe(pd.DataFrame(table_data), use_container_width=True, hide_index=True)

            # Details inspector
            st.markdown("##### 🔍 Inspect Study Details")
            study_choices = [f"{h.get('study_name', h.get('study_id'))} ({h.get('study_id')[:8]})" for h in filtered]
            selected_inspect = st.selectbox("Select a study to view its full configuration:", options=study_choices, key="hist_inspect_sel")
            if selected_inspect:
                sel_idx = study_choices.index(selected_inspect)
                target_study = filtered[sel_idx]
                col_d1, col_d2 = st.columns(2)
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

                # Reproducibility Manifest
                with st.expander("📋 Reproducibility Manifest (Docker Run & YAML)", expanded=False):
                    try:
                        repro = api_client.get_study_reproducibility(token, target_study.get("study_id"))
                        st.caption(f"SHA256 Fingerprint: `{repro.get('sha256_fingerprint')}` | Generated: `{repro.get('generated_at')}`")
                        st.markdown("**Direct Reproduction Docker Command:**")
                        st.code(repro.get("docker_run_command"), language="bash")
                        st.markdown("**YAML Configuration Manifest:**")
                        st.code(repro.get("training_yaml"), language="yaml")
                    except Exception as rpe:
                        st.warning(f"Could not generate the reproducibility manifest: {rpe}")


    # --- TAB 2: Optuna Learning Curves ---
    with tab_metrics:
        st.markdown("#### 📈 Trial Progress & Objective Metric (Optuna)")
        st.caption("Track fitness / accuracy / mAP progress across iterations.")

        if not raw_history:
            st.info("No recorded studies available to chart metrics.")
        else:
            study_metric_choices = {
                f"{h.get('study_name', h.get('study_id'))} [{h.get('status')}]": h.get("study_id")
                for h in raw_history
            }
            selected_metric_label = st.selectbox(
                "Select the study to analyze:",
                options=list(study_metric_choices.keys()),
                key="sel_study_metric_tab",
            )
            selected_metric_id = study_metric_choices[selected_metric_label]

            try:
                metrics_points = api_client.get_study_metrics(token, selected_metric_id)
            except Exception as me:
                st.error(f"Failed to retrieve Optuna metrics: {me}")
                metrics_points = []

            if not metrics_points:
                st.info(f"Study `{selected_metric_id}` has not recorded any metric points in Redis yet.")
            else:
                df_metrics = pd.DataFrame(metrics_points)
                best_val = df_metrics["fitness"].max()
                best_trial_row = df_metrics[df_metrics["fitness"] == best_val].iloc[0]

                col_m1, col_m2 = st.columns([1, 3])
                with col_m1:
                    st.metric(label="🏆 Best Value (Fitness)", value=f"{best_val:.4f}")
                    st.write(f"• **Best Trial:** `#{int(best_trial_row['trial'])}`")
                    st.write(f"• **Total Trials:** `{len(df_metrics)}`")
                with col_m2:
                    st.line_chart(df_metrics.set_index("trial")["fitness"])

                with st.expander("📊 View Full Trials & Parameters Table"):
                    st.dataframe(df_metrics, use_container_width=True, hide_index=True)

    # --- TAB 3: Head-to-Head Comparison ---
    with tab_compare:
        st.markdown("#### 🔬 Head-to-Head Study Comparison")
        st.caption("Select 2 to 5 studies to compare parameters, architectures, and performance metrics side by side.")

        if not raw_history or len(raw_history) < 2:
            st.info("At least 2 recorded studies are required to run a comparison.")
        else:
            study_map = {
                f"{h.get('study_name', h.get('study_id'))} [{h.get('model', 'N/A')}] ({h.get('study_id')[:8]})": h.get("study_id")
                for h in raw_history
            }
            default_selection = list(study_map.keys())[:2]
            selected_labels = st.multiselect(
                "Select the studies to compare (2 to 5):",
                options=list(study_map.keys()),
                default=default_selection,
                key="multisel_compare_studies",
            )

            selected_ids = [study_map[lbl] for lbl in selected_labels if lbl in study_map]

            if st.button("🔬 Compare Selected Studies", type="primary", use_container_width=True, disabled=(len(selected_ids) < 2 or len(selected_ids) > 5)):
                try:
                    comp_res = api_client.compare_studies(token, selected_ids)
                    st.session_state["active_comparison_result"] = comp_res
                except Exception as ce:
                    st.error(f"Failed to compare studies: {ce}")

            if "active_comparison_result" in st.session_state:
                res = st.session_state["active_comparison_result"]
                st.success(f"💡 {res.get('comparison_summary')}")
                comp_studies = res.get("studies", [])
                if comp_studies:
                    df_comp = pd.DataFrame(comp_studies)
                    st.dataframe(df_comp, use_container_width=True, hide_index=True)

    # --- TAB 4: Report Exporter ---
    with tab_export:
        st.markdown("#### 📥 Study Report Generator & Download")
        st.caption("Download a technical report in Markdown or CSV format to attach to technical documentation.")

        if not raw_history:
            st.info("No studies available to export.")
        else:
            export_choices = {
                f"{h.get('study_name', h.get('study_id'))} ({h.get('study_id')[:8]})": h
                for h in raw_history
            }
            sel_export_label = st.selectbox("Select the study to export:", options=list(export_choices.keys()), key="sel_export_target")
            selected_study = export_choices[sel_export_label]
            sid = selected_study.get("study_id")

            # Try to fetch metrics
            try:
                trials_data = api_client.get_study_metrics(token, sid)
            except Exception:
                trials_data = []

            # Generate Markdown report
            md_lines = [
                f"# NeuralForge Study Report: {selected_study.get('study_name', sid)}",
                "",
                f"- **Study ID:** `{sid}`",
                f"- **Author:** {selected_study.get('author', 'Unknown')}",
                f"- **Assigned Node:** {selected_study.get('destination_node', 'N/A')}",
                f"- **Model:** `{selected_study.get('model', 'N/A')}`",
                f"- **Dataset:** `{selected_study.get('dataset', 'N/A')}`",
                f"- **Status:** {selected_study.get('status')}",
                f"- **Start Date:** {selected_study.get('start_time', 'N/A')}",
                "",
                "## Optimization Results (Optuna)",
            ]
            if trials_data:
                df_t = pd.DataFrame(trials_data)
                best_t = df_t.sort_values(by="fitness", ascending=False).iloc[0]
                md_lines.append(f"- **Best Fitness:** `{best_t['fitness']:.4f}` (Trial #{int(best_t['trial'])})")
                md_lines.append(f"- **Total Trials Executed:** {len(trials_data)}")
                md_lines.append("")
                md_lines.append("### Trials Table")
                md_lines.append(df_t.to_markdown(index=False))
            else:
                md_lines.append("No detailed trial metrics were recorded.")

            markdown_report = "\n".join(md_lines)

            col_exp1, col_exp2 = st.columns(2)
            with col_exp1:
                st.download_button(
                    label="📄 Download Markdown Report (.md)",
                    data=markdown_report,
                    file_name=f"report_{selected_study.get('study_name', sid)[:20]}.md",
                    mime="text/markdown",
                    use_container_width=True,
                )
            with col_exp2:
                # CSV export
                if trials_data:
                    csv_data = pd.DataFrame(trials_data).to_csv(index=False)
                else:
                    csv_data = pd.DataFrame([selected_study]).to_csv(index=False)

                st.download_button(
                    label="📊 Download CSV Data (.csv)",
                    data=csv_data,
                    file_name=f"data_{selected_study.get('study_name', sid)[:20]}.csv",
                    mime="text/csv",
                    use_container_width=True,
                )

            st.markdown("##### Report Preview:")
            st.code(markdown_report, language="markdown")
