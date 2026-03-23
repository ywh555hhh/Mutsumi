# Mutsumi v1.0.0 Beta — Internal Testing Playbook

> **[中文版](./BETA_V1_cn.md)**

| Status  | Draft — Internal Only |
|---------|----------------------|
| Date    | 2026-03-23           |
| Version | 1.0.0-beta.1         |
| Package | `mutsumi-tui` (PyPI) |
| CLI     | `mutsumi`            |

---

## What Is This Document

This is the **internal testing playbook** for Mutsumi v1.0.0 beta. It defines two "aha moments" that must land perfectly before any public release. Each aha moment has a precise validation checklist — every step must pass, no exceptions.

Beta testers should follow this document **top to bottom** as a guided experience. If any step fails, file an issue immediately.

---

## The Two Aha Moments

| # | Name | One-liner | Time budget |
|---|------|-----------|-------------|
| **Aha 1** | Out-of-the-Box | One command to install, 3-second onboarding, you're in. | < 60 seconds |
| **Aha 2** | Agent Live Sync | Talk to your agent casually, Mutsumi updates in real time. | < 30 seconds |

If a tester completes both aha moments and says "that's it?" (in a good way) — we've succeeded.

---

# Aha 1: Out-of-the-Box

**Promise**: From zero to a fully working task board in under 60 seconds. No config files, no YAML, no setup wizard hell. One command, one screen, done.

## 1.1 Prerequisites

| Requirement | How to check |
|-------------|-------------|
| macOS / Linux terminal | `uname` |
| Python 3.12+ | `python3 --version` |
| `uv` or `pip` | `uv --version` or `pip --version` |

Windows users: use WSL or PowerShell (native Windows is supported but not the primary beta target).

## 1.2 Install — The One Command

```bash
# Option A: uv (recommended — fast, isolated)
uv tool install mutsumi-tui

# Option B: pip
pip install mutsumi-tui

# Option C: from source (for contributors)
uv tool install git+https://github.com/ywh555hhh/Mutsumi.git
```

### Validation Checklist — Install

| # | Step | Expected | Pass? |
|---|------|----------|-------|
| 1.2.1 | Run `mutsumi --version` | Prints `mutsumi, version 1.0.0b1` | [ ] |
| 1.2.2 | Run `mutsumi --help` | Shows help text with subcommands | [ ] |
| 1.2.3 | Install time | < 15 seconds (uv) / < 30 seconds (pip) | [ ] |
| 1.2.4 | No compilation step | Pure Python, no C extensions to build | [ ] |

## 1.3 First Launch — Onboarding

```bash
cd ~/some-project   # or any directory
mutsumi
```

Since this is the first launch, Mutsumi shows a **single-page onboarding screen**.

### What You Should See

```
┌─────────────────────────────────────────────────────────┐
│               Welcome to Mutsumi                        │
│      Your silent task board is ready to set up.          │
│                                                         │
│  Language       ● English  ○ 中文  ○ 日本語             │
│                                                         │
│  Keybindings    ● Arrows  ○ Vim  ○ Emacs                │
│                                                         │
│  Theme          ● Monochrome Zen  ○ Nord  ○ Dracula     │
│                 ○ Solarized                              │
│                                                         │
│  Workspace      ○ Personal only  ○ Project only         │
│                 ● Personal + Project                     │
│                                                         │
│  Agent          ○ Claude Code  ○ Codex CLI               │
│                 ○ Gemini CLI   ○ OpenCode  ● Skip        │
│                                                         │
│           [Start Mutsumi]           [Skip]               │
└─────────────────────────────────────────────────────────┘
```

### Validation Checklist — Onboarding

