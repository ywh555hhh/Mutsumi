"""Mutsumi CLI entry point."""

from __future__ import annotations

from pathlib import Path

import click

from mutsumi import __version__
from mutsumi.onboarding.bootstrap import detect_startup_state


@click.group(invoke_without_command=True)
@click.version_option(version=__version__, prog_name="mutsumi")
@click.option(
    "--path", "-p",
    type=click.Path(),
    default=None,
    help="Path to task file (default: ./mutsumi.json, fallback: ./tasks.json)",
)
@click.option(
    "--watch", "-w",
    type=click.Path(),
    multiple=True,
    help="Additional task file paths to watch (multi-project)",
)
@click.pass_context
def main(ctx: click.Context, path: str | None, watch: tuple[str, ...]) -> None:
    """A silent TUI task board that watches your JSON."""
    ctx.ensure_object(dict)
    ctx.obj["path"] = path
    if ctx.invoked_subcommand is None:
        from mutsumi.app import run

        task_path = Path(path) if path else None
        watch_paths: list[Path] | None = None
        if watch:
            watch_paths = [Path(p) for p in watch]
            if task_path:
                watch_paths.insert(0, task_path)

        startup_state = detect_startup_state()
        run(path=task_path, watch_paths=watch_paths, startup_state=startup_state)


# Register subcommands
from mutsumi.cli.add import add  # noqa: E402
from mutsumi.cli.bye import bye  # noqa: E402
from mutsumi.cli.done import done  # noqa: E402
from mutsumi.cli.edit import edit  # noqa: E402
from mutsumi.cli.init_cmd import init  # noqa: E402
from mutsumi.cli.list_cmd import list_tasks  # noqa: E402
from mutsumi.cli.migrate import migrate  # noqa: E402
from mutsumi.cli.project import project  # noqa: E402
from mutsumi.cli.rm import rm  # noqa: E402
from mutsumi.cli.schema import schema  # noqa: E402
from mutsumi.cli.setup import setup  # noqa: E402
from mutsumi.cli.validate import validate  # noqa: E402

main.add_command(init)
main.add_command(validate)
main.add_command(schema)
main.add_command(add)
main.add_command(list_tasks)
main.add_command(done)
main.add_command(rm)
main.add_command(edit)
main.add_command(setup)
main.add_command(migrate)
main.add_command(project)
main.add_command(bye)


if __name__ == "__main__":
    main()
