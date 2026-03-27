"""Tests for help screen semantic-first rendering."""

from __future__ import annotations

import pytest
from textual.app import App

pytest.importorskip("textual")

from mutsumi.tui.help_screen import HelpScreen


class _HelpScreenHarnessApp(App[None]):
    def __init__(self, screen: HelpScreen) -> None:
        super().__init__()
        self._screen = screen

    def on_mount(self) -> None:
        self.push_screen(self._screen)

    def get_css_variables(self) -> dict[str, str]:
        return {
            **super().get_css_variables(),
            "theme-bg": "#000000",
            "theme-surface": "#111111",
            "theme-border": "#222222",
            "theme-text": "#ffffff",
            "theme-text-muted": "#888888",
            "theme-accent": "#00aaff",
        }


@pytest.mark.asyncio
async def test_help_screen_displays_semantic_first_labels() -> None:
    screen = HelpScreen("arrows")
    app = _HelpScreenHarnessApp(screen)

    async with app.run_test():
        text = screen._build_table().plain
        assert "Confirm" in text
        assert "Back" in text
        assert "New" in text
        assert "Edit" in text
        assert "show_detail" not in text
        assert "close_detail" not in text
        assert "new_task" not in text
        assert "edit_task" not in text
