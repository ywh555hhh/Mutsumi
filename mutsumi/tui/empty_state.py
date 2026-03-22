"""Empty state placeholder widget with actionable button."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from textual.containers import Vertical
from textual.message import Message
from textual.widget import Widget
from textual.widgets import Static

if TYPE_CHECKING:
    from textual.app import ComposeResult


class _NewTaskButton(Static, can_focus=True):
    """Clickable & focusable button inside the empty state."""

    DEFAULT_CSS = """
    _NewTaskButton {
        width: auto;
        height: 1;
        padding: 0 2;
        color: #5de4c7;
        text-align: center;
    }

    _NewTaskButton:hover {
        background: #2a2a2a;
        color: #ffffff;
    }

    _NewTaskButton:focus {
        text-style: reverse;
    }
    """

    class Pressed(Message):
        """Posted when the button is clicked or activated."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__("\\[+ New Task]", **kwargs)

    def on_click(self) -> None:
        self.post_message(self.Pressed())

    def on_key(self, event: object) -> None:
        from textual.events import Key

        if isinstance(event, Key) and event.key in ("enter", "space"):
            event.stop()
            event.prevent_default()
            self.post_message(self.Pressed())


class EmptyState(Widget):
    """Shown when the current tab has no tasks."""

    DEFAULT_CSS = """
    EmptyState {
        width: 100%;
        height: 100%;
        align: center middle;
    }

    EmptyState > Vertical {
        width: auto;
        height: auto;
        align: center middle;
    }

    EmptyState .hint {
        color: #666666;
        text-align: center;
        width: auto;
        padding: 0 0 1 0;
    }
    """

    class NewTaskRequested(Message):
        """Posted when user clicks the new-task button in empty state."""

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Static(
                "Nothing here yet.\n\n"
                "Press [bold #5de4c7]n[/] to create a task\n"
                "or let your Agent write tasks.json",
                classes="hint",
            )
            yield _NewTaskButton(id="empty-new-btn")

    def on__new_task_button_pressed(self, event: _NewTaskButton.Pressed) -> None:
        self.post_message(self.NewTaskRequested())
