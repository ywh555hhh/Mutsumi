"""Search bar widget — / to open, realtime filter, Esc to close."""

from __future__ import annotations

from typing import TYPE_CHECKING

from textual.containers import Horizontal
from textual.message import Message
from textual.widget import Widget
from textual.widgets import Input, Static

if TYPE_CHECKING:
    from textual.app import ComposeResult
    from textual.events import Key


class SearchBar(Widget):
    """Inline search bar for filtering tasks."""

    DEFAULT_CSS = """
    SearchBar {
        dock: top;
        height: 1;
        background: #1a1a1a;
        display: none;
    }

    SearchBar.visible {
        display: block;
    }

    SearchBar > Horizontal {
        height: 1;
        width: 100%;
    }

    SearchBar .search-icon {
        width: 3;
        padding: 0 0 0 1;
        color: #5de4c7;
    }

    SearchBar Input {
        width: 1fr;
        height: 1;
        border: none;
        background: #1a1a1a;
    }
    """

    class QueryChanged(Message):
        """Posted when search query changes."""

        def __init__(self, query: str) -> None:
            self.query = query
            super().__init__()

    class SearchClosed(Message):
        """Posted when search is closed."""

    def compose(self) -> ComposeResult:
        with Horizontal():
            yield Static("/", classes="search-icon")
            inp = Input(placeholder="Search...", id="search-input")
            inp.can_focus = False  # disabled until show() is called
            yield inp

    def show(self) -> None:
        """Show search bar and focus input."""
        self.add_class("visible")
        try:
            inp = self.query_one("#search-input", Input)
            inp.can_focus = True
            inp.value = ""
            inp.focus()
        except Exception:
            pass

    def hide(self) -> None:
        """Hide search bar and clear query."""
        self.remove_class("visible")
        try:
            inp = self.query_one("#search-input", Input)
            inp.can_focus = False
            inp.value = ""
        except Exception:
            pass
        self.post_message(self.SearchClosed())

    @property
    def is_visible(self) -> bool:
        return self.has_class("visible")

    def on_input_changed(self, event: Input.Changed) -> None:
        """Forward input changes as search queries."""
        self.post_message(self.QueryChanged(event.value))

    def on_key(self, event: Key) -> None:
        """Intercept keys while search input is focused to prevent leaking."""
        if event.key == "escape":
            event.stop()
            event.prevent_default()
            self.hide()
            return
        # Stop all single-char keys from leaking to App bindings
        # while the search input is focused (q, j, k, d, n, e, etc.)
        if self.is_visible and len(event.key) == 1:
            event.stop()
