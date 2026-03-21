"""Task detail panel — shown when pressing Enter on a task."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from rich.text import Text
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.message import Message
from textual.widget import Widget
from textual.widgets import Static

from mutsumi.core.models import Task, TaskPriority, TaskStatus

if TYPE_CHECKING:
    from textual.app import ComposeResult

PRIORITY_LABELS = {
    TaskPriority.HIGH: ("HIGH", "#e06c75"),
    TaskPriority.NORMAL: ("NORMAL", "#e5c07b"),
    TaskPriority.LOW: ("LOW", "#666666"),
}


class _ResponsiveSeparator(Widget):
    """A separator line that fills the available width with ─."""

    DEFAULT_CSS = """
    _ResponsiveSeparator {
        height: 1;
        padding: 0 1;
        color: #333333;
    }
    """

    def render(self) -> Text:
        width = self.size.width
        return Text("\u2500" * max(width, 0), style="#333333")


class _PanelAction(Static):
    """A clickable label for detail panel actions (1-line height)."""

    def __init__(self, label: str, action_name: str, **kwargs: Any) -> None:
        super().__init__(label, **kwargs)
        self._action_name = action_name

    def on_click(self) -> None:
        parent = self.parent
        while parent is not None:
            if isinstance(parent, DetailPanel):
                parent.handle_action(self._action_name)
                break
            parent = parent.parent


class DetailPanel(Widget):
    """Side panel showing full task details with action buttons."""

    DEFAULT_CSS = """
    DetailPanel {
        dock: right;
        width: 40%;
        max-width: 50;
        min-width: 24;
        background: #141414;
        border-left: solid #333333;
        display: none;
    }

    DetailPanel.visible {
        display: block;
    }

    DetailPanel .detail-topbar {
        height: 1;
        padding: 0 1;
        background: #1a1a1a;
    }

    DetailPanel .detail-topbar-title {
        width: 1fr;
        color: #5de4c7;
        text-style: bold;
    }

    DetailPanel .detail-close-btn {
        width: auto;
        height: 1;
        padding: 0 1;
        color: #666666;
    }

    DetailPanel .detail-close-btn:hover {
        color: #e06c75;
    }

    DetailPanel .detail-actions {
        height: 1;
        padding: 0 1;
        background: #1a1a1a;
    }

    DetailPanel .detail-action-btn {
        width: auto;
        height: 1;
        padding: 0 1;
        color: #5de4c7;
    }

    DetailPanel .detail-action-btn:hover {
        background: #2a2a2a;
        color: #ffffff;
    }

    DetailPanel .detail-delete-btn {
        width: auto;
        height: 1;
        padding: 0 1;
        color: #e06c75;
    }

    DetailPanel .detail-delete-btn:hover {
        background: #3a1a1a;
        color: #ff8888;
    }

    DetailPanel .detail-field {
        height: auto;
        padding: 0 1;
        color: #e0e0e0;
    }

    DetailPanel .detail-label {
        height: 1;
        padding: 0 1;
        color: #666666;
        text-style: bold;
    }

    DetailPanel _ResponsiveSeparator {
        height: 1;
        padding: 0 1;
        color: #333333;
    }

    DetailPanel .detail-scroll {
        height: 1fr;
    }
    """

    class EditRequested(Message):
        """Posted when the Edit button is clicked."""

        def __init__(self, task_id: str) -> None:
            self.task_id = task_id
            super().__init__()

    class DeleteRequested(Message):
        """Posted when the Delete button is clicked."""

        def __init__(self, task_id: str, task_title: str) -> None:
            self.task_id = task_id
            self.task_title = task_title
            super().__init__()

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._detail_task: Task | None = None

    def compose(self) -> ComposeResult:
        with Horizontal(classes="detail-topbar"):
            yield Static("Detail", classes="detail-topbar-title")
            yield _PanelAction("\\[x]", "close", classes="detail-close-btn")
        with Horizontal(classes="detail-actions"):
            yield _PanelAction("\\[Edit]", "edit", classes="detail-action-btn")
            yield _PanelAction("\\[Delete]", "delete", classes="detail-delete-btn")
        with VerticalScroll(classes="detail-scroll"):
            yield Vertical(id="detail-content")

    def handle_action(self, action: str) -> None:
        """Dispatch action from clickable labels."""
        if action == "close":
            self.hide()
        elif action == "edit" and self._detail_task is not None:
            self.post_message(self.EditRequested(self._detail_task.id))
        elif action == "delete" and self._detail_task is not None:
            self.post_message(
                self.DeleteRequested(self._detail_task.id, self._detail_task.title)
            )

    def show_task(self, task: Task) -> None:
        """Display details for a task."""
        self._detail_task = task
        self.add_class("visible")
        self._rebuild()

    def hide(self) -> None:
        """Hide the detail panel."""
        self._detail_task = None
        self.remove_class("visible")

    @property
    def is_visible(self) -> bool:
        return self.has_class("visible")

    def _rebuild(self) -> None:
        """Rebuild the detail content."""
        if self._detail_task is None:
            return

        task = self._detail_task
        content = self.query_one("#detail-content", Vertical)
        content.remove_children()

        # Title
        status_icon = "[x]" if task.status == TaskStatus.DONE else "[ ]"
        content.mount(
            Static(f"{status_icon} {task.title}", classes="detail-label")
        )

        content.mount(_ResponsiveSeparator())

        # Status
        content.mount(Static("Status", classes="detail-label"))
        status_text = "Done" if task.status == TaskStatus.DONE else "Pending"
        content.mount(Static(f"  {status_text}", classes="detail-field"))

        # Priority
        content.mount(Static("Priority", classes="detail-label"))
        plabel, pcolor = PRIORITY_LABELS[task.priority]
        content.mount(
            Static(f"  [{pcolor}]{plabel}[/]", classes="detail-field")
        )

        # Scope
        content.mount(Static("Scope", classes="detail-label"))
        content.mount(Static(f"  {task.scope.value}", classes="detail-field"))

        # Tags
        if task.tags:
            content.mount(Static("Tags", classes="detail-label"))
            content.mount(
                Static(f"  {', '.join(task.tags)}", classes="detail-field")
            )

        # Due date
        if task.due_date:
            content.mount(Static("Due", classes="detail-label"))
            content.mount(Static(f"  {task.due_date}", classes="detail-field"))

        # Description
        if task.description:
            content.mount(_ResponsiveSeparator())
            content.mount(Static("Description", classes="detail-label"))
            content.mount(
                Static(f"  {task.description}", classes="detail-field")
            )

        # Children summary
        done, total = task.children_progress()
        if total > 0:
            content.mount(_ResponsiveSeparator())
            content.mount(Static("Subtasks", classes="detail-label"))
            content.mount(
                Static(f"  {done}/{total} completed", classes="detail-field")
            )
            for child in task.children:
                icon = "[x]" if child.is_done else "[ ]"
                content.mount(
                    Static(f"  {icon} {child.title}", classes="detail-field")
                )

        # Created / completed timestamps
        if task.created_at or task.completed_at:
            content.mount(_ResponsiveSeparator())
            if task.created_at:
                content.mount(Static("Created", classes="detail-label"))
                content.mount(
                    Static(f"  {task.created_at}", classes="detail-field")
                )
            if task.completed_at:
                content.mount(Static("Completed", classes="detail-label"))
                content.mount(
                    Static(f"  {task.completed_at}", classes="detail-field")
                )
