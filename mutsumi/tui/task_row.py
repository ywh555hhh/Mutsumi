"""Single task row widget for the Mutsumi TUI."""

from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING, Any

from rich.text import Text
from textual.message import Message
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Input

from mutsumi.core.models import Task, TaskPriority
from mutsumi.themes import get_theme

if TYPE_CHECKING:
    from textual.app import ComposeResult
    from textual.events import Click

PRIORITY_STARS: dict[TaskPriority, str] = {
    TaskPriority.HIGH: "\u2605\u2605\u2605",
    TaskPriority.NORMAL: "\u2605\u2605",
    TaskPriority.LOW: "\u2605",
}


def _priority_star_style(priority: TaskPriority) -> str:
    """Return the Rich style for a priority star from the current theme."""
    theme = get_theme()
    return {
        TaskPriority.HIGH: theme.priority_high,
        TaskPriority.NORMAL: theme.priority_normal,
        TaskPriority.LOW: theme.priority_low,
    }[priority]

INDENT_GLYPH = "  \u2514\u2500 "

# Width of the checkbox region "[ ] │" including left padding
_CHECKBOX_COLS = 6

# All possible columns for dynamic layout
COLUMN_RENDERERS: dict[str, str] = {
    "checkbox": "_render_checkbox",
    "title": "_render_title",
    "tags": "_render_tags",
    "priority": "_render_priority",
    "due": "_render_due",
    "effort": "_render_effort",
    "progress": "_render_progress",
}


def _due_status(due_date: str | None) -> str | None:
    """Return 'overdue', 'today', or None based on due_date vs today."""
    if due_date is None:
        return None
    try:
        due = date.fromisoformat(due_date)
    except ValueError:
        return None
    today = date.today()
    if due < today:
        return "overdue"
    if due == today:
        return "today"
    return None


