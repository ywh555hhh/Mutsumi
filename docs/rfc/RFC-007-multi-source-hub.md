# RFC-007: Multi-Source Hub — From Tool to Command Center

> **[中文版](./RFC-007-multi-source-hub_cn.md)** | **[日本語版](./RFC-007-multi-source-hub_ja.md)**

| Field       | Value                                          |
|-------------|------------------------------------------------|
| **RFC**     | 007                                            |
| **Title**   | Multi-Source Hub: Personal Todo + Multi-Project Agent Dashboard |
| **Status**  | Draft                                          |
| **Author**  | Wayne (ywh)                                    |
| **Created** | 2026-03-22                                     |

---

## Abstract

Mutsumi currently watches a single `tasks.json` in the working directory — one project, one file, one view. This RFC proposes evolving Mutsumi from a **single-project task viewer** into a **personal command center** that aggregates:

1. **A global personal todo list** — your life tasks, not tied to any project
2. **Multiple project dashboards** — each driven by an Agent writing to its own `mutsumi.json`
3. **A Main tab** — a unified at-a-glance view showing what matters most right now

This is the natural upgrade from "tool" to "hub".

## 1. Motivation

### 1.1 The Two-Scatter Problem

Independent developers and multi-project users face two kinds of scatter:

| Scatter | Current State | Pain |
|---------|---------------|------|
| **Personal todos** | Todoist, Obsidian, sticky notes, brain | Context-switching to check personal tasks breaks flow |
| **Agent project progress** | Each project directory has its own terminal | Vibe-coding 3 projects? Open 3 terminals, `cd` 3 times, check 3 files |

Mutsumi already solves the "Agent → visual feedback" loop for a single project. But the moment you run 2+ projects concurrently, the value drops — you're back to tab-switching.

### 1.2 Core Insight

> **The real bottleneck is not managing tasks within a project — it's seeing ALL your threads at once.**

A developer running Claude Code on project-A, Codex on project-B, and personally tracking "reply to advisor's email" needs ONE place to glance at. Not three terminals. Not a browser tab. One TUI.

### 1.3 Positioning Shift

| Before | After |
|--------|-------|
| "External display for one Agent session" | "Personal command center for your entire workload" |
| Single-project viewer | Multi-source aggregator |
| `tasks.json` in cwd | Global `mutsumi.json` + per-project `mutsumi.json` |

## 2. Design

### 2.1 File Rename: `tasks.json` → `mutsumi.json`

The data file is renamed to `mutsumi.json` for:
- **Brand identity**: Clear ownership, avoids collision with other tools' `tasks.json`
- **Discoverability**: Seeing `mutsumi.json` in a project immediately signals "this project uses Mutsumi"
- **Multi-source clarity**: When watching multiple files, the name makes intent obvious

**Migration**: Mutsumi auto-detects and reads `tasks.json` as a fallback. A `mutsumi migrate` command renames `tasks.json` → `mutsumi.json` in-place.

Schema remains **identical** — only the filename changes. The `version` field stays at `1`.

### 2.2 Data Architecture: Global + Per-Project

```
~/.mutsumi/                          ← Platform-aware (APPDATA on Windows)
├── mutsumi.json                     ← Personal global tasks
└── config.toml                      ← Moves here from ~/.config/mutsumi/

~/Code/project-a/
└── mutsumi.json                     ← Agent-driven project tasks

~/Code/project-b/
└── mutsumi.json                     ← Agent-driven project tasks
```

**Two categories of data sources:**

| Source | Location | Writer | Purpose |
|--------|----------|--------|---------|
| **Personal** | `~/.mutsumi/mutsumi.json` | User (TUI/CLI) | Life tasks, cross-project errands, personal reminders |
| **Project** | `<project-dir>/mutsumi.json` | Agent + User | Project-specific tasks driven by AI Agents |

Each file is an independent `mutsumi.json` with the same schema. No cross-file references. No shared state. Each file can be used standalone.

### 2.3 Project Registry

Projects are registered in `~/.mutsumi/config.toml`:

```toml
[[projects]]
name = "saas-app"
path = "~/Code/saas-app"

[[projects]]
name = "oshigrid"
path = "~/Code/oshigrid"

[[projects]]
name = "mutsumi"
path = "~/Code/Mutsumi"
```

**Registration methods:**

