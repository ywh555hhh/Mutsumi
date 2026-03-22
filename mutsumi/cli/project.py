"""CLI command group: mutsumi project — manage registered projects."""

from __future__ import annotations

from pathlib import Path

import click

from mutsumi.config import get_config, save_config
from mutsumi.config.settings import ProjectEntry


@click.group("project")
def project() -> None:
    """Manage project sources."""


@project.command("add")
@click.argument("path", type=click.Path(exists=True, file_okay=False))
@click.option("--name", "-n", default=None, help="Display name (default: directory name)")
def project_add(path: str, name: str | None) -> None:
    """Register a project directory as a source."""
    proj_path = Path(path).resolve()
    proj_name = name or proj_path.name

    config = get_config()

    # Check for duplicates
    for existing in config.projects:
        if existing.name == proj_name:
            click.echo(f"Project '{proj_name}' already registered.", err=True)
            raise SystemExit(1)
        if existing.path.resolve() == proj_path:
            click.echo(f"Path already registered as '{existing.name}'.", err=True)
            raise SystemExit(1)

    config.projects.append(ProjectEntry(name=proj_name, path=proj_path))
    save_config(config)
    click.echo(f"Added project: {proj_name} → {proj_path}")


@project.command("remove")
@click.argument("name")
def project_remove(name: str) -> None:
    """Unregister a project source."""
    config = get_config()
    original_len = len(config.projects)
    config.projects = [p for p in config.projects if p.name != name]

    if len(config.projects) == original_len:
        click.echo(f"Project '{name}' not found.", err=True)
        raise SystemExit(1)

    save_config(config)
    click.echo(f"Removed project: {name}")


@project.command("list")
def project_list() -> None:
    """List registered projects."""
    config = get_config()
    if not config.projects:
        click.echo("No projects registered. Use 'mutsumi project add <path>' to add one.")
        return

    click.echo("Registered projects:\n")
    for proj in config.projects:
        exists = proj.path.exists()
        status = "" if exists else " (not found)"
        click.echo(f"  {proj.name:<20} {proj.path}{status}")
