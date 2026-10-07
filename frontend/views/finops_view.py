"""FinOps, Energy Efficiency (Green AI) and Cost Governance view for NeuralForge Cluster Admin."""

import pandas as pd
import streamlit as st
from frontend.api_client import ClusterApiClient


def render_finops(api_client: ClusterApiClient, token: str):
    """Renders the FinOps, Energy Monitoring, and Infrastructure Cost Governance dashboard."""
    st.markdown("## 🌿 Cluster FinOps, Energy & Costs")
    st.caption("Real-time control of electricity operating costs, environmental sustainability (Green AI) and budget forecasting.")

    tab_overview, tab_rates, tab_sustainability = st.tabs([
        "💶 Cost & FinOps Overview",
        "⚡ Electricity Rate & Budget",
        "🌱 Sustainability Certificate (Green AI)",
    ])

    try:
        finops = api_client.get_finops_report(token)
    except Exception as e:
        st.error(f"Error loading FinOps report: {e}")
        finops = {}

    total_kwh = finops.get("total_kwh", 0.0)
    rate_eur = finops.get("rate_eur_per_kwh", 0.18)
    total_cost = finops.get("total_cost_eur", 0.0)
    currency = finops.get("currency", "EUR")
    projected = finops.get("projected_monthly_cost_eur", 0.0)

    # --- TAB 1: Cost Overview ---
    with tab_overview:
        st.markdown("#### 📊 Infrastructure Cost Balance")
        col_c1, col_c2, col_c3, col_c4 = st.columns(4)

        with col_c1:
            st.metric("💶 Accumulated Electricity Cost", f"{total_cost:.3f} €")
        with col_c2:
            st.metric("⚡ Energy Consumed", f"{total_kwh:.3f} kWh")
        with col_c3:
            st.metric("📈 Projected Monthly Cost", f"{projected:.2f} €/month")
        with col_c4:
            st.metric("💡 Applied Base Rate", f"{rate_eur:.3f} €/kWh")

        st.markdown("---")
        st.subheader("🖥️ Consumption & Cost Breakdown by GPU Model")
        gpu_costs = finops.get("gpu_cost_breakdown", [])
        if gpu_costs:
            df_costs = pd.DataFrame(gpu_costs)
            st.dataframe(df_costs, use_container_width=True, hide_index=True)

    # --- TAB 2: Electricity Rate & Budget ---
    with tab_rates:
        st.markdown("#### ⚡ Electricity Billing Parameters")
        st.caption("Set the kWh price agreed with your electricity provider to recalculate costs in real time.")

        with st.container(border=True):
            col_r1, col_r2 = st.columns([2, 1])
            with col_r1:
                new_rate = st.number_input(
                    "Electricity Rate (€ / kWh):",
                    min_value=0.01,
                    max_value=2.00,
                    value=float(rate_eur),
                    step=0.01,
                    format="%.3f",
                    key="finops_rate_input",
                )
                st.caption("Reference: average Spanish regulated market price (PVPC) ~0.150 to 0.220 €/kWh.")
            with col_r2:
                st.write(" ")
                st.write(" ")
                if st.button("💾 Update Rate", type="primary", use_container_width=True):
                    try:
                        res = api_client.update_electricity_rate(token, new_rate)
                        st.success(res.get("message", "Rate updated."))
                        st.rerun()
                    except Exception as re:
                        st.error(f"Error updating rate: {re}")

    # --- TAB 3: Sustainability Certificate ---
    with tab_sustainability:
        st.markdown("#### 🌱 Cluster Carbon Footprint (Green AI)")
        st.caption("Emissions audit based on the Spanish electricity mix factor (0.150 kg CO₂e / kWh).")

        try:
            green = api_client.get_green_ai_metrics(token)
            co2_kg = green.get("estimated_co2_kg", 0.0)
            trees = green.get("trees_offset_equivalent", 0.0)
            eff = green.get("avg_efficiency_img_per_watt", 0.45)

            col_s1, col_s2, col_s3 = st.columns(3)
            with col_s1:
                st.metric("🌱 Total CO₂e Emissions", f"{co2_kg:.3f} kg")
            with col_s2:
                st.metric("🌳 Tree Offset Equivalent", f"{trees:.2f} trees/year")
            with col_s3:
                st.metric("🚀 Energy Efficiency", f"{eff:.2f} img/Watt")

            st.info("💡 **Efficiency Tip:** RTX 4060 and RTX 3060 GPUs offer the best `images per watt` ratio, ideal for extensive Optuna sweeps.")
        except Exception as ge:
            st.caption(f"Could not load environmental data: {ge}")
