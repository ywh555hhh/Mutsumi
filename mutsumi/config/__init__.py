"""Configuration loading for Mutsumi.

Reads from XDG config path: ~/.config/mutsumi/config.toml
Falls back to defaults if file is missing.
"""

from __future__ import annotations

import os
import tomllib
from pathlib import Path

from mutsumi.config.settings import MutsumiConfig

_config: MutsumiConfig | None = None


def _xdg_config_home() -> Path:
    """Return XDG_CONFIG_HOME or default (~/.config)."""
    xdg = os.environ.get("XDG_CONFIG_HOME")
    if xdg:
        return Path(xdg)
    return Path.home() / ".config"


def _config_path() -> Path:
    """Return the path to mutsumi's config.toml."""
    return _xdg_config_home() / "mutsumi" / "config.toml"


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
