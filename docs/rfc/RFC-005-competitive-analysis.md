# RFC-005: Competitive Analysis — What We Borrowed, What We Kept

| 项目 | 内容 |
|------|------|
| RFC  | 005 |
| 标题 | Competitive Analysis — What We Borrowed, What We Kept |
| 状态 | Draft |
| 作者 | Wayne (ywh) |
| 创建 | 2026-03-21 |

[中文](RFC-005-competitive-analysis_cn.md) · [日本語](RFC-005-competitive-analysis_ja.md)

---

## 1. Abstract

Mutsumi 的 UX 设计不是凭空发明的——它站在数十个终端任务管理器的肩膀上。本 RFC 记录我们系统性地分析了哪些竞品，从中借鉴了什么，刻意拒绝了什么，以及每一个设计决策背后的理由。

这份文档同时也是一份活文档：每当 Mutsumi 引入新的交互模式时，应回溯到本 RFC 中注明灵感来源。

---

## 2. Competitive Landscape

### 2.1 Primary Competitors

| Product | Language | Storage | TUI Framework | Stars | Key Innovation |
|---------|----------|---------|---------------|------:|----------------|
| **Dooit** (kraanzu/dooit) | Python | SQLite | Textual | 2.2k | Plugin system, urgency scoring, Python-as-config |
| **Taskwarrior** | C++ | Flat file | ncurses | 4.5k | 40+ report types, UDA, hooks, sync server |
| **Ultralist** | Go | JSON | Bubble Tea | 800+ | Natural language input, due-date parsing |
| **Todoman** | Python | iCalendar | urwid | 600+ | CalDAV sync, standards-based |
| **dstask** | Go | Git repo | Custom | 800+ | Git-native sync, context-based filtering |
| **Calcure** | Python | JSON/iCal | curses | 900+ | Calendar + task hybrid, daily view |

### 2.2 Adjacent References (not direct competitors)

| Product | What We Looked At |
|---------|-------------------|
| **Vim/Neovim** | Modal editing, multi-key sequences (`dd`, `gg`, `yy`), operator-motion grammar |
| **Obsidian** | Graph view inspiration, local-first philosophy, plugin marketplace model |
| **Notion** | Inline editing, slash commands, block-based composition |
| **Todoist** | Natural language quick-add, priority colors, project nesting |
| **Linear** | Keyboard-first design, `Cmd+K` command palette, minimal UI |

---

## 3. Design Decision Matrix

### Legend

| Symbol | Meaning |
|--------|---------|
| ✅ **Borrowed** | Adopted into Mutsumi with adaptation |
| 🚫 **Rejected** | Evaluated and explicitly excluded |
| 🔄 **Transformed** | Took the concept but changed the implementation significantly |
| 📌 **Kept (Mutsumi Original)** | Our own design, preserved despite competing approaches |

---

## 4. What We Borrowed

### 4.1 From Dooit

Dooit was our primary inspiration source. We performed a line-by-line analysis of its interaction patterns.

#### ✅ Multi-Key Sequence Engine (Dooit → KeyManager)

| Aspect | Dooit | Mutsumi |
|--------|-------|---------|
| Mechanism | Key buffer with prefix matching, no timeout | Same: `KeyManager._buffer` + `MatchResult` enum |
| Sequences | `dd` delete | `dd` delete, `gg` cursor-top (vim preset) |
| Timeout | None — explicit Escape to cancel | Same |
| Integration | Replaces all keybinding handling | Coexists with Textual `Binding` system — KeyManager only handles multi-key, single-key stays in Textual |

**Why**: Dooit's no-timeout accumulator is strictly better than our original timer-based `_d_pending`/`_d_timer` state machine. The timer approach had a race condition: type `d` then wait → confusing state. Prefix matching is deterministic.

**Adaptation**: Dooit puts *all* keys through its key handler. We kept Textual's Binding for single-key actions (more maintainable, binding inspection, help generation) and only route multi-key sequences through KeyManager.

#### ✅ Inline Confirmation Bar (Dooit → ConfirmBar)

| Aspect | Dooit | Mutsumi |
|--------|-------|---------|
| Trigger | Destructive action (delete) | `dd` sequence |
| Rendering | Bottom bar: `"Delete 'xxx'? [y/N]"` | Same format, docked bottom, 1-line height |
| Confirm key | `y` | `y` |
| Cancel | Any other key | Any other key |
| Focus behavior | Steals focus, returns after resolution | Same: `can_focus=True`, posts `Resolved` message |

