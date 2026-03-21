"""CLI command: mutsumi setup — inject agent integration instructions."""

from __future__ import annotations

from pathlib import Path

import click

_MARKER = "## Mutsumi Task Integration"

_PROMPT_TEMPLATE = """\
## Mutsumi Task Integration

This project uses Mutsumi for task management. Tasks live in `./tasks.json`.

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
1. Read `./tasks.json`  2. Modify tasks array  3. Write ENTIRE file back
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


def _file_contains_marker(path: Path) -> bool:
    """Check if file already contains the Mutsumi integration marker."""
    if not path.exists():
        return False
    content = path.read_text(encoding="utf-8")
    return _MARKER in content


def _inject_to_file(path: Path) -> None:
    """Append the prompt template to a file, creating it if needed."""
    if _file_contains_marker(path):
        click.echo(f"Already configured: {path} already contains '{_MARKER}'")
        return

    existing = ""
    if path.exists():
        existing = path.read_text(encoding="utf-8")

    separator = "\n\n" if existing and not existing.endswith("\n\n") else (
        "\n" if existing and not existing.endswith("\n") else ""
    )

    with open(path, "a", encoding="utf-8") as f:
        f.write(separator + _PROMPT_TEMPLATE)

    click.echo(f"Injected Mutsumi integration into {path}")


@click.command("setup")
@click.option(
    "--agent", "-a",
    type=click.Choice(list(AGENT_TARGETS.keys())),
    default=None,
    help="Target agent to configure.",
)
def setup(agent: str | None) -> None:
    """Set up Mutsumi integration for an AI agent."""
    if agent is None:
        click.echo("Available agents:\n")
        for name, target in AGENT_TARGETS.items():
            dest = target if target else "(stdout)"
            click.echo(f"  {name:<14} → {dest}")
        click.echo("\nUsage: mutsumi setup --agent <name>")
        return

    target_file = AGENT_TARGETS[agent]

    if target_file is None:
        click.echo(_PROMPT_TEMPLATE)
        return

    _inject_to_file(Path(target_file))
