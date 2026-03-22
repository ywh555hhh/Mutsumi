"""Confirm dialog for task deletion."""

from __future__ import annotations

from typing import TYPE_CHECKING

from textual.containers import Horizontal, Vertical
from textual.message import Message
from textual.screen import ModalScreen
from textual.widgets import Button, Static

if TYPE_CHECKING:
    from textual.app import ComposeResult


class ConfirmDialog(ModalScreen[bool]):
    """Modal confirmation dialog for destructive actions."""

    DEFAULT_CSS = """
    ConfirmDialog {
        align: center middle;
    }

    ConfirmDialog > Vertical {
        width: 40;
        max-width: 90%;
        height: auto;
        max-height: 10;
        background: #1a1a1a;
        border: solid #e06c75;
        padding: 1 2;
    }

    ConfirmDialog .confirm-message {
        height: auto;
        text-align: center;
        color: #e0e0e0;
        margin-bottom: 1;
    }

    ConfirmDialog .confirm-buttons {
        height: 3;
        align: center middle;
    }

    ConfirmDialog Button {
        margin: 0 1;
    }
    """

    class Confirmed(Message):
        """Posted when the action is confirmed."""

        def __init__(self, task_id: str) -> None:
            self.task_id = task_id
            super().__init__()

    BINDINGS = [("escape", "cancel", "Cancel")]

    def __init__(self, task_id: str, task_title: str) -> None:
        super().__init__()
        self._task_id = task_id
        self._task_title = task_title

    def compose(self) -> ComposeResult:
        safe_title = self._task_title.replace("[", "\\[")
        with Vertical():
            yield Static(
                f'Delete "{safe_title}"?',
                classes="confirm-message",
            )
            with Horizontal(classes="confirm-buttons"):
                yield Button("Delete", variant="error", id="confirm-yes")
                yield Button("Cancel", variant="default", id="confirm-no")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "confirm-yes":
            # Post to app BEFORE dismiss — ModalScreen.post_message() won't
            # reach the App after dismiss() removes the screen.
            self.app.post_message(self.Confirmed(self._task_id))
            self.dismiss(True)
        elif event.button.id == "confirm-no":
            self.dismiss(False)

    def action_cancel(self) -> None:
        self.dismiss(False)
