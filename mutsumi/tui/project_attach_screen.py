"""Lightweight project attach prompt for known users entering a new repo."""

from __future__ import annotations

from typing import TYPE_CHECKING

from textual.containers import Horizontal, Vertical
from textual.message import Message
from textual.screen import ModalScreen
from textual.widgets import Button, Static

if TYPE_CHECKING:
    from textual.app import ComposeResult


class ProjectAttachScreen(ModalScreen[None]):
    """Offer lightweight project registration for a new repo."""

    DEFAULT_CSS = """
    ProjectAttachScreen {
        align: center middle;
    }

    ProjectAttachScreen > Vertical {
        width: 64;
        max-width: 92%;
        height: auto;
        background: $theme-surface;
        border: solid $theme-border;
        padding: 1 2;
    }

    ProjectAttachScreen .title {
        color: $theme-accent;
        text-style: bold;
        text-align: center;
        margin-bottom: 1;
    }

    ProjectAttachScreen .description {
        color: $theme-text;
        text-align: center;
        margin-bottom: 1;
    }

    ProjectAttachScreen .buttons {
        height: 3;
        align: center middle;
    }

    ProjectAttachScreen Button {
        margin: 0 1;
    }
    """

    BINDINGS = [("escape", "skip", "Skip")]

    class Resolved(Message):
        """Posted when the user decides how to handle project attach."""

        def __init__(self, action: str) -> None:
            self.action = action
            super().__init__()

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Static("This folder looks like a project", classes="title")
            yield Static(
                "You already finished onboarding. Do you want to attach this repo now?",
                classes="description",
            )
            with Horizontal(classes="buttons"):
                yield Button("Register project", variant="primary", id="attach-register")
                yield Button("Create local file", id="attach-create")
                yield Button("Skip", id="attach-skip")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id or ""
        if button_id == "attach-register":
            self.app.post_message(self.Resolved("register"))
            self.dismiss()
        elif button_id == "attach-create":
            self.app.post_message(self.Resolved("create"))
            self.dismiss()
        elif button_id == "attach-skip":
            self.action_skip()

    def action_skip(self) -> None:
        self.app.post_message(self.Resolved("skip"))
        self.dismiss()
