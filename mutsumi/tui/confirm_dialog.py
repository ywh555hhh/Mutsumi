"""Confirm dialog for task deletion."""

from __future__ import annotations

from typing import TYPE_CHECKING

from textual.containers import Horizontal, Vertical
from textual.message import Message
from textual.screen import ModalScreen
from textual.widgets import Button, Static

from mutsumi.i18n import get_i18n

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
        background: $theme-surface;
        border: solid $theme-error;
        padding: 1 2;
    }

    ConfirmDialog .confirm-message {
        height: auto;
        text-align: center;
        color: $theme-text;
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
        t = get_i18n().t
        safe_title = self._task_title.replace("[", "\\[")
        with Vertical():
            yield Static(
                f'{t("actions.confirm_delete")}\n"{safe_title}"',
                classes="confirm-message",
            )
            with Horizontal(classes="confirm-buttons"):
                yield Button(t("actions.delete"), variant="error", id="confirm-yes")
                yield Button(t("actions.cancel"), variant="default", id="confirm-no")

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
