"""Tests for onboarding and attach screen wiring."""

from __future__ import annotations

from pathlib import Path

import pytest
from textual.app import App

pytest.importorskip("textual")

from mutsumi.config.settings import MutsumiConfig
from mutsumi.onboarding.bootstrap import StartupState
from mutsumi.tui.onboarding_screen import OnboardingScreen


class _OnboardingHarnessApp(App[None]):
    def __init__(self, screen: OnboardingScreen) -> None:
        super().__init__()
        self._screen = screen

    def on_mount(self) -> None:
        self.push_screen(self._screen)

    def get_css_variables(self) -> dict[str, str]:
        return {
            **super().get_css_variables(),
            "theme-bg": "#000000",
            "theme-surface": "#111111",
            "theme-border": "#222222",
            "theme-text": "#ffffff",
            "theme-text-muted": "#888888",
            "theme-accent": "#00aaff",
        }


def test_onboarding_screen_module_imports() -> None:
    screen = OnboardingScreen(MutsumiConfig(), is_git_repo=False)
    assert screen is not None


def test_project_attach_screen_module_imports() -> None:
    from mutsumi.tui.project_attach_screen import ProjectAttachScreen

    screen = ProjectAttachScreen()
    assert screen is not None


def test_startup_state_attach_mode_shape() -> None:
    state = StartupState(
        mode="attach_needed",
        cwd=Path.cwd(),
        is_git_repo=True,
        config_exists=True,
        onboarding_completed=True,
        personal_tasks_exists=True,
        project_tasks_exists=False,
        project_registered=False,
    )
    assert state.mode == "attach_needed"


def test_onboarding_finished_message_shape() -> None:
    msg = OnboardingScreen.Finished(
        selections={
            "language": "zh",
            "keybindings": "vim",
            "theme": "nord",
            "workspace_mode": "personal+project",
            "preferred_agent": "claude-code",
        },
        skipped=False,
    )
    assert msg.selections["preferred_agent"] == "claude-code"
    assert not msg.skipped


def test_onboarding_finished_skip_message() -> None:
    msg = OnboardingScreen.Finished(
        selections={
            "language": "en",
            "keybindings": "arrows",
            "theme": "monochrome-zen",
            "workspace_mode": "personal-only",
            "preferred_agent": "none",
        },
        skipped=True,
    )
    assert msg.skipped
    assert msg.selections["preferred_agent"] == "none"


def test_onboarding_default_selections_no_git() -> None:
    screen = OnboardingScreen(MutsumiConfig(), is_git_repo=False)
    assert screen._selections["workspace_mode"] == "personal-only"
    assert screen._selections["preferred_agent"] == "none"


def test_onboarding_default_selections_git_repo() -> None:
    screen = OnboardingScreen(MutsumiConfig(), is_git_repo=True)
    assert screen._selections["workspace_mode"] == "personal+project"


@pytest.mark.asyncio
async def test_onboarding_vertical_navigation_moves_between_rows() -> None:
    screen = OnboardingScreen(MutsumiConfig(), is_git_repo=False)
    app = _OnboardingHarnessApp(screen)

    async with app.run_test() as pilot:
        assert screen._active_row == 0
        await pilot.press("down")
        assert screen._active_row == 1
        await pilot.press("up")
        assert screen._active_row == 0


@pytest.mark.asyncio
async def test_onboarding_horizontal_navigation_changes_current_row_option() -> None:
    screen = OnboardingScreen(MutsumiConfig(), is_git_repo=False)
    app = _OnboardingHarnessApp(screen)

    async with app.run_test() as pilot:
        assert screen._selections["language"] == "en"
        await pilot.press("right")
        assert screen._selections["language"] == "zh"
        assert screen._active_row == 0
        await pilot.press("left")
        assert screen._selections["language"] == "en"


@pytest.mark.asyncio
async def test_onboarding_cta_row_uses_left_right_and_enter() -> None:
    screen = OnboardingScreen(MutsumiConfig(), is_git_repo=False)
    app = _OnboardingHarnessApp(screen)

    async with app.run_test() as pilot:
        for _ in range(len(screen._selections)):
            await pilot.press("down")
        assert screen._active_row == len(screen._selections)
        assert screen._active_cta == 0

        await pilot.press("right")
        assert screen._active_cta == 1

        await pilot.press("left")
        assert screen._active_cta == 0

        await pilot.press("enter")
        await pilot.pause()
        assert len(app.screen_stack) == 1
