"""Single task row widget for the Mutsumi TUI."""

from typing import Any

from rich.text import Text
from textual.reactive import reactive
from textual.widget import Widget

from mutsumi.core.models import Task, TaskPriority

PRIORITY_STARS: dict[TaskPriority, str] = {
    TaskPriority.HIGH: "\u2605\u2605\u2605",
    TaskPriority.NORMAL: "\u2605\u2605",
    TaskPriority.LOW: "\u2605",
}

PRIORITY_STAR_STYLE: dict[TaskPriority, str] = {
    TaskPriority.HIGH: "#e06c75",
    TaskPriority.NORMAL: "#e5c07b",
    TaskPriority.LOW: "#666666",
}

INDENT_GLYPH = "  \u2514\u2500 "


class TaskRow(Widget, can_focus=True):
    """Renders a single task as a one-line row."""

    DEFAULT_CSS = """
    TaskRow {
        height: 1;
        padding: 0 1;
        color: #e0e0e0;
    }

    TaskRow:focus {
        background: #2a2a2a;
    }

    TaskRow:hover {
        background: #1a1a1a;
    }

    TaskRow.done {
        color: #666666;
    }
    """

    toggled = reactive(False)

    def __init__(self, task: Task, depth: int = 0, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.task_data = task
        self.depth = depth
        self.toggled = task.is_done

    def render(self) -> Text:
        line = Text()

        # Indentation
        if self.depth > 0:
            indent = "  " * (self.depth - 1) + INDENT_GLYPH
            line.append(indent, style="#666666")

        # Checkbox
        checkbox = "[x] " if self.toggled else "[ ] "
        line.append(checkbox, style="#5de4c7" if self.toggled else "#e0e0e0")

        # Title
        title_style = "strike #666666" if self.toggled else "#e0e0e0"
        line.append(self.task_data.title, style=title_style)

        # Children progress
        done, total = self.task_data.children_progress()
        if total > 0:
            line.append(f"  ({done}/{total})", style="#666666")

        # Tags
        if self.task_data.tags:
            tags_str = ",".join(self.task_data.tags)
            line.append(f"  {tags_str}", style="#666666")

        # Priority stars
        stars = PRIORITY_STARS[self.task_data.priority]
        star_style = PRIORITY_STAR_STYLE[self.task_data.priority]
        line.append(f" {stars}", style=star_style)

        return line

    def on_click(self) -> None:
        """Focus this row when clicked."""
        self.focus()

    def toggle_done(self) -> None:
        """Toggle the done status visually (no write-back in Phase 1)."""
        self.toggled = not self.toggled
        self.set_class(self.toggled, "done")
        self.refresh()
