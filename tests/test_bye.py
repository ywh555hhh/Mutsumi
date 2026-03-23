"""Tests for mutsumi bye command."""

from __future__ import annotations

import contextlib
import os
from typing import TYPE_CHECKING
from unittest.mock import patch

from click.testing import CliRunner

if TYPE_CHECKING:
    from collections.abc import Iterator
    from pathlib import Path

from mutsumi.cli import main
from mutsumi.core.skill_installer import SKILL_NAMES

_P = "mutsumi.cli.bye"
_SK = "mutsumi.core.skill_installer"


@contextlib.contextmanager
def _fake_env(home: Path) -> Iterator[None]:
    """Patch all path functions to use a fake home."""
    data_dir = home / ".local" / "share" / "mutsumi"
    with (
        patch(f"{_P}.mutsumi_home", return_value=home / ".mutsumi"),
        patch(f"{_P}.mutsumi_config_dir", return_value=home / ".config" / "mutsumi"),
        patch(f"{_P}.mutsumi_data_dir", return_value=data_dir),
        patch(f"{_SK}._home", return_value=home),
    ):
        yield


def _setup_traces(home: Path, cwd: Path) -> None:
    """Create fake Mutsumi traces for testing."""
    (home / ".mutsumi" / "skills").mkdir(parents=True)
    (home / ".mutsumi" / "config.toml").write_text("", encoding="utf-8")
    (home / ".config" / "mutsumi").mkdir(parents=True)
    (home / ".local" / "share" / "mutsumi").mkdir(parents=True)

    claude_dir = home / ".claude" / "skills"
    claude_dir.mkdir(parents=True)
    for name in SKILL_NAMES:
        src = home / ".mutsumi" / "skills" / name
        src.mkdir(exist_ok=True)
        (claude_dir / name).symlink_to(src)

    (cwd / "mutsumi.json").write_text(
        '{"version":1,"tasks":[]}', encoding="utf-8",
    )


def test_bye_removes_all_traces(tmp_path: Path) -> None:
    """bye removes global dirs, skill symlinks, and project files."""
    home = tmp_path / "home"
    home.mkdir()
    cwd = tmp_path / "project"
    cwd.mkdir()
    _setup_traces(home, cwd)

    original = os.getcwd()
    os.chdir(cwd)
    try:
        with _fake_env(home):
            runner = CliRunner()
            result = runner.invoke(main, ["bye", "--yes"])
            assert result.exit_code == 0
            assert "Bye." in result.output

            assert not (home / ".mutsumi").exists()
            assert not (home / ".config" / "mutsumi").exists()
            assert not (home / ".local" / "share" / "mutsumi").exists()

            for name in SKILL_NAMES:
                assert not (home / ".claude" / "skills" / name).exists()

            assert not (cwd / "mutsumi.json").exists()
    finally:
        os.chdir(original)


def test_bye_keep_project(tmp_path: Path) -> None:
    """--keep-project preserves mutsumi.json in cwd."""
    home = tmp_path / "home"
    home.mkdir()
    cwd = tmp_path / "project"
    cwd.mkdir()
    (home / ".mutsumi").mkdir(parents=True)
    (cwd / "mutsumi.json").write_text(
        '{"version":1,"tasks":[]}', encoding="utf-8",
    )

    original = os.getcwd()
    os.chdir(cwd)
    try:
        with _fake_env(home):
            runner = CliRunner()
            result = runner.invoke(main, ["bye", "--yes", "--keep-project"])
            assert result.exit_code == 0
            assert (cwd / "mutsumi.json").exists()
    finally:
        os.chdir(original)


def test_bye_nothing_to_remove(tmp_path: Path) -> None:
    """When no traces exist, bye says so."""
    home = tmp_path / "home"
    home.mkdir()

    original = os.getcwd()
    os.chdir(tmp_path)
    try:
        with _fake_env(home):
            runner = CliRunner()
            result = runner.invoke(main, ["bye", "--yes"])
            assert result.exit_code == 0
            assert "already gone" in result.output
    finally:
        os.chdir(original)


def test_bye_aborts_without_confirm(tmp_path: Path) -> None:
    """Without --yes, bye asks for confirmation and aborts on 'n'."""
    home = tmp_path / "home"
    home.mkdir()
    (home / ".mutsumi").mkdir(parents=True)

    original = os.getcwd()
    os.chdir(tmp_path)
    try:
        with _fake_env(home):
            runner = CliRunner()
            result = runner.invoke(main, ["bye"], input="n\n")
            assert result.exit_code != 0
            assert (home / ".mutsumi").exists()
    finally:
        os.chdir(original)
