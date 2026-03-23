#!/usr/bin/env python3
"""Auto-generate Mutsumi reference documentation from source code.

Introspects Click CLI commands, Pydantic models, config settings,
and keybinding presets to produce 4 .mdx files for the Starlight docs site.

Usage:
    uv run python scripts/gen_docs.py          # Generate all 4 docs
    uv run python scripts/gen_docs.py --check  # CI check: exit 1 if stale
"""

from __future__ import annotations

import argparse
import inspect
import subprocess
import sys
import textwrap
from pathlib import Path
from typing import get_args, get_origin

import click

# ── Paths ────────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DOCS_OUT = PROJECT_ROOT / "docs" / "site" / "src" / "content" / "docs" / "reference"


def _git_short_hash() -> str:
    """Return the short hash of HEAD, or 'unknown' if git is unavailable."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True, text=True, cwd=PROJECT_ROOT,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except FileNotFoundError:
        pass
    return "unknown"


def _auto_header() -> str:
    """Build the auto-generated header: hidden comment + visible Aside."""
    commit = _git_short_hash()
    return "\n".join([
        f"{{/* AUTO-GENERATED from commit {commit} — DO NOT EDIT. Run: uv run python scripts/gen_docs.py */}}",
        "",
        "import { Aside } from '@astrojs/starlight/components';",
        "",
        "<Aside type=\"tip\">",
        f"This page is auto-generated from source code (commit [`{commit}`](https://github.com/ywh555hhh/Mutsumi/commit/{commit})). "
        "Do not edit manually — run `uv run python scripts/gen_docs.py` to regenerate.",
        "</Aside>",
    ])


# ══════════════════════════════════════════════════════════════════════
#  1. CLI Reference
# ══════════════════════════════════════════════════════════════════════

# -- Editorial: examples, descriptions, notes per command --------

CLI_ROOT_EDITORIAL = {
    "description": "Launch the Mutsumi TUI task board.",
    "examples": textwrap.dedent("""\
        ### Examples

        ```bash
        # Launch TUI (watches mutsumi.json in current directory)
        mutsumi

        # Watch a specific file
        mutsumi --path /path/to/mutsumi.json

        # Watch multiple files (multi-project)
        mutsumi --path ~/proj-a/mutsumi.json -w ~/proj-b/mutsumi.json

        # Print version
        mutsumi --version
        ```

        If this is your first launch, the onboarding wizard runs automatically. See [Startup Flow](../../getting-started/startup-flow/) for details."""),
}

CLI_COMMANDS_EDITORIAL: dict[str, dict[str, str]] = {
    "add": {
        "description": "Create a new task and append it to `mutsumi.json`.",
        "examples": textwrap.dedent("""\
            ### Examples

            ```bash
            # Minimal
            mutsumi add "Fix login bug"

            # Full options
            mutsumi add "Fix login bug" -P high -s day -t "bugfix,urgent" -d "Session expires on refresh"

            # Short flags
            mutsumi add "Write tests" -P low -s week -t "dev"
            ```

            A unique ID and `created_at` timestamp are auto-generated."""),
    },
    "list": {
        "description": "List tasks from `mutsumi.json`.",
        "examples": textwrap.dedent("""\
            ### Examples

            ```bash
            # List all tasks
            mutsumi list

            # Filter by scope
            mutsumi list --scope day

            # Only pending tasks
            mutsumi list --no-done

            # Only completed tasks
            mutsumi list --done
            ```"""),
    },
    "done": {
        "description": "Mark a task as done (supports ID prefix matching).",
        "examples": textwrap.dedent("""\
            ### Examples

            ```bash
            # Full ID
            mutsumi done 01JQ8X7K3M0000000000000001

            # Prefix matching
            mutsumi done 01JQ

            # If prefix is ambiguous, Mutsumi lists matches
            mutsumi done 01
            # Error: Multiple tasks match '01'. Be more specific.
            ```

            Sets `status` to `"done"` and auto-fills `completed_at`."""),
    },
    "edit": {
        "description": "Edit an existing task's fields (supports ID prefix matching).",
        "examples": textwrap.dedent("""\
            ### Examples

            ```bash
            # Change title
            mutsumi edit 01JQ --title "New title"

            # Change priority and scope
            mutsumi edit 01JQ -P low -s week

            # Replace tags
            mutsumi edit 01JQ -t "docs,review"

            # Update description
            mutsumi edit 01JQ -d "Updated requirements"
            ```"""),
    },
    "rm": {
        "description": "Remove a task from `mutsumi.json` (supports ID prefix matching).",
        "examples": textwrap.dedent("""\
            ### Examples

            ```bash
            mutsumi rm 01JQ
            ```

            Removes the task and all its children."""),
    },
    "init": {
        "description": "Generate a template `mutsumi.json`.",
        "examples": textwrap.dedent("""\
            ### Examples

            ```bash
            # Create mutsumi.json in current directory
            mutsumi init

            # Overwrite existing file
            mutsumi init --force

            # Initialize personal tasks
            mutsumi init --personal

            # Create and register as project
            mutsumi init --project
            ```

            <Aside type="tip">
            In most cases you don't need `mutsumi init` — running `mutsumi` for the first time triggers the onboarding wizard which handles file creation automatically.
            </Aside>"""),
    },
    "setup": {
        "description": "Set up Mutsumi integration for an AI agent.",
        "examples": textwrap.dedent("""\
            ### Modes

            | Mode | Behavior |
            |------|----------|
            | `skills` | Remember preferred agent in config only. No files modified. |
            | `skills+project-doc` | Save preference AND append integration instructions to the agent's project doc (`CLAUDE.md`, `AGENTS.md`, etc.) |
            | `snippet` | Print the integration prompt to stdout for manual pasting. |

            ### Examples

            ```bash
            # List available agents and modes
            mutsumi setup

            # Skills-first (default -- no files modified)
            mutsumi setup --agent claude-code

            # Inject project doc into CLAUDE.md
            mutsumi setup --agent claude-code --mode skills+project-doc

            # Print prompt for manual use
            mutsumi setup --agent custom --mode snippet

            # Gemini CLI with project doc injection
            mutsumi setup --agent gemini-cli --mode skills+project-doc
            ```

            Running `skills+project-doc` again is safe -- it detects existing sections and does not duplicate."""),
    },
    "migrate": {
        "description": "Migrate from legacy file names and config locations.",
        "examples": textwrap.dedent("""\
            ### Examples

            ```bash
            # Migrate tasks.json -> mutsumi.json
            mutsumi migrate

            # Migrate config directory
            mutsumi migrate --config

            # Migrate everything
            mutsumi migrate --all
            ```"""),
    },
    "validate": {
        "description": "Validate the task file schema.",
        "examples": textwrap.dedent("""\
            ### Examples

            ```bash
            # Validate default file
            mutsumi validate

            # Validate a specific file
            mutsumi -p /path/to/mutsumi.json validate
            ```"""),
    },
    "schema": {
        "description": "Output the JSON Schema for `mutsumi.json`.",
        "examples": textwrap.dedent("""\
            ### Examples

            ```bash
            # Print schema to terminal
            mutsumi schema

            # Pipe to a file
            mutsumi schema > schema.json
            ```"""),
    },
    "project": {
        "description": "Manage registered project sources.",
    },
    "project add": {
        "description": "Register a project directory as a source.",
        "examples": textwrap.dedent("""\
            ```bash
            mutsumi project add .
            mutsumi project add ~/projects/saas-app
            ```"""),
    },
    "project remove": {
        "description": "Unregister a project source.",
        "examples": textwrap.dedent("""\
            ```bash
            mutsumi project remove saas-app
            ```"""),
    },
    "project list": {
        "description": "List all registered projects with their paths.",
    },
}

# Tail sections appended after all commands
CLI_TAIL = textwrap.dedent("""\
    ## ID Prefix Matching

    Commands that take a `TASK_ID` argument (`done`, `edit`, `rm`) support prefix matching. You don't need to type the full ID:

    ```bash
    mutsumi done 01EX    # Matches if only one ID starts with "01EX"
    ```

    If the prefix is ambiguous, Mutsumi lists matching tasks and asks you to be more specific.

    ---

    ## Exit Codes

    | Code | Meaning |
    |------|---------|
    | `0` | Success |
    | `1` | General error (file not found, ambiguous ID, etc.) |
    | `2` | Invalid arguments (click usage error) |
    """)


def _param_type_str(param: click.Parameter) -> str:
    """Human-readable type string for a Click parameter."""
    if isinstance(param.type, click.Choice):
        return "choice"
    if param.is_flag:
        return "flag"
    type_name = param.type.name
    mapping = {"STRING": "string", "TEXT": "string", "INT": "int", "FLOAT": "float", "PATH": "path", "BOOL": "flag"}
    return mapping.get(type_name, type_name.lower())


def _param_choices(param: click.Parameter) -> str:
    """Return comma-separated choices or --."""
    if isinstance(param.type, click.Choice):
        return ", ".join(f"`{c}`" for c in param.type.choices)
    return "--"


def _param_default(param: click.Parameter) -> str:
    """Format default value for display."""
    if param.default is None:
        return "--"
    if param.is_flag:
        return ""
    if isinstance(param.default, tuple) and not param.default:
        return "--"
    default = param.default
    # Filter out sentinel objects
    default_str = str(default)
    if "Sentinel" in default_str or "UNSET" in default_str:
        return "--"
    if isinstance(default, str) and default == "":
        return "--"
    return f"`{default}`"


def _format_option_name(param: click.Option) -> str:
    """Format option with long and short forms."""
    opts = param.opts + param.secondary_opts
    # Sort so long option (--) comes first
    long_opts = [o for o in opts if o.startswith("--")]
    short_opts = [o for o in opts if o.startswith("-") and not o.startswith("--")]

    parts = []
    for lo in long_opts:
        if not param.is_flag and param.type.name != "BOOL":
            type_hint = param.human_readable_name.upper() if param.human_readable_name else param.name.upper()
            parts.append(f"`{lo} {type_hint}`")
        else:
            parts.append(f"`{lo}`")
    for so in short_opts:
        parts.append(f"`{so}`")
    return " / ".join(parts) if parts else f"`{param.name}`"


def _format_flag_name(param: click.Option) -> str:
    """Format a boolean flag like --done/--no-done."""
    opts = param.opts + param.secondary_opts
    return " / ".join(f"`{o}`" for o in opts)


def introspect_cli_command(
    cmd: click.Command | click.Group,
    prefix: str = "mutsumi",
) -> list[dict[str, object]]:
    """Walk a Click command tree and collect structured data."""
    results: list[dict[str, object]] = []

    # Build usage string
    args = [p for p in cmd.params if isinstance(p, click.Argument)]
    opts = [p for p in cmd.params if isinstance(p, click.Option) and p.name != "help"]

    arg_str = " ".join(p.human_readable_name.upper() if p.human_readable_name else p.name.upper() for p in args)
    usage = f"{prefix}"
    if arg_str:
        usage += f" {arg_str}"
    if opts:
        usage += " [OPTIONS]"

    results.append({
        "name": prefix,
        "help": cmd.help or "",
        "usage": usage,
        "arguments": args,
        "options": opts,
        "is_group": isinstance(cmd, click.Group),
    })

    # Recurse into subcommands
    if isinstance(cmd, click.Group):
        for sub_name in sorted(cmd.commands):
            sub_cmd = cmd.commands[sub_name]
            results.extend(introspect_cli_command(sub_cmd, f"{prefix} {sub_name}"))

    return results


def render_cli() -> str:
    """Render the CLI reference .mdx from introspection + editorial."""
    from mutsumi.cli import main

    lines: list[str] = []
    lines.append("---")
    lines.append("title: CLI Command Reference")
    lines.append("description: Complete reference for every Mutsumi CLI command — synced with code.")
    lines.append("---")
    lines.append("")
    lines.append(_auto_header())
    lines.append("")
    lines.append("<Aside type=\"note\">")
    lines.append("This reference is generated from `mutsumi --help` output. Every option, argument, and default value matches the actual code. If something doesn't match, the code is the source of truth.")
    lines.append("</Aside>")
    lines.append("")

    # Root command
    lines.append("## mutsumi (TUI Launch)")
    lines.append("")
    lines.append(CLI_ROOT_EDITORIAL["description"])
    lines.append("")
    lines.append("```bash")
    lines.append("mutsumi [OPTIONS] [COMMAND]")
    lines.append("```")
    lines.append("")

    # Root options
    root_opts = [p for p in main.params if isinstance(p, click.Option) and p.name not in ("help", "version")]
    if root_opts:
        lines.append("| Option | Short | Description | Default |")
        lines.append("|--------|-------|-------------|---------|")
        for param in root_opts:
            long_opts = [o for o in param.opts if o.startswith("--")]
            short_opts = [o for o in param.opts if o.startswith("-") and not o.startswith("--")]
            type_hint = "PATH" if isinstance(param.type, click.Path) else param.name.upper()
            long_str = ", ".join(f"`{o} {type_hint}`" for o in long_opts) if long_opts else ""
            short_str = ", ".join(f"`{o}`" for o in short_opts) if short_opts else ""
            help_text = param.help or ""
            default = _param_default(param)
            lines.append(f"| {long_str} | {short_str} | {help_text} | {default} |")

        # Always add --version and --help manually
        lines.append("| `--version` | | Show version and exit | -- |")
        lines.append("| `--help` | | Show help and exit | -- |")
        lines.append("")

    lines.append(CLI_ROOT_EDITORIAL["examples"])
    lines.append("")
    lines.append("---")
    lines.append("")

    # Subcommands
    cmd_order = ["add", "list", "done", "edit", "rm", "init", "setup", "migrate", "validate", "schema", "project"]
    for cmd_name in cmd_order:
        if cmd_name not in main.commands:
            continue
        cmd = main.commands[cmd_name]
        editorial = CLI_COMMANDS_EDITORIAL.get(cmd_name, {})

        _render_command(lines, cmd, cmd_name, f"mutsumi {cmd_name}", editorial)

        # Handle nested group (project)
        if isinstance(cmd, click.Group):
            for sub_name in ["add", "remove", "list"]:
                if sub_name not in cmd.commands:
                    continue
                sub_cmd = cmd.commands[sub_name]
                sub_editorial = CLI_COMMANDS_EDITORIAL.get(f"{cmd_name} {sub_name}", {})
                _render_command(lines, sub_cmd, f"{cmd_name} {sub_name}", f"mutsumi {cmd_name} {sub_name}", sub_editorial, heading="###")

        lines.append("---")
        lines.append("")

    # Tail sections
    lines.append(CLI_TAIL)

    return "\n".join(lines) + "\n"


def _render_command(
    lines: list[str],
    cmd: click.Command,
    display_name: str,
    usage_prefix: str,
    editorial: dict[str, str],
    heading: str = "##",
) -> None:
    """Render a single CLI command section."""
    lines.append(f"{heading} mutsumi {display_name}")
    lines.append("")

    desc = editorial.get("description", cmd.help or "")
    if desc:
        lines.append(desc)
        lines.append("")

    # Usage
    args = [p for p in cmd.params if isinstance(p, click.Argument)]
    opts = [p for p in cmd.params if isinstance(p, click.Option) and p.name != "help"]
    arg_str = " ".join(p.human_readable_name.upper() if p.human_readable_name else p.name.upper() for p in args)
    usage = usage_prefix
    if arg_str:
        usage += f" {arg_str}"
    if opts:
        usage += " [OPTIONS]"

    lines.append("```bash")
    lines.append(usage)
    lines.append("```")
    lines.append("")

    # Options/Arguments table
    if args and not opts:
        lines.append("| Argument | Description |")
        lines.append("|----------|-------------|")
        for a in args:
            name = f"`{a.human_readable_name.upper() if a.human_readable_name else a.name.upper()}`"
            help_text = getattr(a, "help", "") or ""
            if not help_text:
                # Derive from known patterns
                arg_name_upper = a.name.upper()
                if arg_name_upper == "TASK_ID":
                    help_text = "Full task ID or any unique prefix"
                elif arg_name_upper == "TITLE":
                    help_text = "Task title text"
                elif arg_name_upper == "PATH":
                    help_text = "Path to project directory"
                elif arg_name_upper == "NAME":
                    help_text = "Project name"
            lines.append(f"| {name} | {help_text} |")
        lines.append("")

    if opts:
        # Determine table columns based on whether we have choices
        has_choices = any(isinstance(p.type, click.Choice) for p in opts)
        has_short = any(any(o.startswith("-") and not o.startswith("--") for o in p.opts) for p in opts)

        if has_choices:
            lines.append("| Option | Short | Type | Values | Default |")
            lines.append("|--------|-------|------|--------|---------|")
        else:
            lines.append("| Option | Description |")
            lines.append("|--------|-------------|")

        for param in opts:
            long_opts = [o for o in param.opts if o.startswith("--")]
            short_opts = [o for o in param.opts if o.startswith("-") and not o.startswith("--")]
            secondary = param.secondary_opts if hasattr(param, "secondary_opts") else []

            if param.is_flag and secondary:
                # Boolean flag like --done/--no-done
                all_opts = param.opts + secondary
                opt_str = " / ".join(f"`{o}`" for o in all_opts)
            else:
                opt_str = ", ".join(f"`{o}`" for o in long_opts) if long_opts else ""

            short_str = ", ".join(f"`{o}`" for o in short_opts) if short_opts else ""
            help_text = param.help or ""
            default = _param_default(param)

            if has_choices:
                type_str = _param_type_str(param)
                choices = _param_choices(param)
                lines.append(f"| {opt_str} | {short_str} | {type_str} | {choices} | {default} |")
            else:
                lines.append(f"| {opt_str} | {help_text} |")
        lines.append("")

    # Editorial: examples, notes
    if "examples" in editorial:
        lines.append(editorial["examples"])
        lines.append("")


# ══════════════════════════════════════════════════════════════════════
#  2. Task Schema Reference
# ══════════════════════════════════════════════════════════════════════

SCHEMA_EDITORIAL: dict[str, dict[str, str]] = {
    "id": {
        "validation": "Non-empty string. UUIDv7 format recommended but not enforced.",
        "example": '"id": "01JQ8X7K3M0000000000000001"',
        "notes": "UUIDv7 encodes a millisecond-precision timestamp, making IDs naturally sortable by creation time. Both agents and the TUI can generate IDs independently without coordination.",
    },
    "title": {
        "validation": "Non-empty string. Recommended 120 characters max.",
        "example": '"title": "Refactor Auth module"',
    },
    "status": {
        "validation": 'Must be `"pending"` or `"done"`. Unknown values trigger a warning badge.',
        "example": '"status": "pending"',
        "notes": 'When toggled to `"done"`, Mutsumi auto-fills `completed_at`. When toggled back to `"pending"`, `completed_at` is cleared.',
    },
    "scope": {
        "validation": 'Must be one of `"day"`, `"week"`, `"month"`, `"inbox"`.',
        "example": '"scope": "day"',
        "notes": textwrap.dedent("""\
            Scope determines which tab the task appears under. If omitted, scope is auto-derived from `due_date`. If neither `scope` nor `due_date` is set, the task falls to `"inbox"`.

            Resolution order: `manual scope > due_date derivation > fallback "inbox"`."""),
    },
    "priority": {
        "validation": 'Must be one of `"high"`, `"normal"`, `"low"`.',
        "example": '"priority": "high"',
        "notes": "Displayed as stars in the TUI: `high` = 3 stars, `normal` = 2 stars, `low` = 1 star. Tasks are grouped by priority within each scope tab.",
    },
    "tags": {
        "validation": "Array of strings. No constraints on tag values.",
        "example": '"tags": ["dev", "backend", "urgent"]',
        "notes": "Tags are displayed in the task row (space permitting) and are searchable via the <kbd>/</kbd> search bar.",
    },
    "children": {
        "validation": "Array of task objects following the same schema (recursive).",
        "example": textwrap.dedent("""\
            "children": [
              {
                "id": "01JQ8X7K4N...",
                "title": "Install PyJWT",
                "status": "done",
                "children": []
              }
            ]"""),
        "notes": "Nesting is unlimited at the data layer. The TUI renders 3 levels by default; deeper levels are collapsed.",
    },
    "created_at": {
        "validation": "ISO 8601 datetime string.",
        "example": '"created_at": "2026-03-21T08:00:00Z"',
    },
    "due_date": {
        "validation": "ISO 8601 date string (date only, no time).",
        "example": '"due_date": "2026-03-25"',
        "notes": "Used for scope auto-derivation when `scope` is not manually set. Overdue tasks (past `due_date`) are escalated to the Today tab and rendered with an overdue color indicator.",
    },
    "completed_at": {
        "validation": "ISO 8601 datetime string.",
        "example": '"completed_at": "2026-03-21T14:30:00Z"',
        "notes": 'Auto-filled when `status` changes to `"done"`. Cleared when `status` changes back to `"pending"`.',
    },
    "description": {
        "validation": "Free-form string. Markdown content is supported in the detail panel.",
        "example": '"description": "Change session-based auth to JWT.\\nNeed to modify both middleware and routing layer."',
        "notes": "Displayed in the detail panel (press <kbd>Enter</kbd> to expand).",
    },
}

SCHEMA_TAIL = textwrap.dedent("""\
    ## Custom Fields

    Any field not listed above is a custom field. Mutsumi's Pydantic model uses `extra="allow"`, which means:

    - Custom fields are **read** from `tasks.json` and stored in memory
    - Custom fields are **preserved** through every read-modify-write cycle
    - Custom fields are **never deleted** or modified by Mutsumi
    - Custom fields can be **displayed** by adding them to the `columns` config

    ```json
    {
      "id": "01JQ...",
      "title": "Train model v2",
      "status": "pending",
      "estimated_minutes": 120,
      "energy_level": "high-focus",
      "sprint": "2026-W12",
      "blocked_by": "01JQ8X7K3M0000000000000005"
    }
    ```

    ## Full Example

    ```json
    {
      "$schema": "https://mutsumi.dev/schema/v1.json",
      "version": 1,
      "tasks": [
        {
          "id": "01JQ8X7K3M0000000000000001",
          "title": "Refactor Auth module",
          "status": "pending",
          "scope": "day",
          "priority": "high",
          "tags": ["dev", "backend"],
          "created_at": "2026-03-21T08:00:00Z",
          "due_date": "2026-03-25",
          "description": "Change session-based auth to JWT",
          "children": [
            {
              "id": "01JQ8X7K3M0000000000000002",
              "title": "Install PyJWT",
              "status": "done",
              "priority": "normal",
              "tags": [],
              "completed_at": "2026-03-21T09:30:00Z",
              "children": []
            },
            {
              "id": "01JQ8X7K3M0000000000000003",
              "title": "Write middleware",
              "status": "pending",
              "priority": "normal",
              "tags": [],
              "children": []
            }
          ]
        },
        {
          "id": "01JQ8X7K3M0000000000000004",
          "title": "Buy coffee beans",
          "status": "pending",
          "scope": "inbox",
          "priority": "low",
          "tags": ["life"],
          "children": []
        }
      ]
    }
    ```
    """)


def _python_type_to_str(annotation: object) -> str:
    """Convert a Python type annotation to a human-readable string for docs."""
    if annotation is type(None):
        return "null"

    origin = get_origin(annotation)
    args = get_args(annotation)

    if origin is list:
        inner = _python_type_to_str(args[0]) if args else "any"
        return f"{inner}[]"

    # Union type (e.g., str | None)
    if origin is type(None):
        return "null"

    # Handle str | None style unions
    try:
        import types
        if isinstance(annotation, types.UnionType):
            non_none = [a for a in args if a is not type(None)]
            if len(non_none) == 1:
                return _python_type_to_str(non_none[0])
            return " | ".join(_python_type_to_str(a) for a in non_none)
    except AttributeError:
        pass

    # StrEnum subclass
    if isinstance(annotation, type) and issubclass(annotation, str) and hasattr(annotation, "__members__"):
        return "string"

    if annotation is str:
        return "string"
    if annotation is int:
        return "integer"
    if annotation is float:
        return "number"
    if annotation is bool:
        return "boolean"

    return str(annotation).replace("typing.", "").lower()


def _field_default_str(field_info: object, annotation: object) -> str:
    """Format default value for a Pydantic field."""
    from pydantic.fields import FieldInfo
    from pydantic_core import PydanticUndefined

    if not isinstance(field_info, FieldInfo):
        return "--"
    if field_info.default is PydanticUndefined:
        return "--"
    default = field_info.default
    if default is None:
        return "--"
    if isinstance(default, list):
        return "`[]`"
    if isinstance(default, dict):
        return "`{}`"
    if isinstance(default, bool):
        return f"`{str(default).lower()}`"
    if isinstance(default, str):
        return f'`"{default}"`'
    return f"`{default}`"


def _is_required(field_info: object) -> bool:
    """Check if a Pydantic field is required."""
    from pydantic.fields import FieldInfo
    from pydantic_core import PydanticUndefined

    if not isinstance(field_info, FieldInfo):
        return False
    return field_info.default is PydanticUndefined


def render_schema() -> str:
    """Render the task schema reference .mdx."""
    from mutsumi.core.models import Task, TaskFile

    lines: list[str] = []
    lines.append("---")
    lines.append("title: Task Schema Reference")
    lines.append("description: Complete reference for every field in the Mutsumi task object. Types, required status, defaults, validation rules, and examples.")
    lines.append("---")
    lines.append("")
    lines.append(_auto_header())
    lines.append("")

    # Root Object
    lines.append("## Root Object")
    lines.append("")
    lines.append("The `tasks.json` file has the following root structure:")
    lines.append("")
    lines.append("```json")
    lines.append("{")
    lines.append('  "$schema": "https://mutsumi.dev/schema/v1.json",')
    lines.append('  "version": 1,')
    lines.append('  "tasks": []')
    lines.append("}")
    lines.append("```")
    lines.append("")
    lines.append("| Field | Type | Required | Default | Validation |")
    lines.append("|-------|------|----------|---------|------------|")
    lines.append("| `$schema` | `string` | No | -- | Valid URL. For editor hints only; Mutsumi does not fetch it. |")

    for field_name, field_info in TaskFile.model_fields.items():
        annotation = field_info.annotation
        type_str = _python_type_to_str(annotation)
        if field_name == "tasks":
            type_str = "Task[]"
        required = "**Yes**" if _is_required(field_info) else "No"
        default = _field_default_str(field_info, annotation)
        validation = ""
        if field_name == "version":
            validation = "Must be `1`. Future versions may change the schema."
            required = "Yes"
            default = "--"
        elif field_name == "tasks":
            validation = "Array of task objects."
        lines.append(f"| `{field_name}` | `{type_str}` | {required} | {default} | {validation} |")

    lines.append("")
    lines.append("## Task Object Fields")
    lines.append("")

    # Task fields
    field_order = ["id", "title", "status", "scope", "priority", "tags", "children",
                   "created_at", "due_date", "completed_at", "description"]

    for field_name in field_order:
        if field_name not in Task.model_fields:
            continue
        field_info = Task.model_fields[field_name]
        annotation = field_info.annotation
        editorial = SCHEMA_EDITORIAL.get(field_name, {})

        type_str = _python_type_to_str(annotation)
        if field_name == "children":
            type_str = "Task[]"

        required = "**Yes**" if _is_required(field_info) else "No"
        default = _field_default_str(field_info, annotation)
        validation = editorial.get("validation", "")

        # Special defaults from editorial
        if field_name == "created_at":
            default = "Auto-generated on creation"

        lines.append(f"### `{field_name}`")
        lines.append("")
        lines.append("| Property | Value |")
        lines.append("|----------|-------|")
        lines.append(f"| Type | `{type_str}` |")
        lines.append(f"| Required | {required} |")
        lines.append(f"| Default | {default} |")
        if validation:
            lines.append(f"| Validation | {validation} |")
        lines.append("")

        if "example" in editorial:
            lines.append("```json")
            lines.append(editorial["example"])
            lines.append("```")
            lines.append("")

        if "notes" in editorial:
            lines.append(editorial["notes"])
            lines.append("")

    # Tail
    lines.append(SCHEMA_TAIL)

    return "\n".join(lines) + "\n"


# ══════════════════════════════════════════════════════════════════════
#  3. Config Reference
# ══════════════════════════════════════════════════════════════════════

CONFIG_EDITORIAL: dict[str, dict[str, str]] = {
    "theme": {
        "valid_values": '`"monochrome-zen"`, `"nord"`, `"dracula"`, `"solarized"`, or any custom theme filename (without `.toml`)',
        "description": "Sets the color theme. Custom themes are loaded from `~/.mutsumi/themes/<name>.toml`.",
        "example": 'theme = "dracula"',
    },
    "keybindings": {
        "valid_values": '`"vim"`, `"emacs"`, `"arrows"`',
        "description": "Selects the keybinding preset. Per-key overrides can be applied via `[key_overrides]`.",
        "example": 'keybindings = "emacs"',
    },
    "language": {
        "valid_values": '`"en"`, `"zh"`, `"ja"`',
        "description": 'Sets the UI language. Detection priority: config > `$LANG` env > fallback `"en"`.',
        "example": 'language = "zh"',
    },
    "default_scope": {
        "valid_values": '`"day"`, `"week"`, `"month"`, `"inbox"`',
        "description": "The default scope assigned to new tasks created via the TUI (unless overridden in the dialog). Also determines which tab is active on launch.",
        "example": 'default_scope = "week"',
    },
    "notification_mode": {
        "valid_values": '`"quiet"`, `"badge"`, `"bell"`, `"system"`',
        "description": textwrap.dedent("""\
            Controls how Mutsumi notifies about overdue or updated tasks:

            | Mode | Behavior |
            |------|----------|
            | `quiet` | Fully silent. Status bar shows counts only. |
            | `badge` | Overdue tasks flash/highlight within the TUI. |
            | `bell` | Sends terminal bell (`\\a`). Terminal app decides handling. |
            | `system` | Calls system notification API (macOS/Linux/Windows). |"""),
        "example": 'notification_mode = "badge"',
    },
    "key_overrides": {
        "description": "Maps action names to new key strings, applied on top of the selected preset. See [Custom Keybindings](../../customization/custom-keybindings/) for all action names.",
        "example": textwrap.dedent("""\
            [key_overrides]
            quit = "ctrl+q"
            cursor_down = "ctrl+j"
            cursor_up = "ctrl+k\""""),
    },
    "default_path": {
        "description": "Default path to `mutsumi.json`. If set, `mutsumi` (without `--path`) watches this file instead of `./mutsumi.json`.",
        "example": 'default_path = "~/projects/main/mutsumi.json"',
    },
    "event_log_path": {
        "description": "Path for the JSONL event log. If set, Mutsumi appends events when users operate in the TUI.",
        "example": 'event_log_path = "./events.jsonl"',
    },
    "custom_css_path": {
        "description": "Path to a Textual CSS file for visual overrides. See [Custom CSS](../../customization/custom-css/).",
        "example": 'custom_css_path = "~/.mutsumi/custom.tcss"',
    },
    "columns": {
        "description": textwrap.dedent("""\
            Columns displayed in the task list. You can reference both built-in fields and custom fields added by agents.

            Built-in column names:

            | Column | Description |
            |--------|-------------|
            | `checkbox` | Done/pending checkbox |
            | `title` | Task title |
            | `tags` | Tag labels |
            | `priority` | Priority stars |
            | `due_date` | Due date |
            | `created_at` | Creation timestamp |
            | `status` | Status text |

            Custom field columns:"""),
        "example": textwrap.dedent("""\
            # Show agent-added fields
            columns = ["checkbox", "title", "effort", "sprint", "priority"]"""),
        "notes": "If a task doesn't have a referenced custom field, the column cell is empty.",
    },
    "default_tab": {
        "description": 'Default tab on launch. In multi-source mode, this is the source name (e.g., `"main"`, `"personal"`, or a project name). In single-source mode, this acts as the default scope.',
        "example": 'default_tab = "main"',
    },
    "dashboard_max_tasks": {
        "description": "Maximum number of pending tasks shown per source card on the Main dashboard.",
        "example": "dashboard_max_tasks = 5",
    },
    "dashboard_show_completed": {
        "description": "Whether to include completed tasks in dashboard progress counts.",
        "example": "dashboard_show_completed = false",
    },
    "projects": {
        "description": "Registered project sources. Each entry has a `name` (display name) and `path` (absolute path to directory containing `mutsumi.json`). Managed via `mutsumi project add/remove`.",
        "example": textwrap.dedent("""\
            [[projects]]
            name = "saas-app"
            path = "/Users/you/projects/saas-app"

            [[projects]]
            name = "oshigrid"
            path = "/Users/you/projects/oshigrid\""""),
    },
}

