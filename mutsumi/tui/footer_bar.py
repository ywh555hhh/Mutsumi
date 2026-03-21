"""Footer bar widget with mode indicator, stats, and bar switching."""

from __future__ import annotations

from enum import StrEnum, auto
from typing import TYPE_CHECKING, Any

from textual.containers import Horizontal
from textual.message import Message
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Static

if TYPE_CHECKING:
    from textual.app import ComposeResult
    from textual.events import Resize


class BarMode(StrEnum):
    """Current mode of the footer bar."""

    NORMAL = auto()
    SEARCH = auto()
    CONFIRM = auto()
    NOTIFICATION = auto()


_MODE_STYLES: dict[BarMode, tuple[str, str]] = {
    # (label, color)
    BarMode.NORMAL: ("NORMAL", "#666666"),
    BarMode.SEARCH: ("SEARCH", "#5de4c7"),
    BarMode.CONFIRM: ("CONFIRM", "#e06c75"),
    BarMode.NOTIFICATION: ("NORMAL", "#666666"),
}


class _ClickableAction(Static):
    """A clickable label that acts like a button in a 1-line bar."""

    DEFAULT_CSS = """
    _ClickableAction {
        width: auto;
        height: 1;
        padding: 0 1;
        color: #5de4c7;
    }

    _ClickableAction:hover {
        background: #2a2a2a;
        color: #ffffff;
    }
    """

    def __init__(self, label: str, action_name: str, **kwargs: Any) -> None:
        super().__init__(label, **kwargs)
        self._action_name = action_name

    def on_click(self) -> None:
        parent = self.parent
        while parent is not None:
            if isinstance(parent, FooterBar):
                parent.post_message(FooterBar.ActionRequested(self._action_name))
                break
            parent = parent.parent


class FooterBar(Widget):
    """Bottom status bar with mode indicator and bar switching.

    Modes:
      - NORMAL:       show stats + action buttons + mode badge
      - SEARCH:       show stats + mode badge (cyan)
      - CONFIRM:      show confirm prompt (red badge)
      - NOTIFICATION: show temporary message, auto-reset
    """

    DEFAULT_CSS = """
    FooterBar {
        dock: bottom;
        height: 2;
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

    FooterBar .hint-bar {
        height: 1;
        width: 100%;
        padding: 0 1;
        color: #555555;
    }

    FooterBar .mode-badge {
        width: auto;
        padding: 0 1;
        color: #666666;
    }
    """

    bar_mode: reactive[BarMode] = reactive(BarMode.NORMAL)

    class ActionRequested(Message):
        """Posted when a footer action button is clicked."""

        def __init__(self, action: str) -> None:
            self.action = action
            super().__init__()

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
        yield Static(
            "[x]=toggle done \u2502 click title=detail/edit \u2502 ?=help",
            classes="hint-bar",
            id="hint-bar",
        )
        with Horizontal():
            yield Static(self._format_stats(), classes="stats", id="stats-text")
            yield _ClickableAction("\\[+New]", "new_task", id="btn-new")
            yield _ClickableAction("\\[/Search]", "search", id="btn-search")
            yield Static("NORMAL", classes="mode-badge", id="mode-badge")

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

    def set_mode(self, mode: BarMode) -> None:
        """Switch the bar mode and update the badge."""
        self.bar_mode = mode

    def watch_bar_mode(self, new_mode: BarMode) -> None:
        """Update badge text and color when mode changes."""
        try:
            badge = self.query_one("#mode-badge", Static)
            label, color = _MODE_STYLES[new_mode]
            badge.update(label)
            badge.styles.color = color
        except Exception:
            pass

    def show_notification(self, message: str, duration: float = 1.5) -> None:
        """Show a temporary notification message in the stats area.

        Reverts to normal stats after *duration* seconds.
        """
        try:
            stats_widget = self.query_one("#stats-text", Static)
            stats_widget.update(message)
            self.set_mode(BarMode.NOTIFICATION)
            self.set_timer(duration, self._restore_stats)
        except Exception:
            pass

    def _restore_stats(self) -> None:
        """Restore stats text and mode after notification."""
        try:
            stats_widget = self.query_one("#stats-text", Static)
            stats_widget.update(self._format_stats())
            self.set_mode(BarMode.NORMAL)
        except Exception:
            pass

    def reset(self) -> None:
        """Reset to NORMAL mode."""
        self.set_mode(BarMode.NORMAL)

    def on_resize(self, event: Resize) -> None:
        """Hide buttons at narrow widths to prevent crowding."""
        try:
            btn_new = self.query_one("#btn-new", _ClickableAction)
            btn_search = self.query_one("#btn-search", _ClickableAction)
            badge = self.query_one("#mode-badge", Static)
        except Exception:
            return
        w = event.size.width
        if w < 50:
            btn_new.display = False
            btn_search.display = False
            badge.display = False
        elif w < 70:
            btn_new.display = True
            btn_search.display = False
            badge.display = True
        else:
            btn_new.display = True
            btn_search.display = True
            badge.display = True
