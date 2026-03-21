"""Integration tests for the Mutsumi TUI application."""

from __future__ import annotations

from pathlib import Path

import pytest

from mutsumi.app import MutsumiApp
from mutsumi.tui.empty_state import EmptyState
from mutsumi.tui.header_bar import HeaderBar
from mutsumi.tui.task_row import TaskRow

FIXTURE = Path(__file__).parent / "fixtures" / "tasks.json"


@pytest.mark.asyncio
async def test_app_renders_with_fixture() -> None:
    """App should render tasks from the fixture file."""
    app = MutsumiApp(tasks_path=FIXTURE)
    async with app.run_test():
        # Header should be present
        header = app.query_one(HeaderBar)
        assert header is not None

        # TaskRows should be rendered (day scope by default)
        rows = app.query(TaskRow)
        assert len(rows) > 0


@pytest.mark.asyncio
async def test_app_empty_state_no_file() -> None:
    """App should show empty state when no file exists."""
    app = MutsumiApp(tasks_path=Path("/nonexistent/tasks.json"))
    async with app.run_test():
        empty = app.query(EmptyState)
        assert len(empty) > 0


@pytest.mark.asyncio
async def test_tab_switching() -> None:
    """Tab switching should re-render tasks."""
    app = MutsumiApp(tasks_path=FIXTURE)
    async with app.run_test() as pilot:
        # Default is Today (day scope)
        header = app.query_one(HeaderBar)
        assert header.active_scope.value == "day"

        # Press 4 to switch to Inbox
        await pilot.press("4")
        assert header.active_scope.value == "inbox"


@pytest.mark.asyncio
async def test_keyboard_navigation() -> None:
    """j/k should move focus between task rows."""
    app = MutsumiApp(tasks_path=FIXTURE)
    async with app.run_test() as pilot:
        # Press j to focus first task
        await pilot.press("j")
        focused = app.focused
        assert isinstance(focused, TaskRow)


@pytest.mark.asyncio
async def test_quit_binding() -> None:
    """q should exit the app."""
    app = MutsumiApp(tasks_path=FIXTURE)
    async with app.run_test() as pilot:
        await pilot.press("q")
        # If we get here without hanging, the app exited
