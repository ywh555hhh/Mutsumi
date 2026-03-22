# Mutsumi Development Roadmap

> **[中文版](./ROADMAP_cn.md)** | **[日本語版](./ROADMAP_ja.md)**

| Status  | Living Document     |
|---------|---------------------|
| Date    | 2026-03-22          |

---

## Phase Overview

```
Phase 0          Phase 1          Phase 2          Phase 3          Phase 3.5
Foundations      Skeleton         Reactivity       CLI & Polish     Friend Beta
────────────     ────────────     ────────────     ────────────     ────────────
docs & specs     static TUI       hot-reload       CLI CRUD         AGENT.md
project setup    tab switching    file watcher     i18n             setup command
data model       task list        click → JSON     themes           tmux scripts
                 detail panel     JSON → re-draw   config system    beta packaging

Phase 5          Phase 4
Multi-Source     Launch
────────────     ────────────
file rename      README
multi-source     GIF demo
project CLI      Product Hunt
tab redesign     community
dashboard
```

---

## Phase 0: Foundations ✅

**Goal**: Complete all design documents, set up project skeleton. Zero-code phase.

- [x] Vision Document
- [x] RFC-001: Core Architecture
- [x] Data Contract Spec (`DATA_CONTRACT.md`)
- [x] Agent Integration Protocol (`AGENT_PROTOCOL.md`)
- [x] TUI Specification (`TUI_SPEC.md`)
- [x] Brand Identity (`BRAND.md`)
- [x] Roadmap (this document)
- [x] `uv init` project skeleton
- [x] `pyproject.toml` dependency declaration
- [x] Sample `tasks.json` (fixture)
- [x] `CLAUDE.md` project-level dev conventions
- [x] CI: GitHub Actions (lint + type check)

**Exit Criteria**: `uv run mutsumi` can launch a blank Textual window and exit cleanly.

---

## Phase 1: Skeleton ✅

**Goal**: Render a static TUI that reads `tasks.json` and displays tasks, without reacting to external changes.

- [x] Textual App base framework (`app.py`)
- [x] Header widget: Tab switching (Today / Week / Month / Inbox)
- [x] TaskList widget: Group by priority
- [x] TaskRow widget: checkbox + title + tags + priority stars
- [x] Footer widget: Task statistics
- [x] Data layer: pydantic model for Task schema
- [x] Data layer: Parse `tasks.json`
- [x] Basic keyboard navigation: `j/k` up/down, `q` quit
- [x] Sub-task rendering: indented children (max 3 levels)
- [x] Empty state placeholder page

**Exit Criteria**: Manually create a `tasks.json`, `uv run mutsumi` correctly renders all tasks.

---

## Phase 2: Reactivity ✅

**Goal**: Implement bidirectional data flow — external JSON changes trigger TUI re-render, and TUI interactions write back to JSON.

- [x] watchdog integration: monitor `tasks.json` for changes
- [x] Debounce mechanism (100ms)
- [x] Hot-reload: JSON change → flicker-free TUI re-render
- [x] Mouse click checkbox → toggle status → write back JSON
- [x] Atomic write (temp file + `os.rename`)
- [x] Schema validation: invalid JSON → error banner
- [x] Error state: graceful degradation for missing/malformed files
- [x] Detail panel: `Enter` to expand task details
- [x] End-to-end scenario: Agent writes JSON in another terminal → TUI auto-refreshes

**Exit Criteria**: Record a 10-second GIF: Mutsumi running on the left, JSON being edited on the right, left side refreshes instantly.

---

## Phase 3: CLI & Polish ✅

**Goal**: Flesh out CLI sub-commands, CRUD interactions, and configuration system.

- [x] TUI CRUD: `n` new / `e` edit / `dd` delete
- [x] CLI: `mutsumi add` / `list` / `done` / `rm` / `edit`
- [x] CLI: `mutsumi init` — generate template `tasks.json`
- [x] CLI: `mutsumi validate` — validate file
- [x] CLI: `mutsumi schema` — output JSON Schema
- [x] Config system: `~/.config/mutsumi/config.toml`
- [x] Theme system: 4 built-in themes + custom theme loading
- [x] Key bindings: vim / emacs / arrow presets
- [x] i18n: `en` + `zh` + `ja` trilingual
- [x] Search: `/` triggers real-time search filter
- [x] Event log: TUI actions → append to `events.jsonl`
- [x] Multi-project: `--watch` aggregate multiple paths
- [x] `mutsumi --version` / `--help`

