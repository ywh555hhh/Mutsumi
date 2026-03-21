"""Mutsumi TUI Application entry point."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import Static

from mutsumi.core.loader import filter_tasks_by_scope, load_task_file
from mutsumi.core.models import TaskFile, TaskStatus
from mutsumi.tui.footer_bar import FooterBar
from mutsumi.tui.header_bar import HeaderBar
from mutsumi.tui.task_list import TaskListPanel
from mutsumi.tui.task_row import TaskRow


class MutsumiApp(App[None]):
    """The Mutsumi TUI application."""

    TITLE = "mutsumi"

    DEFAULT_CSS = """
    Screen {
        background: #0f0f0f;
    }

    .error-banner {
        dock: top;
        height: 1;
        background: #e06c75;
        color: #0f0f0f;
        padding: 0 1;
        text-style: bold;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("j", "cursor_down", "Down", show=False),
        Binding("k", "cursor_up", "Up", show=False),
        Binding("space", "toggle_done", "Toggle", show=False),
        Binding("tab", "next_tab", "Next Tab", show=False),
        Binding("shift+tab", "prev_tab", "Prev Tab", show=False),
        Binding("1", "tab_1", "Today", show=False),
        Binding("2", "tab_2", "Week", show=False),
        Binding("3", "tab_3", "Month", show=False),
        Binding("4", "tab_4", "Inbox", show=False),
    ]

    def __init__(self, tasks_path: Path | None = None, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.tasks_path = tasks_path or (Path.cwd() / "tasks.json")
        self.task_file: TaskFile | None = None

    def compose(self) -> ComposeResult:
        yield HeaderBar()
        yield TaskListPanel(id="task-list")
        yield FooterBar(id="footer")

    async def on_mount(self) -> None:
        """Load tasks on startup."""
        await self._load_and_render()

    async def _load_and_render(self) -> None:
        """Load task file and render the current tab."""
        try:
            self.task_file = load_task_file(self.tasks_path)
        except FileNotFoundError:
            self.task_file = None
        except Exception as e:
            self.task_file = None
            await self.mount(
                Static(
                    f"\u26a0 {e}",
                    classes="error-banner",
                ),
                before=self.query_one(TaskListPanel),
            )
            return

        await self._render_current_tab()

    async def _render_current_tab(self) -> None:
        """Filter tasks by current scope and update the task list."""
        header = self.query_one(HeaderBar)
        panel = self.query_one(TaskListPanel)
        footer = self.query_one(FooterBar)

        if self.task_file is None:
            await panel.update_tasks([])
            footer.update_stats(0, 0, 0)
            return

        scope = header.active_scope
        tasks = filter_tasks_by_scope(self.task_file.tasks, scope)
        await panel.update_tasks(tasks)

        # Auto-focus the first task row
        rows = panel.query(TaskRow)
        if rows:
            rows.first().focus()

        total = len(tasks)
        done = sum(1 for t in tasks if t.status == TaskStatus.DONE)
        footer.update_stats(total, done, total - done)

    async def on_header_bar_tab_changed(self, event: HeaderBar.TabChanged) -> None:
        """Re-render when tab changes."""
        await self._render_current_tab()

    def action_cursor_down(self) -> None:
        self.screen.focus_next()

    def action_cursor_up(self) -> None:
        self.screen.focus_previous()

    def action_toggle_done(self) -> None:
        focused = self.focused
        if isinstance(focused, TaskRow):
            focused.toggle_done()

    def action_next_tab(self) -> None:
        self.query_one(HeaderBar).next_tab()

    def action_prev_tab(self) -> None:
        self.query_one(HeaderBar).prev_tab()

    def action_tab_1(self) -> None:
        self.query_one(HeaderBar).set_tab(0)

    def action_tab_2(self) -> None:
        self.query_one(HeaderBar).set_tab(1)

    def action_tab_3(self) -> None:
        self.query_one(HeaderBar).set_tab(2)

    def action_tab_4(self) -> None:
        self.query_one(HeaderBar).set_tab(3)


def run(path: Path | None = None) -> None:
    """Launch the Mutsumi TUI."""
    app = MutsumiApp(tasks_path=path)
    app.run()


if __name__ == "__main__":
    run()