# Fields to skip in docs (internal flags)
CONFIG_SKIP_FIELDS = {"onboarding_completed", "preferred_agent", "agent_integration_mode"}

CONFIG_TAIL = textwrap.dedent("""\
    ## Config Commands

    ```bash
    mutsumi config --edit     # Open in $EDITOR
    mutsumi config --show     # Print current config to stdout
    mutsumi config --reset    # Reset to defaults
    mutsumi config --path     # Print config file path
    ```

    ## Directory Structure

    ```
    ~/.mutsumi/                          (preferred location)
    |-- config.toml          # Main config
    |-- mutsumi.json         # Personal tasks
    |-- themes/
    |   +-- my-theme.toml    # Custom themes
    +-- keys/
        +-- my-keys.toml     # Custom keybindings (future)
    ```
    """)


def _config_type_str(annotation: object) -> str:
    """Convert config field annotation to doc-friendly type string."""
    origin = get_origin(annotation)
    args = get_args(annotation)

    # Handle unions (e.g., Path | None)
    try:
        import types
        if isinstance(annotation, types.UnionType):
            non_none = [a for a in args if a is not type(None)]
            if len(non_none) == 1:
                base = _config_type_str(non_none[0])
                return f"{base} or `null`"
            return " | ".join(_config_type_str(a) for a in non_none)
    except AttributeError:
        pass

    if origin is list:
        inner = args[0] if args else "any"
        # Special case for ProjectEntry
        if hasattr(inner, "__name__") and inner.__name__ == "ProjectEntry":
            return "`list[{name, path}]`"
        inner_str = _config_type_str(inner)
        return f"list[{inner_str}]"

    if origin is dict:
        k = _config_type_str(args[0]) if args else "string"
        v = _config_type_str(args[1]) if len(args) > 1 else "string"
        return f"dict[{k}, {v}]"

    from pathlib import Path as PathType
    if annotation is PathType:
        return "Path"
    if annotation is str:
        return "string"
    if annotation is int:
        return "int"
    if annotation is bool:
        return "bool"

    return str(annotation)


