"""Mutsumi CLI entry point."""

from __future__ import annotations

from pathlib import Path

import click

from mutsumi import __version__


@click.group(invoke_without_command=True)
@click.version_option(version=__version__, prog_name="mutsumi")
@click.option(
    "--path", "-p",
    type=click.Path(),
    default=None,
    help="Path to tasks.json (default: ./tasks.json)",
)
@click.pass_context
def main(ctx: click.Context, path: str | None) -> None:
    """A silent TUI task board that watches your JSON."""
    ctx.ensure_object(dict)
    ctx.obj["path"] = path
    if ctx.invoked_subcommand is None:
        from mutsumi.app import run

        task_path = Path(path) if path else None
        run(path=task_path)


@main.command()
def validate() -> None:
    """Validate tasks.json schema."""
    click.echo("Validation not yet implemented.")


@main.command()
def schema() -> None:
    """Output JSON Schema for tasks.json."""
    click.echo("Schema output not yet implemented.")


if __name__ == "__main__":
    main()
