"""Atomic JSON writer for tasks.json."""

from __future__ import annotations

import contextlib
import json
import os
import tempfile
from datetime import UTC, date, datetime, timedelta
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

    from mutsumi.core.models import Task, TaskFile


def save_task_file(task_file: TaskFile, path: Path) -> None:
    """Atomically write a TaskFile to disk.

    Uses temp file + os.replace to ensure no partial writes.
    Works on both Unix and Windows.
    """
    data = json.loads(task_file.model_dump_json())
    content = json.dumps(data, indent=2, ensure_ascii=False) + "\n"

    # Write to temp file in the same directory, then atomic rename
    dir_path = path.parent
    dir_path.mkdir(parents=True, exist_ok=True)

    fd, tmp_path = tempfile.mkstemp(dir=dir_path, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(content)
        os.replace(tmp_path, path)
    except BaseException:
        # Clean up temp file on failure
        with contextlib.suppress(OSError):
            os.unlink(tmp_path)
        raise


def toggle_task_status(task_file: TaskFile, task_id: str) -> bool:
    """Toggle a task's status between pending and done.

    Returns True if the task was found and toggled.
    """
    from mutsumi.core.models import TaskStatus

    def _toggle_in_list(tasks: list[Task]) -> bool:
        for task in tasks:
            if task.id == task_id:
                if task.status == TaskStatus.DONE:
                    task.status = TaskStatus.PENDING
                    task.completed_at = None
                else:
                    task.status = TaskStatus.DONE
                    from datetime import datetime

                    task.completed_at = datetime.now(tz=UTC).isoformat()
                return True
            if task.children and _toggle_in_list(task.children):
                return True
        return False

    return _toggle_in_list(task_file.tasks)


def find_task(task_file: TaskFile, task_id: str) -> Task | None:
    """Find a task by exact ID, searching recursively through children."""

    def _search(tasks: list[Task]) -> Task | None:
        for task in tasks:
            if task.id == task_id:
                return task
            if task.children:
                found = _search(task.children)
                if found is not None:
                    return found
        return None

    return _search(task_file.tasks)


def add_task(task_file: TaskFile, task: Task) -> None:
    """Add a new task to the task file."""
    task_file.tasks.append(task)


def remove_task(task_file: TaskFile, task_id: str) -> bool:
    """Remove a task by ID. Returns True if found and removed."""

    def _remove_from_list(tasks: list[Task]) -> bool:
        for i, task in enumerate(tasks):
            if task.id == task_id:
                tasks.pop(i)
                return True
            if task.children and _remove_from_list(task.children):
                return True
        return False

    return _remove_from_list(task_file.tasks)


def update_task(task_file: TaskFile, task_id: str, **fields: str | list[str] | None) -> bool:
    """Update fields on a task. Returns True if the task was found and updated.

    Accepts keyword arguments matching Task field names.
    """
    task = find_task(task_file, task_id)
    if task is None:
        return False

    for key, value in fields.items():
        if hasattr(task, key):
            setattr(task, key, value)
    return True


def resolve_partial_id(task_file: TaskFile, prefix: str) -> str | None:
    """Resolve a partial ID prefix to a full task ID.

    Returns the full ID if exactly one task matches the prefix.
    Returns None if zero or multiple tasks match.
    """
    matches: list[str] = []

    def _collect(tasks: list[Task]) -> None:
        for task in tasks:
            if task.id.startswith(prefix) or task.id.lower().startswith(prefix.lower()):
                matches.append(task.id)
            if task.children:
                _collect(task.children)

    _collect(task_file.tasks)
    if len(matches) == 1:
        return matches[0]
    return None


def create_task_from_args(
    title: str,
    priority: str = "normal",
    scope: str = "inbox",
    tags: list[str] | None = None,
    description: str | None = None,
) -> Task:
    """Create a new Task instance with generated ID and timestamps."""
    from mutsumi.core.id import generate_task_id
    from mutsumi.core.models import Task as TaskModel
    from mutsumi.core.models import TaskPriority, TaskScope, TaskStatus

    return TaskModel(
        id=generate_task_id(),
        title=title,
        status=TaskStatus.PENDING,
        scope=TaskScope(scope),
        priority=TaskPriority(priority),
        tags=tags or [],
        created_at=datetime.now(tz=UTC).isoformat(),
        description=description,
    )


def reorder_task(task_file: TaskFile, task_id: str, direction: int) -> bool:
    """Move a task within its sibling list.

    *direction*: -1 = move up, +1 = move down.
    Returns True if the task was found and moved.
    """

    def _reorder_in_list(tasks: list[Task]) -> bool:
        for i, task in enumerate(tasks):
            if task.id == task_id:
                new_idx = i + direction
                if new_idx < 0 or new_idx >= len(tasks):
                    return False  # already at boundary
                tasks[i], tasks[new_idx] = tasks[new_idx], tasks[i]
                return True
            if task.children and _reorder_in_list(task.children):
                return True
        return False

    return _reorder_in_list(task_file.tasks)


def clone_task(task_file: TaskFile, task_id: str) -> Task | None:
    """Deep-copy a task and append it after the original in the same list.

    Recursively assigns new IDs to the clone and all its children.
    Returns the cloned task, or None if the source was not found.
    """
    from copy import deepcopy

    from mutsumi.core.id import generate_task_id

    def _assign_new_ids(task: Task) -> None:
        task.id = generate_task_id()
        task.created_at = datetime.now(tz=UTC).isoformat()
        task.completed_at = None
        for child in task.children:
            _assign_new_ids(child)

    def _clone_in_list(tasks: list[Task]) -> Task | None:
        for i, task in enumerate(tasks):
            if task.id == task_id:
                cloned = deepcopy(task)
                _assign_new_ids(cloned)
                tasks.insert(i + 1, cloned)
                return cloned
            if task.children:
                result = _clone_in_list(task.children)
                if result is not None:
                    return result
        return None

    return _clone_in_list(task_file.tasks)


def cascade_toggle_status(task_file: TaskFile, task_id: str) -> bool:
    """Toggle a task's status with cascading behaviour.

    - Marking parent DONE → marks all children DONE.
    - Marking parent PENDING → marks all children PENDING.
    - If toggling a child causes all siblings to be DONE, auto-mark parent DONE.
    - If toggling a child causes any sibling to be PENDING, auto-mark parent PENDING.

    Returns True if the task was found and toggled.
    """
    from mutsumi.core.models import TaskStatus

    def _set_status_deep(task: Task, status: TaskStatus) -> None:
        task.status = status
        if status == TaskStatus.DONE:
            task.completed_at = datetime.now(tz=UTC).isoformat()
        else:
            task.completed_at = None
        for child in task.children:
            _set_status_deep(child, status)

    def _find_parent(tasks: list[Task], target_id: str) -> Task | None:
        for t in tasks:
            for child in t.children:
                if child.id == target_id:
                    return t
                parent = _find_parent(t.children, target_id)
                if parent is not None:
                    return parent
        return None

    task = find_task(task_file, task_id)
    if task is None:
        return False

    # Toggle this task
    if task.status == TaskStatus.DONE:
        _set_status_deep(task, TaskStatus.PENDING)
    else:
        _set_status_deep(task, TaskStatus.DONE)

    # Propagate upward: check if all siblings are now done
    parent = _find_parent(task_file.tasks, task_id)
    if parent is not None:
        all_done = all(c.status == TaskStatus.DONE for c in parent.children)
        if all_done:
            parent.status = TaskStatus.DONE
            parent.completed_at = datetime.now(tz=UTC).isoformat()
        else:
            parent.status = TaskStatus.PENDING
            parent.completed_at = None

    return True


def add_child_task(task_file: TaskFile, parent_id: str, child: Task) -> bool:
    """Add a child task under the specified parent.

    Returns True if the parent was found and child appended.
    """
    parent = find_task(task_file, parent_id)
    if parent is None:
        return False
    parent.children.append(child)
    return True


def handle_recurrence(task: Task) -> bool:
    """If *task* has a ``recurrence`` extra field, bump due_date and reset status.

    Supports: ``daily``, ``weekly``, ``monthly``.
    Returns True if recurrence was applied.
    """
    from mutsumi.core.models import TaskStatus

    recurrence = task.model_extra.get("recurrence") if task.model_extra else None
    if not recurrence or not isinstance(recurrence, str):
        return False

    if task.due_date is None:
        return False

    try:
        due = date.fromisoformat(task.due_date)
    except ValueError:
        return False

    recurrence_lower = recurrence.lower()
    if recurrence_lower == "daily":
        new_due = due + timedelta(days=1)
    elif recurrence_lower == "weekly":
        new_due = due + timedelta(weeks=1)
    elif recurrence_lower == "monthly":
        # Approximate: add 30 days
        new_due = due + timedelta(days=30)
    else:
        return False

    task.due_date = new_due.isoformat()
    task.status = TaskStatus.PENDING
    task.completed_at = None
    return True


def cycle_priority(task_file: TaskFile, task_id: str, direction: int) -> bool:
    """Cycle a task's priority up (+1) or down (-1).

    Priority order: low → normal → high.
    Clamps at boundaries (high cannot go higher, low cannot go lower).
    Returns True if the task was found and changed.
    """
    from mutsumi.core.models import TaskPriority

    priority_order = [TaskPriority.LOW, TaskPriority.NORMAL, TaskPriority.HIGH]

    task = find_task(task_file, task_id)
    if task is None:
        return False

    current_idx = priority_order.index(task.priority)
    new_idx = max(0, min(len(priority_order) - 1, current_idx + direction))
    if new_idx == current_idx:
        return False  # already at boundary
    task.priority = priority_order[new_idx]
    return True
