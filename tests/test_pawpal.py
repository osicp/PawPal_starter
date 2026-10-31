import pytest
from pawpal_system import Owner, Pet, Task, Scheduler, Priority, TimeOfDay

def test_owner_pet_creation():
    owner = Owner(name="Alice", available_time_minutes=60, preferences={"outdoor_only": True})
    pet = Pet(name="Biscuit", species="Dog", breed="Golden Retriever", age=3, owner=owner)

    assert pet.name == "Biscuit"
    assert pet.owner.name == "Alice"
    assert "Alice" in owner.get_owner_details()
    assert "Biscuit" in pet.get_profile()

def test_priority_timeofday_from_str():
    assert Priority.from_str("high") == Priority.HIGH
    assert Priority.from_str(" MEDIUM ") == Priority.MEDIUM
    assert Priority.from_str("low") == Priority.LOW
    with pytest.raises(ValueError):
        Priority.from_str("invalid")

    assert TimeOfDay.from_str("morning") == TimeOfDay.MORNING
    assert TimeOfDay.from_str(" afternoon ") == TimeOfDay.AFTERNOON
    assert TimeOfDay.from_str("evening") == TimeOfDay.EVENING
    assert TimeOfDay.from_str("any") == TimeOfDay.ANY
    with pytest.raises(ValueError):
        TimeOfDay.from_str("invalid")

def test_task_status_update():
    task = Task(title="Morning feeding", duration_minutes=10, priority=Priority.HIGH, category="Feeding")
    assert not task.is_completed
    task.update_status(True)
    assert task.is_completed

def test_scheduler_task_addition():
    owner = Owner(name="Charlie", available_time_minutes=60)
    pet = Pet(name="Biscuit", species="Dog", breed="Poodle", age=4, owner=owner)
    scheduler = Scheduler(pet=pet, tasks=[])
    
    assert len(scheduler.tasks) == 0
    new_task = Task(title="Walk", duration_minutes=20, priority=Priority.HIGH, category="walk")
    scheduler.add_task(new_task)
    assert len(scheduler.tasks) == 1
    assert scheduler.tasks[0] == new_task

def test_scheduler_greedy_time_constraint():

    # Owner has 60 minutes available
    owner = Owner(name="Bob", available_time_minutes=60)
    pet = Pet(name="Mochi", species="Cat", breed="Ragdoll", age=2, owner=owner)

    # 4 tasks totaling 100 minutes. 
    # High Priority: Walk (30 min)
    # High Priority: Feed (15 min)
    # Medium Priority: Grooming (30 min) -> should be skipped because 30+15+30 = 75 > 60
    # Low Priority: Play (25 min) -> should also be skipped
    tasks = [
        Task(title="Grooming", duration_minutes=30, priority=Priority.MEDIUM, category="grooming", time_of_day=TimeOfDay.AFTERNOON),
        Task(title="Walk", duration_minutes=30, priority=Priority.HIGH, category="walk", time_of_day=TimeOfDay.MORNING),
        Task(title="Feed", duration_minutes=15, priority=Priority.HIGH, category="feeding", time_of_day=TimeOfDay.MORNING),
        Task(title="Play", duration_minutes=25, priority=Priority.LOW, category="enrichment", time_of_day=TimeOfDay.ANY),
    ]

    scheduler = Scheduler(pet=pet, tasks=tasks)
    plan = scheduler.generate_plan()

    # The scheduled tasks should be Walk and Feed (total 45 mins).
    scheduled_titles = [item["title"] for item in plan]
    assert "Walk" in scheduled_titles
    assert "Feed" in scheduled_titles
    assert "Grooming" not in scheduled_titles
    assert "Play" not in scheduled_titles

    # Verify times assigned
    # Walk starts at 8:00 AM (480 mins) and ends at 8:30 (510 mins)
    # Feed starts at 8:30 AM (510 mins) and ends at 8:45 (525 mins)
    walk_item = next(item for item in plan if item["title"] == "Walk")
    feed_item = next(item for item in plan if item["title"] == "Feed")
    
    assert walk_item["start_time"] == "08:00"
    assert walk_item["end_time"] == "08:30"
    assert feed_item["start_time"] == "08:30"
    assert feed_item["end_time"] == "08:45"

    # Verify reasoning contains explanations for scheduled and skipped tasks
    reasoning = scheduler.get_reasoning()
    assert "Scheduled 'Walk'" in reasoning
    assert "Scheduled 'Feed'" in reasoning
    assert "Skipped 'Grooming'" in reasoning
    assert "Skipped 'Play'" in reasoning
    assert "45 / 60 available minutes" in reasoning

