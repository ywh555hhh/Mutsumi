"""Header bar widget with scope tabs."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from textual.containers import Horizontal
from textual.message import Message
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Static

from mutsumi.core.models import TaskScope

if TYPE_CHECKING:
    from textual.app import ComposeResult
    from textual.events import Resize

TAB_LABELS: dict[TaskScope, str] = {
    TaskScope.DAY: "Today",
    TaskScope.WEEK: "Week",
    TaskScope.MONTH: "Month",
    TaskScope.INBOX: "Inbox",
}

TAB_ORDER: list[TaskScope] = [
    TaskScope.DAY,
    TaskScope.WEEK,
    TaskScope.MONTH,
    TaskScope.INBOX,
]


class TabButton(Static, can_focus=True):
    """A single clickable & focusable tab button."""

    DEFAULT_CSS = """
    TabButton {
        width: auto;
        height: 1;
        padding: 0 1;
        color: #666666;
    }

    TabButton:hover {
        color: #999999;
        background: #222222;
    }

    TabButton:focus {
        text-style: reverse;
    }

    TabButton.active {
        color: #5de4c7;
        text-style: bold;
        background: #1f2f2a;
    }

    TabButton.active:hover {
        color: #5de4c7;
        background: #253530;
    }

    TabButton.active:focus {
        color: #5de4c7;
        text-style: bold reverse;
    }
    """

    def __init__(self, scope: TaskScope, **kwargs: Any) -> None:
        self.scope = scope
        super().__init__(self._label_for(active=False), **kwargs)

    @staticmethod
    def _label_for(scope: TaskScope | None = None, active: bool = False) -> str:
        """Return bracketed label when active, plain when inactive."""
        name = TAB_LABELS[scope] if scope else ""
        return f"[{name}]" if active else f" {name} "

    def set_active(self, active: bool) -> None:
        """Update label text to reflect active/inactive state."""
        self.update(self._label_for(self.scope, active))
        self.set_class(active, "active")

    def on_click(self) -> None:
        parent = self.parent
        while parent is not None:
            if isinstance(parent, HeaderBar):
                parent.active_scope = self.scope
                break
            parent = parent.parent


class HeaderBar(Widget):
    """Top bar with scope tabs and app title."""

    DEFAULT_CSS = """
    HeaderBar {
        dock: top;
        height: 1;
        background: #1a1a1a;
    }

    HeaderBar > Horizontal {
        height: 1;
        width: 100%;
    }

    HeaderBar .title {
        width: 1fr;
        text-align: right;
        padding: 0 1;
        color: #666666;
    }
    """

    class TabChanged(Message):
        """Posted when the active tab changes."""

        def __init__(self, scope: TaskScope) -> None:
            self.scope = scope
            super().__init__()

    active_scope: reactive[TaskScope] = reactive(TaskScope.DAY)

    def compose(self) -> ComposeResult:
        with Horizontal():
            for scope in TAB_ORDER:
                is_active = scope == self.active_scope
                btn = TabButton(scope, classes="active" if is_active else "")
                btn.update(TabButton._label_for(scope, is_active))
                yield btn
            yield Static("mutsumi", classes="title")

    def watch_active_scope(self, new_scope: TaskScope) -> None:
        """Update tab styling and post message when active scope changes."""
        for btn in self.query(TabButton):
            btn.set_active(btn.scope == new_scope)
        self.post_message(self.TabChanged(new_scope))

    def next_tab(self) -> None:
        idx = TAB_ORDER.index(self.active_scope)
        self.active_scope = TAB_ORDER[(idx + 1) % len(TAB_ORDER)]

    def prev_tab(self) -> None:
        idx = TAB_ORDER.index(self.active_scope)
        self.active_scope = TAB_ORDER[(idx - 1) % len(TAB_ORDER)]

    def set_tab(self, index: int) -> None:
        if 0 <= index < len(TAB_ORDER):
            self.active_scope = TAB_ORDER[index]

    def on_resize(self, event: Resize) -> None:
        """Hide title at narrow widths to give tabs more room."""
        try:
            title = self.query_one(".title", Static)
        except Exception:
            return
        title.display = event.size.width >= 60
