"""Task form modal — ModalScreen for creating/editing tasks."""

from __future__ import annotations

from typing import TYPE_CHECKING

from textual.containers import Horizontal, VerticalScroll
from textual.message import Message
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label, Select, Static

if TYPE_CHECKING:
    from textual.app import ComposeResult

    from mutsumi.core.models import Task


class TaskForm(ModalScreen[None]):
    """Modal form for creating or editing a task."""

    DEFAULT_CSS = """
    TaskForm {
        align: center middle;
    }

    TaskForm > VerticalScroll {
        width: 64;
        max-width: 90%;
        height: auto;
        max-height: 80%;
        background: #1a1a1a;
        border: solid #333333;
        padding: 1 2;
    }

    TaskForm .form-title {
        height: 1;
        text-align: center;
        text-style: bold;
        color: #5de4c7;
        margin-bottom: 1;
    }

    TaskForm Label {
        height: 1;
        color: #e0e0e0;
        margin-top: 1;
    }

    TaskForm Input {
        margin-bottom: 0;
    }

    TaskForm Select {
        margin-bottom: 0;
    }

    TaskForm .form-buttons {
        height: 3;
        margin-top: 1;
        align: center middle;
    }

    TaskForm Button {
        margin: 0 1;
    }
    """

    class TaskSubmitted(Message):
        """Posted when the form is submitted."""

        def __init__(
            self,
            title: str,
            priority: str,
            scope: str,
            tags: str,
            description: str,
            editing_id: str | None,
            parent_id: str | None = None,
        ) -> None:
            self.title = title
            self.priority = priority
            self.scope = scope
            self.tags = tags
            self.description = description
            self.editing_id = editing_id
            self.parent_id = parent_id
            super().__init__()

    BINDINGS = [("escape", "cancel", "Cancel")]

    def __init__(
        self,
        task: Task | None = None,
        parent_id: str | None = None,
        default_scope: str = "inbox",
    ) -> None:
        super().__init__()
        self._editing_task = task
        self._parent_id = parent_id
        self._default_scope = default_scope

    def compose(self) -> ComposeResult:
        task = self._editing_task
        is_edit = task is not None
        if self._parent_id:
            form_title = "Add Subtask"
        elif is_edit:
            form_title = "Edit Task"
        else:
            form_title = "New Task"

        with VerticalScroll():
            yield Static(form_title, classes="form-title")

            yield Label("Title")
            yield Input(
                value=task.title if task else "",
                placeholder="Task title...",
                id="form-title",
            )

            yield Label("Priority")
            yield Select(
                [(p, p) for p in ("high", "normal", "low")],
                value=task.priority.value if task else "normal",
                id="form-priority",
            )

            yield Label("Scope")
            yield Select(
                [(s, s) for s in ("day", "week", "month", "inbox")],
                value=task.scope.value if task else self._default_scope,
                id="form-scope",
            )

            yield Label("Tags (comma-separated)")
            yield Input(
                value=", ".join(task.tags) if task else "",
                placeholder="tag1, tag2",
                id="form-tags",
            )

            yield Label("Description")
            yield Input(
                value=task.description or "" if task else "",
                placeholder="Optional description...",
                id="form-description",
            )

            with Horizontal(classes="form-buttons"):
                yield Button(
                    "Save" if is_edit else "Create",
                    variant="primary",
                    id="form-submit",
                )
                yield Button("Cancel", variant="default", id="form-cancel")

    def on_mount(self) -> None:
        """Auto-focus the title input when the form opens."""
        title_input = self.query_one("#form-title", Input)
        title_input.focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "form-submit":
            self._submit()
        elif event.button.id == "form-cancel":
            self.dismiss()

    def _submit(self) -> None:
        title_input = self.query_one("#form-title", Input)
        title = title_input.value.strip()
        if not title:
            return

        priority_select = self.query_one("#form-priority", Select)
        scope_select = self.query_one("#form-scope", Select)
        tags_input = self.query_one("#form-tags", Input)
        desc_input = self.query_one("#form-description", Input)

        # Post to app BEFORE dismiss — ModalScreen.post_message() won't
        # reach the App after dismiss() removes the screen.
        self.app.post_message(self.TaskSubmitted(
            title=title,
            priority=str(priority_select.value),
            scope=str(scope_select.value),
            tags=tags_input.value,
            description=desc_input.value,
            editing_id=self._editing_task.id if self._editing_task else None,
            parent_id=self._parent_id,
        ))
        self.dismiss()

    def action_cancel(self) -> None:
        self.dismiss()
