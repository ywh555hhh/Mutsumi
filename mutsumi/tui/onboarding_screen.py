"""First-run onboarding modal for Mutsumi — single-page layout."""

from __future__ import annotations

from typing import TYPE_CHECKING

from textual.binding import Binding
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.message import Message
from textual.screen import ModalScreen
from textual.widgets import Button, RadioButton, RadioSet, Static

from mutsumi.core.interaction import SemanticAction

if TYPE_CHECKING:
    from textual.app import ComposeResult

    from mutsumi.config.settings import MutsumiConfig

# ── Setting definitions ─────────────────────────────────────────────

_SETTINGS: list[tuple[str, str, list[tuple[str, str]]]] = [
    # (key, label, [(value, display_label), ...])
    ("language", "Language", [
        ("en", "English"),
        ("zh", "中文"),
        ("ja", "日本語"),
    ]),
    ("keybindings", "Keybindings", [
        ("arrows", "Arrows"),
        ("vim", "Vim"),
        ("emacs", "Emacs"),
    ]),
    ("theme", "Theme", [
        ("monochrome-zen", "Monochrome Zen"),
        ("nord", "Nord"),
        ("dracula", "Dracula"),
        ("solarized", "Solarized"),
    ]),
    ("workspace_mode", "Workspace", [
        ("personal-only", "Personal only"),
        ("project-only", "Project only"),
        ("personal+project", "Personal + Project"),
    ]),
    ("preferred_agent", "Agent", [
        ("claude-code", "Claude Code"),
        ("codex-cli", "Codex CLI"),
        ("gemini-cli", "Gemini CLI"),
        ("opencode", "OpenCode"),
        ("none", "Skip"),
    ]),
]


