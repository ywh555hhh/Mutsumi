"""Integration tests for the Mutsumi TUI application."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

pytest.importorskip("textual")

from textual.widgets import Input

from mutsumi.app import MutsumiApp
from mutsumi.onboarding.bootstrap import StartupState
from mutsumi.tui.detail_panel import DetailPanel
from mutsumi.tui.empty_state import EmptyState
from mutsumi.tui.header_bar import HeaderBar
from mutsumi.tui.help_screen import HelpScreen
from mutsumi.tui.onboarding_screen import OnboardingScreen
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
async def test_onboarding_completion_hot_reloads_keybindings_immediately(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Choosing a preset in onboarding should hot-reload bindings before entering the app."""
    config_path = tmp_path / "config.toml"
    config_path.write_text(
        'language = "en"\nkeybindings = "arrows"\ntheme = "monochrome-zen"\n',
        encoding="utf-8",
    )
    startup_state = StartupState(
        mode="first_run",
        cwd=tmp_path,
        is_git_repo=False,
        config_exists=False,
        onboarding_completed=False,
        personal_tasks_exists=False,
        project_tasks_exists=False,
        project_registered=False,
    )
    monkeypatch.setattr("mutsumi.app.save_config", lambda config: config_path)
    monkeypatch.setattr("mutsumi.app.ensure_personal_task_file", lambda: FIXTURE)
    monkeypatch.setattr("mutsumi.app.personal_tasks_path", lambda: FIXTURE)

    app = MutsumiApp(tasks_path=FIXTURE, config_path=config_path, startup_state=startup_state)
    async with app.run_test(size=(80, 24)) as pilot:
        assert app._keybinding_preset == "arrows"
        assert isinstance(app.screen, OnboardingScreen)
        assert any(binding.key == "down" for binding in app.BINDINGS)

        onboarding = app.screen
        onboarding._selections["keybindings"] = "vim"
        for _ in range(len(onboarding._selections)):
            await pilot.press("down")
        await pilot.press("enter")
        await pilot.pause()

        assert app._keybinding_preset == "vim"
        assert app._config.keybindings == "vim"
        assert not isinstance(app.screen, OnboardingScreen)
        assert any(binding.key == "j" and binding.action == "cursor_down" for binding in app.BINDINGS)
        assert not any(
            binding.key == "down" and binding.action == "cursor_down"
            for binding in app.BINDINGS
        )



