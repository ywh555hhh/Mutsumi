"""CLI command: mutsumi init — generate template mutsumi.json."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

import click

from mutsumi.core.loader import resolve_tasks_path

if TYPE_CHECKING:
    from pathlib import Path

_TEMPLATE = {
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


def _write_template(path: Path) -> None:
    """Write the task template to a file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    content = json.dumps(_TEMPLATE, indent=2, ensure_ascii=False) + "\n"
    path.write_text(content, encoding="utf-8")


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
        _write_template(path)
        click.echo(f"Created personal tasks: {path}")
        return

    path = resolve_tasks_path(ctx.obj.get("path"))
    if path.exists() and not force:
        click.echo(f"{path} already exists. Use --force to overwrite.")
        ctx.exit(1)
        return

    _write_template(path)
    click.echo(f"Created {path}")

    if as_project:
        from mutsumi.config import get_config, save_config
        from mutsumi.config.settings import ProjectEntry

        config = get_config()
        proj_name = path.parent.name
        # Don't add if already registered
        if not any(p.name == proj_name for p in config.projects):
            config.projects.append(
                ProjectEntry(name=proj_name, path=path.parent.resolve())
            )
            save_config(config)
            click.echo(f"Registered project: {proj_name}")
