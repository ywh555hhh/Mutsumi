"""CLI command: mutsumi list — list tasks."""

from __future__ import annotations

from pathlib import Path

import click

from mutsumi.core.loader import load_task_file
from mutsumi.core.models import TaskStatus


@click.command("list")
@click.option("--scope", "-s", type=click.Choice(["day", "week", "month", "inbox"]), default=None)
@click.option("--done/--no-done", default=None, help="Filter by done status")
@click.pass_context
def list_tasks(ctx: click.Context, scope: str | None, done: bool | None) -> None:
    """List tasks from tasks.json."""
    path = Path(ctx.obj.get("path") or "tasks.json")

    if not path.exists():
        click.echo(f"File not found: {path}", err=True)
        ctx.exit(1)
        return

    task_file = load_task_file(path)
    tasks = task_file.tasks

    # Filter by scope
    if scope is not None:
        tasks = [t for t in tasks if t.scope.value == scope]

    # Filter by done status
    if done is True:
        tasks = [t for t in tasks if t.status == TaskStatus.DONE]
    elif done is False:
        tasks = [t for t in tasks if t.status == TaskStatus.PENDING]

    if not tasks:
        click.echo("No tasks found.")
        return

    click.echo(f"Tasks in {path} ({len(tasks)}):\n")
    for task in tasks:
        checkbox = "[x]" if task.is_done else "[ ]"
        priority_marker = {"high": "!!!", "normal": "!!", "low": "!"}[task.priority.value]
        tags_str = f" [{', '.join(task.tags)}]" if task.tags else ""
        id_short = task.id[:8]

        line = f"  {checkbox} {priority_marker} {task.title}{tags_str}  ({id_short})"
        click.secho(line, dim=task.is_done)
