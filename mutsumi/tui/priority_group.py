"""Priority group widget — section header + task rows."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from rich.text import Text
from textual.reactive import reactive
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


class PriorityGroupHeader(Widget, can_focus=True):
    """Section header for a priority group — click or press Enter to toggle."""

    DEFAULT_CSS = """
    PriorityGroupHeader {
        height: 1;
        padding: 0 1;
        color: #666666;
    }

    PriorityGroupHeader:hover {
        background: #1e1e1e;
    }

    PriorityGroupHeader:focus {
        background: #2a2a2a;
    }
    """

    collapsed: reactive[bool] = reactive(False)

    def __init__(self, priority: TaskPriority, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.priority = priority

    def render(self) -> Text:
        label = PRIORITY_LABELS[self.priority]
        style = PRIORITY_HEADER_STYLE[self.priority]
        icon = "\u25b6" if self.collapsed else "\u25bc"
        # Fill remaining width with ─
        prefix = f"{icon} {label} "
        avail = self.size.width - len(prefix)
        sep = "\u2500" * max(avail, 0)
        line = Text()
        line.append(f"{icon} {label} ", style=style)
        line.append(sep, style=style)
        return line

    def on_click(self) -> None:
        self._toggle()

    def _toggle(self) -> None:
        self.collapsed = not self.collapsed
        parent = self.parent
        if isinstance(parent, PriorityGroup):
            parent.set_collapsed(self.collapsed)

    def watch_collapsed(self) -> None:
        self.refresh()


class PriorityGroup(Widget):
    """A priority section with header and task rows."""

    DEFAULT_CSS = """
    PriorityGroup {
        height: auto;
    }
    """

    def __init__(
        self, priority: TaskPriority, tasks: list[Task],
        columns: list[str] | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.priority = priority
        self.tasks = tasks
        self._collapsed = False
        self._columns = columns

    def compose(self) -> ComposeResult:
        yield PriorityGroupHeader(self.priority)

        # Task rows (with recursive children)
        for task in self.tasks:
            yield from self._yield_task_rows(task, depth=0)

    def set_collapsed(self, collapsed: bool) -> None:
        """Show or hide task rows under this group."""
        self._collapsed = collapsed
        for child in self.children:
            if not isinstance(child, PriorityGroupHeader):
                child.display = not collapsed

    def _yield_task_rows(self, task: Task, depth: int) -> Iterator[TaskRow | Static]:
        yield TaskRow(task, depth=depth, columns=self._columns)
        if depth < MAX_NESTING_DEPTH and task.children:
            for child in task.children:
                yield from self._yield_task_rows(child, depth + 1)
        elif task.children:
            count = len(task.children)
            yield Static(
                f"{'  ' * depth}      {count} subtasks...",
                classes="collapsed-hint",
            )
