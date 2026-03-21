"""Tests for Tier 1 & Tier 2 features."""

from __future__ import annotations

import json
from datetime import date, timedelta
from pathlib import Path

import pytest

from mutsumi.core.models import Task, TaskFile, TaskPriority, TaskScope, TaskStatus
from mutsumi.core.writer import (
    add_child_task,
    cascade_toggle_status,
    find_task,
    handle_recurrence,
)
from mutsumi.tui.task_row import _due_status


# ── Tier 1: Cascading completion ──────────────────────────────────────


class TestCascadeToggle:
    def _make_file(self) -> TaskFile:
        parent = Task(
            id="P1", title="Parent", status=TaskStatus.PENDING, scope=TaskScope.DAY,
            children=[
                Task(id="C1", title="Child 1", status=TaskStatus.PENDING, scope=TaskScope.DAY),
                Task(id="C2", title="Child 2", status=TaskStatus.PENDING, scope=TaskScope.DAY),
            ],
        )
        return TaskFile(version=1, tasks=[parent])

    def test_parent_done_cascades_to_children(self) -> None:
        tf = self._make_file()
        cascade_toggle_status(tf, "P1")
        parent = find_task(tf, "P1")
        assert parent is not None and parent.status == TaskStatus.DONE
        for child in parent.children:
            assert child.status == TaskStatus.DONE

    def test_parent_pending_cascades_to_children(self) -> None:
        tf = self._make_file()
        # First mark done
        cascade_toggle_status(tf, "P1")
        # Then toggle back
        cascade_toggle_status(tf, "P1")
        parent = find_task(tf, "P1")
        assert parent is not None and parent.status == TaskStatus.PENDING
        for child in parent.children:
            assert child.status == TaskStatus.PENDING

    def test_all_children_done_auto_marks_parent(self) -> None:
        tf = self._make_file()
        cascade_toggle_status(tf, "C1")
        cascade_toggle_status(tf, "C2")
        parent = find_task(tf, "P1")
        assert parent is not None and parent.status == TaskStatus.DONE

    def test_one_child_pending_keeps_parent_pending(self) -> None:
        tf = self._make_file()
        cascade_toggle_status(tf, "C1")
        parent = find_task(tf, "P1")
        assert parent is not None and parent.status == TaskStatus.PENDING

    def test_nonexistent_returns_false(self) -> None:
        tf = self._make_file()
        assert cascade_toggle_status(tf, "NONE") is False


# ── Tier 1: Overdue / Due-today indicators ───────────────────────────


class TestDueStatus:
    def test_overdue(self) -> None:
        yesterday = (date.today() - timedelta(days=1)).isoformat()
        assert _due_status(yesterday) == "overdue"

    def test_today(self) -> None:
        today = date.today().isoformat()
        assert _due_status(today) == "today"

    def test_future(self) -> None:
        tomorrow = (date.today() + timedelta(days=1)).isoformat()
        assert _due_status(tomorrow) is None

    def test_none(self) -> None:
        assert _due_status(None) is None

    def test_invalid_date(self) -> None:
        assert _due_status("not-a-date") is None


# ── Tier 1: Add child task ───────────────────────────────────────────


class TestAddChildTask:
    def test_add_child_to_parent(self) -> None:
        parent = Task(id="P1", title="Parent", scope=TaskScope.DAY)
        tf = TaskFile(version=1, tasks=[parent])
        child = Task(id="C1", title="Child", scope=TaskScope.DAY)
        assert add_child_task(tf, "P1", child) is True
        assert len(tf.tasks[0].children) == 1
        assert tf.tasks[0].children[0].id == "C1"

    def test_add_child_nonexistent_parent(self) -> None:
        tf = TaskFile(version=1, tasks=[])
        child = Task(id="C1", title="Child", scope=TaskScope.DAY)
        assert add_child_task(tf, "NONE", child) is False


# ── Tier 2: Recurrence ──────────────────────────────────────────────