@pytest.mark.asyncio
async def test_help_screen_uses_hot_reloaded_preset_labels_after_onboarding(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Help should reflect the preset hot-reloaded by onboarding."""
    config_path = tmp_path / "config.toml"
    config_path.write_text(
        'language = "en"\nkeybindings = "arrows"\ntheme = "monochrome-zen"\n',
        encoding="utf-8",
    )
    startup_state = StartupState(
        mode="first_run",
        cwd=tmp_path,
        is_git_repo=False,
        config_exists=False,
        onboarding_completed=False,
        personal_tasks_exists=False,
        project_tasks_exists=False,
        project_registered=False,
    )
    monkeypatch.setattr("mutsumi.app.save_config", lambda config: config_path)
    monkeypatch.setattr("mutsumi.app.ensure_personal_task_file", lambda: FIXTURE)
    monkeypatch.setattr("mutsumi.app.personal_tasks_path", lambda: FIXTURE)

    app = MutsumiApp(tasks_path=FIXTURE, config_path=config_path, startup_state=startup_state)
    async with app.run_test(size=(80, 24)) as pilot:
        onboarding = app.screen
        assert isinstance(onboarding, OnboardingScreen)
        onboarding._selections["keybindings"] = "vim"
        for _ in range(len(onboarding._selections)):
            await pilot.press("down")
        await pilot.press("enter")
        await pilot.pause()

        await pilot.press("question_mark")
        await pilot.pause()

        help_screen = app.screen
        assert isinstance(help_screen, HelpScreen)
        text = help_screen._build_table().plain
        assert "(vim preset)" in text
        assert "Confirm" in text
        assert "Back" in text
        assert "New" in text
        assert "Edit" in text
        assert "j" in text
        assert "show_detail" not in text
        assert "close_detail" not in text


@pytest.mark.asyncio
async def test_app_renders_with_fixture() -> None:
    """App should render tasks from the fixture file."""
    app = MutsumiApp(tasks_path=FIXTURE)
    async with app.run_test():
        header = app.query_one(HeaderBar)
        assert header is not None

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
        header = app.query_one(HeaderBar)
        assert header.active_scope.value == "day"

        await pilot.press("4")
        assert header.active_scope.value == "inbox"


@pytest.mark.asyncio
async def test_keyboard_navigation() -> None:
    """j/k should move focus between task rows."""
    app = MutsumiApp(tasks_path=FIXTURE)
    async with app.run_test() as pilot:
        await pilot.press("j")
        focused = app.focused
        assert isinstance(focused, TaskRow)


@pytest.mark.asyncio
async def test_quit_binding() -> None:
    """q should exit the app."""
    app = MutsumiApp(tasks_path=FIXTURE)
    async with app.run_test() as pilot:
        await pilot.press("q")


@pytest.mark.asyncio
async def test_toggle_writes_back(tmp_path: Path) -> None:
    """Space should toggle status and write back to JSON."""
    tasks_file = tmp_path / "tasks.json"
    shutil.copy2(FIXTURE, tasks_file)

    app = MutsumiApp(tasks_path=tasks_file)
    async with app.run_test() as pilot:
        focused = app.focused
        assert isinstance(focused, TaskRow)
        original_id = focused.task_data.id
        original_status = focused.task_data.status.value

        await pilot.press("space")
        await pilot.pause()

        data = json.loads(tasks_file.read_text())

        def find_task(tasks: list[dict[str, object]], tid: str) -> dict[str, object] | None:
            for task in tasks:
                if task.get("id") == tid:
                    return task
                children = task.get("children", [])
                if isinstance(children, list):
                    found = find_task(children, tid)
                    if found:
                        return found
            return None

        toggled_task = find_task(data["tasks"], original_id)  # type: ignore[arg-type]
        assert toggled_task is not None
        expected = "done" if original_status == "pending" else "pending"
        assert toggled_task["status"] == expected


@pytest.mark.asyncio
async def test_detail_panel_opens_on_confirm_and_closes_on_back() -> None:
    """Confirm should open detail and back should close it."""
    app = MutsumiApp(tasks_path=FIXTURE)
    async with app.run_test() as pilot:
        detail = app.query_one(DetailPanel)
        assert not detail.is_visible

        await pilot.press("j")
        await pilot.press("enter")
        assert detail.is_visible

        await pilot.press("escape")
        assert not detail.is_visible


@pytest.mark.asyncio
async def test_detail_panel_confirm_opens_without_toggling_closed() -> None:
    """Confirm should open detail, but must not act as a back toggle."""
    app = MutsumiApp(tasks_path=FIXTURE)
    async with app.run_test() as pilot:
        detail = app.query_one(DetailPanel)

        await pilot.press("j")
        await pilot.press("enter")
        assert detail.is_visible

        await pilot.press("enter")
        assert detail.is_visible


@pytest.mark.asyncio
async def test_error_banner_on_invalid_json(tmp_path: Path) -> None:
    """Invalid JSON should show error banner."""
    bad_file = tmp_path / "tasks.json"
    bad_file.write_text("{ invalid json !!!}")

    app = MutsumiApp(tasks_path=bad_file)
    async with app.run_test():
        banner = app.query("#error-banner")
        assert len(banner) > 0


@pytest.mark.asyncio
async def test_escape_closes_confirm_before_detail() -> None:
    """Back should dismiss confirm before uncovering the detail layer."""
    app = MutsumiApp(tasks_path=FIXTURE)
    async with app.run_test() as pilot:
        detail = app.query_one(DetailPanel)
        confirm_bar = app.query_one("#confirm-bar")

        await pilot.press("j")
        await pilot.press("enter")
        assert detail.is_visible

        await pilot.press("d")
        await pilot.press("d")
        await pilot.pause()
        assert confirm_bar.display
        assert detail.is_visible

        await pilot.press("escape")
        await pilot.pause()
        assert not confirm_bar.display
        assert detail.is_visible

        await pilot.press("escape")
        assert not detail.is_visible


@pytest.mark.asyncio
async def test_slash_keeps_search_open_when_already_visible() -> None:
    """Search open action should not toggle the bar closed once visible."""
    app = MutsumiApp(tasks_path=FIXTURE)
    async with app.run_test() as pilot:
        rows = app.query(TaskRow)
        rows.first().focus()

        await pilot.press("slash")
        search = app.query_one("#search-bar")
        assert search.is_visible

        rows.first().focus()
        await pilot.press("slash")
        await pilot.pause()
        assert search.is_visible
        assert isinstance(app.focused, Input)


@pytest.mark.asyncio
async def test_escape_closes_search_before_detail() -> None:
    """Back should close the top-most interaction layer first."""
    app = MutsumiApp(tasks_path=FIXTURE)
    async with app.run_test() as pilot:
        detail = app.query_one(DetailPanel)
        await pilot.press("j")
        await pilot.press("enter")
        assert detail.is_visible

        await pilot.press("slash")
        search = app.query_one("#search-bar")
        assert search.is_visible

        await pilot.press("escape")
        assert not search.is_visible
        assert detail.is_visible

        await pilot.press("escape")
        assert not detail.is_visible


@pytest.mark.asyncio
async def test_cancel_matches_back_for_open_layers() -> None:
    """Semantic cancel should share the same close ordering as back."""
    app = MutsumiApp(tasks_path=FIXTURE)
    async with app.run_test() as pilot:
        detail = app.query_one(DetailPanel)
        await pilot.press("j")
        await pilot.press("enter")
        assert detail.is_visible

        app.action_cancel()
        await pilot.pause()
        assert not detail.is_visible


@pytest.mark.asyncio
async def test_onboarding_skip_persists_completion_and_leaves_screen(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Skipping onboarding should still persist completion and continue startup."""
    startup_state = StartupState(
        mode="first_run",
        cwd=tmp_path,
        is_git_repo=False,
        config_exists=False,
        onboarding_completed=False,
        personal_tasks_exists=False,
        project_tasks_exists=False,
        project_registered=False,
    )
    saved_flags: list[bool] = []

    def _save_config(config: object) -> Path:
        saved_flags.append(getattr(config, "onboarding_completed"))
        return tmp_path / "config.toml"

    monkeypatch.setattr("mutsumi.app.save_config", _save_config)

    app = MutsumiApp(tasks_path=FIXTURE, startup_state=startup_state)
    async with app.run_test(size=(80, 24)) as pilot:
        screen = app.screen
        assert isinstance(screen, OnboardingScreen)
        screen.action_skip()
        await pilot.pause()

        assert saved_flags == [True]
        assert app._config.onboarding_completed is True
        assert not isinstance(app.screen, OnboardingScreen)


def test_source_change_ignores_only_matching_self_write_source(monkeypatch: pytest.MonkeyPatch) -> None:
    """Self-write suppression should be scoped to the matching source only."""
    app = MutsumiApp(tasks_path=FIXTURE)
    calls: list[object] = []
    monkeypatch.setattr(app, "call_from_thread", lambda callback: calls.append(callback))

    app._self_writing_sources.add("default")
    app._on_source_changed("default")
    app._on_source_changed("other")

    assert len(calls) == 1
    assert calls[0] == app._reload_from_disk


def test_start_watchers_skips_virtual_main_source(monkeypatch: pytest.MonkeyPatch) -> None:
    """The virtual main source should not register its own watcher."""
    app = MutsumiApp(tasks_path=FIXTURE)
    app._source_registry.add_source("main", FIXTURE)
    app._source_registry.add_source("personal", FIXTURE)
    started: list[str] = []
    monkeypatch.setattr(
        app._source_registry,
        "start_watching",
        lambda name, callback: started.append(name),
    )

    app._start_watchers()

    assert "main" not in started
    assert "default" in started
    assert "personal" in started


def test_write_task_file_to_source_replaces_existing_timer(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """A repeated write to the same source should cancel the previous reset timer."""
    test_file = tmp_path / "tasks.json"
    test_file.write_text(json.dumps({"version": 1, "tasks": []}, indent=2), encoding="utf-8")
    app = MutsumiApp(tasks_path=test_file)

    class _FakeTimer:
        instances: list[object] = []

        def __init__(self, interval: float, callback: object) -> None:
            self.interval = interval
            self.callback = callback
            self.daemon = False
            self.started = False
            self.cancelled = False
            _FakeTimer.instances.append(self)

        def start(self) -> None:
            self.started = True

        def cancel(self) -> None:
            self.cancelled = True

    monkeypatch.setattr("mutsumi.app.threading.Timer", _FakeTimer)

    task_file = app._task_file_for_source("default")
    app._write_task_file_to_source("default", task_file)
    first_timer = app._self_write_timers["default"]
    app._write_task_file_to_source("default", task_file)

    assert len(_FakeTimer.instances) == 2
    assert first_timer.cancelled is True
    assert "default" in app._self_writing_sources
    assert app._self_write_timers["default"] is _FakeTimer.instances[-1]
