"""CLI command: mutsumi bye — complete uninstall, leave no trace."""

from __future__ import annotations

import os
import shutil
from pathlib import Path

import click

from mutsumi.core.paths import mutsumi_config_dir, mutsumi_data_dir, mutsumi_home
from mutsumi.core.skill_installer import (
    SKILL_NAMES,
    get_agent_skill_dir,
    get_all_agent_names,
)


def _safe_cwd() -> Path:
    """Get cwd, falling back to home if the directory no longer exists."""
    try:
        return Path.cwd()
    except (FileNotFoundError, OSError):
        home = Path.home()
        os.chdir(home)
        return home


def _collect_targets(include_project: bool) -> list[tuple[str, Path]]:
    """Build a list of (label, path) pairs to remove."""
    targets: list[tuple[str, Path]] = []

    # Global directories
    for label, path in [
        ("Mutsumi home", mutsumi_home()),
        ("Legacy config", mutsumi_config_dir()),
        ("Data directory", mutsumi_data_dir()),
    ]:
        if path.exists():
            targets.append((label, path))

    # Agent skill symlinks/dirs
    for agent in get_all_agent_names():
        try:
            agent_dir = get_agent_skill_dir(agent)
        except ValueError:
            continue
        for name in SKILL_NAMES:
            skill_path = agent_dir / name
            if skill_path.is_symlink() or skill_path.exists():
                targets.append((f"Skill ({agent})", skill_path))

    # Project-level files in cwd
    if include_project:
        cwd = _safe_cwd()
        for filename in ("mutsumi.json", "tasks.json"):
            p = cwd / filename
            if p.exists():
                targets.append(("Project file", p))

    return targets


def _cwd_inside_targets(targets: list[tuple[str, Path]]) -> bool:
    """Check if the current working directory is inside a target."""
    try:
        cwd = Path.cwd().resolve()
    except (FileNotFoundError, OSError):
        return False
    for _label, path in targets:
        try:
            resolved = path.resolve()
            if cwd == resolved or resolved in cwd.parents:
                return True
        except OSError:
            continue
    return False


def _remove(path: Path) -> None:
    """Remove a path — symlink, file, or directory."""
    if path.is_symlink() or path.is_file():
        path.unlink()
    elif path.is_dir():
        shutil.rmtree(path)


@click.command("bye")
@click.option(
    "--keep-project", is_flag=True, default=False,
    help="Don't delete mutsumi.json / tasks.json in the current directory.",
)
@click.option(
    "--yes", "-y", is_flag=True, default=False,
    help="Skip confirmation prompt.",
)
def bye(keep_project: bool, yes: bool) -> None:
    """Remove all Mutsumi data and skill installations. Leave no trace."""
    targets = _collect_targets(include_project=not keep_project)

    if not targets:
        click.echo("Nothing to remove — Mutsumi is already gone.")
        return

    click.echo("The following will be permanently deleted:\n")
    for label, path in targets:
        link_hint = f" → {path.resolve()}" if path.is_symlink() else ""
        click.echo(f"  {label:<20} {path}{link_hint}")

    cwd_warning = _cwd_inside_targets(targets)
    if cwd_warning:
        click.echo(
            "\n  Warning: your current directory is inside a target "
            "and will be deleted.\n  cd to another directory after this."
        )

    click.echo(f"\n  Total: {len(targets)} item(s)\n")

    if not yes:
        click.confirm("Proceed?", abort=True)

    # cd to home before deleting, so cwd doesn't vanish
    if cwd_warning:
        os.chdir(Path.home())

    removed = 0
    for _label, path in targets:
        try:
            _remove(path)
            removed += 1
        except OSError as exc:
            click.echo(f"  Failed: {path} ({exc})")

    click.echo(f"\nRemoved {removed}/{len(targets)} item(s).")
    click.echo("To uninstall the CLI itself: pip uninstall mutsumi-tui")
    click.echo("Bye.")
