# Mutsumi Friend Beta — Usage SOP

> **[中文版](./BETA_USAGE_cn.md)**

This is the English beta usage guide for the current **`1.0.0b1`** line.
It is meant for internal testing and friend beta onboarding.

---

## 0. Prerequisites

- macOS / Linux terminal
- Windows users: prefer WSL for beta testing
- Python 3.12+
- `uv` or `pip`

If `uv` is missing:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

---

## 1. Install

### Option A — PyPI package

```bash
uv tool install mutsumi-tui
# or
pip install mutsumi-tui
```

### Option B — from source / git

```bash
uv tool install git+https://github.com/ywh555hhh/Mutsumi.git
```

Verify:

```bash
mutsumi --version
# Expected: mutsumi, version 1.0.0b1
```

If you see `command not found`, ensure your tool bin directory is in `PATH`.

---

## 2. First Launch

```bash
cd ~/your-project
mutsumi
```

If this is your first run, Mutsumi shows onboarding.
If you already completed onboarding, it opens directly.

### What onboarding configures

- language
- keybindings
- theme
- workspace mode
- optional agent integration

### Current defaults

- Theme: `monochrome-zen`
- Keybindings: `arrows`
- Language: `en`

---

## 3. Initialize Task Files Explicitly (Optional)

You do **not** have to initialize files manually before using Mutsumi, but the CLI supports it.

```bash
mutsumi init                # create ./mutsumi.json
mutsumi init --personal     # create ~/.mutsumi/mutsumi.json
mutsumi init --project      # create ./mutsumi.json and register current repo
```

For older setups, Mutsumi still reads `tasks.json` automatically as a fallback.

---

## 4. Create Your First Tasks

### Option A: CLI

```bash
mutsumi add "Fix login bug" --priority high --scope day --tags "bugfix"
mutsumi add "Write weekly report" --priority normal --scope week --tags "life"
mutsumi add "Update docs" --priority low --scope month --tags "docs"
```

Verify:

```bash
mutsumi list
mutsumi validate
```

### Option B: Let your AI agent write the file

Tell the agent:

> This project uses Mutsumi. Tasks should go into `./mutsumi.json`.
> If only legacy `tasks.json` exists, use that instead.
> Read the whole file, modify the `tasks` array, and write it back atomically.

### Option C: Create personal tasks

```bash
mutsumi init --personal
```

Then launch Mutsumi again to see the personal source in multi-source mode.

---

## 5. Launch the TUI

```bash
mutsumi
```

Default file resolution:

1. explicit `--path`
2. `./mutsumi.json`
3. `./tasks.json`
4. default new-file target: `./mutsumi.json`

To point at another file:

```bash
mutsumi --path /path/to/mutsumi.json
```

To watch additional task files:

```bash
mutsumi --watch /path/to/project-a/mutsumi.json --watch /path/to/project-b/mutsumi.json
```

---

## 6. What You Should See

### Single-source view

```text
[Today] [Week] [Month] [Inbox]                    mutsumi ♪
------------------------------------------------------------
▼ HIGH
[ ] Fix login bug                        bugfix        ★★★

▼ NORMAL
[ ] Write weekly report                  life          ★★

▼ LOW
[ ] Update docs                          docs          ★
------------------------------------------------------------
3 tasks · 0 done · 3 pending
```

### Multi-source view

```text
[★ Main] [Personal] [your-project]                     mutsumi ♪
---------------------------------------------------------------
★ Main Dashboard

★ Personal      2 pending
  • Buy coffee beans
  • Reply to advisor

your-project    3 pending
  • Fix login bug
  • Update docs
```

---

## 7. Keyboard Controls

### Default preset: `arrows`

| Key | Action |
|---|---|
| `Up` / `Down` | Move selection |
| `Home` / `End` | Jump top / bottom |
| `Left` / `Right` | Collapse / expand |
| `Space` | Toggle done |
| `Enter` | Open detail panel |
| `n` | New task |
| `e` | Edit task |
| `i` | Inline edit title |
| `A` | Add subtask |
| `Tab` / `Shift+Tab` | Next / previous source tab |
| `1-9` | Jump to source tab |
| `f` | Cycle scope filter |
| `/` | Search |
| `s` | Sort |
| `?` | Help |
| `q` | Quit |

### Alternative presets

- `vim`
- `emacs`

These are opt-in. They are **not** the default beta preset.

### Mouse

