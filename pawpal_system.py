from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum
from datetime import date, timedelta

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

@dataclass
class Owner:
    name: str
    available_time_minutes: int
    preferences: Dict[str, Any] = field(default_factory=dict)

    def get_owner_details(self) -> str:
        """Returns a string summary of the owner's profile and constraints."""
        pref_str = ", ".join(f"{k}: {v}" for k, v in self.preferences.items()) if self.preferences else "None"
        return f"Owner: {self.name} | Available Time: {self.available_time_minutes} mins | Preferences: {pref_str}"

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

    def sort_tasks_by_time(self, tasks: Optional[List[Task]] = None) -> List[Task]:
        """
        Sorts tasks chronologically by start time. Fixed-time tasks (those with specific start times)
        are placed first, followed by flexible tasks organized by their preferred TimeOfDay window
        (Morning -> Afternoon -> Evening -> Any) and then by priority descending.

        Args:
            tasks (Optional[List[Task]]): The list of tasks to sort. Defaults to the scheduler's internal list.

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
        # 3. TimeOfDay order (morning -> afternoon -> evening -> any)
        # 4. Priority descending (HIGH -> MEDIUM -> LOW)
        def sort_key(t: Task):
            start_min = t.get_start_minutes()
            if start_min is not None:
                return (0, start_min, 0, -t.priority.value)
            else:
                return (1, 0, get_time_of_day_order(t), -t.priority.value)

        return sorted(target_tasks, key=sort_key)

    # CORE EXECUTION ENGINE
    def generate_plan(self, pet_filter: str = "All", status_filter: str = "All") -> List[Dict[str, Any]]:
        """Generates a daily schedule based on priority, specific times, and owner's time constraints."""
        self.plan = []
        reason_steps = []

        total_time_limit = self.owner.available_time_minutes
        current_used_time = 0

        # Apply filtering
        filtered_tasks = self.filter_tasks(pet_filter=pet_filter, status_filter=status_filter)

        # Separate fixed-time tasks and flexible tasks
        fixed_tasks = [t for t in filtered_tasks if t.get_start_minutes() is not None]
        flexible_tasks = [t for t in filtered_tasks if t.get_start_minutes() is None]

        # Sort fixed-time tasks chronologically, using priority descending as tiebreaker
        fixed_tasks.sort(key=lambda t: (t.get_start_minutes(), -t.priority.value))

        # Sort flexible tasks: Priority descending (HIGH -> MEDIUM -> LOW), then time of day ordering
        def get_time_of_day_order(t: Task) -> int:
            order = {
                TimeOfDay.MORNING: 0,
                TimeOfDay.AFTERNOON: 1,
                TimeOfDay.EVENING: 2,
                TimeOfDay.ANY: 3
            }
            return order.get(t.time_of_day, 4)

        flexible_tasks.sort(
            key=lambda t: (t.priority.value, -get_time_of_day_order(t)),
            reverse=True
        )

        target_entity = (
            "all pets" if pet_filter.strip().lower() in ("all", "all pets")
            else "shared tasks" if pet_filter.strip().lower() in ("all (shared)", "shared")
            else pet_filter if pet_filter.strip().lower() != self.pet.name.lower()
            else self.pet.name
        )
        reason_steps.append(f"Starting schedule generation for {target_entity} (Filter: Pet={pet_filter}, Status={status_filter}).")
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
                    "is_completed": task.is_completed
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

        # 2. Schedule flexible tasks in available gaps
        for task in flexible_tasks:
            remaining_time = total_time_limit - current_used_time

            if task.duration_minutes > remaining_time:
                reason_steps.append(
                    f"❌ Skipped '{task.title}' (Priority: {task.priority.name}, Duration: {task.duration_minutes} min) "
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
                    "is_completed": task.is_completed
                })
                reason_steps.append(
                    f"✅ Scheduled '{task.title}' (Priority: {task.priority.name}, Duration: {task.duration_minutes} min) "
                    f"at {self._format_time(start_min)} - {self._format_time(end_min)}."
                )
            else:
                fallback_note = " or fallback daytime hours" if task.time_of_day != TimeOfDay.ANY else ""
                reason_steps.append(
                    f"❌ Skipped '{task.title}' (Priority: {task.priority.name}, Duration: {task.duration_minutes} min) "
                    f"because no available time gap was found during its preferred window{fallback_note}."
                )

        # Sort the final plan chronologically for display
        self.plan.sort(key=lambda item: item["start_minutes"])

        reason_steps.append(
            f"Schedule generation complete. Scheduled {len(self.plan)} tasks, "
            f"utilizing {current_used_time} / {total_time_limit} available minutes."
        )

        self.reasoning = "\n".join(reason_steps)
        return self.plan

    def get_reasoning(self) -> str:
        """Returns the explanation of how and why the schedule was generated."""
        return self.reasoning