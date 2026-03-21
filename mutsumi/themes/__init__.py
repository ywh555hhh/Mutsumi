"""Theme loading and CSS generation for Mutsumi."""

from __future__ import annotations

from mutsumi.themes.builtin import BUILTIN_THEMES, ThemeColors


def load_theme(name: str) -> ThemeColors:
    """Load a theme by name. Falls back to monochrome-zen if not found."""
    return BUILTIN_THEMES.get(name, BUILTIN_THEMES["monochrome-zen"])


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
