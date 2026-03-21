"""CLI command: mutsumi validate — validate tasks.json."""

from __future__ import annotations

from pathlib import Path

import click

from mutsumi.core.loader import load_task_file


@click.command("validate")
@click.pass_context
def validate(ctx: click.Context) -> None:
    """Validate tasks.json schema."""
    path = Path(ctx.obj.get("path") or "tasks.json")

    if not path.exists():
        click.echo(f"File not found: {path}", err=True)
        ctx.exit(1)
        return

    try:
        task_file = load_task_file(path)
        count = len(task_file.tasks)
        click.echo(f"Valid: {count} task(s)")
    except Exception as e:
        click.echo(f"Validation failed: {e}", err=True)
        ctx.exit(1)
