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


class TabButton(Static):
    """A single clickable tab button."""

    DEFAULT_CSS = """
    TabButton {
        width: auto;
        height: 1;
        padding: 0 1;
        color: #666666;
    }

    TabButton.active {
        color: #5de4c7;
        text-style: bold;
    }
    """

    def __init__(self, scope: TaskScope, **kwargs: Any) -> None:
        self.scope = scope
        label = f"[{TAB_LABELS[scope]}]"
        super().__init__(label, **kwargs)

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
                yield TabButton(scope, classes="active" if scope == self.active_scope else "")
            yield Static("mutsumi", classes="title")

    def watch_active_scope(self, new_scope: TaskScope) -> None:
        """Update tab styling and post message when active scope changes."""
        for btn in self.query(TabButton):
            btn.set_class(btn.scope == new_scope, "active")
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
