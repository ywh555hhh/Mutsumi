# Mutsumi v1.0.0 Beta — Internal Testing Playbook

> **[中文版](./BETA_V1_cn.md)** | **[日本語版](./BETA_V1_ja.md)**

| Status | Draft — Internal Only |
|---|---|
| Date | 2026-03-23 |
| Version | `1.0.0b1` |
| Package | `mutsumi-tui` |
| CLI | `mutsumi` |

---

## What This Document Is

This is the English testing playbook for the current **`1.0.0b1`** beta line.

It focuses on two core moments:

1. **Out-of-the-box startup** — install, launch, onboarding, immediate usability
2. **Agent live sync** — talk to an agent, update the task file, watch Mutsumi refresh

This document should describe the product **as it exists now**.
Planned work such as calendar should be treated as roadmap/RFC material, not as shipped beta surface.

---

## The Two Aha Moments

| # | Name | Promise |
|---|---|---|
| Aha 1 | Out-of-the-Box | One install, short onboarding, usable board immediately |
| Aha 2 | Agent Live Sync | Agent updates tasks, Mutsumi refreshes almost immediately |

---

# Aha 1: Out-of-the-Box

## 1.1 Prerequisites

| Requirement | How to check |
|---|---|
| macOS / Linux terminal | `uname` |
| Python 3.12+ | `python3 --version` |
| `uv` or `pip` | `uv --version` or `pip --version` |

Windows users should prefer WSL during this beta stage.

## 1.2 Install

```bash
# Recommended
uv tool install mutsumi-tui

# Alternative
pip install mutsumi-tui

# Contributor path
uv tool install git+https://github.com/ywh555hhh/Mutsumi.git
```

### Validation checklist — install

| # | Step | Expected | Pass? |
|---|---|---|---|
| 1.2.1 | Run `mutsumi --version` | Prints `mutsumi, version 1.0.0b1` | [ ] |
| 1.2.2 | Run `mutsumi --help` | Shows help text with subcommands | [ ] |
| 1.2.3 | Install works via `uv` | Command is available afterward | [ ] |
| 1.2.4 | Install works via `pip` | Command is available afterward | [ ] |

## 1.3 First Launch — Onboarding

```bash
cd ~/some-project
mutsumi
```

If this is the first launch, Mutsumi should show the onboarding flow.

### Expected defaults

- language: English unless changed
- keybindings: **Arrows**
- theme: Monochrome Zen
- task file preference: `mutsumi.json`

### Validation checklist — onboarding

| # | Step | Expected | Pass? |
|---|---|---|---|
| 1.3.1 | First `mutsumi` shows onboarding | Onboarding appears instead of failing | [ ] |
| 1.3.2 | Settings are adjustable | Language, keybindings, theme, workspace, agent | [ ] |
| 1.3.3 | Choose `中文` then continue | UI labels switch accordingly | [ ] |
| 1.3.4 | Choose `Nord` then continue | Theme updates accordingly | [ ] |
| 1.3.5 | Choose `Vim` then continue | Vim bindings work afterward | [ ] |
| 1.3.6 | Leave keybindings untouched | Default preset is `arrows` | [ ] |
| 1.3.7 | Select `Claude Code` agent | Skills are installed for Claude Code | [ ] |
| 1.3.8 | Skip onboarding | App still opens with usable defaults | [ ] |
| 1.3.9 | Multi-source setup chosen | Main tab and additional source tabs appear as expected | [ ] |
| 1.3.10 | Second launch | Full onboarding does not repeat | [ ] |

## 1.4 First Interaction — Empty or Fresh Board

After onboarding, the user should be able to create a task immediately.

### Validation checklist — first interaction

| # | Step | Expected | Pass? |
|---|---|---|---|
| 1.4.1 | Empty state appears when no tasks exist | Friendly message + new-task affordance | [ ] |
| 1.4.2 | Press `n` | Task form opens | [ ] |
| 1.4.3 | Click new-task UI affordance | Task form opens | [ ] |
| 1.4.4 | Submit a title | Task appears immediately | [ ] |
| 1.4.5 | Toggle checkbox | Task switches done/pending | [ ] |
| 1.4.6 | Press `?` | Help UI appears | [ ] |