def render_config() -> str:
    """Render the config reference .mdx."""
    from mutsumi.config.settings import MutsumiConfig

    lines: list[str] = []
    lines.append("---")
    lines.append("title: Configuration Reference")
    lines.append("description: Complete reference for every config.toml field with type, default, description, and example values.")
    lines.append("---")
    lines.append("")
    lines.append(_auto_header())
    lines.append("")

    # Header sections (static)
    lines.append("## Config File Location")
    lines.append("")
    lines.append("| Platform | Path (preferred) | Legacy fallback |")
    lines.append("|----------|------------------|-----------------|")
    lines.append("| Linux | `~/.mutsumi/config.toml` | `~/.config/mutsumi/config.toml` |")
    lines.append("| macOS | `~/.mutsumi/config.toml` | `~/.config/mutsumi/config.toml` or `~/Library/Application Support/mutsumi/config.toml` |")
    lines.append("| Windows | `%APPDATA%\\mutsumi\\config.toml` | -- |")
    lines.append("")
    lines.append("Mutsumi searches the preferred path first, then falls back to legacy locations. Run `mutsumi migrate --config` to move your config to the new location.")
    lines.append("")

    # Full Config Template (static — easier to maintain manually)
    lines.append("## Full Config Template")
    lines.append("")
    lines.append("```toml")
    lines.append("# -- Mutsumi Configuration ----------------------")
    lines.append("")
    lines.append("# Theme: built-in name or custom theme filename")
    lines.append('theme = "monochrome-zen"')
    lines.append("")
    lines.append("# Keybinding preset")
    lines.append('keybindings = "arrows"')
    lines.append("")
    lines.append("# UI language")
    lines.append('language = "en"')
    lines.append("")
    lines.append("# Default scope for new tasks and active tab on launch")
    lines.append('default_scope = "day"')
    lines.append("")
    lines.append("# Notification mode")
    lines.append('notification_mode = "quiet"')
    lines.append("")
    lines.append("# Default task file path (optional)")
    lines.append('# default_path = "/path/to/mutsumi.json"')
    lines.append("")
    lines.append("# Event log path (optional -- disabled if unset)")
    lines.append('# event_log_path = "~/.local/share/mutsumi/events.jsonl"')
    lines.append("")
    lines.append("# Custom Textual CSS path (optional)")
    lines.append('# custom_css_path = "~/.mutsumi/custom.tcss"')
    lines.append("")
    lines.append("# Columns displayed in the task list")
    lines.append('columns = ["checkbox", "title", "tags", "priority"]')
    lines.append("")
    lines.append("# Default tab on launch (multi-source: \"main\", single-source: scope name)")
    lines.append('default_tab = "main"')
    lines.append("")
    lines.append("# Dashboard: max pending tasks shown per source card")
    lines.append("dashboard_max_tasks = 3")
    lines.append("")
    lines.append("# Dashboard: show completed tasks in source cards")
    lines.append("dashboard_show_completed = true")
    lines.append("")
    lines.append("# Registered project sources")
    lines.append("# [[projects]]")
    lines.append('# name = "saas-app"')
    lines.append('# path = "/Users/you/projects/saas-app"')
    lines.append("")
    lines.append("# Per-key overrides")
    lines.append("[key_overrides]")
    lines.append('# quit = "ctrl+q"')
    lines.append('# cursor_down = "ctrl+j"')
    lines.append("```")
    lines.append("")

    # Field Reference
    lines.append("## Field Reference")
    lines.append("")

    for field_name, field_info in MutsumiConfig.model_fields.items():
        if field_name in CONFIG_SKIP_FIELDS:
            continue
        editorial = CONFIG_EDITORIAL.get(field_name, {})
        annotation = field_info.annotation

        type_str = _config_type_str(annotation)
        # Wrap type in backticks if not already
        if not type_str.startswith("`"):
            type_str = f"`{type_str}`"
        default = _field_default_str(field_info, annotation)

        lines.append(f"### `{field_name}`")
        lines.append("")
        lines.append("| Property | Value |")
        lines.append("|----------|-------|")
        lines.append(f"| Type | {type_str} |")
        lines.append(f"| Default | {default} |")
        if "valid_values" in editorial:
            lines.append(f"| Valid values | {editorial['valid_values']} |")
        lines.append("")

        if "description" in editorial:
            lines.append(editorial["description"])
            lines.append("")

        if "example" in editorial:
            lines.append("```toml")
            lines.append(editorial["example"])
            lines.append("```")
            lines.append("")

        if "notes" in editorial:
            lines.append(editorial["notes"])
            lines.append("")

    lines.append(CONFIG_TAIL)

    return "\n".join(lines) + "\n"