| # | Step | Expected | Pass? |
|---|------|----------|-------|
| 1.3.1 | First `mutsumi` shows onboarding | Single-page form, not a multi-step wizard | [ ] |
| 1.3.2 | All 5 settings visible at once | Language, Keybindings, Theme, Workspace, Agent | [ ] |
| 1.3.3 | Arrow keys navigate between RadioButtons | No crashes, smooth focus movement | [ ] |
| 1.3.4 | Select "中文" → click "Start Mutsumi" | UI immediately shows Chinese labels | [ ] |
| 1.3.5 | Select "Nord" theme → click Start | Colors change immediately (blue-ish Nord palette) | [ ] |
| 1.3.6 | Select "Vim" keybindings → Start | `j`/`k` work for navigation after entering TUI | [ ] |
| 1.3.7 | Select "Claude Code" agent → Start | Skill file created at `~/.claude/skills/mutsumi-*/SKILL.md` | [ ] |
| 1.3.8 | Click "Skip" button | Enters TUI with all defaults, no crash | [ ] |
| 1.3.9 | After onboarding, Main tab is visible | Multi-source tabs: `[★ Main] [Personal] ...` | [ ] |
| 1.3.10 | Second launch skips onboarding | Goes directly to TUI | [ ] |
| 1.3.11 | Total time from command to TUI | < 5 seconds (including onboarding interaction) | [ ] |

## 1.4 First Interaction — The Empty Board

After onboarding, you land on the main task board. It's empty — and that's fine.

### Validation Checklist — Empty State

| # | Step | Expected | Pass? |
|---|------|----------|-------|
| 1.4.1 | Empty state shows a helpful message | "Nothing here yet" + `[+ New Task]` button | [ ] |
| 1.4.2 | Click `[+ New Task]` button | Task creation form opens | [ ] |
| 1.4.3 | Type a title → click Create | Task appears in the list immediately | [ ] |
| 1.4.4 | Press `n` (or arrows-preset equivalent) | Task creation form opens via keyboard | [ ] |
| 1.4.5 | Click task checkbox | Task toggles to done | [ ] |
| 1.4.6 | Press `?` | Help screen shows all keybindings | [ ] |

## 1.5 Aha 1 — Summary Criteria

**Pass condition**: A tester with no prior knowledge of Mutsumi can go from `uv tool install mutsumi-tui` to seeing their first task on screen in under 60 seconds, without reading any documentation.

---

# Aha 2: Agent Live Sync

**Promise**: You talk to your AI agent in natural language. The agent writes JSON. Mutsumi hot-reloads. Your task board updates before you finish reading the agent's response.

## 2.0 Setup — Split Terminal

You need two panes side by side:

```
┌──────────────────────────┬──────────────────────────┐
│                          │                          │
│   AI Agent               │   Mutsumi TUI            │
│   (Claude Code, etc.)    │                          │
│                          │                          │
└──────────────────────────┴──────────────────────────┘
```

### Quick Setup

```bash
# tmux (recommended)
tmux new-session -d -s dev
tmux split-window -h -p 35 "mutsumi"
tmux select-pane -t 0
tmux attach -t dev

# iTerm2
# Cmd+D to split → right pane: mutsumi → left pane: your agent

# VS Code / Cursor
# Split terminal → right: mutsumi → left: agent
```

## 2.1 Agent Knows Mutsumi — Skill Injection

The agent needs to know Mutsumi's JSON protocol. This happens automatically if the user selected an agent during onboarding, or can be done manually:

```bash
# Auto-inject (writes SKILL.md to agent's skill directory)
mutsumi setup --agent claude-code
mutsumi setup --agent codex-cli
mutsumi setup --agent gemini-cli
mutsumi setup --agent opencode

# Check it worked
ls ~/.claude/skills/mutsumi-*/SKILL.md    # Claude Code
ls ~/.codex/skills/mutsumi-*/SKILL.md     # Codex CLI
```

### Validation Checklist — Skill Injection

