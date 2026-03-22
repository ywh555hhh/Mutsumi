"""File I/O and task filtering for Mutsumi."""

from __future__ import annotations

import json
import logging
import sys
from collections import OrderedDict
from datetime import date, timedelta
from pathlib import Path

from pydantic import ValidationError

from mutsumi.core.models import Task, TaskFile, TaskPriority, TaskScope

_log = logging.getLogger("mutsumi")


def setup_logging(log_path: Path | None = None) -> None:
    """Configure Mutsumi logging: stderr + optional file.

    Call once at startup.  Safe to call multiple times (idempotent).
    """
    logger = logging.getLogger("mutsumi")
    if logger.handlers:
        return  # already configured
    logger.setLevel(logging.WARNING)

    fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S")

    # stderr handler
    stderr_handler = logging.StreamHandler(sys.stderr)
    stderr_handler.setFormatter(fmt)
    logger.addHandler(stderr_handler)

    # File handler (optional)
    if log_path is None:
        from mutsumi.core.paths import mutsumi_data_dir

        data_home = mutsumi_data_dir()
        data_home.mkdir(parents=True, exist_ok=True)
        log_path = data_home / "error.log"
    try:
        log_path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_path, encoding="utf-8")
        file_handler.setFormatter(fmt)
        logger.addHandler(file_handler)
    except OSError:
        pass  # can't write log file — degrade gracefully


def load_task_file(path: Path) -> TaskFile:
    """Read and parse a tasks.json file with per-task resilience.

    Individual tasks that fail validation are skipped rather than
    crashing the entire file.  The returned TaskFile has *skipped_count*
    set to the number of entries that were dropped.

    Raises FileNotFoundError if file doesn't exist.
    Raises json.JSONDecodeError on invalid JSON.
    """
    raw = path.read_text(encoding="utf-8")
    data = json.loads(raw)

    # Validate top-level structure (version, extra fields) but NOT tasks
    task_dicts: list[dict[str, object]] = data.pop("tasks", [])
    if not isinstance(task_dicts, list):
        task_dicts = []

    # Build TaskFile shell (no tasks yet)
    try:
        shell = TaskFile.model_validate({**data, "tasks": []})
    except ValidationError:
        shell = TaskFile(version=data.get("version", 1))

    # Validate tasks one-by-one
    valid_tasks: list[Task] = []
    skipped = 0
    for i, raw_task in enumerate(task_dicts):
        if not isinstance(raw_task, dict):
            _log.warning("tasks[%d]: not a dict, skipped", i)
            skipped += 1
            continue
        try:
            valid_tasks.append(Task.model_validate(raw_task))
        except ValidationError as exc:
            tid = raw_task.get("id", "???")
            _log.warning("tasks[%d] (id=%s): validation error, skipped — %s", i, tid, exc)
            skipped += 1

    shell.tasks = valid_tasks
    shell.skipped_count = skipped
    return shell


def resolve_tasks_path(cli_path: str | None = None) -> Path:
    """Resolve task file path: CLI arg > mutsumi.json > tasks.json fallback.

    Priority:
      1. Explicit CLI ``--path`` argument
      2. ``mutsumi.json`` in cwd (preferred name)
      3. ``tasks.json`` in cwd (backward compat fallback)
      4. ``mutsumi.json`` in cwd (default for new projects)
    """
    if cli_path is not None:
        return Path(cli_path).resolve()

    cwd = Path.cwd()
    mutsumi_path = cwd / "mutsumi.json"
    tasks_path = cwd / "tasks.json"

    if mutsumi_path.exists():
        return mutsumi_path
    if tasks_path.exists():
        return tasks_path
    # Neither exists — default to new canonical name
    return mutsumi_path


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


def sort_tasks(tasks: list[Task], field: str, reverse: bool = False) -> list[Task]:
    """Sort tasks by *field* name. Unknown fields leave order unchanged.

    Supported fields: title, priority, status, due.
    """
    from mutsumi.core.models import PRIORITY_SORT_ORDER

    if field == "title":
        return sorted(tasks, key=lambda t: t.title.lower(), reverse=reverse)
    if field == "priority":
        return sorted(
            tasks,
            key=lambda t: PRIORITY_SORT_ORDER.get(t.priority, 99),
            reverse=reverse,
        )
    if field == "status":
        return sorted(tasks, key=lambda t: t.status.value, reverse=reverse)
    if field == "due":
        return sorted(tasks, key=lambda t: t.due_date or "", reverse=reverse)
    return list(tasks)
