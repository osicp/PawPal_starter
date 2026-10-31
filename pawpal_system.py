from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Union
from enum import Enum
from datetime import date, timedelta
import json
import os
from pathlib import Path

class Priority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3

    @classmethod
    def from_str(cls, val: Any) -> "Priority":
        if isinstance(val, cls):
            return val
        if not isinstance(val, str):
            raise ValueError(f"Invalid priority: {val}. Must be a string or Priority enum.")
        val_upper = val.strip().upper()
        if val_upper == "LOW":
            return cls.LOW
        elif val_upper == "MEDIUM":
            return cls.MEDIUM
        elif val_upper == "HIGH":
            return cls.HIGH
        raise ValueError(f"Invalid priority: {val}. Must be 'low', 'medium', or 'high'.")

class TimeOfDay(Enum):
    MORNING = "morning"
    AFTERNOON = "afternoon"
    EVENING = "evening"
    ANY = "any"

    @classmethod
    def from_str(cls, val: Any) -> "TimeOfDay":
        if isinstance(val, cls):
            return val
        if not isinstance(val, str):
            raise ValueError(f"Invalid time of day: {val}. Must be a string or TimeOfDay enum.")
        val_lower = val.strip().lower()
        for member in cls:
            if member.value == val_lower:
                return member
        raise ValueError(f"Invalid time of day: {val}. Must be 'morning', 'afternoon', 'evening', or 'any'.")

# Preferred scheduling windows in minutes from midnight (start_minute, end_minute)
TIME_WINDOWS: Dict[TimeOfDay, tuple] = {
    TimeOfDay.MORNING: (8 * 60, 12 * 60),      # 08:00 - 12:00
    TimeOfDay.AFTERNOON: (12 * 60, 17 * 60),   # 12:00 - 17:00
    TimeOfDay.EVENING: (17 * 60, 22 * 60),     # 17:00 - 22:00
    TimeOfDay.ANY: (8 * 60, 22 * 60)           # 08:00 - 22:00
}

# Default category importance weights for multi-factor utility scoring
DEFAULT_CATEGORY_WEIGHTS: Dict[str, float] = {
    "meds": 3.5,        # Critical health and life preservation
    "feeding": 3.0,     # Essential daily nutrition
    "walk": 2.5,        # Exercise, biological relief, and mental health
    "enrichment": 2.0,  # Play and cognitive stimulation
    "grooming": 1.5,    # Hygiene and coat care
    "other": 1.0        # General care activities
}

# Habit consistency bonuses for recurring routines
DEFAULT_RECURRENCE_BONUS: Dict[str, float] = {
    "daily": 0.5,
    "weekly": 0.2,
    "none": 0.0
}

@dataclass
class Owner:
    name: str
    available_time_minutes: int
    preferences: Dict[str, Any] = field(default_factory=dict)

    def get_owner_details(self) -> str:
        """Returns a string summary of the owner's profile and constraints."""
        pref_str = ", ".join(f"{k}: {v}" for k, v in self.preferences.items()) if self.preferences else "None"
        return f"Owner: {self.name} | Available Time: {self.available_time_minutes} mins | Preferences: {pref_str}"

    def to_dict(self) -> Dict[str, Any]:
        """Serializes Owner to a JSON-compatible dictionary."""
        return {
            "name": self.name,
            "available_time_minutes": self.available_time_minutes,
            "preferences": self.preferences
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Owner":
        """Deserializes a dictionary into an Owner instance with safe defaults."""
        return cls(
            name=str(data.get("name", "Caregiver")),
            available_time_minutes=int(data.get("available_time_minutes", 60)),
            preferences=dict(data.get("preferences", {})) if isinstance(data.get("preferences"), dict) else {}
        )

@dataclass
class Pet:
    name: str
    species: str
    breed: str
    age: int
    owner: Owner

    def get_profile(self) -> str:
        """Returns a string profile of the pet."""
        return f"{self.name} ({self.age}yo {self.breed} {self.species}) - Owned by {self.owner.name}"

    def to_dict(self) -> Dict[str, Any]:
        """Serializes Pet to a JSON-compatible dictionary."""
        return {
            "name": self.name,
            "species": self.species,
            "breed": self.breed,
            "age": self.age
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any], owner: Owner) -> "Pet":
        """Deserializes a dictionary into a Pet instance with safe defaults."""
        return cls(
            name=str(data.get("name", "Pet")),
            species=str(data.get("species", "Cat")),
            breed=str(data.get("breed", "Mixed")),
            age=int(data.get("age", 1)),
            owner=owner
        )

