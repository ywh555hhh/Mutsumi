"""Tests for onboarding and attach screen wiring."""

from __future__ import annotations

from pathlib import Path

import pytest

pytest.importorskip("textual")

from mutsumi.config.settings import MutsumiConfig
from mutsumi.onboarding.bootstrap import StartupState


def test_onboarding_screen_module_imports() -> None:
    from mutsumi.tui.onboarding_screen import OnboardingScreen

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