# ══════════════════════════════════════════════════════════════════════
#  4. Keybinding Reference
# ══════════════════════════════════════════════════════════════════════

# Category mapping for actions
ACTION_CATEGORY: dict[str, str] = {
    # Navigation
    "cursor_down": "Navigation",
    "cursor_up": "Navigation",
    "cursor_bottom": "Navigation",
    "cursor_top": "Navigation",
    # Task Operations
    "toggle_done": "Task Operations",
    "new_task": "Task Operations",
    "edit_task": "Task Operations",
    "inline_edit": "Task Operations",
    "show_detail": "Task Operations",
    "close_detail": "Task Operations",
    "cycle_scope": "Task Operations",
    # Priority
    "priority_up": "Priority",
    "priority_down": "Priority",
    # Clipboard
    "copy_task": "Clipboard",
    "paste_task": "Clipboard",
    "paste_task_above": "Clipboard",
    # Subtasks
    "add_child": "Subtasks",
    "toggle_fold": "Subtasks",
    # View Controls
    "collapse_group": "View Controls",
    "expand_group": "View Controls",
    "move_down": "View Controls",
    "move_up": "View Controls",
    # Tab Management
    "next_tab": "Tab Management",
    "prev_tab": "Tab Management",
    "tab_1": "Tab Management",
    "tab_2": "Tab Management",
    "tab_3": "Tab Management",
    "tab_4": "Tab Management",
    "tab_5": "Tab Management",
    "tab_6": "Tab Management",
    "tab_7": "Tab Management",
    "tab_8": "Tab Management",
    "tab_9": "Tab Management",
    # Search and Sort
    "search": "Search and Sort",
    "sort": "Search and Sort",
    # Utility
    "quit": "Utility",
    "show_help": "Utility",
}

