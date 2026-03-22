"""Configuration loading for Mutsumi.

Config search chain (first found wins):
  1. ~/.mutsumi/config.toml    (new unified home)
  2. ~/.config/mutsumi/config.toml  (legacy XDG)
  3. %APPDATA%/mutsumi/config.toml  (Windows legacy)
Falls back to defaults if no file is found.
"""

from __future__ import annotations

import tomllib
from typing import TYPE_CHECKING

from mutsumi.config.settings import MutsumiConfig

if TYPE_CHECKING:
    from pathlib import Path

_config: MutsumiConfig | None = None


def _config_search_chain() -> list[Path]:
    """Return config file candidates in priority order."""
    from mutsumi.core.paths import mutsumi_config_dir, mutsumi_home

    return [
        mutsumi_home() / "config.toml",
        mutsumi_config_dir() / "config.toml",
    ]


def _config_path() -> Path:
    """Return the first existing config.toml, or the preferred location."""
    candidates = _config_search_chain()
    for p in candidates:
        if p.exists():
            return p
    return candidates[0]  # preferred location (for error messages)


def config_exists() -> bool:
    """Return True if any supported config file exists."""
    return any(path.exists() for path in _config_search_chain())


def get_config_path() -> Path:
    """Return the active or preferred config file path."""
    return _config_path()


def load_config(path: Path | None = None) -> MutsumiConfig:
    """Load configuration from TOML file.

    Returns default config if the file doesn't exist or is invalid.
    """
    global _config  # noqa: PLW0603
    config_file = path or _config_path()

    if config_file.exists():
        try:
            with open(config_file, "rb") as f:
                data = tomllib.load(f)
            _config = MutsumiConfig(**data)
        except Exception:
            _config = MutsumiConfig()
    else:
        _config = MutsumiConfig()

    return _config


def get_config() -> MutsumiConfig:
    """Get the current config, loading defaults if not yet loaded."""
    global _config  # noqa: PLW0603
    if _config is None:
        _config = load_config()
    return _config


def reset_config() -> None:
    """Reset the global config (for testing)."""
    global _config  # noqa: PLW0603
    _config = None


def save_config(config: MutsumiConfig | None = None, path: Path | None = None) -> Path:
    """Save configuration to TOML file (simple serializer, no extra deps).

    Returns the path written to.
    """
    from mutsumi.core.paths import mutsumi_home

    cfg = config or get_config()
    dest = path or (mutsumi_home() / "config.toml")
    dest.parent.mkdir(parents=True, exist_ok=True)

    lines: list[str] = []

    def _quote(v: str) -> str:
        escaped = v.replace("\\", "\\\\").replace('"', '\\"')
        return f'"{escaped}"'

    # Simple scalar fields
    for field_name in (
        "theme", "keybindings", "language", "default_scope",
        "notification_mode", "default_tab", "agent_integration_mode",
    ):
        val = getattr(cfg, field_name, None)
        if val is not None:
            lines.append(f"{field_name} = {_quote(str(val))}")

    # Integer fields
    for field_name in ("dashboard_max_tasks",):
        val = getattr(cfg, field_name, None)
        if val is not None:
            lines.append(f"{field_name} = {val}")

    # Boolean fields
    for field_name in ("dashboard_show_completed", "onboarding_completed"):
        val = getattr(cfg, field_name, None)
        if val is not None:
            lines.append(f"{field_name} = {'true' if val else 'false'}")

    # Path fields
    for field_name in ("event_log_path", "default_path", "custom_css_path"):
        val = getattr(cfg, field_name, None)
        if val is not None:
            lines.append(f"{field_name} = {_quote(str(val))}")

    if cfg.preferred_agent is not None:
        lines.append(f"preferred_agent = {_quote(cfg.preferred_agent)}")

    # Columns list
    if cfg.columns:
        cols = ", ".join(_quote(c) for c in cfg.columns)
        lines.append(f"columns = [{cols}]")

    # Key overrides
    if cfg.key_overrides:
        lines.append("")
        lines.append("[key_overrides]")
        for k, v in cfg.key_overrides.items():
            lines.append(f"{k} = {_quote(v)}")

    # Projects
    for proj in cfg.projects:
        lines.append("")
        lines.append("[[projects]]")
        lines.append(f"name = {_quote(proj.name)}")
        lines.append(f"path = {_quote(str(proj.path))}")

    lines.append("")  # trailing newline
    dest.write_text("\n".join(lines), encoding="utf-8")
    return dest
