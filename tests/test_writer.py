"""Tests for the atomic writer and task toggling."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

import pytest

from mutsumi.core.models import TaskFile, TaskPriority, TaskStatus
from mutsumi.core.writer import (
    clone_task,
    cycle_priority,
    reorder_task,
    save_task_file,
    toggle_task_status,
)

if TYPE_CHECKING:
    from pathlib import Path


@pytest.fixture
def sample_task_file() -> TaskFile:
    return TaskFile.model_validate(
        {
            "version": 1,
            "tasks": [
                {"id": "t1", "title": "Task 1", "status": "pending"},
                {
                    "id": "t2",
                    "title": "Task 2",
                    "status": "done",
                    "children": [
                        {"id": "t2a", "title": "Sub A", "status": "pending"},
                    ],
                },
            ],
        }
    )


def test_save_creates_file(tmp_path: Path, sample_task_file: TaskFile) -> None:
    out = tmp_path / "tasks.json"
    save_task_file(sample_task_file, out)
    assert out.exists()
    data = json.loads(out.read_text())
    assert data["version"] == 1
    assert len(data["tasks"]) == 2


def test_save_roundtrip(tmp_path: Path, sample_task_file: TaskFile) -> None:
    out = tmp_path / "tasks.json"
    save_task_file(sample_task_file, out)
    from mutsumi.core.loader import load_task_file

    reloaded = load_task_file(out)
    assert len(reloaded.tasks) == len(sample_task_file.tasks)
    assert reloaded.tasks[0].title == sample_task_file.tasks[0].title


def test_save_atomic_no_partial(tmp_path: Path, sample_task_file: TaskFile) -> None:
    """After save, no .tmp files should remain."""
    out = tmp_path / "tasks.json"
    save_task_file(sample_task_file, out)
    tmp_files = list(tmp_path.glob("*.tmp"))
    assert len(tmp_files) == 0


def test_save_preserves_custom_fields(tmp_path: Path) -> None:
    tf = TaskFile.model_validate(
        {
            "version": 1,
            "custom_meta": "hello",
            "tasks": [
                {"id": "t1", "title": "T1", "agent_context": {"model": "gpt-4"}},
            ],
        }
    )
    out = tmp_path / "tasks.json"
    save_task_file(tf, out)
    data = json.loads(out.read_text())
    assert data["custom_meta"] == "hello"
    assert data["tasks"][0]["agent_context"]["model"] == "gpt-4"


def test_toggle_pending_to_done(sample_task_file: TaskFile) -> None:
    assert sample_task_file.tasks[0].status == TaskStatus.PENDING
    result = toggle_task_status(sample_task_file, "t1")
    assert result is True
    assert sample_task_file.tasks[0].status == TaskStatus.DONE
    assert sample_task_file.tasks[0].completed_at is not None


def test_toggle_done_to_pending(sample_task_file: TaskFile) -> None:
    assert sample_task_file.tasks[1].status == TaskStatus.DONE
    result = toggle_task_status(sample_task_file, "t2")
    assert result is True
    assert sample_task_file.tasks[1].status == TaskStatus.PENDING
    assert sample_task_file.tasks[1].completed_at is None


def test_toggle_child_task(sample_task_file: TaskFile) -> None:
    result = toggle_task_status(sample_task_file, "t2a")
    assert result is True
    child = sample_task_file.tasks[1].children[0]
    assert child.status == TaskStatus.DONE


def test_toggle_nonexistent_returns_false(sample_task_file: TaskFile) -> None:
    result = toggle_task_status(sample_task_file, "nonexistent")
    assert result is False


# ── New writer operations tests ──────────────────────────────────────


def test_reorder_task_down(sample_task_file: TaskFile) -> None:
    """Move first task down → swap positions."""
    assert sample_task_file.tasks[0].id == "t1"
    result = reorder_task(sample_task_file, "t1", direction=1)
    assert result is True
    assert sample_task_file.tasks[0].id == "t2"
    assert sample_task_file.tasks[1].id == "t1"


def test_reorder_task_up(sample_task_file: TaskFile) -> None:
    """Move second task up → swap positions."""
    result = reorder_task(sample_task_file, "t2", direction=-1)
    assert result is True
    assert sample_task_file.tasks[0].id == "t2"


def test_reorder_task_boundary(sample_task_file: TaskFile) -> None:
    """Moving first task up should fail (already at boundary)."""
    result = reorder_task(sample_task_file, "t1", direction=-1)
    assert result is False


def test_reorder_task_nonexistent(sample_task_file: TaskFile) -> None:
    result = reorder_task(sample_task_file, "nope", direction=1)
    assert result is False


def test_clone_task(sample_task_file: TaskFile) -> None:
    original_count = len(sample_task_file.tasks)
    cloned = clone_task(sample_task_file, "t1")
    assert cloned is not None
    assert cloned.id != "t1"  # new ID
    assert cloned.title == "Task 1"
    assert len(sample_task_file.tasks) == original_count + 1


def test_clone_task_with_children(sample_task_file: TaskFile) -> None:
    """Clone should recursively assign new IDs to children."""
    cloned = clone_task(sample_task_file, "t2")
    assert cloned is not None
    assert len(cloned.children) == 1
    assert cloned.children[0].id != "t2a"


def test_clone_task_nonexistent(sample_task_file: TaskFile) -> None:
    result = clone_task(sample_task_file, "nope")
    assert result is None


def test_cycle_priority_up(sample_task_file: TaskFile) -> None:
    """Default is NORMAL → up should become HIGH."""
    result = cycle_priority(sample_task_file, "t1", direction=1)
    assert result is True
    assert sample_task_file.tasks[0].priority == TaskPriority.HIGH


def test_cycle_priority_down(sample_task_file: TaskFile) -> None:
    """Default is NORMAL → down should become LOW."""
    result = cycle_priority(sample_task_file, "t1", direction=-1)
    assert result is True
    assert sample_task_file.tasks[0].priority == TaskPriority.LOW


def test_cycle_priority_clamp_high(sample_task_file: TaskFile) -> None:
    """Cycling up from HIGH should not change (boundary)."""
    sample_task_file.tasks[0].priority = TaskPriority.HIGH
    result = cycle_priority(sample_task_file, "t1", direction=1)
    assert result is False
    assert sample_task_file.tasks[0].priority == TaskPriority.HIGH


def test_cycle_priority_clamp_low(sample_task_file: TaskFile) -> None:
    sample_task_file.tasks[0].priority = TaskPriority.LOW
    result = cycle_priority(sample_task_file, "t1", direction=-1)
    assert result is False


def test_cycle_priority_nonexistent(sample_task_file: TaskFile) -> None:
    result = cycle_priority(sample_task_file, "nope", direction=1)
    assert result is False
