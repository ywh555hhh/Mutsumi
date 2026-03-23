"""First-run onboarding modal for Mutsumi."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.message import Message
from textual.screen import ModalScreen
from textual.widgets import Button, Static

if TYPE_CHECKING:
    from mutsumi.config.settings import MutsumiConfig


@dataclass(frozen=True)
class OnboardingOption:
    value: str
    label: str
    description: str = ""


@dataclass(frozen=True)
class OnboardingStep:
    key: str
    title: str
    description: str
    options: tuple[OnboardingOption, ...]


class OnboardingScreen(ModalScreen[None]):
    """Minimal multi-step first-run onboarding flow."""

    DEFAULT_CSS = """
    OnboardingScreen {
        align: center middle;
    }

    OnboardingScreen > Vertical {
        width: 72;
        max-width: 92%;
        height: auto;
        background: #1a1a1a;
        border: solid #333333;
        padding: 1 2;
    }

    OnboardingScreen .eyebrow {
        color: #5de4c7;
        text-style: bold;
        text-align: center;
        margin-bottom: 1;
    }

    OnboardingScreen .step-title {
        color: #e0e0e0;
        text-style: bold;
        text-align: center;
        margin-bottom: 1;
    }

    OnboardingScreen .step-description {
        color: #9a9a9a;
        text-align: center;
        margin-bottom: 1;
    }

    OnboardingScreen .option-button {
        width: 100%;
        margin: 0 0 1 0;
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
        Binding("left", "focus_prev", "Prev", show=False),
        Binding("up", "focus_prev", "Prev", show=False),
        Binding("right", "focus_next", "Next", show=False),
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
        self._steps = self._build_steps(is_git_repo)
        self._step_index = 0
        self._selections = {
            "language": config.language,
            "keybindings": config.keybindings,
            "theme": config.theme,
            "workspace_mode": "personal+project" if is_git_repo else "personal-only",
            "agent_integration_mode": "none",
        }

    def compose(self):
        with Vertical():
            yield Static("Welcome to Mutsumi", classes="eyebrow", id="onboarding-eyebrow")
            yield Static("", classes="step-title", id="onboarding-title")
            yield Static("", classes="step-description", id="onboarding-description")
            yield Button("", id="option-0", classes="option-button")
            yield Button("", id="option-1", classes="option-button")
            yield Button("", id="option-2", classes="option-button")
            yield Button("", id="option-3", classes="option-button")
            with Horizontal(classes="nav-row"):
                yield Button("Back", id="onboarding-back")
                yield Button("Continue", variant="primary", id="onboarding-continue")
                yield Button("Skip", id="onboarding-skip")

    def on_mount(self) -> None:
        self._render_step()

    def _build_steps(self, is_git_repo: bool) -> tuple[OnboardingStep, ...]:
        workspace_default = (
            "Current folder + personal tasks" if is_git_repo else "Personal tasks only"
        )
        return (
            OnboardingStep(
                key="language",
                title="Choose your language",
                description="Mutsumi will remember this for future launches.",
                options=(
                    OnboardingOption("en", "English"),
                    OnboardingOption("zh", "中文"),
                    OnboardingOption("ja", "日本語"),
                ),
            ),
            OnboardingStep(
                key="keybindings",
                title="Choose your input preset",
                description="Arrows is the default and works best for most users.",
                options=(
                    OnboardingOption("arrows", "Arrows"),
                    OnboardingOption("vim", "Vim"),
                    OnboardingOption("emacs", "Emacs"),
                ),
            ),
            OnboardingStep(
                key="theme",
                title="Choose your theme",
                description="You can change this later in config.toml.",
                options=(
                    OnboardingOption("monochrome-zen", "Monochrome Zen"),
                    OnboardingOption("nord", "Nord"),
                    OnboardingOption("dracula", "Dracula"),
                    OnboardingOption("solarized", "Solarized"),
                ),
            ),
            OnboardingStep(
                key="workspace_mode",
                title="Choose your workspace mode",
                description=f"Recommended right now: {workspace_default}.",
                options=(
                    OnboardingOption("personal-only", "Personal only"),
                    OnboardingOption("project-only", "Current project only"),
                    OnboardingOption("personal+project", "Personal + current project"),
                ),
            ),
            OnboardingStep(
                key="agent_integration_mode",
                title="Choose agent integration",
                description="Skills-first is recommended. Project doc injection stays explicit.",
                options=(
                    OnboardingOption("none", "Skip for now"),
                    OnboardingOption("skills", "Register skills only"),
                    OnboardingOption("skills+project-doc", "Skills + project doc"),
                ),
            ),
        )

    def _render_step(self) -> None:
        step = self._steps[self._step_index]
        eyebrow = self.query_one("#onboarding-eyebrow", Static)
        title = self.query_one("#onboarding-title", Static)
        description = self.query_one("#onboarding-description", Static)
        eyebrow.update(f"Welcome to Mutsumi ({self._step_index + 1}/{len(self._steps)})")
        title.update(step.title)
        description.update(step.description)

        selected = self._selections[step.key]
        for idx in range(4):
            button = self.query_one(f"#option-{idx}", Button)
            if idx < len(step.options):
                option = step.options[idx]
                marker = "●" if option.value == selected else "○"
                button.label = f"{marker} {option.label}"
                button.variant = "primary" if option.value == selected else "default"
                button.display = True
                button.disabled = False
            else:
                button.display = False
                button.disabled = True

        back = self.query_one("#onboarding-back", Button)
        back.display = self._step_index > 0
        continue_button = self.query_one("#onboarding-continue", Button)
        continue_button.label = "Finish" if self._step_index == len(self._steps) - 1 else "Continue"
        self._focus_first_visible_option()

    def _focus_first_visible_option(self) -> None:
        for idx in range(4):
            button = self.query_one(f"#option-{idx}", Button)
            if button.display:
                button.focus()
                return

    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id or ""
        if button_id.startswith("option-"):
            option_index = int(button_id.split("-")[1])
            step = self._steps[self._step_index]
            if option_index < len(step.options):
                self._selections[step.key] = step.options[option_index].value
                self._render_step()
            return

        if button_id == "onboarding-back":
            self._step_index = max(0, self._step_index - 1)
            self._render_step()
            return

        if button_id == "onboarding-continue":
            if self._step_index == len(self._steps) - 1:
                self.app.post_message(self.Finished(dict(self._selections), skipped=False))
                self.dismiss()
                return
            self._step_index += 1
            self._render_step()
            return

        if button_id == "onboarding-skip":
            self.action_skip()

    def action_skip(self) -> None:
        self.app.post_message(self.Finished(dict(self._selections), skipped=True))
        self.dismiss()

    def action_focus_prev(self) -> None:
        self.focus_previous()

    def action_focus_next(self) -> None:
        self.focus_next()
