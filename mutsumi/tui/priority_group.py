"""Priority group widget — section header + task rows."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from textual.widget import Widget
from textual.widgets import Static

from mutsumi.core.models import Task, TaskPriority
from mutsumi.tui.task_row import TaskRow

if TYPE_CHECKING:
    from collections.abc import Iterator

    from textual.app import ComposeResult

PRIORITY_LABELS: dict[TaskPriority, str] = {
    TaskPriority.HIGH: "HIGH",
    TaskPriority.NORMAL: "NORMAL",
    TaskPriority.LOW: "LOW",
}

PRIORITY_HEADER_STYLE: dict[TaskPriority, str] = {
    TaskPriority.HIGH: "#e06c75",
    TaskPriority.NORMAL: "#e0e0e0",
    TaskPriority.LOW: "#666666",
}

MAX_NESTING_DEPTH = 3


class PriorityGroupHeader(Static):
    """Section header for a priority group."""

    DEFAULT_CSS = """
    PriorityGroupHeader {
        height: 1;
        padding: 0 1;
        color: #666666;
    }
    """


class PriorityGroup(Widget):
    """A priority section with header and task rows."""

    DEFAULT_CSS = """
    PriorityGroup {
        height: auto;
    }
    """

    def __init__(
        self, priority: TaskPriority, tasks: list[Task], **kwargs: Any
    ) -> None:
        super().__init__(**kwargs)
        self.priority = priority
        self.tasks = tasks

    def compose(self) -> ComposeResult:
        # Section header
        label = PRIORITY_LABELS[self.priority]
        style = PRIORITY_HEADER_STYLE[self.priority]
        header_text = f"[{style}]\u25bc {label}[/] [{style}]{'─' * 40}[/]"
        yield PriorityGroupHeader(header_text)

        # Task rows (with recursive children)
        for task in self.tasks:
            yield from self._yield_task_rows(task, depth=0)

    def _yield_task_rows(self, task: Task, depth: int) -> Iterator[TaskRow | Static]:
        yield TaskRow(task, depth=depth)
        if depth < MAX_NESTING_DEPTH and task.children:
            for child in task.children:
                yield from self._yield_task_rows(child, depth + 1)
        elif task.children:
            count = len(task.children)
            yield Static(
                f"{'  ' * depth}      {count} subtasks...",
                classes="collapsed-hint",
            )
