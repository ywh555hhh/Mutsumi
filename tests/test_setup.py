"""Tests for mutsumi setup command."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

from click.testing import CliRunner

from mutsumi.cli import main
from mutsumi.onboarding.agent_setup import _MARKER


def test_setup_claude_code_skills_only(tmp_path: Path) -> None:
    """setup defaults to skills mode and does not create CLAUDE.md."""
    import os

    original = os.getcwd()
    os.chdir(tmp_path)
    try:
        runner = CliRunner()
        result = runner.invoke(main, ["setup", "--agent", "claude-code"])
        assert result.exit_code == 0
        assert not (tmp_path / "CLAUDE.md").exists()
        assert "skills-first" in result.output
        assert "No project instruction files were modified" in result.output
    finally:
        os.chdir(original)


def test_setup_custom_snippet_stdout() -> None:
    """snippet mode prints to stdout."""
    runner = CliRunner()
    result = runner.invoke(main, ["setup", "--agent", "custom", "--mode", "snippet"])
    assert result.exit_code == 0
    assert _MARKER in result.output
    assert "mutsumi add" in result.output


def test_setup_project_doc_idempotent(tmp_path: Path) -> None:
    """Running doc injection twice does not duplicate the marker."""
    import os

    original = os.getcwd()
    os.chdir(tmp_path)
    try:
        runner = CliRunner()
        cmd = ["setup", "--agent", "claude-code", "--mode", "skills+project-doc"]
        runner.invoke(main, cmd)
        result2 = runner.invoke(main, cmd)
        assert result2.exit_code == 0
        assert "Already configured" in result2.output
        content = (tmp_path / "CLAUDE.md").read_text(encoding="utf-8")
        assert content.count(_MARKER) == 1
    finally:
        os.chdir(original)


def test_setup_project_doc_appends(tmp_path: Path) -> None:
    """Existing content is preserved when injecting project docs."""
    import os

    original = os.getcwd()
    os.chdir(tmp_path)
    try:
        claude_md = tmp_path / "CLAUDE.md"
        claude_md.write_text("# My Project\n\nExisting rules here.\n", encoding="utf-8")
        runner = CliRunner()
        cmd = ["setup", "--agent", "claude-code", "--mode", "skills+project-doc"]
        result = runner.invoke(main, cmd)
        assert result.exit_code == 0
        content = claude_md.read_text(encoding="utf-8")
        assert "# My Project" in content
        assert "Existing rules here." in content
        assert _MARKER in content
    finally:
        os.chdir(original)


def test_setup_no_agent() -> None:
    """Running without --agent shows available agents and modes."""
    runner = CliRunner()
    result = runner.invoke(main, ["setup"])
    assert result.exit_code == 0
    assert "Available agents" in result.output
    assert "claude-code" in result.output
    assert "gemini-cli" in result.output
    assert "snippet" in result.output


def test_setup_gemini_project_doc(tmp_path: Path) -> None:
    """project doc mode creates GEMINI.md."""
    import os

    original = os.getcwd()
    os.chdir(tmp_path)
    try:
        runner = CliRunner()
        cmd = ["setup", "--agent", "gemini-cli", "--mode", "skills+project-doc"]
        result = runner.invoke(main, cmd)
        assert result.exit_code == 0
        gemini_md = tmp_path / "GEMINI.md"
        assert gemini_md.exists()
        content = gemini_md.read_text(encoding="utf-8")
        assert _MARKER in content
    finally:
        os.chdir(original)