- click source tabs to switch sources
- click scope chips to change the filter
- click a task row to select it
- click a title to open the detail panel
- click a checkbox to toggle done
- click footer actions such as new task or search

---

## 8. Agent Integration

### Option A: Skills-first setup (recommended)

```bash
mutsumi setup --agent claude-code
mutsumi setup --agent codex-cli
mutsumi setup --agent gemini-cli
mutsumi setup --agent opencode
```

This installs bundled Mutsumi skills into the agent's skill directory.
It does **not** modify `CLAUDE.md`, `AGENTS.md`, or similar project files.

### Option B: Skills + project doc injection

```bash
mutsumi setup --agent claude-code --mode skills+project-doc
```

This installs skills and appends a Mutsumi integration snippet to the agent's project instruction file.

### Option C: Manual snippet

```bash
mutsumi setup --agent aider --mode snippet
mutsumi setup --agent custom --mode snippet
```

This prints copyable instructions.

### Quick manual prompt

```text
This project uses Mutsumi for task management.
Prefer ./mutsumi.json; use ./tasks.json only if the project is still on the legacy filename.
Read the whole file, modify the tasks array, preserve unknown fields, and write the file back atomically.
```

---

## 9. tmux / Split-pane Setup

### tmux (recommended)

```bash
bash scripts/tmux-dev.sh
```

### Manual split

```bash
tmux new-session -d -s dev
tmux split-window -h -p 35 "mutsumi"
tmux select-pane -t 0
tmux attach -t dev
```

### iTerm2 / VS Code / Cursor

- split the terminal vertically
- right pane: `mutsumi`
- left pane: your agent or shell

Now ask the agent to add or update tasks. The TUI should refresh automatically.

---

## 10. CLI Reference

```bash
# CRUD
mutsumi add "title" [-P high|normal|low] [-s day|week|month|inbox] [-t "tag1,tag2"] [-d "description"]
mutsumi done <id-prefix>
mutsumi edit <id-prefix> [--title "new"] [--priority high] [--scope week] [--tags "a,b"]
mutsumi rm <id-prefix>
mutsumi list

# Setup / onboarding
mutsumi init
mutsumi init --personal
mutsumi init --project
mutsumi setup --agent <name>
mutsumi setup --agent <name> --mode skills+project-doc
mutsumi setup --agent <name> --mode snippet
mutsumi project add /path/to/repo
mutsumi project list
mutsumi migrate

# Validation / schema
mutsumi validate
mutsumi schema
mutsumi --version
```

Any unique task ID prefix is usually enough for CLI commands.

---

## 11. Configuration Reference

Preferred config path:

```text
~/.mutsumi/config.toml
```

Legacy fallback path:

```text
~/.config/mutsumi/config.toml
```

Example:

```toml
theme = "monochrome-zen"
keybindings = "arrows"
language = "en"
default_scope = "day"
default_tab = "main"
notification_mode = "quiet"
```

---

## 12. Task File Schema

Canonical filename: `mutsumi.json`
Legacy fallback: `tasks.json`

```json
{
  "version": 1,
  "tasks": [
    {
      "id": "01EXAMPLE000000000000000001",
      "title": "Task title",
      "status": "pending",
      "scope": "day",
      "priority": "normal",
      "tags": ["dev", "urgent"],
      "children": [],
      "created_at": "2026-03-23T08:00:00Z",
      "due_date": "2026-03-25",
      "completed_at": null,
      "description": "Optional description"
    }
  ]
}
```

Unknown fields are preserved.

---

## 13. Troubleshooting

### `mutsumi` command not found

Ensure your tool bin directory is in `PATH`.

### TUI shows nothing but the file exists

- check which source tab you are on
- check the active scope filter
- run `mutsumi validate`

### Agent changes do not appear

- ensure the agent writes to the same file Mutsumi is watching
- prefer `mutsumi.json`
- if the repo still uses legacy `tasks.json`, ensure that is the watched file
- validate the file with `mutsumi validate`

### Theme or keybindings are not applied

- run `mutsumi config --show` if available in your workflow
- verify `~/.mutsumi/config.toml`
- remember the default keybinding preset is `arrows`

---

## 14. Current Beta Positioning

For the current beta line:

- version string is **`1.0.0b1`**
- canonical task file is **`mutsumi.json`**
- legacy fallback is **`tasks.json`**
- default preset is **`arrows`**
- multi-source dashboard is already part of the shipped beta surface
- calendar is a planned feature, not a shipped beta view yet
