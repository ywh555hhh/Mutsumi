"""CLI command: mutsumi done — mark a task as done."""

from __future__ import annotations

import click

from mutsumi.core.loader import load_task_file, resolve_tasks_path
from mutsumi.core.writer import find_task, resolve_partial_id, save_task_file, toggle_task_status


@click.command("done")
@click.argument("task_id")
@click.pass_context
def done(ctx: click.Context, task_id: str) -> None:
    """Mark a task as done (supports ID prefix matching)."""
    path = resolve_tasks_path(ctx.obj.get("path"))

    if not path.exists():
        click.echo(f"File not found: {path}", err=True)
        ctx.exit(1)
        return

    task_file = load_task_file(path)

    # Try exact match first, then prefix
    full_id = task_id
    task = find_task(task_file, task_id)
    if task is None:
        resolved = resolve_partial_id(task_file, task_id)
        if resolved is None:
            click.echo(f"No task matching '{task_id}'", err=True)
            ctx.exit(1)
            return
        full_id = resolved
        task = find_task(task_file, full_id)

    if task is None:
        click.echo(f"No task matching '{task_id}'", err=True)
        ctx.exit(1)
        return

    toggle_task_status(task_file, full_id)
    save_task_file(task_file, path)
    click.echo(f"Done: {task.title}")