**Why**: Modal dialog (our old `ConfirmDialog`) requires mouse travel to click a button or tab-navigation to reach it. Inline bar is 1-keystroke to resolve — faster for keyboard-heavy users.

**Kept**: `ConfirmDialog` still exists for detail-panel delete button (mouse-initiated delete benefits from a larger confirmation target).

#### ✅ Cascading Completion (Dooit → `cascade_toggle_status`)

| Aspect | Dooit | Mutsumi |
|--------|-------|---------|
| Parent → children | Marking parent DONE marks all children DONE | Same |
| Children → parent | All children DONE → auto-mark parent DONE | Same |
| Un-complete cascade | Marking parent PENDING un-completes all children | Same |

**Why**: Without cascading, users must manually toggle each subtask — tedious for project-style tasks with many children.

**Adaptation**: Dooit uses SQLite triggers for cascading. We implement it in pure Python (`cascade_toggle_status`) because our data layer is JSON, not SQL.

#### ✅ Priority Cycling via Keyboard (Dooit)

| Aspect | Dooit | Mutsumi |
|--------|-------|---------|
| Keys | `+`/`-` | `+`/`=` (up), `-`/`_` (down) |
| Behavior | Cycle through urgency levels | Cycle through `low → normal → high`, clamped at boundaries |
| Scope | Integer urgency (unbounded) | Enum priority (3 levels) |

**Why**: Direct priority manipulation without opening a form is essential for flow state.

**Adaptation**: Dooit uses unbounded integer urgency (1–999). We use a 3-level enum, which is simpler and matches how humans actually think about priority.

#### ✅ Reorder Tasks via Keyboard (Dooit)

| Aspect | Dooit | Mutsumi |
|--------|-------|---------|
| Keys | `shift+j`/`shift+k` (vim-like) | `J`/`K` (vim), `ctrl+shift+n/p` (emacs), `shift+↑/↓` (arrows) |
| Behavior | Swap with adjacent sibling | Same |
| Persistence | Immediate write-back | Same |

**Adaptation**: Three preset variants instead of one. Emacs and arrow users get equivalent bindings in their own idiom.

#### ✅ Help Screen Auto-Generation (Dooit)

| Aspect | Dooit | Mutsumi |
|--------|-------|---------|
| Trigger | `?` key | `?` key |
| Content source | Hardcoded list | Auto-generated from `Binding` list + `KeySequence` list |
| Categorization | Manual | `_ACTION_CATEGORIES` mapping, 6 groups |
| Dismissal | Escape | Escape, `q`, or `?` |

**Adaptation**: Dooit hardcodes its help text. We auto-generate from the actual binding configuration, so help stays in sync when keybindings change.

#### ✅ Sort Overlay (Dooit)

| Aspect | Dooit | Mutsumi |
|--------|-------|---------|
| Trigger | `s` key | `s` key |
| UI | Horizontal picker with arrow navigation | Same, with `h/l/j/k` vim keys added |
| Fields | Multiple sort fields | `title`, `priority`, `status`, `due` |
| Reverse toggle | Toggle button | `r` key |

### 4.2 From Taskwarrior

#### 🔄 CLI-First Design Philosophy (Transformed)

| Aspect | Taskwarrior | Mutsumi |
|--------|-------------|---------|
| Primary interface | CLI | TUI (CLI is secondary) |
| Data modification | `task add`, `task done`, `task modify` | `mutsumi add`, `mutsumi done`, `mutsumi edit` |
| Output format | Configurable report columns | Plain text (future: `--json`) |

**What we took**: The idea that every operation should be expressible as a one-liner CLI command. Taskwarrior proves this makes agent/script integration trivial.

**What we changed**: Taskwarrior is CLI-primary with TUI as an afterthought (`taskwarrior-tui` is a separate project). Mutsumi is TUI-primary with CLI as a first-class secondary.

#### 🔄 Custom Fields / UDA (Transformed)

| Aspect | Taskwarrior | Mutsumi |
|--------|-------------|---------|
| Custom fields | UDA (User Defined Attributes) with types | Pydantic `extra="allow"` — freeform JSON |
| Schema | Must declare before use | No declaration needed |
| Display | Configurable columns | Dynamic `columns` config in `config.toml` |

**What we took**: The idea that users/agents should be able to attach arbitrary metadata to tasks (effort, sprint, blocked_by, etc.).

**What we changed**: Taskwarrior requires schema declaration. We use Pydantic's `extra="allow"` which is zero-friction — any JSON field is preserved and can be displayed.

