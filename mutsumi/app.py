"""Mutsumi TUI Application entry point."""

from __future__ import annotations

import contextlib
import json
from pathlib import Path
from typing import TYPE_CHECKING

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import Input, Static

if TYPE_CHECKING:
    from textual.widget import Widget

    from mutsumi.onboarding.bootstrap import StartupState

from mutsumi.config import load_config, save_config
from mutsumi.config.keybindings import get_keybindings
from mutsumi.core.loader import (
    filter_tasks_by_scope,
    load_task_file,
    resolve_tasks_path,
    setup_logging,
)
from mutsumi.core.models import Task, TaskFile, TaskScope, TaskStatus
from mutsumi.core.paths import personal_tasks_path
from mutsumi.core.sources import Source, SourceRegistry
from mutsumi.core.writer import (
    add_child_task,
    add_task,
    cascade_toggle_status,
    clone_task,
    create_task_from_args,
    cycle_priority,
    find_task,
    handle_recurrence,
    remove_task,
    reorder_task,
    save_task_file,
    update_task,
)
from mutsumi.i18n import get_i18n, init_i18n
from mutsumi.onboarding.bootstrap import project_tasks_path
from mutsumi.onboarding.files import (
    ensure_personal_task_file,
    ensure_project_task_file,
    register_project,
)
from mutsumi.themes import get_theme, load_theme
from mutsumi.tui.confirm_bar import ConfirmBar
from mutsumi.tui.confirm_dialog import ConfirmDialog
from mutsumi.tui.detail_panel import DetailPanel
from mutsumi.tui.footer_bar import BarMode, FooterBar
from mutsumi.tui.header_bar import HeaderBar, TabButton
from mutsumi.tui.key_manager import KeyManager, MatchResult, get_key_sequences
from mutsumi.tui.main_dashboard import MainDashboard
from mutsumi.tui.onboarding_screen import OnboardingScreen
from mutsumi.tui.priority_group import PriorityGroup, PriorityGroupHeader
from mutsumi.tui.project_attach_screen import ProjectAttachScreen
from mutsumi.tui.scope_filter import ScopeFilter
from mutsumi.tui.search_bar import SearchBar
from mutsumi.tui.task_form import TaskForm
from mutsumi.tui.task_list import TaskListPanel
from mutsumi.tui.task_row import TaskRow, _due_status


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

    .narrow-warning {
        dock: top;
        height: 1;
        background: #e5c07b;
        color: #0f0f0f;
        padding: 0 1;
        text-style: bold;
    }
    """

    # Default bindings — overridden by config keybinding preset
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
        Binding("n", "new_task", "New", show=False),
        Binding("e", "edit_task", "Edit", show=False),
        Binding("slash", "search", "Search", show=False),
        Binding("h", "collapse_group", "Collapse", show=False),
        Binding("l", "expand_group", "Expand", show=False),
        Binding("+", "priority_up", "Priority Up", show=False),
        Binding("=", "priority_up", "Priority Up", show=False),
        Binding("-", "priority_down", "Priority Down", show=False),
        Binding("_", "priority_down", "Priority Down", show=False),
        Binding("y", "copy_task", "Copy", show=False),
        Binding("p", "paste_task", "Paste", show=False),
        Binding("z", "toggle_fold", "Toggle Fold", show=False),
        Binding("question_mark", "show_help", "Help", show=False),
        Binding("i", "inline_edit", "Inline Edit", show=False),
        Binding("s", "sort", "Sort", show=False),
        Binding("G", "cursor_bottom", "Bottom", show=False, key_display="shift+g"),
        Binding("J", "move_down", "Move Down", show=False, key_display="shift+j"),
        Binding("K", "move_up", "Move Up", show=False, key_display="shift+k"),
        Binding("A", "add_child", "Add Child", show=False, key_display="shift+a"),
        Binding("P", "paste_task_above", "Paste Above", show=False, key_display="shift+p"),
        Binding("f", "cycle_scope", "Cycle Scope", show=False),
        Binding("5", "tab_5", "Tab 5", show=False),
        Binding("6", "tab_6", "Tab 6", show=False),
        Binding("7", "tab_7", "Tab 7", show=False),
        Binding("8", "tab_8", "Tab 8", show=False),
        Binding("9", "tab_9", "Tab 9", show=False),
    ]

    def __init__(
        self,
        tasks_path: Path | None = None,
        watch_paths: list[Path] | None = None,
        config_path: Path | None = None,
        startup_state: StartupState | None = None,
    ) -> None:
        # Load config before super().__init__ so theme CSS is ready
        config = load_config(config_path)
        setup_logging()
        init_i18n(config.language)

        # Apply keybindings from config (with optional user overrides)
        self._bindings_list = get_keybindings(config.keybindings, config.key_overrides or None)

        # Apply theme (sets global singleton, get_css_variables reads it)
        load_theme(config.theme)

        # Key manager for multi-key sequences
        self._keybinding_preset = config.keybindings
        self._key_manager = KeyManager(get_key_sequences(config.keybindings))

        # Config for columns and custom CSS
        self._config = config
        self._default_scope = config.default_scope
        self._columns: list[str] = getattr(
            config, "columns", ["checkbox", "title", "tags", "priority"],
        )
        self._custom_css = self._load_custom_css(config)
        self._startup_state = startup_state

        super().__init__()

        # Multi-source registry
        self._source_registry = SourceRegistry()
        if watch_paths:
            for i, wp in enumerate(watch_paths):
                name = wp.stem if wp.stem != "mutsumi" else wp.parent.name or "default"
                if i == 0:
                    name = "default"
                self._source_registry.add_source(name, wp)
        else:
            # Build sources from config projects + personal tasks + cwd
            self._build_sources_from_config(config, tasks_path)

        self._active_source = self._source_registry.source_names[0]
        self._self_writing = False

        # Search state
        self._search_query = ""

        # Clipboard for copy/paste
        self._task_clipboard: Task | None = None

        # Event logger
        self._event_logger = self._init_event_logger(config)

    # --- Source registry accessors (backward compat) ---

    def _build_sources_from_config(self, config: object, tasks_path: Path | None) -> None:
        """Build multi-source registry from config projects, personal tasks, and cwd."""
        from mutsumi.config.settings import MutsumiConfig

        # If an explicit tasks_path was passed (CLI --path or tests), skip project discovery
        if tasks_path is not None:
            self._source_registry.add_source("default", tasks_path)
            return

        has_projects = False
        if isinstance(config, MutsumiConfig) and config.projects:
            has_projects = True
            # Personal tasks
            personal_path = personal_tasks_path()
            if personal_path.exists():
                self._source_registry.add_source("personal", personal_path, is_personal=True)

            # Registered projects — prefer mutsumi.json, fallback to tasks.json
            for proj in config.projects:
                proj_dir = Path(proj.path)
                proj_file = proj_dir / "mutsumi.json"
                if not proj_file.exists():
                    fallback = proj_dir / "tasks.json"
                    if fallback.exists():
                        proj_file = fallback
                self._source_registry.add_source(proj.name, proj_file)

            # Add "main" as a virtual aggregation source (first in order)
            # We re-order: main should be first tab
            from collections import OrderedDict

            reordered: OrderedDict[str, Source] = OrderedDict()
            # Create a synthetic "main" source — it aggregates all tasks
            main_source = Source(name="main", path=personal_path)
            reordered["main"] = main_source
            for k, v in self._source_registry._sources.items():
                reordered[k] = v
            self._source_registry._sources = reordered

        if not has_projects:
            personal_path = personal_tasks_path()
            if personal_path.exists():
                self._source_registry.add_source("default", personal_path)
                return
            # Single-source fallback: just the cwd's mutsumi.json
            default_path = resolve_tasks_path()
            self._source_registry.add_source("default", default_path)

    @property
    def tasks_path(self) -> Path:
        """Path to the active source's task file."""
        src = self._source_registry.get_source(self._active_source)
        if src is not None:
            return src.path
        return Path.cwd() / "mutsumi.json"

    @property
    def task_file(self) -> TaskFile | None:
        """TaskFile of the active source."""
        src = self._source_registry.get_source(self._active_source)
        return src.task_file if src is not None else None

    @task_file.setter
    def task_file(self, value: TaskFile | None) -> None:
        """Set the TaskFile on the active source."""
        src = self._source_registry.get_source(self._active_source)
        if src is not None:
            src.task_file = value

    def _init_event_logger(self, config: object) -> object | None:
        """Initialize event logger if configured."""
        try:
            from mutsumi.config.settings import MutsumiConfig
            from mutsumi.events import EventLogger
            if isinstance(config, MutsumiConfig):
                return EventLogger(config.event_log_path)
            return EventLogger()
        except Exception:
            return None

    @staticmethod
    def _load_custom_css(config: object) -> str:
        """Load custom CSS from user-specified file."""
        from mutsumi.config.settings import MutsumiConfig

        if not isinstance(config, MutsumiConfig):
            return ""
        css_path = config.custom_css_path
        if css_path is None:
            return ""
        try:
            return css_path.read_text(encoding="utf-8")
        except Exception:
            return ""

    def get_css_variables(self) -> dict[str, str]:
        theme = get_theme()
        return {
            **super().get_css_variables(),
            "theme-bg": theme.background,
            "theme-surface": theme.surface,
            "theme-border": theme.border,
            "theme-text": theme.text,
            "theme-text-muted": theme.text_muted,
            "theme-accent": theme.accent,
            "theme-error": theme.error,
            "theme-priority-high": theme.priority_high,
            "theme-priority-normal": theme.priority_normal,
            "theme-priority-low": theme.priority_low,
        }

    def compose(self) -> ComposeResult:
        source_names = self._source_registry.source_names
        multi_source = len(source_names) > 1
        header = HeaderBar(source_names=source_names)
        yield header
        yield ScopeFilter(show_main_button=multi_source, id="scope-filter")
        yield SearchBar(id="search-bar")
        yield MainDashboard(id="main-dashboard")
        yield TaskListPanel(id="task-list")
        yield DetailPanel(id="detail-panel")
        yield ConfirmBar(id="confirm-bar")
        yield FooterBar(id="footer")

    async def on_mount(self) -> None:
        """Load tasks and start file watcher."""
        if self._startup_state is not None and self._startup_state.mode == "first_run":
            self.push_screen(OnboardingScreen(self._config, self._startup_state.is_git_repo))
            return
        if self._startup_state is not None and self._startup_state.mode == "attach_needed":
            self.push_screen(ProjectAttachScreen())
            return

        await self._initialize_main_view()

    async def _initialize_main_view(self) -> None:
        """Initialize the main task board UI and watchers."""
        header = self.query_one(HeaderBar)
        scope_filter = self.query_one(ScopeFilter)
        dashboard = self.query_one(MainDashboard)

        if header.is_multi_source:
            # Multi-source: set initial source tab, show scope filter
            header.active_source = self._active_source
            scope_filter.active_scope = self._default_scope
            # Main tab starts with dashboard visible
            if self._active_source == "main":
                dashboard.display = True
                self.query_one(TaskListPanel).display = False
                scope_filter.display = False
            else:
                dashboard.display = False
                scope_filter.display = True
        else:
            # Single-source: set initial scope tab, hide scope filter and dashboard
            scope_map = {
                "day": TaskScope.DAY,
                "week": TaskScope.WEEK,
                "month": TaskScope.MONTH,
                "inbox": TaskScope.INBOX,
            }
            initial = scope_map.get(self._default_scope, TaskScope.DAY)
            header.active_scope = initial
            scope_filter.display = False
            dashboard.display = False

        # Set notification mode on footer
        footer = self.query_one(FooterBar)
        footer._notification_mode = self._config.notification_mode

        await self._load_and_render()
        self._start_watchers()

    def on_resize(self, event: object) -> None:
        """Adapt layout to terminal width."""
        from textual.events import Resize

        if not isinstance(event, Resize):
            return
        w = event.size.width

        # Detail panel: full-width overlay at narrow terminals, percentage at wide
        detail = self.query_one(DetailPanel)
        if w < 60:
            detail.styles.width = "100%"
        else:
            detail.styles.width = "40%"

        # Show narrow-terminal warning
        self._update_narrow_warning(w)

    def _start_watchers(self) -> None:
        """Start watching all registered sources for external changes."""
        for name in self._source_registry.source_names:
            self._source_registry.start_watching(name, self._on_source_changed)

    def _on_source_changed(self, source_name: str) -> None:
        """Called from watcher thread when a source file changes."""
        if self._self_writing:
            return
        with contextlib.suppress(RuntimeError):
            self.call_from_thread(self._reload_from_disk)  # type: ignore[arg-type]

    def _on_file_changed(self) -> None:
        """Legacy callback — delegates to _on_source_changed."""
        self._on_source_changed(self._active_source)

    async def _reload_from_disk(self) -> None:
        """Reload tasks.json and re-render (called on main thread)."""
        self._clear_error_banner()
        await self._load_and_render()

    async def _load_and_render(self) -> None:
        """Load task file and render the current tab."""
        header = self.query_one(HeaderBar)

        # In multi-source mode, load all sources for dashboard
        if header.is_multi_source:
            self._source_registry.load_all()
            if self._active_source == "main":
                await self._render_dashboard()
                return

        try:
            self.task_file = load_task_file(self.tasks_path)
        except FileNotFoundError:
            self.task_file = None
        except json.JSONDecodeError:
            self.task_file = None
            self._show_error_banner(get_i18n().t("errors.json_invalid"))
            await self._render_current_tab()
            return
        except Exception as e:
            self.task_file = None
            self._show_error_banner(str(e))
            await self._render_current_tab()
            return

        # Show skipped tasks warning in footer
        if self.task_file is not None and self.task_file.skipped_count > 0:
            n = self.task_file.skipped_count
            footer = self.query_one(FooterBar)
            footer.show_notification(f"{n} task(s) skipped — see error log")

        await self._render_current_tab()

    def _show_error_banner(self, message: str) -> None:
        """Show or update the error banner."""
        self._clear_error_banner()
        safe_msg = message.replace("[", "\\[")
        banner = Static(f"\u26a0 {safe_msg}", classes="error-banner", id="error-banner")
        self.mount(banner, before=self.query_one(TaskListPanel))

    def _clear_error_banner(self) -> None:
        """Remove error banner if present."""
        try:
            banner = self.query_one("#error-banner")
            banner.remove()
        except Exception:
            pass

    def _update_narrow_warning(self, width: int) -> None:
        """Show or hide 'terminal too narrow' warning based on width."""
        try:
            existing = self.query_one("#narrow-warning")
            if width >= 40:
                existing.remove()
        except Exception:
            if width < 40:
                warning = Static(
                    f"\u26a0 {get_i18n().t('errors.terminal_narrow')}",
                    classes="narrow-warning",
                    id="narrow-warning",
                )
                self.mount(warning, before=self.query_one(TaskListPanel))

    async def _render_current_tab(self) -> None:
        """Filter tasks by current scope and update the task list."""
        header = self.query_one(HeaderBar)
        panel = self.query_one(TaskListPanel)
        footer = self.query_one(FooterBar)

        if self.task_file is None:
            await panel.update_tasks([], columns=self._columns)
            footer.update_stats(0, 0, 0)
            return

        # Determine active scope
        if header.is_multi_source:
            scope_filter = self.query_one(ScopeFilter)
            scope_key = scope_filter.active_scope
            if scope_key == "all":
                tasks = list(self.task_file.tasks)
            else:
                scope_map = {
                    "day": TaskScope.DAY,
                    "week": TaskScope.WEEK,
                    "month": TaskScope.MONTH,
                    "inbox": TaskScope.INBOX,
                }
                scope = scope_map.get(scope_key, TaskScope.DAY)
                tasks = filter_tasks_by_scope(self.task_file.tasks, scope)
        else:
            scope = header.active_scope
            tasks = filter_tasks_by_scope(self.task_file.tasks, scope)

        await panel.update_tasks(tasks, columns=self._columns)

        # Apply search-as-filter: dim non-matching rows (don't hide them)
        if self._search_query:
            panel.dim_non_matching(self._search_query)

        # Auto-focus the first task row; if empty, focus the active tab button
        # so the user still has a keyboard-navigable anchor.
        rows = panel.query(TaskRow)
        if rows:
            rows.first().focus()
        else:
            self._focus_active_tab()

        total = len(tasks)
        done = sum(1 for t in tasks if t.status == TaskStatus.DONE)
        overdue = sum(
            1 for t in tasks
            if not t.is_done and t.due_date and _due_status(t.due_date) == "overdue"
        )
        footer.update_stats(total, done, total - done, overdue)

    async def _render_dashboard(self) -> None:
        """Render the Main dashboard with all sources' progress."""
        dashboard = self.query_one(MainDashboard)
        footer = self.query_one(FooterBar)

        # Collect sources (skip "main" — it's the virtual aggregation tab)
        sources = [
            src for name, src in self._source_registry._sources.items()
            if name != "main"
        ]
        dashboard.set_sources(sources)

        # Aggregate stats across all sources
        all_tasks = self._source_registry.all_tasks()
        total = len(all_tasks)
        done = sum(1 for _, t in all_tasks if t.status == TaskStatus.DONE)
        footer.update_stats(total, done, total - done)

    def _focus_active_tab(self) -> None:
        """Focus the empty-state button (preferred) or the active tab."""
        # Prefer the [+ New Task] button in empty state
        try:
            btn = self.query_one("#empty-new-btn")
            btn.focus()
            return
        except Exception:
            pass
        # Fallback: focus active tab button
        header = self.query_one(HeaderBar)
        for tab in header.query(TabButton):
            if tab.has_class("active"):
                tab.focus()
                return
        tabs = header.query(TabButton)
        if tabs:
            tabs.first().focus()

    def _task_matches_query(self, task: Task, query: str) -> bool:
        """Check if a task matches the search query."""
        if query in task.title.lower():
            return True
        if any(query in tag.lower() for tag in task.tags):
            return True
        return bool(task.description and query in task.description.lower())

    def _write_back(self) -> None:
        """Atomically write the current task_file back to disk.

        Sets _self_writing flag and keeps it True for longer than the
        watcher's debounce window (0.1s) to prevent self-triggered reloads.
        """
        import threading

        if self.task_file is None:
            return
        self._self_writing = True
        try:
            save_task_file(self.task_file, self.tasks_path)
        except Exception:
            self._self_writing = False
            raise

        # Keep flag True past the debounce window (0.1s) + safety margin
        def _reset_flag() -> None:
            self._self_writing = False

        timer = threading.Timer(0.3, _reset_flag)
        timer.daemon = True
        timer.start()

    def _log_event(self, event_type: str, **data: str | int | list[str] | None) -> None:
        """Log an event if event logger is available."""
        if self._event_logger is not None:
            from mutsumi.events import EventLogger

            if isinstance(self._event_logger, EventLogger):
                self._event_logger.log(event_type, **data)

    # --- Key manager integration ---

    async def on_key(self, event: object) -> None:
        """Intercept key events for multi-key sequences.

        Priority: Input focused → skip | ConfirmBar → handled by ConfirmBar |
                  KeyManager → Textual Binding
        """
        from textual.events import Key

        if not isinstance(event, Key):
            return

        # Don't intercept when Input is focused (search bar, forms)
        if isinstance(self.focused, Input):
            return

        # Don't intercept when ConfirmBar is visible (it handles its own keys)
        confirm_bar = self.query_one(ConfirmBar)
        if confirm_bar.display:
            return

        # Check if this key is a first-char of any sequence
        key = event.key
        first_chars = {seq.keys[0] for seq in self._key_manager.sequences}

        # If buffer is empty and key isn't a sequence starter, let Textual handle it
        if not self._key_manager.pending and key not in first_chars:
            return

        # Feed key to manager
        result, action = self._key_manager.feed(key)

        if result == MatchResult.EXACT:
            # Matched a sequence — stop event and dispatch action
            event.stop()
            event.prevent_default()
            await self._dispatch_sequence_action(action or "")
        elif result == MatchResult.PREFIX:
            # Partial match — stop event, wait for more keys
            event.stop()
            event.prevent_default()
        # NO_MATCH: buffer cleared, event flows to Textual bindings naturally

    async def _dispatch_sequence_action(self, action: str) -> None:
        """Dispatch a matched multi-key sequence action."""
        if action == "delete_confirm":
            self._start_delete_confirm()
        elif action == "cursor_top":
            self.action_cursor_top()

    # --- Tab events ---

    async def on_header_bar_tab_changed(self, event: HeaderBar.TabChanged) -> None:
        """Re-render when scope tab changes (single-source mode)."""
        detail = self.query_one(DetailPanel)
        if detail.is_visible:
            detail.hide()
        await self._render_current_tab()

    async def on_header_bar_source_tab_changed(self, event: HeaderBar.SourceTabChanged) -> None:
        """Switch active source and re-render (multi-source mode)."""
        self._active_source = event.source_name
        detail = self.query_one(DetailPanel)
        if detail.is_visible:
            detail.hide()

        dashboard = self.query_one(MainDashboard)
        panel = self.query_one(TaskListPanel)
        scope_filter = self.query_one(ScopeFilter)

        if event.source_name == "main":
            # Show dashboard, hide task list and scope filter
            dashboard.display = True
            panel.display = False
            scope_filter.display = False
        else:
            # Show task list and scope filter, hide dashboard
            dashboard.display = False
            panel.display = True
            scope_filter.display = True
            # Reload active source
            self._source_registry.load_source(self._active_source)

        await self._load_and_render()

    async def on_scope_filter_scope_changed(self, event: ScopeFilter.ScopeChanged) -> None:
        """Re-render when scope filter changes."""
        await self._render_current_tab()

    async def on_scope_filter_main_requested(self, event: ScopeFilter.MainRequested) -> None:
        """Return to Main dashboard when user clicks the Main button in scope filter."""
        header = self.query_one(HeaderBar)
        header.active_source = "main"

    async def on_main_dashboard_source_clicked(self, event: MainDashboard.SourceClicked) -> None:
        """Jump to clicked source from dashboard."""
        header = self.query_one(HeaderBar)
        header.active_source = event.source_name

    # --- Search events ---

    async def on_search_bar_query_changed(self, event: SearchBar.QueryChanged) -> None:
        """Filter tasks based on search query (dim non-matches)."""
        self._search_query = event.query
        footer = self.query_one(FooterBar)
        footer.set_mode(BarMode.SEARCH)
        panel = self.query_one(TaskListPanel)
        panel.dim_non_matching(event.query)

    async def on_search_bar_search_closed(self, event: SearchBar.SearchClosed) -> None:
        """Clear search and re-render."""
        self._search_query = ""
        footer = self.query_one(FooterBar)
        footer.set_mode(BarMode.NORMAL)
        await self._render_current_tab()

    async def on_onboarding_screen_finished(self, event: OnboardingScreen.Finished) -> None:
        """Persist first-run onboarding choices, hot-reload, and continue startup."""
        selections = event.selections
        if not event.skipped:
            self._config.language = selections.get("language", self._config.language)
            self._config.keybindings = selections.get("keybindings", self._config.keybindings)
            self._config.theme = selections.get("theme", self._config.theme)

            preferred_agent = selections.get("preferred_agent", "none")
            self._config.preferred_agent = (
                preferred_agent if preferred_agent != "none" else None
            )
            self._config.onboarding_completed = True

            workspace_mode = selections.get("workspace_mode", "personal-only")
            if workspace_mode in {"personal-only", "personal+project"}:
                ensure_personal_task_file()
            if workspace_mode in {"project-only", "personal+project"}:
                project_path = ensure_project_task_file(
                    self._startup_state.cwd if self._startup_state else None,
                )
                register_project(self._config, project_path.parent)
            save_config(self._config)

            # Hot-reload i18n
            init_i18n(self._config.language)

            # Hot-reload theme (load_theme sets global singleton, refresh_css re-reads variables)
            load_theme(self._config.theme)
            self.refresh_css()

            # Hot-reload keybindings
            self._bindings_list = get_keybindings(
                self._config.keybindings,
                self._config.key_overrides or None,
            )
            self._keybinding_preset = self._config.keybindings
            self._key_manager = KeyManager(get_key_sequences(self._config.keybindings))

            # Install skills for selected agent
            if preferred_agent and preferred_agent != "none":
                from mutsumi.core.skill_installer import install_for_agent

                with contextlib.suppress(ValueError, OSError):
                    install_for_agent(preferred_agent)

        self._source_registry = SourceRegistry()
        self._build_sources_from_config(self._config, None)
        source_names = self._source_registry.source_names
        self._active_source = source_names[0]
        self._default_scope = self._config.default_scope

        # Rebuild HeaderBar tabs and ScopeFilter for the new source layout
        header = self.query_one(HeaderBar)
        header.set_sources(source_names)
        scope_filter = self.query_one(ScopeFilter)
        scope_filter.set_show_main_button(len(source_names) > 1)

        await self._initialize_main_view()

    async def on_project_attach_screen_resolved(self, event: ProjectAttachScreen.Resolved) -> None:
        """Handle lightweight project attach after onboarding."""
        if self._startup_state is None:
            await self._initialize_main_view()
            return

        if event.action in {"register", "create"}:
            project_path = (
                ensure_project_task_file(self._startup_state.cwd)
                if event.action == "create"
                else project_tasks_path(self._startup_state.cwd)
            )
            register_project(self._config, project_path.parent)
            save_config(self._config)
            self._source_registry = SourceRegistry()
            self._build_sources_from_config(self._config, None)
            source_names = self._source_registry.source_names
            self._active_source = source_names[0]

            # Rebuild HeaderBar tabs and ScopeFilter for the new source layout
            header = self.query_one(HeaderBar)
            header.set_sources(source_names)
            scope_filter = self.query_one(ScopeFilter)
            scope_filter.set_show_main_button(len(source_names) > 1)

        await self._initialize_main_view()

    # --- Task form events ---

    async def on_task_form_task_submitted(self, event: TaskForm.TaskSubmitted) -> None:
        """Handle task creation or edit from the form."""
        if self.task_file is None:
            self.task_file = TaskFile(version=1, tasks=[])

        footer = self.query_one(FooterBar)

        if event.editing_id:
            # Edit existing task
            fields: dict[str, str | list[str] | None] = {
                "title": event.title,
                "priority": event.priority,
                "scope": event.scope,
            }
            if event.tags:
                fields["tags"] = [t.strip() for t in event.tags.split(",") if t.strip()]
            else:
                fields["tags"] = []
            if event.description:
                fields["description"] = event.description
            update_task(self.task_file, event.editing_id, **fields)
            self._log_event("task_edited", task_id=event.editing_id, title=event.title)
            footer.show_notification(f'Updated: "{event.title}"')
        else:
            # Create new task
            tag_list = [t.strip() for t in event.tags.split(",") if t.strip()] if event.tags else []
            task = create_task_from_args(
                title=event.title,
                priority=event.priority,
                scope=event.scope,
                tags=tag_list,
                description=event.description or None,
            )
            if event.parent_id:
                add_child_task(self.task_file, event.parent_id, task)
                self._log_event(
                    "child_task_added",
                    task_id=task.id, parent_id=event.parent_id, title=event.title,
                )
                footer.show_notification(f'Added subtask: "{event.title}"')
            else:
                add_task(self.task_file, task)
                self._log_event("task_added", task_id=task.id, title=event.title)
                footer.show_notification(f'Created: "{event.title}"')

        self._write_back()
        await self._load_and_render()

    # --- ConfirmBar events ---

    async def on_confirm_bar_resolved(self, event: ConfirmBar.Resolved) -> None:
        """Handle inline confirm bar resolution."""
        footer = self.query_one(FooterBar)
        footer.set_mode(BarMode.NORMAL)
        if event.confirmed and self.task_file is not None:
            task = find_task(self.task_file, event.task_id)
            title = task.title if task else event.task_id
            remove_task(self.task_file, event.task_id)
            self._write_back()
            self._log_event("task_deleted", task_id=event.task_id, title=title)
            footer.show_notification(f'Deleted: "{title}"')
            await self._load_and_render()
        else:
            footer.show_notification("Cancelled")

    # --- Confirm dialog events (kept for DetailPanel delete) ---

    async def on_confirm_dialog_confirmed(self, event: ConfirmDialog.Confirmed) -> None:
        """Handle task deletion confirmation from modal dialog."""
        if self.task_file is None:
            return
        task = find_task(self.task_file, event.task_id)
        title = task.title if task else event.task_id
        remove_task(self.task_file, event.task_id)
        self._write_back()
        self._log_event("task_deleted", task_id=event.task_id, title=title)
        footer = self.query_one(FooterBar)
        footer.show_notification(f'Deleted: "{title}"')
        await self._load_and_render()

    # --- Footer action button events ---

    async def on_footer_bar_action_requested(self, event: FooterBar.ActionRequested) -> None:
        """Handle clicks on footer action buttons."""
        if event.action == "new_task":
            self.action_new_task()
        elif event.action == "search":
            self.action_search()
        elif event.action == "sort":
            await self.action_sort()

    def on_empty_state_new_task_requested(self, event: object) -> None:
        """Handle [+ New Task] button in empty state."""
        self.action_new_task()

    # --- Detail panel action button events ---

    def on_detail_panel_edit_requested(self, event: DetailPanel.EditRequested) -> None:
        """Handle Edit button click in detail panel."""
        if self.task_file is None:
            return
        task = find_task(self.task_file, event.task_id)
        if task is not None:
            self.push_screen(TaskForm(task=task))

    def on_detail_panel_delete_requested(self, event: DetailPanel.DeleteRequested) -> None:
        """Handle Delete button click in detail panel."""
        self.push_screen(ConfirmDialog(event.task_id, event.task_title))

    def on_detail_panel_add_child_requested(self, event: DetailPanel.AddChildRequested) -> None:
        """Handle +Subtask button click in detail panel."""
        self.push_screen(
            TaskForm(parent_id=event.task_id, default_scope=self._current_scope_value())
        )
    # --- TaskRow click-to-detail events ---

    def on_task_row_detail_clicked(self, event: TaskRow.DetailClicked) -> None:
        """Handle click on the title area of a TaskRow — open detail."""
        detail = self.query_one(DetailPanel)
        detail.show_task(event.task)

    # --- TaskRow inline edit events ---

    async def on_task_row_title_edited(self, event: TaskRow.TitleEdited) -> None:
        """Handle inline title edit from TaskRow."""
        if self.task_file is None:
            return
        update_task(self.task_file, event.task_id, title=event.new_title)
        self._write_back()
        self._log_event("task_edited", task_id=event.task_id, title=event.new_title)
        footer = self.query_one(FooterBar)
        footer.show_notification(f'Updated: "{event.new_title}"')
        await self._load_and_render()
        self._restore_focus(event.task_id)

    # --- Actions ---

    def _input_focused(self) -> bool:
        """Return True if an Input widget is focused (e.g. search bar)."""
        return isinstance(self.focused, Input)

    async def action_quit(self) -> None:
        if self._input_focused():
            return
        await super().action_quit()

    def _focusable_items(self) -> list[Widget]:
        """Return the ordered list of focusable items (headers + visible rows)."""
        items: list[Widget] = []
        for group in self.query(PriorityGroup):
            header = group.query_one(PriorityGroupHeader)
            items.append(header)
            if not header.collapsed:
                for row in group.query(TaskRow):
                    items.append(row)
        return items

    def action_cursor_down(self) -> None:
        if self._input_focused():
            return
        items = self._focusable_items()
        if not items:
            return
        focused = self.focused
        if focused in items:
            idx = items.index(focused)
            if idx < len(items) - 1:
                items[idx + 1].focus()
        else:
            items[0].focus()

    def action_cursor_up(self) -> None:
        if self._input_focused():
            return
        items = self._focusable_items()
        if not items:
            return
        focused = self.focused
        if focused in items:
            idx = items.index(focused)
            if idx > 0:
                items[idx - 1].focus()
        else:
            items[-1].focus()

    def action_cursor_top(self) -> None:
        items = self._focusable_items()
        if items:
            items[0].focus()

    def action_cursor_bottom(self) -> None:
        items = self._focusable_items()
        if items:
            items[-1].focus()

    def action_collapse_group(self) -> None:
        """Collapse the priority group of the focused task."""
        if self._input_focused():
            return
        focused = self.focused
        if isinstance(focused, PriorityGroupHeader):
            if not focused.collapsed:
                focused._toggle()
            return
        if isinstance(focused, TaskRow):
            parent = focused.parent
            if isinstance(parent, PriorityGroup):
                header = parent.query_one(PriorityGroupHeader)
                if not header.collapsed:
                    header._toggle()

    def action_expand_group(self) -> None:
        """Expand the priority group of the focused task."""
        if self._input_focused():
            return
        focused = self.focused
        if isinstance(focused, PriorityGroupHeader):
            if focused.collapsed:
                focused._toggle()
            return
        if isinstance(focused, TaskRow):
            parent = focused.parent
            if isinstance(parent, PriorityGroup):
                header = parent.query_one(PriorityGroupHeader)
                if header.collapsed:
                    header._toggle()

    async def action_toggle_done(self) -> None:
        if self._input_focused():
            return
        focused = self.focused
        if isinstance(focused, TaskRow):
            task_id = focused.task_data.id
            focused.toggle_done()
            if self.task_file is not None:
                cascade_toggle_status(self.task_file, task_id)
                # Handle recurrence: if task was just marked done and has recurrence
                task = find_task(self.task_file, task_id)
                if task is not None and task.is_done:
                    handle_recurrence(task)
                self._write_back()
                self._log_event("task_toggled", task_id=task_id)
                await self._load_and_render()
                self._restore_focus(task_id)

    async def _update_footer(self) -> None:
        """Recalculate and update footer stats."""
        if self.task_file is None:
            return
        header = self.query_one(HeaderBar)
        footer = self.query_one(FooterBar)
        tasks = filter_tasks_by_scope(self.task_file.tasks, header.active_scope)
        total = len(tasks)
        done = sum(1 for t in tasks if t.status == TaskStatus.DONE)
        overdue = sum(
            1 for t in tasks
            if not t.is_done and t.due_date and _due_status(t.due_date) == "overdue"
        )
        footer.update_stats(total, done, total - done, overdue)

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
        """Close the detail panel or search bar."""
        # Clear KeyManager buffer on Escape
        self._key_manager.clear()

        search = self.query_one(SearchBar)
        if search.is_visible:
            search.hide()
            return
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

    def action_tab_5(self) -> None:
        self.query_one(HeaderBar).set_tab(4)

    def action_tab_6(self) -> None:
        self.query_one(HeaderBar).set_tab(5)

    def action_tab_7(self) -> None:
        self.query_one(HeaderBar).set_tab(6)

    def action_tab_8(self) -> None:
        self.query_one(HeaderBar).set_tab(7)

    def action_tab_9(self) -> None:
        self.query_one(HeaderBar).set_tab(8)

    def action_cycle_scope(self) -> None:
        """Cycle through scope filters (f key)."""
        if self._input_focused():
            return
        header = self.query_one(HeaderBar)
        if header.is_multi_source:
            scope_filter = self.query_one(ScopeFilter)
            scope_filter.next_scope()

    def _current_scope_value(self) -> str:
        """Return the active scope as a string for TaskForm defaults."""
        header = self.query_one(HeaderBar)
        if header.is_multi_source:
            scope_filter = self.query_one(ScopeFilter)
            scope_key = scope_filter.active_scope
            return scope_key if scope_key != "all" else "inbox"
        return header.active_scope.value

    def action_new_task(self) -> None:
        """Open new task form."""
        if isinstance(self.focused, Input):
            return
        self.push_screen(TaskForm(default_scope=self._current_scope_value()))

    def action_edit_task(self) -> None:
        """Open edit form for focused task."""
        if isinstance(self.focused, Input):
            return
        focused = self.focused
        if isinstance(focused, TaskRow):
            self.push_screen(TaskForm(task=focused.task_data))

    def _start_delete_confirm(self) -> None:
        """Start inline delete confirmation (triggered by dd sequence)."""
        if isinstance(self.focused, Input):
            return
        focused = self.focused
        if isinstance(focused, TaskRow):
            confirm_bar = self.query_one(ConfirmBar)
            footer = self.query_one(FooterBar)
            footer.set_mode(BarMode.CONFIRM)
            confirm_bar.show(focused.task_data.id, focused.task_data.title)

    def action_search(self) -> None:
        """Open the search bar."""
        if isinstance(self.focused, Input):
            return
        search = self.query_one(SearchBar)
        if search.is_visible:
            search.hide()
        else:
            search.show()

    # --- New actions (Step 4) ---

    async def action_priority_up(self) -> None:
        """Increase focused task's priority (low → normal → high)."""
        if self._input_focused():
            return
        focused = self.focused
        if isinstance(focused, TaskRow) and self.task_file is not None:
            task_id = focused.task_data.id
            if cycle_priority(self.task_file, task_id, direction=1):
                self._write_back()
                self._log_event("priority_changed", task_id=task_id)
                await self._load_and_render()
                self._restore_focus(task_id)

    async def action_priority_down(self) -> None:
        """Decrease focused task's priority (high → normal → low)."""
        if self._input_focused():
            return
        focused = self.focused
        if isinstance(focused, TaskRow) and self.task_file is not None:
            task_id = focused.task_data.id
            if cycle_priority(self.task_file, task_id, direction=-1):
                self._write_back()
                self._log_event("priority_changed", task_id=task_id)
                await self._load_and_render()
                self._restore_focus(task_id)

    async def action_move_up(self) -> None:
        """Move focused task up in its sibling list."""
        if self._input_focused():
            return
        focused = self.focused
        if isinstance(focused, TaskRow) and self.task_file is not None:
            task_id = focused.task_data.id
            if reorder_task(self.task_file, task_id, direction=-1):
                self._write_back()
                self._log_event("task_reordered", task_id=task_id)
                await self._load_and_render()
                self._restore_focus(task_id)

    async def action_move_down(self) -> None:
        """Move focused task down in its sibling list."""
        if self._input_focused():
            return
        focused = self.focused
        if isinstance(focused, TaskRow) and self.task_file is not None:
            task_id = focused.task_data.id
            if reorder_task(self.task_file, task_id, direction=1):
                self._write_back()
                self._log_event("task_reordered", task_id=task_id)
                await self._load_and_render()
                self._restore_focus(task_id)

    def action_copy_task(self) -> None:
        """Copy focused task to internal clipboard."""
        if self._input_focused():
            return
        focused = self.focused
        if isinstance(focused, TaskRow):
            self._task_clipboard = focused.task_data
            footer = self.query_one(FooterBar)
            footer.show_notification(f'Copied: "{focused.task_data.title}"')

    async def action_paste_task(self) -> None:
        """Paste task from clipboard as a clone."""
        if self._input_focused():
            return
        if self._task_clipboard is None or self.task_file is None:
            footer = self.query_one(FooterBar)
            footer.show_notification("Nothing to paste")
            return
        cloned = clone_task(self.task_file, self._task_clipboard.id)
        if cloned is None:
            # Source task was removed; create a fresh clone from clipboard data
            from copy import deepcopy

            from mutsumi.core.id import generate_task_id

            cloned = deepcopy(self._task_clipboard)
            cloned.id = generate_task_id()
            add_task(self.task_file, cloned)
        self._write_back()
        self._log_event("task_pasted", task_id=cloned.id, title=cloned.title)
        footer = self.query_one(FooterBar)
        footer.show_notification(f'Pasted: "{cloned.title}"')
        await self._load_and_render()

    def action_toggle_fold(self) -> None:
        """Toggle fold on the focused group."""
        if self._input_focused():
            return
        focused = self.focused
        if isinstance(focused, PriorityGroupHeader):
            focused._toggle()
            return
        if isinstance(focused, TaskRow):
            parent = focused.parent
            if isinstance(parent, PriorityGroup):
                header = parent.query_one(PriorityGroupHeader)
                header._toggle()

    def action_show_help(self) -> None:
        """Open the help screen."""
        if self._input_focused():
            return
        from mutsumi.tui.help_screen import HelpScreen

        self.push_screen(HelpScreen(self._keybinding_preset))

    def action_inline_edit(self) -> None:
        """Start inline title editing on the focused task row."""
        if self._input_focused():
            return
        focused = self.focused
        if isinstance(focused, TaskRow):
            focused.start_editing()

    async def action_sort(self) -> None:
        """Open the sort bar."""
        if self._input_focused():
            return
        from mutsumi.tui.sort_bar import SortBar

        self.push_screen(SortBar())

    def action_add_child(self) -> None:
        """Open new task form as a subtask of the focused task."""
        if self._input_focused():
            return
        focused = self.focused
        if isinstance(focused, TaskRow):
            self.push_screen(
                TaskForm(
                    parent_id=focused.task_data.id,
                    default_scope=self._current_scope_value(),
                )
            )

    async def action_paste_task_above(self) -> None:
        """Paste task from clipboard BEFORE the focused task (P key)."""
        if self._input_focused():
            return
        if self._task_clipboard is None or self.task_file is None:
            footer = self.query_one(FooterBar)
            footer.show_notification("Nothing to paste")
            return

        from copy import deepcopy

        from mutsumi.core.id import generate_task_id

        cloned = deepcopy(self._task_clipboard)
        cloned.id = generate_task_id()

        # Insert before the focused task
        focused = self.focused
        if isinstance(focused, TaskRow):
            target_id = focused.task_data.id
            inserted = self._insert_before(self.task_file.tasks, target_id, cloned)
            if not inserted:
                add_task(self.task_file, cloned)
        else:
            add_task(self.task_file, cloned)

        self._write_back()
        self._log_event("task_pasted", task_id=cloned.id, title=cloned.title)
        footer = self.query_one(FooterBar)
        footer.show_notification(f'Pasted above: "{cloned.title}"')
        await self._load_and_render()

    def _insert_before(self, tasks: list[Task], target_id: str, new_task: Task) -> bool:
        """Insert *new_task* before the task with *target_id* in *tasks* list.

        Searches recursively through children.
        """
        for i, task in enumerate(tasks):
            if task.id == target_id:
                tasks.insert(i, new_task)
                return True
            if task.children and self._insert_before(task.children, target_id, new_task):
                return True
        return False

    async def on_sort_bar_sort_selected(self, event: object) -> None:
        """Handle sort selection from SortBar."""
        from mutsumi.core.loader import sort_tasks
        from mutsumi.tui.sort_bar import SortBar

        if not isinstance(event, SortBar.SortSelected):
            return
        if self.task_file is None:
            return
        self.task_file.tasks = sort_tasks(
            self.task_file.tasks, event.field, event.reverse
        )
        self._write_back()
        await self._load_and_render()
        footer = self.query_one(FooterBar)
        direction = "desc" if event.reverse else "asc"
        footer.show_notification(f"Sorted by {event.field} ({direction})")

    # --- Focus restoration ---

    def _restore_focus(self, task_id: str) -> None:
        """Find the TaskRow with *task_id* and focus it."""
        for row in self.query(TaskRow):
            if row.task_data.id == task_id:
                row.focus()
                return

    # --- Cleanup ---

    async def on_unmount(self) -> None:
        """Cleanup watchers on exit."""
        self._stop_watchers()

    def _stop_watchers(self) -> None:
        self._source_registry.stop_all_watchers()


def run(
    path: Path | None = None,
    watch_paths: list[Path] | None = None,
    startup_state: StartupState | None = None,
) -> None:
    """Launch the Mutsumi TUI."""
    app = MutsumiApp(tasks_path=path, watch_paths=watch_paths, startup_state=startup_state)
    app.run()


if __name__ == "__main__":
    run()
