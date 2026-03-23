# Mutsumi TUI Specification

| Version | 1.0 |
|---------|-----|
| Status  | Draft |
| Date    | 2026-03-23 |

> **[中文版](./TUI_SPEC_cn.md)** | **[日本語版](./TUI_SPEC_ja.md)**

---

## 1. Layout

### 1.1 Default layout

In multi-source mode, Mutsumi uses dynamic source tabs plus a second-level scope filter.

```text
┌──────────────────────────────────────────────────────────────┐
│ [★ Main] [Personal] [saas-app] [docs-site]       mutsumi ♪  │
├──────────────────────────────────────────────────────────────┤
│ ★ Main │ [Today] [Week] [Month] [Inbox] [All]               │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  ▼ HIGH ───────────────────────────────────────────────      │
│  [ ] Refactor auth module                 dev,backend  ★★★   │
│  [x] Fix cache bug                        bugfix       ★★★   │
│                                                              │
│  ▼ NORMAL ─────────────────────────────────────────────      │
│  [ ] Write weekly report                  life         ★★    │
│  [ ] Review PR #42                        dev          ★★    │
│    └─ [ ] Check type safety                               │
│    └─ [x] Run tests                                        │
│                                                              │
├──────────────────────────────────────────────────────────────┤
│  6 tasks · 2 done · 4 pending                      🔇 quiet  │
└──────────────────────────────────────────────────────────────┘
```

### 1.2 Main dashboard view

When the active source tab is `Main`, Mutsumi shows an aggregated dashboard instead of an editable task list.

```text
┌──────────────────────────────────────────────────────────────┐
│ [★ Main] [Personal] [saas-app] [docs-site]       mutsumi ♪  │
├──────────────────────────────────────────────────────────────┤
│                    ★ Main Dashboard                          │
│                                                              │
│  ★ Personal    3 pending                                     │
│  ████████░░░░░░░░░░ 40% (2/5)                                │
│    • Buy coffee beans                                        │
│    • Reply to advisor                                        │
│                                                              │
│  saas-app     5 pending                                      │
│  ███░░░░░░░░░░░░░░ 15% (1/7)                                 │
│    !!! • Fix token refresh                                   │
│    • Add rate limiting                                       │
└──────────────────────────────────────────────────────────────┘
```

### 1.3 Responsive behavior

| Terminal width | Behavior |
|---|---|
| `>= 80` cols | Full row: title + tags + priority |
| `60-79` cols | Reduced metadata |
| `40-59` cols | Minimal row layout |
| `< 40` cols | Show terminal-too-narrow warning |

### 1.4 Detail panel

Selecting a task and pressing `Enter` or clicking its title opens the detail panel.

The detail panel shows:

- title
- status
- priority
- scope
- tags
- due date
- description
- child progress
- created / completed timestamps

It also provides clickable actions:

- `[Edit]`
- `[+Sub]`
- `[Delete]`
- `[x]` to close

---

## 2. Interaction Model

### 2.1 Mouse

| Action | Behavior |
|---|---|
| Click checkbox | Toggle done state |
| Click task row | Select row |
| Click task title | Open detail panel |
| Click source tab | Switch source |
| Click scope chip | Change scope filter |
| Click footer action | Open task form, search, or sort |
| Click dashboard card | Jump to that source tab |
| Click `[+Sub]` in detail panel | Open subtask form |

### 2.2 Keyboard presets

Mutsumi ships with three built-in presets:

- `arrows` — **default**
- `vim`
- `emacs`

#### `arrows` (default)

| Key | Action |
|---|---|
| `Up` / `Down` | Move selection |
| `Home` / `End` | Jump to top / bottom |
| `Left` / `Right` | Collapse / expand group |
| `Shift+Up` / `Shift+Down` | Move task up / down |
| `Space` | Toggle done |
| `Enter` | Show detail |
| `n` | New task |
| `e` | Edit task |
| `i` | Inline edit title |
| `A` | Add subtask |
| `Tab` / `Shift+Tab` | Next / previous source tab |
| `1-9` | Jump to numbered source tab |
| `f` | Cycle scope filter |
| `/` | Search |
| `s` | Sort |
| `?` | Show help |
| `q` | Quit |

#### `vim`

| Key | Action |
|---|---|
| `j` / `k` | Move selection |
| `gg` / `G` | Top / bottom |
| `h` / `l` | Collapse / expand group |
| `J` / `K` | Move task down / up |
| `dd` | Delete with confirmation |
| `Space` | Toggle done |
| `Enter` | Show detail |
| `n` / `e` / `i` | New / edit / inline edit |
| `A` | Add subtask |
| `Tab` / `Shift+Tab` | Next / previous source tab |
| `f` | Cycle scope filter |
| `/` | Search |
| `?` | Help |
| `q` | Quit |

#### `emacs`

