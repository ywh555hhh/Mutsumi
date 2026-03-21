"""Mutsumi configuration model."""

from __future__ import annotations

from pathlib import Path  # noqa: TC003  — pydantic needs Path at runtime

from pydantic import BaseModel, ConfigDict


class MutsumiConfig(BaseModel):
    """Application configuration loaded from config.toml."""

    model_config = ConfigDict(extra="allow")

    theme: str = "monochrome-zen"
    keybindings: str = "vim"
    language: str = "en"
    event_log_path: Path | None = None
    default_path: Path | None = None
    custom_css_path: Path | None = None
    columns: list[str] = ["checkbox", "title", "tags", "priority"]
