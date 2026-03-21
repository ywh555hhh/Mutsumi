"""Empty state placeholder widget."""

from typing import Any

from textual.widgets import Static


class EmptyState(Static):
    """Shown when the current tab has no tasks."""

    DEFAULT_CSS = """
    EmptyState {
        content-align: center middle;
        width: 100%;
        height: 100%;
        color: #666666;
    }
    """

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(
            "Nothing here yet.\n\n"
            "Press [bold #5de4c7]n[/] to create a task\n"
            "or let your Agent write tasks.json",
            **kwargs,
        )
