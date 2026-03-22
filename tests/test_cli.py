"""Tests for CLI base commands (init, validate, schema, --version, --help)."""

from __future__ import annotations

import json

from click.testing import CliRunner

from mutsumi.cli import main


class TestCliVersion:
    def test_version(self) -> None:
        runner = CliRunner()
        result = runner.invoke(main, ["--version"])
        assert result.exit_code == 0
        assert "mutsumi" in result.output

    def test_help(self) -> None:
        runner = CliRunner()
        result = runner.invoke(main, ["--help"])
        assert result.exit_code == 0
        assert "mutsumi" in result.output.lower()


class TestCliInit:
    def test_init_creates_file(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            result = runner.invoke(main, ["init"])
            assert result.exit_code == 0
            assert "Created" in result.output

            with open("mutsumi.json") as f:
                data = json.load(f)
            assert data["version"] == 1
            assert len(data["tasks"]) == 1

    def test_init_no_overwrite(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            with open("mutsumi.json", "w") as f:
                f.write("{}")
            result = runner.invoke(main, ["init"])
            assert result.exit_code != 0
            assert "already exists" in result.output

    def test_init_force(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            with open("mutsumi.json", "w") as f:
                f.write("{}")
            result = runner.invoke(main, ["init", "--force"])
            assert result.exit_code == 0


class TestCliValidate:
    def test_validate_valid(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            data = {"version": 1, "tasks": [{"id": "t1", "title": "Test"}]}
            with open("mutsumi.json", "w") as f:
                json.dump(data, f)
            result = runner.invoke(main, ["validate"])
            assert result.exit_code == 0
            assert "Valid" in result.output

    def test_validate_missing_file(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            result = runner.invoke(main, ["validate"])
            assert result.exit_code != 0

    def test_validate_invalid_json(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            with open("mutsumi.json", "w") as f:
                f.write("not json")
            result = runner.invoke(main, ["validate"])
            assert result.exit_code != 0


class TestCliSchema:
    def test_schema_output(self) -> None:
        runner = CliRunner()
        result = runner.invoke(main, ["schema"])
        assert result.exit_code == 0
        schema = json.loads(result.output)
        assert "properties" in schema
