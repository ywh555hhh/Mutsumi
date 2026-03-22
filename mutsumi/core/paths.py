"""Cross-platform path helpers for Mutsumi.

Provides config and data directories that follow platform conventions:
- Linux/macOS: XDG ($XDG_CONFIG_HOME, $XDG_DATA_HOME) with ~/.config / ~/.local/share fallback
- Windows: %APPDATA% for config, %LOCALAPPDATA% for data

The unified home directory (~/.mutsumi/ or %APPDATA%/mutsumi) is the
preferred location for config and personal tasks starting with v0.6.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

_IS_WINDOWS = sys.platform == "win32"


def config_home() -> Path:
    """Return the platform-appropriate config base directory.

    - Linux/macOS: $XDG_CONFIG_HOME or ~/.config
    - Windows: %APPDATA% or ~/AppData/Roaming
    """
    if _IS_WINDOWS:
        appdata = os.environ.get("APPDATA")
        if appdata:
            return Path(appdata)
        return Path.home() / "AppData" / "Roaming"

    xdg = os.environ.get("XDG_CONFIG_HOME")
    if xdg:
        return Path(xdg)
    return Path.home() / ".config"


def data_home() -> Path:
    """Return the platform-appropriate data base directory.

    - Linux/macOS: $XDG_DATA_HOME or ~/.local/share
    - Windows: %LOCALAPPDATA% or ~/AppData/Local
    """
    if _IS_WINDOWS:
        local = os.environ.get("LOCALAPPDATA")
        if local:
            return Path(local)
        return Path.home() / "AppData" / "Local"

    xdg = os.environ.get("XDG_DATA_HOME")
    if xdg:
        return Path(xdg)
    return Path.home() / ".local" / "share"


def mutsumi_home() -> Path:
    """Return the unified Mutsumi home directory.

    - Linux/macOS: ~/.mutsumi
    - Windows: %APPDATA%/mutsumi
    """
    if _IS_WINDOWS:
        appdata = os.environ.get("APPDATA")
        if appdata:
            return Path(appdata) / "mutsumi"
        return Path.home() / "AppData" / "Roaming" / "mutsumi"
    return Path.home() / ".mutsumi"


def personal_tasks_path() -> Path:
    """Return the path to the personal (global) task file.

    ~/.mutsumi/mutsumi.json (or %APPDATA%/mutsumi/mutsumi.json on Windows)
    """
    return mutsumi_home() / "mutsumi.json"


def mutsumi_config_dir() -> Path:
    """Return the Mutsumi config directory (e.g. ~/.config/mutsumi).

    Legacy location — prefer mutsumi_home() for new installs.
    """
    return config_home() / "mutsumi"


def mutsumi_data_dir() -> Path:
    """Return the Mutsumi data directory (e.g. ~/.local/share/mutsumi)."""
    return data_home() / "mutsumi"
