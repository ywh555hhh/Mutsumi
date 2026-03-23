"""CLI command: mutsumi setup — configure agent integration modes."""

from __future__ import annotations

import click

from mutsumi.config import get_config, save_config
from mutsumi.onboarding.agent_setup import (
    _MARKER,
    AGENT_TARGETS,
    SKILL_CAPABLE_AGENTS,
    apply_agent_setup,
    get_prompt_template,
    inject_project_doc,
)


def _echo_skill_results(result: object) -> None:
    """Print skill installation feedback."""
    installed = getattr(result, "installed_skills", [])
    if not installed:
        click.echo("No skills were installed.")
        return
    click.echo(f"Installed {len(installed)} skill(s):")
    for path in installed:
        link_type = "symlink" if path.is_symlink() else "copy"
        click.echo(f"  {path.name} → {path} ({link_type})")


@click.command("setup")
@click.option(
    "--agent", "-a",
    type=click.Choice(list(AGENT_TARGETS.keys())),
    default=None,
    help="Target agent to configure.",
)
@click.option(
    "--mode",
    type=click.Choice(["skills", "skills+project-doc", "snippet"]),
    default="skills",
    show_default=True,
    help="Integration mode to configure.",
)
def setup(agent: str | None, mode: str) -> None:
    """Set up Mutsumi integration for an AI agent."""
    if agent is None:
        click.echo("Available agents:\n")
        for name, target in AGENT_TARGETS.items():
            skill_badge = " [skills]" if name in SKILL_CAPABLE_AGENTS else ""
            dest = target if target else "(stdout only)"
            click.echo(f"  {name:<14} → {dest}{skill_badge}")
        click.echo("\nModes:")
        click.echo("  skills            → install skill files into agent's skill directory")
        click.echo("  skills+project-doc → install skills and append project doc")
        click.echo("  snippet           → print copyable instructions")
        click.echo("\nUsage: mutsumi setup --agent <name> --mode <mode>")
        return

    config = get_config()
    result = apply_agent_setup(config, agent, mode)  # type: ignore[arg-type]
    save_config(config)

    if mode == "snippet":
        click.echo(get_prompt_template())
        click.echo(f"Saved integration mode: {result.config_mode}")
        return

    if mode == "skills+project-doc":
        _echo_skill_results(result)

        if result.target_file is None:
            click.echo(get_prompt_template())
            click.echo("This agent has no default project doc target; printed snippet instead.")
        else:
            wrote = inject_project_doc(result.target_file)
            if wrote:
                click.echo(f"Injected Mutsumi integration into {result.target_file}")
            else:
                click.echo(f"Already configured: {result.target_file} already contains '{_MARKER}'")
        click.echo(f"Saved integration mode: {result.config_mode}")
        return

    # skills mode
    _echo_skill_results(result)
    click.echo(f"Saved integration mode: {result.config_mode}")
