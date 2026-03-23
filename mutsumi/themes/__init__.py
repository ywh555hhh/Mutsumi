"""Theme loading and CSS generation for Mutsumi."""

from __future__ import annotations

import tomllib
from typing import TYPE_CHECKING

from mutsumi.themes.builtin import BUILTIN_THEMES, ThemeColors

if TYPE_CHECKING:
    from pathlib import Path

# Global theme singleton — set by load_theme(), read by get_theme()
_current_theme: ThemeColors = BUILTIN_THEMES["monochrome-zen"]


def get_theme() -> ThemeColors:
    """Return the currently loaded theme colors."""
    return _current_theme


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
    """Load a theme by name and set it as the current global theme.

    Priority: user TOML file > built-in theme > monochrome-zen fallback.
    """
    global _current_theme
    # Check built-in first (fast path)
    if name in BUILTIN_THEMES:
        _current_theme = BUILTIN_THEMES[name]
        return _current_theme

    # Look for user theme file
    user_dir = _user_themes_dir()
    user_file = user_dir / f"{name}.toml"
    if user_file.exists():
        theme = _load_theme_from_toml(user_file)
        if theme is not None:
            _current_theme = theme
            return _current_theme

    _current_theme = BUILTIN_THEMES["monochrome-zen"]
    return _current_theme


def theme_to_css(theme: ThemeColors) -> str:
    """Generate CSS overrides from a ThemeColors instance.

    Covers ALL TUI widgets so that switching themes works fully.
    The DEFAULT_CSS in each widget defines *layout*; this function
    overrides all *color* properties.
    """
    return f"""
    /* --- Screen --- */
    Screen {{
        background: {theme.background};
    }}

    .error-banner {{
        background: {theme.error};
        color: {theme.background};
    }}

    /* --- HeaderBar --- */
    HeaderBar {{
        background: {theme.surface};
    }}

    HeaderBar .title {{
        color: {theme.text_muted};
    }}

    TabButton {{
        color: {theme.text_muted};
    }}

    TabButton:hover {{
        color: {theme.text};
        background: {theme.surface};
    }}

    TabButton.active {{
        color: {theme.accent};
        background: {theme.background};
    }}

    TabButton.active:hover {{
        color: {theme.accent};
    }}

    /* --- ScopeFilter --- */
    ScopeFilter {{
        background: {theme.surface};
    }}

    ScopeFilter .scope-sep {{
        color: {theme.border};
    }}

    _ScopeButton {{
        color: {theme.text_muted};
    }}

    _ScopeButton:hover {{
        color: {theme.text};
        background: {theme.background};
    }}

    _ScopeButton.active {{
        color: {theme.accent};
    }}

    _ScopeButton.active:focus {{
        color: {theme.accent};
    }}

    _MainButton {{
        color: {theme.accent};
    }}

    _MainButton:hover {{
        color: {theme.text};
        background: {theme.background};
    }}

    /* --- TaskListPanel --- */
    TaskListPanel {{
        background: {theme.background};
    }}

    /* --- TaskRow --- */
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

    TaskRow .inline-edit {{
        background: {theme.surface};
        color: {theme.text};
    }}

    /* --- PriorityGroupHeader --- */
    PriorityGroupHeader {{
        color: {theme.text_muted};
    }}

    PriorityGroupHeader:hover {{
        background: {theme.surface};
    }}

    PriorityGroupHeader:focus {{
        background: {theme.surface};
    }}

    /* --- DetailPanel --- */
    DetailPanel {{
        background: {theme.surface};
        border-left: solid {theme.border};
    }}

    DetailPanel .detail-topbar {{
        background: {theme.surface};
    }}

    DetailPanel .detail-topbar-title {{
        color: {theme.accent};
    }}

    DetailPanel .detail-close-btn {{
        color: {theme.text_muted};
    }}

    DetailPanel .detail-close-btn:hover {{
        color: {theme.error};
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

    DetailPanel .detail-actions {{
        background: {theme.surface};
    }}

    DetailPanel .detail-action-btn {{
        color: {theme.accent};
    }}

    DetailPanel .detail-action-btn:hover {{
        background: {theme.background};
        color: {theme.text};
    }}

    DetailPanel .detail-delete-btn {{
        color: {theme.error};
    }}

    _ResponsiveSeparator {{
        color: {theme.border};
    }}

    /* --- FooterBar --- */
    FooterBar {{
        background: {theme.surface};
    }}

    FooterBar .stats {{
        color: {theme.text};
    }}

    FooterBar .hint-bar {{
        color: {theme.text_muted};
    }}

    FooterBar .mode {{
        color: {theme.text_muted};
    }}

    _ClickableAction {{
        color: {theme.accent};
    }}

    _ClickableAction:hover {{
        background: {theme.background};
        color: {theme.text};
    }}

    /* --- SearchBar --- */
    SearchBar {{
        background: {theme.surface};
    }}

    SearchBar .search-icon {{
        color: {theme.accent};
    }}

    SearchBar Input {{
        background: {theme.surface};
    }}

    /* --- ConfirmBar --- */
    ConfirmBar {{
        background: {theme.surface};
    }}

    ConfirmBar .prompt {{
        color: {theme.error};
    }}

    /* --- ConfirmDialog --- */
    ConfirmDialog > Vertical {{
        background: {theme.surface};
        border: solid {theme.error};
    }}

    ConfirmDialog .confirm-message {{
        color: {theme.text};
    }}

    /* --- TaskForm --- */
    TaskForm > VerticalScroll {{
        background: {theme.surface};
        border: solid {theme.border};
    }}

    TaskForm .form-title {{
        color: {theme.accent};
    }}

    TaskForm Label {{
        color: {theme.text};
    }}

    /* --- MainDashboard --- */
    MainDashboard .dashboard-title {{
        color: {theme.accent};
    }}

    SourceCard {{
        background: {theme.surface};
        border: solid {theme.border};
    }}

    SourceCard:hover {{
        border: solid {theme.text_muted};
    }}

    SourceCard:focus {{
        border: solid {theme.accent};
    }}

    SourceCard .card-header {{
        color: {theme.accent};
    }}

    SourceCard .card-progress {{
        color: {theme.text_muted};
    }}

    SourceCard .card-tasks {{
        color: {theme.text_muted};
    }}

    /* --- EmptyState --- */
    EmptyState .hint {{
        color: {theme.text_muted};
    }}

    _NewTaskButton {{
        color: {theme.accent};
    }}

    _NewTaskButton:hover {{
        background: {theme.surface};
        color: {theme.text};
    }}

    /* --- OnboardingScreen --- */
    OnboardingScreen > VerticalScroll {{
        background: {theme.surface};
        border: solid {theme.border};
    }}

    OnboardingScreen .ob-title {{
        color: {theme.accent};
    }}

    OnboardingScreen .ob-subtitle {{
        color: {theme.text_muted};
    }}

    OnboardingScreen .setting-label {{
        color: {theme.text};
    }}

    /* --- ProjectAttachScreen --- */
    ProjectAttachScreen > Vertical {{
        background: {theme.surface};
        border: solid {theme.border};
    }}

    ProjectAttachScreen .title {{
        color: {theme.accent};
    }}

    ProjectAttachScreen .description {{
        color: {theme.text};
    }}

    /* --- HelpScreen / SortBar --- */
    HelpScreen > Static {{
        background: {theme.surface};
        border: solid {theme.border};
    }}

    SortBar > Static {{
        background: {theme.surface};
        border: solid {theme.border};
    }}
    """
