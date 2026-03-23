"""First-run onboarding modal for Mutsumi — single-page layout."""

from __future__ import annotations

from typing import TYPE_CHECKING

from textual.binding import Binding
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.message import Message
from textual.screen import ModalScreen
from textual.widgets import Button, RadioButton, RadioSet, Static

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

    OnboardingScreen Button {
        margin: 0 1;
    }
    """

    BINDINGS = [
        ("escape", "skip", "Skip"),
        Binding("up", "focus_previous", "Prev", show=False),
        Binding("down", "focus_next", "Next", show=False),
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
                    with Horizontal(classes="setting-row"):
                        yield Static(label, classes="setting-label")
                        with RadioSet(id=f"rs-{safe_key}"):
                            for idx, (value, display) in enumerate(options):
                                yield RadioButton(
                                    display,
                                    value=(value == default),
                                    id=f"rb-{safe_key}-{idx}",
                                )
            with Horizontal(classes="nav-row"):
                yield Button(
                    "Start Mutsumi",
                    variant="primary",
                    id="onboarding-start",
                )
                yield Button("Skip", id="onboarding-skip")

    def on_mount(self) -> None:
        first_rs = self.query("RadioSet").first()
        if first_rs is not None:
            first_rs.focus()

    def on_radio_set_changed(self, event: RadioSet.Changed) -> None:
        rs_id = (event.radio_set.id or "").removeprefix("rs-")
        # Map safe key back to original key
        for key, _label, options in _SETTINGS:
            if key.replace("_", "-") == rs_id:
                idx = event.radio_set.pressed_index
                if 0 <= idx < len(options):
                    self._selections[key] = options[idx][0]
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

    def action_skip(self) -> None:
        self.app.post_message(
            self.Finished(dict(self._selections), skipped=True),
        )
        self.dismiss()
