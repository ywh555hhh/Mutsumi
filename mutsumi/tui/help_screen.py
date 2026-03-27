"""Help screen — auto-generated from Binding + KeySequence lists."""

from __future__ import annotations

from typing import TYPE_CHECKING

from rich.text import Text
from textual.screen import ModalScreen
from textual.widgets import Static

from mutsumi.config.keybindings import get_keybindings
from mutsumi.core.interaction import SemanticAction
from mutsumi.themes import get_theme
from mutsumi.tui.key_manager import get_key_sequences

if TYPE_CHECKING:
    from textual.app import ComposeResult

# Map actions to user-friendly category names
_ACTION_CATEGORIES: dict[str, str] = {
    # Navigation
    "cursor_down": "Navigation",
    "cursor_up": "Navigation",
    "cursor_top": "Navigation",
    "cursor_bottom": "Navigation",
    # Tabs
    "next_tab": "Tabs",
    "prev_tab": "Tabs",
    "tab_1": "Tabs",
    "tab_2": "Tabs",
    "tab_3": "Tabs",
    "tab_4": "Tabs",
    # View
    SemanticAction.CONFIRM.value: "View",
    SemanticAction.BACK.value: "View",
    "collapse_group": "View",
    "expand_group": "View",
    "toggle_fold": "View",
    "search": "View",
    "sort": "View",
    # Actions
    "toggle_done": "Actions",
    SemanticAction.CREATE.value: "Actions",
    SemanticAction.EDIT.value: "Actions",
    "inline_edit": "Actions",
    "delete_start": "Actions",
    "delete_confirm": "Actions",
    "add_child": "Actions",
    # Priority & Order
    "priority_up": "Priority & Order",
    "priority_down": "Priority & Order",
    "move_up": "Priority & Order",
    "move_down": "Priority & Order",
    "copy_task": "Priority & Order",
    "paste_task": "Priority & Order",
    "paste_task_above": "Priority & Order",
    # App
    "quit": "App",
    "show_help": "App",
}

_CATEGORY_ORDER = [
    "Navigation",
    "Tabs",
    "View",
    "Actions",
    "Priority & Order",
    "App",
]


class HelpScreen(ModalScreen[None]):
    """Full-screen help overlay showing all keybindings."""

    DEFAULT_CSS = """
    HelpScreen {
        align: center middle;
    }

    HelpScreen > Static {
        width: 60;
        max-width: 90%;
        max-height: 80%;
        background: $theme-surface;
        border: tall $theme-border;
        padding: 1 2;
        overflow-y: auto;
    }
    """

    BINDINGS = [
        ("escape", "dismiss", "Close"),
        ("q", "dismiss", "Close"),
        ("question_mark", "dismiss", "Close"),
    ]

    def __init__(self, preset: str = "arrows") -> None:
        super().__init__()
        self._preset = preset

    def compose(self) -> ComposeResult:
        yield Static(self._build_table(), id="help-content")

    def _build_table(self) -> Text:
        """Build a Rich renderable with all keybindings grouped by category."""
        bindings = get_keybindings(self._preset)
        sequences = get_key_sequences(self._preset)

        # Collect (key_display, action, description) entries
        entries: list[tuple[str, str, str]] = []

        # From Textual Bindings
        seen_actions: set[str] = set()
        for b in bindings:
            action = b.action.replace("app.", "")
            if action in seen_actions:
                continue
            seen_actions.add(action)
            key_display = b.key_display or b.key
            entries.append((key_display, action, b.description))

        # From KeySequences
        for seq in sequences:
            if seq.action in seen_actions:
                continue
            seen_actions.add(seq.action)
            key_display = "".join(seq.keys)
            entries.append((key_display, seq.action, seq.description))

        # Group by category
        categorized: dict[str, list[tuple[str, str]]] = {c: [] for c in _CATEGORY_ORDER}
        for key_display, action, description in entries:
            category = _ACTION_CATEGORIES.get(action, "App")
            if category not in categorized:
                categorized[category] = []
            label = description or action.replace("_", " ").title()
            categorized[category].append((key_display, label))

        # Build output
        result = Text()
        theme = get_theme()
        result.append(f"  Mutsumi Help  ({self._preset} preset)\n", style=f"bold {theme.accent}")
        result.append("  Press Escape or ? to close\n\n", style=theme.text_muted)

        for category in _CATEGORY_ORDER:
            items = categorized.get(category, [])
            if not items:
                continue

            result.append(f"  {category}\n", style=f"bold underline {theme.text}")
            for key_display, label in items:
                result.append(f"    {key_display:>14}  ", style=theme.accent)
                result.append(f"{label}\n", style=theme.text)
            result.append("\n")

        return result