### 4.3 From Vim/Neovim

#### ✅ Modal Keybinding Presets

| Aspect | Vim | Mutsumi |
|--------|-----|---------|
| `j`/`k` navigation | Universal | Vim preset |
| `dd` delete | Operator grammar | Multi-key sequence via KeyManager |
| `gg` go to top | Motion command | Multi-key sequence via KeyManager |
| `y`/`p` yank/paste | Register-based | Internal clipboard (`_task_clipboard`) |
| `i` insert mode | Modal switch | Inline edit mode (scoped to single row) |
| `G` go to bottom | Motion command | Binding |
| `J`/`K` with Shift | Join/K-something | Reorder (adapted semantics) |

**What we took**: The muscle memory. Vim users should feel at home without reading any docs.

**What we changed**: We don't implement full Vim grammar (operators × motions × counts). `dd` means delete (not "delete line"), `y` means copy task (not "yank to register"). The key *positions* are Vim-like; the *semantics* are task-domain-specific.

### 4.4 From Linear

#### 🔄 Keyboard-First, Not Keyboard-Only

| Aspect | Linear | Mutsumi |
|--------|--------|---------|
| Philosophy | Every action has a keyboard shortcut | Every action has keyboard + mouse + CLI |
| Discovery | `Cmd+K` command palette | `?` help screen |
| Speed | Sub-100ms response | File watcher debounce + instant TUI |

**What we took**: The conviction that keyboard shortcuts aren't a power-user niche — they're the primary interaction mode for developers.

**What we added**: Linear has no CLI. Mutsumi's RFC-004 Triple Input Parity extends this to three surfaces.

---

## 5. What We Rejected

### 5.1 From Dooit

#### 🚫 SQLite Storage

| Dooit | Mutsumi | Why Rejected |
|-------|---------|--------------|
| SQLite database | JSON flat file | **Agent Agnostic**: Any program that writes JSON is a valid controller. SQLite requires a driver, imposes schema, and is opaque to `cat`/`jq`/human inspection. JSON is the universal interchange format for AI agents. |

#### 🚫 Python-as-Config

| Dooit | Mutsumi | Why Rejected |
|-------|---------|--------------|
| `config.py` executed at startup | `config.toml` parsed with stdlib `tomllib` | **Security**: Executing arbitrary Python at startup is a remote code execution vector. TOML is declarative and safe. |

#### 🚫 Plugin System (for now)

| Dooit | Mutsumi | Why Rejected |
|-------|---------|--------------|
| Plugin API with hooks | No plugin system | **Complexity budget**: Plugins require versioned API contracts, error isolation, and dependency management. Mutsumi's philosophy is that *agents write JSON* — the "plugin" is any external program. Reconsidered post-1.0. |

#### 🚫 Unbounded Integer Urgency

| Dooit | Mutsumi | Why Rejected |
|-------|---------|--------------|
| `urgency: int` (1–999) | `priority: "high"\|"normal"\|"low"` | **Cognitive overhead**: Users don't think "this is urgency 73 vs 71." Three named levels cover 99% of use cases. Agents that need finer granularity can use custom fields via `extra="allow"`. |

#### 🚫 `pyperclip` System Clipboard

| Dooit | Mutsumi | Why Rejected |
|-------|---------|--------------|
| System clipboard via pyperclip | Internal clipboard (`_task_clipboard`) | **No heavy dependencies** (CLAUDE.md Rule 4). pyperclip has platform-specific issues (xclip/xsel on Linux, pbcopy on macOS). Internal clipboard is sufficient for task-level copy/paste. |

#### 🚫 Workspace Dual-Pane Layout

| Dooit | Mutsumi | Why Rejected |
|-------|---------|--------------|
| Left pane: workspaces, Right pane: tasks | Single-pane with scope tabs | **Layout Agnostic** (RFC-001 Commandment 2): Mutsumi is an independent terminal process, not a workspace manager. Scope tabs (`Day/Week/Month/Inbox`) serve the same filtering purpose without the spatial complexity. |

### 5.2 From Taskwarrior

#### 🚫 Sync Server (taskserver)

| Taskwarrior | Mutsumi | Why Rejected |
|-------------|---------|--------------|
| taskd sync server | No sync | **Local Only** (RFC-001 Commandment 5). No network calls. Users who need sync can use git, Syncthing, or cloud-synced directories. |

#### 🚫 40+ Report Types