| Method | Command | Behavior |
|--------|---------|----------|
| CLI add | `mutsumi project add ~/Code/saas-app` | Register path, auto-create `mutsumi.json` if missing |
| CLI add with name | `mutsumi project add ~/Code/saas-app --name saas` | Register with custom display name |
| TUI add | `P` → folder picker / path input | Same as CLI, from within the TUI |
| CLI remove | `mutsumi project remove saas-app` | Unregister (does NOT delete `mutsumi.json`) |
| CLI list | `mutsumi project list` | Show all registered projects |

When a project is added:
1. Path is resolved to absolute and stored in config
2. If `mutsumi.json` doesn't exist at that path, create it with default empty template
3. Watchdog starts watching the new file immediately (if TUI is running)

### 2.4 Tab Structure

```
[★ Main]  [Personal]  [saas-app]  [oshigrid]  [mutsumi]
```

| Tab | Data Source | Content |
|-----|-------------|---------|
| **★ Main** | All sources aggregated | Dashboard: personal high-priority + per-project summary cards |
| **Personal** | `~/.mutsumi/mutsumi.json` | Full personal task list with day/week/month/inbox sub-filter |
| **\<project\>** | `<project>/mutsumi.json` | Full project task list with day/week/month/inbox sub-filter |

Tabs are **dynamic** — they appear/disappear as projects are registered/removed. The tab order follows config file order. Personal is always second (after Main).

#### 2.4.1 Main Tab Layout

The Main tab is a **read-only dashboard** — a glanceable summary of everything.

```
┌──────────────────────────────────────────────────────────┐
│  [★ Main]  [Personal]  [saas-app]  [oshigrid]  mutsumi  │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  ▸ Personal                                    2 tasks   │
│    ★★★ 写毕业论文 introduction                           │
│    ★★  回复导师邮件                                       │
│                                                          │
│  ▸ saas-app                              3/7 done  42%  │
│    ★★★ Fix auth token refresh                            │
│    ★★  Add rate limiting middleware                      │
│                                                          │
│  ▸ oshigrid                              1/4 done  25%  │
│    ★★★ Deploy staging environment                        │
│                                                          │
│  ▸ mutsumi                               5/5 done 100%  │
│    ✓ All tasks completed                                 │
│                                                          │
├──────────────────────────────────────────────────────────┤
│  16 tasks · 9 done · 7 pending · 4 sources    🔇 quiet  │
└──────────────────────────────────────────────────────────┘
```

**Main tab rules:**

1. Each project shows as a **collapsible section** with:
   - Project name + progress (`done/total` + percentage bar)
   - Top N highest-priority pending tasks (default N=3, configurable)
2. Personal section always appears first
3. Projects with all tasks done show a "✓ All tasks completed" summary
4. Clicking/pressing Enter on a project section → jumps to that project's tab
5. Main tab is **not editable** — task CRUD happens in the specific tabs

#### 2.4.2 Project Tab (and Personal Tab)

Within each tab, the existing time-based scope filter is preserved:

```
┌──────────────────────────────────────────────────────────┐
│  [★ Main]  [Personal]  [saas-app]  [oshigrid]  mutsumi  │
│            ──────────                                    │
│  Filter: [Today] [Week] [Month] [Inbox] [All]           │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  ▼ HIGH                                                  │
│  [ ] Fix auth token refresh           backend   ★★★     │
│  [ ] Patch SQL injection in /users    security  ★★★     │
│                                                          │
│  ▼ NORMAL                                                │
│  [ ] Add rate limiting middleware     backend   ★★      │
│  [x] Set up CI pipeline              devops    ★★      │
│                                                          │
├──────────────────────────────────────────────────────────┤
│  4 tasks · 1 done · 3 pending                  🔇 quiet │
└──────────────────────────────────────────────────────────┘
```

The scope filter (Today/Week/Month/Inbox) becomes a **sub-filter** within each tab, not a top-level tab. A new **[All]** option shows unfiltered tasks.

### 2.5 Input: Keyboard + Mouse Full Coverage

Every action is reachable by **both** keyboard and mouse. Mouse is a first-class citizen.

#### Tab Navigation

| Action | Keyboard | Mouse |
|--------|----------|-------|
| Jump to tab | `1-9` | Click tab |
| Previous / Next tab | `H` / `L` or `Shift+Tab` / `Tab` | Click tab |

#### Main Tab

