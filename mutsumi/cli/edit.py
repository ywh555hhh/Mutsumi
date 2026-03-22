"""CLI command: mutsumi edit — edit an existing task."""

from __future__ import annotations

import click

from mutsumi.core.loader import load_task_file, resolve_tasks_path
from mutsumi.core.writer import find_task, resolve_partial_id, save_task_file, update_task


@click.command("edit")
@click.argument("task_id")
@click.option("--title", default=None, help="New title")
@click.option("--priority", "-P", type=click.Choice(["high", "normal", "low"]), default=None)
@click.option("--scope", "-s", type=click.Choice(["day", "week", "month", "inbox"]), default=None)
@click.option("--tags", "-t", default=None, help="Comma-separated tags (replaces existing)")
@click.option("--description", "-d", default=None, help="Task description")
@click.pass_context
def edit(
    ctx: click.Context,
    task_id: str,
    title: str | None,
    priority: str | None,
    scope: str | None,
    tags: str | None,
    description: str | None,
) -> None:
    """Edit an existing task (supports ID prefix matching)."""
    path = resolve_tasks_path(ctx.obj.get("path"))

    if not path.exists():
        click.echo(f"File not found: {path}", err=True)
        ctx.exit(1)
        return

    task_file = load_task_file(path)

    # Resolve ID
    full_id = task_id
    task = find_task(task_file, task_id)
    if task is None:
        resolved = resolve_partial_id(task_file, task_id)
        if resolved is None:
            click.echo(f"No task matching '{task_id}'", err=True)
            ctx.exit(1)
            return
        full_id = resolved

    # Build update fields
    fields: dict[str, str | list[str] | None] = {}
    if title is not None:
        fields["title"] = title
    if priority is not None:
        fields["priority"] = priority
    if scope is not None:
        fields["scope"] = scope
    if tags is not None:
        fields["tags"] = [t.strip() for t in tags.split(",") if t.strip()]
    if description is not None:
        fields["description"] = description

    if not fields:
        click.echo(
            "No fields to update. Use --title, --priority, "
            "--scope, --tags, or --description."
        )
        return

    update_task(task_file, full_id, **fields)
    save_task_file(task_file, path)

    updated = find_task(task_file, full_id)
    display_title = updated.title if updated else full_id
    click.echo(f"Updated: {display_title}")
