"""Footer bar widget with task statistics."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from textual.containers import Horizontal
from textual.widget import Widget
from textual.widgets import Static

if TYPE_CHECKING:
    from textual.app import ComposeResult


class FooterBar(Widget):
    """Bottom status bar showing task statistics."""

    DEFAULT_CSS = """
    FooterBar {
        dock: bottom;
        height: 1;
        background: #1a1a1a;
    }

    FooterBar > Horizontal {
        height: 1;
        width: 100%;
    }

    FooterBar .stats {
        width: 1fr;
        padding: 0 1;
        color: #e0e0e0;
    }

    FooterBar .mode {
        width: auto;
        padding: 0 1;
        color: #666666;
    }
    """

    def __init__(
        self,
        total: int = 0,
        done: int = 0,
        pending: int = 0,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self._total = total
        self._done = done
        self._pending = pending

    def compose(self) -> ComposeResult:
        with Horizontal():
            yield Static(self._format_stats(), classes="stats", id="stats-text")
            yield Static("quiet", classes="mode")

    def _format_stats(self) -> str:
        return f"{self._total} tasks \u00b7 {self._done} done \u00b7 {self._pending} pending"

    def update_stats(self, total: int, done: int, pending: int) -> None:
        """Update the displayed statistics."""
        self._total = total
        self._done = done
        self._pending = pending
        try:
            stats_widget = self.query_one("#stats-text", Static)
            stats_widget.update(self._format_stats())
        except Exception:
            pass
