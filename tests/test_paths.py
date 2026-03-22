"""Tests for path helpers and config fallback chain (Phase 5f)."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING
from unittest.mock import patch

from mutsumi.config import load_config, reset_config
from mutsumi.core.paths import mutsumi_home, personal_tasks_path

if TYPE_CHECKING:
    import pytest


class TestMutsumiHome:
    def test_unix_default(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr("mutsumi.core.paths._IS_WINDOWS", False)
        monkeypatch.delenv("APPDATA", raising=False)
        result = mutsumi_home()
        assert result == Path.home() / ".mutsumi"

    def test_windows(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr("mutsumi.core.paths._IS_WINDOWS", True)
        monkeypatch.setenv("APPDATA", "/mock/appdata")
        result = mutsumi_home()
        assert result == Path("/mock/appdata") / "mutsumi"

    def test_windows_no_appdata(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr("mutsumi.core.paths._IS_WINDOWS", True)
        monkeypatch.delenv("APPDATA", raising=False)
        result = mutsumi_home()
        assert result == Path.home() / "AppData" / "Roaming" / "mutsumi"


class TestPersonalTasksPath:
    def test_returns_mutsumi_json_in_home(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr("mutsumi.core.paths._IS_WINDOWS", False)
        result = personal_tasks_path()
        assert result.name == "mutsumi.json"
        assert ".mutsumi" in str(result)


class TestConfigFallbackChain:
    def test_prefers_mutsumi_home(self, tmp_path: Path) -> None:
        """Config in ~/.mutsumi/ takes priority over ~/.config/mutsumi/."""
        reset_config()
        new_dir = tmp_path / ".mutsumi"
        new_dir.mkdir()
        (new_dir / "config.toml").write_text('theme = "nord"\n')

        old_dir = tmp_path / ".config" / "mutsumi"
        old_dir.mkdir(parents=True)
        (old_dir / "config.toml").write_text('theme = "dracula"\n')

        with patch("mutsumi.core.paths.mutsumi_home", return_value=new_dir), \
             patch("mutsumi.core.paths.mutsumi_config_dir", return_value=old_dir):
            config = load_config()
            assert config.theme == "nord"

    def test_falls_back_to_legacy(self, tmp_path: Path) -> None:
        """If no ~/.mutsumi/config.toml, use legacy ~/.config/mutsumi/."""
        reset_config()
        new_dir = tmp_path / ".mutsumi"
        # Don't create new_dir — no config there

        old_dir = tmp_path / ".config" / "mutsumi"
        old_dir.mkdir(parents=True)
        (old_dir / "config.toml").write_text('theme = "solarized"\n')

        with patch("mutsumi.core.paths.mutsumi_home", return_value=new_dir), \
             patch("mutsumi.core.paths.mutsumi_config_dir", return_value=old_dir):
            config = load_config()
            assert config.theme == "solarized"

    def test_defaults_when_no_config(self, tmp_path: Path) -> None:
        """No config files anywhere → defaults."""
        reset_config()
        new_dir = tmp_path / ".mutsumi"
        old_dir = tmp_path / ".config" / "mutsumi"

        with patch("mutsumi.core.paths.mutsumi_home", return_value=new_dir), \
             patch("mutsumi.core.paths.mutsumi_config_dir", return_value=old_dir):
            config = load_config()
            assert config.theme == "monochrome-zen"


class TestMigrateConfigCommand:
    def test_migrate_config_dir(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test --config flag migrates config directory."""
        from click.testing import CliRunner

        from mutsumi.cli import main

        monkeypatch.chdir(tmp_path)

        old_dir = tmp_path / "old_config"
        old_dir.mkdir()
        (old_dir / "config.toml").write_text('theme = "nord"\n')

        new_dir = tmp_path / "new_home"

        with patch("mutsumi.core.paths.mutsumi_config_dir", return_value=old_dir), \
             patch("mutsumi.core.paths.mutsumi_home", return_value=new_dir):
            runner = CliRunner()
            result = runner.invoke(main, ["migrate", "--config"], catch_exceptions=False)
            assert result.exit_code == 0
            assert (new_dir / "config.toml").exists()
