"""Tasks and trials monitoring view for Streamlit application."""

import streamlit as st
from frontend.api_client import ClusterApiClient


def render_tasks(api_client: ClusterApiClient, token: str):
    """Renders active training trials and historical studies."""
    st.title("🚀 Monitoreo de Entrenamientos y Tareas")
    st.caption("Visualiza los trials que se están ejecutando en los invokers en tiempo real.")

    tab_active, tab_history = st.tabs(["⚡ Tareas Activas en Ejecución", "📜 Historial de Estudios"])

    with tab_active:
        try:
            active_tasks = api_client.list_active_tasks(token)
        except Exception as e:
            st.error(f"Error cargando tareas activas: {e}")
            active_tasks = []

        if not active_tasks:
            st.info("No hay ningún entrenamiento ejecutándose en este momento en el cluster.")
        else:
            for task in active_tasks:
                study_id = task.get("study_id")
                model = task.get("model", "N/A")
                invoker = task.get("invoker", "N/A")
                start_time = task.get("start_time", "N/A")
                progress = task.get("progress", {})
                completed_trials = progress.get("completed_trials", 0)
                total_trials = progress.get("total_trials", 1)

                with st.container(border=True):
                    col_t1, col_t2 = st.columns([3, 1])
                    with col_t1:
                        st.markdown(f"### 🎯 Estudio: `{study_id}`")
                        st.write(f"• **Modelo:** `{model}` | **Tipo:** `{task.get('task_type', 'N/A')}`")
                        st.write(f"• **Invoker Asignado:** `{invoker}`")
                        st.write(f"• **Iniciado:** `{start_time}`")

                        if total_trials > 0:
                            pct = min(completed_trials / total_trials, 1.0)
                            st.progress(pct, text=f"Progreso de Trials: {completed_trials}/{total_trials} ({int(pct*100)}%)")
                    with col_t2:
                        st.write(" ")
                        st.write(" ")
                        if st.button("🛑 Cancelar Estudio", key=f"btn_cancel_{study_id}", type="secondary"):
                            try:
                                api_client.cancel_task(token, study_id)
                                st.warning(f"Señal de cancelación enviada para {study_id}.")
                                st.rerun()
                            except Exception as ce:
                                st.error(f"Error cancelando: {ce}")

    with tab_history:
        st.caption("Últimos estudios registrados en Redis:")
        try:
            history = api_client.list_task_history(token, limit=30)
            if not history:
                st.info("No hay historial disponible.")
            else:
                table_hist = []
                for h in history:
                    table_hist.append({
                        "Study ID": h.get("study_id"),
                        "Modelo": h.get("model"),
                        "Estado": h.get("status"),
                        "Invoker": h.get("invoker"),
                        "Iniciado": h.get("start_time", "N/A"),
                    })
                st.dataframe(table_hist, use_container_width=True, hide_index=True)
        except Exception as he:
            st.error(f"Error cargando historial: {he}")
