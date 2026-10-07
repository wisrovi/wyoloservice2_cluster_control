"""FinOps, Energy Efficiency (Green AI) and Cost Governance view for NeuralForge Cluster Admin."""

import pandas as pd
import streamlit as st
from frontend.api_client import ClusterApiClient


def render_finops(api_client: ClusterApiClient, token: str):
    """Renders the FinOps, Energy Monitoring, and Infrastructure Cost Governance dashboard."""
    st.markdown("## 🌿 FinOps, Energía y Costes del Clúster")
    st.caption("Control de gasto operativo eléctrico en tiempo real, sostenibilidad ambiental (Green AI) y proyección presupuestaria.")

    tab_overview, tab_rates, tab_sustainability = st.tabs([
        "💶 Resumen de Costes & FinOps",
        "⚡ Tarifa Eléctrica & Presupuesto",
        "🌱 Certificado de Sostenibilidad (Green AI)",
    ])

    try:
        finops = api_client.get_finops_report(token)
    except Exception as e:
        st.error(f"Error cargando informe FinOps: {e}")
        finops = {}

    total_kwh = finops.get("total_kwh", 0.0)
    rate_eur = finops.get("rate_eur_per_kwh", 0.18)
    total_cost = finops.get("total_cost_eur", 0.0)
    currency = finops.get("currency", "EUR")
    projected = finops.get("projected_monthly_cost_eur", 0.0)

    # --- TAB 1: Cost Overview ---
    with tab_overview:
        st.markdown("#### 📊 Balance Económico de Infraestructura")
        col_c1, col_c2, col_c3, col_c4 = st.columns(4)

        with col_c1:
            st.metric("💶 Gasto Eléctrico Acumulado", f"{total_cost:.3f} €")
        with col_c2:
            st.metric("⚡ Energía Consumida", f"{total_kwh:.3f} kWh")
        with col_c3:
            st.metric("📈 Coste Mensual Proyectado", f"{projected:.2f} €/mes")
        with col_c4:
            st.metric("💡 Tarifa Base Aplicada", f"{rate_eur:.3f} €/kWh")

        st.markdown("---")
        st.subheader("🖥️ Desglose de Consumo y Costes por Modelo de GPU")
        gpu_costs = finops.get("gpu_cost_breakdown", [])
        if gpu_costs:
            df_costs = pd.DataFrame(gpu_costs)
            st.dataframe(df_costs, use_container_width=True, hide_index=True)

    # --- TAB 2: Electricity Rate & Budget ---
    with tab_rates:
        st.markdown("#### ⚡ Parámetros de Facturación Eléctrica")
        st.caption("Ajusta el precio del kWh acordado con tu comercializadora eléctrica para recalcular costes en tiempo real.")

        with st.container(border=True):
            col_r1, col_r2 = st.columns([2, 1])
            with col_r1:
                new_rate = st.number_input(
                    "Tarifa Eléctrica (€ / kWh):",
                    min_value=0.01,
                    max_value=2.00,
                    value=float(rate_eur),
                    step=0.01,
                    format="%.3f",
                    key="finops_rate_input",
                )
                st.caption("Referencia: Precio medio mercado regulado (PVPC) España ~0.150 a 0.220 €/kWh.")
            with col_r2:
                st.write(" ")
                st.write(" ")
                if st.button("💾 Actualizar Tarifa", type="primary", use_container_width=True):
                    try:
                        res = api_client.update_electricity_rate(token, new_rate)
                        st.success(res.get("message", "Tarifa actualizada."))
                        st.rerun()
                    except Exception as re:
                        st.error(f"Error actualizando tarifa: {re}")

    # --- TAB 3: Sustainability Certificate ---
    with tab_sustainability:
        st.markdown("#### 🌱 Huella Ecológica del Clúster (Green AI)")
        st.caption("Auditoría de emisiones basada en el factor de mix eléctrico español (0.150 kg CO₂e / kWh).")

        try:
            green = api_client.get_green_ai_metrics(token)
            co2_kg = green.get("estimated_co2_kg", 0.0)
            trees = green.get("trees_offset_equivalent", 0.0)
            eff = green.get("avg_efficiency_img_per_watt", 0.45)

            col_s1, col_s2, col_s3 = st.columns(3)
            with col_s1:
                st.metric("🌱 Emisiones Totales CO₂e", f"{co2_kg:.3f} kg")
            with col_s2:
                st.metric("🌳 Compensación Arbórea", f"{trees:.2f} árboles/año")
            with col_s3:
                st.metric("🚀 Eficiencia Energética", f"{eff:.2f} img/Vatio")

            st.info("💡 **Consejo de Eficiencia:** Las GPUs RTX 4060 y RTX 3060 ofrecen la mejor relación `imágenes por vatio`, ideales para barridos extensos de Optuna.")
        except Exception as ge:
            st.caption(f"No se pudieron cargar datos ambientales: {ge}")
