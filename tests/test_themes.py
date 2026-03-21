"""Tests for the theme system."""

from __future__ import annotations

from mutsumi.themes import load_theme, theme_to_css
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


class TestThemeToCss:
    def test_generates_css(self) -> None:
        theme = load_theme("nord")
        css = theme_to_css(theme)
        assert "Screen" in css
        assert theme.background in css
        assert theme.accent in css

    def test_all_themes_produce_valid_css(self) -> None:
        for _name, theme in BUILTIN_THEMES.items():
            css = theme_to_css(theme)
            assert isinstance(css, str)
            assert len(css) > 100
