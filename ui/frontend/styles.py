"""VSCode Workbench styling and UI component helpers for NeuralForge Cluster Admin."""

import textwrap
import streamlit as st
from typing import Any, Dict, List, Optional


def apply_custom_theme():
    """Injects authentic Visual Studio Code Dark+ Workbench CSS into the Streamlit app."""
    custom_css = """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&display=swap');

    :root {
      /* VSCode Dark+ Theme Tokens */
      --vscode-editor-bg: #1E1E1E;
      --vscode-sidebar-bg: #252526;
      --vscode-activitybar-bg: #333333;
      --vscode-statusbar-bg: #007ACC;
      --vscode-titlebar-bg: #1F1F1F;
      --vscode-panel-bg: #1E1E1E;
      --vscode-tab-active-bg: #1E1E1E;
      --vscode-tab-inactive-bg: #2D2D2D;
      --vscode-tab-border: #007ACC;
      --vscode-accent: #007ACC;
      --vscode-accent-hover: #1177BB;
      --vscode-accent-emerald: #10B981;
      --vscode-accent-amber: #CCA700;
      --vscode-accent-rose: #F14C4C;
      --vscode-border: #2B2B2B;
      --vscode-border-light: rgba(255, 255, 255, 0.08);
      --vscode-text-main: #CCCCCC;
      --vscode-text-bright: #FFFFFF;
      --vscode-text-muted: #858585;
      --vscode-list-hover: #2A2D2E;
      --vscode-list-active: #37373D;
      --vscode-input-bg: #3C3C3C;
      --vscode-font-ui: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      --vscode-font-code: 'JetBrains Mono', 'Fira Code', 'Cascadia Code', Consolas, monospace;
    }

    /* Global Workspace Layout */
    html, body, [data-testid="stAppViewContainer"], .main {
      font-family: var(--vscode-font-ui) !important;
      background-color: var(--vscode-editor-bg) !important;
      color: var(--vscode-text-main) !important;
    }

    .main .block-container {
      padding-top: 1.2rem !important;
      padding-bottom: 3.5rem !important;
      max-width: 100% !important;
    }

    /* VSCode Primary Sidebar */
    [data-testid="stSidebar"] {
      background-color: var(--vscode-sidebar-bg) !important;
      border-right: 1px solid var(--vscode-border) !important;
      box-shadow: 2px 0 8px rgba(0, 0, 0, 0.3) !important;
    }

    [data-testid="stSidebar"] > div:first-child {
      padding-top: 0.8rem !important;
      padding-left: 0.9rem !important;
      padding-right: 0.9rem !important;
    }

    [data-testid="stSidebar"] hr {
      margin: 0.8rem 0 !important;
      border-color: var(--vscode-border) !important;
    }

    /* VSCode Navigation / Radio Options */
    [data-testid="stSidebar"] [data-testid="stRadio"] > div {
      gap: 2px !important;
    }

    [data-testid="stSidebar"] [data-testid="stRadio"] label {
      background: transparent !important;
      border-radius: 4px !important;
      padding: 6px 10px !important;
      color: var(--vscode-text-main) !important;
      font-size: 0.88rem !important;
      font-weight: 500 !important;
      transition: background 0.15s ease !important;
      border: 1px solid transparent !important;
      cursor: pointer !important;
    }

    [data-testid="stSidebar"] [data-testid="stRadio"] label:hover {
      background: var(--vscode-list-hover) !important;
      color: var(--vscode-text-bright) !important;
    }

    [data-testid="stSidebar"] [data-testid="stRadio"] label[data-checked="true"],
    [data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) {
      background: var(--vscode-list-active) !important;
      border-left: 3px solid var(--vscode-accent) !important;
      color: var(--vscode-text-bright) !important;
      font-weight: 600 !important;
    }

    /* VSCode Cards & Containers */
    [data-testid="stVerticalBlockBorderWrapper"] {
      background: #252526 !important;
      border: 1px solid var(--vscode-border) !important;
      border-radius: 4px !important;
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.35) !important;
      transition: border-color 0.2s ease !important;
    }

    [data-testid="stVerticalBlockBorderWrapper"]:hover {
      border-color: rgba(255, 255, 255, 0.16) !important;
    }

    /* VSCode Metric Widgets */
    [data-testid="stMetric"] {
      background: #252526 !important;
      border: 1px solid var(--vscode-border) !important;
      border-top: 2px solid var(--vscode-accent) !important;
      border-radius: 4px !important;
      padding: 10px 14px !important;
      box-shadow: 0 2px 6px rgba(0, 0, 0, 0.3) !important;
      transition: all 0.2s ease !important;
    }

    [data-testid="stMetric"]:hover {
      background: #2A2D2E !important;
      border-color: var(--vscode-accent) !important;
    }

    [data-testid="stMetricLabel"] {
      font-size: 0.76rem !important;
      font-weight: 700 !important;
      text-transform: uppercase !important;
      letter-spacing: 0.04em !important;
      color: var(--vscode-text-muted) !important;
    }

    [data-testid="stMetricValue"] {
      font-family: var(--vscode-font-code) !important;
      font-size: 1.6rem !important;
      font-weight: 700 !important;
      color: var(--vscode-text-bright) !important;
    }

    [data-testid="stMetricDelta"] {
      font-size: 0.75rem !important;
      font-weight: 600 !important;
    }

    /* VSCode Editor Tabs */
    .stTabs [data-baseweb="tab-list"] {
      background: #252526 !important;
      border-bottom: 1px solid var(--vscode-border) !important;
      padding: 0 !important;
      gap: 1px !important;
    }

    .stTabs [data-baseweb="tab"] {
      background: var(--vscode-tab-inactive-bg) !important;
      border-radius: 0 !important;
      color: var(--vscode-text-muted) !important;
      font-size: 0.82rem !important;
      font-weight: 500 !important;
      padding: 8px 16px !important;
      border: none !important;
      border-top: 2px solid transparent !important;
      border-right: 1px solid var(--vscode-border) !important;
      transition: all 0.15s ease !important;
    }

    .stTabs [data-baseweb="tab"]:hover {
      color: var(--vscode-text-bright) !important;
      background: #323233 !important;
    }

    .stTabs [aria-selected="true"] {
      background: var(--vscode-tab-active-bg) !important;
      color: var(--vscode-text-bright) !important;
      font-weight: 600 !important;
      border-top: 2px solid var(--vscode-accent) !important;
      border-bottom: 1px solid var(--vscode-tab-active-bg) !important;
    }

    /* VSCode Standard Buttons */
    .stButton > button[kind="primary"] {
      background: var(--vscode-accent) !important;
      color: #FFFFFF !important;
      border: 1px solid transparent !important;
      border-radius: 3px !important;
      font-size: 0.85rem !important;
      font-weight: 600 !important;
      padding: 6px 14px !important;
      box-shadow: 0 1px 3px rgba(0, 0, 0, 0.4) !important;
      transition: background 0.15s ease !important;
    }

    .stButton > button[kind="primary"]:hover {
      background: var(--vscode-accent-hover) !important;
    }

    .stButton > button[kind="secondary"] {
      background: #3C3C3C !important;
      color: var(--vscode-text-bright) !important;
      border: 1px solid #454545 !important;
      border-radius: 3px !important;
      font-size: 0.85rem !important;
      font-weight: 500 !important;
      padding: 6px 14px !important;
      transition: all 0.15s ease !important;
    }

    .stButton > button[kind="secondary"]:hover {
      background: #4A4A4A !important;
      border-color: #555555 !important;
    }

    /* VSCode Inputs, Textareas, Selectboxes */
    div[data-baseweb="input"], div[data-baseweb="select"], div[data-baseweb="textarea"] {
      background-color: var(--vscode-input-bg) !important;
      border: 1px solid var(--vscode-input-bg) !important;
      border-radius: 3px !important;
      color: var(--vscode-text-bright) !important;
      font-size: 0.88rem !important;
    }

    div[data-baseweb="input"]:focus-within, div[data-baseweb="select"]:focus-within, div[data-baseweb="textarea"]:focus-within {
      border-color: var(--vscode-accent) !important;
      box-shadow: 0 0 0 1px var(--vscode-accent) !important;
    }

    /* VSCode Expanders / Tree Collapsible Sections */
    [data-testid="stExpander"] {
      background: #252526 !important;
      border: 1px solid var(--vscode-border) !important;
      border-radius: 3px !important;
      margin-bottom: 8px !important;
    }

    [data-testid="stExpander"] summary {
      font-size: 0.85rem !important;
      font-weight: 600 !important;
      color: var(--vscode-text-main) !important;
      padding: 8px 12px !important;
      background: #2D2D2D !important;
      border-radius: 2px !important;
    }

    [data-testid="stExpander"] summary:hover {
      color: var(--vscode-text-bright) !important;
      background: #333333 !important;
    }

    /* VSCode Monospace Terminal / Code Logs */
    code, pre {
      font-family: var(--vscode-font-code) !important;
      background-color: #181818 !important;
      border: 1px solid var(--vscode-border) !important;
      border-radius: 3px !important;
      color: #E2E8F0 !important;
    }

    /* Custom Scrollbars like Monaco / VSCode */
    ::-webkit-scrollbar {
      width: 10px;
      height: 10px;
    }
    ::-webkit-scrollbar-track {
      background: #1E1E1E;
    }
    ::-webkit-scrollbar-thumb {
      background: #424242;
      border-radius: 4px;
    }
    ::-webkit-scrollbar-thumb:hover {
      background: #4F4F4F;
    }

    /* Status indicator dots */
    .pulse-dot {
      display: inline-block;
      width: 7px;
      height: 7px;
      border-radius: 50%;
      margin-right: 6px;
      animation: pulse 2s infinite;
    }
    .pulse-green {
      background: #10B981;
      box-shadow: 0 0 6px #10B981;
    }
    .pulse-amber {
      background: #CCA700;
      box-shadow: 0 0 6px #CCA700;
    }
    .pulse-red {
      background: #F14C4C;
      box-shadow: 0 0 6px #F14C4C;
    }
    .pulse-blue {
      background: #007ACC;
      box-shadow: 0 0 6px #007ACC;
    }
    @keyframes pulse {
      0% { transform: scale(0.95); opacity: 0.8; }
      50% { transform: scale(1.2); opacity: 1; }
      100% { transform: scale(0.95); opacity: 0.8; }
    }
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)


def clean_html(html_str: str) -> str:
    """Strips leading and trailing whitespace from every line to ensure Markdown never treats indented HTML as pre/code blocks."""
    return "\n".join(line.strip() for line in html_str.strip().splitlines())


def render_vscode_titlebar(cluster_name: str = "production-cima", active_view: str = "Operations Center", username: str = "admin"):
    """Renders the signature VSCode Title Bar with Command Center search bar."""
    html = f"""
    <div style="background: #1F1F1F; border-bottom: 1px solid #2B2B2B; padding: 6px 14px; margin: -1.2rem -1rem 1rem -1rem; display: flex; align-items: center; justify-content: space-between; font-size: 0.82rem; user-select: none;">
        <!-- Left: Logo & Window Title -->
        <div style="display: flex; align-items: center; gap: 10px; min-width: 260px;">
            <span style="font-size: 1.1rem;">🧠</span>
            <div style="display: flex; align-items: center; gap: 6px;">
                <span style="font-weight: 700; color: #FFFFFF; letter-spacing: -0.01em;">NeuralForge</span>
                <span style="color: #6E7681;">[{cluster_name}]</span>
                <span style="color: #484F58;">—</span>
                <span style="color: #8B949E;">{active_view}</span>
            </div>
        </div>

        <!-- Center: VSCode Command Center Search Pill -->
        <div style="flex: 1; max-width: 540px; margin: 0 16px;">
            <div style="background: #2D2D2D; border: 1px solid #3C3C3C; border-radius: 6px; padding: 4px 14px; display: flex; align-items: center; justify-content: space-between; color: #CCCCCC; font-size: 0.78rem; cursor: pointer;">
                <div style="display: flex; align-items: center; gap: 8px;">
                    <span style="font-size: 0.85rem; color: #858585;">🔍</span>
                    <span>neuralforge-cluster &gt; Quick Open, nodes, actions...</span>
                </div>
                <span style="background: #1E1E1E; border: 1px solid #3C3C3C; border-radius: 3px; padding: 1px 5px; font-size: 0.68rem; color: #858585; font-family: monospace;">Ctrl+P</span>
            </div>
        </div>

        <!-- Right: Layout and User Pill -->
        <div style="display: flex; align-items: center; gap: 12px; min-width: 240px; justify-content: flex-end;">
            <div style="display: flex; align-items: center; gap: 5px; background: rgba(0, 122, 204, 0.15); border: 1px solid rgba(0, 122, 204, 0.3); padding: 2px 8px; border-radius: 4px; font-size: 0.72rem; color: #60A5FA; font-weight: 600;">
                <span class="pulse-dot pulse-blue"></span>
                <span>WSL: Ubuntu-22.04</span>
            </div>
            <div style="display: flex; align-items: center; gap: 6px; color: #CCCCCC; font-size: 0.76rem;">
                <span style="background: #007ACC; color: #FFFFFF; font-weight: 700; width: 20px; height: 20px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 0.7rem;">
                    {username[:1].upper() if username else 'A'}
                </span>
                <span style="font-weight: 600;">{username}</span>
            </div>
        </div>
    </div>
    """
    st.markdown(clean_html(html), unsafe_allow_html=True)


def render_vscode_breadcrumbs(category: str, view_name: str, file_name: str):
    """Renders the VSCode Breadcrumbs trail directly below the editor tabs."""
    html = f"""
    <div style="background: #1E1E1E; border-bottom: 1px solid #2B2B2B; padding: 3px 12px; margin-bottom: 1rem; display: flex; align-items: center; gap: 6px; font-size: 0.76rem; color: #858585; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">
        <span style="color: #6E7681;">neuralforge-cluster</span>
        <span>›</span>
        <span style="color: #8B949E;">{category.lower()}</span>
        <span>›</span>
        <span style="color: #007ACC; font-weight: 600;">{file_name}</span>
        <span>›</span>
        <span style="color: #E2E8F0; font-weight: 500;">{view_name}</span>
    </div>
    """
    st.markdown(clean_html(html), unsafe_allow_html=True)


def render_page_header(title: str, subtitle: str, badge_text: str = "VSCode v2.2.0", badge_color: str = "#007ACC"):
    """Renders a sleek VSCode-styled section header."""
    html = f"""
    <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 1.2rem; padding-bottom: 0.6rem; border-bottom: 1px solid #2B2B2B;">
        <div>
            <div style="display: flex; align-items: center; gap: 8px;">
                <h2 style="font-size: 1.7rem; font-weight: 700; margin: 0; color: #FFFFFF; letter-spacing: -0.01em;">{title}</h2>
                <span style="background: rgba(0, 122, 204, 0.15); color: {badge_color}; border: 1px solid rgba(0, 122, 204, 0.35); font-size: 0.7rem; font-weight: 700; padding: 2px 7px; border-radius: 4px; text-transform: uppercase;">
                    {badge_text}
                </span>
            </div>
            <p style="color: #858585; font-size: 0.88rem; margin: 3px 0 0 0;">{subtitle}</p>
        </div>
        <div style="display: flex; align-items: center; gap: 6px; background: #252526; padding: 4px 10px; border-radius: 4px; border: 1px solid #2B2B2B;">
            <span class="pulse-dot pulse-green"></span>
            <span style="font-size: 0.72rem; font-weight: 600; color: #10B981; letter-spacing: 0.03em;">SYSTEM NOMINAL</span>
        </div>
    </div>
    """
    st.markdown(clean_html(html), unsafe_allow_html=True)


def render_cluster_pulse_bar(overview: Dict[str, Any], health: Optional[Dict[str, Any]] = None):
    """Renders the VSCode-styled telemetry ribbon."""
    total_nodes = overview.get("total_nodes", 0)
    active_nodes = overview.get("active_nodes", 0)
    total_gpus = overview.get("total_gpus", 0)
    active_trials = overview.get("active_trials_count", 0)
    
    redis_status = health.get("redis_status", "healthy") if health else "healthy"
    latency = health.get("redis_latency_ms", 1.2) if health else 1.2
    samba_status = health.get("storage_samba", "healthy") if health else "healthy"
    minio_status = health.get("storage_minio", "healthy") if health else "healthy"

    r_color = "#10B981" if redis_status == "healthy" else "#F14C4C"
    s_color = "#10B981" if samba_status == "healthy" else "#CCA700"
    m_color = "#10B981" if minio_status == "healthy" else "#CCA700"

    html = f"""
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(170px, 1fr)); gap: 8px; margin-bottom: 1.2rem;">
        <div style="background: #252526; border: 1px solid #2B2B2B; border-radius: 4px; padding: 8px 12px;">
            <div style="font-size: 0.7rem; color: #858585; font-weight: 700; text-transform: uppercase;">Node Allocation</div>
            <div style="font-family: var(--vscode-font-code); font-size: 1.15rem; font-weight: 700; color: #FFFFFF; margin-top: 2px;">
                <span style="color: #60A5FA;">{active_nodes}</span> / {total_nodes} <span style="font-size: 0.72rem; color: #858585; font-weight: normal;">Online</span>
            </div>
        </div>
        <div style="background: #252526; border: 1px solid #2B2B2B; border-radius: 4px; padding: 8px 12px;">
            <div style="font-size: 0.7rem; color: #858585; font-weight: 700; text-transform: uppercase;">Compute Fabric</div>
            <div style="font-family: var(--vscode-font-code); font-size: 1.15rem; font-weight: 700; color: #FFFFFF; margin-top: 2px;">
                <span style="color: #34D399;">{total_gpus}</span> GPUs <span style="font-size: 0.72rem; color: #858585; font-weight: normal;">Pool</span>
            </div>
        </div>
        <div style="background: #252526; border: 1px solid #2B2B2B; border-radius: 4px; padding: 8px 12px;">
            <div style="font-size: 0.7rem; color: #858585; font-weight: 700; text-transform: uppercase;">Active Workloads</div>
            <div style="font-family: var(--vscode-font-code); font-size: 1.15rem; font-weight: 700; color: #FFFFFF; margin-top: 2px;">
                <span style="color: #A78BFA;">{active_trials}</span> Trials <span style="font-size: 0.72rem; color: #858585; font-weight: normal;">Running</span>
            </div>
        </div>
        <div style="background: #252526; border: 1px solid #2B2B2B; border-radius: 4px; padding: 8px 12px;">
            <div style="font-size: 0.7rem; color: #858585; font-weight: 700; text-transform: uppercase;">Broker Latency</div>
            <div style="font-family: var(--vscode-font-code); font-size: 1.15rem; font-weight: 700; color: {r_color}; margin-top: 2px;">
                {latency:.1f} ms <span style="font-size: 0.72rem; color: #858585; font-weight: normal;">Redis</span>
            </div>
        </div>
        <div style="background: #252526; border: 1px solid #2B2B2B; border-radius: 4px; padding: 8px 12px;">
            <div style="font-size: 0.7rem; color: #858585; font-weight: 700; text-transform: uppercase;">Storage Fabrics</div>
            <div style="font-family: var(--vscode-font-code); font-size: 0.82rem; font-weight: 600; margin-top: 4px;">
                <span style="color: {s_color};">● Samba</span> &nbsp;|&nbsp; <span style="color: {m_color};">● MinIO</span>
            </div>
        </div>
    </div>
    """
    st.markdown(clean_html(html), unsafe_allow_html=True)


def render_vscode_statusbar(overview: Dict[str, Any], health: Optional[Dict[str, Any]] = None):
    """Renders the authentic VSCode blue bottom Status Bar."""
    total_gpus = overview.get("total_gpus", 22)
    active_nodes = overview.get("active_nodes", 11)
    total_nodes = overview.get("total_nodes", 11)
    
    html = f"""
    <div style="position: fixed; bottom: 0; left: 0; right: 0; height: 24px; background: #007ACC; color: #FFFFFF; display: flex; align-items: center; justify-content: space-between; padding: 0 12px; font-size: 0.74rem; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; z-index: 999999; box-shadow: 0 -1px 4px rgba(0,0,0,0.3); user-select: none;">
        <!-- Left status items -->
        <div style="display: flex; align-items: center; gap: 14px;">
            <div style="display: flex; align-items: center; gap: 4px; font-weight: 600;">
                <span>⑂</span>
                <span>main*</span>
            </div>
            <div style="display: flex; align-items: center; gap: 4px;">
                <span>🔄</span>
                <span>Synced (0↓ 0↑)</span>
            </div>
            <div style="display: flex; align-items: center; gap: 6px;">
                <span>⨂ 0</span>
                <span>⚠ 0</span>
            </div>
            <div style="display: flex; align-items: center; gap: 4px;">
                <span>⚡</span>
                <span>{total_gpus} GPUs Online</span>
            </div>
            <div style="display: flex; align-items: center; gap: 4px;">
                <span>🟢</span>
                <span>{active_nodes}/{total_nodes} Nodes Healthy</span>
            </div>
        </div>

        <!-- Right status items -->
        <div style="display: flex; align-items: center; gap: 14px;">
            <span>API: 8001</span>
            <span>FastAPI v2.2.0</span>
            <span>Spaces: 4</span>
            <span>UTF-8</span>
            <span>Python 3.10</span>
            <span style="cursor: pointer;">🔔</span>
        </div>
    </div>
    """
    st.markdown(clean_html(html), unsafe_allow_html=True)
