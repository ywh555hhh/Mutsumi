"""Task list panel — main content area."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from textual.containers import VerticalScroll
from textual.widget import Widget

from mutsumi.core.loader import group_tasks_by_priority
from mutsumi.tui.empty_state import EmptyState
from mutsumi.tui.priority_group import PriorityGroup

if TYPE_CHECKING:
    from textual.app import ComposeResult

    from mutsumi.core.models import Task


class TaskListPanel(Widget):
    """Main content area displaying tasks grouped by priority."""

    DEFAULT_CSS = """
    TaskListPanel {
        height: 1fr;
        background: #0f0f0f;
    }

    TaskListPanel > VerticalScroll {
        height: 100%;
    }
    """

    def __init__(self, tasks: list[Task] | None = None, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._tasks: list[Task] = tasks or []

    def compose(self) -> ComposeResult:
        scroll = VerticalScroll()
        scroll.can_focus = False
        with scroll:
            if not self._tasks:
                yield EmptyState()
            else:
                groups = group_tasks_by_priority(self._tasks)
                for priority, group_tasks in groups.items():
                    yield PriorityGroup(priority, group_tasks)

    async def update_tasks(self, tasks: list[Task]) -> None:
        """Replace the task list and re-render."""
        self._tasks = tasks
        scroll = self.query_one(VerticalScroll)
        scroll.can_focus = False
        await scroll.remove_children()
        if not self._tasks:
            await scroll.mount(EmptyState())
        else:
            groups = group_tasks_by_priority(self._tasks)
            for priority, group_tasks in groups.items():
                await scroll.mount(PriorityGroup(priority, group_tasks))
