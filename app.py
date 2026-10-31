import streamlit as st
from pawpal_system import Owner, Pet, Task, Scheduler, Priority, TimeOfDay

# Set page config
st.set_page_config(page_title="PawPal+ — Smart Pet Care Planner", page_icon="🐾", layout="wide")

# Custom CSS for premium aesthetics
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap');
    
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
    }

    /* Widget Labels (inputs, selectboxes, number inputs) */
    label,
    [data-testid="stWidgetLabel"] label,
    [data-testid="stWidgetLabel"] p,
    [data-testid="stWidgetLabel"] span {
        color: #1A1A2E !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
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

    /* Metrics */
    [data-testid="stMetricLabel"] p {
        color: #4A5568 !important;
        font-weight: 600 !important;
    }
    [data-testid="stMetricValue"] div {
        color: #1A1A2E !important;
    }
    
    /* Header styling */
    .app-header {
        background: linear-gradient(135deg, #4D96FF 0%, #6BCB77 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        font-size: 3rem;
        margin-bottom: 0.5rem;
    }
    
    .stSubheader {
        font-weight: 600;
        color: #1A1A2E !important;
    }
    
    /* Cards and Containers */
    .plan-card {
        background: white;
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.04);
        margin-bottom: 20px;
        border: 1px solid #EAECEF;
        transition: transform 0.2s ease;
    }
    
    .plan-card:hover {
        transform: translateY(-2px);
    }
    
    /* Custom Timeline Item styling */
    .timeline-container {
        display: flex;
        flex-direction: column;
        gap: 12px;
        margin-top: 15px;
    }
    
    .timeline-item {
        display: flex;
        align-items: center;
        background: white;
        border-radius: 12px;
        padding: 16px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.02);
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
        min-width: 110px;
        font-size: 1.05rem;
        display: flex;
        align-items: center;
        gap: 6px;
    }
    
    .task-details {
        flex-grow: 1;
        padding-left: 15px;
    }
    
    .task-title {
        font-weight: 600;
        font-size: 1.1rem;
        color: #2D3748 !important;
        margin: 0;
    }
    
    .task-meta {
        font-size: 0.85rem;
        color: #718096 !important;
        margin-top: 4px;
        display: flex;
        gap: 12px;
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
    div.stButton > button:first-child {
        background: linear-gradient(135deg, #4D96FF 0%, #6BCB77 100%) !important;
        color: white !important;
        border: none;
        border-radius: 8px;
        padding: 10px 24px;
        font-weight: 600;
        box-shadow: 0 4px 15px rgba(77, 150, 255, 0.2);
        transition: all 0.2s ease;
        width: 100%;
    }
    
    div.stButton > button:first-child:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(77, 150, 255, 0.3);
    }

    div.stButton > button:first-child p {
        color: white !important;
    }
    
    .reason-box {
        background-color: #F7FAFC;
        border-radius: 8px;
        padding: 16px;
        border-left: 4px solid #CBD5E0;
        font-family: monospace;
        font-size: 0.9rem;
        color: #4A5568 !important;
        white-space: pre-wrap;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ----------------- SESSION STATE INITIALIZATION (Pattern A) -----------------
if "owner" not in st.session_state:
    st.session_state.owner = Owner(name="Jordan", available_time_minutes=60)

if "pet" not in st.session_state:
    st.session_state.pet = Pet(name="Mochi", species="Cat", breed="Ragdoll", age=2, owner=st.session_state.owner)

if "scheduler" not in st.session_state:
    # Seed default tasks inside our Task class instances
    default_tasks = [
        Task(title="Morning Walk", duration_minutes=30, priority=Priority.HIGH, category="walk", time_of_day=TimeOfDay.MORNING),
        Task(title="Breakfast Feed", duration_minutes=15, priority=Priority.HIGH, category="feeding", time_of_day=TimeOfDay.MORNING),
        Task(title="Teeth Grooming", duration_minutes=10, priority=Priority.MEDIUM, category="grooming", time_of_day=TimeOfDay.AFTERNOON),
        Task(title="Fetch Playtime", duration_minutes=25, priority=Priority.MEDIUM, category="enrichment", time_of_day=TimeOfDay.ANY),
        Task(title="Brush Fur", duration_minutes=15, priority=Priority.LOW, category="grooming", time_of_day=TimeOfDay.EVENING)
    ]
    st.session_state.scheduler = Scheduler(pet=st.session_state.pet, tasks=default_tasks)

# Render main header with nice emojis
st.markdown('<h1 class="app-header">🐾 PawPal+ Care Assistant</h1>', unsafe_allow_html=True)
st.markdown("##### *Helping busy pet owners maintain consistent, optimized care for their companions.*")
st.divider()

# Layout split into two columns: Left for Inputs, Right for Generated Schedule
col_left, col_right = st.columns([1, 1.2], gap="large")

with col_left:
    st.subheader("👤 Profiles & Constraints")
    
    # Grid for Owner & Pet info (updating the session state objects directly)
    c1, c2 = st.columns(2)
    with c1:
        owner_name = st.text_input("Owner Name", value=st.session_state.owner.name)
        available_time = st.number_input("Available Time (min/day)", min_value=10, max_value=1440, value=st.session_state.owner.available_time_minutes, step=10)
    with c2:
        pet_name = st.text_input("Pet Name", value=st.session_state.pet.name)
        
        # Selectbox mapping index to preserve current species selection
        species_options = ["Dog", "Cat", "Bird", "Rabbit", "Reptile", "Other"]
        species_index = species_options.index(st.session_state.pet.species) if st.session_state.pet.species in species_options else 1
        species = st.selectbox("Species", species_options, index=species_index)
        
    c3, c4 = st.columns(2)
    with c3:
        breed = st.text_input("Breed", value=st.session_state.pet.breed)
    with c4:
        age = st.number_input("Age (years)", min_value=0, max_value=30, value=st.session_state.pet.age, step=1)
    
    # Keep attributes in session state synced with UI inputs
    st.session_state.owner.name = owner_name
    st.session_state.owner.available_time_minutes = available_time
    st.session_state.pet.name = pet_name
    st.session_state.pet.species = species
    st.session_state.pet.breed = breed
    st.session_state.pet.age = age
    
    st.divider()
    
    st.subheader("📝 Add Pet Care Task")
    
    t_col1, t_col2 = st.columns(2)
    with t_col1:
        task_title = st.text_input("Task Title", placeholder="e.g. Give Medication")
        category = st.selectbox("Category", ["walk", "feeding", "meds", "enrichment", "grooming", "other"])
        
        # Associated pet selection
        pet_name_opt = st.selectbox("Associated Pet", ["All", st.session_state.pet.name, "Other..."])
        if pet_name_opt == "Other...":
            t_pet_name = st.text_input("Enter Pet Name", value="Biscuit")
        else:
            t_pet_name = pet_name_opt
            
    with t_col2:
        duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=15, step=5)
        priority = st.selectbox("Priority Level", ["low", "medium", "high"], index=1)
        recurrence = st.selectbox("Recurrence", ["none", "daily", "weekly"])
        
    c_time1, c_time2 = st.columns(2)
    with c_time1:
        time_of_day = st.selectbox("Preferred Time of Day", ["any", "morning", "afternoon", "evening"], index=0)
    with c_time2:
        specific_time_val = st.text_input("Specific Start Time (HH:MM, Optional)", value="")
    
    # Task actions (Add, Clear, Reset)
    act_col1, act_col2, act_col3 = st.columns([1, 1, 1.2])
    with act_col1:
        if st.button("➕ Add Task"):
            if task_title.strip():
                # Validate specific time format if provided
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
                    st.success(f"Added task: '{task_title}'!")
                    st.rerun()
            else:
                st.error("Task title cannot be empty!")
                
    with act_col2:
        if st.button("🗑️ Clear Tasks"):
            st.session_state.scheduler.tasks = []
            st.info("Cleared all tasks.")
            st.rerun()

    with act_col3:
        if st.button("🔄 Reset Recurring"):
            reset_count = 0
            for t in st.session_state.scheduler.tasks:
                if t.recurrence != "none" and t.is_completed:
                    t.is_completed = False
                    reset_count += 1
            st.success(f"Reset {reset_count} completed recurring tasks!")
            st.rerun()
            
    # List Current Tasks from Scheduler's internal list
    st.divider()
    st.markdown("### 📋 Current Task List Pool")
    
    # Conflict Detection Warning Banner
    pool_conflicts = st.session_state.scheduler.detect_conflicts()
    if pool_conflicts:
        st.warning("⚠️ **Time Conflict Warning in Pool**:")
        for c in pool_conflicts:
            st.write(f"- {c['message']}")
            
    # Filters
    st.markdown("##### *Filter Pool List:*")
    f_col1, f_col2 = st.columns(2)
    
    # Get unique pet names in the pool to populate the dropdown
    unique_pets = {"All"}
    for t in st.session_state.scheduler.tasks:
        if t.pet_name:
            unique_pets.add(t.pet_name)
    sorted_pets = sorted(list(unique_pets))
    
    with f_col1:
        selected_pet_filter = st.selectbox("Filter by Pet", ["All Pets"] + [p for p in sorted_pets if p != "All"] + (["All (Shared)"] if "All" in sorted_pets else []), index=0)
    with f_col2:
        selected_status_filter = st.selectbox("Filter by Status", ["All Tasks", "Pending", "Completed"], index=0)
        
    # Map selection strings to filter keys
    pet_filter_key = "All"
    if selected_pet_filter == "All (Shared)":
        pet_filter_key = "All"
    elif selected_pet_filter != "All Pets":
        pet_filter_key = selected_pet_filter
        
    # Filter and display tasks interactively using Scheduler methods
    gen_status = "All" if selected_status_filter == "All Tasks" else selected_status_filter
    
    filtered_tasks = st.session_state.scheduler.filter_tasks(
        pet_filter=pet_filter_key, 
        status_filter=gen_status
    )
    
    # Sort tasks using Scheduler method
    sorted_tasks = st.session_state.scheduler.sort_tasks_by_time(filtered_tasks)
    
    # Post-filter for "All (Shared)" if selected in the UI
    if selected_pet_filter == "All (Shared)":
        sorted_tasks = [t for t in sorted_tasks if t.pet_name.lower() == "all"]
        
    if sorted_tasks:
        # Collapsible Expander containing professional summary table
        with st.expander("📊 View Task Summary Table"):
            summary_df = []
            for i, t in enumerate(sorted_tasks):
                summary_df.append({
                    "Index": i + 1,
                    "Title": t.title,
                    "Pet": t.pet_name,
                    "Duration (min)": t.duration_minutes,
                    "Priority": t.priority.name,
                    "Time Preference": f"{t.specific_time}" if t.specific_time else f"{t.time_of_day.value.capitalize()}",
                    "Recurrence": t.recurrence.capitalize(),
                    "Status": "Completed" if t.is_completed else "Pending"
                })
            st.table(summary_df)

        st.markdown("##### *Interactive Checklist:*")
        for t in sorted_tasks:
            # Find original index of this task in st.session_state.scheduler.tasks to maintain state
            try:
                original_idx = st.session_state.scheduler.tasks.index(t)
            except ValueError:
                continue

            # Custom container for interactive tasks
            t_col_check, t_col_desc = st.columns([0.08, 0.92])
            with t_col_check:
                # Track check box state and update status when toggled
                is_checked = st.checkbox("", value=t.is_completed, key=f"check_pool_{original_idx}")
                if is_checked != t.is_completed:
                    if is_checked:
                        st.session_state.scheduler.mark_task_complete(t)
                    else:
                        t.update_status(False)
                    st.rerun()
            with t_col_desc:
                time_str = f"⏰ {t.specific_time}" if t.specific_time else f"📅 {t.time_of_day.value.capitalize()}"
                rec_badge = f" | 🔄 {t.recurrence.capitalize()}" if t.recurrence != "none" else ""
                pet_badge = f" | 🐾 {t.pet_name}" if t.pet_name != "All" else " | 🐾 All Pets"
                
                # Render using st.success for completed tasks and st.info for pending tasks
                if t.is_completed:
                    st.success(f"**{t.title}** ({t.duration_minutes}m) — `{t.priority.name}` — {time_str}{pet_badge}{rec_badge} (Completed)")
                else:
                    st.info(f"**{t.title}** ({t.duration_minutes}m) — `{t.priority.name}` — {time_str}{pet_badge}{rec_badge}")
    else:
        st.info("No tasks in the pool matching current filters.")

with col_right:
    st.subheader("📅 Daily Schedule & Planner")
    
    # Build schedule button
    if st.button("⚡ Generate Daily Schedule"):
        if not st.session_state.scheduler.tasks:
            st.warning("Please add some tasks to the pool before generating the schedule.")
        else:
            # Map filters for generate_plan
            gen_pet_filter = pet_filter_key
            gen_status_filter = "All"
            if selected_status_filter == "Pending":
                gen_status_filter = "Pending"
            elif selected_status_filter == "Completed":
                gen_status_filter = "Completed"

            # Solve schedule and retrieve reasoning using methods we wrote
            plan = st.session_state.scheduler.generate_plan(pet_filter=gen_pet_filter, status_filter=gen_status_filter)
            reasoning = st.session_state.scheduler.get_reasoning()
            
            # Summarize metrics
            total_scheduled_time = sum(item["duration_minutes"] for item in plan)
            utilization = (total_scheduled_time / st.session_state.owner.available_time_minutes) * 100
            
            st.markdown(f"#### Generated Schedule for **{st.session_state.pet.name}**")
            st.markdown(f"*{st.session_state.pet.get_profile()}*")
            
            # Metrics Row
            m_col1, m_col2, m_col3 = st.columns(3)
            m_col1.metric("Scheduled Tasks", f"{len(plan)} / {len(sorted_tasks)}")
            m_col2.metric("Scheduled Duration", f"{total_scheduled_time} mins")
            m_col3.metric("Available Time Limit", f"{st.session_state.owner.available_time_minutes} mins")
            
            # Progress bar for time utilization
            st.progress(min(utilization / 100.0, 1.0))
            st.caption(f"Time utilization: {total_scheduled_time} / {st.session_state.owner.available_time_minutes} minutes ({utilization:.1f}%)")
            
            # Display Plan Timeline
            if plan:
                st.markdown("### ⏰ Daily Timeline")
                timeline_cards = []
                for item in plan:
                    # Select icons based on category
                    category_icons = {
                        "walk": "🦮",
                        "feeding": "🥣",
                        "meds": "💊",
                        "enrichment": "🧸",
                        "grooming": "✂️",
                        "other": "🐾"
                    }
                    icon = category_icons.get(item["category"].lower(), "🐾")
                    
                    time_class = item["time_of_day"].lower()
                    p_name = item["priority"].lower()
                    
                    pet_badge_text = f"🐾 {item['pet_name']}" if item.get("pet_name") and item["pet_name"] != "All" else "🐾 All Pets"
                    rec_badge_text = f"🔄 {item['recurrence'].capitalize()}" if item.get("recurrence") and item["recurrence"] != "none" else ""
                    rec_badge_html = f"<span>{rec_badge_text}</span>" if rec_badge_text else ""
                    
                    card_html = (
                        f'<div class="timeline-item {time_class}">'
                        f'<div class="time-slot">⏱️ {item["start_time"]} - {item["end_time"]}</div>'
                        f'<div class="task-details">'
                        f'<p class="task-title">{icon} {item["title"]}</p>'
                        f'<div class="task-meta">'
                        f'<span>⏳ {item["duration_minutes"]} mins</span>'
                        f'<span>📂 {item["category"].capitalize()}</span>'
                        f'<span class="badge badge-{p_name}">{item["priority"]} Priority</span>'
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
            
            # Display Reasoning
            st.markdown("### 🧠 Scheduling Engine Reasoning")
            st.markdown(f'<div class="reason-box">{reasoning}</div>', unsafe_allow_html=True)
    else:
        # Initial call-to-action placeholder
        st.info(f"Click the 'Generate Daily Schedule' button above to plan {st.session_state.pet.name}'s day based on your available time constraints.")
