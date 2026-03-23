"""Tests for mutsumi.core.skill_installer."""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import patch

import pytest

if TYPE_CHECKING:
    from pathlib import Path

from mutsumi.core.skill_installer import (
    SKILL_NAMES,
    ensure_ssot,
    get_agent_skill_dir,
    get_all_agent_names,
    get_install_status,
    install_for_agent,
    install_for_all_agents,
    ssot_dir,
    uninstall_for_agent,
)

# ── Fixtures ────────────────────────────────────────────────────────


@pytest.fixture()
def fake_home(tmp_path: Path) -> Path:
    """Patch Path.home() to return a temporary directory."""
    with patch("mutsumi.core.skill_installer._home", return_value=tmp_path):
        yield tmp_path


@pytest.fixture()
def fake_ssot(tmp_path: Path, fake_home: Path) -> Path:
    """Patch ssot_dir and populate it with stub skill directories."""
    ssot = fake_home / ".mutsumi" / "skills"
    ssot.mkdir(parents=True, exist_ok=True)
    for name in SKILL_NAMES:
        skill_dir = ssot / name
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text(f"# {name}\n", encoding="utf-8")
    with patch("mutsumi.core.skill_installer.ssot_dir", return_value=ssot):
        yield ssot


# ── ssot_dir / get_agent_skill_dir ──────────────────────────────────


def test_ssot_dir_location(fake_home: Path) -> None:
    """SSOT is at ~/.mutsumi/skills/."""
    with patch("mutsumi.core.skill_installer.mutsumi_home", return_value=fake_home / ".mutsumi"):
        result = ssot_dir()
    assert result == fake_home / ".mutsumi" / "skills"


def test_get_agent_skill_dir_claude(fake_home: Path) -> None:
    assert get_agent_skill_dir("claude-code") == fake_home / ".claude" / "skills"


def test_get_agent_skill_dir_codex(fake_home: Path) -> None:
    assert get_agent_skill_dir("codex-cli") == fake_home / ".agents" / "skills"


def test_get_agent_skill_dir_gemini(fake_home: Path) -> None:
    assert get_agent_skill_dir("gemini-cli") == fake_home / ".gemini" / "skills"


def test_get_agent_skill_dir_opencode(fake_home: Path) -> None:
    assert get_agent_skill_dir("opencode") == fake_home / ".config" / "opencode" / "skills"


def test_get_agent_skill_dir_unknown(fake_home: Path) -> None:
    with pytest.raises(ValueError, match="Unknown agent"):
        get_agent_skill_dir("nonexistent")


def test_get_all_agent_names() -> None:
    names = get_all_agent_names()
    assert "claude-code" in names
    assert "codex-cli" in names
    assert "gemini-cli" in names
    assert "opencode" in names


# ── ensure_ssot ─────────────────────────────────────────────────────


def test_ensure_ssot_copies_bundled_skills(fake_home: Path) -> None:
    """ensure_ssot() copies bundled skills into the SSOT directory."""
    with patch("mutsumi.core.skill_installer.mutsumi_home", return_value=fake_home / ".mutsumi"):
        created = ensure_ssot()
    ssot = fake_home / ".mutsumi" / "skills"
    for name in SKILL_NAMES:
        skill_dir = ssot / name
        assert skill_dir.is_dir(), f"Expected {skill_dir} to exist"
        assert (skill_dir / "SKILL.md").exists()
    assert len(created) > 0


def test_ensure_ssot_idempotent(fake_home: Path) -> None:
    """Second call to ensure_ssot() skips existing skills."""
    with patch("mutsumi.core.skill_installer.mutsumi_home", return_value=fake_home / ".mutsumi"):
        ensure_ssot()
        second = ensure_ssot()
    assert len(second) == 0


def test_ensure_ssot_force(fake_home: Path) -> None:
    """ensure_ssot(force=True) re-copies all skills."""
    with patch("mutsumi.core.skill_installer.mutsumi_home", return_value=fake_home / ".mutsumi"):
        ensure_ssot()
        forced = ensure_ssot(force=True)
    assert len(forced) == len(SKILL_NAMES)


# ── install_for_agent ───────────────────────────────────────────────


