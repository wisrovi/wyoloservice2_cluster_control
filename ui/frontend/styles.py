"""Enterprise 5-Star styling and UI component helpers for NeuralForge Cluster Admin."""

import streamlit as st
from typing import Any, Dict, List, Optional


def apply_custom_theme():
    """Injects high-end Enterprise Dark Glassmorphism CSS into the Streamlit app."""
    custom_css = """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&display=swap');

    :root {
      --bg-main: #0B0F19;
      --bg-card: rgba(18, 24, 38, 0.75);
      --bg-card-hover: rgba(24, 33, 52, 0.85);
      --border-subtle: rgba(255, 255, 255, 0.08);
      --border-glow: rgba(59, 130, 246, 0.35);
      --primary-gradient: linear-gradient(135deg, #3B82F6 0%, #1D4ED8 100%);
      --accent-cyan: #06B6D4;
      --accent-emerald: #10B981;
      --accent-violet: #8B5CF6;
      --accent-amber: #F59E0B;
      --accent-rose: #F43F5E;
      --text-main: #F8FAFC;
      --text-muted: #94A3B8;
      --font-main: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
      --font-mono: 'JetBrains Mono', monospace;
    }

    /* Global Background & Typography */
    html, body, [data-testid="stAppViewContainer"], .main {
      font-family: var(--font-main) !important;
      background-color: var(--bg-main) !important;
      background-image: 
        radial-gradient(at 0% 0%, rgba(59, 130, 246, 0.08) 0px, transparent 50%),
        radial-gradient(at 100% 0%, rgba(139, 92, 246, 0.07) 0px, transparent 50%),
        radial-gradient(at 50% 100%, rgba(16, 185, 129, 0.05) 0px, transparent 50%) !important;
      color: var(--text-main) !important;
    }

    /* Sidebar Styling */
    [data-testid="stSidebar"] {
      background-color: rgba(11, 15, 25, 0.95) !important;
      border-right: 1px solid var(--border-subtle) !important;
      backdrop-filter: blur(20px) !important;
    }

    [data-testid="stSidebar"] hr {
      margin: 1.2rem 0 !important;
      border-color: var(--border-subtle) !important;
    }

    /* Radio Navigation in Sidebar */
    [data-testid="stSidebar"] [data-testid="stRadio"] > div {
      gap: 4px !important;
    }

    [data-testid="stSidebar"] [data-testid="stRadio"] label {
      background: transparent !important;
      border-radius: 8px !important;
      padding: 8px 12px !important;
      color: #94A3B8 !important;
      font-size: 0.92rem !important;
      font-weight: 500 !important;
      transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
      border: 1px solid transparent !important;
    }

    [data-testid="stSidebar"] [data-testid="stRadio"] label:hover {
      background: rgba(255, 255, 255, 0.05) !important;
      color: #F8FAFC !important;
      transform: translateX(3px) !important;
    }

    [data-testid="stSidebar"] [data-testid="stRadio"] label[data-checked="true"],
    [data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) {
      background: linear-gradient(90deg, rgba(59, 130, 246, 0.15) 0%, rgba(59, 130, 246, 0.05) 100%) !important;
      border-left: 3px solid #3B82F6 !important;
      border-top: 1px solid rgba(59, 130, 246, 0.2) !important;
      border-right: 1px solid rgba(59, 130, 246, 0.2) !important;
      border-bottom: 1px solid rgba(59, 130, 246, 0.2) !important;
      color: #60A5FA !important;
      font-weight: 600 !important;
    }

    /* Containers & Cards */
    [data-testid="stVerticalBlockBorderWrapper"] {
      background: var(--bg-card) !important;
      border: 1px solid var(--border-subtle) !important;
      border-radius: 12px !important;
      backdrop-filter: blur(16px) !important;
      box-shadow: 0 4px 20px -2px rgba(0, 0, 0, 0.5) !important;
      transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }

    [data-testid="stVerticalBlockBorderWrapper"]:hover {
      border-color: rgba(255, 255, 255, 0.14) !important;
      box-shadow: 0 8px 30px -4px rgba(0, 0, 0, 0.7) !important;
    }

    /* Metric Cards */
    [data-testid="stMetric"] {
      background: rgba(18, 24, 38, 0.8) !important;
      border: 1px solid var(--border-subtle) !important;
      border-radius: 12px !important;
      padding: 14px 18px !important;
      box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3) !important;
      transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
      position: relative !important;
      overflow: hidden !important;
    }

    [data-testid="stMetric"]::before {
      content: "" !important;
      position: absolute !important;
      top: 0 !important;
      left: 0 !important;
      right: 0 !important;
      height: 2px !important;
      background: linear-gradient(90deg, #3B82F6, #10B981) !important;
      opacity: 0.8 !important;
    }

    [data-testid="stMetric"]:hover {
      transform: translateY(-3px) !important;
      border-color: var(--border-glow) !important;
      box-shadow: 0 8px 24px -2px rgba(59, 130, 246, 0.25) !important;
    }

    [data-testid="stMetricLabel"] {
      font-size: 0.85rem !important;
      font-weight: 600 !important;
      text-transform: uppercase !important;
      letter-spacing: 0.05em !important;
      color: var(--text-muted) !important;
    }

    [data-testid="stMetricValue"] {
      font-family: var(--font-mono) !important;
      font-size: 1.85rem !important;
      font-weight: 700 !important;
      color: #FFFFFF !important;
      text-shadow: 0 0 12px rgba(255, 255, 255, 0.15) !important;
    }

    [data-testid="stMetricDelta"] {
      font-size: 0.8rem !important;
      font-weight: 600 !important;
    }

    /* Modern Segmented Tabs */
    .stTabs [data-baseweb="tab-list"] {
      background: rgba(15, 23, 42, 0.6) !important;
      border-radius: 10px !important;
      padding: 4px !important;
      border: 1px solid var(--border-subtle) !important;
      gap: 4px !important;
    }

    .stTabs [data-baseweb="tab"] {
      background: transparent !important;
      border-radius: 8px !important;
      color: var(--text-muted) !important;
      font-weight: 500 !important;
      padding: 8px 16px !important;
      border: none !important;
      transition: all 0.2s ease !important;
    }

    .stTabs [data-baseweb="tab"]:hover {
      color: #FFFFFF !important;
      background: rgba(255, 255, 255, 0.04) !important;
    }

    .stTabs [aria-selected="true"] {
      background: #1E293B !important;
      color: #60A5FA !important;
      font-weight: 600 !important;
      border: 1px solid rgba(59, 130, 246, 0.3) !important;
      box-shadow: 0 2px 10px rgba(0, 0, 0, 0.3) !important;
    }

    /* Modern Buttons */
    .stButton > button[kind="primary"] {
      background: var(--primary-gradient) !important;
      color: #FFFFFF !important;
      border: none !important;
      border-radius: 8px !important;
      font-weight: 600 !important;
      letter-spacing: 0.02em !important;
      padding: 0.55rem 1.25rem !important;
      box-shadow: 0 4px 14px 0 rgba(37, 99, 235, 0.39) !important;
      transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }

    .stButton > button[kind="primary"]:hover {
      box-shadow: 0 6px 20px 0 rgba(37, 99, 235, 0.55) !important;
      transform: translateY(-1px) !important;
      filter: brightness(1.08) !important;
    }

    .stButton > button[kind="secondary"] {
      background: rgba(255, 255, 255, 0.04) !important;
      color: #E2E8F0 !important;
      border: 1px solid rgba(255, 255, 255, 0.12) !important;
      border-radius: 8px !important;
      font-weight: 500 !important;
      transition: all 0.2s ease !important;
    }

    .stButton > button[kind="secondary"]:hover {
      background: rgba(255, 255, 255, 0.08) !important;
      border-color: rgba(255, 255, 255, 0.25) !important;
      color: #FFFFFF !important;
      transform: translateY(-1px) !important;
    }

    /* Expanders */
    [data-testid="stExpander"] {
      background: rgba(18, 24, 38, 0.6) !important;
      border: 1px solid var(--border-subtle) !important;
      border-radius: 10px !important;
      margin-bottom: 12px !important;
    }

    [data-testid="stExpander"] summary {
      font-weight: 600 !important;
      color: #E2E8F0 !important;
      padding: 12px 16px !important;
    }

    [data-testid="stExpander"] summary:hover {
      color: #60A5FA !important;
    }

    /* Inputs, Selectboxes, Number Inputs */
    div[data-baseweb="input"], div[data-baseweb="select"] {
      background-color: rgba(15, 23, 42, 0.7) !important;
      border: 1px solid var(--border-subtle) !important;
      border-radius: 8px !important;
      color: #F8FAFC !important;
    }

    div[data-baseweb="input"]:focus-within, div[data-baseweb="select"]:focus-within {
      border-color: #3B82F6 !important;
      box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.25) !important;
    }

    /* Monospace Code & Logs */
    code, pre {
      font-family: var(--font-mono) !important;
      background-color: #080D1A !important;
      border: 1px solid rgba(255, 255, 255, 0.06) !important;
      border-radius: 6px !important;
    }

    /* Pulsing status dots */
    .pulse-dot {
      display: inline-block;
      width: 8px;
      height: 8px;
      border-radius: 50%;
      margin-right: 6px;
      animation: pulse 2s infinite;
    }

    .pulse-green {
      background: #10B981;
      box-shadow: 0 0 8px #10B981;
    }

    .pulse-amber {
      background: #F59E0B;
      box-shadow: 0 0 8px #F59E0B;
    }

    .pulse-red {
      background: #EF4444;
      box-shadow: 0 0 8px #EF4444;
    }

    .pulse-blue {
      background: #3B82F6;
      box-shadow: 0 0 8px #3B82F6;
    }

    @keyframes pulse {
      0% { transform: scale(0.95); opacity: 0.8; }
      50% { transform: scale(1.2); opacity: 1; }
      100% { transform: scale(0.95); opacity: 0.8; }
    }
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)


def render_page_header(title: str, subtitle: str, badge_text: str = "Enterprise v2.1.0", badge_color: str = "#3B82F6"):
    """Renders a sleek, high-end hero header with badge and metadata."""
    html = f"""
    <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 1.5rem; padding-bottom: 0.8rem; border-bottom: 1px solid rgba(255,255,255,0.08);">
        <div>
            <div style="display: flex; align-items: center; gap: 10px;">
                <h1 style="font-size: 2.1rem; font-weight: 800; margin: 0; color: #FFFFFF; letter-spacing: -0.02em;">{title}</h1>
                <span style="background: rgba(59, 130, 246, 0.15); color: {badge_color}; border: 1px solid rgba(59, 130, 246, 0.3); font-size: 0.72rem; font-weight: 700; padding: 3px 8px; border-radius: 6px; text-transform: uppercase; letter-spacing: 0.05em;">
                    {badge_text}
                </span>
            </div>
            <p style="color: #94A3B8; font-size: 0.95rem; margin: 4px 0 0 0;">{subtitle}</p>
        </div>
        <div style="display: flex; align-items: center; gap: 8px; background: rgba(18, 24, 38, 0.6); padding: 6px 12px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.06);">
            <span class="pulse-dot pulse-green"></span>
            <span style="font-size: 0.75rem; font-weight: 600; color: #E2E8F0; letter-spacing: 0.03em;">SYSTEM NOMINAL</span>
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def render_cluster_pulse_bar(overview: Dict[str, Any], health: Optional[Dict[str, Any]] = None):
    """Renders a high-tech top HUD pulse bar showing real-time cluster vitality."""
    total_nodes = overview.get("total_nodes", 0)
    active_nodes = overview.get("active_nodes", 0)
    total_gpus = overview.get("total_gpus", 0)
    active_trials = overview.get("active_trials_count", 0)
    
    redis_status = health.get("redis_status", "healthy") if health else "healthy"
    latency = health.get("redis_latency_ms", 1.2) if health else 1.2
    samba_status = health.get("storage_samba", "healthy") if health else "healthy"
    minio_status = health.get("storage_minio", "healthy") if health else "healthy"

    r_color = "#10B981" if redis_status == "healthy" else "#EF4444"
    s_color = "#10B981" if samba_status == "healthy" else "#F59E0B"
    m_color = "#10B981" if minio_status == "healthy" else "#F59E0B"

    html = f"""
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 12px; margin-bottom: 1.5rem;">
        <div style="background: rgba(18, 24, 38, 0.65); border: 1px solid rgba(255,255,255,0.06); border-radius: 10px; padding: 10px 14px;">
            <div style="font-size: 0.72rem; color: #94A3B8; font-weight: 600; text-transform: uppercase;">Node Allocation</div>
            <div style="font-family: 'JetBrains Mono', monospace; font-size: 1.25rem; font-weight: 700; color: #FFFFFF;">
                <span style="color: #60A5FA;">{active_nodes}</span> / {total_nodes} <span style="font-size: 0.75rem; color: #94A3B8; font-weight: normal;">Online</span>
            </div>
        </div>
        <div style="background: rgba(18, 24, 38, 0.65); border: 1px solid rgba(255,255,255,0.06); border-radius: 10px; padding: 10px 14px;">
            <div style="font-size: 0.72rem; color: #94A3B8; font-weight: 600; text-transform: uppercase;">Compute Capacity</div>
            <div style="font-family: 'JetBrains Mono', monospace; font-size: 1.25rem; font-weight: 700; color: #FFFFFF;">
                <span style="color: #34D399;">{total_gpus}</span> GPUs <span style="font-size: 0.75rem; color: #94A3B8; font-weight: normal;">Pool</span>
            </div>
        </div>
        <div style="background: rgba(18, 24, 38, 0.65); border: 1px solid rgba(255,255,255,0.06); border-radius: 10px; padding: 10px 14px;">
            <div style="font-size: 0.72rem; color: #94A3B8; font-weight: 600; text-transform: uppercase;">Active Workloads</div>
            <div style="font-family: 'JetBrains Mono', monospace; font-size: 1.25rem; font-weight: 700; color: #FFFFFF;">
                <span style="color: #A78BFA;">{active_trials}</span> Trials <span style="font-size: 0.75rem; color: #94A3B8; font-weight: normal;">Running</span>
            </div>
        </div>
        <div style="background: rgba(18, 24, 38, 0.65); border: 1px solid rgba(255,255,255,0.06); border-radius: 10px; padding: 10px 14px;">
            <div style="font-size: 0.72rem; color: #94A3B8; font-weight: 600; text-transform: uppercase;">Broker Latency</div>
            <div style="font-family: 'JetBrains Mono', monospace; font-size: 1.25rem; font-weight: 700; color: {r_color};">
                {latency:.1f} ms <span style="font-size: 0.75rem; color: #94A3B8; font-weight: normal;">Redis</span>
            </div>
        </div>
        <div style="background: rgba(18, 24, 38, 0.65); border: 1px solid rgba(255,255,255,0.06); border-radius: 10px; padding: 10px 14px;">
            <div style="font-size: 0.72rem; color: #94A3B8; font-weight: 600; text-transform: uppercase;">Storage Fabrics</div>
            <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.85rem; font-weight: 600; margin-top: 4px;">
                <span style="color: {s_color};">● Samba</span> &nbsp;|&nbsp; <span style="color: {m_color};">● MinIO</span>
            </div>
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)
