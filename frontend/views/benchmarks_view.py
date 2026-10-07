"""GPU Benchmarks and Leaderboard view for NeuralForge Cluster Control."""

import pandas as pd
import streamlit as st
from frontend.api_client import ClusterApiClient


def render_benchmarks(api_client: ClusterApiClient, token: str):
    """Renders GPU performance comparison, throughput metrics, and leaderboard."""
    st.title("🏆 Rendimiento de GPUs y Leaderboard del Clúster")
    st.caption("Comparativa de velocidad de entrenamiento (throughput img/s y tiempo por época) entre las GPUs del ecosistema.")

    try:
        data = api_client.get_gpu_benchmarks(token)
        benchmarks = data.get("benchmarks", [])
        updated_at = data.get("updated_at", "N/A")
    except Exception as e:
        st.error(f"Error cargando benchmarks de GPU: {e}")
        benchmarks = []
        updated_at = "N/A"

    if not benchmarks:
        st.info("No hay datos de benchmark disponibles en este momento.")
        return

    df = pd.DataFrame(benchmarks)

    # Top KPI cards
    col_kpi1, col_kpi2, col_kpi3 = st.columns(3)
    fastest_gpu = df.sort_values(by="avg_throughput_img_s", ascending=False).iloc[0]
    total_benchmark_studies = df["completed_studies_count"].sum()

    with col_kpi1:
        st.metric(
            label="⚡ GPU Más Rápida",
            value=fastest_gpu["gpu_model"].replace("NVIDIA GeForce ", ""),
            delta=f"{fastest_gpu['avg_throughput_img_s']} img/s",
        )
    with col_kpi2:
        st.metric(
            label="⏱️ Tiempo Mínimo (100 Épocas)",
            value=f"~{fastest_gpu['estimated_100_epochs_min']} min",
            delta="Alta eficiencia",
        )
    with col_kpi3:
        st.metric(
            label="📊 Estudios Analizados",
            value=f"{total_benchmark_studies} runs",
            delta=f"Actualizado: {updated_at.split(' ')[1] if ' ' in updated_at else updated_at}",
        )

    st.markdown("---")

    col_chart, col_details = st.columns([1.6, 1.4], gap="large")

    with col_chart:
        st.subheader("📊 Comparativa de Throughput (Imágenes por Segundo)")
        st.caption("A mayor valor, más rápido procesa batches durante el entrenamiento YOLO.")
        chart_data = df.set_index("gpu_model")["avg_throughput_img_s"]
        st.bar_chart(chart_data)

    with col_details:
        st.subheader("⏱️ Tiempo Estimado para 100 Épocas (Minutos)")
        st.caption("A menor tiempo, más rápido concluye un ciclo de entrenamiento completo.")
        time_chart_data = df.set_index("gpu_model")["estimated_100_epochs_min"]
        st.bar_chart(time_chart_data)

    st.markdown("---")
    st.subheader("📋 Tabla Comparativa Completa de Modelos y Nodos Asignados")

    display_table = []
    for idx, row in df.iterrows():
        display_table.append({
            "Rango": f"#{idx + 1}",
            "Modelo GPU": row["gpu_model"],
            "Throughput Promedio": f"{row['avg_throughput_img_s']} img/s",
            "Tiempo Medio / Época": f"{row['avg_epoch_seconds']} seg",
            "100 Épocas Est.": f"{row['estimated_100_epochs_min']} min",
            "Estudios Registrados": row["completed_studies_count"],
            "Nodos con este Modelo": ", ".join(row.get("sample_workers", [])),
        })

    st.dataframe(pd.DataFrame(display_table), use_container_width=True, hide_index=True)
