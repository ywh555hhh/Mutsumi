"""CLI command: mutsumi migrate — rename tasks.json → mutsumi.json."""

from __future__ import annotations

import shutil
from pathlib import Path

import click


@click.command("migrate")
@click.option(
    "--config", "migrate_config", is_flag=True,
    help="Migrate config from ~/.config/mutsumi/ to ~/.mutsumi/",
)
@click.option(
    "--all", "migrate_all", is_flag=True,
    help="Migrate both task file and config directory",
)
@click.pass_context
def migrate(ctx: click.Context, migrate_config: bool, migrate_all: bool) -> None:
    """Migrate tasks.json → mutsumi.json and/or config directory."""
    did_something = False

    # Task file migration (default behavior, or with --all)
    if not migrate_config or migrate_all:
        did_something |= _migrate_task_file()

    # Config migration (--config or --all)
    if migrate_config or migrate_all:
        did_something |= _migrate_config_dir()

    if not did_something:
        click.echo("Nothing to migrate.")


def _migrate_task_file() -> bool:
    """Rename tasks.json → mutsumi.json in cwd."""
    old = Path.cwd() / "tasks.json"
    new = Path.cwd() / "mutsumi.json"

    if not old.exists():
        click.echo("No tasks.json found in current directory.")
        return False

    if new.exists():
        click.echo("mutsumi.json already exists. Skipping task file migration.")
        return False

    old.rename(new)
    click.echo(f"Migrated: tasks.json → mutsumi.json")
    return True


def _migrate_config_dir() -> bool:
    """Migrate config from ~/.config/mutsumi/ to ~/.mutsumi/."""
    from mutsumi.core.paths import mutsumi_config_dir, mutsumi_home

    old_dir = mutsumi_config_dir()
    new_dir = mutsumi_home()

    if not old_dir.exists():
        click.echo(f"No legacy config directory found at {old_dir}")
        return False

    if new_dir.exists():
        # Merge: copy files that don't exist in new_dir
        copied = 0
        for item in old_dir.iterdir():
            dest = new_dir / item.name
            if not dest.exists():
                if item.is_file():
                    shutil.copy2(item, dest)
                    copied += 1
                elif item.is_dir():
                    shutil.copytree(item, dest)
                    copied += 1
        if copied:
            click.echo(f"Merged {copied} item(s) from {old_dir} → {new_dir}")
        else:
            click.echo(f"Config directory {new_dir} already up to date.")
        return copied > 0

    new_dir.mkdir(parents=True, exist_ok=True)
    for item in old_dir.iterdir():
        dest = new_dir / item.name
        if item.is_file():
            shutil.copy2(item, dest)
        elif item.is_dir():
            shutil.copytree(item, dest)

    click.echo(f"Migrated config: {old_dir} → {new_dir}")
    return True