# Category display order
CATEGORY_ORDER = [
    "Navigation",
    "Task Operations",
    "Priority",
    "Clipboard",
    "Subtasks",
    "View Controls",
    "Tab Management",
    "Search and Sort",
    "Utility",
]

# Actions to skip (duplicates or not user-facing)
SKIP_ACTIONS = {
    "tab_5", "tab_6", "tab_7", "tab_8", "tab_9",
}

# Human-readable key display
KEY_DISPLAY_MAP: dict[str, str] = {
    "space": "Space",
    "enter": "Enter",
    "escape": "Escape",
    "tab": "Tab",
    "shift+tab": "Shift+Tab",
    "slash": "/",
    "question_mark": "?",
    "up": "Up",
    "down": "Down",
    "left": "Left",
    "right": "Right",
    "home": "Home",
    "end": "End",
    "shift+up": "Shift+Up",
    "shift+down": "Shift+Down",
}

KEYBINDING_TAIL = textwrap.dedent("""\
    ## Multi-Key Sequences

    These actions require two key presses in sequence, handled by the `KeyManager` engine:

    | Sequence | Action | Preset |
    |----------|--------|--------|
    | <kbd>dd</kbd> | Delete selected task (then <kbd>y</kbd> to confirm) | All presets |
    | <kbd>gg</kbd> | Jump to top of list | vim only |

    Multi-key sequences have no timeout. Type keys at any speed. Press <kbd>Escape</kbd> to cancel a partial sequence.

    ## Mouse Actions

    Mouse behavior is identical across all presets:

    | Action | Behavior |
    |--------|----------|
    | Click `[ ]` / `[x]` | Toggle done/pending |
    | Click task row | Select task |
    | Double-click title | Enter inline edit mode |
    | Click tab button | Switch view (Today/Week/Month/Inbox) |
    | Click `[+New]` | Open new task dialog |
    | Click `[/Search]` | Open search bar |
    | Scroll wheel | Scroll the task list |

    ## Sort Overlay Keys

    When the sort overlay is open (triggered by <kbd>s</kbd>):

    | Key | Action |
    |-----|--------|
    | <kbd>h</kbd> / <kbd>Left</kbd> | Previous sort field |
    | <kbd>l</kbd> / <kbd>Right</kbd> | Next sort field |
    | <kbd>j</kbd> / <kbd>Down</kbd> | Next sort field |
    | <kbd>k</kbd> / <kbd>Up</kbd> | Previous sort field |
    | <kbd>r</kbd> | Toggle reverse order |
    | <kbd>Enter</kbd> | Apply sort |
    | <kbd>Escape</kbd> | Cancel |

    ## Search Bar Keys

    When the search bar is active (triggered by <kbd>/</kbd>):

    | Key | Action |
    |-----|--------|
    | Any character | Type search query |
    | <kbd>Escape</kbd> | Exit search, restore full list |
    | <kbd>Enter</kbd> | Confirm search (keep filter active) |

    ## Help Screen

    Press <kbd>?</kbd> to open the help screen displaying all keybindings for the active preset, organized by category:

    - Navigation
    - Task Operations
    - Tab Management
    - View Controls
    - Clipboard
    - Utility

    Dismiss with <kbd>Escape</kbd>, <kbd>q</kbd>, or <kbd>?</kbd>.
    """)


