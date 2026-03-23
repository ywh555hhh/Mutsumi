"""First-run bootstrap state detection for Mutsumi."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Literal

from mutsumi.config import config_exists, get_config

if TYPE_CHECKING:
    from mutsumi.config.settings import MutsumiConfig

StartupMode = Literal["ready", "first_run", "attach_needed"]


@dataclass(frozen=True)
class StartupState:
    """Computed startup state for the current working directory."""

    mode: StartupMode
    cwd: Path
    is_git_repo: bool
    config_exists: bool
    onboarding_completed: bool
    personal_tasks_exists: bool
    project_tasks_exists: bool
    project_registered: bool


def is_git_repo(path: Path | None = None) -> bool:
    """Return True if *path* looks like a Git repository root."""
    repo_path = (path or Path.cwd()).resolve()
    return (repo_path / ".git").exists()


def project_tasks_path(cwd: Path | None = None) -> Path:
    """Return the preferred task file path for a project directory."""
    project_dir = (cwd or Path.cwd()).resolve()
    mutsumi_path = project_dir / "mutsumi.json"
    legacy_path = project_dir / "tasks.json"
    if mutsumi_path.exists():
        return mutsumi_path
    if legacy_path.exists():
        return legacy_path
    return mutsumi_path


def is_registered_project(config: MutsumiConfig, cwd: Path | None = None) -> bool:
    """Return True if the current directory is already registered."""
    project_dir = (cwd or Path.cwd()).resolve()
    return any(project.path.resolve() == project_dir for project in config.projects)


def detect_startup_state(
    cwd: Path | None = None,
    config: MutsumiConfig | None = None,
) -> StartupState:
    """Detect whether startup should launch, bootstrap, or soft-attach."""
    try:
        current_dir = (cwd or Path.cwd()).resolve()
    except (FileNotFoundError, OSError):
        current_dir = Path.home().resolve()
    current_config = config or get_config()
    config_file_exists = config_exists()

    from mutsumi.core.paths import personal_tasks_path

    personal_exists = personal_tasks_path().exists()
    project_file_exists = project_tasks_path(current_dir).exists()
    in_git_repo = is_git_repo(current_dir)
    registered = in_git_repo and is_registered_project(current_config, current_dir)

    first_run = not any((
        config_file_exists,
        personal_exists,
        project_file_exists,
        bool(current_config.projects),
        current_config.onboarding_completed,
    ))

    if first_run:
        mode: StartupMode = "first_run"
    elif current_config.onboarding_completed and in_git_repo and not registered:
        mode = "attach_needed"
    else:
        mode = "ready"

    return StartupState(
        mode=mode,
        cwd=current_dir,
        is_git_repo=in_git_repo,
        config_exists=config_file_exists,
        onboarding_completed=current_config.onboarding_completed,
        personal_tasks_exists=personal_exists,
        project_tasks_exists=project_file_exists,
        project_registered=registered,
    )
