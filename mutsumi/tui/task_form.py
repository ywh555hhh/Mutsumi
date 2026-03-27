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

from mutsumi.i18n import get_i18n


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
        background: $theme-surface;
        border: solid $theme-border;
        padding: 1 2;
    }

    TaskForm .form-title {
        height: 1;
        text-align: center;
        text-style: bold;
        color: $theme-accent;
        margin-bottom: 1;
    }

    TaskForm Label {
        height: 1;
        color: $theme-text;
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
            source_name: str | None = None,
        ) -> None:
            self.title = title
            self.priority = priority
            self.scope = scope
            self.tags = tags
            self.description = description
            self.editing_id = editing_id
            self.parent_id = parent_id
            self.source_name = source_name
            super().__init__()

    BINDINGS = [("escape", "cancel", "Cancel")]

    def __init__(
        self,
        task: Task | None = None,
        parent_id: str | None = None,
        default_scope: str = "inbox",
        source_options: list[tuple[str, str]] | None = None,
        default_source: str | None = None,
        show_source_selector: bool = False,
    ) -> None:
        super().__init__()
        self._editing_task = task
        self._parent_id = parent_id
        self._default_scope = default_scope
        self._source_options = source_options or []
        self._default_source = default_source
        self._show_source_selector = show_source_selector and parent_id is None

    def compose(self) -> ComposeResult:
        task = self._editing_task
        is_edit = task is not None
        t = get_i18n().t
        if self._parent_id:
            form_title = t("actions.new_task")
        elif is_edit:
            form_title = t("actions.edit_task")
        else:
            form_title = t("actions.new_task")

        with VerticalScroll():
            yield Static(form_title, classes="form-title")

            if self._show_source_selector and self._source_options and not is_edit:
                yield Label(t("form.source_label"))
                yield Select(
                    self._source_options,
                    value=self._default_source,
                    id="form-source",
                )

            yield Label(t("form.title_label"))
            yield Input(
                value=task.title if task else "",
                placeholder=t("form.title_placeholder"),
                id="form-title",
            )

            yield Label(t("form.priority_label"))
            yield Select(
                [(p, p) for p in ("high", "normal", "low")],
                value=task.priority.value if task else "normal",
                id="form-priority",
            )

            yield Label(t("form.scope_label"))
            yield Select(
                [(s, s) for s in ("day", "week", "month", "inbox")],
                value=task.scope.value if task else self._default_scope,
                id="form-scope",
            )

            yield Label(t("form.tags_label"))
            yield Input(
                value=", ".join(task.tags) if task else "",
                placeholder="tag1, tag2",
                id="form-tags",
            )

            yield Label(t("form.description_label"))
            yield Input(
                value=task.description or "" if task else "",
                placeholder="...",
                id="form-description",
            )

            with Horizontal(classes="form-buttons"):
                yield Button(
                    t("actions.save") if is_edit else t("actions.create"),
                    variant="primary",
                    id="form-submit",
                )
                yield Button(t("actions.cancel"), variant="default", id="form-cancel")

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

        source_name: str | None = None
        if self._show_source_selector and not self._editing_task:
            source_select = self.query_one("#form-source", Select)
            source_name = str(source_select.value)

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
            source_name=source_name,
        ))
        self.dismiss()

    def action_cancel(self) -> None:
        self.dismiss()
