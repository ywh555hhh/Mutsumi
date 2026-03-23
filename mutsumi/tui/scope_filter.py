"""Scope filter sub-bar widget.

Shows [Today] [Week] [Month] [Inbox] [All] as a second-level filter
below the source tabs. Hidden when the Main dashboard tab is active.

In multi-source mode, a [★ Main] button appears at the left edge so
the user always has a visible click target to return to the dashboard.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from textual.containers import Horizontal
from textual.message import Message
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Static

from mutsumi.i18n import get_i18n

if TYPE_CHECKING:
    from textual.app import ComposeResult


def _scope_labels() -> dict[str, str]:
    """Build scope labels from i18n (called at render time)."""
    t = get_i18n().t
    return {
        "day": t("tabs.today"),
        "week": t("tabs.week"),
        "month": t("tabs.month"),
        "inbox": t("tabs.inbox"),
        "all": t("tabs.all"),
    }

SCOPE_ORDER: list[str] = ["day", "week", "month", "inbox", "all"]


class _ScopeButton(Static, can_focus=True):
    """A single clickable scope filter button."""

    DEFAULT_CSS = """
    _ScopeButton {
        width: auto;
        height: 1;
        padding: 0 1;
        color: $theme-text-muted;
    }

    _ScopeButton:hover {
        color: $theme-text;
        background: $theme-bg;
    }

    _ScopeButton:focus {
        text-style: reverse;
    }

    _ScopeButton.active {
        color: $theme-accent;
        text-style: bold;
    }

    _ScopeButton.active:focus {
        color: $theme-accent;
        text-style: bold reverse;
    }
    """

    def __init__(self, scope_key: str, **kwargs: Any) -> None:
        self.scope_key = scope_key
        label = _scope_labels().get(scope_key, scope_key)
        super().__init__(f" {label} ", **kwargs)

    def set_active(self, active: bool) -> None:
        label = _scope_labels().get(self.scope_key, self.scope_key)
        if active:
            self.update(f"\\[{label}]")
        else:
            self.update(f" {label} ")
        self.set_class(active, "active")

    def on_click(self) -> None:
        parent = self.parent
        while parent is not None:
            if isinstance(parent, ScopeFilter):
                parent.active_scope = self.scope_key
                break
            parent = parent.parent


class _MainButton(Static, can_focus=True):
    """Clickable button to return to the Main dashboard."""

    DEFAULT_CSS = """
    _MainButton {
        width: auto;
        height: 1;
        padding: 0 1;
        color: $theme-accent;
    }

    _MainButton:hover {
        background: $theme-bg;
        color: $theme-text;
    }

    _MainButton:focus {
        text-style: reverse;
    }
    """

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(f"\u2605 {get_i18n().t('tabs.main')}", **kwargs)

    def on_click(self) -> None:
        parent = self.parent
        while parent is not None:
            if isinstance(parent, ScopeFilter):
                parent.post_message(ScopeFilter.MainRequested())
                break
            parent = parent.parent


class ScopeFilter(Widget):
    """Sub-filter bar for scope selection within a source tab."""

    DEFAULT_CSS = """
    ScopeFilter {
        dock: top;
        height: 1;
        background: $theme-surface;
    }

    ScopeFilter > Horizontal {
        height: 1;
        width: 100%;
    }

    ScopeFilter .scope-sep {
        width: auto;
        height: 1;
        color: $theme-border;
    }
    """

    class ScopeChanged(Message):
        """Posted when the active scope changes."""

        def __init__(self, scope: str) -> None:
            self.scope = scope
            super().__init__()

    class MainRequested(Message):
        """Posted when the user clicks the Main button to return to dashboard."""

    active_scope: reactive[str] = reactive("day")

    def __init__(self, *, show_main_button: bool = False, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._show_main_button = show_main_button

    def set_show_main_button(self, show: bool) -> None:
        """Show or hide the Main return button."""
        self._show_main_button = show
        try:
            btn = self.query_one("#scope-main-btn", _MainButton)
            sep = self.query_one("#scope-sep", Static)
            btn.display = show
            sep.display = show
        except Exception:
            pass

    def compose(self) -> ComposeResult:
        with Horizontal():
            btn = _MainButton(id="scope-main-btn")
            btn.display = self._show_main_button
            yield btn
            sep = Static("\u2502", classes="scope-sep", id="scope-sep")
            sep.display = self._show_main_button
            yield sep
            for key in SCOPE_ORDER:
                is_active = key == self.active_scope
                scope_btn = _ScopeButton(key, classes="active" if is_active else "")
                if is_active:
                    scope_btn.set_active(True)
                yield scope_btn

    def watch_active_scope(self, new_scope: str) -> None:
        for btn in self.query(_ScopeButton):
            btn.set_active(btn.scope_key == new_scope)
        self.post_message(self.ScopeChanged(new_scope))

    def next_scope(self) -> None:
        idx = SCOPE_ORDER.index(self.active_scope) if self.active_scope in SCOPE_ORDER else 0
        self.active_scope = SCOPE_ORDER[(idx + 1) % len(SCOPE_ORDER)]

    def set_scope(self, key: str) -> None:
        if key in SCOPE_ORDER:
            self.active_scope = key
