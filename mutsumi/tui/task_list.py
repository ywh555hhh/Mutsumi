"""Task list panel — main content area."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from textual.containers import VerticalScroll
from textual.widget import Widget

from mutsumi.core.loader import group_tasks_by_priority
from mutsumi.tui.empty_state import EmptyState
from mutsumi.tui.priority_group import PriorityGroup
from mutsumi.tui.task_row import TaskRow

if TYPE_CHECKING:
    from textual.app import ComposeResult

    from mutsumi.core.models import Task


class TaskListPanel(Widget):
    """Main content area displaying tasks grouped by priority."""

    DEFAULT_CSS = """
    TaskListPanel {
        height: 1fr;
        background: $theme-bg;
    }

    TaskListPanel > VerticalScroll {
        height: 100%;
    }
    """

    def __init__(
        self,
        tasks: list[Task] | None = None,
        columns: list[str] | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self._tasks: list[Task] = tasks or []
        self._columns = columns

    def compose(self) -> ComposeResult:
        scroll = VerticalScroll()
        scroll.can_focus = False
        with scroll:
            if not self._tasks:
                yield EmptyState()
            else:
                groups = group_tasks_by_priority(self._tasks)
                for priority, group_tasks in groups.items():
                    yield PriorityGroup(priority, group_tasks, columns=self._columns)

    async def update_tasks(
        self,
        tasks: list[Task],
        columns: list[str] | None = None,
    ) -> None:
        """Replace the task list and re-render."""
        self._tasks = tasks
        if columns is not None:
            self._columns = columns
        scroll = self.query_one(VerticalScroll)
        scroll.can_focus = False
        await scroll.remove_children()
        if not self._tasks:
            await scroll.mount(EmptyState())
        else:
            groups = group_tasks_by_priority(self._tasks)
            for priority, group_tasks in groups.items():
                await scroll.mount(
                    PriorityGroup(priority, group_tasks, columns=self._columns)
                )

    def dim_non_matching(self, query: str) -> None:
        """Dim task rows that don't match *query*. Clear dimming if query is empty."""
        query_lower = query.lower()
        for row in self.query(TaskRow):
            if not query_lower:
                row.set_dimmed(False)
            else:
                has_desc = row.task_data.description is not None
                matches = (
                    query_lower in row.task_data.title.lower()
                    or any(query_lower in tag.lower() for tag in row.task_data.tags)
                    or (has_desc and query_lower in row.task_data.description.lower())  # type: ignore[union-attr]
                )
                row.set_dimmed(not matches)