class OnboardingScreen(ModalScreen[None]):
    """Single-page first-run onboarding — pick everything, confirm once."""

    DEFAULT_CSS = """
    OnboardingScreen {
        align: center middle;
    }

    OnboardingScreen > Vertical {
        width: 72;
        max-width: 92%;
        max-height: 90%;
        background: $theme-surface;
        border: solid $theme-border;
        padding: 1 2;
    }

    OnboardingScreen .ob-title {
        color: $theme-accent;
        text-style: bold;
        text-align: center;
        margin-bottom: 0;
    }

    OnboardingScreen .ob-subtitle {
        color: $theme-text-muted;
        text-align: center;
        margin-bottom: 1;
    }

    OnboardingScreen .setting-row {
        height: auto;
        margin: 0 0 1 0;
    }

    OnboardingScreen .setting-row.-active {
        background: $theme-bg;
    }

    OnboardingScreen .setting-label {
        width: 14;
        color: $theme-text;
        text-style: bold;
        padding: 0 1 0 0;
    }

    OnboardingScreen RadioSet {
        layout: horizontal;
        height: auto;
        background: transparent;
        border: none;
        padding: 0;
    }

    OnboardingScreen RadioButton {
        background: transparent;
        padding: 0 1 0 0;
        height: 1;
        border: none;
    }

    OnboardingScreen .nav-row {
        height: 3;
        align: center middle;
        margin-top: 1;
    }

    OnboardingScreen .nav-row.-active {
        background: $theme-bg;
    }

    OnboardingScreen Button {
        margin: 0 1;
    }
    """

    BINDINGS = [
        Binding("escape", SemanticAction.CANCEL.value, "Skip", priority=True),
        Binding("up", SemanticAction.MOVE_UP.value, "Prev", show=False, priority=True),
        Binding("down", SemanticAction.MOVE_DOWN.value, "Next", show=False, priority=True),
        Binding("left", SemanticAction.MOVE_LEFT.value, "Prev", show=False, priority=True),
        Binding("right", SemanticAction.MOVE_RIGHT.value, "Next", show=False, priority=True),
        Binding("enter", SemanticAction.CONFIRM.value, "Confirm", show=False, priority=True),
    ]

    class Finished(Message):
        """Posted when onboarding finishes or is skipped."""

        def __init__(self, selections: dict[str, str], skipped: bool) -> None:
            self.selections = selections
            self.skipped = skipped
            super().__init__()

    def __init__(self, config: MutsumiConfig, is_git_repo: bool) -> None:
        super().__init__()
        self._is_git_repo = is_git_repo
        self._selections: dict[str, str] = {
            "language": config.language,
            "keybindings": config.keybindings,
            "theme": config.theme,
            "workspace_mode": "personal+project" if is_git_repo else "personal-only",
            "preferred_agent": "none",
        }
        self._active_row = 0
        self._active_cta = 0

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Static("Welcome to Mutsumi", classes="ob-title")
            yield Static(
                "Your silent task board is ready to set up.",
                classes="ob-subtitle",
            )
            with VerticalScroll():
                for key, label, options in _SETTINGS:
                    safe_key = key.replace("_", "-")
                    default = self._selections[key]
                    with Horizontal(classes="setting-row", id=f"row-{safe_key}"):
                        yield Static(label, classes="setting-label")
                        with RadioSet(id=f"rs-{safe_key}"):
                            for idx, (value, display) in enumerate(options):
                                yield RadioButton(
                                    display,
                                    value=(value == default),
                                    id=f"rb-{safe_key}-{idx}",
                                )
            with Horizontal(classes="nav-row", id="onboarding-nav-row"):
                yield Button(
                    "Start Mutsumi",
                    variant="primary",
                    id="onboarding-start",
                )
                yield Button("Skip", id="onboarding-skip")

    def on_mount(self) -> None:
        self._refresh_active_focus()

    def _row_count(self) -> int:
        return len(_SETTINGS) + 1

    def _row_key(self, row_index: int) -> str | None:
        if row_index < len(_SETTINGS):
            return _SETTINGS[row_index][0]
        return None

    def _current_radio_set(self) -> RadioSet | None:
        row_key = self._row_key(self._active_row)
        if row_key is None:
            return None
        safe_key = row_key.replace("_", "-")
        return self.query_one(f"#rs-{safe_key}", RadioSet)

    def _current_options(self) -> list[tuple[str, str]]:
        row_key = self._row_key(self._active_row)
        if row_key is None:
            return []
        for key, _label, options in _SETTINGS:
            if key == row_key:
                return options
        return []

    def _current_option_index(self) -> int:
        row_key = self._row_key(self._active_row)
        if row_key is None:
            return 0
        selected = self._selections[row_key]
        for idx, (value, _display) in enumerate(self._current_options()):
            if value == selected:
                return idx
        return 0

    def _set_current_option(self, index: int) -> None:
        row_key = self._row_key(self._active_row)
        if row_key is None:
            return
        options = self._current_options()
        if not options:
            return
        next_index = index % len(options)
        self._selections[row_key] = options[next_index][0]
        safe_key = row_key.replace("_", "-")
        radio_set = self.query_one(f"#rs-{safe_key}", RadioSet)
        for idx, button in enumerate(radio_set.query(RadioButton)):
            button.value = idx == next_index
        self._refresh_active_focus()

    def _refresh_active_focus(self) -> None:
        for idx, (key, _label, _options) in enumerate(_SETTINGS):
            row = self.query_one(f"#row-{key.replace('_', '-')}", Horizontal)
            row.set_class(idx == self._active_row, "-active")
        nav_row = self.query_one("#onboarding-nav-row", Horizontal)
        nav_row.set_class(self._active_row == len(_SETTINGS), "-active")

        if self._active_row < len(_SETTINGS):
            radio_set = self._current_radio_set()
            if radio_set is not None:
                buttons = list(radio_set.query(RadioButton))
                option_index = self._current_option_index()
                if 0 <= option_index < len(buttons):
                    buttons[option_index].focus()
                else:
                    radio_set.focus()
            return

        nav_row = self.query_one("#onboarding-nav-row", Horizontal)
        buttons = list(nav_row.query(Button))
        if buttons:
            buttons[self._active_cta % len(buttons)].focus()

    def on_radio_set_changed(self, event: RadioSet.Changed) -> None:
        rs_id = (event.radio_set.id or "").removeprefix("rs-")
        for index, (key, _label, options) in enumerate(_SETTINGS):
            if key.replace("_", "-") != rs_id:
                continue
            self._active_row = index
            pressed_index = event.radio_set.pressed_index
            if 0 <= pressed_index < len(options):
                self._selections[key] = options[pressed_index][0]
            self._refresh_active_focus()
            break

    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id or ""
        if button_id == "onboarding-start":
            self.app.post_message(
                self.Finished(dict(self._selections), skipped=False),
            )
            self.dismiss()
        elif button_id == "onboarding-skip":
            self.action_skip()

    def action_move_up(self) -> None:
        self._active_row = (self._active_row - 1) % self._row_count()
        self._refresh_active_focus()

    def action_move_down(self) -> None:
        self._active_row = (self._active_row + 1) % self._row_count()
        self._refresh_active_focus()

    def action_move_left(self) -> None:
        if self._active_row < len(_SETTINGS):
            self._set_current_option(self._current_option_index() - 1)
            return
        nav_row = self.query_one("#onboarding-nav-row", Horizontal)
        buttons = list(nav_row.query(Button))
        if buttons:
            self._active_cta = (self._active_cta - 1) % len(buttons)
            self._refresh_active_focus()

    def action_move_right(self) -> None:
        if self._active_row < len(_SETTINGS):
            self._set_current_option(self._current_option_index() + 1)
            return
        nav_row = self.query_one("#onboarding-nav-row", Horizontal)
        buttons = list(nav_row.query(Button))
        if buttons:
            self._active_cta = (self._active_cta + 1) % len(buttons)
            self._refresh_active_focus()

    def action_confirm(self) -> None:
        if self._active_row < len(_SETTINGS):
            self._set_current_option(self._current_option_index())
            return
        nav_row = self.query_one("#onboarding-nav-row", Horizontal)
        buttons = list(nav_row.query(Button))
        if not buttons:
            return
        buttons[self._active_cta % len(buttons)].press()

    def action_cancel(self) -> None:
        self.action_skip()

    def action_skip(self) -> None:
        self.app.post_message(
            self.Finished(dict(self._selections), skipped=True),
        )
        self.dismiss()
