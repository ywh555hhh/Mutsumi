"""CLI command: mutsumi validate — validate task file schema."""

from __future__ import annotations

import click

from mutsumi.core.loader import load_task_file, resolve_tasks_path


@click.command("validate")
@click.pass_context
def validate(ctx: click.Context) -> None:
    """Validate task file schema."""
    path = resolve_tasks_path(ctx.obj.get("path"))

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