| Action | Keyboard | Mouse |
|--------|----------|-------|
| Navigate sections | `↑` / `↓` | Scroll / Click section |
| Jump into project | `Enter` | Click project name or `→` button |
| Collapse/expand section | `←` / `→` | Click `▸` / `▾` chevron |
| Add new project | `P` | Click `[+ Project]` button in footer |

#### Project / Personal Tabs

| Action | Keyboard | Mouse |
|--------|----------|-------|
| Navigate tasks | `↑` / `↓` | Click task row |
| Toggle done | `Space` | Click checkbox |
| View detail | `Enter` | Click task title |
| New task | `n` | Click `[+ New]` button |
| Edit task | `e` | Double-click title |
| Delete task | `Delete` | Right-click → Delete |
| Cycle scope filter | `f` | Click filter chips (Today/Week/Month/Inbox/All) |
| Priority up/down | `+` / `-` | Click priority stars |
| Move task up/down | `Shift+↑` / `Shift+↓` | Drag & drop (future) |

#### Default Keybinding Preset: `arrows`

The default preset uses **arrow keys** — no vim knowledge required. Power users can switch to `vim` or `emacs` in config:

```toml
[keys]
preset = "arrows"   # default — arrow keys, Home/End, Shift+arrows
# preset = "vim"    # j/k/G/dd
# preset = "emacs"  # C-n/C-p/C-a/C-e
```

### 2.6 Config Migration

The config directory moves to consolidate with the personal data file:

| Before | After |
|--------|-------|
| `~/.config/mutsumi/config.toml` | `~/.mutsumi/config.toml` |
| `~/.config/mutsumi/themes/` | `~/.mutsumi/themes/` |
| (no personal tasks) | `~/.mutsumi/mutsumi.json` |

On Windows: `%APPDATA%\mutsumi\` (unchanged, already correct).

Mutsumi checks the old path as fallback and offers `mutsumi migrate` to move config.

### 2.7 Updated Config Schema

```toml
[general]
language = "auto"
default_tab = "main"              # Which tab to show on launch

[theme]
name = "monochrome-zen"

[keys]
preset = "vim"

[notifications]
mode = "quiet"

[dashboard]
max_tasks_per_project = 3         # How many top tasks to show on Main tab
show_completed_projects = true    # Show projects with 100% completion

[[projects]]
name = "saas-app"
path = "~/Code/saas-app"

[[projects]]
name = "oshigrid"
path = "~/Code/oshigrid"

[[projects]]
name = "mutsumi"
path = "~/Code/Mutsumi"
```

## 3. Agent Protocol Changes

### 3.1 File Name

Agents should write to `mutsumi.json` (not `tasks.json`). For backward compatibility, Mutsumi reads `tasks.json` if `mutsumi.json` is not found.

### 3.2 No Schema Changes

The `mutsumi.json` schema is **identical** to the current `tasks.json` schema. No fields are added or removed. The `scope` field retains its time-based semantics (day/week/month/inbox).

### 3.3 Agent Setup

The `mutsumi setup --agent` command is updated to reference `mutsumi.json`:

```
# In your project directory, create and manage tasks in mutsumi.json
# Schema: { "version": 1, "tasks": [...] }
# Mutsumi watches this file and renders a live TUI dashboard
```

### 3.4 Multi-Agent Isolation

Each project has its own `mutsumi.json`. Two Agents working on different projects **never** write to the same file — zero conflict by design.

```
Terminal 1: claude-code → writes ~/Code/saas-app/mutsumi.json
Terminal 2: codex       → writes ~/Code/oshigrid/mutsumi.json
Terminal 3: mutsumi     → watches both, renders unified view
```

## 4. CLI Changes

### 4.1 New `project` Command Group

```bash
mutsumi project add <path> [--name <display-name>]
mutsumi project remove <name>
mutsumi project list
```

### 4.2 Updated `init` Command

```bash
mutsumi init                    # Create mutsumi.json in cwd
mutsumi init --global           # Create ~/.mutsumi/mutsumi.json
mutsumi init --project <path>   # Create mutsumi.json + register project
```

### 4.3 Updated `add` / `list` / `done` Commands

```bash
mutsumi add "Buy coffee" --personal          # Add to personal tasks
mutsumi add "Fix bug" --project saas-app     # Add to specific project
mutsumi add "Fix bug"                        # Add to cwd's mutsumi.json (current behavior)