| Taskwarrior | Mutsumi | Why Rejected |
|-------------|---------|--------------|
| `burndown.daily`, `history.monthly`, etc. | 4 scope tabs + sort + search | **Over-engineering**. Mutsumi is a "quiet dashboard", not a project management suite. Complex reporting belongs in dedicated tools. |

#### 🚫 Hook Scripts

| Taskwarrior | Mutsumi | Why Rejected |
|-------------|---------|--------------|
| `on-add`, `on-modify` shell hooks | `events.jsonl` event log | **Agent Agnostic**: Shell hooks assume a specific execution environment. Event logs are passive — any consumer can tail and react. No coupling to Mutsumi's process lifecycle. |

### 5.3 From Todoist/Notion

#### 🚫 Cloud Sync / Account System

Mutsumi is 100% local. No accounts, no telemetry, no API calls. This is a foundational constraint, not a missing feature.

#### 🚫 Natural Language Date Parsing

| Todoist/Ultralist | Mutsumi | Why Rejected |
|-------------------|---------|--------------|
| "every monday", "tomorrow", "in 3 days" | ISO 8601 dates (`YYYY-MM-DD`) | **Ambiguity**: "next Friday" is ambiguous across locales and user expectations. ISO dates are unambiguous and machine-writable. Agent controllers can do their own NLP → ISO conversion. |

---

## 6. What We Kept (Mutsumi Originals)

These are design decisions unique to Mutsumi that we deliberately preserved despite pressure from competitive patterns.

### 📌 JSON as the Model

| Alternative | Why We Kept JSON |
|-------------|------------------|
| SQLite (Dooit) | Human-readable, `cat`/`jq`-friendly, git-diffable |
| iCalendar (Todoman) | Too rigid for arbitrary task metadata |
| Git repo (dstask) | Couples storage to version control |
| YAML | Whitespace-sensitive, security issues with `!!python/object` |

JSON is the **lingua franca of AI agents**. Claude, GPT, Gemini — they all output JSON natively. Making `tasks.json` the single source of truth means any agent can participate with zero Mutsumi-specific knowledge.

### 📌 Agent Agnostic Architecture (MVC Separation)

No other task manager in our competitive set explicitly designs for AI agent integration. Our MVC split (Mutsumi=View, Agent=Controller, tasks.json=Model) is unique:

```
┌─────────────┐     ┌──────────────┐     ┌──────────────┐
│  Claude Code │     │  Codex CLI   │     │  Custom Bot  │
│  (writes     │     │  (writes     │     │  (writes     │
│   tasks.json)│     │   tasks.json)│     │   tasks.json)│
└──────┬───────┘     └──────┬───────┘     └──────┬───────┘
       │                    │                    │
       └────────────┬───────┘────────────────────┘
                    │
              ┌─────▼─────┐
              │ tasks.json │  ← Model (single source of truth)
              └─────┬──────┘
                    │
              ┌─────▼──────┐
              │  Mutsumi   │  ← View (watches, renders, accepts input)
              │  TUI/CLI   │
              └────────────┘
```

This architecture survives agent churn. When the next agent framework drops, it just needs to write JSON.

### 📌 TOML Configuration (not Python, not YAML, not JSON)

| Format | Why Not |
|--------|---------|
| Python (Dooit) | RCE vector |
| YAML | `!!python/object` RCE, whitespace fragility |
| JSON | No comments, poor human editability |
| INI | No nested structures |

TOML is the Goldilocks format: safe, readable, commentable, supports nested tables, and has stdlib support in Python 3.11+ (`tomllib`).

### 📌 Three Keybinding Presets (not "one true way")

Most competitors pick one keybinding style and force it. Mutsumi offers three presets (vim, emacs, arrows) because:

1. **Muscle memory is personal.** Forcing vim keys on an Emacs user is hostile.
2. **Preset ≠ customization complexity.** Three predefined sets are simpler than a full keymap editor.
3. **Mouse behavior is universal.** Only keyboard bindings vary; mouse clicks work the same everywhere.

### 📌 `extra="allow"` for Unknown Fields

Instead of a formal UDA system (Taskwarrior) or ignoring unknown fields (most tools), Mutsumi's Pydantic models use `extra="allow"`:

- **Writer guarantee**: Unknown fields are preserved on read-modify-write cycles.
- **Display**: The `columns` config can reference extra fields (e.g., `effort`, `sprint`).
- **Zero ceremony**: Agents add fields without registering them first.

### 📌 Scope Hybrid (Manual + Auto-Derivation)

