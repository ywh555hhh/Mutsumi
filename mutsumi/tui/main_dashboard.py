"""Main dashboard widget — aggregated source overview.

Shows all registered sources as cards with progress bars and top-N
pending tasks. Clicking a card jumps to that source's tab.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from textual.containers import VerticalScroll
from textual.message import Message
from textual.widget import Widget
from textual.widgets import Static

from mutsumi.core.models import TaskStatus

if TYPE_CHECKING:
    from textual.app import ComposeResult

    from mutsumi.core.sources import Source


class SourceCard(Widget, can_focus=True):
    """A card summarizing a single source's progress."""

    DEFAULT_CSS = """
    SourceCard {
        width: 100%;
        height: auto;
        min-height: 3;
        padding: 0 1;
        margin: 0 0 1 0;
        background: #1a1a1a;
        border: solid #333333;
    }

    SourceCard:hover {
        border: solid #555555;
    }

    SourceCard:focus {
        border: solid #5de4c7;
    }

    SourceCard .card-header {
        width: 100%;
        height: 1;
        color: #5de4c7;
        text-style: bold;
    }

    SourceCard .card-progress {
        width: 100%;
        height: 1;
        color: #888888;
    }

    SourceCard .card-tasks {
        width: 100%;
        height: auto;
        color: #666666;
        padding: 0 1;
    }
    """

    class Clicked(Message):
        """Posted when a source card is clicked."""

        def __init__(self, source_name: str) -> None:
            self.source_name = source_name
            super().__init__()

    def __init__(
        self,
        source: Source,
        *,
        max_tasks: int = 3,
        show_completed: bool = True,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self._source = source
        self._max_tasks = max_tasks
        self._show_completed = show_completed

    def compose(self) -> ComposeResult:
        source = self._source
        name = source.name
        display_name = f"\u2605 {name}" if source.is_personal else name

        if source.error:
            yield Static(f"{display_name}  \u26a0 Error", classes="card-header")
            yield Static(source.error, classes="card-tasks")
            return

        if source.task_file is None:
            yield Static(f"{display_name}  (no file)", classes="card-header")
            return

        tasks = source.task_file.tasks
        total = len(tasks)
        done = sum(1 for t in tasks if t.status == TaskStatus.DONE)
        pending = total - done

        # Progress bar
        if total > 0:
            pct = int(done / total * 100)
            bar_width = 20
            filled = int(bar_width * done / total)
            bar = "\u2588" * filled + "\u2591" * (bar_width - filled)
            progress = f"{bar} {pct}% ({done}/{total})"
        else:
            progress = "No tasks"

        yield Static(f"{display_name}  {pending} pending", classes="card-header")
        yield Static(progress, classes="card-progress")

        # Top-N pending tasks
        pending_tasks = [t for t in tasks if t.status != TaskStatus.DONE][:self._max_tasks]
        if pending_tasks:
            lines = []
            for t in pending_tasks:
                priority_marker = {"high": "!!!", "normal": "", "low": ""}
                p = priority_marker.get(t.priority.value, "")
                prefix = f"{p} " if p else "  "
                lines.append(f"{prefix}\u2022 {t.title}")
            yield Static("\n".join(lines), classes="card-tasks")

    def on_click(self) -> None:
        self.post_message(self.Clicked(self._source.name))

    def on_key(self, event: object) -> None:
        from textual.events import Key

        if isinstance(event, Key) and event.key in ("enter", "space"):
            event.stop()
            event.prevent_default()
            self.post_message(self.Clicked(self._source.name))


class MainDashboard(Widget):
    """Aggregated dashboard showing all source cards."""

    DEFAULT_CSS = """
    MainDashboard {
        width: 100%;
        height: 100%;
    }

    MainDashboard > VerticalScroll {
        width: 100%;
        height: 100%;
        padding: 1 2;
    }

    MainDashboard .dashboard-title {
        width: 100%;
        height: 1;
        color: #5de4c7;
        text-style: bold;
        text-align: center;
        padding: 0 0 1 0;
    }
    """

    class SourceClicked(Message):
        """Posted when a source card is clicked — jump to that tab."""

        def __init__(self, source_name: str) -> None:
            self.source_name = source_name
            super().__init__()

    def __init__(
        self,
        sources: list[Source] | None = None,
        *,
        max_tasks: int = 3,
        show_completed: bool = True,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self._sources = sources or []
        self._max_tasks = max_tasks
        self._show_completed = show_completed

    def set_sources(self, sources: list[Source]) -> None:
        """Update sources and re-render."""
        self._sources = sources
        # Remove old cards and re-compose
        try:
            container = self.query_one(VerticalScroll)
            container.remove_children()
            container.mount(Static("\u2605 Dashboard", classes="dashboard-title"))
            for source in self._sources:
                container.mount(
                    SourceCard(
                        source,
                        max_tasks=self._max_tasks,
                        show_completed=self._show_completed,
                    )
                )
        except Exception:
            pass  # Not yet mounted

    def compose(self) -> ComposeResult:
        with VerticalScroll():
            yield Static("\u2605 Dashboard", classes="dashboard-title")
            for source in self._sources:
                yield SourceCard(
                    source,
                    max_tasks=self._max_tasks,
                    show_completed=self._show_completed,
                )

    def on_source_card_clicked(self, event: SourceCard.Clicked) -> None:
        self.post_message(self.SourceClicked(event.source_name))
