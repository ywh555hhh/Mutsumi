"""Install and manage Mutsumi skills in agent-specific directories.

Architecture:
- SSOT (source of truth): ~/.mutsumi/skills/<skill-name>/
- Agent directories: symlink from SSOT → agent's skill dir
- Fallback: file copy when symlinks are not available (e.g. Windows without admin)

Supported agents and their skill directories:
- Claude Code:  ~/.claude/skills/
- Codex CLI:    ~/.agents/skills/       (also discovered by Gemini/OpenCode)
- Gemini CLI:   ~/.gemini/skills/
- OpenCode:     ~/.config/opencode/skills/
"""

from __future__ import annotations

import importlib.resources
import logging
import os
import shutil
from pathlib import Path

from mutsumi.core.paths import mutsumi_home

log = logging.getLogger(__name__)

# ── Agent skill directory mapping ────────────────────────────────────

_IS_WINDOWS = os.name == "nt"


def _home() -> Path:
    return Path.home()


AGENT_SKILL_DIRS: dict[str, Path] = {}


def _build_agent_dirs() -> dict[str, Path]:
    """Build agent skill directory map (lazy, uses runtime home)."""
    home = _home()
    dirs: dict[str, Path] = {
        "claude-code": home / ".claude" / "skills",
        "codex-cli": home / ".agents" / "skills",
        "gemini-cli": home / ".gemini" / "skills",
        "opencode": home / ".config" / "opencode" / "skills",
    }
    if _IS_WINDOWS:
        appdata = os.environ.get("APPDATA", "")
        if appdata:
            dirs["opencode"] = Path(appdata) / "opencode" / "skills"
    return dirs


def get_agent_skill_dir(agent: str) -> Path:
    """Return the skill directory for a given agent."""
    dirs = _build_agent_dirs()
    if agent not in dirs:
        msg = f"Unknown agent: {agent}. Valid: {', '.join(dirs)}"
        raise ValueError(msg)
    return dirs[agent]


def get_all_agent_names() -> list[str]:
    """Return all supported agent names."""
    return list(_build_agent_dirs().keys())


# ── SSOT directory ───────────────────────────────────────────────────


def ssot_dir() -> Path:
    """Return the SSOT skills directory: ~/.mutsumi/skills/."""
    return mutsumi_home() / "skills"


# ── Bundled skill names ──────────────────────────────────────────────

SKILL_NAMES: list[str] = [
    "mutsumi-manage",
    "mutsumi-track",
    "mutsumi-plan",
    "mutsumi-report",
    "mutsumi-context",
]


def _bundled_skills_root() -> Path:
    """Return the path to the bundled skills directory in the package."""
    pkg = importlib.resources.files("mutsumi.skills")
    return Path(str(pkg))


# ── Core operations ──────────────────────────────────────────────────


def ensure_ssot(*, force: bool = False) -> list[Path]:
    """Copy bundled skills to the SSOT directory.

    Returns a list of skill directories that were created/updated.
    Skips existing directories unless *force* is True.
    """
    src_root = _bundled_skills_root()
    dst_root = ssot_dir()
    created: list[Path] = []

    # Also copy shared references/
    _sync_references(src_root, dst_root)

    for name in SKILL_NAMES:
        src = src_root / name
        dst = dst_root / name
        if not src.is_dir():
            log.warning("Bundled skill not found: %s", src)
            continue
        if dst.exists() and not force:
            log.debug("SSOT skill already exists: %s", dst)
            continue
        if dst.exists():
            shutil.rmtree(dst)
        shutil.copytree(src, dst)
        log.info("Copied skill to SSOT: %s → %s", name, dst)
        created.append(dst)

    return created


def _sync_references(src_root: Path, dst_root: Path) -> None:
    """Copy the shared references/ directory to SSOT."""
    src_ref = src_root / "references"
    dst_ref = dst_root / "references"
    if not src_ref.is_dir():
        return
    if dst_ref.exists():
        shutil.rmtree(dst_ref)
    shutil.copytree(src_ref, dst_ref)


def install_for_agent(agent: str, *, use_symlink: bool = True) -> list[Path]:
    """Install all Mutsumi skills into an agent's skill directory.

    1. Ensures SSOT is populated.
    2. For each skill, creates a symlink (or copy) in the agent's dir.

    Returns list of installed paths.
    """
    ensure_ssot()
    agent_dir = get_agent_skill_dir(agent)
    agent_dir.mkdir(parents=True, exist_ok=True)
    installed: list[Path] = []

    for name in SKILL_NAMES:
        src = ssot_dir() / name
        dst = agent_dir / name

        if not src.is_dir():
            log.warning("SSOT skill missing: %s", src)
            continue

        # Remove existing (stale symlink, old copy, etc.)
        if dst.is_symlink() or dst.exists():
            if dst.is_symlink():
                dst.unlink()
            else:
                shutil.rmtree(dst)

        if use_symlink:
            try:
                dst.symlink_to(src)
                log.info("Symlinked %s → %s", dst, src)
                installed.append(dst)
                continue
            except OSError:
                log.warning(
                    "Symlink failed for %s, falling back to copy", name,
                )

        # Fallback: copy
        shutil.copytree(src, dst)
        log.info("Copied %s → %s", name, dst)
        installed.append(dst)

    return installed


def install_for_all_agents(*, use_symlink: bool = True) -> dict[str, list[Path]]:
    """Install skills for all supported agents.

    Returns a dict of agent → installed paths.
    """
    result: dict[str, list[Path]] = {}
    for agent in get_all_agent_names():
        result[agent] = install_for_agent(agent, use_symlink=use_symlink)
    return result


def uninstall_for_agent(agent: str) -> list[Path]:
    """Remove all Mutsumi skills from an agent's skill directory.

    Returns list of removed paths.
    """
    agent_dir = get_agent_skill_dir(agent)
    removed: list[Path] = []

    for name in SKILL_NAMES:
        dst = agent_dir / name
        if dst.is_symlink():
            dst.unlink()
            log.info("Removed symlink: %s", dst)
            removed.append(dst)
        elif dst.is_dir():
            shutil.rmtree(dst)
            log.info("Removed directory: %s", dst)
            removed.append(dst)

    return removed


def uninstall_for_all_agents() -> dict[str, list[Path]]:
    """Remove Mutsumi skills from all agent directories."""
    result: dict[str, list[Path]] = {}
    for agent in get_all_agent_names():
        result[agent] = uninstall_for_agent(agent)
    return result


def get_install_status(agent: str) -> dict[str, str]:
    """Check installation status for each skill in an agent's directory.

    Returns a dict of skill_name → status string:
    - "symlink" — installed as symlink
    - "copy" — installed as file copy
    - "missing" — not installed
    - "broken" — broken symlink
    """
    agent_dir = get_agent_skill_dir(agent)
    status: dict[str, str] = {}

    for name in SKILL_NAMES:
        dst = agent_dir / name
        if dst.is_symlink():
            if dst.resolve().exists():
                status[name] = "symlink"
            else:
                status[name] = "broken"
        elif dst.is_dir():
            status[name] = "copy"
        else:
            status[name] = "missing"

    return status
