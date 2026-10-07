"""Study History, Optuna Analytics, and Report Exporter view for NeuralForge Cluster Control."""

import json
import pandas as pd
import streamlit as st
from frontend.api_client import ClusterApiClient


def render_history(api_client: ClusterApiClient, token: str):
    """Renders historical study browser, Optuna trial curves, and 1-click report export."""
    st.title("📈 Historial, Métricas y Reportes de Estudios")
    st.caption("Búsqueda avanzada, curvas de aprendizaje de Optuna y exportación de informes de experimentos.")

    current_user = st.session_state.get("username", "wisrovi")

    tab_history, tab_metrics, tab_export = st.tabs([
        "📜 Historial y Búsqueda",
        "📈 Curvas de Aprendizaje (Optuna)",
        "📥 Exportador de Reportes",
    ])

    # Fetch history
    try:
        raw_history = api_client.list_task_history(token, limit=100)
    except Exception as he:
        st.error(f"Error cargando historial de estudios: {he}")
        raw_history = []

    # --- TAB 1: History Search and Filters ---
    with tab_history:
        st.markdown("#### 🔍 Filtros de Búsqueda")

        col_s1, col_s2 = st.columns([3, 1])
        with col_s1:
            search_query = st.text_input(
                "Buscador",
                placeholder="Busca por Nombre de Estudio, Study ID, Dataset o Modelo...",
                key="hist_search_input",
                label_visibility="collapsed",
            )
        with col_s2:
            only_mine = st.checkbox("👤 Solo mis estudios", value=False, key="hist_cb_only_mine")

        all_authors = sorted(list({h.get("author", "Desconocido") for h in raw_history if h.get("author")}))
        author_options = ["Todos"] + all_authors

        all_nodes = sorted(list({h.get("destination_node", "N/A") for h in raw_history if h.get("destination_node")}))
        node_options = ["Todos"] + all_nodes

        col_f1, col_f2, col_f3, col_f4 = st.columns(4)
        with col_f1:
            sel_author = st.selectbox("Remitente / Autor", options=author_options, key="hist_filter_author")
        with col_f2:
            sel_node = st.selectbox("Nodo Asignado", options=node_options, key="hist_filter_node")
        with col_f3:
            sel_status = st.selectbox("Estado", options=["Todos", "completed", "running", "failed"], key="hist_filter_status")
        with col_f4:
            limit_val = st.selectbox("Límite de Registros", options=[20, 50, 100], index=1, key="hist_filter_limit")

        # Filtering logic
        filtered = raw_history
        if only_mine:
            filtered = [h for h in filtered if current_user.lower() in str(h.get("author", "")).lower()]
        elif sel_author != "Todos":
            filtered = [h for h in filtered if sel_author.lower() in str(h.get("author", "")).lower()]

        if sel_node != "Todos":
            filtered = [h for h in filtered if sel_node.lower() in str(h.get("destination_node", "")).lower()]

        if sel_status != "Todos":
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
        st.caption(f"Mostrando {len(filtered)} de {len(raw_history)} estudios registrados:")

        if not filtered:
            st.info("No se encontraron estudios que coincidan con los criterios de búsqueda.")
        else:
            table_data = []
            for h in filtered:
                st_icon = "🟢" if h.get("status") == "completed" else ("⚡" if h.get("status") == "running" else "🔴")
                table_data.append({
                    "Estado": f"{st_icon} {h.get('status')}",
                    "Nombre del Estudio": h.get("study_name", h.get("study_id")),
                    "Remitente": h.get("author", "Desconocido"),
                    "Nodo Destino": h.get("destination_node", "wyolo_gpu_queue"),
                    "Modelo": h.get("model", "N/A"),
                    "Dataset": h.get("dataset", "N/A"),
                    "Iniciado": h.get("start_time", "N/A"),
                    "Study ID": h.get("study_id"),
                })

            st.dataframe(pd.DataFrame(table_data), use_container_width=True, hide_index=True)

            # Details inspector
            st.markdown("##### 🔍 Inspeccionar Detalle del Estudio")
            study_choices = [f"{h.get('study_name', h.get('study_id'))} ({h.get('study_id')[:8]})" for h in filtered]
            selected_inspect = st.selectbox("Selecciona un estudio para ver su configuración completa:", options=study_choices, key="hist_inspect_sel")
            if selected_inspect:
                sel_idx = study_choices.index(selected_inspect)
                target_study = filtered[sel_idx]
                col_d1, col_d2 = st.columns(2)
                with col_d1:
                    st.write(f"• **Study ID Completo:** `{target_study.get('study_id')}`")
                    st.write(f"• **Autor / Remitente:** `{target_study.get('author')}`")
                    st.write(f"• **Nodo / Host:** `{target_study.get('destination_node')}`")
                    st.write(f"• **Dataset:** `{target_study.get('dataset')}`")
                with col_d2:
                    st.write(f"• **Modelo:** `{target_study.get('model')}`")
                    st.write(f"• **Estado:** `{target_study.get('status')}`")
                    st.write(f"• **Fecha de Inicio:** `{target_study.get('start_time')}`")
                    if target_study.get("error"):
                        st.error(f"Error registrado: {target_study.get('error')}")

    # --- TAB 2: Optuna Learning Curves ---
    with tab_metrics:
        st.markdown("#### 📈 Evolución de Trials y Métrica Objetivo (Optuna)")
        st.caption("Visualiza el progreso de fitness / accuracy / mAP a lo largo de las iteraciones.")

        if not raw_history:
            st.info("No hay estudios registrados para graficar métricas.")
        else:
            study_metric_choices = {
                f"{h.get('study_name', h.get('study_id'))} [{h.get('status')}]": h.get("study_id")
                for h in raw_history
            }
            selected_metric_label = st.selectbox(
                "Selecciona el estudio a analizar:",
                options=list(study_metric_choices.keys()),
                key="sel_study_metric_tab",
            )
            selected_metric_id = study_metric_choices[selected_metric_label]

            try:
                metrics_points = api_client.get_study_metrics(token, selected_metric_id)
            except Exception as me:
                st.error(f"Error obteniendo métricas de Optuna: {me}")
                metrics_points = []

            if not metrics_points:
                st.info(f"El estudio `{selected_metric_id}` aún no ha registrado puntos de métricas en Redis.")
            else:
                df_metrics = pd.DataFrame(metrics_points)
                best_val = df_metrics["fitness"].max()
                best_trial_row = df_metrics[df_metrics["fitness"] == best_val].iloc[0]

                col_m1, col_m2 = st.columns([1, 3])
                with col_m1:
                    st.metric(label="🏆 Mejor Valor (Fitness)", value=f"{best_val:.4f}")
                    st.write(f"• **Mejor Trial:** `#{int(best_trial_row['trial'])}`")
                    st.write(f"• **Total Trials:** `{len(df_metrics)}`")
                with col_m2:
                    st.line_chart(df_metrics.set_index("trial")["fitness"])

                with st.expander("📊 Ver Tabla Completa de Trials y Parámetros"):
                    st.dataframe(df_metrics, use_container_width=True, hide_index=True)

    # --- TAB 3: Report Exporter ---
    with tab_export:
        st.markdown("#### 📥 Generador y Descarga de Reportes de Estudio")
        st.caption("Descarga un informe técnico en formato Markdown o CSV para adjuntar a documentación técnica.")

        if not raw_history:
            st.info("No hay estudios para exportar.")
        else:
            export_choices = {
                f"{h.get('study_name', h.get('study_id'))} ({h.get('study_id')[:8]})": h
                for h in raw_history
            }
            sel_export_label = st.selectbox("Selecciona el estudio a exportar:", options=list(export_choices.keys()), key="sel_export_target")
            selected_study = export_choices[sel_export_label]
            sid = selected_study.get("study_id")

            # Try to fetch metrics
            try:
                trials_data = api_client.get_study_metrics(token, sid)
            except Exception:
                trials_data = []

            # Generate Markdown report
            md_lines = [
                f"# Informe de Estudio NeuralForge: {selected_study.get('study_name', sid)}",
                "",
                f"- **Study ID:** `{sid}`",
                f"- **Autor:** {selected_study.get('author', 'Desconocido')}",
                f"- **Nodo Asignado:** {selected_study.get('destination_node', 'N/A')}",
                f"- **Modelo:** `{selected_study.get('model', 'N/A')}`",
                f"- **Dataset:** `{selected_study.get('dataset', 'N/A')}`",
                f"- **Estado:** {selected_study.get('status')}",
                f"- **Fecha de Inicio:** {selected_study.get('start_time', 'N/A')}",
                "",
                "## Resultados de Optimización (Optuna)",
            ]
            if trials_data:
                df_t = pd.DataFrame(trials_data)
                best_t = df_t.sort_values(by="fitness", ascending=False).iloc[0]
                md_lines.append(f"- **Mejor Fitness:** `{best_t['fitness']:.4f}` (Trial #{int(best_t['trial'])})")
                md_lines.append(f"- **Total de Trials Ejecutados:** {len(trials_data)}")
                md_lines.append("")
                md_lines.append("### Tabla de Trials")
                md_lines.append(df_t.to_markdown(index=False))
            else:
                md_lines.append("No se registraron trials de métricas detallados.")

            markdown_report = "\n".join(md_lines)

            col_exp1, col_exp2 = st.columns(2)
            with col_exp1:
                st.download_button(
                    label="📄 Descargar Reporte en Markdown (.md)",
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
                    label="📊 Descargar Datos en CSV (.csv)",
                    data=csv_data,
                    file_name=f"data_{selected_study.get('study_name', sid)[:20]}.csv",
                    mime="text/csv",
                    use_container_width=True,
                )

            st.markdown("##### Previsualización del Informe:")
            st.code(markdown_report, language="markdown")
