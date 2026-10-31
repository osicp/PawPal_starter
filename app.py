import streamlit as st
import pandas as pd
import altair as alt
from pawpal_system import Owner, Pet, Task, Scheduler, Priority, TimeOfDay

# Set page config
st.set_page_config(page_title="PawPal+ — Smart Pet Care Planner", page_icon="🐾", layout="wide")

# Custom CSS for modern aesthetics and high contrast
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap');
    
    /* Global Styles */
    html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
        font-family: 'Outfit', sans-serif;
        background-color: #F8F9FD !important;
        color: #1A1A2E !important;
    }
    
    /* Global Typography & Headings */
    h1, h2, h3, h4, h5, h6,
    [data-testid="stHeadingWithActionElements"] h1,
    [data-testid="stHeadingWithActionElements"] h2,
    [data-testid="stHeadingWithActionElements"] h3,
    [data-testid="stHeadingWithActionElements"] h4,
    [data-testid="stHeadingWithActionElements"] h5 {
        color: #1A1A2E !important;
        font-family: 'Outfit', sans-serif !important;
        font-weight: 700 !important;
    }

    /* Widget Labels */
    label,
    [data-testid="stWidgetLabel"] label,
    [data-testid="stWidgetLabel"] p,
    [data-testid="stWidgetLabel"] span {
        color: #1A1A2E !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
    }

    /* Input & Select Box styling */
    div[data-baseweb="input"],
    div[data-baseweb="select"] > div {
        background-color: #FFFFFF !important;
        border: 1px solid #CBD5E0 !important;
        border-radius: 8px !important;
    }
    div[data-baseweb="input"] input,
    div[data-baseweb="select"] div,
    div[data-baseweb="select"] span {
        color: #1A1A2E !important;
    }

    /* General Markdown and Text */
    [data-testid="stMarkdownContainer"] p,
    [data-testid="stMarkdownContainer"] span,
    [data-testid="stMarkdownContainer"] em,
    [data-testid="stMarkdownContainer"] strong {
        color: #1A1A2E !important;
    }

    /* Executive Top Bar */
    .executive-bar {
        background: white;
        border-radius: 16px;
        padding: 16px 24px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.04);
        border: 1px solid #EAECEF;
        margin-bottom: 20px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 20px;
    }

    .app-title {
        background: linear-gradient(135deg, #4D96FF 0%, #6BCB77 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        font-size: 2.2rem;
        margin: 0;
        line-height: 1.2;
    }

    .info-badge {
        background: #F1F5F9;
        border-radius: 10px;
        padding: 8px 16px;
        font-size: 0.9rem;
        font-weight: 600;
        color: #334155 !important;
        border: 1px solid #E2E8F0;
        display: inline-flex;
        align-items: center;
        gap: 8px;
    }

    /* Cards and Containers */
    .plan-card {
        background: white;
        border-radius: 14px;
        padding: 22px;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.03);
        margin-bottom: 18px;
        border: 1px solid #EAECEF;
    }

    .chart-card {
        background: white;
        border-radius: 14px;
        padding: 18px;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.03);
        border: 1px solid #EAECEF;
        margin-bottom: 16px;
    }

    /* Empty State Card */
    .empty-state-card {
        background: white;
        border-radius: 16px;
        padding: 48px 32px;
        text-align: center;
        border: 2px dashed #CBD5E0;
        margin: 24px auto;
        max-width: 600px;
    }

    .empty-state-icon {
        font-size: 3.5rem;
        margin-bottom: 12px;
    }

    .empty-state-title {
        font-size: 1.4rem;
        font-weight: 700;
        color: #1A1A2E !important;
        margin-bottom: 8px;
    }

    .empty-state-desc {
        font-size: 0.95rem;
        color: #64748B !important;
        margin-bottom: 24px;
        line-height: 1.5;
    }

    /* Custom Timeline Item styling */
    .timeline-container {
        display: flex;
        flex-direction: column;
        gap: 12px;
        margin-top: 10px;
    }
    
    .timeline-item {
        display: flex;
        align-items: center;
        background: white;
        border-radius: 12px;
        padding: 14px 18px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.02);
        border: 1px solid #F1F3F5;
        border-left-width: 6px;
        border-left-style: solid;
    }
    
    .timeline-item.morning { border-left-color: #4D96FF; }
    .timeline-item.afternoon { border-left-color: #FFB319; }
    .timeline-item.evening { border-left-color: #9B72AA; }
    .timeline-item.any { border-left-color: #6BCB77; }
    
    .time-slot {
        font-weight: 700;
        color: #1A1A2E !important;
        min-width: 120px;
        font-size: 1rem;
        display: flex;
        align-items: center;
        gap: 6px;
    }
    
    .task-details {
        flex-grow: 1;
        padding-left: 14px;
    }
    
    .task-title {
        font-weight: 600;
        font-size: 1.05rem;
        color: #2D3748 !important;
        margin: 0;
    }
    
    .task-meta {
        font-size: 0.85rem;
        color: #718096 !important;
        margin-top: 4px;
        display: flex;
        gap: 12px;
        flex-wrap: wrap;
    }

    .task-meta span {
        color: #718096 !important;
    }
    
    .badge {
        padding: 2px 8px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.75rem;
        text-transform: uppercase;
    }
    
    .badge-high { background-color: #FFF5F5 !important; color: #E53E3E !important; }
    .badge-medium { background-color: #FFFDF0 !important; color: #D69E2E !important; }
    .badge-low { background-color: #F0FFF4 !important; color: #38A169 !important; }
    
    /* Styled buttons */
    div.stButton > button {
        border-radius: 8px !important;
        font-weight: 600 !important;
        transition: all 0.2s ease !important;
    }

    div.stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #4D96FF 0%, #6BCB77 100%) !important;
        color: white !important;
        border: none !important;
        box-shadow: 0 4px 14px rgba(77, 150, 255, 0.25) !important;
    }

    div.stButton > button[kind="primary"] p {
        color: white !important;
        font-weight: 700 !important;
    }
    
    .reason-box {
        background-color: #F8FAFC;
        border-radius: 8px;
        padding: 16px;
        border-left: 4px solid #CBD5E0;
        font-family: monospace;
        font-size: 0.88rem;
        color: #4A5568 !important;
        white-space: pre-wrap;
    }

    /* Custom Segmented Control styling */
    [data-testid="stSegmentedControl"] {
        background-color: white !important;
        border-radius: 12px !important;
        padding: 4px !important;
        border: 1px solid #E2E8F0 !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.02) !important;
        margin-bottom: 18px !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ----------------- SESSION STATE & PERSISTENCE INITIALIZATION -----------------
DATA_FILE = "data.json"

if "scheduler" not in st.session_state:
    loaded_scheduler = Scheduler.from_json(DATA_FILE)
    if loaded_scheduler:
        st.session_state.scheduler = loaded_scheduler
        st.session_state.owner = loaded_scheduler.owner
        st.session_state.pet = loaded_scheduler.pet
    else:
        # Seed default tasks inside our Task class instances
        default_owner = Owner(name="Jordan", available_time_minutes=60)
        default_pet = Pet(name="Mochi", species="Cat", breed="Ragdoll", age=2, owner=default_owner)
        default_tasks = [
            Task(title="Morning Walk", duration_minutes=30, priority=Priority.HIGH, category="walk", time_of_day=TimeOfDay.MORNING),
            Task(title="Breakfast Feed", duration_minutes=15, priority=Priority.HIGH, category="feeding", time_of_day=TimeOfDay.MORNING),
            Task(title="Teeth Grooming", duration_minutes=10, priority=Priority.MEDIUM, category="grooming", time_of_day=TimeOfDay.AFTERNOON),
            Task(title="Fetch Playtime", duration_minutes=25, priority=Priority.MEDIUM, category="enrichment", time_of_day=TimeOfDay.ANY),
            Task(title="Brush Fur", duration_minutes=15, priority=Priority.LOW, category="grooming", time_of_day=TimeOfDay.EVENING)
        ]
        st.session_state.owner = default_owner
        st.session_state.pet = default_pet
        st.session_state.scheduler = Scheduler(pet=st.session_state.pet, tasks=default_tasks)
        st.session_state.scheduler.save_to_json(DATA_FILE)

if "owner" not in st.session_state:
    st.session_state.owner = st.session_state.scheduler.owner

if "pet" not in st.session_state:
    st.session_state.pet = st.session_state.scheduler.pet

TAB_DAILY = "📅 Daily Schedule & Visual Analytics"
TAB_POOL = "📋 Task Pool & Builder"
TAB_SETTINGS = "👤 Pet Settings & Constraints"
TAB_OPTIONS = [TAB_DAILY, TAB_POOL, TAB_SETTINGS]

if "current_tab" not in st.session_state:
    st.session_state.current_tab = TAB_DAILY

if "plan" not in st.session_state:
    st.session_state.plan = None

if "reasoning" not in st.session_state:
    st.session_state.reasoning = ""

if "scheduling_strategy" not in st.session_state:
    st.session_state.scheduling_strategy = "Weighted Multi-Factor Utility"

STRAT_MAP = {
    "Priority Greedy": "priority_greedy",
    "Weighted Multi-Factor Utility": "weighted_utility",
    "Optimal Knapsack": "optimal_knapsack"
}

# Auto-generate initial plan if not yet created and tasks exist
if st.session_state.plan is None and st.session_state.scheduler.tasks:
    strat_key = STRAT_MAP.get(st.session_state.scheduling_strategy, "weighted_utility")
    st.session_state.plan = st.session_state.scheduler.generate_plan(strategy=strat_key)
    st.session_state.reasoning = st.session_state.scheduler.get_reasoning()

# ----------------- PERSISTENT EXECUTIVE TOP BAR -----------------
total_tasks_count = len(st.session_state.scheduler.tasks)
completed_tasks_count = sum(1 for t in st.session_state.scheduler.tasks if t.is_completed)
avail_limit = st.session_state.owner.available_time_minutes

total_scheduled_minutes = sum(item["duration_minutes"] for item in st.session_state.plan) if st.session_state.plan else 0
util_percent = (total_scheduled_minutes / avail_limit * 100) if avail_limit > 0 else 0

top_c1, top_c2, top_c3, top_c4 = st.columns([1.6, 1.2, 1.2, 1.1], vertical_alignment="center")

with top_c1:
    st.markdown('<p class="app-title">🐾 PawPal+ Care</p>', unsafe_allow_html=True)
    st.caption("AI-Powered Pet Care Schedule & Constraints Optimizer")

with top_c2:
    st.markdown(
        f"""
        <div class="info-badge">
            <span>👤 <strong>{st.session_state.owner.name}</strong></span>
            <span>•</span>
            <span>🐾 <strong>{st.session_state.pet.name}</strong> ({st.session_state.pet.species}, {st.session_state.pet.age}yo)</span>
        </div>
        """,
        unsafe_allow_html=True
    )

with top_c3:
    st.markdown(
        f"""
        <div class="info-badge">
            <span>⏱️ <strong>{total_scheduled_minutes} / {avail_limit}m</strong> scheduled ({util_percent:.0f}%)</span>
        </div>
        """,
        unsafe_allow_html=True
    )

with top_c4:
    if st.button("⚡ Generate Schedule", type="primary", use_container_width=True):
        if not st.session_state.scheduler.tasks:
            st.warning("Please add tasks to the pool before generating the schedule.")
        else:
            strat_key = STRAT_MAP.get(st.session_state.scheduling_strategy, "weighted_utility")
            st.session_state.plan = st.session_state.scheduler.generate_plan(strategy=strat_key)
            st.session_state.reasoning = st.session_state.scheduler.get_reasoning()
            st.session_state.current_tab = TAB_DAILY
            st.rerun()

# ----------------- SLEEK TAB NAVIGATION -----------------
nav_idx = TAB_OPTIONS.index(st.session_state.current_tab) if st.session_state.current_tab in TAB_OPTIONS else 0
selected_nav = st.segmented_control(
    "Navigation Tabs",
    options=TAB_OPTIONS,
    default=TAB_OPTIONS[nav_idx],
    label_visibility="collapsed"
)

if selected_nav and selected_nav != st.session_state.current_tab:
    st.session_state.current_tab = selected_nav
    st.rerun()

st.divider()

# ==============================================================================
# TAB 1: 📅 DAILY SCHEDULE & VISUAL ANALYTICS
# ==============================================================================
if st.session_state.current_tab == TAB_DAILY:
    # Check for empty task pool
    if not st.session_state.scheduler.tasks:
        st.markdown(
            """
            <div class="empty-state-card">
                <div class="empty-state-icon">🐾</div>
                <div class="empty-state-title">No Pet Care Tasks Yet</div>
                <div class="empty-state-desc">
                    Your task pool is currently empty. Add your daily pet care routines
                    (walks, meals, medication, enrichment, and grooming) to automatically
                    build an optimized schedule.
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        _, emp_col, _ = st.columns([1, 1.2, 1])
        with emp_col:
            if st.button("➕ Add your first task", type="primary", use_container_width=True):
                st.session_state.current_tab = TAB_POOL
                st.rerun()

    else:
        # Schedule filter controls row
        sf_col1, sf_col2, sf_col3, sf_col4 = st.columns([1.1, 1.0, 1.3, 0.9], vertical_alignment="center")
        
        # Get unique pet names in pool
        unique_pets = {"All"}
        for t in st.session_state.scheduler.tasks:
            if t.pet_name:
                unique_pets.add(t.pet_name)
        sorted_pets = sorted(list(unique_pets))

        with sf_col1:
            sch_pet_filter = st.selectbox(
                "Filter by Pet",
                ["All Pets"] + [p for p in sorted_pets if p != "All"] + (["All (Shared)"] if "All" in sorted_pets else []),
                index=0,
                key="sch_pet_select"
            )
        with sf_col2:
            sch_status_filter = st.selectbox(
                "Filter by Status",
                ["All Tasks", "Pending", "Completed"],
                index=0,
                key="sch_status_select"
            )
        with sf_col3:
            strategy_opts = ["Weighted Multi-Factor Utility", "Optimal Knapsack", "Priority Greedy"]
            cur_strat_idx = strategy_opts.index(st.session_state.scheduling_strategy) if st.session_state.scheduling_strategy in strategy_opts else 0
            sel_strategy = st.selectbox(
                "Scheduling Strategy",
                strategy_opts,
                index=cur_strat_idx,
                key="sch_strategy_select"
            )
            st.session_state.scheduling_strategy = sel_strategy

        with sf_col4:
            st.markdown("<div style='height: 24px;'></div>", unsafe_allow_html=True)
            if st.button("🔄 Recalculate", use_container_width=True):
                gen_p_filter = "All"
                if sch_pet_filter == "All (Shared)":
                    gen_p_filter = "All (Shared)"
                elif sch_pet_filter != "All Pets":
                    gen_p_filter = sch_pet_filter

                gen_s_filter = "All"
                if sch_status_filter == "Pending":
                    gen_s_filter = "Pending"
                elif sch_status_filter == "Completed":
                    gen_s_filter = "Completed"

                strat_key = STRAT_MAP.get(st.session_state.scheduling_strategy, "weighted_utility")
                st.session_state.plan = st.session_state.scheduler.generate_plan(
                    pet_filter=gen_p_filter,
                    status_filter=gen_s_filter,
                    strategy=strat_key
                )
                st.session_state.reasoning = st.session_state.scheduler.get_reasoning()
                st.rerun()

        current_plan = st.session_state.plan or []
        current_reasoning = st.session_state.reasoning or ""

        # Balanced 50/50 Layout: Left for Analytics, Right for Timeline
        col_analytics, col_timeline = st.columns([1, 1], gap="large")

        # ----------------- LEFT: VISUAL ANALYTICS -----------------
        with col_analytics:
            st.subheader("📊 Schedule Analytics & Utilization")

            total_sched_time = sum(item["duration_minutes"] for item in current_plan)
            time_limit = st.session_state.owner.available_time_minutes
            utilization = (total_sched_time / time_limit * 100) if time_limit > 0 else 0
            total_utility_pts = sum(item.get("utility_score", 0.0) for item in current_plan)

            # Filter candidate pool count
            pool_candidates = st.session_state.scheduler.filter_tasks(
                pet_filter=sch_pet_filter if sch_pet_filter != "All Pets" else "All",
                status_filter="All" if sch_status_filter == "All Tasks" else sch_status_filter
            )

            # Metric Cards
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Scheduled Tasks", f"{len(current_plan)} / {len(pool_candidates)}")
            m2.metric("Scheduled Time", f"{total_sched_time}m")
            m3.metric("Available Budget", f"{time_limit}m")
            m4.metric("Care Utility Score", f"{total_utility_pts:.1f} pts")

            # Progress Bar
            st.progress(min(utilization / 100.0, 1.0))
            st.caption(f"Time Budget Utilization: **{total_sched_time} / {time_limit} mins** ({utilization:.1f}%)")

            if current_plan:
                st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
                
                # --- CHART 1: Care Category Distribution (Donut Chart) ---
                st.markdown("##### 🍩 Care Category Time Distribution")
                cat_minutes = {}
                for item in current_plan:
                    cat = item["category"].capitalize()
                    cat_minutes[cat] = cat_minutes.get(cat, 0) + item["duration_minutes"]
                
                cat_df = pd.DataFrame([{"Category": k, "Minutes": v} for k, v in cat_minutes.items()])
                
                category_colors = {
                    "Walk": "#4D96FF",
                    "Feeding": "#6BCB77",
                    "Grooming": "#FFB319",
                    "Meds": "#E53E3E",
                    "Enrichment": "#9B72AA",
                    "Other": "#718096"
                }
                
                donut_chart = (
                    alt.Chart(cat_df)
                    .mark_arc(innerRadius=50, outerRadius=90, stroke="#FFFFFF", strokeWidth=2)
                    .encode(
                        theta=alt.Theta(field="Minutes", type="quantitative"),
                        color=alt.Color(
                            field="Category",
                            type="nominal",
                            scale=alt.Scale(
                                domain=list(category_colors.keys()),
                                range=list(category_colors.values())
                            ),
                            legend=alt.Legend(orient="bottom", columns=3, title=None)
                        ),
                        tooltip=["Category:N", "Minutes:Q"]
                    )
                    .properties(height=240)
                )
                st.altair_chart(donut_chart, use_container_width=True)

                # --- CHART 2: Priority vs Time Allocation (Stacked Bar) ---
                st.markdown("##### 📈 Priority Time Allocation")
                pri_minutes = {"High": 0, "Medium": 0, "Low": 0}
                for item in current_plan:
                    p = item["priority"].capitalize()
                    if p in pri_minutes:
                        pri_minutes[p] += item["duration_minutes"]

                pri_df = pd.DataFrame([
                    {"Priority": k, "Minutes": v} 
                    for k, v in pri_minutes.items() if v > 0
                ])

                if not pri_df.empty:
                    pri_colors = {
                        "High": "#E53E3E",
                        "Medium": "#D69E2E",
                        "Low": "#38A169"
                    }
                    bar_chart = (
                        alt.Chart(pri_df)
                        .mark_bar(cornerRadius=6, height=26)
                        .encode(
                            x=alt.X("Minutes:Q", title="Total Minutes Allocated", axis=alt.Axis(tickMinStep=5)),
                            y=alt.Y("Priority:N", title=None, sort=["High", "Medium", "Low"]),
                            color=alt.Color(
                                "Priority:N",
                                scale=alt.Scale(
                                    domain=list(pri_colors.keys()),
                                    range=list(pri_colors.values())
                                ),
                                legend=None
                            ),
                            tooltip=["Priority:N", "Minutes:Q"]
                        )
                        .properties(height=140)
                    )
                    st.altair_chart(bar_chart, use_container_width=True)

        # ----------------- RIGHT: DAILY TIMELINE -----------------
        with col_timeline:
            st.subheader("⏰ Daily Chronological Timeline")

            if current_plan:
                category_icons = {
                    "walk": "🦮",
                    "feeding": "🥣",
                    "meds": "💊",
                    "enrichment": "🧸",
                    "grooming": "✂️",
                    "other": "🐾"
                }

                timeline_cards = []
                for item in current_plan:
                    icon = category_icons.get(item["category"].lower(), "🐾")
                    time_class = item["time_of_day"].lower()
                    p_name = item["priority"].lower()
                    
                    pet_badge_text = f"🐾 {item['pet_name']}" if item.get("pet_name") and item["pet_name"] != "All" else "🐾 All Pets"
                    rec_badge_text = f"🔄 {item['recurrence'].capitalize()}" if item.get("recurrence") and item["recurrence"] != "none" else ""
                    rec_badge_html = f"<span>{rec_badge_text}</span>" if rec_badge_text else ""
                    util_badge_html = f'<span class="badge" style="background:#EBF8FF !important; color:#2B6CB0 !important;">⭐ {item["utility_score"]} pts ({item["utility_density"]}/m)</span>' if item.get("utility_score") is not None else ""
                    
                    card_html = (
                        f'<div class="timeline-item {time_class}">'
                        f'<div class="time-slot">⏱️ {item["start_time"]} - {item["end_time"]}</div>'
                        f'<div class="task-details">'
                        f'<p class="task-title">{icon} {item["title"]}</p>'
                        f'<div class="task-meta">'
                        f'<span>⏳ {item["duration_minutes"]} mins</span>'
                        f'<span>📂 {item["category"].capitalize()}</span>'
                        f'<span class="badge badge-{p_name}">{item["priority"]} Priority</span>'
                        f'{util_badge_html}'
                        f'<span>{pet_badge_text}</span>'
                        f'{rec_badge_html}'
                        f'</div>'
                        f'</div>'
                        f'</div>'
                    )
                    timeline_cards.append(card_html)
                
                timeline_html = f'<div class="timeline-container">{"".join(timeline_cards)}</div>'
                st.markdown(timeline_html, unsafe_allow_html=True)
            else:
                st.warning("No tasks could be scheduled within your available time limit!")

            # Collapsible Reasoning Log
            st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)
            with st.expander("🧠 View AI Scheduling Reasoning & Decision Engine"):
                st.markdown(f'<div class="reason-box">{current_reasoning}</div>', unsafe_allow_html=True)

# ==============================================================================
# TAB 2: 📋 TASK POOL & BUILDER
# ==============================================================================
elif st.session_state.current_tab == TAB_POOL:
    pool_left, pool_right = st.columns([1, 1.2], gap="large")

    # LEFT: Add Pet Care Task Form (Compact, un-stretched)
    with pool_left:
        st.subheader("📝 Add Pet Care Task")
        
        with st.container():
            task_title = st.text_input("Task Title", placeholder="e.g. Morning Medication")
            
            c_row1_1, c_row1_2 = st.columns(2)
            with c_row1_1:
                duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=15, step=5)
            with c_row1_2:
                priority = st.selectbox("Priority Level", ["low", "medium", "high"], index=1)
                
            c_row2_1, c_row2_2 = st.columns(2)
            with c_row2_1:
                category = st.selectbox("Category", ["walk", "feeding", "meds", "enrichment", "grooming", "other"])
            with c_row2_2:
                pet_name_opt = st.selectbox("Associated Pet", ["All", st.session_state.pet.name, "Other..."])
                if pet_name_opt == "Other...":
                    t_pet_name = st.text_input("Enter Pet Name", value="Biscuit")
                else:
                    t_pet_name = pet_name_opt

            c_row3_1, c_row3_2 = st.columns(2)
            with c_row3_1:
                time_of_day = st.selectbox("Preferred Time of Day", ["any", "morning", "afternoon", "evening"], index=0)
            with c_row3_2:
                recurrence = st.selectbox("Recurrence", ["none", "daily", "weekly"])

            specific_time_val = st.text_input("Specific Start Time (HH:MM, Optional)", value="", placeholder="e.g. 08:30")

            # Actions Row
            act1, act2, act3 = st.columns([1.2, 1, 1.2])
            with act1:
                if st.button("➕ Add Task", type="primary", use_container_width=True):
                    if task_title.strip():
                        spec_time = None
                        valid = True
                        if specific_time_val.strip():
                            try:
                                parts = specific_time_val.strip().split(":")
                                if len(parts) != 2:
                                    raise ValueError()
                                h, m = int(parts[0]), int(parts[1])
                                if not (0 <= h < 24 and 0 <= m < 60):
                                    raise ValueError()
                                spec_time = f"{h:02d}:{m:02d}"
                            except ValueError:
                                st.error("Invalid time! Use HH:MM format (e.g. 08:30).")
                                valid = False
                        
                        if valid:
                            new_task = Task(
                                title=task_title.strip(),
                                duration_minutes=int(duration),
                                priority=Priority.from_str(priority),
                                category=category,
                                time_of_day=TimeOfDay.from_str(time_of_day),
                                specific_time=spec_time,
                                pet_name=t_pet_name.strip(),
                                recurrence=recurrence
                            )
                            st.session_state.scheduler.add_task(new_task)
                            st.session_state.scheduler.save_to_json(DATA_FILE)
                            # Regenerate plan with new task using selected strategy
                            strat_key = STRAT_MAP.get(st.session_state.get("scheduling_strategy", "Weighted Multi-Factor Utility"), "weighted_utility")
                            st.session_state.plan = st.session_state.scheduler.generate_plan(strategy=strat_key)
                            st.session_state.reasoning = st.session_state.scheduler.get_reasoning()
                            st.success(f"Added task: '{task_title}'!")
                            st.rerun()
                    else:
                        st.error("Task title cannot be empty!")

            with act2:
                if st.button("🗑️ Clear", use_container_width=True):
                    st.session_state.scheduler.tasks = []
                    st.session_state.plan = []
                    st.session_state.reasoning = ""
                    st.session_state.scheduler.save_to_json(DATA_FILE)
                    st.info("Cleared all tasks.")
                    st.rerun()

            with act3:
                if st.button("🔄 Reset Recurring", use_container_width=True):
                    reset_count = 0
                    for t in st.session_state.scheduler.tasks:
                        if t.recurrence != "none" and t.is_completed:
                            t.is_completed = False
                            reset_count += 1
                    if reset_count > 0:
                        st.session_state.scheduler.save_to_json(DATA_FILE)
                    st.success(f"Reset {reset_count} completed recurring tasks!")
                    st.rerun()

    # RIGHT: Current Task List Pool & Filters
    with pool_right:
        st.subheader("📋 Current Task Pool & Checklist")

        # Conflict Detection Warning Banner
        pool_conflicts = st.session_state.scheduler.detect_conflicts()
        if pool_conflicts:
            st.warning("⚠️ **Time Conflict Warning in Pool**:")
            for c in pool_conflicts:
                st.write(f"- {c['message']}")

        # Filter Pool
        f1, f2 = st.columns(2)
        unique_pets_pool = {"All"}
        for t in st.session_state.scheduler.tasks:
            if t.pet_name:
                unique_pets_pool.add(t.pet_name)
        sorted_pets_pool = sorted(list(unique_pets_pool))

        with f1:
            sel_pet_filter = st.selectbox(
                "Filter by Pet",
                ["All Pets"] + [p for p in sorted_pets_pool if p != "All"] + (["All (Shared)"] if "All" in sorted_pets_pool else []),
                index=0,
                key="pool_pet_filter"
            )
        with f2:
            sel_status_filter = st.selectbox(
                "Filter by Status",
                ["All Tasks", "Pending", "Completed"],
                index=0,
                key="pool_status_filter"
            )

        gen_status_pool = "All" if sel_status_filter == "All Tasks" else sel_status_filter
        filtered_pool_tasks = st.session_state.scheduler.filter_tasks(
            pet_filter=sel_pet_filter if sel_pet_filter != "All Pets" else "All",
            status_filter=gen_status_pool
        )
        sorted_pool_tasks = st.session_state.scheduler.sort_tasks_by_time(filtered_pool_tasks)

        if sorted_pool_tasks:
            with st.expander("📊 View Task Summary Table"):
                summary_df = []
                for i, t in enumerate(sorted_pool_tasks):
                    summary_df.append({
                        "Index": i + 1,
                        "Title": t.title,
                        "Pet": t.pet_name,
                        "Duration (min)": t.duration_minutes,
                        "Priority": t.priority.name,
                        "Category": t.category.capitalize(),
                        "Utility Score": t.calculate_utility_score(),
                        "Density (pts/m)": t.get_utility_density(),
                        "Time Preference": f"{t.specific_time}" if t.specific_time else f"{t.time_of_day.value.capitalize()}",
                        "Recurrence": t.recurrence.capitalize(),
                        "Status": "Completed" if t.is_completed else "Pending"
                    })
                st.table(summary_df)

            st.markdown("##### *Interactive Checklist:*")
            for t in sorted_pool_tasks:
                try:
                    original_idx = st.session_state.scheduler.tasks.index(t)
                except ValueError:
                    continue

                t_col_check, t_col_desc, t_col_del = st.columns([0.08, 0.84, 0.08])
                with t_col_check:
                    is_checked = st.checkbox(f"Complete {t.title}", value=t.is_completed, key=f"check_pool_{original_idx}", label_visibility="collapsed")
                    if is_checked != t.is_completed:
                        if is_checked:
                            st.session_state.scheduler.mark_task_complete(t)
                        else:
                            t.update_status(False)
                        st.session_state.scheduler.save_to_json(DATA_FILE)
                        strat_key = STRAT_MAP.get(st.session_state.get("scheduling_strategy", "Weighted Multi-Factor Utility"), "weighted_utility")
                        st.session_state.plan = st.session_state.scheduler.generate_plan(strategy=strat_key)
                        st.session_state.reasoning = st.session_state.scheduler.get_reasoning()
                        st.rerun()

                with t_col_desc:
                    time_str = f"⏰ {t.specific_time}" if t.specific_time else f"📅 {t.time_of_day.value.capitalize()}"
                    rec_badge = f" | 🔄 {t.recurrence.capitalize()}" if t.recurrence != "none" else ""
                    pet_badge = f" | 🐾 {t.pet_name}" if t.pet_name != "All" else " | 🐾 All Pets"
                    
                    if t.is_completed:
                        st.success(f"**{t.title}** ({t.duration_minutes}m) — `{t.priority.name}` — {time_str}{pet_badge}{rec_badge} (Completed)")
                    else:
                        st.info(f"**{t.title}** ({t.duration_minutes}m) — `{t.priority.name}` — {time_str}{pet_badge}{rec_badge}")

                with t_col_del:
                    if st.button("🗑️", key=f"del_task_{original_idx}", help=f"Delete '{t.title}'"):
                        st.session_state.scheduler.tasks.remove(t)
                        st.session_state.scheduler.save_to_json(DATA_FILE)
                        strat_key = STRAT_MAP.get(st.session_state.get("scheduling_strategy", "Weighted Multi-Factor Utility"), "weighted_utility")
                        st.session_state.plan = st.session_state.scheduler.generate_plan(strategy=strat_key)
                        st.session_state.reasoning = st.session_state.scheduler.get_reasoning()
                        st.rerun()
        else:
            st.info("No tasks matching current filters.")

# ==============================================================================
# TAB 3: 👤 PET SETTINGS & CONSTRAINTS
# ==============================================================================
elif st.session_state.current_tab == TAB_SETTINGS:
    st.subheader("👤 Profiles & Constraints Management")

    set_c1, set_c2 = st.columns(2, gap="large")

    with set_c1:
        st.markdown("#### Caregiver Profile & Time Constraints")
        with st.container():
            owner_name = st.text_input("Owner Name", value=st.session_state.owner.name)
            available_time = st.number_input(
                "Available Care Time (min/day)",
                min_value=10,
                max_value=1440,
                value=st.session_state.owner.available_time_minutes,
                step=10,
                help="Maximum minutes you can dedicate to pet care today."
            )
            
            if (owner_name != st.session_state.owner.name or 
                available_time != st.session_state.owner.available_time_minutes):
                st.session_state.owner.name = owner_name
                st.session_state.owner.available_time_minutes = available_time
                st.session_state.scheduler.save_to_json(DATA_FILE)
                strat_key = STRAT_MAP.get(st.session_state.get("scheduling_strategy", "Weighted Multi-Factor Utility"), "weighted_utility")
                st.session_state.plan = st.session_state.scheduler.generate_plan(strategy=strat_key)
                st.session_state.reasoning = st.session_state.scheduler.get_reasoning()

    with set_c2:
        st.markdown("#### Primary Pet Details")
        with st.container():
            pet_name = st.text_input("Pet Name", value=st.session_state.pet.name)
            
            species_options = ["Dog", "Cat", "Bird", "Rabbit", "Reptile", "Other"]
            species_index = species_options.index(st.session_state.pet.species) if st.session_state.pet.species in species_options else 1
            species = st.selectbox("Species", species_options, index=species_index)
            
            breed = st.text_input("Breed", value=st.session_state.pet.breed)
            age = st.number_input("Age (years)", min_value=0, max_value=30, value=st.session_state.pet.age, step=1)
            
            if (pet_name != st.session_state.pet.name or
                species != st.session_state.pet.species or
                breed != st.session_state.pet.breed or
                age != st.session_state.pet.age):
                st.session_state.pet.name = pet_name
                st.session_state.pet.species = species
                st.session_state.pet.breed = breed
                st.session_state.pet.age = age
                st.session_state.scheduler.save_to_json(DATA_FILE)

    st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
    
    # Storage & Persistence Management
    st.markdown("#### 💾 Storage & Data Persistence")
    persist_c1, persist_c2, persist_c3 = st.columns([1, 1, 1.2])
    with persist_c1:
        if st.button("💾 Force Save to data.json", use_container_width=True):
            if st.session_state.scheduler.save_to_json(DATA_FILE):
                st.success("Successfully persisted current state to data.json!")
            else:
                st.error("Failed to save to data.json.")
    with persist_c2:
        if st.button("📥 Reload from data.json", use_container_width=True):
            if st.session_state.scheduler.load_from_json(DATA_FILE):
                st.session_state.owner = st.session_state.scheduler.owner
                st.session_state.pet = st.session_state.scheduler.pet
                strat_key = STRAT_MAP.get(st.session_state.get("scheduling_strategy", "Weighted Multi-Factor Utility"), "weighted_utility")
                st.session_state.plan = st.session_state.scheduler.generate_plan(strategy=strat_key)
                st.session_state.reasoning = st.session_state.scheduler.get_reasoning()
                st.success("Reloaded state from data.json!")
                st.rerun()
            else:
                st.warning("Could not reload data.json (missing or corrupt).")
    with persist_c3:
        st.caption(f"📁 Local storage file: `{DATA_FILE}` (Atomic write protected)")

    st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
    st.markdown("#### Active Configuration Preview")
    prev_col1, prev_col2 = st.columns(2)
    with prev_col1:
        st.info(f"**Caregiver Summary:** {st.session_state.owner.get_owner_details()}")
    with prev_col2:
        st.success(f"**Pet Profile:** {st.session_state.pet.get_profile()}")
