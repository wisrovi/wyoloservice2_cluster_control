"""GPU Benchmarks and Leaderboard view for NeuralForge Cluster Control."""

import pandas as pd
import streamlit as st
from frontend.api_client import ClusterApiClient


def render_benchmarks(api_client: ClusterApiClient, token: str):
    """Renders GPU performance comparison, throughput metrics, and leaderboard."""
    st.title("🏆 Cluster GPU Performance & Leaderboard")
    st.caption("Training speed comparison (throughput in img/s and time per epoch) across all GPUs in the ecosystem.")

    try:
        data = api_client.get_gpu_benchmarks(token)
        benchmarks = data.get("benchmarks", [])
        updated_at = data.get("updated_at", "N/A")
    except Exception as e:
        st.error(f"Failed to load GPU benchmarks: {e}")
        benchmarks = []
        updated_at = "N/A"

    if not benchmarks:
        st.info("No benchmark data is available at the moment.")
        return

    df = pd.DataFrame(benchmarks)

    # Top KPI cards
    col_kpi1, col_kpi2, col_kpi3 = st.columns(3)
    fastest_gpu = df.sort_values(by="avg_throughput_img_s", ascending=False).iloc[0]
    total_benchmark_studies = df["completed_studies_count"].sum()

    with col_kpi1:
        st.metric(
            label="⚡ Fastest GPU",
            value=fastest_gpu["gpu_model"].replace("NVIDIA GeForce ", ""),
            delta=f"{fastest_gpu['avg_throughput_img_s']} img/s",
        )
    with col_kpi2:
        st.metric(
            label="⏱️ Best Time (100 Epochs)",
            value=f"~{fastest_gpu['estimated_100_epochs_min']} min",
            delta="High efficiency",
        )
    with col_kpi3:
        st.metric(
            label="📊 Studies Analyzed",
            value=f"{total_benchmark_studies} runs",
            delta=f"Updated: {updated_at.split(' ')[1] if ' ' in updated_at else updated_at}",
        )

    st.markdown("---")

    col_chart, col_details = st.columns([1.6, 1.4], gap="large")

    with col_chart:
        st.subheader("📊 Throughput Comparison (Images per Second)")
        st.caption("Higher is better: the GPU processes batches faster during YOLO training.")
        chart_data = df.set_index("gpu_model")["avg_throughput_img_s"]
        st.bar_chart(chart_data)

    with col_details:
        st.subheader("⏱️ Estimated Time for 100 Epochs (Minutes)")
        st.caption("Lower is better: a full training cycle completes sooner.")
        time_chart_data = df.set_index("gpu_model")["estimated_100_epochs_min"]
        st.bar_chart(time_chart_data)

    st.markdown("---")
    st.subheader("📋 Full Comparison of GPU Models and Assigned Nodes")

    display_table = []
    for idx, row in df.iterrows():
        display_table.append({
            "Rank": f"#{idx + 1}",
            "GPU Model": row["gpu_model"],
            "Avg. Throughput": f"{row['avg_throughput_img_s']} img/s",
            "Avg. Time / Epoch": f"{row['avg_epoch_seconds']} s",
            "Est. 100 Epochs": f"{row['estimated_100_epochs_min']} min",
            "Recorded Studies": row["completed_studies_count"],
            "Nodes with this Model": ", ".join(row.get("sample_workers", [])),
        })

    st.dataframe(pd.DataFrame(display_table), use_container_width=True, hide_index=True)
