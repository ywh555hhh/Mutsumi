"""Mutsumi configuration model."""

from __future__ import annotations

from pathlib import Path  # noqa: TC003  — pydantic needs Path at runtime

from pydantic import BaseModel, ConfigDict


class ProjectEntry(BaseModel):
    """A registered project source."""

    name: str
    path: Path


class MutsumiConfig(BaseModel):
    """Application configuration loaded from config.toml."""

    model_config = ConfigDict(extra="allow")

    theme: str = "monochrome-zen"
    keybindings: str = "arrows"
    language: str = "en"
    default_scope: str = "day"
    notification_mode: str = "quiet"
    key_overrides: dict[str, str] = {}
    event_log_path: Path | None = None
    default_path: Path | None = None
    custom_css_path: Path | None = None
    columns: list[str] = ["checkbox", "title", "tags", "priority"]
    projects: list[ProjectEntry] = []
    default_tab: str = "main"
    dashboard_max_tasks: int = 3
    dashboard_show_completed: bool = True
    onboarding_completed: bool = False
    preferred_agent: str | None = None
    agent_integration_mode: str = "none"