mutsumi list --all                           # List across all sources
mutsumi list --project saas-app              # List specific project
```

### 4.4 Migration Command

```bash
mutsumi migrate                  # Rename tasks.json → mutsumi.json in cwd
mutsumi migrate --config         # Move ~/.config/mutsumi/ → ~/.mutsumi/
mutsumi migrate --all            # Both
```

## 5. Implementation Strategy

### 5.1 Data Layer Changes

| Component | Change |
|-----------|--------|
| `core/loader.py` | Accept multiple file paths, return tagged `(source_name, TaskFile)` tuples |
| `core/watcher.py` | Watch multiple files, tag events with source name |
| `core/writer.py` | Route writes to correct file based on active tab context |
| `core/models.py` | No changes — schema is unchanged |
| `core/paths.py` | Add `mutsumi_home()` → `~/.mutsumi/` |

### 5.2 TUI Changes

| Component | Change |
|-----------|--------|
| `app.py` | Manage multiple data sources, dynamic tab creation |
| `tui/header_bar.py` | Render dynamic project tabs |
| `tui/main_dashboard.py` | **New widget** — aggregated dashboard view |
| `tui/task_list_panel.py` | Unchanged — renders one source's tasks |
| `tui/scope_filter.py` | **New widget** — sub-filter bar (Today/Week/Month/Inbox/All) |

### 5.3 Phases

| Phase | Scope | Deliverable |
|-------|-------|-------------|
| **5a** | File rename + fallback | `mutsumi.json` support with `tasks.json` backward compat |
| **5b** | Multi-source data layer | Loader/watcher handle N files, tagged by source |
| **5c** | Project registry | `mutsumi project add/remove/list` CLI commands |
| **5d** | Tab redesign | Dynamic tabs: Main + Personal + per-project |
| **5e** | Main dashboard widget | Aggregated summary view with progress bars |
| **5f** | Config migration | `~/.mutsumi/` consolidation + `mutsumi migrate` |

## 6. Backward Compatibility

| Concern | Handling |
|---------|----------|
| Existing `tasks.json` users | Auto-detected as fallback; `mutsumi migrate` to rename |
| Existing `~/.config/mutsumi/` config | Auto-detected as fallback; `mutsumi migrate --config` to move |
| Single-project usage (no projects registered) | Works exactly as before — watches cwd's `mutsumi.json` |
| Agent Protocol | Schema unchanged — Agents only need to rename the file |
| `scope` field semantics | Unchanged — still time-based (day/week/month/inbox) |
| `--watch` flag | Still works, but `project add` is the preferred approach |

## 7. What This Is NOT

- **Not a team collaboration tool.** All data is local. No shared boards, no permissions, no sync.
- **Not a project management tool.** No Gantt charts, no sprints, no resource allocation. Just tasks.
- **Not replacing the Agent.** Mutsumi is still the View. Agents are still the Controllers. `mutsumi.json` is still the Model.
- **Not a workspace manager.** Mutsumi does not manage terminals, windows, or processes.

## 8. Open Questions

1. **Project health indicators** — Should the Main tab show "last updated" timestamps to detect stale projects?
2. **Cross-project task moving** — Should users be able to move a task from one project to another? (Probably not in v1.)
3. **Project archival** — How to handle finished projects? Remove from registry? Archive flag?
4. **Notification per-project** — Should notification modes be configurable per-project?
5. **Max projects** — Is there a practical upper limit? Tab bar overflow strategy?

---

## Appendix A: Migration Path

```
v0.4.x (current)          v0.5.0 (this RFC)
─────────────────          ──────────────────
tasks.json          →      mutsumi.json (auto-fallback)
~/.config/mutsumi/  →      ~/.mutsumi/ (auto-fallback)
[Today][Week][Month][Inbox] → [★ Main][Personal][proj-a][proj-b]
                                       └─ [Today][Week][Month][Inbox][All]
Single file watcher  →      Multi-file watcher
No personal tasks    →      ~/.mutsumi/mutsumi.json
```

## Appendix B: Competitive Landscape

No existing terminal tool does this combination:

| Tool | Personal Todo | Multi-Project Agent View | Unified Dashboard |
|------|:---:|:---:|:---:|
| Todoist | ✅ | ❌ | ❌ |
| Taskwarrior | ✅ | ❌ | ❌ |
| GitHub Projects | ❌ | Partial | ❌ |
| Linear | ❌ | ✅ | ✅ (but team, not personal) |
| **Mutsumi v0.5** | **✅** | **✅** | **✅** |
