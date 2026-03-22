"""CLI command: mutsumi add — add a new task."""

from __future__ import annotations

import click

from mutsumi.core.loader import load_task_file, resolve_tasks_path
from mutsumi.core.writer import add_task, create_task_from_args, save_task_file


@click.command("add")
@click.argument("title")
@click.option(
    "--priority", "-P",
    type=click.Choice(["high", "normal", "low"]),
    default="normal",
)
@click.option(
    "--scope", "-s",
    type=click.Choice(["day", "week", "month", "inbox"]),
    default="inbox",
)
@click.option("--tags", "-t", default="", help="Comma-separated tags")
@click.option("--description", "-d", default=None, help="Task description")
@click.pass_context
def add(
    ctx: click.Context,
    title: str,
    priority: str,
    scope: str,
    tags: str,
    description: str | None,
) -> None:
    """Add a new task."""
    path = resolve_tasks_path(ctx.obj.get("path"))

    if not path.exists():
        from mutsumi.core.models import TaskFile

        task_file = TaskFile(version=1, tasks=[])
    else:
        task_file = load_task_file(path)

    tag_list = [t.strip() for t in tags.split(",") if t.strip()] if tags else []
    task = create_task_from_args(
        title=title,
        priority=priority,
        scope=scope,
        tags=tag_list,
        description=description,
    )

    add_task(task_file, task)
    save_task_file(task_file, path)
    click.echo(f"Added: {title} ({task.id[:8]})")