| Approach | Used By | Mutsumi's Approach |
|----------|---------|-------------------|
| Manual scope only | Most tools | ❌ |
| Due-date only | Todoist, Ultralist | ❌ |
| Hybrid: manual > due_date > fallback | — | ✅ |

Mutsumi's scope resolution: `manual scope > due_date auto-derivation > fallback inbox`. This means:
- Setting `scope: "day"` always works.
- Setting only `due_date: "2026-03-21"` auto-derives `scope: "day"`.
- Setting neither defaults to `inbox`.

No other tool in our competitive set does this hybrid approach.

### 📌 i18n at Both Runtime and Documentation Level

| Layer | Implementation |
|-------|---------------|
| TUI strings | TOML locale files (`locales/en.toml`, `zh.toml`, `ja.toml`) |
| Documentation | Trilingual Markdown (RFC-003 convention) |

Most terminal tools are English-only. Mutsumi supports three languages from day one because its creator operates in all three.

---

## 7. Feature Comparison Matrix

Comprehensive side-by-side comparison of all major features:

| Feature | Mutsumi | Dooit | Taskwarrior | Ultralist | dstask |
|---------|:-------:|:-----:|:-----------:|:---------:|:------:|
| TUI | ✅ Textual | ✅ Textual | ✅ ncurses (separate) | ✅ Bubble Tea | ✅ Custom |
| CLI | ✅ Click | ❌ | ✅ Custom | ✅ Custom | ✅ Custom |
| Storage | JSON | SQLite | Flat file | JSON | Git |
| Config | TOML | Python | RC file | YAML | YAML |
| Custom fields | `extra="allow"` | ❌ | UDA | ❌ | ❌ |
| Priority model | 3-level enum | Integer urgency | Integer urgency | Boolean | P1-P3 |
| Subtasks | Nested JSON | SQLite parent_id | Depends annotation | ❌ | ❌ |
| Scope / Context | 4 scope tabs | Workspace tree | Project + context | ❌ | Context |
| Multi-key sequences | `dd`, `gg` | `dd`, `da`, `dA` | ❌ | ❌ | ❌ |
| Keybinding presets | 3 (vim/emacs/arrows) | 1 (vim-like) | N/A | 1 (vim-like) | N/A |
| Inline confirmation | ConfirmBar | ✅ | ❌ | ❌ | ❌ |
| Cascading completion | ✅ | ✅ | ❌ | ❌ | ❌ |
| Recurrence | Extra field | ❌ | ✅ (recur) | ❌ | ❌ |
| File watching | watchdog | ❌ | ❌ | ❌ | ❌ |
| Agent integration | First-class | ❌ | Hooks | ❌ | ❌ |
| i18n | 3 languages | ❌ | ❌ | ❌ | ❌ |
| Themes | 4 built-in + custom | ✅ | ❌ | ❌ | ❌ |
| Network calls | Never | Never | Sync server | Never | Git push |
| Search | Dim-as-filter | Filter | Report filter | ❌ | ❌ |
| Sort | Interactive overlay | ❌ | Report columns | ❌ | ❌ |
| Help screen | Auto-generated | ❌ | `man` page | ❌ | ❌ |
| Copy/paste | Internal clipboard | ❌ | ❌ | ❌ | ❌ |
| Custom CSS | ✅ | ❌ | N/A | N/A | N/A |
| Dynamic columns | ✅ | ❌ | ✅ (report columns) | ❌ | ❌ |
| Overdue indicators | Color-coded | ❌ | Report coloring | ❌ | ❌ |
| Effort tracking | Extra field display | ❌ | UDA | ❌ | ❌ |

---

## 8. Lessons Learned

### 8.1 Steal the Interaction, Not the Architecture

Dooit's *UX* is excellent: multi-key sequences, inline confirmation, cascading completion. Dooit's *architecture* (SQLite, Python config, plugin system) serves different goals. We borrowed the interaction layer and kept our own stack.

### 8.2 Pydantic `extra="allow"` Is Our Secret Weapon

This single configuration line in our model eliminates the need for:
- UDA declarations (Taskwarrior)
- Schema migrations (any SQL-based tool)
- Plugin hooks for custom fields (Dooit)

Any field an agent writes is preserved and can be displayed.

### 8.3 Triple Input Parity Is a Unique Differentiator

No competitor in our set achieves keyboard + mouse + CLI parity for all features. This is Mutsumi's unique positioning: the task manager that works equally well for humans pressing keys, humans clicking mice, and AI agents running commands.

