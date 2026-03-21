"""Tests for Mutsumi file loader and filtering."""

from pathlib import Path

import pytest

from mutsumi.core import (
    TaskPriority,
    TaskScope,
    filter_tasks_by_scope,
    group_tasks_by_priority,
    load_task_file,
)

FIXTURE = Path(__file__).parent / "fixtures" / "tasks.json"


def test_load_valid_fixture() -> None:
    tf = load_task_file(FIXTURE)
    assert tf.version == 1
    assert len(tf.tasks) == 7


def test_load_nonexistent_raises() -> None:
    with pytest.raises(FileNotFoundError):
        load_task_file(Path("/nonexistent/tasks.json"))


def test_filter_by_scope_day() -> None:
    tf = load_task_file(FIXTURE)
    day_tasks = filter_tasks_by_scope(tf.tasks, TaskScope.DAY)
    titles = {t.title for t in day_tasks}
    assert "Refactor Auth module" in titles
    assert "Fix cache penetration bug" in titles


def test_filter_by_scope_inbox() -> None:
    tf = load_task_file(FIXTURE)
    inbox_tasks = filter_tasks_by_scope(tf.tasks, TaskScope.INBOX)
    titles = {t.title for t in inbox_tasks}
    assert "Buy coffee beans" in titles


def test_filter_by_scope_week() -> None:
    tf = load_task_file(FIXTURE)
    week_tasks = filter_tasks_by_scope(tf.tasks, TaskScope.WEEK)
    titles = {t.title for t in week_tasks}
    assert "Write weekly report" in titles
    assert "Update README" in titles


def test_group_by_priority() -> None:
    tf = load_task_file(FIXTURE)
    day_tasks = filter_tasks_by_scope(tf.tasks, TaskScope.DAY)
    groups = group_tasks_by_priority(day_tasks)
    keys = list(groups.keys())
    # HIGH should come before NORMAL and LOW
    assert keys[0] == TaskPriority.HIGH


def test_group_preserves_order() -> None:
    tf = load_task_file(FIXTURE)
    groups = group_tasks_by_priority(tf.tasks)
    keys = list(groups.keys())
    expected_order = [TaskPriority.HIGH, TaskPriority.NORMAL, TaskPriority.LOW]
    for i, key in enumerate(keys):
        assert key == expected_order[i]
