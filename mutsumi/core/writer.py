"""Atomic JSON writer for tasks.json."""

from __future__ import annotations

import contextlib
import json
import os
import tempfile
from datetime import UTC
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

    from mutsumi.core.models import Task, TaskFile


def save_task_file(task_file: TaskFile, path: Path) -> None:
    """Atomically write a TaskFile to disk.

    Uses temp file + os.rename to ensure no partial writes.
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
        os.rename(tmp_path, path)
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
