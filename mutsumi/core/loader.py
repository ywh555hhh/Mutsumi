"""File I/O and task filtering for Mutsumi."""

from __future__ import annotations

import json
from collections import OrderedDict
from datetime import date, timedelta
from pathlib import Path

from mutsumi.core.models import Task, TaskFile, TaskPriority, TaskScope


def load_task_file(path: Path) -> TaskFile:
    """Read and parse a tasks.json file.

    Raises FileNotFoundError if file doesn't exist.
    Raises json.JSONDecodeError on invalid JSON.
    Raises pydantic.ValidationError on schema errors.
    """
    raw = path.read_text(encoding="utf-8")
    data = json.loads(raw)
    return TaskFile.model_validate(data)


def resolve_tasks_path(cli_path: str | None) -> Path:
    """Resolve tasks.json path from CLI arg or current directory."""
    if cli_path is not None:
        return Path(cli_path).resolve()
    return Path.cwd() / "tasks.json"


def _derive_scope(task: Task, today: date) -> TaskScope:
    """Derive scope from due_date when no explicit scope is set."""
    if task.due_date is None:
        return TaskScope.INBOX

    try:
        due = date.fromisoformat(task.due_date)
    except ValueError:
        return TaskScope.INBOX

    if due <= today:
        return TaskScope.DAY
    # Check if within this week (Monday to Sunday)
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6)
    if due <= week_end:
        return TaskScope.WEEK
    # Check if within this month
    if due.year == today.year and due.month == today.month:
        return TaskScope.MONTH
    return TaskScope.MONTH


def get_task_scope(task: Task, today: date | None = None) -> TaskScope:
    """Resolve the effective scope of a task.

    Priority: manual scope > due_date auto-derivation > fallback inbox.
    """
    if today is None:
        today = date.today()

    # If task has an explicit scope that isn't inbox, use it
    # (inbox is the default, so it might be auto-derived)
    if task.scope != TaskScope.INBOX:
        return task.scope

    # If scope is inbox but has due_date, try to derive
    if task.due_date is not None:
        return _derive_scope(task, today)

    return TaskScope.INBOX


def filter_tasks_by_scope(
    tasks: list[Task],
    scope: TaskScope,
    today: date | None = None,
) -> list[Task]:
    """Filter top-level tasks by their effective scope."""
    return [t for t in tasks if get_task_scope(t, today) == scope]


def group_tasks_by_priority(
    tasks: list[Task],
) -> OrderedDict[TaskPriority, list[Task]]:
    """Group tasks by priority in HIGH > NORMAL > LOW order."""
    groups: OrderedDict[TaskPriority, list[Task]] = OrderedDict()
    for p in (TaskPriority.HIGH, TaskPriority.NORMAL, TaskPriority.LOW):
        group = [t for t in tasks if t.priority == p]
        if group:
            groups[p] = group
    return groups
