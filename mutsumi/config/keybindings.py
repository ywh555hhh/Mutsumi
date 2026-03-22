"""Keybinding presets for Mutsumi.

Three built-in presets: vim, emacs, arrows.
Each returns a list of Textual Binding objects.

Design principles:
  - Mouse behaviour is identical across all presets.
  - Common functional keys (space, enter, escape, tab, 1-4, n, e, /)
    are shared because they don't conflict with any preset's conventions.
  - Navigation keys differ per habit: j/k, ctrl+n/p, or arrow keys.
  - Quit key adapts: vim=q, emacs=ctrl+q, arrows=q.
  - Multi-key sequences (dd, gg) are handled by KeyManager, not here.
"""

from __future__ import annotations

from textual.binding import Binding

# ── Shared bindings ──────────────────────────────────────────────────
# These don't conflict with any navigation style.
# NOTE: 'd' and 'g' removed — handled by KeyManager multi-key sequences.
_COMMON_BINDINGS: list[Binding] = [
    Binding("space", "toggle_done", "Toggle", show=False),
    Binding("enter", "show_detail", "Detail", show=False),
    Binding("escape", "close_detail", "Close", show=False),
    Binding("tab", "next_tab", "Next Tab", show=False),
    Binding("shift+tab", "prev_tab", "Prev Tab", show=False),
    Binding("1", "tab_1", "Today", show=False),
    Binding("2", "tab_2", "Week", show=False),
    Binding("3", "tab_3", "Month", show=False),
    Binding("4", "tab_4", "Inbox", show=False),
    Binding("5", "tab_5", "Tab 5", show=False),
    Binding("6", "tab_6", "Tab 6", show=False),
    Binding("7", "tab_7", "Tab 7", show=False),
    Binding("8", "tab_8", "Tab 8", show=False),
    Binding("9", "tab_9", "Tab 9", show=False),
    Binding("n", "new_task", "New", show=False),
    Binding("e", "edit_task", "Edit", show=False),
    Binding("slash", "search", "Search", show=False),
    # ── New shared bindings ──
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
    Binding("A", "add_child", "Add Child", show=False, key_display="shift+a"),
    Binding("P", "paste_task_above", "Paste Above", show=False, key_display="shift+p"),
    Binding("f", "cycle_scope", "Cycle Scope", show=False),
]

# ── Vim preset ───────────────────────────────────────────────────────
# Navigation: j/k, fold: h/l (tree-style)
# NOTE: 'g' removed from here — gg is a KeyManager sequence
VIM_BINDINGS: list[Binding] = [
    *_COMMON_BINDINGS,
    Binding("q", "quit", "Quit"),
    Binding("j", "cursor_down", "Down", show=False),
    Binding("k", "cursor_up", "Up", show=False),
    Binding("G", "cursor_bottom", "Bottom", show=False, key_display="shift+g"),
    Binding("h", "collapse_group", "Collapse", show=False),
    Binding("l", "expand_group", "Expand", show=False),
    # Vim-specific: J/K for move up/down
    Binding("J", "move_down", "Move Down", show=False, key_display="shift+j"),
    Binding("K", "move_up", "Move Up", show=False, key_display="shift+k"),
]

# ── Emacs preset ─────────────────────────────────────────────────────
# Navigation: ctrl+n/p, quit: ctrl+q (free q for typing)
EMACS_BINDINGS: list[Binding] = [
    *_COMMON_BINDINGS,
    Binding("ctrl+q", "quit", "Quit"),
    Binding("ctrl+n", "cursor_down", "Down", show=False),
    Binding("ctrl+p", "cursor_up", "Up", show=False),
    Binding("ctrl+a", "cursor_top", "Top", show=False),
    Binding("ctrl+e", "cursor_bottom", "Bottom", show=False),
    Binding("ctrl+b", "collapse_group", "Collapse", show=False),
    Binding("ctrl+f", "expand_group", "Expand", show=False),
    # Emacs-specific: ctrl+shift+n/p for move
    Binding("ctrl+shift+n", "move_down", "Move Down", show=False),
    Binding("ctrl+shift+p", "move_up", "Move Up", show=False),
]

# ── Arrows preset ────────────────────────────────────────────────────
# Standard arrow key navigation, home/end, left/right for fold
ARROW_BINDINGS: list[Binding] = [
    *_COMMON_BINDINGS,
    Binding("q", "quit", "Quit"),
    Binding("down", "cursor_down", "Down", show=False),
    Binding("up", "cursor_up", "Up", show=False),
    Binding("home", "cursor_top", "Top", show=False),
    Binding("end", "cursor_bottom", "Bottom", show=False),
    Binding("left", "collapse_group", "Collapse", show=False),
    Binding("right", "expand_group", "Expand", show=False),
    # Arrows-specific: shift+arrows for move
    Binding("shift+down", "move_down", "Move Down", show=False),
    Binding("shift+up", "move_up", "Move Up", show=False),
]

PRESET_MAP: dict[str, list[Binding]] = {
    "vim": VIM_BINDINGS,
    "emacs": EMACS_BINDINGS,
    "arrows": ARROW_BINDINGS,
}


def get_keybindings(
    preset: str,
    overrides: dict[str, str] | None = None,
) -> list[Binding]:
    """Get keybindings for a preset name with optional user overrides.

    *overrides* maps action names to new key strings.
    Example: ``{"quit": "ctrl+q", "cursor_down": "ctrl+j"}``
    Falls back to vim if preset is unknown.
    """
    bindings = list(PRESET_MAP.get(preset, ARROW_BINDINGS))
    if not overrides:
        return bindings

    # Apply overrides: replace the key for matching actions
    result: list[Binding] = []
    for b in bindings:
        action = b.action.replace("app.", "")
        if action in overrides:
            new_key = overrides[action]
            result.append(
                Binding(new_key, b.action, b.description, show=b.show, key_display=new_key)
            )
        else:
            result.append(b)
    return result
