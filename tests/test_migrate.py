"""Tests for resolve_tasks_path and migrate command (Phase 5a)."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

from click.testing import CliRunner

from mutsumi.cli import main
from mutsumi.core.loader import resolve_tasks_path

if TYPE_CHECKING:
    from pathlib import Path

    import pytest


class TestResolveTasksPath:
    def test_cli_path_takes_priority(self, tmp_path: Path) -> None:
        """Explicit --path always wins."""
        explicit = tmp_path / "custom.json"
        explicit.touch()
        result = resolve_tasks_path(str(explicit))
        assert result == explicit.resolve()

    def test_prefers_mutsumi_json(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """When both files exist, mutsumi.json wins."""
        monkeypatch.chdir(tmp_path)
        (tmp_path / "mutsumi.json").write_text('{"version":1,"tasks":[]}')
        (tmp_path / "tasks.json").write_text('{"version":1,"tasks":[]}')
        result = resolve_tasks_path()
        assert result.name == "mutsumi.json"

    def test_fallback_tasks_json(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """When only tasks.json exists, use it as fallback."""
        monkeypatch.chdir(tmp_path)
        (tmp_path / "tasks.json").write_text('{"version":1,"tasks":[]}')
        result = resolve_tasks_path()
        assert result.name == "tasks.json"

    def test_default_mutsumi_json_when_neither_exists(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """When neither exists, default to mutsumi.json."""
        monkeypatch.chdir(tmp_path)
        result = resolve_tasks_path()
        assert result.name == "mutsumi.json"

    def test_cli_none_uses_auto_detection(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """None CLI path triggers auto-detection."""
        monkeypatch.chdir(tmp_path)
        (tmp_path / "mutsumi.json").write_text('{"version":1,"tasks":[]}')
        result = resolve_tasks_path(None)
        assert result.name == "mutsumi.json"


class TestMigrateCommand:
    def test_migrate_tasks_file(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """tasks.json → mutsumi.json rename."""
        monkeypatch.chdir(tmp_path)
        data = {"version": 1, "tasks": [{"id": "t1", "title": "Test", "status": "pending"}]}
        (tmp_path / "tasks.json").write_text(json.dumps(data))

        runner = CliRunner()
        result = runner.invoke(main, ["migrate"], catch_exceptions=False)
        assert result.exit_code == 0
        assert "mutsumi.json" in result.output
        assert (tmp_path / "mutsumi.json").exists()
        assert not (tmp_path / "tasks.json").exists()

    def test_migrate_no_tasks_json(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """No tasks.json → nothing to do."""
        monkeypatch.chdir(tmp_path)
        runner = CliRunner()
        result = runner.invoke(main, ["migrate"], catch_exceptions=False)
        assert result.exit_code == 0
        assert "No tasks.json" in result.output

    def test_migrate_mutsumi_exists(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """mutsumi.json already exists → skip."""
        monkeypatch.chdir(tmp_path)
        (tmp_path / "tasks.json").write_text('{"version":1,"tasks":[]}')
        (tmp_path / "mutsumi.json").write_text('{"version":1,"tasks":[]}')

        runner = CliRunner()
        result = runner.invoke(main, ["migrate"], catch_exceptions=False)
        assert result.exit_code == 0
        assert "already exists" in result.output
