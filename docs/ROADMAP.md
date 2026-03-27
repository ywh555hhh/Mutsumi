# Mutsumi Development Roadmap

> **[中文版](./ROADMAP_cn.md)** | **[日本語版](./ROADMAP_ja.md)**

| Status | Living Document |
|---|---|
| Date | 2026-03-25 |
| Current Beta | `1.1.0b1` |

---

## Product State

Mutsumi is currently in the **`1.1.0b1` beta** phase.

What is already real in this beta:

- canonical task file: `mutsumi.json`
- legacy fallback: `tasks.json`
- default keybinding preset: `arrows`
- semantic-first interaction layer (`confirm` / `back` / `create` / `edit`)
- layered close ordering for confirm/search/detail interactions
- multi-source hub: Main + Personal + project tabs
- source-aware task creation (`source/project -> scope -> task fields`)
- first-run onboarding with immediate preset hot-reload
- skills-first agent setup

What is **not** shipped yet:

- built-in calendar UI
- plugin system
- web companion

Calendar is now tracked as a planned feature via **RFC-009**.

---

## Phase Overview

```text
Phase 0   Foundations
Phase 1   Static TUI
Phase 2   Reactivity
Phase 3   CLI & Polish
Phase 3.5 Friend Beta
Phase 5   Multi-Source Hub
Phase 8   Out-of-Box Onboarding
Phase 9   Calendar View (planned)
Phase 10  Launch / GA polish
```

---

## Phase 0: Foundations ✅

**Goal**: establish the product model, specs, and initial project skeleton.

- [x] Vision and architecture docs
- [x] RFC-001: Core Architecture
- [x] Data Contract spec
- [x] Agent Integration Protocol
- [x] TUI spec
- [x] Brand identity
- [x] Roadmap
- [x] `uv` project setup
- [x] sample fixture task file
- [x] project development rules (`CLAUDE.md`)
- [x] CI baseline

**Exit criteria**: `uv run mutsumi` can launch a blank Textual window cleanly.

---

## Phase 1: Skeleton ✅

**Goal**: render a static task board from local JSON.

- [x] Textual app shell
- [x] task list rendering
- [x] priority grouping
- [x] task row UI
- [x] footer statistics
- [x] task schema models
- [x] file parsing
- [x] basic keyboard navigation
- [x] nested child rendering
- [x] empty state

**Exit criteria**: a local task file renders correctly in the TUI.

---

## Phase 2: Reactivity ✅

**Goal**: external file changes and local interactions both update the board correctly.

- [x] watchdog file watching
- [x] debounce
- [x] hot reload
- [x] checkbox click → JSON write-back
- [x] atomic file writes
- [x] invalid JSON → error banner
- [x] graceful degradation
- [x] detail panel
- [x] end-to-end agent write → TUI refresh flow

**Exit criteria**: the board refreshes live when the task file changes.

---

## Phase 3: CLI & Polish ✅

**Goal**: provide a usable local product loop, not just a demo UI.

- [x] TUI CRUD
- [x] CLI CRUD: `add`, `list`, `done`, `rm`, `edit`
- [x] `mutsumi init`
- [x] `mutsumi validate`
- [x] `mutsumi schema`
- [x] theme system
- [x] i18n (`en`, `zh`, `ja`)
- [x] config system
- [x] search
- [x] local event logging
- [x] version / help output

**Exit criteria**: a new user can install and complete the basic local workflow quickly.

---

## Phase 3.5: Friend Beta ✅

**Goal**: make agent-driven usage understandable for early testers.

- [x] `AGENT.md`
- [x] sample fixtures
- [x] `mutsumi setup --agent`
- [x] split-pane helper scripts
- [x] demo script
- [x] beta packaging work
- [x] early beta docs

**Historical note**: this phase introduced the earlier friend-beta line. The current product has moved forward beyond that stage.

---

## Phase 5: Multi-Source Hub ✅

**Goal**: turn Mutsumi from a single-project viewer into a multi-source command center.

- [x] rename `tasks.json` → `mutsumi.json` with compatibility fallback
- [x] unify home directory around `~/.mutsumi/`
- [x] multi-source registry and watchers
- [x] project registration CLI
- [x] source-tab redesign
- [x] Main dashboard aggregation

**Exit criteria**: Mutsumi can aggregate personal and project task files in one UI.

---

## Phase 8: Out-of-Box Onboarding ✅

**Goal**: make `mutsumi` the natural entrypoint.

- [x] first-run onboarding flow
- [x] onboarding-based preference capture
- [x] lightweight project attach flow
- [x] skills-first agent integration path
- [x] auto-creation of Mutsumi-owned files when appropriate
- [x] onboarding completion immediately hot-reloads theme, i18n, and keybinding preset

**Exit criteria**: first launch succeeds without the user needing to learn a setup graph first.

---

## Phase 9: Calendar View (Planned)

**Goal**: add a built-in calendar surface for time-based navigation of existing tasks.

Design authority:

- [x] RFC-009: Calendar View

Planned implementation slices:

- [ ] Main-layer calendar mode
- [ ] month / agenda foundation
- [ ] date drill-down into task detail
- [ ] source-aware calendar aggregation
- [ ] lightweight date-based create/edit flows
- [ ] richer week/day interactions

Scope notes:

- calendar reuses `due_date`
- calendar does not introduce a second task model
- calendar is planned, not shipped in the current `1.1.0b1` beta line

---

## Phase 10: Launch / GA Polish (Next)

**Goal**: polish the product, docs, packaging, and marketing surfaces for broader release.

- [ ] finalize English-facing docs for the beta/GA path
- [ ] record polished demo assets
- [ ] publish / verify PyPI install flow for `mutsumi-tui`
- [ ] tighten beta testing checklist and feedback loop
- [ ] close remaining UX/documentation gaps before GA
- [ ] prepare launch copy and release materials

**Exit criteria**: installation, onboarding, agent setup, and day-to-day usage all feel coherent enough for broader public release.

---

## Future Ideas (Post-GA / Unscheduled)

These are ideas, not committed roadmap promises.

| Feature | Description | Priority |
|---|---|---|
| Plugin system | User-defined widgets or extensions | P2 |
| Task templates | Reusable recurring task setups | P2 |
| Archive | Move completed tasks out of the active file | P2 |
| Pomodoro timer | Task-linked focus timer | P3 |
| Git sync helper | Optional Git-based task-file workflow | P3 |
| Dashboard widgets | Additional charts or summaries | P3 |
| Web companion | Read-only web surface | P3 |
| Taskwarrior import | Import from existing systems | P3 |
| Markdown tasks | Support a markdown-based source format | P3 |

---

## Versioning Strategy

| Version | Meaning |
|---|---|
| `0.1.x` | static rendering baseline |
| `0.2.x` | reactivity baseline |
| `0.3.x` | CLI/config baseline |
| `0.4.0b1` | earlier friend-beta milestone |
| `1.0.0b1` | integrated beta before RFC-010 interaction convergence |
| `1.1.0b1` | current semantic-first beta line |
| `1.0.0` | stable release target after beta hardening |

---

## Beta Guidance

For the current cycle, the important source of truth is:

- current beta version: **`1.1.0b1`**
- canonical task file: **`mutsumi.json`**
- default preset: **`arrows`**
- semantic-first interaction is shipped in the beta line
- calendar status: **planned via RFC-009, not yet shipped**
