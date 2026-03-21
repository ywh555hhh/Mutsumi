"""Mutsumi CLI entry point."""

import click

from mutsumi import __version__


@click.group(invoke_without_command=True)
@click.version_option(version=__version__, prog_name="mutsumi")
@click.pass_context
def main(ctx: click.Context) -> None:
    """A silent TUI task board that watches your JSON."""
    if ctx.invoked_subcommand is None:
        from mutsumi.app import run

        run()


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