def test_task_time_parsing():
    # Valid times
    t1 = Task(title="Test 1", duration_minutes=30, priority=Priority.HIGH, category="walk", specific_time="08:30")
    assert t1.get_start_minutes() == 510
    assert t1.get_end_minutes() == 540

    t2 = Task(title="Test 2", duration_minutes=15, priority=Priority.HIGH, category="walk", specific_time="23:59")
    assert t2.get_start_minutes() == 1439
    assert t2.get_end_minutes() == 1454

    # Invalid times
    t3 = Task(title="Test 3", duration_minutes=10, priority=Priority.MEDIUM, category="walk", specific_time="invalid")
    assert t3.get_start_minutes() is None
    assert t3.get_end_minutes() is None

    t4 = Task(title="Test 4", duration_minutes=10, priority=Priority.MEDIUM, category="walk", specific_time=None)
    assert t4.get_start_minutes() is None

    t5 = Task(title="Test 5", duration_minutes=10, priority=Priority.MEDIUM, category="walk", specific_time="25:00")
    assert t5.get_start_minutes() is None

def test_conflict_detection():
    owner = Owner(name="Jordan", available_time_minutes=60)
    pet = Pet(name="Mochi", species="Cat", breed="Ragdoll", age=2, owner=owner)
    
    # Overlapping tasks
    t1 = Task(title="Walk A", duration_minutes=30, priority=Priority.HIGH, category="walk", specific_time="08:00")
    t2 = Task(title="Feed B", duration_minutes=15, priority=Priority.HIGH, category="feeding", specific_time="08:15") # overlap [480, 510] and [495, 510]
    t3 = Task(title="Play C", duration_minutes=10, priority=Priority.LOW, category="enrichment", specific_time="09:00") # no overlap
    
    scheduler = Scheduler(pet=pet, tasks=[t1, t2, t3])
    conflicts = scheduler.detect_conflicts()
    
    assert len(conflicts) == 1
    assert conflicts[0]["task1"] == t1
    assert conflicts[0]["task2"] == t2
    assert "Walk A" in conflicts[0]["message"]
    assert "Feed B" in conflicts[0]["message"]

def test_filtering_by_pet_and_status():
    owner = Owner(name="Jordan", available_time_minutes=120)
    pet = Pet(name="Mochi", species="Cat", breed="Ragdoll", age=2, owner=owner)
    
    tasks = [
        Task(title="Mochi Meds", duration_minutes=10, priority=Priority.HIGH, category="meds", pet_name="Mochi", is_completed=False),
        Task(title="Biscuit Walk", duration_minutes=30, priority=Priority.HIGH, category="walk", pet_name="Biscuit", is_completed=False),
        Task(title="Mochi Brush", duration_minutes=15, priority=Priority.MEDIUM, category="grooming", pet_name="Mochi", is_completed=True),
        Task(title="All Feeding", duration_minutes=20, priority=Priority.HIGH, category="feeding", pet_name="All", is_completed=False),
    ]
    
    scheduler = Scheduler(pet=pet, tasks=tasks)
    
    # Test Pet Filter = "Mochi", Status Filter = "All"
    plan_mochi_all = scheduler.generate_plan(pet_filter="Mochi", status_filter="All")
    titles_mochi_all = [item["title"] for item in plan_mochi_all]
    assert "Mochi Meds" in titles_mochi_all
    assert "Mochi Brush" in titles_mochi_all
    assert "All Feeding" in titles_mochi_all # "All" shared tasks should be included
    assert "Biscuit Walk" not in titles_mochi_all
    
    # Test Pet Filter = "Mochi", Status Filter = "Pending"
    plan_mochi_pending = scheduler.generate_plan(pet_filter="Mochi", status_filter="Pending")
    titles_mochi_pending = [item["title"] for item in plan_mochi_pending]
    assert "Mochi Meds" in titles_mochi_pending
    assert "All Feeding" in titles_mochi_pending
    assert "Mochi Brush" not in titles_mochi_pending # Completed task filtered out

