"""Tests for TUI search, CRUD modals, and dd delete."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from mutsumi.app import MutsumiApp
from mutsumi.tui.confirm_bar import ConfirmBar
from mutsumi.tui.search_bar import SearchBar
from mutsumi.tui.task_row import TaskRow

FIXTURE = Path(__file__).parent / "fixtures" / "tasks.json"


@pytest.mark.asyncio
async def test_search_bar_toggle() -> None:
    """Pressing / should show search bar."""
    app = MutsumiApp(tasks_path=FIXTURE)
    async with app.run_test() as pilot:
        search = app.query_one(SearchBar)
        assert not search.is_visible
        await pilot.press("slash")
        assert search.is_visible
        await pilot.press("escape")
        assert not search.is_visible


@pytest.mark.asyncio
async def test_new_task_modal(tmp_path: Path) -> None:
    """Pressing n should open new task form."""
    test_file = tmp_path / "tasks.json"
    data = {
        "version": 1,
        "tasks": [{"id": "T1", "title": "Existing Task", "status": "pending", "scope": "day"}],
    }
    test_file.write_text(json.dumps(data, indent=2))

    app = MutsumiApp(tasks_path=test_file)
    async with app.run_test(size=(80, 24)) as pilot:
        # Focus a task row first (n is ignored when no row focused or Input focused)
        rows = app.query(TaskRow)
        if rows:
            rows.first().focus()
        await pilot.press("n")
        assert len(app.screen_stack) > 1


@pytest.mark.asyncio
async def test_edit_task_modal(tmp_path: Path) -> None:
    """Pressing e on a focused task should open edit form."""
    test_file = tmp_path / "tasks.json"
    data = {
        "version": 1,
        "tasks": [{"id": "T1", "title": "Edit Me", "status": "pending", "scope": "day"}],
    }
    test_file.write_text(json.dumps(data, indent=2))

    app = MutsumiApp(tasks_path=test_file)
    async with app.run_test(size=(80, 24)) as pilot:
        rows = app.query(TaskRow)
        if rows:
            rows.first().focus()
        await pilot.press("e")
        assert len(app.screen_stack) > 1


@pytest.mark.asyncio
async def test_dd_delete_shows_confirm_bar(tmp_path: Path) -> None:
    """Pressing dd should show the inline ConfirmBar (not modal dialog)."""
    test_file = tmp_path / "tasks.json"
    data = {
        "version": 1,
        "tasks": [{"id": "DEL001", "title": "Delete me", "scope": "day"}],
    }
    test_file.write_text(json.dumps(data, indent=2))

    app = MutsumiApp(tasks_path=test_file)
    async with app.run_test(size=(80, 24)) as pilot:
        rows = app.query(TaskRow)
        if rows:
            rows.first().focus()
            # First d — should show PREFIX state in KeyManager (nothing visible yet)
            await pilot.press("d")
            confirm_bar = app.query_one(ConfirmBar)
            assert not confirm_bar.display

            # Second d — should show ConfirmBar
            await pilot.press("d")
            confirm_bar = app.query_one(ConfirmBar)
            assert confirm_bar.display


@pytest.mark.asyncio
async def test_dd_confirm_bar_cancel(tmp_path: Path) -> None:
    """Pressing n (or any non-y key) on ConfirmBar should cancel."""
    test_file = tmp_path / "tasks.json"
    data = {
        "version": 1,
        "tasks": [{"id": "DEL002", "title": "Keep me", "scope": "day"}],
    }
    test_file.write_text(json.dumps(data, indent=2))

    app = MutsumiApp(tasks_path=test_file)
    async with app.run_test(size=(80, 24)) as pilot:
        rows = app.query(TaskRow)
        if rows:
            rows.first().focus()
            await pilot.press("d")
            await pilot.press("d")
            await pilot.pause()
            # Press n to cancel
            await pilot.press("n")
            await pilot.pause()
            confirm_bar = app.query_one(ConfirmBar)
            assert not confirm_bar.display
            # Task should still exist
            reloaded = json.loads(test_file.read_text())
            assert len(reloaded["tasks"]) == 1
