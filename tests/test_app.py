"""Integration tests for the Mutsumi TUI application."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

pytest.importorskip("textual")

from mutsumi.app import MutsumiApp
from mutsumi.onboarding.bootstrap import StartupState
from mutsumi.tui.detail_panel import DetailPanel
from mutsumi.tui.empty_state import EmptyState
from mutsumi.tui.header_bar import HeaderBar
from mutsumi.tui.task_row import TaskRow

FIXTURE = Path(__file__).parent / "fixtures" / "tasks.json"


@pytest.mark.asyncio
async def test_app_accepts_startup_state() -> None:
    """App should accept startup state wiring before onboarding UI lands."""
    startup_state = StartupState(
        mode="first_run",
        cwd=Path.cwd(),
        is_git_repo=False,
        config_exists=False,
        onboarding_completed=False,
        personal_tasks_exists=False,
        project_tasks_exists=False,
        project_registered=False,
    )
    app = MutsumiApp(tasks_path=FIXTURE, startup_state=startup_state)
    async with app.run_test():
        assert app._startup_state == startup_state


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


@pytest.mark.asyncio
async def test_toggle_writes_back(tmp_path: Path) -> None:
    """Space should toggle status and write back to JSON."""
    # Copy fixture to tmp for write test
    tasks_file = tmp_path / "tasks.json"
    shutil.copy2(FIXTURE, tasks_file)

    app = MutsumiApp(tasks_path=tasks_file)
    async with app.run_test() as pilot:
        # The app auto-focuses the first task row
        focused = app.focused
        assert isinstance(focused, TaskRow)
        original_id = focused.task_data.id
        original_status = focused.task_data.status.value

        await pilot.press("space")
        await pilot.pause()

        # Verify file was updated — search recursively
        data = json.loads(tasks_file.read_text())

        def find_task(tasks: list[dict[str, object]], tid: str) -> dict[str, object] | None:
            for t in tasks:
                if t.get("id") == tid:
                    return t
                children = t.get("children", [])
                if isinstance(children, list):
                    found = find_task(children, tid)
                    if found:
                        return found
            return None

        toggled_task = find_task(data["tasks"], original_id)  # type: ignore[arg-type]
        assert toggled_task is not None
        # Status should have changed
        expected = "done" if original_status == "pending" else "pending"
        assert toggled_task["status"] == expected


@pytest.mark.asyncio
async def test_detail_panel_toggle() -> None:
    """Enter should open/close the detail panel."""
    app = MutsumiApp(tasks_path=FIXTURE)
    async with app.run_test() as pilot:
        detail = app.query_one(DetailPanel)
        assert not detail.is_visible

        # Focus a task, press enter
        await pilot.press("j")
        await pilot.press("enter")
        assert detail.is_visible

        # Press escape to close
        await pilot.press("escape")
        assert not detail.is_visible


@pytest.mark.asyncio
async def test_detail_panel_enter_toggles() -> None:
    """Enter should toggle detail panel open/closed."""
    app = MutsumiApp(tasks_path=FIXTURE)
    async with app.run_test() as pilot:
        detail = app.query_one(DetailPanel)

        await pilot.press("j")
        await pilot.press("enter")
        assert detail.is_visible

        # Enter again should close
        await pilot.press("enter")
        assert not detail.is_visible


@pytest.mark.asyncio
async def test_error_banner_on_invalid_json(tmp_path: Path) -> None:
    """Invalid JSON should show error banner."""
    bad_file = tmp_path / "tasks.json"
    bad_file.write_text("{ invalid json !!!}")

    app = MutsumiApp(tasks_path=bad_file)
    async with app.run_test():
        banner = app.query("#error-banner")
        assert len(banner) > 0