@dataclass
class Task:
    title: str
    duration_minutes: int
    priority: Priority
    category: str
    time_of_day: TimeOfDay = TimeOfDay.ANY
    is_completed: bool = False
    specific_time: Optional[str] = None  # Format "HH:MM", e.g., "08:30"
    pet_name: str = "All"
    recurrence: str = "none"             # "none", "daily", "weekly"
    due_date: Optional[date] = None

    def __post_init__(self):
        if self.duration_minutes <= 0:
            raise ValueError(f"duration_minutes must be positive, got {self.duration_minutes}")
        if isinstance(self.recurrence, str):
            self.recurrence = self.recurrence.strip().lower()
        if self.recurrence not in ("none", "daily", "weekly"):
            raise ValueError(f"Invalid recurrence: '{self.recurrence}'. Must be 'none', 'daily', or 'weekly'.")
        if isinstance(self.pet_name, str):
            self.pet_name = self.pet_name.strip()

    def update_status(self, completed: bool) -> Optional['Task']:
        """
        Updates the completion status of the task. If a recurring task ("daily" or "weekly")
        is transitioned from incomplete to complete, this method automatically instantiates
        and returns a new pending Task instance representing the next scheduled occurrence.

        Args:
            completed (bool): The new completion status to set.

        Returns:
            Optional[Task]: A new Task instance for the next occurrence if the task is recurring
                            and has just been marked complete. Returns None otherwise.
        """
        was_completed = self.is_completed
        self.is_completed = completed
        
        if completed and not was_completed and self.recurrence in ("daily", "weekly"):
            # For overdue tasks, roll forward from today; for future tasks, preserve the future base date
            base_date = max(self.due_date, date.today()) if self.due_date else date.today()
            if self.recurrence == "daily":
                next_date = base_date + timedelta(days=1)
            else:  # weekly
                next_date = base_date + timedelta(weeks=1)
                
            return Task(
                title=self.title,
                duration_minutes=self.duration_minutes,
                priority=self.priority,
                category=self.category,
                time_of_day=self.time_of_day,
                is_completed=False,
                specific_time=self.specific_time,
                pet_name=self.pet_name,
                recurrence=self.recurrence,
                due_date=next_date
            )
        return None

    def get_start_minutes(self) -> Optional[int]:
        """Converts specific_time 'HH:MM' to minutes from midnight."""
        if not self.specific_time or not self.specific_time.strip():
            return None
        try:
            parts = self.specific_time.strip().split(":")
            if len(parts) != 2:
                return None
            hrs = int(parts[0])
            mins = int(parts[1])
            if 0 <= hrs < 24 and 0 <= mins < 60:
                return hrs * 60 + mins
        except Exception:
            pass
        return None

    def get_end_minutes(self) -> Optional[int]:
        """Returns end time in minutes from midnight if specific_time is set."""
        start = self.get_start_minutes()
        if start is None:
            return None
        return start + self.duration_minutes

    def calculate_utility_score(self, custom_weights: Optional[Dict[str, float]] = None) -> float:
        """
        Computes a composite multi-factor utility score for the task based on:
          1. Priority Value (High = 3.0, Medium = 2.0, Low = 1.0)
          2. Category Importance (Meds = 3.5, Feeding = 3.0, Walk = 2.5, etc.)
          3. Recurrence Habit Bonus (Daily = +0.5, Weekly = +0.2)
        Formula: (Priority * Category Weight) + Recurrence Bonus

        Args:
            custom_weights (Optional[Dict[str, float]]): Custom category importance overrides.

        Returns:
            float: Composite utility score rounded to 2 decimal places.
        """
        cat_weights = DEFAULT_CATEGORY_WEIGHTS.copy()
        if custom_weights:
            cat_weights.update(custom_weights)

        p_val = float(self.priority.value)
        c_val = cat_weights.get(self.category.strip().lower(), 1.0)
        r_bonus = DEFAULT_RECURRENCE_BONUS.get(self.recurrence.strip().lower(), 0.0)

        return round((p_val * c_val) + r_bonus, 2)

    def get_utility_density(self, custom_weights: Optional[Dict[str, float]] = None) -> float:
        """
        Calculates value density (utility points generated per minute of caregiver time):
            Utility Density = Utility Score / Duration in Minutes

        Args:
            custom_weights (Optional[Dict[str, float]]): Custom category importance overrides.

        Returns:
            float: Points per minute rounded to 3 decimal places.
        """
        score = self.calculate_utility_score(custom_weights)
        return round(score / max(self.duration_minutes, 1), 3)

    def to_dict(self) -> Dict[str, Any]:
        """Serializes the task to a JSON-compatible dictionary."""
        return {
            "title": self.title,
            "duration_minutes": self.duration_minutes,
            "priority": self.priority.name,
            "category": self.category,
            "time_of_day": self.time_of_day.value,
            "is_completed": self.is_completed,
            "specific_time": self.specific_time,
            "pet_name": self.pet_name,
            "recurrence": self.recurrence,
            "due_date": self.due_date.isoformat() if self.due_date else None
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Task":
        """
        Deserializes a dictionary into a Task instance with defensive fallbacks
        for missing fields or schema variations.
        """
        due_date_raw = data.get("due_date")
        parsed_due_date = None
        if due_date_raw:
            try:
                parsed_due_date = date.fromisoformat(due_date_raw)
            except Exception:
                parsed_due_date = None

        return cls(
            title=str(data.get("title", "Untitled Task")),
            duration_minutes=int(data.get("duration_minutes", 15)),
            priority=Priority.from_str(data.get("priority", "medium")),
            category=str(data.get("category", "other")),
            time_of_day=TimeOfDay.from_str(data.get("time_of_day", "any")),
            is_completed=bool(data.get("is_completed", False)),
            specific_time=data.get("specific_time"),
            pet_name=str(data.get("pet_name", "All")),
            recurrence=str(data.get("recurrence", "none")),
            due_date=parsed_due_date
        )

class Scheduler:
    def __init__(self, pet: Pet, tasks: List[Task]):
        self.pet: Pet = pet
        self.owner: Owner = pet.owner
        self.tasks: List[Task] = tasks
        self.plan: List[Dict[str, Any]] = []
        self.reasoning: str = ""

    def add_task(self, task: Task) -> None:
        """Adds a task to the scheduler's list of tasks."""
        self.tasks.append(task)

    def mark_task_complete(self, task: Task) -> Optional[Task]:
        """
        Marks a task complete within the scheduler. If the task is configured as a daily
        or weekly recurring task, it automatically spawns the next pending occurrence
        and registers it into the scheduler's internal task pool.

        Args:
            task (Task): The task to mark complete.

        Returns:
            Optional[Task]: The newly created Task instance for the next occurrence if recurring,
                            or None if the task is non-recurring.
        """
        new_task = task.update_status(True)
        if new_task:
            self.add_task(new_task)
        return new_task

    def _format_time(self, minutes: int) -> str:
        hrs = (minutes // 60) % 24
        mins = minutes % 60
        return f"{hrs:02d}:{mins:02d}"

    def detect_conflicts(self, tasks: Optional[List[Task]] = None, include_completed: bool = True) -> List[Dict[str, Any]]:
        """
        Scans a list of tasks for time slot conflicts. A conflict is defined as two tasks having
        overlapping specific time windows (e.g., trying to do two tasks at once).

        Args:
            tasks (Optional[List[Task]]): The list of tasks to scan. Defaults to the scheduler's internal list.
            include_completed (bool): Whether to include completed tasks in conflict checks (default: True).

        Returns:
            List[Dict[str, Any]]: A list of conflict descriptions, each specifying the conflicting
                                  tasks and a descriptive message.
        """
        target_tasks = tasks if tasks is not None else self.tasks
        if not include_completed:
            target_tasks = [t for t in target_tasks if not t.is_completed]
        fixed_tasks = [t for t in target_tasks if t.get_start_minutes() is not None]
        
        # Sort them by start time
        fixed_tasks = sorted(fixed_tasks, key=lambda t: t.get_start_minutes())
        
        conflicts = []
        for i in range(len(fixed_tasks)):
            t1 = fixed_tasks[i]
            s1 = t1.get_start_minutes()
            e1 = t1.get_end_minutes()
            for j in range(i + 1, len(fixed_tasks)):
                t2 = fixed_tasks[j]
                s2 = t2.get_start_minutes()
                e2 = t2.get_end_minutes()
                
                # Since fixed_tasks is sorted by start time, if t2 starts at or after t1 ends,
                # no subsequent task can overlap with t1
                if s2 >= e1:
                    break
                
                # Overlap check
                if s1 < e2 and s2 < e1:
                    conflicts.append({
                        "task1": t1,
                        "task2": t2,
                        "message": f"Conflict: '{t1.title}' ({t1.specific_time}) overlaps with '{t2.title}' ({t2.specific_time})"
                    })
        return conflicts

    def filter_tasks(self, pet_filter: str = "All", status_filter: str = "All", tasks: Optional[List[Task]] = None) -> List[Task]:
        """
        Filters a list of tasks by pet ownership (matching the pet name or shared 'All' tasks)
        and completion status.

        Args:
            pet_filter (str): Pet name filter (e.g. "Mochi"). If "All" or "All Pets", no pet filter is applied.
                              If "All (Shared)" or "Shared", only shared tasks are included.
            status_filter (str): Completion status filter ("All", "Pending", or "Completed", case-insensitive).
            tasks (Optional[List[Task]]): The list of tasks to filter. Defaults to the scheduler's internal list.

        Returns:
            List[Task]: A filtered copy of the list of tasks.
        """
        target_tasks = tasks if tasks is not None else self.tasks
        norm_pet = pet_filter.strip().lower()
        norm_status = status_filter.strip().lower()
        filtered = []
        for t in target_tasks:
            # Pet name filter
            if norm_pet in ("all (shared)", "shared"):
                if t.pet_name.lower() != "all":
                    continue
            elif norm_pet not in ("all", "all pets"):
                if t.pet_name.lower() != "all" and t.pet_name.lower() != norm_pet:
                    continue

            # Status filter
            if norm_status == "pending" and t.is_completed:
                continue
            elif norm_status == "completed" and not t.is_completed:
                continue
            filtered.append(t)
        return filtered

    def sort_tasks_by_time(
        self,
        tasks: Optional[List[Task]] = None,
        by_utility: bool = False,
        custom_weights: Optional[Dict[str, float]] = None
    ) -> List[Task]:
        """
        Sorts tasks chronologically by start time. Fixed-time tasks (those with specific start times)
        are placed first. Flexible tasks are ordered:
          - If by_utility=False (default): By preferred TimeOfDay window and then by priority descending.
          - If by_utility=True: By utility density descending, then utility score descending, then window.

        Args:
            tasks (Optional[List[Task]]): The list of tasks to sort. Defaults to the scheduler's internal list.
            by_utility (bool): Whether to rank flexible tasks by weighted utility density.
            custom_weights (Optional[Dict[str, float]]): Custom category weights for utility scoring.

        Returns:
            List[Task]: A sorted copy of the tasks list.
        """
        target_tasks = tasks if tasks is not None else self.tasks
        
        def get_time_of_day_order(t: Task) -> int:
            order = {
                TimeOfDay.MORNING: 0,
                TimeOfDay.AFTERNOON: 1,
                TimeOfDay.EVENING: 2,
                TimeOfDay.ANY: 3
            }
            return order.get(t.time_of_day, 4)

        # Sort key:
        # 1. Has specific time (0) vs. does not (1)
        # 2. Start time in minutes (if it exists)
        # 3. For flexible tasks:
        #    - If by_utility: (-density, -score, window_order)
        #    - If priority: (window_order, -priority.value)
        def sort_key(t: Task):
            start_min = t.get_start_minutes()
            if start_min is not None:
                return (0, start_min, 0, -t.priority.value)
            elif by_utility:
                return (1, -t.get_utility_density(custom_weights), -t.calculate_utility_score(custom_weights), get_time_of_day_order(t))
            else:
                return (1, 0, get_time_of_day_order(t), -t.priority.value)

        return sorted(target_tasks, key=sort_key)

    # CORE EXECUTION ENGINE
    def generate_plan(
        self,
        pet_filter: str = "All",
        status_filter: str = "All",
        strategy: str = "priority_greedy",
        custom_weights: Optional[Dict[str, float]] = None
    ) -> List[Dict[str, Any]]:
        """
        Generates a daily schedule based on priority, specific times, category necessity, and time constraints.

        Strategies:
          - "priority_greedy" (default): Standard greedy constraint-aware packing ordered by Priority (High -> Med -> Low).
          - "weighted_utility": Multi-factor utility ranking based on Priority, Category necessity, Recurrence, and Value Density.
          - "optimal_knapsack": 0/1 Knapsack dynamic programming selecting the global maximum utility bundle within available time.

        Args:
            pet_filter (str): Pet filter ("All", "All Pets", "All (Shared)", or pet name).
            status_filter (str): Task completion status filter ("All", "Pending", or "Completed").
            strategy (str): Scheduling strategy ("priority_greedy", "weighted_utility", or "optimal_knapsack").
            custom_weights (Optional[Dict[str, float]]): Custom category importance overrides.

        Returns:
            List[Dict[str, Any]]: Chronologically sorted list of scheduled care items.
        """
        self.plan = []
        reason_steps = []
        strategy_clean = strategy.strip().lower()

        total_time_limit = self.owner.available_time_minutes
        current_used_time = 0

        # Apply filtering
        filtered_tasks = self.filter_tasks(pet_filter=pet_filter, status_filter=status_filter)

        # Separate fixed-time tasks and flexible tasks
        fixed_tasks = [t for t in filtered_tasks if t.get_start_minutes() is not None]
        flexible_tasks = [t for t in filtered_tasks if t.get_start_minutes() is None]

        # Sort fixed-time tasks chronologically, using priority descending as tiebreaker
        fixed_tasks.sort(key=lambda t: (t.get_start_minutes(), -t.priority.value))

        def get_time_of_day_order(t: Task) -> int:
            order = {
                TimeOfDay.MORNING: 0,
                TimeOfDay.AFTERNOON: 1,
                TimeOfDay.EVENING: 2,
                TimeOfDay.ANY: 3
            }
            return order.get(t.time_of_day, 4)

        target_entity = (
            "all pets" if pet_filter.strip().lower() in ("all", "all pets")
            else "shared tasks" if pet_filter.strip().lower() in ("all (shared)", "shared")
            else pet_filter if pet_filter.strip().lower() != self.pet.name.lower()
            else self.pet.name
        )

        if strategy_clean == "priority_greedy":
            reason_steps.append(f"Starting schedule generation for {target_entity} (Filter: Pet={pet_filter}, Status={status_filter}).")
        else:
            strat_label = strategy_clean.replace("_", " ").title()
            reason_steps.append(f"Starting schedule generation for {target_entity} using Strategy: {strat_label} (Filter: Pet={pet_filter}, Status={status_filter}).")

        reason_steps.append(f"Owner {self.owner.name} has {total_time_limit} minutes available.")
        reason_steps.append(f"Analyzing {len(filtered_tasks)} filtered tasks ({len(fixed_tasks)} fixed-time, {len(flexible_tasks)} flexible).")

        # Keep track of scheduled intervals: (start_minutes, end_minutes, task)
        scheduled_intervals = []

        # 1. Schedule fixed-time tasks first
        for task in fixed_tasks:
            start_min = task.get_start_minutes()
            end_min = task.get_end_minutes()
            remaining_time = total_time_limit - current_used_time

            if task.duration_minutes > remaining_time:
                reason_steps.append(
                    f"❌ Skipped '{task.title}' (Priority: {task.priority.name}, Duration: {task.duration_minutes} min, Time: {task.specific_time}) "
                    f"because it exceeds the remaining available care time of {remaining_time} minutes."
                )
                continue

            # Check overlap with already scheduled intervals
            overlap = False
            for s, e, other_task in scheduled_intervals:
                if start_min < e and s < end_min:
                    overlap = True
                    reason_steps.append(
                        f"❌ Conflict: Skipped '{task.title}' ({task.specific_time}) because it overlaps with "
                        f"'{other_task.title}' ({self._format_time(s)} - {self._format_time(e)})."
                    )
                    break

            if not overlap:
                scheduled_intervals.append((start_min, end_min, task))
                current_used_time += task.duration_minutes
                u_score = task.calculate_utility_score(custom_weights)
                u_density = task.get_utility_density(custom_weights)

                self.plan.append({
                    "title": task.title,
                    "category": task.category,
                    "duration_minutes": task.duration_minutes,
                    "priority": task.priority.name,
                    "time_of_day": task.time_of_day.value,
                    "start_time": self._format_time(start_min),
                    "end_time": self._format_time(end_min),
                    "start_minutes": start_min,
                    "pet_name": task.pet_name,
                    "recurrence": task.recurrence,
                    "is_completed": task.is_completed,
                    "utility_score": u_score,
                    "utility_density": u_density
                })
                reason_steps.append(
                    f"✅ Scheduled Fixed-Time '{task.title}' (Priority: {task.priority.name}, Duration: {task.duration_minutes} min) "
                    f"at {self._format_time(start_min)} - {self._format_time(end_min)}."
                )

        # Helper to find first available gap in a window
        def find_gap(window_start: int, window_end: int, duration: int, scheduled: List[tuple]) -> Optional[int]:
            sorted_sched = sorted(scheduled, key=lambda x: x[0])
            curr = window_start
            for s, e, _ in sorted_sched:
                if s > curr:
                    gap_end = min(s, window_end)
                    if gap_end - curr >= duration:
                        return curr
                curr = max(curr, e)
                if curr >= window_end:
                    break
            if curr + duration <= window_end:
                return curr
            return None

        # 2. Select and rank flexible tasks according to chosen strategy
        remaining_budget = total_time_limit - current_used_time
        candidate_tasks = []

        if strategy_clean == "optimal_knapsack" and flexible_tasks and remaining_budget > 0:
            # 0/1 Knapsack Dynamic Programming: Maximize sum(utility) s.t. sum(duration) <= remaining_budget
            n = len(flexible_tasks)
            cap = max(0, remaining_budget)
            dp = [0.0] * (cap + 1)
            keep = [[False] * (cap + 1) for _ in range(n)]

            for i, t in enumerate(flexible_tasks):
                wt = t.duration_minutes
                val = t.calculate_utility_score(custom_weights)
                for w in range(cap, wt - 1, -1):
                    if dp[w - wt] + val > dp[w]:
                        dp[w] = dp[w - wt] + val
                        keep[i][w] = True

            # Reconstruct selected optimal task subset
            knapsack_selected = []
            curr_w = cap
            for i in range(n - 1, -1, -1):
                if keep[i][curr_w]:
                    knapsack_selected.append(flexible_tasks[i])
                    curr_w -= flexible_tasks[i].duration_minutes
            knapsack_selected_ids = {id(t) for t in knapsack_selected}

            # Log unselected tasks
            for t in flexible_tasks:
                if id(t) not in knapsack_selected_ids:
                    reason_steps.append(
                        f"❌ Excluded '{t.title}' (Utility: {t.calculate_utility_score(custom_weights)}, {t.duration_minutes}m) "
                        f"in favor of higher cumulative utility bundle."
                    )

            # Order selected knapsack tasks by utility density descending for interval placement
            candidate_tasks = sorted(
                knapsack_selected,
                key=lambda t: (t.get_utility_density(custom_weights), -get_time_of_day_order(t)),
                reverse=True
            )
            reason_steps.append(f"0/1 Knapsack identified {len(candidate_tasks)} optimal tasks maximizing care utility ({dp[cap]:.1f} pts).")

        elif strategy_clean == "weighted_utility":
            # Multi-factor utility ranking: Value Density (Score / Duration), then raw score, then preferred window
            candidate_tasks = sorted(
                flexible_tasks,
                key=lambda t: (t.get_utility_density(custom_weights), t.calculate_utility_score(custom_weights), -get_time_of_day_order(t)),
                reverse=True
            )
            reason_steps.append("Ranked flexible tasks by Value Density (Score / Duration).")

        else:
            # Default "priority_greedy": Priority descending (HIGH -> MEDIUM -> LOW), then time of day ordering
            candidate_tasks = sorted(
                flexible_tasks,
                key=lambda t: (t.priority.value, -get_time_of_day_order(t)),
                reverse=True
            )

        # 3. Schedule candidate flexible tasks in available gaps
        for task in candidate_tasks:
            remaining_time = total_time_limit - current_used_time

            if task.duration_minutes > remaining_time:
                if strategy_clean == "priority_greedy":
                    reason_steps.append(
                        f"❌ Skipped '{task.title}' (Priority: {task.priority.name}, Duration: {task.duration_minutes} min) "
                        f"because it exceeds the remaining available care time of {remaining_time} minutes."
                    )
                else:
                    reason_steps.append(
                        f"❌ Skipped '{task.title}' (Utility: {task.calculate_utility_score(custom_weights)}, Duration: {task.duration_minutes} min) "
                        f"because it exceeds the remaining available care time of {remaining_time} minutes."
                    )
                continue

            # Determine preferred window
            w_start, w_end = TIME_WINDOWS.get(task.time_of_day, TIME_WINDOWS[TimeOfDay.ANY])

            gap_start = find_gap(w_start, w_end, task.duration_minutes, scheduled_intervals)

            # If not found and preferred window wasn't ANY, try ANY window as fallback
            if gap_start is None and task.time_of_day != TimeOfDay.ANY:
                any_start, any_end = TIME_WINDOWS[TimeOfDay.ANY]
                gap_start = find_gap(any_start, any_end, task.duration_minutes, scheduled_intervals)
                if gap_start is not None:
                    reason_steps.append(
                        f"ℹ️ Note: '{task.title}' could not fit in preferred {task.time_of_day.value} window; scheduled in fallback slot."
                    )

            if gap_start is not None:
                start_min = gap_start
                end_min = start_min + task.duration_minutes
                scheduled_intervals.append((start_min, end_min, task))
                current_used_time += task.duration_minutes

                u_score = task.calculate_utility_score(custom_weights)
                u_density = task.get_utility_density(custom_weights)

                self.plan.append({
                    "title": task.title,
                    "category": task.category,
                    "duration_minutes": task.duration_minutes,
                    "priority": task.priority.name,
                    "time_of_day": task.time_of_day.value,
                    "start_time": self._format_time(start_min),
                    "end_time": self._format_time(end_min),
                    "start_minutes": start_min,
                    "pet_name": task.pet_name,
                    "recurrence": task.recurrence,
                    "is_completed": task.is_completed,
                    "utility_score": u_score,
                    "utility_density": u_density
                })

                if strategy_clean == "priority_greedy":
                    reason_steps.append(
                        f"✅ Scheduled '{task.title}' (Priority: {task.priority.name}, Duration: {task.duration_minutes} min) "
                        f"at {self._format_time(start_min)} - {self._format_time(end_min)}."
                    )
                else:
                    reason_steps.append(
                        f"⭐ Scheduled '{task.title}' (Utility: {u_score}, Density: {u_density}/m, Duration: {task.duration_minutes}m) "
                        f"at {self._format_time(start_min)} - {self._format_time(end_min)}."
                    )
            else:
                fallback_note = " or fallback daytime hours" if task.time_of_day != TimeOfDay.ANY else ""
                if strategy_clean == "priority_greedy":
                    reason_steps.append(
                        f"❌ Skipped '{task.title}' (Priority: {task.priority.name}, Duration: {task.duration_minutes} min) "
                        f"because no available time gap was found during its preferred window{fallback_note}."
                    )
                else:
                    reason_steps.append(
                        f"❌ Skipped '{task.title}' (Utility: {task.calculate_utility_score(custom_weights)}, Duration: {task.duration_minutes} min) "
                        f"because no available time gap was found during its preferred window{fallback_note}."
                    )

        # Sort the final plan chronologically for display
        self.plan.sort(key=lambda item: item["start_minutes"])

        total_utility = sum(item.get("utility_score", 0.0) for item in self.plan)
        if strategy_clean == "priority_greedy":
            reason_steps.append(
                f"Schedule generation complete. Scheduled {len(self.plan)} tasks, "
                f"utilizing {current_used_time} / {total_time_limit} available minutes."
            )
        else:
            reason_steps.append(
                f"Schedule generation complete. Scheduled {len(self.plan)} tasks, "
                f"utilizing {current_used_time} / {total_time_limit} available minutes. "
                f"Total Care Utility Score: {total_utility:.1f} pts."
            )

        self.reasoning = "\n".join(reason_steps)
        return self.plan

    def get_reasoning(self) -> str:
        """Returns the explanation of how and why the schedule was generated."""
        return self.reasoning

    # PERSISTENCE & DATA STORAGE
    def save_to_json(self, file_path: Union[str, Path] = "data.json") -> bool:
        """
        Saves current owner, pet, and tasks pool to a JSON file using atomic writes.
        Atomic write pattern: writes to a temporary file first, flushes to disk, and
        atomically replaces the target file to prevent corruption during unexpected crashes.

        Args:
            file_path (Union[str, Path]): Destination file path (defaults to 'data.json').

        Returns:
            bool: True if saving succeeded, False otherwise.
        """
        target = Path(file_path)
        temp_target = target.with_suffix(f"{target.suffix}.tmp")
        payload = {
            "version": "1.0",
            "owner": self.owner.to_dict(),
            "pet": self.pet.to_dict(),
            "tasks": [t.to_dict() for t in self.tasks]
        }
        try:
            target.parent.mkdir(parents=True, exist_ok=True)
            with open(temp_target, "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2, ensure_ascii=False)
                f.flush()
                os.fsync(f.fileno())
            os.replace(temp_target, target)
            return True
        except Exception:
            if temp_target.exists():
                try:
                    temp_target.unlink()
                except Exception:
                    pass
            return False

    def load_from_json(self, file_path: Union[str, Path] = "data.json") -> bool:
        """
        Loads owner, pet, and tasks from a JSON file into this scheduler instance.
        Implements defensive fallbacks against missing files, corrupted JSON, and schema changes.

        Args:
            file_path (Union[str, Path]): Source file path (defaults to 'data.json').

        Returns:
            bool: True if loaded successfully, False if file was missing or corrupt.
        """
        target = Path(file_path)
        if not target.exists():
            return False

        try:
            with open(target, "r", encoding="utf-8") as f:
                data = json.load(f)

            if not isinstance(data, dict):
                return False

            if "owner" in data and isinstance(data["owner"], dict):
                loaded_owner = Owner.from_dict(data["owner"])
                self.owner.name = loaded_owner.name
                self.owner.available_time_minutes = loaded_owner.available_time_minutes
                self.owner.preferences = loaded_owner.preferences

            if "pet" in data and isinstance(data["pet"], dict):
                loaded_pet = Pet.from_dict(data["pet"], self.owner)
                self.pet.name = loaded_pet.name
                self.pet.species = loaded_pet.species
                self.pet.breed = loaded_pet.breed
                self.pet.age = loaded_pet.age
                self.pet.owner = self.owner

            if "tasks" in data and isinstance(data["tasks"], list):
                loaded_tasks = []
                for t_dict in data["tasks"]:
                    if isinstance(t_dict, dict):
                        try:
                            loaded_tasks.append(Task.from_dict(t_dict))
                        except Exception:
                            continue
                self.tasks = loaded_tasks

            return True
        except Exception:
            return False

    @classmethod
    def from_json(cls, file_path: Union[str, Path] = "data.json") -> Optional["Scheduler"]:
        """
        Instantiates and returns a new Scheduler instance loaded directly from a JSON file.

        Args:
            file_path (Union[str, Path]): Source file path (defaults to 'data.json').

        Returns:
            Optional[Scheduler]: A new Scheduler instance if loaded successfully, None otherwise.
        """
        target = Path(file_path)
        if not target.exists():
            return None
        try:
            with open(target, "r", encoding="utf-8") as f:
                data = json.load(f)
            if not isinstance(data, dict):
                return None
            owner = Owner.from_dict(data.get("owner", {}))
            pet = Pet.from_dict(data.get("pet", {}), owner)
            tasks = []
            for t in data.get("tasks", []):
                if isinstance(t, dict):
                    try:
                        tasks.append(Task.from_dict(t))
                    except Exception:
                        continue
            return cls(pet=pet, tasks=tasks)
        except Exception:
            return None