def test_interval_gap_filling():
    owner = Owner(name="Jordan", available_time_minutes=120)
    pet = Pet(name="Mochi", species="Cat", breed="Ragdoll", age=2, owner=owner)
    
    tasks = [
        # Fixed time task from 08:30 to 09:00 (510 to 540)
        Task(title="Fixed Meds", duration_minutes=30, priority=Priority.HIGH, category="meds", specific_time="08:30"),
        # Flexible morning task (08:00 to 12:00 / 480 to 720). Should fit in the gap 08:00 - 08:30 (480 - 510)
        Task(title="Morning Feeding", duration_minutes=30, priority=Priority.HIGH, category="feeding", time_of_day=TimeOfDay.MORNING),
        # Flexible morning task. Should fit after the fixed meds, starting at 09:00 (540)
        Task(title="Morning Grooming", duration_minutes=20, priority=Priority.MEDIUM, category="grooming", time_of_day=TimeOfDay.MORNING),
    ]
    
    scheduler = Scheduler(pet=pet, tasks=tasks)
    plan = scheduler.generate_plan()
    
    # Verify times assigned
    # Fixed Meds should start at 08:30 exactly
    meds_item = next(item for item in plan if item["title"] == "Fixed Meds")
    assert meds_item["start_time"] == "08:30"
    assert meds_item["end_time"] == "09:00"
    
    # Morning Feeding should start at 08:00 and end at 08:30
    feeding_item = next(item for item in plan if item["title"] == "Morning Feeding")
    assert feeding_item["start_time"] == "08:00"
    assert feeding_item["end_time"] == "08:30"
    
    # Morning Grooming should start at 09:00 and end at 09:20
    grooming_item = next(item for item in plan if item["title"] == "Morning Grooming")
    assert grooming_item["start_time"] == "09:00"
    assert grooming_item["end_time"] == "09:20"

def test_recurring_task_auto_spawning():
    import datetime
    owner = Owner(name="Jordan", available_time_minutes=60)
    pet = Pet(name="Mochi", species="Cat", breed="Ragdoll", age=2, owner=owner)
    
    # Create daily recurring task
    t_daily = Task(title="Daily Feed", duration_minutes=15, priority=Priority.HIGH, category="feeding", recurrence="daily")
    t_weekly = Task(title="Weekly Bath", duration_minutes=30, priority=Priority.MEDIUM, category="grooming", recurrence="weekly")
    t_none = Task(title="One-time Play", duration_minutes=10, priority=Priority.LOW, category="enrichment", recurrence="none")
    
    scheduler = Scheduler(pet=pet, tasks=[t_daily, t_weekly, t_none])
    
    # Mark t_daily complete
    new_daily = scheduler.mark_task_complete(t_daily)
    assert t_daily.is_completed
    assert new_daily is not None
    assert new_daily.title == "Daily Feed"
    assert not new_daily.is_completed
    # Check date calculation (today + 1 day)
    assert new_daily.due_date == datetime.date.today() + datetime.timedelta(days=1)
    # Check it was added to pool
    assert new_daily in scheduler.tasks
    
    # Mark t_weekly complete
    new_weekly = scheduler.mark_task_complete(t_weekly)
    assert t_weekly.is_completed
    assert new_weekly is not None
    assert new_weekly.due_date == datetime.date.today() + datetime.timedelta(weeks=1)
    assert new_weekly in scheduler.tasks
    
    # Mark t_none complete (should not spawn anything)
    new_none = scheduler.mark_task_complete(t_none)
    assert t_none.is_completed
    assert new_none is None

