"""Tests for Project CLI and save_config (Phase 5c)."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from click.testing import CliRunner

from mutsumi.cli import main
from mutsumi.config import load_config, reset_config, save_config
from mutsumi.config.settings import MutsumiConfig, ProjectEntry


class TestProjectEntry:
    def test_project_entry(self) -> None:
        p = ProjectEntry(name="myapp", path=Path("/home/user/myapp"))
        assert p.name == "myapp"
        assert p.path == Path("/home/user/myapp")

    def test_config_with_projects(self) -> None:
        config = MutsumiConfig(projects=[
            ProjectEntry(name="a", path=Path("/a")),
            ProjectEntry(name="b", path=Path("/b")),
        ])
        assert len(config.projects) == 2
        assert config.projects[0].name == "a"

    def test_config_defaults(self) -> None:
        config = MutsumiConfig()
        assert config.projects == []
        assert config.default_tab == "main"
        assert config.dashboard_max_tasks == 3
        assert config.dashboard_show_completed is True


class TestSaveConfig:
    def test_save_and_reload(self, tmp_path: Path) -> None:
        reset_config()
        config = MutsumiConfig(
            theme="nord",
            language="zh",
            projects=[ProjectEntry(name="proj-a", path=tmp_path / "proj-a")],
        )
        dest = save_config(config, tmp_path / "config.toml")
        assert dest.exists()

        # Reload and verify
        reset_config()
        loaded = load_config(dest)
        assert loaded.theme == "nord"
        assert loaded.language == "zh"
        assert len(loaded.projects) == 1
        assert loaded.projects[0].name == "proj-a"

    def test_save_creates_parent_dirs(self, tmp_path: Path) -> None:
        reset_config()
        config = MutsumiConfig()
        dest = tmp_path / "sub" / "dir" / "config.toml"
        save_config(config, dest)
        assert dest.exists()

    def test_roundtrip_with_key_overrides(self, tmp_path: Path) -> None:
        reset_config()
        config = MutsumiConfig(key_overrides={"quit": "ctrl+q"})
        dest = save_config(config, tmp_path / "config.toml")

        reset_config()
        loaded = load_config(dest)
        assert loaded.key_overrides == {"quit": "ctrl+q"}


class TestProjectCli:
    def test_project_add(self, tmp_path: Path) -> None:
        reset_config()
        proj_dir = tmp_path / "my-project"
        proj_dir.mkdir()

        config_path = tmp_path / "config.toml"
        config_path.write_text("")

        with patch("mutsumi.config.get_config", return_value=MutsumiConfig()), \
             patch("mutsumi.config.save_config") as mock_save, \
             patch("mutsumi.cli.project.get_config", return_value=MutsumiConfig()), \
             patch("mutsumi.cli.project.save_config") as mock_save2:
            runner = CliRunner()
            result = runner.invoke(main, ["project", "add", str(proj_dir)], catch_exceptions=False)
            assert result.exit_code == 0
            assert "Added project" in result.output

    def test_project_list_empty(self) -> None:
        reset_config()
        with patch("mutsumi.cli.project.get_config", return_value=MutsumiConfig()):
            runner = CliRunner()
            result = runner.invoke(main, ["project", "list"], catch_exceptions=False)
            assert result.exit_code == 0
            assert "No projects registered" in result.output

    def test_project_list_with_entries(self, tmp_path: Path) -> None:
        reset_config()
        config = MutsumiConfig(projects=[
            ProjectEntry(name="app-a", path=tmp_path),
        ])
        with patch("mutsumi.cli.project.get_config", return_value=config):
            runner = CliRunner()
            result = runner.invoke(main, ["project", "list"], catch_exceptions=False)
            assert result.exit_code == 0
            assert "app-a" in result.output

    def test_project_remove(self, tmp_path: Path) -> None:
        reset_config()
        config = MutsumiConfig(projects=[
            ProjectEntry(name="old-proj", path=tmp_path),
        ])
        with patch("mutsumi.cli.project.get_config", return_value=config), \
             patch("mutsumi.cli.project.save_config"):
            runner = CliRunner()
            result = runner.invoke(main, ["project", "remove", "old-proj"], catch_exceptions=False)
            assert result.exit_code == 0
            assert "Removed" in result.output

    def test_project_remove_not_found(self) -> None:
        reset_config()
        config = MutsumiConfig()
        with patch("mutsumi.cli.project.get_config", return_value=config):
            runner = CliRunner()
            result = runner.invoke(main, ["project", "remove", "nope"], catch_exceptions=False)
            assert result.exit_code != 0


class TestInitPersonal:
    def test_init_personal(self, tmp_path: Path) -> None:
        reset_config()
        personal = tmp_path / ".mutsumi" / "mutsumi.json"

        with patch("mutsumi.core.paths.mutsumi_home", return_value=tmp_path / ".mutsumi"):
            runner = CliRunner()
            result = runner.invoke(main, ["init", "--personal"], catch_exceptions=False)
            assert result.exit_code == 0
            assert "personal" in result.output.lower()
            assert personal.exists()

    def test_init_project(self, tmp_path: Path, monkeypatch: object) -> None:
        reset_config()
        import pytest

        if not isinstance(monkeypatch, pytest.MonkeyPatch):
            return
        monkeypatch.chdir(tmp_path)

        config_dest = tmp_path / ".mutsumi" / "config.toml"

        with patch("mutsumi.core.paths.mutsumi_home", return_value=tmp_path / ".mutsumi"):
            runner = CliRunner()
            result = runner.invoke(main, ["init", "--project"], catch_exceptions=False)
            assert result.exit_code == 0
            assert (tmp_path / "mutsumi.json").exists()
