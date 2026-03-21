"""CLI command: mutsumi init — generate template tasks.json."""

from __future__ import annotations

import json
from pathlib import Path

import click


@click.command("init")
@click.option("--force", is_flag=True, help="Overwrite existing tasks.json")
@click.pass_context
def init(ctx: click.Context, force: bool) -> None:
    """Generate a template tasks.json."""
    path = Path(ctx.obj.get("path") or "tasks.json")

    if path.exists() and not force:
        click.echo(f"{path} already exists. Use --force to overwrite.")
        ctx.exit(1)
        return

    template = {
        "version": 1,
        "tasks": [
            {
                "id": "example-001",
                "title": "My first task",
                "status": "pending",
                "scope": "day",
                "priority": "normal",
                "tags": [],
                "children": [],
            }
        ],
    }

    content = json.dumps(template, indent=2, ensure_ascii=False) + "\n"
    path.write_text(content, encoding="utf-8")
    click.echo(f"Created {path}")
