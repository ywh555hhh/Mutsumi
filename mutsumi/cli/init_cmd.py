"""CLI command: mutsumi init — generate template mutsumi.json."""

from __future__ import annotations

import click

from mutsumi.core.loader import resolve_tasks_path
from mutsumi.onboarding.files import (
    ensure_personal_task_file,
    ensure_project_task_file,
    register_project,
)


@click.command("init")
@click.option("--force", is_flag=True, help="Overwrite existing file")
@click.option(
    "--personal", is_flag=True,
    help="Initialize personal task file (~/.mutsumi/mutsumi.json)",
)
@click.option(
    "--project", "as_project", is_flag=True,
    help="Create mutsumi.json in cwd AND register as a project source",
)
@click.pass_context
def init(ctx: click.Context, force: bool, personal: bool, as_project: bool) -> None:
    """Generate a template mutsumi.json."""
    if personal:
        from mutsumi.core.paths import personal_tasks_path

        path = personal_tasks_path()
        if path.exists() and not force:
            click.echo(f"{path} already exists. Use --force to overwrite.")
            ctx.exit(1)
            return
        ensure_personal_task_file(force=True)
        click.echo(f"Created personal tasks: {path}")
        return

    path = resolve_tasks_path(ctx.obj.get("path"))
    if path.exists() and not force:
        click.echo(f"{path} already exists. Use --force to overwrite.")
        ctx.exit(1)
        return

    ensure_project_task_file(path.parent, force=True)
    click.echo(f"Created {path}")

    if as_project:
        from mutsumi.config import get_config, save_config

        config = get_config()
        added, entry = register_project(config, path.parent)
        if added:
            save_config(config)
            click.echo(f"Registered project: {entry.name}")
