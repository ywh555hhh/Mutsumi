# Mutsumi TUI Specification

| Version | 0.1.0              |
|---------|---------------------|
| Status  | Draft               |
| Date    | 2026-03-21          |

> **[中文版](./TUI_SPEC_cn.md)** | **[日本語版](./TUI_SPEC_ja.md)**

---

## 1. Layout

### 1.1 Default Layout

```
┌─────────────────────────────────────────────────────┐
│  [Today] [Week] [Month] [Inbox]          mutsumi ♪  │  ← Header (1 line)
├─────────────────────────────────────────────────────┤
│                                                     │
│  ▼ HIGH ─────────────────────────────────────────   │  ← Priority Group
│  [ ] 重構 Auth 模块                dev,backend ★★★  │  ← Task Row
│  [x] 修復缓存穿透 Bug            bugfix       ★★★  │
│                                                     │
│  ▼ NORMAL ───────────────────────────────────────   │
│  [ ] 写周报                       life         ★★   │
│  [ ] Review PR #42                dev          ★★   │
│    └─ [ ] 检查类型安全            (1/2)             │  ← Nested child
│    └─ [x] 跑通测试                                  │
│                                                     │
│  ▼ LOW ──────────────────────────────────────────   │
│  [ ] 更新 README                  docs         ★   │
│                                                     │
├─────────────────────────────────────────────────────┤
│  6 tasks · 2 done · 4 pending              🔇 quiet │  ← Footer (1 line)
└─────────────────────────────────────────────────────┘
```

### 1.2 Responsive Behavior

Mutsumi adapts to the terminal window size.

| Terminal Width  | Behavior                                                     |
|-----------------|--------------------------------------------------------------|
| ≥ 80 cols       | Full layout: title + tags + priority stars                   |
| 60-79 cols      | Tags omitted, show title + priority only                     |
| 40-59 cols      | Minimal mode: checkbox + title only                          |
| < 40 cols       | Show "Terminal too narrow" warning                           |

### 1.3 Detail Panel (Expandable)

Select a task and press `Enter` (or click) to expand the detail panel at the bottom.

```
├─────────────────────────────────────────────────────┤
│  ▶ 重构 Auth 模块                                    │
│  ─────────────────────────────────────────────────   │
│  Status:   pending                                   │
│  Priority: high                                      │
│  Scope:    day                                       │
│  Tags:     dev, backend                              │
│  Due:      2026-03-25                                │
│  Created:  2026-03-21 08:00                          │
│  ─────────────────────────────────────────────────   │
│  Description:                                        │
│  把 session-based auth 改成 JWT，需要同时改           │
│  middleware 和路由层。                                │
│  ─────────────────────────────────────────────────   │
│  Subtasks: 1/2 done                                  │
│    [x] 安装 PyJWT                                    │
│    [ ] 写 middleware                                 │
├─────────────────────────────────────────────────────┤
```

## 2. Interaction

### 2.1 Mouse

| Action                    | Behavior                                             |
|---------------------------|------------------------------------------------------|
| Click `[ ]` / `[x]`      | Toggle done status, write back to JSON               |
| Click task row            | Select task (highlight)                              |
| Double-click title        | Enter inline edit mode                               |
| Click Tab                 | Switch view (Today/Week/Month/Inbox)                 |
| Click [+New]              | Open new task input dialog                           |
| Scroll wheel              | Scroll the task list                                 |

### 2.2 Keyboard Presets

#### vim (default)

| Key      | Action                                |
|----------|---------------------------------------|
| `j`      | Move cursor down                      |
| `k`      | Move cursor up                        |
| `g`      | Jump to top of list                   |
| `G`      | Jump to bottom of list                |
| `Space`  | Toggle done status                    |
| `Enter`  | Expand/collapse detail panel          |
| `n`      | New task (open input dialog)          |
| `e`      | Edit selected task title              |
| `dd`     | Delete selected task (requires confirm) |
| `Tab`    | Switch to next view Tab               |
| `S-Tab`  | Switch to previous view Tab           |
| `1-4`    | Quick switch to Nth Tab               |
| `/`      | Search tasks                          |
| `q`      | Quit Mutsumi                          |
| `?`      | Show keybinding help                  |

#### emacs

| Key        | Action                                |
|------------|---------------------------------------|
| `C-n`      | Move cursor down                      |
| `C-p`      | Move cursor up                        |
| `C-Space`  | Toggle done status                    |
| `C-o`      | New task                              |
| `C-e`      | Edit task                             |
| `C-d`      | Delete task                           |
| `C-q`      | Quit                                  |

#### arrow

| Key        | Action                                        |
|------------|-----------------------------------------------|
| `Down`     | Move cursor down                              |
| `Up`       | Move cursor up                                |
| `Enter`    | Toggle done status / confirm edit             |
| `Delete`   | Delete task                                   |
| `Insert`   | New task                                      |

