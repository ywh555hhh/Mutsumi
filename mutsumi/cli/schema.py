"""CLI command: mutsumi schema — output JSON Schema for tasks.json."""

from __future__ import annotations

import json

import click

from mutsumi.core.models import TaskFile


@click.command("schema")
def schema() -> None:
    """Output JSON Schema for tasks.json."""
    schema_dict = TaskFile.model_json_schema()
    click.echo(json.dumps(schema_dict, indent=2))
