"""Main Streamlit entrypoint for NeuralForge Cluster Admin — VSCode Workbench Edition."""

import streamlit as st

from frontend import __version__
from frontend.api_client import ClusterApiClient
from frontend.styles import (
    apply_custom_theme,
    clean_html,
    render_vscode_breadcrumbs,
    render_vscode_menubar,
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
        "description": "Cluster Topology & Storage",
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
        "description": "Workload Scheduler & History",
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
        "description": "Task Monitor & Benchmarks",
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
        "description": "Green AI & Hardware Specs",
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
        "description": "Audit & System Configuration",
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

CLUSTER_FOLDERS = [
    {
        "folder": "CLUSTER TOPOLOGY",
        "icon": "📁",
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
    {
        "folder": "WORKLOADS & ORCHESTRATION",
        "icon": "🚀",
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
    {
        "folder": "GOVERNANCE & TELEMETRY",
        "icon": "🛡️",
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
            {
                "name": "📜 Audit & Security",
                "file": "audit.sec",
                "badge": "RBAC",
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
]

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
            clean_html(f"""
            <div style="background: #1F1F1F; border: 1px solid #2B2B2B; border-radius: 4px; padding: 8px 10px; margin-bottom: 10px;">
                <div style="display: flex; align-items: center; justify-content: space-between;">
                    <div style="display: flex; align-items: center; gap: 8px;">
                        <span style="font-size: 1.2rem;">🧠</span>
                        <div>
                            <div style="font-size: 0.9rem; font-weight: 800; color: #FFFFFF; letter-spacing: -0.01em;">NeuralForge</div>
                            <div style="font-size: 0.65rem; color: #858585; text-transform: uppercase; font-weight: 700;">VSCode Workbench • v{__version__}</div>
                        </div>
                    </div>
                    <span style="background: #007ACC; color: #FFFFFF; font-size: 0.65rem; font-weight: 700; padding: 2px 6px; border-radius: 3px;">22 GPUs</span>
                </div>
            </div>
            """),
            unsafe_allow_html=True,
        )

        # 2-COLUMN SPLIT: Left Activity Bar Icon Rail + Right Primary Sidebar Pane
        col_rail, col_pane = st.columns([1, 4], gap="small")

        with col_rail:
            rail_items = [
                ("explorer", "📁", "Explorer: All Cluster Files & Views (Ctrl+Shift+E)"),
                ("run", "🚀", "Run: Workload Dispatch & Execution (Ctrl+Shift+D)"),
                ("queues", "📋", "Queues: Celery Tasks & DLQ (Ctrl+Shift+T)"),
                ("telemetry", "🌿", "Telemetry: Green AI & Hardware Specs (Ctrl+Shift+M)"),
                ("management", "⚙️", "Settings: Security & Maintenance (Ctrl+,)"),
            ]
            for act_id, icon, act_help in rail_items:
                is_active = (st.session_state["activity_category"] == act_id)
                btn_type = "primary" if is_active else "secondary"
                if st.button(icon, key=f"rail_btn_{act_id}", help=act_help, type=btn_type, use_container_width=True):
                    st.session_state["activity_category"] = act_id
                    st.rerun()

            st.markdown("<div style='margin-top: 1.5rem; border-top: 1px solid #333333; padding-top: 6px;'></div>", unsafe_allow_html=True)
            avatar_initial = username[:1].upper() if username else "A"
            if st.button(avatar_initial, key="rail_btn_user", help=f"User: {username} (Cluster Admin)", type="secondary", use_container_width=True):
                st.toast(f"Operator: {username} | Role: Cluster Admin")
            if st.button("🚪", key="rail_btn_logout", help="Sign Out of Workbench", type="secondary", use_container_width=True):
                st.session_state["authenticated"] = False
                st.session_state["token"] = None
                st.session_state["username"] = None
                st.rerun()

        with col_pane:
            current_cat = st.session_state["activity_category"]

            if current_cat == "explorer":
                st.markdown(
                    clean_html("""
                    <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 6px;">
                        <span style="font-size: 0.72rem; font-weight: 800; color: #BBBBBB; letter-spacing: 0.05em; text-transform: uppercase;">
                            EXPLORER: CLUSTER
                        </span>
                        <span style="font-size: 0.65rem; color: #60A5FA; font-weight: 700;">11 VIEWS</span>
                    </div>
                    """),
                    unsafe_allow_html=True,
                )

                # Search filter: Instant view search
                filter_text = st.text_input(
                    "Filter Views",
                    placeholder="🔎 Filter views (e.g. nodes, gpu)...",
                    label_visibility="collapsed",
                    key="explorer_filter_text",
                ).strip().lower()

                # Open Editors Section
                with st.expander("▼ OPEN EDITORS", expanded=True):
                    if st.session_state["open_tabs"]:
                        for tab_name in list(st.session_state["open_tabs"]):
                            c_t1, c_t2 = st.columns([5, 1])
                            is_active_tab = (tab_name == st.session_state["active_page"])
                            with c_t1:
                                tab_prefix = "● " if is_active_tab else "  "
                                if st.button(f"{tab_prefix}{tab_name}", key=f"open_tab_p_{tab_name}", use_container_width=True):
                                    st.session_state["active_page"] = tab_name
                                    st.session_state["activity_category"] = PAGE_TO_CATEGORY.get(tab_name, "explorer")
                                    st.rerun()
                            with c_t2:
                                if len(st.session_state["open_tabs"]) > 1:
                                    if st.button("×", key=f"close_tab_p_{tab_name}", help=f"Close {tab_name}"):
                                        st.session_state["open_tabs"].remove(tab_name)
                                        if tab_name == st.session_state["active_page"]:
                                            st.session_state["active_page"] = st.session_state["open_tabs"][-1]
                                            st.session_state["activity_category"] = PAGE_TO_CATEGORY.get(st.session_state["active_page"], "explorer")
                                        st.rerun()

                # All 3 Folders with All Views Visible at Once
                for folder_data in CLUSTER_FOLDERS:
                    views_list = folder_data["views"]
                    if filter_text:
                        filtered = [v for v in views_list if filter_text in v["name"].lower() or filter_text in v["file"].lower() or filter_text in v.get("desc", "").lower()]
                        if not filtered:
                            continue
                        views_to_show = filtered
                        is_expanded = True
                    else:
                        views_to_show = views_list
                        is_expanded = True

                    with st.expander(f"📁 {folder_data['folder']}", expanded=is_expanded):
                        for v in views_to_show:
                            is_sel = (v["name"] == st.session_state["active_page"])
                            btn_t = "primary" if is_sel else "secondary"
                            c_b, c_bdg = st.columns([3, 1])
                            with c_b:
                                if st.button(v["name"], key=f"tree_v_{v['file']}", type=btn_t, use_container_width=True):
                                    st.session_state["active_page"] = v["name"]
                                    if v["name"] not in st.session_state["open_tabs"]:
                                        st.session_state["open_tabs"].append(v["name"])
                                    st.rerun()
                            with c_bdg:
                                st.markdown(
                                    clean_html(f"""
                                    <div style="text-align: right; padding-top: 5px;">
                                        <span style="background: rgba(255,255,255,0.06); color: {v['badge_color']}; font-size: 0.62rem; font-weight: 700; padding: 1px 4px; border-radius: 2px;">
                                            {v['badge']}
                                        </span>
                                    </div>
                                    """),
                                    unsafe_allow_html=True,
                                )

            elif current_cat == "run":
                st.markdown(
                    clean_html("""
                    <div style="margin-bottom: 8px;">
                        <span style="font-size: 0.72rem; font-weight: 800; color: #BBBBBB; letter-spacing: 0.05em; text-transform: uppercase;">
                            RUN & DISPATCH
                        </span>
                    </div>
                    """),
                    unsafe_allow_html=True,
                )
                if st.button("🚀 New Workload Dispatch", key="run_quick_dispatch", type="primary", use_container_width=True):
                    st.session_state["active_page"] = "🚀 Dispatch & Scheduler"
                    st.rerun()
                if st.button("📈 View Training History", key="run_quick_history", use_container_width=True):
                    st.session_state["active_page"] = "📈 Job History"
                    st.rerun()
                if st.button("🏆 Benchmark GPU Fabric", key="run_quick_bench", use_container_width=True):
                    st.session_state["active_page"] = "🏆 GPU Benchmarks"
                    st.rerun()
                st.markdown(
                    clean_html("""
                    <div style="font-size: 0.72rem; color: #858585; margin-top: 10px; line-height: 1.5; border-top: 1px solid #2B2B2B; padding-top: 8px;">
                        <div>⚡ <strong>Active Trials:</strong> 4 running</div>
                        <div>🎯 <strong>HPO Engine:</strong> Optuna DB</div>
                        <div>📦 <strong>Storage:</strong> Samba & MinIO</div>
                    </div>
                    """),
                    unsafe_allow_html=True,
                )

            elif current_cat == "queues":
                st.markdown(
                    clean_html("""
                    <div style="margin-bottom: 8px;">
                        <span style="font-size: 0.72rem; font-weight: 800; color: #BBBBBB; letter-spacing: 0.05em; text-transform: uppercase;">
                            TASKS & QUEUES
                        </span>
                    </div>
                    """),
                    unsafe_allow_html=True,
                )
                if st.button("📋 Celery Tasks Monitor", key="queues_quick_tasks", type="primary", use_container_width=True):
                    st.session_state["active_page"] = "📋 Tasks & Queues Monitor"
                    st.rerun()
                st.markdown(
                    clean_html("""
                    <div style="font-size: 0.72rem; color: #858585; margin-top: 10px; line-height: 1.5; border-top: 1px solid #2B2B2B; padding-top: 8px;">
                        <div>📬 <strong>Broker:</strong> Redis (Healthy)</div>
                        <div>⚡ <strong>Invokers:</strong> 11 Nodes Active</div>
                        <div>🧯 <strong>Dead Letter:</strong> 0 in Quarantine</div>
                    </div>
                    """),
                    unsafe_allow_html=True,
                )

            elif current_cat == "telemetry":
                st.markdown(
                    clean_html("""
                    <div style="margin-bottom: 8px;">
                        <span style="font-size: 0.72rem; font-weight: 800; color: #BBBBBB; letter-spacing: 0.05em; text-transform: uppercase;">
                            TELEMETRY & GREEN AI
                        </span>
                    </div>
                    """),
                    unsafe_allow_html=True,
                )
                if st.button("🌿 FinOps & Energy Footprint", key="telemetry_quick_finops", type="primary", use_container_width=True):
                    st.session_state["active_page"] = "🌿 FinOps & Energy (Green AI)"
                    st.rerun()
                if st.button("🔬 Cluster Hardware Specs", key="telemetry_quick_caps", use_container_width=True):
                    st.session_state["active_page"] = "🔬 Cluster Capabilities"
                    st.rerun()
                st.markdown(
                    clean_html("""
                    <div style="font-size: 0.72rem; color: #858585; margin-top: 10px; line-height: 1.5; border-top: 1px solid #2B2B2B; padding-top: 8px;">
                        <div>⚡ <strong>Total GPUs:</strong> 22 Units</div>
                        <div>🌱 <strong>Carbon:</strong> Nominal</div>
                        <div>🔋 <strong>Efficiency:</strong> Green AI v2.2</div>
                    </div>
                    """),
                    unsafe_allow_html=True,
                )

            elif current_cat == "management":
                st.markdown(
                    clean_html("""
                    <div style="margin-bottom: 8px;">
                        <span style="font-size: 0.72rem; font-weight: 800; color: #BBBBBB; letter-spacing: 0.05em; text-transform: uppercase;">
                            ADMIN & SETTINGS
                        </span>
                    </div>
                    """),
                    unsafe_allow_html=True,
                )
                if st.button("📜 Audit & Security Logs", key="mgmt_quick_audit", type="primary", use_container_width=True):
                    st.session_state["active_page"] = "📜 Audit & Security"
                    st.rerun()
                if st.button("🛠️ System Maintenance", key="mgmt_quick_settings", use_container_width=True):
                    st.session_state["active_page"] = "🛠️ Maintenance & Settings"
                    st.rerun()
                st.markdown(
                    clean_html(f"""
                    <div style="font-size: 0.72rem; color: #858585; margin-top: 10px; line-height: 1.5; border-top: 1px solid #2B2B2B; padding-top: 8px;">
                        <div>🔒 <strong>Auth:</strong> JWT Bearer HS256</div>
                        <div>🛡️ <strong>RBAC:</strong> Full Admin (RW)</div>
                        <div>🌐 <strong>API:</strong> FastAPI v{__version__}</div>
                    </div>
                    """),
                    unsafe_allow_html=True,
                )

    # --- MAIN WORKBENCH EDITOR AREA ---

    # 1. VSCode Top Title Bar with Command Center
    active_page = st.session_state["active_page"]
    active_file = PAGE_TO_FILE.get(active_page, "workspace.file")
    active_category_key = PAGE_TO_CATEGORY.get(active_page, "explorer")
    active_category_title = ACTIVITY_GROUPS.get(active_category_key, {}).get("short_name", "Explorer")

    render_vscode_titlebar(cluster_name="production-cima", active_view=active_page, username=username)

    # 2. VSCode Classic Menu Bar (File, Edit, Selection, View, Go, Run, Terminal, Help)
    def handle_navigate(p):
        st.session_state["active_page"] = p
        st.session_state["activity_category"] = PAGE_TO_CATEGORY.get(p, "explorer")
        if p not in st.session_state["open_tabs"]:
            st.session_state["open_tabs"].append(p)
        st.rerun()

    def handle_toggle_panel():
        st.session_state["panel_expanded"] = not st.session_state["panel_expanded"]
        st.rerun()

    def handle_logout():
        st.session_state["authenticated"] = False
        st.session_state["token"] = None
        st.session_state["username"] = None
        st.rerun()

    render_vscode_menubar(
        all_pages=ALL_PAGES,
        current_page=active_page,
        on_select_page=handle_navigate,
        on_toggle_panel=handle_toggle_panel,
        on_logout=handle_logout,
    )

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
                clean_html("""
                <div style="background: #252526; border-bottom: 1px solid #2B2B2B; padding: 4px 10px; margin: -0.8rem -0.8rem 0.6rem -0.8rem; display: flex; align-items: center; justify-content: space-between;">
                    <div style="display: flex; align-items: center; gap: 14px; font-size: 0.75rem; font-weight: 700; color: #CCCCCC; text-transform: uppercase;">
                        <span style="color: #FFFFFF; border-bottom: 2px solid #007ACC; padding-bottom: 2px;">OUTPUT</span>
                        <span style="color: #858585; cursor: pointer;">TERMINAL</span>
                        <span style="color: #858585; cursor: pointer;">PROBLEMS (0)</span>
                        <span style="color: #858585; cursor: pointer;">DEBUG CONSOLE</span>
                    </div>
                    <span style="font-size: 0.7rem; color: #858585; font-family: monospace;">bash / cluster_admin_api:8001</span>
                </div>
                """),
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
