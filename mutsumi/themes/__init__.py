"""Theme loading and CSS generation for Mutsumi."""

from __future__ import annotations

import tomllib
from pathlib import Path

from mutsumi.themes.builtin import BUILTIN_THEMES, ThemeColors


def _user_themes_dir() -> Path:
    """Return the user themes directory."""
    from mutsumi.core.paths import mutsumi_config_dir

    return mutsumi_config_dir() / "themes"


def _load_theme_from_toml(path: Path) -> ThemeColors | None:
    """Load a ThemeColors from a TOML file.

    Expected format: flat key-value pairs matching ThemeColors fields.
    Returns None on any error.
    """
    try:
        with open(path, "rb") as f:
            data = tomllib.load(f)
        # Require at least 'name' or use filename stem
        if "name" not in data:
            data["name"] = path.stem
        return ThemeColors(**data)
    except Exception:
        return None


def load_theme(name: str) -> ThemeColors:
    """Load a theme by name.

    Priority: user TOML file > built-in theme > monochrome-zen fallback.
    """
    # Check built-in first (fast path)
    if name in BUILTIN_THEMES:
        return BUILTIN_THEMES[name]

    # Look for user theme file
    user_dir = _user_themes_dir()
    user_file = user_dir / f"{name}.toml"
    if user_file.exists():
        theme = _load_theme_from_toml(user_file)
        if theme is not None:
            return theme

    return BUILTIN_THEMES["monochrome-zen"]


def theme_to_css(theme: ThemeColors) -> str:
    """Generate CSS overrides from a ThemeColors instance."""
    return f"""
    Screen {{
        background: {theme.background};
    }}

    .error-banner {{
        background: {theme.error};
        color: {theme.background};
    }}

    HeaderBar {{
        background: {theme.surface};
    }}

    HeaderBar .title {{
        color: {theme.text_muted};
    }}

    TabButton {{
        color: {theme.text_muted};
    }}

    TabButton.active {{
        color: {theme.accent};
    }}

    TaskListPanel {{
        background: {theme.background};
    }}

    TaskRow {{
        color: {theme.text};
    }}

    TaskRow:focus {{
        background: {theme.surface};
    }}

    TaskRow:hover {{
        background: {theme.surface};
    }}

    TaskRow.done {{
        color: {theme.text_muted};
    }}

    DetailPanel {{
        background: {theme.surface};
        border-left: solid {theme.border};
    }}

    DetailPanel .detail-header {{
        background: {theme.surface};
        color: {theme.accent};
    }}

    DetailPanel .detail-field {{
        color: {theme.text};
    }}

    DetailPanel .detail-label {{
        color: {theme.text_muted};
    }}

    DetailPanel .detail-separator {{
        color: {theme.border};
    }}

    FooterBar {{
        background: {theme.surface};
    }}

    FooterBar .stats {{
        color: {theme.text};
    }}

    FooterBar .mode {{
        color: {theme.text_muted};
    }}
    """