def _display_key(key: str, key_display: str | None = None) -> str:
    """Format a key for display in docs."""
    display = key_display or KEY_DISPLAY_MAP.get(key, key)
    return f"<kbd>{display}</kbd>"


def introspect_keybindings() -> dict[str, dict[str, str | None]]:
    """Build action -> {vim, emacs, arrows, description} mapping.

    Returns only actions that differ between presets or are shared.
    """
    from mutsumi.config.keybindings import PRESET_MAP

    # Build per-preset action maps
    preset_actions: dict[str, dict[str, tuple[str, str, str | None]]] = {}  # preset -> action -> (key, desc, key_display)
    for preset_name, bindings in PRESET_MAP.items():
        action_map: dict[str, tuple[str, str, str | None]] = {}
        for b in bindings:
            action = b.action.replace("app.", "")
            key_display = b.key_display if hasattr(b, "key_display") and b.key_display else None
            action_map[action] = (b.key, b.description, key_display)
        preset_actions[preset_name] = action_map

    # Merge into unified structure
    all_actions: set[str] = set()
    for am in preset_actions.values():
        all_actions.update(am.keys())

    result: dict[str, dict[str, str | None]] = {}
    for action in sorted(all_actions):
        vim_data = preset_actions.get("vim", {}).get(action)
        emacs_data = preset_actions.get("emacs", {}).get(action)
        arrows_data = preset_actions.get("arrows", {}).get(action)

        vim_key = _display_key(vim_data[0], vim_data[2]) if vim_data else "--"
        emacs_key = _display_key(emacs_data[0], emacs_data[2]) if emacs_data else "--"
        arrows_key = _display_key(arrows_data[0], arrows_data[2]) if arrows_data else "--"

        # Description from any preset
        desc = ""
        for data in (vim_data, emacs_data, arrows_data):
            if data and data[1]:
                desc = data[1]
                break

        is_shared = (vim_key == emacs_key == arrows_key)

        result[action] = {
            "vim": vim_key,
            "emacs": emacs_key,
            "arrows": arrows_key,
            "description": desc,
            "shared": "yes" if is_shared else "no",
        }

    return result