## 1.5 Aha 1 summary

**Pass condition:** a new tester can install Mutsumi, get through onboarding, and create a first task without reading deep docs first.

---

# Aha 2: Agent Live Sync

## 2.0 Split Terminal Setup

Use any split-terminal workflow you like.

### tmux

```bash
bash scripts/tmux-dev.sh
```

### Manual

```bash
tmux new-session -d -s dev
tmux split-window -h -p 35 "mutsumi"
tmux select-pane -t 0
tmux attach -t dev
```

### Other terminals

- iTerm2 split pane
- VS Code integrated terminal split
- Cursor integrated terminal split

## 2.1 Agent Setup

### Recommended: skills-first

```bash
mutsumi setup --agent claude-code
mutsumi setup --agent codex-cli
mutsumi setup --agent gemini-cli
mutsumi setup --agent opencode
```

### Optional: skills + project doc

```bash
mutsumi setup --agent claude-code --mode skills+project-doc
```

### Manual snippet

```bash
mutsumi setup --agent aider --mode snippet
mutsumi setup --agent custom --mode snippet
```

### Validation checklist — setup

| # | Step | Expected | Pass? |
|---|---|---|---|
| 2.1.1 | `mutsumi setup --agent claude-code` | Installs skill files successfully | [ ] |
| 2.1.2 | Run setup twice | Idempotent enough for repeat use | [ ] |
| 2.1.3 | `mutsumi setup` with no flags | Lists supported agents and modes | [ ] |
| 2.1.4 | `--mode skills+project-doc` | Also appends project integration snippet | [ ] |
| 2.1.5 | `--mode snippet` | Prints copyable instructions | [ ] |

## 2.2 Core Loop — Talk → Write → See

### Scenario A: Add a task casually

Example:

```text
You: "帮我加个 todo，明天交周报"
```

Expected agent behavior:

- prefer `./mutsumi.json`
- if the repo still uses legacy `tasks.json`, use that file instead
- modify the task data and write back atomically

Expected Mutsumi behavior:

- detects the change
- refreshes the board
- shows the new task without restart

### Scenario B: Batch add multiple tasks

```text
You: "把这三个 bug 都加进去：登录页白屏、支付超时、头像上传失败，都是 high priority"
```

Expected result: all tasks appear after the update.

### Scenario C: Mark done

```text
You: "登录页白屏修好了，帮我标记完成"
```

Expected result: task becomes done in the UI.

### Scenario D: Edit metadata

```text
You: "把支付超时的优先级降到 normal，加个 tag 叫 backend"
```

Expected result: updated priority and tags appear promptly.

### Validation checklist — live sync

| # | Step | Expected | Pass? |
|---|---|---|---|
| 2.2.1 | Agent adds 1 task | Appears quickly in Mutsumi | [ ] |
| 2.2.2 | Agent adds several tasks | All appear correctly | [ ] |
| 2.2.3 | Agent marks task done | Status updates immediately | [ ] |
| 2.2.4 | Agent edits priority | Priority display updates | [ ] |
| 2.2.5 | Agent edits tags | Tags update correctly | [ ] |
| 2.2.6 | Agent adds subtask | Child appears under parent | [ ] |
| 2.2.7 | Agent writes invalid JSON | Error banner appears, app stays alive | [ ] |
| 2.2.8 | Agent fixes JSON | Error clears and tasks return | [ ] |
| 2.2.9 | Unknown fields preserved | Custom metadata survives later writes | [ ] |

## 2.3 Reverse Direction — TUI → File → Agent

The sync should feel bidirectional.

| # | Step | Expected | Pass? |
|---|---|---|---|
| 2.3.1 | Toggle task in TUI | Task file updates correctly | [ ] |
| 2.3.2 | Create task in TUI | Task file updates correctly | [ ] |
| 2.3.3 | Delete task in TUI | Task file updates correctly | [ ] |
| 2.3.4 | Inline edit task title | File updates atomically | [ ] |

