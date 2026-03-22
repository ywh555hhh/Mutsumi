"""CLI command: mutsumi list — list tasks."""

from __future__ import annotations

import click

from mutsumi.core.loader import get_task_scope, load_task_file, resolve_tasks_path
from mutsumi.core.models import TaskScope, TaskStatus


@click.command("list")
@click.option("--scope", "-s", type=click.Choice(["day", "week", "month", "inbox"]), default=None)
@click.option("--done/--no-done", default=None, help="Filter by done status")
@click.pass_context
def list_tasks(ctx: click.Context, scope: str | None, done: bool | None) -> None:
    """List tasks."""
    path = resolve_tasks_path(ctx.obj.get("path"))

    if not path.exists():
        click.echo(f"File not found: {path}", err=True)
        ctx.exit(1)
        return

    task_file = load_task_file(path)
    tasks = task_file.tasks

    # Filter by scope using due_date inference
    if scope is not None:
        scope_enum = TaskScope(scope)
        tasks = [t for t in tasks if get_task_scope(t) == scope_enum]

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