| Key | Action |
|---|---|
| `Ctrl+n` / `Ctrl+p` | Move selection |
| `Ctrl+a` / `Ctrl+e` | Top / bottom |
| `Ctrl+b` / `Ctrl+f` | Collapse / expand group |
| `Ctrl+Shift+n` / `Ctrl+Shift+p` | Move task |
| `Space` | Toggle done |
| `Enter` | Show detail |
| `n` / `e` / `i` | New / edit / inline edit |
| `A` | Add subtask |
| `Tab` / `Shift+Tab` | Next / previous source tab |
| `f` | Cycle scope filter |
| `/` | Search |
| `?` | Help |
| `Ctrl+q` | Quit |

### 2.3 Triple input parity

Mutsumi follows the product rule that key actions should be reachable by keyboard and mouse, and core task changes should also have CLI equivalents where relevant.

Examples:

| Capability | Keyboard | Mouse | CLI |
|---|---|---|---|
| Create task | `n` | footer action | `mutsumi add` |
| Edit task | `e` | `[Edit]` | `mutsumi edit` |
| Delete task | `dd` or delete flow | `[Delete]` | `mutsumi rm` |
| Toggle done | `Space` | checkbox | `mutsumi done` |
| Validate file | — | — | `mutsumi validate` |

---

## 3. Views and Filters

### 3.1 Source tabs

Source tabs represent data sources, not time scopes.
Examples:

- `Main`
- `Personal`
- registered projects such as `saas-app`

### 3.2 Scope filter

Inside editable tabs, Mutsumi shows a second-level filter:

- `Today`
- `Week`
- `Month`
- `Inbox`
- `All`

The `Main` dashboard hides the scope filter.

### 3.3 Scope semantics

Scope filtering uses the effective scope from the data contract:

```text
explicit scope > due_date auto-derivation > inbox
```

This means `due_date` influences list placement even when no explicit scope was set.

---

## 4. CRUD Behavior

### 4.1 Create task

Trigger:

- keyboard: `n`
- mouse: footer new-task action

Behavior:

- opens task form
- `title` is required
- scope defaults to current filter context when relevant
- file is written atomically after submit

### 4.2 Edit task

Trigger:

- keyboard: `e`
- keyboard inline: `i`
- mouse: `[Edit]` in detail panel

Behavior:

- updates the task in memory
- writes back atomically
- preserves unknown fields

### 4.3 Delete task

Trigger:

- keyboard delete flow
- mouse `[Delete]`

Behavior:

- requires confirmation
- removes the selected task
- writes back atomically

### 4.4 Toggle status

Trigger:

- keyboard `Space`
- mouse checkbox click

Behavior:

- `pending` → `done`: fills `completed_at`
- `done` → `pending`: clears `completed_at`
- recurring task handling may update the due date according to recurrence metadata

---

## 5. Hot Reload

### 5.1 File watch behavior

Mutsumi watches each registered source file independently.

```text
external save
   ↓
watchdog event
   ↓
debounce
   ↓
re-read active source(s)
   ↓
re-render TUI
```

### 5.2 Multi-source behavior

- in single-source mode, one file is watched
- in multi-source mode, all registered source files are watched
- dashboard stats aggregate tasks across all loaded sources

### 5.3 Self-write suppression

Mutsumi suppresses immediate self-triggered reloads around its own atomic writes to avoid redundant refreshes.

---

## 6. Error and Empty States

### 6.1 Invalid JSON

If the active task file becomes invalid JSON:

- Mutsumi shows an error banner
- the app does not crash
- the user can fix the file and continue

Example banner:

```text
⚠ JSON is invalid — showing last valid state
```

### 6.2 Missing file

If the active file does not yet exist:

- the UI shows an empty usable state
- task creation can create the file on first write
- new projects should create `mutsumi.json`

### 6.3 Empty state

When there are no tasks in the current view, Mutsumi shows a friendly empty state with a `+ New Task` action.

The copy should reference the active task flow generically, not assume only `tasks.json`.

---

## 7. Theme and Config

### 7.1 Built-in themes

- `monochrome-zen` — default
- `solarized`
- `nord`
- `dracula`

### 7.2 Config home

Preferred config and personal-data home:

```text
~/.mutsumi/
```

Legacy config location remains readable for compatibility:

```text
~/.config/mutsumi/
```

### 7.3 Keybinding config

Default preset is:

```toml
keybindings = "arrows"
```

Users may switch to `vim` or `emacs`, and may define key overrides in config.

---

## 8. Calendar Readiness

This specification does not define a calendar UI yet, but current TUI semantics are intentionally compatible with a future time-based view.

Foundations already present:

- `due_date` in the task model
- effective scope derivation from dates
- multi-source aggregation
- dashboard/source separation
- detail panel drill-down

A future calendar view should build on these semantics rather than invent a second task model.

---

## 9. Current Beta Notes

For the current beta line:

- canonical task file is `mutsumi.json`
- legacy fallback is `tasks.json`
- default preset is `arrows`
- multi-source dashboard is already part of the product surface
- calendar is a planned capability, not a shipped view yet
