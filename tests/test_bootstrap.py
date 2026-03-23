"""Tests for startup bootstrap state and reusable onboarding helpers."""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import patch

from mutsumi.config import reset_config
from mutsumi.config.settings import MutsumiConfig, ProjectEntry
from mutsumi.onboarding.bootstrap import detect_startup_state, project_tasks_path
from mutsumi.onboarding.files import ensure_project_task_file, register_project

if TYPE_CHECKING:
    from pathlib import Path


class TestDetectStartupState:
    def test_first_run_when_nothing_exists(self, tmp_path: Path) -> None:
        reset_config()
        home_dir = tmp_path / ".mutsumi"
        cwd = tmp_path / "workspace"
        cwd.mkdir()

        with patch("mutsumi.onboarding.bootstrap.config_exists", return_value=False), \
             patch("mutsumi.core.paths.mutsumi_home", return_value=home_dir):
            state = detect_startup_state(cwd=cwd, config=MutsumiConfig())

        assert state.mode == "first_run"
        assert state.project_registered is False
        assert state.personal_tasks_exists is False

    def test_attach_needed_for_new_git_repo_after_onboarding(self, tmp_path: Path) -> None:
        reset_config()
        home_dir = tmp_path / ".mutsumi"
        cwd = tmp_path / "repo"
        cwd.mkdir()
        (cwd / ".git").mkdir()

        config = MutsumiConfig(onboarding_completed=True)
        with patch("mutsumi.onboarding.bootstrap.config_exists", return_value=True), \
             patch("mutsumi.core.paths.mutsumi_home", return_value=home_dir):
            state = detect_startup_state(cwd=cwd, config=config)

        assert state.mode == "attach_needed"
        assert state.is_git_repo is True
        assert state.project_registered is False

    def test_ready_when_project_already_registered(self, tmp_path: Path) -> None:
        reset_config()
        home_dir = tmp_path / ".mutsumi"
        cwd = tmp_path / "repo"
        cwd.mkdir()
        (cwd / ".git").mkdir()

        config = MutsumiConfig(
            onboarding_completed=True,
            projects=[ProjectEntry(name="repo", path=cwd)],
        )
        with patch("mutsumi.onboarding.bootstrap.config_exists", return_value=True), \
             patch("mutsumi.core.paths.mutsumi_home", return_value=home_dir):
            state = detect_startup_state(cwd=cwd, config=config)

        assert state.mode == "ready"
        assert state.project_registered is True


class TestOnboardingFiles:
    def test_project_tasks_path_prefers_legacy_when_present(self, tmp_path: Path) -> None:
        legacy = tmp_path / "tasks.json"
        legacy.write_text("{}", encoding="utf-8")
        assert project_tasks_path(tmp_path) == legacy

    def test_ensure_project_task_file_creates_mutsumi_json(self, tmp_path: Path) -> None:
        path = ensure_project_task_file(tmp_path)
        assert path == tmp_path / "mutsumi.json"
        assert path.exists()

    def test_register_project_deduplicates_by_path(self, tmp_path: Path) -> None:
        config = MutsumiConfig(projects=[ProjectEntry(name="existing", path=tmp_path)])
        added, entry = register_project(config, tmp_path, "another")
        assert added is False
        assert entry.name == "existing"

    def test_detect_state_sees_personal_file_for_known_user(self, tmp_path: Path) -> None:
        personal_dir = tmp_path / ".mutsumi"
        personal_dir.mkdir()
        (personal_dir / "mutsumi.json").write_text('{"version": 1, "tasks": []}', encoding="utf-8")
        cwd = tmp_path / "workspace"
        cwd.mkdir()

        with patch("mutsumi.onboarding.bootstrap.config_exists", return_value=False), \
             patch("mutsumi.core.paths.mutsumi_home", return_value=personal_dir):
            state = detect_startup_state(cwd=cwd, config=MutsumiConfig())

        assert state.personal_tasks_exists is True
        assert state.mode == "ready"
