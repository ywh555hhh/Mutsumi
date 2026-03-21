"""Mutsumi TUI Application entry point."""

from __future__ import annotations

import contextlib
import json
from pathlib import Path
from typing import Any

from pydantic import ValidationError
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import Static

from mutsumi.core.loader import filter_tasks_by_scope, load_task_file
from mutsumi.core.models import TaskFile, TaskStatus
from mutsumi.core.watcher import TaskFileWatcher
from mutsumi.core.writer import save_task_file, toggle_task_status
from mutsumi.tui.detail_panel import DetailPanel
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
        Binding("enter", "show_detail", "Detail", show=False),
        Binding("escape", "close_detail", "Close", show=False),
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
        self._watcher: TaskFileWatcher | None = None
        self._self_writing = False  # Guard to skip watcher events from our own writes

    def compose(self) -> ComposeResult:
        yield HeaderBar()
        yield TaskListPanel(id="task-list")
        yield DetailPanel(id="detail-panel")
        yield FooterBar(id="footer")

    async def on_mount(self) -> None:
        """Load tasks and start file watcher."""
        await self._load_and_render()
        self._start_watcher()

    def _start_watcher(self) -> None:
        """Start watching tasks.json for external changes."""
        if not self.tasks_path.exists():
            return
        self._watcher = TaskFileWatcher(
            self.tasks_path,
            self._on_file_changed,
        )
        self._watcher.start()

    def _on_file_changed(self) -> None:
        """Called from watcher thread when tasks.json changes."""
        if self._self_writing:
            return
        # Schedule reload on the main Textual thread
        with contextlib.suppress(RuntimeError):
            self.call_from_thread(self._reload_from_disk)  # type: ignore[arg-type]

    async def _reload_from_disk(self) -> None:
        """Reload tasks.json and re-render (called on main thread)."""
        self._clear_error_banner()
        await self._load_and_render()

    async def _load_and_render(self) -> None:
        """Load task file and render the current tab."""
        try:
            self.task_file = load_task_file(self.tasks_path)
        except FileNotFoundError:
            self.task_file = None
        except (json.JSONDecodeError, ValidationError) as e:
            self.task_file = None
            self._show_error_banner(f"Invalid tasks.json: {e}")
            await self._render_current_tab()
            return
        except Exception as e:
            self.task_file = None
            self._show_error_banner(str(e))
            await self._render_current_tab()
            return

        await self._render_current_tab()

    def _show_error_banner(self, message: str) -> None:
        """Show or update the error banner."""
        self._clear_error_banner()
        banner = Static(f"\u26a0 {message}", classes="error-banner", id="error-banner")
        self.mount(banner, before=self.query_one(TaskListPanel))

    def _clear_error_banner(self) -> None:
        """Remove error banner if present."""
        try:
            banner = self.query_one("#error-banner")
            banner.remove()
        except Exception:
            pass

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

    def _write_back(self) -> None:
        """Atomically write the current task_file back to disk."""
        if self.task_file is None:
            return
        self._self_writing = True
        try:
            save_task_file(self.task_file, self.tasks_path)
        finally:
            self._self_writing = False

    async def on_header_bar_tab_changed(self, event: HeaderBar.TabChanged) -> None:
        """Re-render when tab changes."""
        # Close detail panel when switching tabs
        detail = self.query_one(DetailPanel)
        if detail.is_visible:
            detail.hide()
        await self._render_current_tab()

    def action_cursor_down(self) -> None:
        self.screen.focus_next()

    def action_cursor_up(self) -> None:
        self.screen.focus_previous()

    async def action_toggle_done(self) -> None:
        focused = self.focused
        if isinstance(focused, TaskRow):
            task_id = focused.task_data.id
            focused.toggle_done()
            # Write back to file
            if self.task_file is not None:
                toggle_task_status(self.task_file, task_id)
                self._write_back()
                # Update footer stats
                await self._update_footer()

    async def _update_footer(self) -> None:
        """Recalculate and update footer stats."""
        if self.task_file is None:
            return
        header = self.query_one(HeaderBar)
        footer = self.query_one(FooterBar)
        tasks = filter_tasks_by_scope(self.task_file.tasks, header.active_scope)
        total = len(tasks)
        done = sum(1 for t in tasks if t.status == TaskStatus.DONE)
        footer.update_stats(total, done, total - done)

    def action_show_detail(self) -> None:
        """Show detail panel for the focused task."""
        detail = self.query_one(DetailPanel)
        if detail.is_visible:
            detail.hide()
            return
        focused = self.focused
        if isinstance(focused, TaskRow):
            detail.show_task(focused.task_data)

    def action_close_detail(self) -> None:
        """Close the detail panel."""
        detail = self.query_one(DetailPanel)
        if detail.is_visible:
            detail.hide()

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

    async def on_unmount(self) -> None:
        """Cleanup watcher on exit."""
        self._stop_watcher()

    def _stop_watcher(self) -> None:
        if self._watcher is not None:
            self._watcher.stop()
            self._watcher = None


def run(path: Path | None = None) -> None:
    """Launch the Mutsumi TUI."""
    app = MutsumiApp(tasks_path=path)
    app.run()


if __name__ == "__main__":
    run()
