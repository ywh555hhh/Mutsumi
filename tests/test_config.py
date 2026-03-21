"""Tests for the configuration system."""

from __future__ import annotations

from typing import TYPE_CHECKING

from mutsumi.config import load_config, reset_config
from mutsumi.config.settings import MutsumiConfig

if TYPE_CHECKING:
    from pathlib import Path


class TestMutsumiConfig:
    def test_defaults(self) -> None:
        config = MutsumiConfig()
        assert config.theme == "monochrome-zen"
        assert config.keybindings == "vim"
        assert config.language == "en"
        assert config.event_log_path is None
        assert config.default_path is None

    def test_custom_values(self) -> None:
        config = MutsumiConfig(theme="nord", language="zh", keybindings="emacs")
        assert config.theme == "nord"
        assert config.language == "zh"
        assert config.keybindings == "emacs"

    def test_extra_fields_preserved(self) -> None:
        config = MutsumiConfig(theme="nord", custom_field="hello")
        assert config.model_extra is not None
        assert config.model_extra["custom_field"] == "hello"


class TestLoadConfig:
    def test_load_missing_file(self, tmp_path: Path) -> None:
        reset_config()
        config = load_config(tmp_path / "nonexistent.toml")
        assert config.theme == "monochrome-zen"

    def test_load_valid_file(self, tmp_path: Path) -> None:
        reset_config()
        config_file = tmp_path / "config.toml"
        config_file.write_text('theme = "dracula"\nlanguage = "ja"\n')
        config = load_config(config_file)
        assert config.theme == "dracula"
        assert config.language == "ja"

    def test_load_invalid_toml(self, tmp_path: Path) -> None:
        reset_config()
        config_file = tmp_path / "config.toml"
        config_file.write_text("this is not valid toml {{{")
        config = load_config(config_file)
        # Should fall back to defaults
        assert config.theme == "monochrome-zen"

    def test_load_partial_config(self, tmp_path: Path) -> None:
        reset_config()
        config_file = tmp_path / "config.toml"
        config_file.write_text('theme = "solarized"\n')
        config = load_config(config_file)
        assert config.theme == "solarized"
        assert config.language == "en"  # default