**Exit Criteria**: After `uv tool install mutsumi`, a new user can complete the full workflow within 2 minutes.

---

## Phase 3.5: Friend Beta ✅

**Goal**: Prepare for small-scale friend beta — any agent can learn to control Mutsumi in 2 minutes.

- [x] `AGENT.md` — one-page agent cheat sheet (schema, CLI, JSON protocol)
- [x] `examples/` — sample `config.toml` and `tasks.json`
- [x] `mutsumi setup --agent` — inject integration instructions into agent config files
- [x] `scripts/tmux-dev.sh` — one-command tmux split-pane setup
- [x] `scripts/demo.sh` — demo script showing live-reload
- [x] Version bump to `0.4.0b1`
- [x] README: Terminal Integration section (tmux + iTerm2)
- [x] `pyproject.toml`: Beta classifier

**Exit Criteria**: A friend can `uv tool install git+...`, run `mutsumi setup --agent claude-code`, and start using Mutsumi within 2 minutes.

---

## Phase 5: Multi-Source Hub ✅ (Current)

**Goal**: Upgrade Mutsumi from a single-file task viewer to a personal command center — global personal todo + multi-project Agent dashboard + aggregated Main tab.

- [x] **5a** — File rename: `tasks.json` → `mutsumi.json` with backward-compatible fallback
- [x] **5f** — Config migration: `~/.config/mutsumi/` → `~/.mutsumi/` unified home
- [x] **5b** — Multi-Source data layer: `SourceRegistry` managing N data sources
- [x] **5c** — Project Registry CLI: `mutsumi project add/remove/list`
- [x] **5d** — Tab redesign: dynamic source tabs + scope sub-filter
- [x] **5e** — Main Dashboard: aggregated progress view across all sources

**Exit Criteria**: `uv run mutsumi` with multiple registered projects shows a dashboard on the Main tab, individual source tabs with scope filtering, and all 239 tests pass.

---

## Phase 4: Launch (Next)

**Goal**: Polish all release materials and sprint for a Product Hunt launch.

- [ ] README.md: A compelling product introduction
- [ ] README "Pro Workflow" section (Typeless voice workflow)
- [ ] README "Layout Gallery" section (layout screenshots)
- [ ] Record Hero GIF: Claude Code + Mutsumi split-screen collaboration
- [ ] Record Bonus GIF: Typeless voice → Agent → Mutsumi refresh
- [ ] Product Hunt page copy
- [ ] Publish to PyPI
- [ ] GitHub Release v0.5.0
- [ ] Hacker News / Reddit /r/commandline post
- [ ] V2EX post
- [ ] Community template collection: users show their tmux/zellij layouts

**Exit Criteria**: Product Hunt page is live, GitHub receives its first batch of stars.

---

## Future (Post-Launch Ideas)

The following features are outside the MVP scope. Listed here for reference only.

| Feature              | Description                                              | Priority |
|----------------------|----------------------------------------------------------|----------|
| Plugin system        | Users can write custom view widgets                      | P2       |
| Task templates       | Daily standup / weekly report templates                  | P2       |
| Archive              | Auto-archive completed tasks to `archive.json`           | P2       |
| Pomodoro timer       | Built-in Pomodoro timer linked to tasks                  | P3       |
| Git sync             | Auto Git commit for `tasks.json`                         | P3       |
| Calendar view        | Calendar display for tasks with `due_date`               | P3       |
| Dashboard widgets    | Completion charts, daily trends                          | P3       |
| Web companion        | Read-only web UI (view only, no interaction)             | P3       |
| Taskwarrior import   | Import existing tasks from Taskwarrior                   | P3       |
| Markdown tasks       | Support `tasks.md` as an alternative data source         | P3       |

---

## Versioning Strategy

| Version | Milestone                                          |
|---------|----------------------------------------------------|
| 0.1.0   | Phase 1 complete — static rendering usable         |
| 0.2.0   | Phase 2 complete — hot-reload + interaction        |
| 0.3.0   | Phase 3 complete — CLI + config complete           |
| 0.4.0b1 | Phase 3.5 complete — Friend Beta                   |
| 0.6.0   | Phase 5 complete — Multi-Source Hub                |
| 0.5.0   | Phase 4 complete — Product Hunt launch build       |
| 1.0.0   | Stable release after community feedback            |
