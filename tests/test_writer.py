"""Tests for the atomic writer and task toggling."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

import pytest

from mutsumi.core.models import TaskFile, TaskStatus
from mutsumi.core.writer import save_task_file, toggle_task_status

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