def render_keybindings() -> str:
    """Render the keybinding reference .mdx."""
    actions = introspect_keybindings()

    lines: list[str] = []
    lines.append("---")
    lines.append("title: Keybinding Reference")
    lines.append("description: Complete table of all keybinding actions across vim, emacs, and arrows presets.")
    lines.append("---")
    lines.append("")
    lines.append(_auto_header())
    lines.append("")
    lines.append("## All Actions")
    lines.append("")
    lines.append("Complete reference of every keybinding action with keys for each preset. Actions marked \"shared\" use the same key in all three presets.")
    lines.append("")

    for category in CATEGORY_ORDER:
        # Find actions in this category
        cat_actions = [
            (action, data) for action, data in actions.items()
            if ACTION_CATEGORY.get(action) == category and action not in SKIP_ACTIONS
        ]
        if not cat_actions:
            continue

        lines.append(f"### {category}")
        lines.append("")

        # Check if all in category are shared
        all_shared = all(d["shared"] == "yes" for _, d in cat_actions)
        any_shared = any(d["shared"] == "yes" for _, d in cat_actions)

        if all_shared:
            # Use shared table format
            lines.append("| Action | Description | Key (all presets) |")
            lines.append("|--------|-------------|-------------------|")
            for action, data in cat_actions:
                desc = data["description"]
                key = data["vim"]  # All same
                # Special display for multi-key actions
                if action == "priority_up":
                    key = "`+` or `=`"
                elif action == "priority_down":
                    key = "`-` or `_`"
                elif action in ("tab_1", "tab_2", "tab_3", "tab_4"):
                    key = f"`{action[-1]}`"
                lines.append(f"| `{action}` | {desc} | {key} |")
        else:
            # Use 5-column format for mixed categories
            lines.append("| Action | Description | vim | emacs | arrows |")
            lines.append("|--------|-------------|-----|-------|--------|")
            for action, data in cat_actions:
                desc = data["description"]
                lines.append(f"| `{action}` | {desc} | {data['vim']} | {data['emacs']} | {data['arrows']} |")

        lines.append("")

    lines.append(KEYBINDING_TAIL)

    return "\n".join(lines) + "\n"