## 2.4 Aha 2 summary

**Pass condition:** the tester sees Mutsumi behave like a live visual brain extension for the agent, not like a separate manual tool.

---

# Pre-Release Checklist

Everything below should be green before advancing beyond the current beta cut.

## Code Quality

| # | Item | Status |
|---|---|---|
| C1 | Automated tests pass | [ ] |
| C2 | No hardcoded monochrome-only assumptions in shared CSS | [ ] |
| C3 | Major TUI strings use i18n | [ ] |
| C4 | Theme switching works | [ ] |
| C5 | i18n switching works | [ ] |
| C6 | Keybinding switching works (`arrows` / `vim` / `emacs`) | [ ] |
| C7 | Onboarding settings apply correctly | [ ] |
| C8 | Main dashboard works in multi-source mode | [ ] |
| C9 | File watching remains stable over longer sessions | [ ] |
| C10 | Atomic writes prevent partial corruption | [ ] |

## Packaging

| # | Item | Status |
|---|---|---|
| P1 | `pyproject.toml` version is `1.0.0b1` | [ ] |
| P2 | `uv tool install mutsumi-tui` works | [ ] |
| P3 | `pip install mutsumi-tui` works | [ ] |
| P4 | `mutsumi` command is available after install | [ ] |
| P5 | sdist excludes unnecessary internal directories | [ ] |
| P6 | Python 3.12+ requirement is enforced | [ ] |

## Documentation

| # | Item | Status |
|---|---|---|
| D1 | This playbook reflects the current beta accurately | [ ] |
| D2 | README matches current product behavior | [ ] |
| D3 | AGENT.md matches current file naming and setup modes | [ ] |
| D4 | Specs match canonical `mutsumi.json` + legacy fallback | [ ] |
| D5 | RFC-009 exists and calendar is documented as planned, not shipped | [ ] |

## Platform Testing

| # | Platform | Tester | Pass? |
|---|---|---|---|
| T1 | macOS + iTerm2 | Wayne | [ ] |
| T2 | macOS + tmux |  | [ ] |
| T3 | Ubuntu + tmux |  | [ ] |
| T4 | Windows WSL |  | [ ] |
| T5 | VS Code integrated terminal |  | [ ] |
| T6 | Cursor integrated terminal |  | [ ] |

## Agent Compatibility

| # | Agent | Skill setup | Live sync | Pass? |
|---|---|---|---|---|
| A1 | Claude Code | [ ] | [ ] | [ ] |
| A2 | Codex CLI | [ ] | [ ] | [ ] |
| A3 | Gemini CLI | [ ] | [ ] | [ ] |
| A4 | OpenCode | [ ] | [ ] | [ ] |
| A5 | Manual / custom | N/A | [ ] | [ ] |

---

# Known Issues / Blockers

Track blockers here during beta testing.

| # | Issue | Severity | Status |
|---|---|---|---|
| | | | |

---

# Beta Timeline

| Milestone | Owner | Status |
|---|---|---|
| Internal beta hardening for `1.0.0b1` | Wayne |  |
| Friend beta testing | Wayne |  |
| Bug-fix sprint | Wayne |  |
| Next beta / release candidate decision | Wayne |  |
| `1.0.0` GA release | Wayne |  |

---

# Important Scope Boundary

For the current beta line:

- shipped now: multi-source hub, onboarding, skills-first setup, live file sync
- not shipped yet: built-in calendar view
- calendar status: **planned via RFC-009**

This distinction should stay explicit in all beta-facing communication.

---

# Feedback Template

```markdown
## Environment
- OS:
- Terminal:
- Python version:
- Install method: uv / pip / source
- Agent (if testing Aha 2):

## Aha 1
- Install smoothness:
- Onboarding smoothness:
- First task created:
- Overall feeling (1-5):
- Issues:

## Aha 2
- Agent used:
- Split-pane method:
- Add task via agent:
- Hot-reload speed:
- Overall feeling (1-5):
- Issues:

## General
- Would you use this daily?
- What surprised you?
- What is still missing?
```