class TaskRow(Widget, can_focus=True):
    """Renders a single task as a one-line row.

    Supports inline title editing: call ``start_editing()`` to overlay
    an Input widget. Enter saves, Escape cancels.
    """

    DEFAULT_CSS = """
    TaskRow {
        height: auto;
        min-height: 1;
        padding: 0 1;
        color: $theme-text;
    }

    TaskRow:focus {
        background: $theme-surface;
    }

    TaskRow:hover {
        background: $theme-surface;
    }

    TaskRow.done {
        color: $theme-text-muted;
    }

    TaskRow.dimmed {
        opacity: 0.3;
    }

    TaskRow .inline-edit {
        height: 1;
        border: none;
        padding: 0;
        background: $theme-surface;
        color: $theme-text;
    }
    """

    class DetailClicked(Message):
        """Posted when the title area of a row is clicked."""

        def __init__(self, task: Task) -> None:
            self.task = task
            super().__init__()

    class TitleEdited(Message):
        """Posted when inline title edit is confirmed."""

        def __init__(self, task_id: str, new_title: str) -> None:
            self.task_id = task_id
            self.new_title = new_title
            super().__init__()

    toggled = reactive(False)
    editing = reactive(False)
    dimmed = reactive(False)

    def __init__(
        self,
        task: Task,
        depth: int = 0,
        columns: list[str] | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.task_data = task
        self.depth = depth
        self.toggled = task.is_done
        self._columns = columns or ["checkbox", "title", "tags", "priority"]

    def compose(self) -> ComposeResult:
        return
        yield  # make it a generator  # noqa: F401

    # --- Column renderers (formatter pipeline) ---

    def _render_checkbox(self, line: Text) -> None:
        theme = get_theme()
        checkbox = "[x]" if self.toggled else "[ ]"
        line.append(checkbox, style=theme.accent)
        line.append("\u2502", style=theme.border)  # │ separator

    def _render_title(self, line: Text) -> None:
        line.append(self.task_data.title, style=self._title_style())

    def _render_tags(self, line: Text) -> None:
        if self.task_data.tags:
            tags_str = ",".join(self.task_data.tags)
            line.append(f"  {tags_str}", style=get_theme().text_muted)

    def _render_priority(self, line: Text) -> None:
        stars = PRIORITY_STARS[self.task_data.priority]
        star_style = _priority_star_style(self.task_data.priority)
        line.append(f" {stars}", style=star_style)

    def _render_due(self, line: Text) -> None:
        if self.task_data.due_date:
            theme = get_theme()
            due_st = _due_status(self.task_data.due_date)
            if due_st == "overdue":
                style = theme.error
            elif due_st == "today":
                style = theme.priority_normal
            else:
                style = theme.text_muted
            line.append(f"  \u23f0{self.task_data.due_date}", style=style)

    def _render_effort(self, line: Text) -> None:
        effort = self.task_data.model_extra.get("effort") if self.task_data.model_extra else None
        if effort:
            line.append(f"  [{effort}]", style=get_theme().accent)

    def _render_progress(self, line: Text) -> None:
        done, total = self.task_data.children_progress()
        if total > 0:
            line.append(f"  ({done}/{total})", style=get_theme().text_muted)

    # Minimum characters to show for the title before truncating suffix
    _MIN_TITLE_WIDTH = 6

    def _title_style(self) -> str:
        """Return the Rich style string for the title."""
        theme = get_theme()
        due_st = _due_status(self.task_data.due_date)
        if self.toggled:
            return f"strike {theme.text_muted}"
        if due_st == "overdue":
            return theme.error
        if due_st == "today":
            return theme.priority_normal
        return theme.text

    def render(self) -> Text:
        if self.editing:
            return Text("")

        avail = self.size.width

        # 1. Build indent
        indent_text = Text()
        if self.depth > 0:
            indent = "  " * (self.depth - 1) + INDENT_GLYPH
            indent_text.append(indent, style=get_theme().text_muted)

        # 2. Build checkbox
        checkbox_text = Text()
        self._render_checkbox(checkbox_text)

        # 3. Build suffix (everything AFTER title: tags, priority, progress, due badge)
        suffix = Text()
        for col in self._columns:
            if col in ("checkbox", "title"):
                continue
            renderer_name = COLUMN_RENDERERS.get(col)
            if renderer_name:
                renderer = getattr(self, renderer_name, None)
                if renderer:
                    renderer(suffix)

        if "progress" not in self._columns:
            self._render_progress(suffix)

        if "due" not in self._columns and self.task_data.due_date:
            due_st = _due_status(self.task_data.due_date)
            theme = get_theme()
            if due_st == "overdue":
                suffix.append("  \u26a0overdue", style=theme.error)
            elif due_st == "today":
                suffix.append("  \u2691today", style=theme.priority_normal)

        # 4. Calculate title budget (1 space between separator and title)
        fixed = len(indent_text) + len(checkbox_text) + 1 + len(suffix)
        title_budget = avail - fixed

        # 5. Build title (truncated to budget)
        title_str = self.task_data.title
        style = self._title_style()

        title_text = Text()
        if title_budget >= self._MIN_TITLE_WIDTH:
            # Normal: title gets remaining space
            if len(title_str) > title_budget:
                title_text.append(title_str[: title_budget - 1], style=style)
                title_text.append("\u2026", style=get_theme().text_muted)
            else:
                title_text.append(title_str, style=style)
        elif title_budget > 1:
            # Very tight: show what we can
            title_text.append(title_str[: title_budget - 1], style=style)
            title_text.append("\u2026", style=get_theme().text_muted)
        else:
            # No room at all — just truncate everything from the right
            line = Text()
            line.append(indent_text)
            line.append(checkbox_text)
            line.append(" ")
            line.append(title_str, style=style)
            line.append(suffix)
            line.truncate(max(avail, 0))
            return line

        # 6. Assemble
        line = Text()
        line.append(indent_text)
        line.append(checkbox_text)
        line.append(" ")
        line.append(title_text)
        line.append(suffix)
        return line

    def set_dimmed(self, dim: bool) -> None:
        """Set dim state for search-as-filter."""
        self.dimmed = dim
        self.set_class(dim, "dimmed")
        self.refresh()

    def on_click(self, event: Click) -> None:
        """Click checkbox area -> toggle done; click title area -> open detail."""
        if self.editing:
            return
        self.focus()
        checkbox_end = _CHECKBOX_COLS + self.depth * 2
        if event.x <= checkbox_end:
            from mutsumi.app import MutsumiApp

            app = self.app
            if isinstance(app, MutsumiApp):
                app.run_worker(app.action_toggle_done())
        else:
            self.post_message(self.DetailClicked(self.task_data))

    def toggle_done(self) -> None:
        """Toggle the done status visually."""
        self.toggled = not self.toggled
        self.set_class(self.toggled, "done")
        self.refresh()

    # --- Inline editing ---

    def start_editing(self) -> None:
        """Enter inline edit mode: mount an Input overlay."""
        if self.editing:
            return
        self.editing = True
        input_widget = Input(
            value=self.task_data.title,
            classes="inline-edit",
            id="inline-edit-input",
        )
        self.mount(input_widget)
        input_widget.focus()

    def _stop_editing(self, save: bool = False) -> None:
        """Exit inline edit mode."""
        if not self.editing:
            return
        try:
            input_widget = self.query_one("#inline-edit-input", Input)
            if save:
                new_title = input_widget.value.strip()
                if new_title and new_title != self.task_data.title:
                    self.post_message(
                        self.TitleEdited(self.task_data.id, new_title)
                    )
            input_widget.remove()
        except Exception:
            pass
        self.editing = False
        self.focus()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Enter pressed in inline edit -> save."""
        if self.editing:
            event.stop()
            self._stop_editing(save=True)

    def on_key(self, event: object) -> None:
        """Escape in inline edit -> cancel."""
        from textual.events import Key

        if isinstance(event, Key) and event.key == "escape" and self.editing:
            event.stop()
            event.prevent_default()
            self._stop_editing(save=False)