class TestRecurrence:
    def test_daily_recurrence(self) -> None:
        task = Task(
            id="R1", title="Daily", status=TaskStatus.DONE,
            scope=TaskScope.DAY, due_date="2026-03-20",
        )
        # Inject recurrence via model_extra
        task.__pydantic_extra__["recurrence"] = "daily"
        assert handle_recurrence(task) is True
        assert task.due_date == "2026-03-21"
        assert task.status == TaskStatus.PENDING

    def test_weekly_recurrence(self) -> None:
        task = Task(
            id="R2", title="Weekly", status=TaskStatus.DONE,
            scope=TaskScope.WEEK, due_date="2026-03-20",
        )
        task.__pydantic_extra__["recurrence"] = "weekly"
        assert handle_recurrence(task) is True
        assert task.due_date == "2026-03-27"

    def test_monthly_recurrence(self) -> None:
        task = Task(
            id="R3", title="Monthly", status=TaskStatus.DONE,
            scope=TaskScope.MONTH, due_date="2026-03-01",
        )
        task.__pydantic_extra__["recurrence"] = "monthly"
        assert handle_recurrence(task) is True
        assert task.due_date == "2026-03-31"

    def test_no_recurrence(self) -> None:
        task = Task(id="R4", title="No recur", status=TaskStatus.DONE, scope=TaskScope.DAY)
        assert handle_recurrence(task) is False

    def test_invalid_recurrence(self) -> None:
        task = Task(
            id="R5", title="Bad", status=TaskStatus.DONE,
            scope=TaskScope.DAY, due_date="2026-03-20",
        )
        task.__pydantic_extra__["recurrence"] = "biweekly"
        assert handle_recurrence(task) is False

    def test_no_due_date(self) -> None:
        task = Task(id="R6", title="No date", status=TaskStatus.DONE, scope=TaskScope.DAY)
        task.__pydantic_extra__["recurrence"] = "daily"
        assert handle_recurrence(task) is False


# ── Tier 2: Effort field display ─────────────────────────────────────


class TestEffortField:
    def test_effort_in_extra_fields(self) -> None:
        data = {
            "id": "E1", "title": "Effort task", "status": "pending",
            "scope": "day", "effort": "2h",
        }
        task = Task.model_validate(data)
        assert task.model_extra is not None
        assert task.model_extra.get("effort") == "2h"


# ── Tier 2: Config fields ───────────────────────────────────────────


class TestConfigFields:
    def test_custom_css_path_default(self) -> None:
        from mutsumi.config.settings import MutsumiConfig

        config = MutsumiConfig()
        assert config.custom_css_path is None

    def test_columns_default(self) -> None:
        from mutsumi.config.settings import MutsumiConfig

        config = MutsumiConfig()
        assert config.columns == ["checkbox", "title", "tags", "priority"]

    def test_columns_custom(self) -> None:
        from mutsumi.config.settings import MutsumiConfig

        config = MutsumiConfig(columns=["checkbox", "title", "due", "effort", "priority"])
        assert "due" in config.columns
        assert "effort" in config.columns


# ── TUI integration: search-as-filter ────────────────────────────────


@pytest.mark.asyncio
async def test_search_dims_non_matches(tmp_path: Path) -> None:
    """Searching should dim non-matching rows, not remove them."""
    from mutsumi.app import MutsumiApp
    from mutsumi.tui.task_row import TaskRow

    test_file = tmp_path / "tasks.json"
    data = {
        "version": 1,
        "tasks": [
            {"id": "S1", "title": "Alpha task", "status": "pending", "scope": "day"},
            {"id": "S2", "title": "Beta task", "status": "pending", "scope": "day"},
        ],
    }
    test_file.write_text(json.dumps(data, indent=2))

    app = MutsumiApp(tasks_path=test_file)
    async with app.run_test(size=(80, 24)) as pilot:
        # Both rows should be visible
        rows = app.query(TaskRow)
        assert len(rows) == 2

        # Search for "Alpha"
        await pilot.press("slash")
        await pilot.press("A", "l", "p", "h", "a")
        await pilot.pause()

        rows = app.query(TaskRow)
        # Both still present (not removed)
        assert len(rows) == 2
        # Beta should be dimmed
        for row in rows:
            if "Beta" in row.task_data.title:
                assert row.has_class("dimmed")
            else:
                assert not row.has_class("dimmed")


# ── TUI integration: add child via A key ─────────────────────────────


@pytest.mark.asyncio
async def test_add_child_key(tmp_path: Path) -> None:
    """Pressing A on a focused task should open TaskForm with parent_id."""
    from mutsumi.app import MutsumiApp
    from mutsumi.tui.task_row import TaskRow

    test_file = tmp_path / "tasks.json"
    data = {
        "version": 1,
        "tasks": [{"id": "AC1", "title": "Parent", "status": "pending", "scope": "day"}],
    }
    test_file.write_text(json.dumps(data, indent=2))

    app = MutsumiApp(tasks_path=test_file)
    async with app.run_test(size=(80, 24)) as pilot:
        rows = app.query(TaskRow)
        if rows:
            rows.first().focus()
        await pilot.press("A")
        # Should have pushed a screen (TaskForm)
        assert len(app.screen_stack) > 1