# ══════════════════════════════════════════════════════════════════════
#  Main
# ══════════════════════════════════════════════════════════════════════

GENERATORS: dict[str, tuple[str, object]] = {
    "cli-commands.mdx": ("CLI Command Reference", render_cli),
    "task-schema.mdx": ("Task Schema Reference", render_schema),
    "config-reference.mdx": ("Configuration Reference", render_config),
    "keybinding-reference.mdx": ("Keybinding Reference", render_keybindings),
}


_AUTO_HEADER_PREFIX = "{/* AUTO-GENERATED from commit "

# ── i18n Aside injection for zh-cn / ja ──────────────────────────────

_I18N_ASIDE_MARKER = "{/* AUTO-GENERATED"

_I18N_ASIDE: dict[str, str] = {
    "zh-cn": (
        '<Aside type="tip">\n'
        "本页内容基于英文版自动生成（commit [`{commit}`](https://github.com/ywh555hhh/Mutsumi/commit/{commit})）。"
        "翻译可能滞后，权威参考请查阅 [English 版本](/reference/{slug}/)。\n"
        "</Aside>"
    ),
    "ja": (
        '<Aside type="tip">\n'
        "このページは英語版から自動生成されたものです（commit [`{commit}`](https://github.com/ywh555hhh/Mutsumi/commit/{commit})）。"
        "翻訳が遅れている場合があります。正確な情報は [English 版](/reference/{slug}/) をご参照ください。\n"
        "</Aside>"
    ),
}

# Files to inject i18n aside into (same 4 as EN)
_I18N_FILES = [
    "cli-commands.mdx",
    "task-schema.mdx",
    "config-reference.mdx",
    "keybinding-reference.mdx",
]


def _inject_i18n_aside(locale: str, check_only: bool) -> list[str]:
    """Inject or update the auto-generated Aside in i18n reference files.

    Returns list of stale/updated file descriptions.
    """
    commit = _git_short_hash()
    locale_dir = DOCS_OUT.parent / locale / "reference"
    results: list[str] = []

    if not locale_dir.exists():
        return results

    for filename in _I18N_FILES:
        filepath = locale_dir / filename
        if not filepath.exists():
            continue

        content = filepath.read_text(encoding="utf-8")
        slug = filename.replace(".mdx", "")
        aside_text = _I18N_ASIDE[locale].format(commit=commit, slug=slug)
        header_comment = f"{{/* AUTO-GENERATED from commit {commit} */}}"

        # Check if already has our marker
        if _I18N_ASIDE_MARKER in content:
            # Replace existing block: find from marker to </Aside>
            lines = content.splitlines()
            new_lines: list[str] = []
            skip = False
            for line in lines:
                if line.startswith(_I18N_ASIDE_MARKER):
                    skip = True
                    continue
                if skip and line.strip() == "</Aside>":
                    skip = False
                    continue
                if skip:
                    continue
                new_lines.append(line)
            content = "\n".join(new_lines)

        # Insert after frontmatter closing ---
        lines = content.splitlines()
        insert_idx = -1
        frontmatter_count = 0
        for i, line in enumerate(lines):
            if line.strip() == "---":
                frontmatter_count += 1
                if frontmatter_count == 2:
                    insert_idx = i + 1
                    break

        if insert_idx < 0:
            continue

        # Build injection block
        inject_lines = [
            "",
            header_comment,
            "",
            "import { Aside } from '@astrojs/starlight/components';",
            "",
            aside_text,
        ]

        # Remove existing import { Aside } if present (avoid duplicate)
        filtered = []
        for i, line in enumerate(lines):
            if i > insert_idx - 1 and line.strip() == "import { Aside } from '@astrojs/starlight/components';":
                continue
            filtered.append(line)
        lines = filtered

        # Recalculate insert_idx after filtering
        frontmatter_count = 0
        for i, line in enumerate(lines):
            if line.strip() == "---":
                frontmatter_count += 1
                if frontmatter_count == 2:
                    insert_idx = i + 1
                    break

        new_content = "\n".join(lines[:insert_idx] + inject_lines + lines[insert_idx:]) + "\n"

        # Normalize trailing whitespace
        if not content.endswith("\n"):
            content += "\n"

        if check_only:
            existing = filepath.read_text(encoding="utf-8")
            if _strip_header_line(existing) != _strip_header_line(new_content):
                results.append(f"  STALE: {locale}/{filename}")
        else:
            filepath.write_text(new_content, encoding="utf-8")
            results.append(f"  Injected: {locale}/{filename}")

    return results


def _strip_header_line(text: str) -> str:
    """Remove the AUTO-GENERATED header line for content comparison.

    The header contains a commit hash that changes on every commit,
    so we strip it before comparing to avoid false staleness.
    """
    return "\n".join(
        line for line in text.splitlines()
        if not line.startswith(_AUTO_HEADER_PREFIX)
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate Mutsumi reference docs from code.")
    parser.add_argument("--check", action="store_true", help="Check if generated docs are up-to-date (exit 1 if stale)")
    args = parser.parse_args()

    DOCS_OUT.mkdir(parents=True, exist_ok=True)

    stale: list[str] = []

    for filename, (title, render_fn) in GENERATORS.items():
        content = render_fn()
        out_path = DOCS_OUT / filename

        if args.check:
            if not out_path.exists():
                stale.append(f"  MISSING: {filename}")
                continue
            existing = out_path.read_text(encoding="utf-8")
            if _strip_header_line(existing) != _strip_header_line(content):
                stale.append(f"  STALE: {filename}")
        else:
            out_path.write_text(content, encoding="utf-8")
            print(f"  Generated: {filename}")

    if args.check:
        if stale:
            print("Reference docs are out of date:")
            for msg in stale:
                print(msg)
            print("\nRun: uv run python scripts/gen_docs.py")
            sys.exit(1)
        else:
            print("All reference docs are up to date.")
            sys.exit(0)
    else:
        # Inject i18n Aside into zh-cn and ja
        for locale in ("zh-cn", "ja"):
            results = _inject_i18n_aside(locale, check_only=False)
            for msg in results:
                print(msg)

        total = len(GENERATORS)
        print(f"\nDone. {total} EN files written to {DOCS_OUT}/")
        print("i18n Aside injected into zh-cn/ and ja/ reference files.")


if __name__ == "__main__":
    main()
