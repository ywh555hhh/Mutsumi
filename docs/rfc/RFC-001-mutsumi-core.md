# RFC-001: Mutsumi Core Architecture

| Field       | Value                                       |
|-------------|---------------------------------------------|
| **RFC**     | 001                                         |
| **Title**   | Mutsumi Core Product Definition & Architecture |
| **Status**  | Draft                                       |
| **Author**  | Wayne (ywh)                                 |
| **Created** | 2026-03-21                                  |

> **[中文版](./RFC-001-mutsumi-core_cn.md)** | **[日本語版](./RFC-001-mutsumi-core_ja.md)**

---

> **Historical note (2026-03-24):** This RFC captures the earliest Mutsumi architecture direction. Some details here are no longer the current product baseline. For current canonical behavior, prefer `README.md`, `docs/specs/*.md`, `docs/ROADMAP.md`, and newer RFCs such as RFC-006, RFC-007, RFC-008, and RFC-009.

## Abstract

Mutsumi (若叶睦) is a silent task exo-brain designed for **multi-threaded super-individuals**. She is a standalone terminal TUI application that achieves decoupled collaboration with any AI Agent by watching local JSON files. This RFC defines Mutsumi's product boundaries, core architecture, data contract, interaction specifications, and integration protocol.

## 1. Motivation

### 1.1 Problem Statement

The working mode of modern developers (super-individuals) has shifted from single-threaded to multi-threaded:

- **Fragmented inputs**: Simultaneously active across browsers, QQ groups, Reddit, Discord, forums.
- **Concurrent Agents**: Running multiple AI Agents on different tasks at the same time (Claude Code for frontend, Codex CLI for tests, Gemini CLI for docs).
- **Extreme time pressure**: Too busy every day to click around in complex project management tools.

Problems with existing tools:

| Tool Type | Problem |
|---|---|
| Notion/Todoist | Too heavy — opening it is a burden, disconnected from terminal workflows |
| Taskwarrior | Pure CLI, no visual anchor, not intuitive enough |
| GitHub Issues | Platform-locked, no local offline support, not "personal" enough |
| IDE Todo plugins | Editor-locked, Agents cannot write directly |

### 1.2 Core Insight

> **The bottleneck of task management is not "management" itself, but the friction of "summoning" it.**

If the cost of viewing/updating tasks approaches zero (one-key summon, one-key check-off), users won't resist using it. Mutsumi compresses this friction to the level of a terminal hotkey.

### 1.3 One-liner Positioning

> "What's the difference between Mutsumi and Taskwarrior?"
> — **Zero-friction summoning, native fit with your favorite Agent.** Taskwarrior is a task database that requires you to learn commands; Mutsumi is a quiet visual kanban — she doesn't tell you what to do, she just waits for you to glance at her.

## 2. Design Principles

### 2.1 MVC Separation (Core Philosophy)

```
┌─────────────────────────────────────────────────┐
│                  User's Brain                    │
│   "Put fix-cache-bug at today's top priority"    │
└────────────────────┬────────────────────────────┘
                     │ natural language
                     ▼
┌─────────────────────────────────────────────────┐
│        Controller: AI Agent (decoupled)          │
│  Claude Code / Codex CLI / Gemini CLI / OpenCode │
│  Manual edit / custom scripts / anything that    │
│  writes JSON                                     │
└────────────────────┬────────────────────────────┘
                     │ writes/reads
                     ▼
┌─────────────────────────────────────────────────┐
│         Model: tasks.json (local file)           │
│     100% data sovereignty, plain text, Git-able   │
└────────────────────┬────────────────────────────┘
                     │ watchdog
                     ▼
┌─────────────────────────────────────────────────┐
│      View: Mutsumi TUI (minimal kanban)          │
│   Hot-reload render · mouse/keyboard interaction  │
│   State write-back to JSON                        │
└─────────────────────────────────────────────────┘
```

### 2.2 Five Commandments

1. **Zero Friction** — From summon to action complete < 2 seconds. No loading screen, no login, no network request.
2. **Layout Agnostic** — Mutsumi doesn't care how you arrange windows. She's an independent process — use tmux/zellij/multi-monitor as you please.
3. **Agent Agnostic** — Not bound to any LLM or Agent. Any program that can write JSON is a legitimate Controller.
4. **Hackable First** — Official skeleton provided; users can trivially hack the data structure, theme, keybindings, and views.
5. **Local Only** — Zero network dependency. Data is files, files are local.

## 3. Target User

**Primary Persona: The Multi-threaded Individual**

- Simultaneously roaming across browsers, QQ groups, Reddit, Discord, forums
- Running multiple Agents on different tasks simultaneously
- Very busy every day, every interaction must feel "snappy"
- Terminal is the primary work environment (or at least not averse to it)
- Natural affinity for geek tools, loves DIY and customization