def test_install_for_agent_symlink(fake_ssot: Path, fake_home: Path) -> None:
    """install_for_agent creates symlinks from agent dir → SSOT."""
    installed = install_for_agent("claude-code")
    agent_dir = fake_home / ".claude" / "skills"
    assert len(installed) == len(SKILL_NAMES)
    for name in SKILL_NAMES:
        skill_path = agent_dir / name
        assert skill_path.is_symlink()
        assert skill_path.resolve() == (fake_ssot / name).resolve()


def test_install_for_agent_copy_fallback(fake_ssot: Path, fake_home: Path) -> None:
    """install_for_agent(use_symlink=False) copies instead of symlinking."""
    installed = install_for_agent("codex-cli", use_symlink=False)
    agent_dir = fake_home / ".agents" / "skills"
    assert len(installed) == len(SKILL_NAMES)
    for name in SKILL_NAMES:
        skill_path = agent_dir / name
        assert skill_path.is_dir()
        assert not skill_path.is_symlink()
        assert (skill_path / "SKILL.md").exists()


def test_install_for_agent_idempotent(fake_ssot: Path, fake_home: Path) -> None:
    """Running install twice doesn't break existing symlinks."""
    install_for_agent("gemini-cli")
    installed = install_for_agent("gemini-cli")
    assert len(installed) == len(SKILL_NAMES)
    agent_dir = fake_home / ".gemini" / "skills"
    for name in SKILL_NAMES:
        assert (agent_dir / name).is_symlink()


def test_install_replaces_stale_copy(fake_ssot: Path, fake_home: Path) -> None:
    """If a skill was installed as copy, re-install replaces it with symlink."""
    install_for_agent("opencode", use_symlink=False)
    agent_dir = fake_home / ".config" / "opencode" / "skills"
    assert not (agent_dir / SKILL_NAMES[0]).is_symlink()

    install_for_agent("opencode", use_symlink=True)
    assert (agent_dir / SKILL_NAMES[0]).is_symlink()


# ── uninstall_for_agent ─────────────────────────────────────────────


def test_uninstall_removes_symlinks(fake_ssot: Path, fake_home: Path) -> None:
    install_for_agent("claude-code")
    removed = uninstall_for_agent("claude-code")
    assert len(removed) == len(SKILL_NAMES)
    agent_dir = fake_home / ".claude" / "skills"
    for name in SKILL_NAMES:
        assert not (agent_dir / name).exists()


def test_uninstall_removes_copies(fake_ssot: Path, fake_home: Path) -> None:
    install_for_agent("codex-cli", use_symlink=False)
    removed = uninstall_for_agent("codex-cli")
    assert len(removed) == len(SKILL_NAMES)


def test_uninstall_noop_when_clean(fake_ssot: Path, fake_home: Path) -> None:
    """Uninstalling when nothing is installed returns empty list."""
    agent_dir = fake_home / ".agents" / "skills"
    agent_dir.mkdir(parents=True, exist_ok=True)
    removed = uninstall_for_agent("codex-cli")
    assert removed == []


# ── install_for_all_agents ──────────────────────────────────────────


def test_install_for_all_agents(fake_ssot: Path, fake_home: Path) -> None:
    result = install_for_all_agents()
    assert len(result) == len(get_all_agent_names())
    for _agent, paths in result.items():
        assert len(paths) == len(SKILL_NAMES)


# ── get_install_status ──────────────────────────────────────────────


def test_status_symlink(fake_ssot: Path, fake_home: Path) -> None:
    install_for_agent("claude-code")
    status = get_install_status("claude-code")
    for name in SKILL_NAMES:
        assert status[name] == "symlink"


def test_status_copy(fake_ssot: Path, fake_home: Path) -> None:
    install_for_agent("codex-cli", use_symlink=False)
    status = get_install_status("codex-cli")
    for name in SKILL_NAMES:
        assert status[name] == "copy"


def test_status_missing(fake_ssot: Path, fake_home: Path) -> None:
    agent_dir = fake_home / ".gemini" / "skills"
    agent_dir.mkdir(parents=True, exist_ok=True)
    status = get_install_status("gemini-cli")
    for name in SKILL_NAMES:
        assert status[name] == "missing"


def test_status_broken_symlink(fake_ssot: Path, fake_home: Path) -> None:
    """A symlink pointing to a deleted SSOT dir reports as 'broken'."""
    install_for_agent("claude-code")
    # Remove the SSOT source to break the symlink
    import shutil

    shutil.rmtree(fake_ssot / SKILL_NAMES[0])
    status = get_install_status("claude-code")
    assert status[SKILL_NAMES[0]] == "broken"
