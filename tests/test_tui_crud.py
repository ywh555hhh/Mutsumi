"""Tests for TUI search, CRUD modals, and dd delete."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

pytest.importorskip("textual")

from mutsumi.app import MutsumiApp
from mutsumi.tui.confirm_bar import ConfirmBar
from mutsumi.tui.search_bar import SearchBar
from mutsumi.tui.task_form import TaskForm
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


@pytest.mark.asyncio
async def test_new_task_form_shows_source_selector_for_multiple_sources(tmp_path: Path) -> None:
    """New task flow should expose source selection when multiple writable sources exist."""
    personal_file = tmp_path / "personal.json"
    repo_file = tmp_path / "repo.json"
    personal_file.write_text(json.dumps({"version": 1, "tasks": []}, indent=2))
    repo_file.write_text(json.dumps({"version": 1, "tasks": []}, indent=2))

    app = MutsumiApp(tasks_path=personal_file)
    app._source_registry.add_source("repo", repo_file)
    app.BINDINGS = list(app._bindings_list)
    async with app.run_test(size=(80, 24)) as pilot:
        await pilot.press("n")
        form = app.screen_stack[-1]
        assert form.query_one("#form-source").value == "default"


@pytest.mark.asyncio
async def test_submit_new_task_to_selected_source(tmp_path: Path) -> None:
    """Submitting with a selected source should write to that source file."""
    personal_file = tmp_path / "personal.json"
    repo_file = tmp_path / "repo.json"
    personal_file.write_text(json.dumps({"version": 1, "tasks": []}, indent=2))
    repo_file.write_text(json.dumps({"version": 1, "tasks": []}, indent=2))

    app = MutsumiApp(tasks_path=personal_file)
    app._source_registry.add_source("repo", repo_file)
    app.BINDINGS = list(app._bindings_list)
    async with app.run_test(size=(80, 24)) as pilot:
        await pilot.press("n")
        form = app.screen_stack[-1]
        form.query_one("#form-title").value = "Cross source task"
        form.query_one("#form-source").value = "repo"
        form._submit()
        await pilot.pause()

    personal_data = json.loads(personal_file.read_text())
    repo_data = json.loads(repo_file.read_text())
    assert personal_data["tasks"] == []
    assert len(repo_data["tasks"]) == 1
    assert repo_data["tasks"][0]["title"] == "Cross source task"


@pytest.mark.asyncio
async def test_add_child_form_hides_source_selector_even_with_multiple_sources(tmp_path: Path) -> None:
    """Subtask flow should stay in the parent's source and hide source selection."""
    personal_file = tmp_path / "personal.json"
    repo_file = tmp_path / "repo.json"
    personal_file.write_text(
        json.dumps(
            {
                "version": 1,
                "tasks": [{"id": "P1", "title": "Parent", "status": "pending", "scope": "day"}],
            },
            indent=2,
        ),
    )
    repo_file.write_text(json.dumps({"version": 1, "tasks": []}, indent=2))

    app = MutsumiApp(tasks_path=personal_file)
    app._source_registry.add_source("repo", repo_file)
    app.BINDINGS = list(app._bindings_list)
    async with app.run_test(size=(80, 24)) as pilot:
        rows = app.query(TaskRow)
        rows.first().focus()
        await pilot.press("A")
        form = app.screen_stack[-1]
        assert len(form.query("#form-source")) == 0


@pytest.mark.asyncio
async def test_cross_source_subtask_failure_does_not_write_or_claim_success(tmp_path: Path) -> None:
    """Subtask creation must fail loudly when the chosen source lacks the parent."""
    personal_file = tmp_path / "personal.json"
    repo_file = tmp_path / "repo.json"
    personal_file.write_text(
        json.dumps(
            {
                "version": 1,
                "tasks": [{"id": "P1", "title": "Parent", "status": "pending", "scope": "day"}],
            },
            indent=2,
        ),
    )
    repo_file.write_text(json.dumps({"version": 1, "tasks": []}, indent=2))

    app = MutsumiApp(tasks_path=personal_file)
    app._source_registry.add_source("repo", repo_file)
    app.BINDINGS = list(app._bindings_list)
    async with app.run_test(size=(80, 24)) as pilot:
        await app.on_task_form_task_submitted(
            TaskForm.TaskSubmitted(
                title="Bad subtask",
                priority="normal",
                scope="day",
                tags="",
                description="",
                editing_id=None,
                parent_id="P1",
                source_name="repo",
            ),
        )
        await pilot.pause()
        footer = app.query_one("#stats-text")
        assert "Parent task P1 not found in source repo" in str(footer.render())

    personal_data = json.loads(personal_file.read_text())
    repo_data = json.loads(repo_file.read_text())
    assert len(personal_data["tasks"]) == 1
    assert repo_data["tasks"] == []


@pytest.mark.asyncio
async def test_invalid_selected_source_shows_error_and_does_not_write(tmp_path: Path) -> None:
    """Submitting to a missing source should fail visibly without writing anywhere."""
    personal_file = tmp_path / "personal.json"
    repo_file = tmp_path / "repo.json"
    personal_file.write_text(json.dumps({"version": 1, "tasks": []}, indent=2))
    repo_file.write_text(json.dumps({"version": 1, "tasks": []}, indent=2))

    app = MutsumiApp(tasks_path=personal_file)
    app._source_registry.add_source("repo", repo_file)
    app.BINDINGS = list(app._bindings_list)
    async with app.run_test(size=(80, 24)) as pilot:
        await app.on_task_form_task_submitted(
            TaskForm.TaskSubmitted(
                title="Ghost target",
                priority="normal",
                scope="day",
                tags="",
                description="",
                editing_id=None,
                parent_id=None,
                source_name="missing",
            ),
        )
        await pilot.pause()
        footer = app.query_one("#stats-text")
        render = str(footer.render())
        assert "Unknown source: missing" in render
        assert 'Created: "Ghost target"' not in render

    personal_data = json.loads(personal_file.read_text())
    repo_data = json.loads(repo_file.read_text())
    assert personal_data["tasks"] == []
    assert repo_data["tasks"] == []