def test_sorting_correctness_suite():
    # Test sorting correctness on various list conditions, including empty lists, mixed types, and tie-breakers.
    owner = Owner(name="Jordan", available_time_minutes=120)
    pet = Pet(name="Mochi", species="Cat", breed="Ragdoll", age=2, owner=owner)
    
    # 1. Edge Case: Empty list sorting should return an empty list and not fail
    scheduler = Scheduler(pet=pet, tasks=[])
    assert scheduler.sort_tasks_by_time() == []

    # 2. Edge Case: Sorting mixed fixed and flexible tasks with priority tie-breakers
    t_flexible_low = Task(title="Flex Low", duration_minutes=10, priority=Priority.LOW, category="walk", time_of_day=TimeOfDay.AFTERNOON)
    t_fixed_late = Task(title="Fixed Late", duration_minutes=15, priority=Priority.HIGH, category="walk", specific_time="14:00")
    t_fixed_early = Task(title="Fixed Early", duration_minutes=20, priority=Priority.MEDIUM, category="walk", specific_time="08:30")
    t_flexible_high = Task(title="Flex High", duration_minutes=15, priority=Priority.HIGH, category="walk", time_of_day=TimeOfDay.MORNING)
    
    scheduler.tasks = [t_flexible_low, t_fixed_late, t_fixed_early, t_flexible_high]
    sorted_tasks = scheduler.sort_tasks_by_time()
    
    # Fixed-time tasks should appear first chronologically: Fixed Early (08:30) -> Fixed Late (14:00)
    # Next, flexible tasks: Flex High (Morning, High Priority) -> Flex Low (Afternoon, Low Priority)
    assert sorted_tasks[0] == t_fixed_early
    assert sorted_tasks[1] == t_fixed_late
    assert sorted_tasks[2] == t_flexible_high
    assert sorted_tasks[3] == t_flexible_low

    # 3. Edge Case: Tie-breaker on the same start time but different priorities
    t_fixed_high_priority = Task(title="High Priority", duration_minutes=10, priority=Priority.HIGH, category="meds", specific_time="10:00")
    t_fixed_medium_priority = Task(title="Medium Priority", duration_minutes=10, priority=Priority.MEDIUM, category="feeding", specific_time="10:00")
    
    scheduler.tasks = [t_fixed_medium_priority, t_fixed_high_priority]
    sorted_tasks = scheduler.sort_tasks_by_time()
    assert sorted_tasks[0] == t_fixed_high_priority
    assert sorted_tasks[1] == t_fixed_medium_priority

def test_recurrence_logic_suite():
    # Test recurrence logic, verifying that transitioning to complete spawns a new task, while completing a completed task does not trigger duplication.
    owner = Owner(name="Jordan", available_time_minutes=60)
    pet = Pet(name="Mochi", species="Cat", breed="Ragdoll", age=2, owner=owner)
    
    # 1. Edge Case: Toggling completion status on a completed recurring task should not spawn another task instance
    t_daily = Task(title="Daily Feeding", duration_minutes=10, priority=Priority.HIGH, category="feeding", recurrence="daily")
    scheduler = Scheduler(pet=pet, tasks=[t_daily])
    
    # Complete the task first time -> should spawn next occurrence
    new_occurrence = scheduler.mark_task_complete(t_daily)
    assert new_occurrence is not None
    assert len(scheduler.tasks) == 2
    
    # Complete it again while it's already complete -> should NOT spawn any additional task
    duplicate_check = scheduler.mark_task_complete(t_daily)
    assert duplicate_check is None
    assert len(scheduler.tasks) == 2
    
    # 2. Date arithmetic edge cases: Verify base date rollover
    import datetime
    custom_date = datetime.date(2026, 12, 31) # End of year rollover test
    t_rollover = Task(title="Year End Feed", duration_minutes=10, priority=Priority.HIGH, category="feeding", recurrence="daily", due_date=custom_date)
    scheduler.tasks = [t_rollover]
    
    next_occurrence = scheduler.mark_task_complete(t_rollover)
    assert next_occurrence is not None
    # End of year roll-over check: 2026-12-31 + 1 day = 2027-01-01
    assert next_occurrence.due_date == datetime.date(2027, 1, 1)