### 2.3 Custom Keymap

Users can define custom keybindings in `~/.config/mutsumi/keys/custom.toml`.

```toml
[keys]
move_down = "j"
move_up = "k"
toggle_done = "space"
new_task = "n"
edit_task = "e"
delete_task = "d,d"    # chord: two key presses
quit = "q"
search = "/"
help = "?"
tab_next = "tab"
tab_prev = "shift+tab"
tab_1 = "1"
tab_2 = "2"
tab_3 = "3"
tab_4 = "4"
expand = "enter"
top = "g"
bottom = "shift+g"
```

## 3. CRUD Operations

### 3.1 Create Task

Trigger: `n` key or click [+New] button.

```
┌─────────── New Task ───────────┐
│ Title: [                     ] │
│ Scope: (Day) Week Month Inbox  │
│ Priority: High (Normal) Low    │
│ Tags: [                     ]  │
│                                │
│        [Create]  [Cancel]      │
└────────────────────────────────┘
```

- Title is the only required field
- Scope/Priority defaults to the current Tab and Normal
- Tags accept comma-separated input
- UUIDv7 ID and created_at are auto-generated on creation

### 3.2 Edit Task

Trigger: `e` key or double-click the title.

- Inline edit: the title becomes an editable text field directly in the list row
- Press `Enter` to confirm, `Escape` to cancel
- Changes are immediately written back to JSON

### 3.3 Delete Task

Trigger: `dd` key or context menu.

- A confirmation dialog is shown (can be disabled in config)
- The task is removed from JSON after deletion
- A `task_deleted` event is emitted

### 3.4 Toggle Status

Trigger: `Space` key or mouse click on checkbox.

- `pending` → `done`: auto-fills `completed_at`
- `done` → `pending`: clears `completed_at`
- Immediately written back to JSON, no confirmation step (snappy feel)

## 4. Hot Reload

### 4.1 Mechanism

```
watchdog (inotify/FSEvents/kqueue)
         │
         ▼
  File change event
         │
         ▼
  debounce (100ms)  ← Prevent jitter from rapid writes
         │
         ▼
  re-read tasks.json
         │
         ▼
  validate schema
         │
    ┌────┴────┐
    ▼         ▼
  valid    invalid
    │         │
    ▼         ▼
  re-render  show error
  TUI        banner
```

### 4.2 Debounce

- Wait 100ms after file change before reading (wait for write to complete)
- Multiple changes within 100ms are merged into a single re-read
- The debounce value is configurable in config

## 5. Theme System

### 5.1 Theme File Format

```toml
# ~/.config/mutsumi/themes/my-theme.toml

[meta]
name = "My Custom Theme"
author = "wayne"

[colors]
background = "#1e1e2e"
foreground = "#cdd6f4"
accent = "#94e2d5"
muted = "#6c7086"
error = "#f38ba8"
warning = "#fab387"
success = "#a6e3a1"

[priority_colors]
high = "#f38ba8"
normal = "#cdd6f4"
low = "#6c7086"

[tag_colors]
dev = "#89b4fa"
bugfix = "#f38ba8"
life = "#a6e3a1"
docs = "#fab387"
# Unmatched tags use accent color
```

### 5.2 Built-in Themes

| Theme               | Vibe                                                |
|----------------------|-----------------------------------------------------|
| `monochrome-zen`     | Minimalist B&W with light cyan accent (default)     |
| `nord`               | Cool tones, restrained                              |
| `dracula`            | High contrast, purple-tinted                        |
| `solarized`          | Warm dark, teal accent                              |

## 6. Search

Press `/` to enter search mode.

```
┌─────────────────────────────────────────┐
│  🔍 Search: auth mod█                   │
├─────────────────────────────────────────┤
│  [ ] 重构 Auth 模块          dev   ★★★  │  ← Matching results highlighted
│  [x] 修复 Auth token 过期    bugfix     │
└─────────────────────────────────────────┘
```

- Real-time filtering (filters as you type)
- Search scope: title + tags + description
- `Escape` exits search and restores the full list

## 7. Error States

### 7.1 Error Banner

When `tasks.json` is unreadable or malformed:

```
┌─────────────────────────────────────────────────────┐
│  ⚠ tasks.json has errors · showing last valid state  │
│  Run `mutsumi validate` for details                  │
├─────────────────────────────────────────────────────┤
│  (Last valid task list)                              │
│  ...                                                 │
└─────────────────────────────────────────────────────┘
```

### 7.2 Warning Badge

When individual task fields are abnormal, the task row displays a warning badge but remains interactive.

### 7.3 Empty State

When `tasks.json` is empty or there are no tasks for the current Tab:

```
┌─────────────────────────────────────────┐
│                                         │
│           Nothing here yet.             │
│       Press [n] to create a task        │
│    or let your Agent write tasks.json   │
│                                         │
└─────────────────────────────────────────┘
```