**NOT for:**

- PMs who need team collaboration/shared boards (use Linear)
- Project managers who need Gantt charts and resource allocation (use Jira)
- Users who never touch a terminal (use Todoist)

## 4. Architecture Overview

### 4.1 System Diagram

```
                    ┌──────────────────────┐
                    │   Agent A (write)     │
                    │   Claude Code         │
                    └──────────┬───────────┘
                               │
┌──────────────┐               ▼              ┌──────────────┐
│  Agent B     │        ┌────────────┐        │  Agent C     │
│  Codex CLI   │───────▶│ tasks.json │◀───────│  custom script│
└──────────────┘        └─────┬──────┘        └──────────────┘
                              │
                    ┌─────────┼─────────┐
                    │   watchdog watch   │
                    ▼                   ▼
             ┌────────────┐     ┌────────────┐
             │ Mutsumi TUI│     │ event.log  │
             │ (render+UX) │     │ (reverse   │
             │             │     │  notify)   │
             └─────┬──────┘     └────────────┘
                   │
                   │ user clicks done
                   ▼
             write back tasks.json
```

### 4.2 Component Breakdown

| Component | Responsibility | Technology |
|---|---|---|
| **TUI Renderer** | Render task list, handle user interaction | Textual (Python) |
| **File Watcher** | Watch tasks.json for changes and trigger re-render | watchdog |
| **Data Layer** | Read/write tasks.json, schema validation | pydantic |
| **CLI Interface** | Provide non-TUI command-line CRUD | click / typer |
| **Config Loader** | Load user config (theme, keybindings, language) | tomllib (stdlib) |
| **i18n Engine** | UI text multi-language switching | Custom (simple dict) |
| **Event Emitter** | Reverse-notify Agent (optional) | File append-write |

### 4.3 Technology Stack

| Layer | Choice | Rationale |
|---|---|---|
| Language | Python 3.12+ | Textual ecosystem, dev speed, zero-friction with uv |
| Package Mgr | uv | Blazing fast, modern, matches geek aesthetics |
| TUI Framework | Textual | Mouse support, animations, CSS-like styling, minimal code |
| CLI Framework | click | Mature & stable, coexists with Textual without conflict |
| Validation | pydantic v2 | JSON schema validation, blazing fast, type-safe |
| File Watch | watchdog | Cross-platform, mature, event-driven |
| Config Format | TOML | Human-readable, Python stdlib native support (tomllib) |
| Distribution | uv tool install | Zero-dependency install experience |

## 5. Data Contract

> See `docs/specs/DATA_CONTRACT.md` for detailed schema definition.

### 5.1 Design Philosophy

- **Official skeleton provided; users can trivially hack it**
- Base fields have clear semantics and validation rules
- Users can add arbitrary custom fields — Mutsumi will ignore but never delete them
- Nesting (sub-tasks) is theoretically unlimited; TUI renders 3 levels by default, configurable

### 5.2 Minimal Task Object

```json
{
  "id": "01JQ8X7K3M0000000000000000",
  "title": "重构 Auth 模块",
  "status": "pending",
  "scope": "day",
  "priority": "high",
  "tags": ["dev"],
  "children": []
}
```

### 5.3 ID Strategy

Uses **UUIDv7** (time-sortable UUID):

- Naturally sorted by creation time
- Guaranteed unique without central coordination
- Both Agent and TUI can independently generate IDs
- Natively supported in Python 3.12+ (`uuid.uuid7()` — or fallback `uuid7` lib)

### 5.4 Scope: Hybrid Mode

The `scope` field supports hybrid mode:

- Users/Agents can **manually** set `scope: "day"` as a static label
- If a task contains a `due_date` field, TUI **automatically** infers view assignment based on current date
- Manual `scope` takes priority over auto-inference
- Tasks with neither `scope` nor `due_date` go to `inbox`

### 5.5 Concurrent Write Strategy

| Scenario | Handling |
|---|---|
| TUI modifies → writes | Read latest file → modify target field → atomic write (temp file + rename) |
| Agent modifies → watchdog | Detect file change → reload → re-render TUI |
| Simultaneous writes (extremely rare) | Last Write Wins; TUI self-heals on next watchdog trigger |
| JSON format corruption | TUI shows error badge, retains last valid state, never overwrites |

Atomic write flow:

```
TUI click → read tasks.json → modify in memory → write to .tasks.json.tmp → os.rename() → watchdog detects → re-render
```

`os.rename()` is atomic on POSIX systems, preventing reads of half-written files.

## 6. TUI Specification