def test_conflict_detection_suite():
    # Test conflict detection, covering full overlaps, touch-point overlaps (boundaries), and clean schedules.
    owner = Owner(name="Jordan", available_time_minutes=60)
    pet = Pet(name="Mochi", species="Cat", breed="Ragdoll", age=2, owner=owner)
    scheduler = Scheduler(pet=pet, tasks=[])
    
    # 1. Edge Case: Touch-point boundaries (Task A ends at 08:30, Task B starts at 08:30). Should NOT conflict.
    t_a = Task(title="Walk A", duration_minutes=30, priority=Priority.HIGH, category="walk", specific_time="08:00") # 08:00 - 08:30
    t_b = Task(title="Feed B", duration_minutes=15, priority=Priority.MEDIUM, category="feeding", specific_time="08:30") # 08:30 - 08:45
    scheduler.tasks = [t_a, t_b]
    assert len(scheduler.detect_conflicts()) == 0
    
    # 2. Edge Case: Partial overlap (Task B starts 1 minute before Task A ends)
    t_c = Task(title="Play C", duration_minutes=20, priority=Priority.LOW, category="enrichment", specific_time="08:29") # 08:29 - 08:49 (overlaps A)
    scheduler.tasks = [t_a, t_c]
    conflicts = scheduler.detect_conflicts()
    assert len(conflicts) == 1
    assert conflicts[0]["task1"] == t_a
    assert conflicts[0]["task2"] == t_c
    
    # 3. Edge Case: Nested overlap (Task D is fully inside Task A)
    t_d = Task(title="Meds D", duration_minutes=10, priority=Priority.HIGH, category="meds", specific_time="08:10") # 08:10 - 08:20
    scheduler.tasks = [t_a, t_d]
    conflicts_nested = scheduler.detect_conflicts()
    assert len(conflicts_nested) == 1
    assert conflicts_nested[0]["task1"] == t_a
    assert conflicts_nested[0]["task2"] == t_d

def test_zero_and_constrained_budget_edge_cases():
    """Verify scheduler behavior under zero and ultra-constrained budget limits."""
    owner_zero = Owner(name="Sam", available_time_minutes=0)
    pet = Pet(name="Mochi", species="Cat", breed="Ragdoll", age=2, owner=owner_zero)
    task = Task(title="Walk", duration_minutes=30, priority=Priority.HIGH, category="walk")
    
    # 1. Zero budget
    scheduler_zero = Scheduler(pet=pet, tasks=[task])
    assert scheduler_zero.generate_plan() == []
    reasoning_zero = scheduler_zero.get_reasoning()
    assert "utilizing 0 / 0 available minutes" in reasoning_zero
    assert "exceeds the remaining available care time of 0 minutes" in reasoning_zero
    
    # 2. Budget smaller than single task (e.g., 10 mins available, task is 30 mins)
    owner_tight = Owner(name="Sam", available_time_minutes=10)
    pet.owner = owner_tight
    scheduler_tight = Scheduler(pet=pet, tasks=[task])
    assert scheduler_tight.generate_plan() == []
    assert "exceeds the remaining available care time of 10 minutes" in scheduler_tight.get_reasoning()