| # | Step | Expected | Pass? |
|---|------|----------|-------|
| 2.1.1 | `mutsumi setup --agent claude-code` | Prints success, creates skill file | [ ] |
| 2.1.2 | Agent session reads the skill | Agent knows `mutsumi.json` schema without prompting | [ ] |
| 2.1.3 | Running setup twice | Idempotent, no duplicate files | [ ] |
| 2.1.4 | `mutsumi setup` (no flag) | Lists available agents | [ ] |

## 2.2 The Core Loop — Talk → Write → See

This is the money shot. The tester should feel the magic here.

### Scenario A: Add a task casually

```
You (to agent): "帮我加个 todo，明天交周报"
```

Agent should:
1. Read `mutsumi.json` (or know the schema from skill)
2. Add a new task with title "明天交周报", scope "day", reasonable priority
3. Write the file back atomically

Mutsumi should:
- Detect the file change via watchdog (< 200ms)
- Re-render the task list
- New task appears with no flicker, no restart

### Scenario B: Batch operations

```
You (to agent): "把这三个 bug 都加进去：登录页白屏、支付超时、头像上传失败，都是 high priority"
```

Agent writes 3 tasks at once. Mutsumi shows all 3 after a single re-render.

### Scenario C: Mark done

```
You (to agent): "登录页白屏修好了，帮我标记完成"
```

Agent sets `status: "done"`. Mutsumi shows the checkbox checked, task grayed out.

### Scenario D: Edit and reorganize

```
You (to agent): "把支付超时的优先级降到 normal，加个 tag 叫 backend"
```

Agent updates fields. Mutsumi re-renders with new priority stars and tag.

### Validation Checklist — Live Sync

| # | Step | Expected | Pass? |
|---|------|----------|-------|
| 2.2.1 | Agent adds 1 task | Appears in Mutsumi within 1 second | [ ] |
| 2.2.2 | Agent adds 3 tasks at once | All 3 appear after single re-render | [ ] |
| 2.2.3 | Agent marks task done | Checkbox + strikethrough update immediately | [ ] |
| 2.2.4 | Agent edits priority | Priority stars change immediately | [ ] |
| 2.2.5 | Agent edits tags | Tags column updates immediately | [ ] |
| 2.2.6 | Agent adds subtask (children) | Indented child appears under parent | [ ] |
| 2.2.7 | Agent deletes a task | Task disappears from list | [ ] |
| 2.2.8 | Agent writes invalid JSON | Mutsumi shows error banner, does NOT crash | [ ] |
| 2.2.9 | Agent fixes JSON back to valid | Error banner clears, tasks re-appear | [ ] |
| 2.2.10 | No flicker during any update | Cursor position preserved, no full-screen flash | [ ] |
| 2.2.11 | Unknown fields preserved | Agent adds `"effort": "2h"` → Mutsumi keeps it on next write | [ ] |

## 2.3 Reverse Direction — TUI → JSON → Agent

The sync is bidirectional. When the user interacts with Mutsumi, the JSON updates, and the agent can read the latest state.

| # | Step | Expected | Pass? |
|---|------|----------|-------|
| 2.3.1 | Toggle done in TUI | `mutsumi.json` updates, agent can see the change | [ ] |
| 2.3.2 | Create task in TUI (press `n`) | New task written to JSON, agent can read it | [ ] |
| 2.3.3 | Delete task in TUI | Task removed from JSON | [ ] |
| 2.3.4 | Edit task title inline | JSON updated atomically | [ ] |

## 2.4 Aha 2 — Summary Criteria

**Pass condition**: A tester casually tells their agent "加几个 todo" while Mutsumi is open in a split pane. The tasks appear on screen before the agent finishes printing its response. The tester's reaction: "哦这也太爽了吧"。

---

# Pre-Release Checklist

Everything below must be green before tagging `v1.0.0-beta.1`.

## Code Quality

