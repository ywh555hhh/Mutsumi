"""Agent integration helpers for onboarding and explicit setup."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from mutsumi.config.settings import MutsumiConfig

_MARKER = "## Mutsumi Task Integration"
SetupMode = Literal["skills", "skills+project-doc", "snippet"]

_PROMPT_TEMPLATE = """\
## Mutsumi Task Integration

This project uses Mutsumi for task management.
Tasks live in `./mutsumi.json` (fallback: `./tasks.json`).

### Schema
- Required: `id` (unique string), `title` (string), `status` ("pending"|"done")
- Optional: `scope` ("day"|"week"|"month"|"inbox"), `priority` ("high"|"normal"|"low"),
  `tags` (string[]), `children` (Task[]), `due_date` (ISO date), `description` (string)
- **Preserve any fields you don't recognize — do NOT delete them**

### CLI (preferred)
- `mutsumi add "title" --priority high --scope day --tags "dev,urgent"`
- `mutsumi done <id-prefix>` / `mutsumi edit <id-prefix> --title "new"`
- `mutsumi rm <id-prefix>` / `mutsumi list`

### Direct JSON
1. Read `./mutsumi.json`  2. Modify tasks array  3. Write ENTIRE file back
4. Atomic write: temp file + `os.rename()`  5. Generate unique ID for new tasks

The Mutsumi TUI watches this file and re-renders automatically on every save.
"""

AGENT_TARGETS: dict[str, str | None] = {
    "claude-code": "CLAUDE.md",
    "codex-cli": "AGENTS.md",
    "opencode": "opencode.md",
    "gemini-cli": "GEMINI.md",
    "aider": None,
    "custom": None,
}


@dataclass(frozen=True)
class AgentSetupResult:
    """Result of an agent setup operation."""

    mode: SetupMode
    preferred_agent: str
    config_mode: str
    target_file: Path | None = None
    wrote_project_doc: bool = False
    printed_snippet: bool = False


def get_prompt_template() -> str:
    """Return the project integration snippet."""
    return _PROMPT_TEMPLATE


def get_target_file(agent: str) -> Path | None:
    """Return the core project doc target for an agent, if any."""
    target = AGENT_TARGETS[agent]
    return Path(target) if target is not None else None


def file_contains_marker(path: Path) -> bool:
    """Check if file already contains the Mutsumi integration marker."""
    if not path.exists():
        return False
    return _MARKER in path.read_text(encoding="utf-8")


def inject_project_doc(path: Path) -> bool:
    """Append the prompt template to a file unless it is already present."""
    if file_contains_marker(path):
        return False

    existing = path.read_text(encoding="utf-8") if path.exists() else ""
    separator = "\n\n" if existing and not existing.endswith("\n\n") else (
        "\n" if existing and not existing.endswith("\n") else ""
    )
    with open(path, "a", encoding="utf-8") as f:
        f.write(separator + _PROMPT_TEMPLATE)
    return True


def apply_agent_setup(config: MutsumiConfig, agent: str, mode: SetupMode) -> AgentSetupResult:
    """Apply setup state to config and describe required side effects."""
    config.preferred_agent = agent
    config.agent_integration_mode = mode

    target_file = get_target_file(agent)
    if mode == "skills":
        return AgentSetupResult(
            mode=mode,
            preferred_agent=agent,
            config_mode=mode,
            target_file=target_file,
        )
    if mode == "snippet":
        return AgentSetupResult(
            mode=mode,
            preferred_agent=agent,
            config_mode=mode,
            target_file=target_file,
            printed_snippet=True,
        )
    return AgentSetupResult(
        mode=mode,
        preferred_agent=agent,
        config_mode=mode,
        target_file=target_file,
        wrote_project_doc=target_file is not None,
    )