### 8.4 "Search as Filter" > "Search as Hide"

Most tools hide non-matching results. Dooit hides them too. We chose to *dim* non-matching rows instead, preserving spatial context. This is a Mutsumi original that emerged from our "quiet dashboard" philosophy — the board should feel stable, not jumpy.

---

## 9. Future Competitive Monitoring

Features from competitors we're tracking for potential future adoption:

| Feature | Source | Viability | Phase |
|---------|--------|-----------|-------|
| Calendar view | Calcure | Medium — significant UI effort | Post-1.0 |
| Git sync | dstask | Low — conflicts with "no network" rule, but git is local | Post-1.0 |
| Command palette (`Cmd+K`) | Linear | High — good discoverability | Phase 5 |
| Pomodoro timer | Various | Medium — separate widget | Post-1.0 |
| Natural language date input | Todoist | Low — ambiguity concerns, but useful for CLI | Phase 5 |
| Template tasks | Taskwarrior | High — useful for recurring workflows | Phase 5 |

---

## Appendix A: Dooit Source Analysis References

| Dooit File | What We Studied | What We Took |
|------------|-----------------|--------------|
| `dooit/ui/tui.py` | Key handling, event loop | Multi-key buffer pattern |
| `dooit/ui/widgets/todo.py` | Task rendering, completion cascade | Cascade logic, inline confirmation |
| `dooit/api/todo.py` | Data model, urgency system | Priority cycling (adapted to enum) |
| `dooit/ui/widgets/sort_menu.py` | Sort overlay UX | Sort bar design |
| `dooit/utils/keybinder.py` | Keybinding configuration | Sequence table design |
| `dooit/ui/widgets/help_menu.py` | Help screen | Auto-generation pattern |

## Appendix B: Design Decision Log

Chronological record of when each borrowing/rejection decision was made:

| Date | Decision | Source | Type |
|------|----------|--------|------|
| 2026-03 | Adopt multi-key sequence engine | Dooit | ✅ Borrowed |
| 2026-03 | Adopt inline confirmation bar | Dooit | ✅ Borrowed |
| 2026-03 | Reject SQLite storage | Dooit | 🚫 Rejected |
| 2026-03 | Reject Python-as-config | Dooit | 🚫 Rejected |
| 2026-03 | Reject plugin system (for now) | Dooit | 🚫 Rejected |
| 2026-03 | Reject unbounded urgency | Dooit | 🚫 Rejected |
| 2026-03 | Reject pyperclip dependency | Dooit | 🚫 Rejected |
| 2026-03 | Reject workspace dual-pane | Dooit | 🚫 Rejected |
| 2026-03 | Adopt cascading completion | Dooit | ✅ Borrowed |
| 2026-03 | Adopt priority cycling | Dooit | ✅ Borrowed |
| 2026-03 | Adopt sort overlay | Dooit | ✅ Borrowed |
| 2026-03 | Adopt help screen (auto-gen) | Dooit | ✅ Borrowed |
| 2026-03 | Adopt CLI-for-every-action philosophy | Taskwarrior | 🔄 Transformed |
| 2026-03 | Reject sync server | Taskwarrior | 🚫 Rejected |
| 2026-03 | Reject hook scripts | Taskwarrior | 🚫 Rejected |
| 2026-03 | Adopt vim keybinding muscle memory | Vim/Neovim | ✅ Borrowed |
| 2026-03 | Adopt search-as-dim (not hide) | Mutsumi original | 📌 Kept |
| 2026-03 | Adopt scope hybrid resolution | Mutsumi original | 📌 Kept |
| 2026-03 | Adopt `extra="allow"` strategy | Mutsumi original | 📌 Kept |
| 2026-03 | Adopt triple input parity | Mutsumi original + Linear inspiration | 📌 Kept |
| 2026-03 | Adopt recurrence via extra fields | Taskwarrior (adapted) | 🔄 Transformed |
| 2026-03 | Adopt effort display via extra fields | Dooit/Taskwarrior (adapted) | 🔄 Transformed |
| 2026-03 | Adopt custom CSS injection | Textual ecosystem | ✅ Borrowed |
| 2026-03 | Adopt dynamic column layout | Taskwarrior report columns | 🔄 Transformed |
| 2026-03 | Reject natural language dates | Todoist/Ultralist | 🚫 Rejected |
| 2026-03 | Reject cloud sync | Todoist/Notion | 🚫 Rejected |