| # | Item | Status |
|---|------|--------|
| C1 | All tests pass (`pytest tests/ -v`) | [ ] |
| C2 | No hardcoded monochrome-zen colors in DEFAULT_CSS | [ ] |
| C3 | All major TUI strings use i18n (`get_i18n().t()`) | [ ] |
| C4 | Theme switching works (onboarding + config change) | [ ] |
| C5 | i18n switching works (en → zh → ja) | [ ] |
| C6 | Keybinding switching works (arrows / vim / emacs) | [ ] |
| C7 | Onboarding hot-reload: all settings apply immediately | [ ] |
| C8 | Main tab visible after first onboarding | [ ] |
| C9 | File watcher: stable over 10+ minutes | [ ] |
| C10 | Atomic writes: no partial JSON corruption | [ ] |

## Packaging

| # | Item | Status |
|---|------|--------|
| P1 | `pyproject.toml` version = `1.0.0b1` | [ ] |
| P2 | `uv tool install mutsumi-tui` works from PyPI | [ ] |
| P3 | `pip install mutsumi-tui` works | [ ] |
| P4 | `mutsumi` command available after install | [ ] |
| P5 | No unnecessary files in sdist (docs/, tests/, .claude/) | [ ] |
| P6 | Python 3.12+ requirement enforced | [ ] |

## Documentation

| # | Item | Status |
|---|------|--------|
| D1 | This playbook (BETA_V1.md) — complete | [ ] |
| D2 | Chinese version (BETA_V1_cn.md) — complete | [ ] |
| D3 | README.md — updated for v1.0.0 | [ ] |
| D4 | AGENT.md — updated JSON schema (mutsumi.json) | [ ] |
| D5 | CHANGELOG.md — v1.0.0-beta.1 entry | [ ] |

## Platform Testing

| # | Platform | Tester | Pass? |
|---|----------|--------|-------|
| T1 | macOS + iTerm2 | Wayne | [ ] |
| T2 | macOS + tmux | | [ ] |
| T3 | Ubuntu + tmux | | [ ] |
| T4 | Windows WSL | | [ ] |
| T5 | VS Code integrated terminal | | [ ] |
| T6 | Cursor integrated terminal | | [ ] |

## Agent Compatibility

| # | Agent | Skill injection | Live sync | Pass? |
|---|-------|----------------|-----------|-------|
| A1 | Claude Code | [ ] | [ ] | [ ] |
| A2 | Codex CLI | [ ] | [ ] | [ ] |
| A3 | Gemini CLI | [ ] | [ ] | [ ] |
| A4 | OpenCode | [ ] | [ ] | [ ] |
| A5 | Manual (no skill) | N/A | [ ] | [ ] |

---

# Known Issues / Blockers

Track blockers here during beta testing. Each must be resolved before GA.

| # | Issue | Severity | Status |
|---|-------|----------|--------|
| | | | |

---

# Beta Timeline

| Milestone | Target Date | Owner |
|-----------|-------------|-------|
| Code freeze (all features complete) | | Wayne |
| Internal dogfooding (Wayne solo) | | Wayne |
| v1.0.0-beta.1 tag + PyPI publish | | Wayne |
| Friend beta (3-5 testers) | | Wayne |
| Bug fix sprint | | Wayne |
| v1.0.0 GA release | | Wayne |

---

# Feedback Template

Beta testers: copy this template when reporting.

```markdown
## Environment
- OS:
- Terminal:
- Python version:
- Install method: uv / pip / source
- Agent (if testing Aha 2):

## Aha 1 (Out-of-the-Box)
- Install time:
- Onboarding: smooth / had issues
- First task created: yes / no
- Overall feeling (1-5):
- Issues:

## Aha 2 (Agent Live Sync)
- Agent used:
- Split pane method: tmux / iTerm2 / VS Code / other
- Add task via agent: worked / failed
- Hot-reload speed: instant / noticeable delay / broken
- Overall feeling (1-5):
- Issues:

## General
- Would you use this daily? yes / maybe / no
- What surprised you (good or bad)?
- What's missing?
```

---

*mutsumi — "harmony, closeness". She doesn't tell you what to do. She just waits quietly, and updates when you're ready.*
