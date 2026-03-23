"""Reusable onboarding file and project helpers."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

from mutsumi.config import save_config
from mutsumi.config.settings import MutsumiConfig, ProjectEntry
from mutsumi.onboarding.bootstrap import project_tasks_path

if TYPE_CHECKING:
    from pathlib import Path

_TEMPLATE = {
    "version": 1,
    "tasks": [
        {
            "id": "example-001",
            "title": "My first task",
            "status": "pending",
            "scope": "day",
            "priority": "normal",
            "tags": [],
            "children": [],
        }
    ],
}


def write_task_template(path: Path) -> None:
    """Write the default task template to *path*."""
    path.parent.mkdir(parents=True, exist_ok=True)
    content = json.dumps(_TEMPLATE, indent=2, ensure_ascii=False) + "\n"
    path.write_text(content, encoding="utf-8")


def ensure_config_file(
    config: MutsumiConfig | None = None,
    path: Path | None = None,
) -> Path:
    """Create config.toml if it does not exist and return its path."""
    cfg = config or MutsumiConfig()
    dest = path or save_config(cfg)
    if not dest.exists():
        save_config(cfg, dest)
    return dest


def ensure_personal_task_file(force: bool = False) -> Path:
    """Create the personal task file if needed and return its path."""
    from mutsumi.core.paths import personal_tasks_path

    path = personal_tasks_path()
    if force or not path.exists():
        write_task_template(path)
    return path


def ensure_project_task_file(project_dir: Path | None = None, force: bool = False) -> Path:
    """Create the project task file if needed and return its path."""
    path = project_tasks_path(project_dir)
    if force or not path.exists():
        write_task_template(path)
    return path


def register_project(
    config: MutsumiConfig,
    path: Path,
    name: str | None = None,
) -> tuple[bool, ProjectEntry]:
    """Register a project path unless it already exists."""
    project_path = path.resolve()
    project_name = name or project_path.name

    for existing in config.projects:
        if existing.name == project_name or existing.path.resolve() == project_path:
            return False, existing

    entry = ProjectEntry(name=project_name, path=project_path)
    config.projects.append(entry)
    return True, entry
