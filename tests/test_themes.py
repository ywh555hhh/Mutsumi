"""Tests for the theme system."""

from __future__ import annotations

from mutsumi.themes import get_theme, load_theme
from mutsumi.themes.builtin import BUILTIN_THEMES


class TestThemeColors:
    def test_monochrome_zen(self) -> None:
        theme = BUILTIN_THEMES["monochrome-zen"]
        assert theme.name == "monochrome-zen"
        assert theme.background == "#0f0f0f"

    def test_nord(self) -> None:
        theme = BUILTIN_THEMES["nord"]
        assert theme.name == "nord"
        assert theme.accent == "#88c0d0"

    def test_dracula(self) -> None:
        theme = BUILTIN_THEMES["dracula"]
        assert theme.name == "dracula"
        assert theme.accent == "#bd93f9"

    def test_solarized(self) -> None:
        theme = BUILTIN_THEMES["solarized"]
        assert theme.name == "solarized"
        assert theme.accent == "#2aa198"

    def test_four_builtin_themes(self) -> None:
        assert len(BUILTIN_THEMES) == 4

    def test_frozen(self) -> None:
        theme = BUILTIN_THEMES["nord"]
        try:
            theme.background = "#000000"  # type: ignore[misc]
            raised = False
        except AttributeError:
            raised = True
        assert raised


class TestLoadTheme:
    def test_load_existing(self) -> None:
        theme = load_theme("nord")
        assert theme.name == "nord"

    def test_load_fallback(self) -> None:
        theme = load_theme("nonexistent")
        assert theme.name == "monochrome-zen"

    def test_load_sets_global(self) -> None:
        load_theme("dracula")
        assert get_theme().name == "dracula"
        # restore default
        load_theme("monochrome-zen")

    def test_get_theme_returns_current(self) -> None:
        load_theme("solarized")
        theme = get_theme()
        assert theme.name == "solarized"
        assert theme.accent == "#2aa198"
        # restore default
        load_theme("monochrome-zen")