> See `docs/specs/TUI_SPEC.md` for detailed interaction specifications.

### 6.1 View Tabs

```
┌─────────────────────────────────────────────┐
│  [Today] [Week] [Month] [Inbox]    mutsumi  │
├─────────────────────────────────────────────┤
│                                             │
│  ▼ HIGH                                     │
│  [ ] 重构 Auth 模块              dev   ★★★  │
│  [x] 修复缓存穿透 Bug           bugfix ★★★  │
│                                             │
│  ▼ NORMAL                                   │
│  [ ] 写周报                      life  ★★   │
│  [ ] Review PR #42               dev   ★★   │
│    └─ [ ] 检查类型安全                      │
│    └─ [x] 跑通测试                          │
│                                             │
│  ▼ LOW                                      │
│  [ ] 更新 README                 docs  ★    │
│                                             │
├─────────────────────────────────────────────┤
│  6 tasks · 1 done · 5 pending    🔇 quiet   │
└─────────────────────────────────────────────┘
```

### 6.2 CRUD in TUI

TUI supports full CRUD — it can be used independently without any external Agent.

| Action | Mouse | Keyboard |
|---|---|---|
| Create | Bottom [+New] button | `n` → popup input |
| View | Click task row to expand | `Enter` to expand |
| Edit | Double-click title | `e` to edit selected |
| Delete | Right-click menu → Delete | `dd` (vim style) |
| Complete | Click checkbox | `Space` |
| Move | Drag & drop (v2) | `j/k` up/down |

### 6.3 Keyboard Scheme: Multi-preset

Multiple preset keybinding schemes are provided. Users can switch between them or fully customize in config:

- **vim** (default): `j/k/g/G/dd/Space/n/e/q`
- **emacs**: `C-n/C-p/C-d/C-Space`
- **arrow**: Arrow keys + Enter + Delete
- **custom**: User-defined in `config.toml`

### 6.4 Theme System

- Default theme: **Monochrome Zen** — minimal black/white/gray, accent color is light teal (similar to Catppuccin Teal)
- Built-in options: `monochrome-zen`, `solarized`, `nord`, `dracula`
- Users can add custom `.toml` theme files under `~/.config/mutsumi/themes/`
- Theme definitions follow Textual CSS variable mapping

### 6.5 Notification System (Configurable)

| Mode | Behavior | Config Value |
|---|---|---|
| **quiet** | Fully silent; status bar shows count only (default) | `quiet` |
| **badge** | Overdue tasks flash/highlight within TUI | `badge` |
| **bell** | Send terminal bell (`\a`); terminal app decides how to handle | `bell` |
| **system** | Call system notification API (macOS/Linux/Windows) | `system` |

## 7. CLI Specification

### 7.1 Primary Commands

```bash
# Launch TUI (core usage)
mutsumi                           # watch tasks.json in current dir
mutsumi --watch ./project/tasks.json  # specify path
mutsumi --watch ~/a.json ~/b.json     # multi-project aggregate

# CRUD (non-TUI mode, for scripts/Agents)
mutsumi add "修复登录 Bug" --priority high --scope day --tags dev,urgent
mutsumi list                      # list all tasks
mutsumi list --scope today        # filter by scope
mutsumi done <task-id>            # mark complete
mutsumi edit <task-id> --title "新标题" --priority low
mutsumi rm <task-id>              # delete

# Utilities
mutsumi init                      # generate tasks.json template in cwd
mutsumi validate                  # validate tasks.json format
mutsumi setup --agent claude-code    # inject Agent integration instructions
mutsumi schema                    # output JSON Schema (for Agent reference)
```

### 7.2 Multi-project Aggregation

When `--watch` receives multiple paths, TUI adds a project dimension to the Tab bar:

```
[Project A] [Project B] [All]  ·  [Today] [Week] [Month] [Inbox]
```

Or display source projects as groups within the task list.

## 8. Agent Integration Protocol

> See `docs/specs/AGENT_PROTOCOL.md` for detailed protocol.

### 8.1 Write Protocol (Agent → Mutsumi)

An Agent only needs to do one thing: **write to `tasks.json` correctly following the schema.**

```
Agent reads tasks.json → modifies in memory → writes entire file back
```

Requirements:

- Must preserve unrecognized custom fields (never discard them)
- The file must be valid JSON after writing
- Atomic write (temp file + rename) is recommended

### 8.2 Read Protocol (Mutsumi → Agent)

**Event Log mechanism**: When a user operates in the TUI, Mutsumi optionally appends to `events.jsonl`:

```jsonl
{"ts":"2026-03-21T10:00:00Z","event":"task_completed","task_id":"01JQ8X7K3M...","title":"修复缓存 Bug"}
{"ts":"2026-03-21T10:01:00Z","event":"task_created","task_id":"01JQ8X7K4N...","title":"写单元测试"}
```