def test_time_fragmentation_edge_case():
    """Verify that small flexible tasks fill fragmented intervals while larger tasks skip to larger slots."""
    owner = Owner(name="Jordan", available_time_minutes=180)
    pet = Pet(name="Mochi", species="Cat", breed="Ragdoll", age=2, owner=owner)
    
    # Set up fixed appointments creating a 15-minute fragmented gap (09:00 - 09:15)
    t_b0 = Task(title="Block 0", duration_minutes=30, priority=Priority.HIGH, category="meds", specific_time="08:00")
    t_b1 = Task(title="Block 1", duration_minutes=30, priority=Priority.HIGH, category="meds", specific_time="08:30")
    t_b2 = Task(title="Block 2", duration_minutes=30, priority=Priority.HIGH, category="meds", specific_time="09:15")
    
    # A 20-minute task cannot fit into 09:00 - 09:15, so it skips to 09:45
    t_20m = Task(title="Task 20m", duration_minutes=20, priority=Priority.HIGH, category="enrichment", time_of_day=TimeOfDay.MORNING)
    # A 15-minute task CAN fit into 09:00 - 09:15
    t_15m = Task(title="Task 15m", duration_minutes=15, priority=Priority.MEDIUM, category="grooming", time_of_day=TimeOfDay.MORNING)
    
    scheduler = Scheduler(pet=pet, tasks=[t_b0, t_b1, t_b2, t_20m, t_15m])
    plan = scheduler.generate_plan()
    
    item_15m = next(i for i in plan if i["title"] == "Task 15m")
    item_20m = next(i for i in plan if i["title"] == "Task 20m")
    
    # 15m task must fit into the fragmented 09:00 - 09:15 gap
    assert item_15m["start_time"] == "09:00"
    assert item_15m["end_time"] == "09:15"
    
    # 20m task must skip the 15m fragment and be scheduled at 09:45 - 10:05
    assert item_20m["start_time"] == "09:45"
    assert item_20m["end_time"] == "10:05"

def test_fallback_window_edge_case():
    """Verify fallback from preferred time window to ANY daytime window, and skip on fully blocked days."""
    owner = Owner(name="Jordan", available_time_minutes=300)
    pet = Pet(name="Mochi", species="Cat", breed="Ragdoll", age=2, owner=owner)
    
    # Block the entire morning window (08:00 - 12:00 = 240 mins) with a fixed task
    t_morning_block = Task(title="Morning Vet", duration_minutes=240, priority=Priority.HIGH, category="meds", specific_time="08:00")
    # Morning-preferred task that cannot fit in Morning, but can fit in Afternoon fallback
    t_morning_flex = Task(title="Morning Feeding", duration_minutes=30, priority=Priority.HIGH, category="feeding", time_of_day=TimeOfDay.MORNING)
    
    scheduler = Scheduler(pet=pet, tasks=[t_morning_block, t_morning_flex])
    plan = scheduler.generate_plan()
    
    feed_item = next(i for i in plan if i["title"] == "Morning Feeding")
    assert feed_item["start_time"] == "12:00"
    assert feed_item["end_time"] == "12:30"
    assert "could not fit in preferred morning window; scheduled in fallback slot" in scheduler.get_reasoning()
    
    # Case where even the fallback window is completely blocked (08:00 - 22:00 = 840 min)
    pet.owner = Owner(name="Jordan", available_time_minutes=900)
    t_all_day = Task(title="All Day Stay", duration_minutes=840, priority=Priority.HIGH, category="meds", specific_time="08:00")
    t_flex_blocked = Task(title="Evening Walk", duration_minutes=30, priority=Priority.HIGH, category="walk", time_of_day=TimeOfDay.EVENING)
    
    scheduler_block = Scheduler(pet=pet, tasks=[t_all_day, t_flex_blocked])
    plan_block = scheduler_block.generate_plan()
    assert len(plan_block) == 1
    assert "no available time gap was found during its preferred window" in scheduler_block.get_reasoning()

