"""Inline 1-line confirmation bar for Mutsumi.

Replaces ConfirmDialog for lightweight confirmations (e.g. dd delete).
Renders: ``Delete "task title"? [y/N]``
  - Press ``y`` → confirm (post Resolved with confirmed=True)
  - Any other key → cancel (post Resolved with confirmed=False)
"""

from __future__ import annotations

import contextlib
from typing import TYPE_CHECKING, Any

from textual.message import Message
from textual.widget import Widget
from textual.widgets import Static

if TYPE_CHECKING:
    from textual.app import ComposeResult
    from textual.events import Key


class ConfirmBar(Widget, can_focus=True):
    """Inline confirmation bar — docked at bottom, height 1."""

    DEFAULT_CSS = """
    ConfirmBar {
        dock: bottom;
        height: 1;
        background: #2a1a1a;
        display: none;
    }

    ConfirmBar .prompt {
        width: 1fr;
        padding: 0 1;
        color: #e06c75;
    }
    """

    class Resolved(Message):
        """Posted when the user confirms or cancels."""

        def __init__(self, task_id: str, confirmed: bool) -> None:
            self.task_id = task_id
            self.confirmed = confirmed
            super().__init__()

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._task_id = ""
        self._task_title = ""

    def compose(self) -> ComposeResult:
        yield Static("", classes="prompt", id="confirm-prompt")

    def show(self, task_id: str, task_title: str) -> None:
        """Display the confirmation prompt."""
        self._task_id = task_id
        self._task_title = task_title
        safe_title = task_title.replace("[", "\\[")
        prompt = f'Delete "{safe_title}"? \\[y/N]'
        with contextlib.suppress(Exception):
            self.query_one("#confirm-prompt", Static).update(prompt)
        self.display = True
        self.focus()

    def hide(self) -> None:
        """Hide the confirmation bar."""
        self.display = False

    def on_key(self, event: Key) -> None:
        """y confirms, anything else cancels."""
        event.stop()
        event.prevent_default()
        if event.key == "y":
            self.post_message(self.Resolved(self._task_id, confirmed=True))
        else:
            self.post_message(self.Resolved(self._task_id, confirmed=False))
        self.hide()
