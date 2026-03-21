# Mutsumi Development Roadmap

> **[中文版](./ROADMAP_cn.md)** | **[日本語版](./ROADMAP_ja.md)**

| Status  | Living Document     |
|---------|---------------------|
| Date    | 2026-03-21          |

---

## Phase Overview

```
Phase 0          Phase 1          Phase 2          Phase 3          Phase 4
Foundations      Skeleton         Reactivity       CLI & Polish      Launch
────────────     ────────────     ────────────     ────────────     ────────────
docs & specs     static TUI       hot-reload       CLI CRUD         README
project setup    tab switching    file watcher     i18n             GIF demo
data model       task list        click → JSON     themes           Product Hunt
                 detail panel     JSON → re-draw   config system    community
```

---

## Phase 0: Foundations (Current)

**Goal**: Complete all design documents, set up project skeleton. Zero-code phase.

- [x] Vision Document
- [x] RFC-001: Core Architecture
- [x] Data Contract Spec (`DATA_CONTRACT.md`)
- [x] Agent Integration Protocol (`AGENT_PROTOCOL.md`)
- [x] TUI Specification (`TUI_SPEC.md`)
- [x] Brand Identity (`BRAND.md`)
- [x] Roadmap (this document)
- [ ] `uv init` project skeleton
- [ ] `pyproject.toml` dependency declaration
- [ ] Sample `tasks.json` (fixture)
- [ ] `CLAUDE.md` project-level dev conventions
- [ ] CI: GitHub Actions (lint + type check)

**Exit Criteria**: `uv run mutsumi` can launch a blank Textual window and exit cleanly.

---

## Phase 1: Skeleton

**Goal**: Render a static TUI that reads `tasks.json` and displays tasks, without reacting to external changes.

- [ ] Textual App base framework (`app.py`)
- [ ] Header widget: Tab switching (Today / Week / Month / Inbox)
- [ ] TaskList widget: Group by priority
- [ ] TaskRow widget: checkbox + title + tags + priority stars
- [ ] Footer widget: Task statistics
- [ ] Data layer: pydantic model for Task schema
- [ ] Data layer: Parse `tasks.json`
- [ ] Basic keyboard navigation: `j/k` up/down, `q` quit
- [ ] Sub-task rendering: indented children (max 3 levels)
- [ ] Empty state placeholder page

**Exit Criteria**: Manually create a `tasks.json`, `uv run mutsumi` correctly renders all tasks.

---

## Phase 2: Reactivity

**Goal**: Implement bidirectional data flow — external JSON changes trigger TUI re-render, and TUI interactions write back to JSON.

- [ ] watchdog integration: monitor `tasks.json` for changes
- [ ] Debounce mechanism (100ms)
- [ ] Hot-reload: JSON change → flicker-free TUI re-render
- [ ] Mouse click checkbox → toggle status → write back JSON
- [ ] Atomic write (temp file + `os.rename`)
- [ ] Schema validation: invalid JSON → error banner
- [ ] Error state: graceful degradation for missing/malformed files
- [ ] Detail panel: `Enter` to expand task details
- [ ] End-to-end scenario: Agent writes JSON in another terminal → TUI auto-refreshes

**Exit Criteria**: Record a 10-second GIF: Mutsumi running on the left, JSON being edited on the right, left side refreshes instantly.

---

## Phase 3: CLI & Polish

**Goal**: Flesh out CLI sub-commands, CRUD interactions, and configuration system.

- [ ] TUI CRUD: `n` new / `e` edit / `dd` delete
- [ ] CLI: `mutsumi add` / `list` / `done` / `rm` / `edit`
- [ ] CLI: `mutsumi init` — generate template `tasks.json`
- [ ] CLI: `mutsumi validate` — validate file
- [ ] CLI: `mutsumi schema` — output JSON Schema
- [ ] Config system: `~/.config/mutsumi/config.toml`
- [ ] Theme system: 4 built-in themes + custom theme loading
- [ ] Key bindings: vim / emacs / arrow presets
- [ ] i18n: `en` + `zh` bilingual
- [ ] Search: `/` triggers real-time search filter
- [ ] Event log: TUI actions → append to `events.jsonl`
- [ ] Multi-project: `--watch` aggregate multiple paths
- [ ] `mutsumi --version` / `--help`

**Exit Criteria**: After `uv tool install mutsumi`, a new user can complete the full workflow within 2 minutes.

---

## Phase 4: Launch

**Goal**: Polish all release materials and sprint for a Product Hunt launch.

- [ ] README.md: A compelling product introduction
- [ ] README "Pro Workflow" section (Typeless voice workflow)
- [ ] README "Layout Gallery" section (layout screenshots)
- [ ] Record Hero GIF: Claude Code + Mutsumi split-screen collaboration
- [ ] Record Bonus GIF: Typeless voice → Agent → Mutsumi refresh
- [ ] Product Hunt page copy
- [ ] Publish to PyPI
- [ ] GitHub Release v0.1.0
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
| 0.5.0   | Phase 4 complete — Product Hunt launch build       |
| 1.0.0   | Stable release after community feedback            |