Agents can `tail -f events.jsonl` to sense user actions on the TUI side, enabling two-way communication.

### 8.3 Schema Validation Behavior

When `tasks.json` contains invalid data:

| Error Type | Mutsumi Behavior |
|---|---|
| JSON syntax error | TUI shows error banner, retains last valid snapshot |
| Unknown status value | TUI shows warning badge on that task |
| Missing required field (id/title) | Skip that task; TUI footer shows "1 task skipped" |
| Unknown custom field | Render normally, ignore custom fields (never delete) |

All validation errors are also written to stderr and `~/.local/share/mutsumi/error.log`, allowing Agents to self-correct.

## 9. Configuration System

### 9.1 Config Location

Follows the XDG Base Directory specification (like starship, lazygit, bat, and other mainstream CLI tools):

```
~/.config/mutsumi/
├── config.toml          # main config
├── themes/
│   └── my-theme.toml    # custom theme
└── keys/
    └── my-keys.toml     # custom keybindings
```

Platform exceptions:

- macOS: `~/Library/Application Support/mutsumi/` (also accepts `~/.config/mutsumi/`)
- Windows: `%APPDATA%\mutsumi\`

### 9.2 Config Schema

```toml
[general]
language = "auto"          # "auto" | "en" | "zh" | "ja"
default_watch = "."        # default watch path
default_scope = "day"      # default Tab on launch

[theme]
name = "monochrome-zen"   # built-in theme name or custom theme filename
accent_color = "#94e2d5"   # override accent color

[keys]
preset = "vim"             # "vim" | "emacs" | "arrow" | "custom"

[notifications]
mode = "quiet"             # "quiet" | "badge" | "bell" | "system"

[data]
id_format = "uuidv7"      # "uuidv7" | "ulid" | "auto-increment"

[events]
enabled = true             # whether to write events.jsonl
path = "./events.jsonl"    # event log path
```

## 10. i18n Strategy

### 10.1 Implementation

```
locales/
├── en.toml
├── zh.toml
└── ja.toml
```

```toml
# locales/en.toml
[tabs]
today = "Today"
week = "Week"
month = "Month"
inbox = "Inbox"

[status]
tasks = "{count} tasks"
done = "{count} done"
pending = "{count} pending"

[actions]
new_task = "New Task"
confirm_delete = "Delete this task?"
```

### 10.2 Language Detection

Priority: `config.toml` setting > `$LANG` environment variable > fallback `en`

## 11. Distribution

### 11.1 Primary Channel

```bash
uv tool install mutsumi
```

Users don't need Python pre-installed — `uv` automatically manages an isolated Python environment.

### 11.2 Secondary Channels (Post-MVP)

| Channel | Priority | Notes |
|---|---|---|
| `pipx` | P1 | Fallback when uv is unavailable |
| `brew` | P2 | macOS user habit |
| `nix` | P3 | NixOS community |
| GitHub Releases | P1 | Direct wheel download |

## 12. Security & Privacy

- **Zero network**: Mutsumi makes no network requests, includes no telemetry
- **Zero cloud**: All data stored on the local filesystem
- **File permissions**: tasks.json recommended permission `0600` (owner read/write only)
- **No eval**: Will never execute any field content from tasks.json

## 13. Open Questions

The following questions are deferred to future RFCs:

1. **Plugin System** — Should a plugin mechanism be introduced (e.g., custom view components)?
2. **Sync** — Should optional cross-device sync be provided (via Git or Syncthing)?
3. **Task Templates** — Should task templates be supported (e.g., daily standup template)?
4. **Time Tracking** — Should Pomodoro/time tracking be integrated?
5. **Archive** — Archival strategy for completed tasks (keep in file vs. move to archive.json)?

---

## Appendix A: Rejected Alternatives

| Alternative | Why Rejected |
|---|---|
| Electron GUI | Violates "minimal" principle — slow startup, high resource usage |
| SQLite storage | Not Agent-friendly — cannot directly cat/edit |
| Rust TUI (ratatui) | Slower dev speed; Textual's CSS styling is better for rapid iteration |
| Built-in Agent | Violates "decoupled" principle — binding a model loses generality |
| WebSocket communication | Over-engineered — the filesystem is the best IPC |
| Markdown tasks.md | High parsing complexity, poor nesting support — deferred to v2 |

## Appendix B: Naming & Branding

> See `docs/BRAND.md` for details.

**Mutsumi (若叶睦)** — From the Japanese "睦" (harmony, closeness). It conveys the idea of living in harmony with the user's workflow — not intrusive, not prescriptive, just quietly being there.
