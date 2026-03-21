"""Task detail panel — shown when pressing Enter on a task."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from textual.containers import Vertical, VerticalScroll
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


class DetailPanel(Widget):
    """Side panel showing full task details."""

    DEFAULT_CSS = """
    DetailPanel {
        dock: right;
        width: 40;
        background: #141414;
        border-left: solid #333333;
        display: none;
    }

    DetailPanel.visible {
        display: block;
    }

    DetailPanel .detail-header {
        height: 1;
        padding: 0 1;
        background: #1a1a1a;
        color: #5de4c7;
        text-style: bold;
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

    DetailPanel .detail-separator {
        height: 1;
        padding: 0 1;
        color: #333333;
    }

    DetailPanel .detail-scroll {
        height: 1fr;
    }
    """

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._detail_task: Task | None = None

    def compose(self) -> ComposeResult:
        with VerticalScroll(classes="detail-scroll"):
            yield Vertical(id="detail-content")

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
            Static(f"{status_icon} {task.title}", classes="detail-header")
        )

        content.mount(Static("─" * 38, classes="detail-separator"))

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
            content.mount(Static("─" * 38, classes="detail-separator"))
            content.mount(Static("Description", classes="detail-label"))
            content.mount(
                Static(f"  {task.description}", classes="detail-field")
            )

        # Children summary
        done, total = task.children_progress()
        if total > 0:
            content.mount(Static("─" * 38, classes="detail-separator"))
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
            content.mount(Static("─" * 38, classes="detail-separator"))
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

        # Hint
        content.mount(Static("─" * 38, classes="detail-separator"))
        content.mount(
            Static(
                "  [#666666]Press Enter or Esc to close[/]",
                classes="detail-field",
            )
        )
