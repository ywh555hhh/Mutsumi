"""Header bar widget with dynamic source tabs.

In single-source mode (no projects registered), shows scope tabs
like before for backward compat. In multi-source mode, shows source
tabs with the Main tab first.
"""

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

# Legacy scope tab support (single-source mode)
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
        color: #999999;
    }

    TabButton:hover {
        color: #cccccc;
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

    def __init__(
        self,
        scope: TaskScope | None = None,
        *,
        source_name: str = "",
        display_name: str = "",
        **kwargs: Any,
    ) -> None:
        self.scope = scope
        self.source_name = source_name
        self.display_name = display_name or source_name
        if scope is not None:
            super().__init__(self._scope_label(scope, active=False), **kwargs)
        else:
            super().__init__(self._source_label(self.display_name, active=False), **kwargs)

    @staticmethod
    def _scope_label(scope: TaskScope, active: bool = False) -> str:
        name = TAB_LABELS.get(scope, "")
        return f"\\[{name}]" if active else f" {name} "

    @staticmethod
    def _source_label(name: str, active: bool = False) -> str:
        return f"\\[{name}]" if active else f" {name} "

    def set_active(self, active: bool) -> None:
        if self.scope is not None:
            self.update(self._scope_label(self.scope, active))
        else:
            self.update(self._source_label(self.display_name, active))
        self.set_class(active, "active")

    def on_click(self) -> None:
        parent = self.parent
        while parent is not None:
            if isinstance(parent, HeaderBar):
                if self.scope is not None:
                    parent.active_scope = self.scope
                elif self.source_name:
                    parent.active_source = self.source_name
                break
            parent = parent.parent


class HeaderBar(Widget):
    """Top bar with scope tabs (single-source) or source tabs (multi-source)."""

    DEFAULT_CSS = """
    HeaderBar {
        dock: top;
        height: 1;
        background: #0e0e0e;
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
        """Posted when the active scope tab changes (single-source mode)."""

        def __init__(self, scope: TaskScope) -> None:
            self.scope = scope
            super().__init__()

    class SourceTabChanged(Message):
        """Posted when the active source tab changes (multi-source mode)."""

        def __init__(self, source_name: str) -> None:
            self.source_name = source_name
            super().__init__()

    active_scope: reactive[TaskScope] = reactive(TaskScope.DAY)
    active_source: reactive[str] = reactive("")

    def __init__(self, *, source_names: list[str] | None = None, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._source_names = source_names or []
        self._multi_source = len(self._source_names) > 1

    @property
    def is_multi_source(self) -> bool:
        return self._multi_source

    def set_sources(self, source_names: list[str]) -> None:
        """Update the source tab list dynamically."""
        self._source_names = source_names
        self._multi_source = len(source_names) > 1
        # Re-compose would be ideal but for now this is called before mount

    def compose(self) -> ComposeResult:
        with Horizontal():
            if self._multi_source:
                # Multi-source: show source tabs
                for name in self._source_names:
                    is_active = name == self.active_source
                    display_name = "\u2605 Main" if name == "main" else name
                    btn = TabButton(
                        source_name=name,
                        display_name=display_name,
                        classes="active" if is_active else "",
                    )
                    yield btn
            else:
                # Single-source: show scope tabs (backward compat)
                for scope in TAB_ORDER:
                    is_active = scope == self.active_scope
                    btn = TabButton(scope, classes="active" if is_active else "")
                    btn.update(TabButton._scope_label(scope, is_active))
                    yield btn
            yield Static("mutsumi", classes="title")

    def watch_active_scope(self, new_scope: TaskScope) -> None:
        """Update tab styling when scope changes (single-source mode)."""
        if self._multi_source:
            return
        for btn in self.query(TabButton):
            if btn.scope is not None:
                btn.set_active(btn.scope == new_scope)
        self.post_message(self.TabChanged(new_scope))

    def watch_active_source(self, new_source: str) -> None:
        """Update tab styling when source changes (multi-source mode)."""
        if not self._multi_source or not new_source:
            return
        for btn in self.query(TabButton):
            if btn.source_name:
                btn.set_active(btn.source_name == new_source)
        self.post_message(self.SourceTabChanged(new_source))

    def next_tab(self) -> None:
        if self._multi_source:
            names = self._source_names
            if not names:
                return
            idx = names.index(self.active_source) if self.active_source in names else 0
            self.active_source = names[(idx + 1) % len(names)]
        else:
            idx = TAB_ORDER.index(self.active_scope)
            self.active_scope = TAB_ORDER[(idx + 1) % len(TAB_ORDER)]

    def prev_tab(self) -> None:
        if self._multi_source:
            names = self._source_names
            if not names:
                return
            idx = names.index(self.active_source) if self.active_source in names else 0
            self.active_source = names[(idx - 1) % len(names)]
        else:
            idx = TAB_ORDER.index(self.active_scope)
            self.active_scope = TAB_ORDER[(idx - 1) % len(TAB_ORDER)]

    def set_tab(self, index: int) -> None:
        if self._multi_source:
            if 0 <= index < len(self._source_names):
                self.active_source = self._source_names[index]
        else:
            if 0 <= index < len(TAB_ORDER):
                self.active_scope = TAB_ORDER[index]

    def on_resize(self, event: Resize) -> None:
        """Hide title at narrow widths to give tabs more room."""
        try:
            title = self.query_one(".title", Static)
        except Exception:
            return
        title.display = event.size.width >= 60
