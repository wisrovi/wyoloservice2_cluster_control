"""Main Streamlit entrypoint for NeuralForge Cluster Admin — VSCode Workbench Edition."""

import streamlit as st

from frontend import __version__
from frontend.api_client import ClusterApiClient
from frontend.styles import (
    apply_custom_theme,
    render_vscode_breadcrumbs,
    render_vscode_statusbar,
    render_vscode_titlebar,
)
from frontend.views.audit_view import render_audit
from frontend.views.benchmarks_view import render_benchmarks
from frontend.views.capabilities_view import render_capabilities
from frontend.views.dispatch_view import render_dispatch
from frontend.views.finops_view import render_finops
from frontend.views.history_view import render_history
from frontend.views.invokers_view import render_invokers
from frontend.views.login_view import render_login
from frontend.views.overview_view import render_overview
from frontend.views.settings_view import render_settings
from frontend.views.storage_view import render_storage
from frontend.views.tasks_view import render_tasks


# Page Configuration
st.set_page_config(
    page_title="NeuralForge Cluster Admin [VSCode Workbench]",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Apply VSCode Dark+ Theme
apply_custom_theme()

# Initialize API client
api_client = ClusterApiClient()

# VSCode Workbench Organization Model
ACTIVITY_GROUPS = {
    "explorer": {
        "title": "EXPLORER",
        "icon": "📁",
        "short_name": "Explorer",
        "badge": "22 GPUs",
        "views": [
            {
                "name": "📊 Operations Center",
                "file": "overview.cluster",
                "badge": "LIVE",
                "badge_color": "#10B981",
                "desc": "Real-time topology, health & watchdog",
            },
            {
                "name": "⚙️ Nodes & Invokers",
                "file": "nodes.invokers",
                "badge": "11 NODES",
                "badge_color": "#007ACC",
                "desc": "Invoker cluster fabric & broadcast pull",
            },
            {
                "name": "📁 Storage & Volumes",
                "file": "storage.volumes",
                "badge": "CIFS",
                "badge_color": "#8B5CF6",
                "desc": "Samba dataset shares & MinIO S3",
            },
        ],
    },
    "run": {
        "title": "RUN & DISPATCH",
        "icon": "🚀",
        "short_name": "Run",
        "badge": "HPO",
        "views": [
            {
                "name": "🚀 Dispatch & Scheduler",
                "file": "dispatch.yaml",
                "badge": "SCHEDULE",
                "badge_color": "#F59E0B",
                "desc": "Workload dispatch & day/night scheduler",
            },
            {
                "name": "📈 Job History",
                "file": "history.log",
                "badge": "LOGS",
                "badge_color": "#6B7280",
                "desc": "Historical trials, artifacts & MLflow",
            },
        ],
    },
    "queues": {
        "title": "TASKS & QUEUES",
        "icon": "📋",
        "short_name": "Queues",
        "badge": "CELERY",
        "views": [
            {
                "name": "📋 Tasks & Queues Monitor",
                "file": "queues.stream",
                "badge": "QUEUED",
                "badge_color": "#EC4899",
                "desc": "Active tasks, Optuna sweeps & DLQ",
            },
            {
                "name": "🏆 GPU Benchmarks",
                "file": "benchmarks.gpu",
                "badge": "RANK",
                "badge_color": "#EAB308",
                "desc": "Inference speed & TFLOPS leaderboard",
            },
        ],
    },
    "telemetry": {
        "title": "TELEMETRY & SPECS",
        "icon": "🌿",
        "short_name": "Telemetry",
        "badge": "GREEN AI",
        "views": [
            {
                "name": "🌿 FinOps & Energy (Green AI)",
                "file": "finops.green",
                "badge": "ECO",
                "badge_color": "#10B981",
                "desc": "Power draw, kWh & carbon footprint",
            },
            {
                "name": "🔬 Cluster Capabilities",
                "file": "capabilities.spec",
                "badge": "CUDA 12",
                "badge_color": "#06B6D4",
                "desc": "Tensor cores, VRAM matrix & architecture",
            },
        ],
    },
    "management": {
        "title": "ADMIN & SECURITY",
        "icon": "⚙️",
        "short_name": "Settings",
        "badge": "RBAC",
        "views": [
            {
                "name": "📜 Audit & Security",
                "file": "audit.sec",
                "badge": "SEC",
                "badge_color": "#6366F1",
                "desc": "Security events & RBAC audit trail",
            },
            {
                "name": "🛠️ Maintenance & Settings",
                "file": "settings.json",
                "badge": "CONFIG",
                "badge_color": "#64748B",
                "desc": "Cluster parameters & webhook alerts",
            },
        ],
    },
}

ALL_PAGES = []
PAGE_TO_CATEGORY = {}
PAGE_TO_FILE = {}
for cat_key, cat_data in ACTIVITY_GROUPS.items():
    for v in cat_data["views"]:
        ALL_PAGES.append(v["name"])
        PAGE_TO_CATEGORY[v["name"]] = cat_key
        PAGE_TO_FILE[v["name"]] = v["file"]

# Check authentication state
if not st.session_state.get("authenticated", False):
    render_login(api_client)
else:
    token = st.session_state.get("token", "")
    username = st.session_state.get("username", "admin")

    # Initialize Workbench Session State
    if "activity_category" not in st.session_state:
        st.session_state["activity_category"] = "explorer"
    if "active_page" not in st.session_state:
        st.session_state["active_page"] = "📊 Operations Center"
    if "open_tabs" not in st.session_state:
        st.session_state["open_tabs"] = ["📊 Operations Center", "⚙️ Nodes & Invokers", "🚀 Dispatch & Scheduler"]
    if "panel_expanded" not in st.session_state:
        st.session_state["panel_expanded"] = False
    if "panel_tab" not in st.session_state:
        st.session_state["panel_tab"] = "OUTPUT"

    # --- PRIMARY SIDEBAR (VSCode Activity Bar + Explorer Pane) ---
    with st.sidebar:
        # VSCode Brand & Activity Bar Header
        st.markdown(
            f"""
            <div style="background: #1F1F1F; border: 1px solid #2B2B2B; border-radius: 4px; padding: 10px 12px; margin-bottom: 12px;">
                <div style="display: flex; align-items: center; justify-content: space-between;">
                    <div style="display: flex; align-items: center; gap: 8px;">
                        <span style="font-size: 1.3rem;">🧠</span>
                        <div>
                            <div style="font-size: 0.95rem; font-weight: 800; color: #FFFFFF; letter-spacing: -0.01em;">NeuralForge</div>
                            <div style="font-size: 0.68rem; color: #858585; text-transform: uppercase; font-weight: 700;">VSCode Workbench • v{__version__}</div>
                        </div>
                    </div>
                    <span style="background: #007ACC; color: #FFFFFF; font-size: 0.65rem; font-weight: 700; padding: 2px 6px; border-radius: 3px;">22 GPUs</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # VSCode Activity Bar (Category Switcher Strip)
        st.caption("🧭 **ACTIVITY BAR**")
        col_act1, col_act2, col_act3, col_act4, col_act5 = st.columns(5)
        
        act_keys = list(ACTIVITY_GROUPS.keys())
        for idx, (col, key) in enumerate(zip([col_act1, col_act2, col_act3, col_act4, col_act5], act_keys)):
            act = ACTIVITY_GROUPS[key]
            is_active = (st.session_state["activity_category"] == key)
            with col:
                btn_type = "primary" if is_active else "secondary"
                if st.button(act["icon"], key=f"act_btn_{key}", help=act["title"], type=btn_type, use_container_width=True):
                    st.session_state["activity_category"] = key
                    # Switch to first view in category if current page is not in it
                    if st.session_state["active_page"] not in [v["name"] for v in act["views"]]:
                        st.session_state["active_page"] = act["views"][0]["name"]
                        if st.session_state["active_page"] not in st.session_state["open_tabs"]:
                            st.session_state["open_tabs"].append(st.session_state["active_page"])
                    st.rerun()

        current_act = ACTIVITY_GROUPS[st.session_state["activity_category"]]

        # Section Header with VSCode Action Bar
        st.markdown(
            f"""
            <div style="display: flex; align-items: center; justify-content: space-between; margin-top: 10px; margin-bottom: 6px; padding: 2px 0;">
                <span style="font-size: 0.72rem; font-weight: 800; color: #BBBBBB; letter-spacing: 0.05em; text-transform: uppercase;">
                    {current_act['title']}
                </span>
                <span style="font-size: 0.7rem; color: #858585;">{current_act['description']}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # VSCode Command Palette Quick Jump (Ctrl+P)
        target_palette_page = st.selectbox(
            "Quick Open (Ctrl+P)",
            options=ALL_PAGES,
            index=ALL_PAGES.index(st.session_state["active_page"]) if st.session_state["active_page"] in ALL_PAGES else 0,
            label_visibility="collapsed",
            help="Type to search and instantly jump to any cluster view or node",
        )
        if target_palette_page != st.session_state["active_page"]:
            st.session_state["active_page"] = target_palette_page
            st.session_state["activity_category"] = PAGE_TO_CATEGORY[target_palette_page]
            if target_palette_page not in st.session_state["open_tabs"]:
                st.session_state["open_tabs"].append(target_palette_page)
            st.rerun()

        # VSCode Collapsible Tree View: WORKSPACE
        with st.expander(f"▼ WORKSPACE: {current_act['short_name'].upper()}", expanded=True):
            category_views = [v["name"] for v in current_act["views"]]
            
            selected_in_category = st.radio(
                "Views in Category:",
                options=category_views,
                index=category_views.index(st.session_state["active_page"]) if st.session_state["active_page"] in category_views else 0,
                label_visibility="collapsed",
                key="category_radio_nav",
            )
            if selected_in_category != st.session_state["active_page"]:
                st.session_state["active_page"] = selected_in_category
                if selected_in_category not in st.session_state["open_tabs"]:
                    st.session_state["open_tabs"].append(selected_in_category)
                st.rerun()

            # Render file-tree badges for active views
            for v in current_act["views"]:
                is_selected = (v["name"] == st.session_state["active_page"])
                bg_item = "background: #37373D; border-left: 2px solid #007ACC;" if is_selected else "background: transparent;"
                st.markdown(
                    f"""
                    <div style="display: flex; align-items: center; justify-content: space-between; {bg_item} padding: 4px 6px; border-radius: 3px; font-size: 0.74rem; font-family: var(--vscode-font-code); color: #CCCCCC; margin-top: 2px;">
                        <div style="display: flex; align-items: center; gap: 6px;">
                            <span style="color: #6E7681;">├─</span>
                            <span style="color: {'#FFFFFF' if is_selected else '#858585'};">{v['file']}</span>
                        </div>
                        <span style="background: rgba(255,255,255,0.06); color: {v['badge_color']}; font-size: 0.65rem; font-weight: 700; padding: 1px 4px; border-radius: 2px;">
                            {v['badge']}
                        </span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        # VSCode Collapsible Tree View: OPEN EDITORS
        with st.expander("▼ OPEN EDITORS", expanded=True):
            if st.session_state["open_tabs"]:
                for tab_name in list(st.session_state["open_tabs"]):
                    col_t1, col_t2 = st.columns([5, 1])
                    is_active_tab = (tab_name == st.session_state["active_page"])
                    with col_t1:
                        tab_prefix = "● " if is_active_tab else "  "
                        btn_label = f"{tab_prefix}{tab_name}"
                        if st.button(btn_label, key=f"open_tab_{tab_name}", use_container_width=True):
                            st.session_state["active_page"] = tab_name
                            st.session_state["activity_category"] = PAGE_TO_CATEGORY[tab_name]
                            st.rerun()
                    with col_t2:
                        if len(st.session_state["open_tabs"]) > 1:
                            if st.button("×", key=f"close_tab_{tab_name}", help=f"Close {tab_name}"):
                                st.session_state["open_tabs"].remove(tab_name)
                                if tab_name == st.session_state["active_page"]:
                                    st.session_state["active_page"] = st.session_state["open_tabs"][-1]
                                    st.session_state["activity_category"] = PAGE_TO_CATEGORY[st.session_state["active_page"]]
                                st.rerun()

        # VSCode Collapsible Tree View: CLUSTER TELEMETRY OUTLINE
        with st.expander("▼ CLUSTER TELEMETRY", expanded=False):
            st.markdown(
                """
                <div style="font-size: 0.74rem; font-family: var(--vscode-font-code); color: #858585; line-height: 1.6;">
                    <div>├─ <span style="color: #60A5FA;">Nodes Online:</span> 11 / 11</div>
                    <div>├─ <span style="color: #34D399;">Active GPUs:</span> 22 Units</div>
                    <div>├─ <span style="color: #A78BFA;">Redis Broker:</span> 1.2 ms (Healthy)</div>
                    <div>├─ <span style="color: #F59E0B;">Samba Share:</span> /datasets (Mounted)</div>
                    <div>└─ <span style="color: #EC4899;">Orchestration:</span> K8s & Docker</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.divider()

        # User Profile Footer
        avatar_initial = username[:1].upper() if username else "A"
        st.markdown(
            f"""
            <div style="background: #1F1F1F; border: 1px solid #2B2B2B; border-radius: 4px; padding: 8px 10px; margin-bottom: 8px; display: flex; align-items: center; justify-content: space-between;">
                <div style="display: flex; align-items: center; gap: 8px;">
                    <div style="width: 24px; height: 24px; border-radius: 50%; background: #007ACC; display: flex; align-items: center; justify-content: center; font-weight: 700; color: #FFFFFF; font-size: 0.75rem;">
                        {avatar_initial}
                    </div>
                    <div>
                        <div style="font-size: 0.78rem; font-weight: 700; color: #FFFFFF;">{username}</div>
                        <div style="font-size: 0.65rem; color: #858585; text-transform: uppercase;">Operator (Admin)</div>
                    </div>
                </div>
                <span class="pulse-dot pulse-green"></span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button("🚪 Sign Out", use_container_width=True, type="secondary"):
            st.session_state["authenticated"] = False
            st.session_state["token"] = None
            st.session_state["username"] = None
            st.rerun()

    # --- MAIN WORKBENCH EDITOR AREA ---

    # 1. VSCode Top Title Bar with Command Center
    active_page = st.session_state["active_page"]
    active_file = PAGE_TO_FILE.get(active_page, "workspace.file")
    active_category_key = PAGE_TO_CATEGORY.get(active_page, "explorer")
    active_category_title = ACTIVITY_GROUPS[active_category_key]["short_name"]

    render_vscode_titlebar(cluster_name="production-cima", active_view=active_page, username=username)

    # 2. VSCode Editor Tabs Strip
    cols_tabs = st.columns(len(st.session_state["open_tabs"]) + 2)
    for idx, t_name in enumerate(st.session_state["open_tabs"]):
        with cols_tabs[idx]:
            is_active = (t_name == active_page)
            t_type = "primary" if is_active else "secondary"
            t_file = PAGE_TO_FILE.get(t_name, "tab")
            if st.button(f"{t_name.split()[0]} {t_file}", key=f"editor_tab_btn_{t_name}", type=t_type, use_container_width=True):
                st.session_state["active_page"] = t_name
                st.session_state["activity_category"] = PAGE_TO_CATEGORY[t_name]
                st.rerun()

    with cols_tabs[-1]:
        # Panel Toggle Button
        panel_label = "🔼 Panel" if not st.session_state["panel_expanded"] else "🔽 Panel"
        if st.button(panel_label, key="toggle_bottom_panel_btn", help="Toggle VSCode Terminal / Output Panel"):
            st.session_state["panel_expanded"] = not st.session_state["panel_expanded"]
            st.rerun()

    # 3. VSCode Breadcrumbs Trail
    render_vscode_breadcrumbs(category=active_category_title, view_name=active_page, file_name=active_file)

    # 4. Route to Active View
    if active_page == "📊 Operations Center":
        render_overview(api_client, token)
    elif active_page == "⚙️ Nodes & Invokers":
        render_invokers(api_client, token)
    elif active_page == "🚀 Dispatch & Scheduler":
        render_dispatch(api_client, token)
    elif active_page == "📋 Tasks & Queues Monitor":
        render_tasks(api_client, token)
    elif active_page == "📁 Storage & Volumes":
        render_storage(api_client, token)
    elif active_page == "📈 Job History":
        render_history(api_client, token)
    elif active_page == "🏆 GPU Benchmarks":
        render_benchmarks(api_client, token)
    elif active_page == "🌿 FinOps & Energy (Green AI)":
        render_finops(api_client, token)
    elif active_page == "🔬 Cluster Capabilities":
        render_capabilities(api_client, token)
    elif active_page == "📜 Audit & Security":
        render_audit(api_client, token)
    elif active_page == "🛠️ Maintenance & Settings":
        render_settings(api_client, token)

    # 5. VSCode Collapsible Bottom Panel (Terminal / Output / Problems / Debug)
    if st.session_state["panel_expanded"]:
        st.markdown("<div style='margin-top: 1.5rem;'></div>", unsafe_allow_html=True)
        with st.container(border=True):
            st.markdown(
                """
                <div style="background: #252526; border-bottom: 1px solid #2B2B2B; padding: 4px 10px; margin: -0.8rem -0.8rem 0.6rem -0.8rem; display: flex; align-items: center; justify-content: space-between;">
                    <div style="display: flex; align-items: center; gap: 14px; font-size: 0.75rem; font-weight: 700; color: #CCCCCC; text-transform: uppercase;">
                        <span style="color: #FFFFFF; border-bottom: 2px solid #007ACC; padding-bottom: 2px;">OUTPUT</span>
                        <span style="color: #858585; cursor: pointer;">TERMINAL</span>
                        <span style="color: #858585; cursor: pointer;">PROBLEMS (0)</span>
                        <span style="color: #858585; cursor: pointer;">DEBUG CONSOLE</span>
                    </div>
                    <span style="font-size: 0.7rem; color: #858585; font-family: monospace;">bash / cluster_admin_api:8001</span>
                </div>
                """,
                unsafe_allow_html=True,
            )

            p_col1, p_col2 = st.columns([4, 1])
            with p_col1:
                st.code(
                    """[2026-10-22 08:24:10] [INFO] [API] GET /api/v1/cluster/overview - 200 OK (1.4ms)
[2026-10-22 08:24:10] [INFO] [CELERY] Broker heartbeat acknowledged: 11 worker invokers active
[2026-10-22 08:24:11] [INFO] [K8S] Dynamic Pod controller pinned to nodes: worker-cima0063p, worker-nas
[2026-10-22 08:24:12] [OK]   [SAMBA] Volume mounted at /wyolo/control_server/datasets (Healthy)
[2026-10-22 08:24:12] [INFO] [OPTUNA] Study state verified on optuna_db: 0 deadlocks detected
[2026-10-22 08:24:13] [READY] NeuralForge Cluster Admin Workbench ready for commands.""",
                    language="bash",
                )
            with p_col2:
                st.caption("⚡ **QUICK COMMANDS**")
                if st.button("🔄 Sync Health", use_container_width=True):
                    st.rerun()
                if st.button("🧹 Clear Output", use_container_width=True):
                    st.toast("Output console cleared.")

    # 6. VSCode Bottom Status Bar
    try:
        overview_data = api_client.get_overview(token)
    except Exception:
        overview_data = {"total_gpus": 22, "active_nodes": 11, "total_nodes": 11}
    render_vscode_statusbar(overview_data)
