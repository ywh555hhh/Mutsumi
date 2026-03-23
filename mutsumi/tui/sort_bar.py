"""Sort bar — horizontal picker for sorting tasks by field."""

from __future__ import annotations

import contextlib
from typing import TYPE_CHECKING

from textual.message import Message
from textual.screen import ModalScreen
from textual.widgets import Static

if TYPE_CHECKING:
    from textual.app import ComposeResult

_SORT_FIELDS = ["title", "priority", "status", "due"]


class SortBar(ModalScreen[None]):
    """A small overlay showing sort options.

    Arrow left/right (or h/l, j/k) to select, Enter to confirm, Escape to cancel.
    """

    DEFAULT_CSS = """
    SortBar {
        align: center middle;
    }

    SortBar > Static {
        width: auto;
        height: 3;
        background: $theme-surface;
        border: tall $theme-border;
        padding: 0 2;
    }
    """

    BINDINGS = [
        ("escape", "cancel", "Cancel"),
        ("enter", "confirm", "Confirm"),
        ("left", "prev_field", "Prev"),
        ("right", "next_field", "Next"),
        ("h", "prev_field", "Prev"),
        ("l", "next_field", "Next"),
        ("j", "next_field", "Next"),
        ("k", "prev_field", "Prev"),
    ]

    class SortSelected(Message):
        """Posted when a sort field is chosen."""

        def __init__(self, field: str, reverse: bool) -> None:
            self.field = field
            self.reverse = reverse
            super().__init__()

    def __init__(self) -> None:
        super().__init__()
        self._selected = 0
        self._reverse = False

    def compose(self) -> ComposeResult:
        yield Static(self._render_bar(), id="sort-display")

    def _render_bar(self) -> str:
        parts: list[str] = []
        for i, field in enumerate(_SORT_FIELDS):
            if i == self._selected:
                arrow = "\u25bc" if self._reverse else "\u25b2"
                parts.append(f"\\[{field} {arrow}]")
            else:
                parts.append(f" {field} ")
        return "Sort by:  " + "  ".join(parts) + "   (Enter=confirm, r=reverse, Esc=cancel)"

    def _update_display(self) -> None:
        with contextlib.suppress(Exception):
            self.query_one("#sort-display", Static).update(self._render_bar())

    def action_next_field(self) -> None:
        self._selected = (self._selected + 1) % len(_SORT_FIELDS)
        self._update_display()

    def action_prev_field(self) -> None:
        self._selected = (self._selected - 1) % len(_SORT_FIELDS)
        self._update_display()

    def action_confirm(self) -> None:
        field = _SORT_FIELDS[self._selected]
        self.app.post_message(self.SortSelected(field, self._reverse))
        self.dismiss()

    def action_cancel(self) -> None:
        self.dismiss()

    def on_key(self, event: object) -> None:
        from textual.events import Key

        if isinstance(event, Key) and event.key == "r":
            self._reverse = not self._reverse
            self._update_display()
            event.stop()
            event.prevent_default()
