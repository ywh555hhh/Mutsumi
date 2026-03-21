"""Tests for mutsumi setup command."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

from click.testing import CliRunner

from mutsumi.cli import main
from mutsumi.cli.setup import _MARKER


def test_setup_claude_code(tmp_path: Path) -> None:
    """setup --agent claude-code creates CLAUDE.md with marker."""
    import os

    original = os.getcwd()
    os.chdir(tmp_path)
    try:
        runner = CliRunner()
        result = runner.invoke(main, ["setup", "--agent", "claude-code"])
        assert result.exit_code == 0
        claude_md = tmp_path / "CLAUDE.md"
        assert claude_md.exists()
        content = claude_md.read_text(encoding="utf-8")
        assert _MARKER in content
        assert "mutsumi add" in content
    finally:
        os.chdir(original)


def test_setup_custom_stdout() -> None:
    """setup --agent custom prints to stdout, creates no file."""
    runner = CliRunner()
    result = runner.invoke(main, ["setup", "--agent", "custom"])
    assert result.exit_code == 0
    assert _MARKER in result.output
    assert "mutsumi add" in result.output


def test_setup_idempotent(tmp_path: Path) -> None:
    """Running setup twice does not duplicate the injection."""
    import os

    original = os.getcwd()
    os.chdir(tmp_path)
    try:
        runner = CliRunner()
        runner.invoke(main, ["setup", "--agent", "claude-code"])
        result2 = runner.invoke(main, ["setup", "--agent", "claude-code"])
        assert result2.exit_code == 0
        assert "Already configured" in result2.output
        content = (tmp_path / "CLAUDE.md").read_text(encoding="utf-8")
        assert content.count(_MARKER) == 1
    finally:
        os.chdir(original)


def test_setup_appends(tmp_path: Path) -> None:
    """Existing content is preserved when injecting."""
    import os

    original = os.getcwd()
    os.chdir(tmp_path)
    try:
        claude_md = tmp_path / "CLAUDE.md"
        claude_md.write_text("# My Project\n\nExisting rules here.\n", encoding="utf-8")
        runner = CliRunner()
        result = runner.invoke(main, ["setup", "--agent", "claude-code"])
        assert result.exit_code == 0
        content = claude_md.read_text(encoding="utf-8")
        assert "# My Project" in content
        assert "Existing rules here." in content
        assert _MARKER in content
    finally:
        os.chdir(original)


def test_setup_no_agent() -> None:
    """Running without --agent shows available agents."""
    runner = CliRunner()
    result = runner.invoke(main, ["setup"])
    assert result.exit_code == 0
    assert "Available agents" in result.output
    assert "claude-code" in result.output
    assert "gemini-cli" in result.output
    assert "custom" in result.output


def test_setup_gemini(tmp_path: Path) -> None:
    """setup --agent gemini-cli creates GEMINI.md."""
    import os

    original = os.getcwd()
    os.chdir(tmp_path)
    try:
        runner = CliRunner()
        result = runner.invoke(main, ["setup", "--agent", "gemini-cli"])
        assert result.exit_code == 0
        gemini_md = tmp_path / "GEMINI.md"
        assert gemini_md.exists()
        content = gemini_md.read_text(encoding="utf-8")
        assert _MARKER in content
    finally:
        os.chdir(original)
