# Mutsumi Friend Beta — Usage SOP

> **[中文版](./BETA_USAGE_cn.md)**

This is the step-by-step guide for beta testers. Follow it top to bottom.

---

## 0. Prerequisites

- macOS / Linux terminal (Windows: use WSL)
- `uv` installed — if not:
  ```bash
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```

---

## 1. Install

```bash
uv tool install git+https://github.com/ywh555hhh/Mutsumi.git
```

Verify:
```bash
mutsumi --version
# Expected: mutsumi, version 0.4.0b1
```

If you see `command not found`, ensure `~/.local/bin` is in your `PATH`:
```bash
export PATH="$HOME/.local/bin:$PATH"
```

---

## 2. Initialize Config (Optional)

```bash
mutsumi init --defaults
```

This creates `~/.config/mutsumi/config.toml` with default settings:
- Theme: `monochrome-zen`
- Keybindings: `vim`
- Language: `en`

To customize:
```bash
mutsumi init --lang zh          # Chinese
mutsumi init --lang ja          # Japanese
```

Or edit directly:
```bash
mutsumi config --edit           # Opens in $EDITOR
mutsumi config --show           # Print current config
```

**Skip this step entirely if you just want defaults — Mutsumi works without any config file.**

---

## 3. Create Your First Tasks

### Option A: CLI (recommended for quick start)

```bash
cd ~/your-project

mutsumi add "Fix login bug" --priority high --scope day --tags "bugfix"
mutsumi add "Write weekly report" --priority normal --scope week --tags "life"
mutsumi add "Update docs" --priority low --scope month --tags "docs"
```

Verify:
```bash
mutsumi list
# Should show 3 tasks
cat tasks.json
# Should be valid JSON with 3 tasks
```

### Option B: Let your AI Agent create tasks

Just ask your agent:
> "Create a tasks.json in the current directory with a few sample tasks."

The agent will write `tasks.json` directly. Mutsumi watches this file.

### Option C: Copy the example file

```bash
# From Mutsumi source (if you cloned it)
cp examples/tasks.json ./tasks.json
```

---

## 4. Launch the TUI

```bash
mutsumi
```

This watches `./tasks.json` in the current directory and renders the task board.

To watch a file in a different location:
```bash
mutsumi --path /path/to/tasks.json
```

### What You Should See

```
[Today] Week  Month  Inbox              mutsumi
─────────────────────────────────────────────────
▼ HIGH ─────────────────────────────────────
[ ] Fix login bug                  bugfix  ★★★

▼ NORMAL ───────────────────────────────────
[ ] Write weekly report            life    ★★

▼ LOW ──────────────────────────────────────
[ ] Update docs                    docs    ★

─────────────────────────────────────────────────
3 tasks · 0 done · 3 pending
```

---

## 5. Keyboard Controls

### Navigation (vim preset — default)

| Key | Action |
|-----|--------|
| `j` / `k` | Move down / up |
| `G` | Jump to bottom |
| `gg` | Jump to top |
| `1` `2` `3` `4` | Switch to Today / Week / Month / Inbox tab |
| `Tab` / `Shift+Tab` | Next / Previous tab |
| `q` | Quit |

### Task Operations

| Key | Action |
|-----|--------|
| `Space` | Toggle done/pending |
| `n` | New task (opens form) |
| `e` | Edit task (opens form) |
| `dd` | Delete task (confirm with `y`) |
| `i` | Inline edit title |
| `Enter` | Show task detail panel |
| `Escape` | Close detail panel |

### Other

| Key | Action |
|-----|--------|
| `/` | Open search bar (filter tasks by title/tag) |
| `+` / `-` | Increase / decrease priority |
| `J` / `K` | Move task down / up in list |
| `h` / `l` | Collapse / expand priority group |
| `z` | Toggle fold (show/hide subtasks) |
| `y` | Copy task |
| `p` | Paste task below |
| `A` (Shift+a) | Add subtask |
| `s` | Sort tasks |
| `?` | Show help screen |

### Mouse

- **Click** tab buttons to switch tabs
- **Click** a task row to select it
- **Click** `[+New]` / `[/Search]` in footer bar
- **Click** the checkbox area to toggle done/pending
- **Click** the title area to open detail panel

---

## 6. tmux Split-pane Setup (Recommended)

Run your agent on the left, Mutsumi on the right:

```bash
# If you cloned the repo:
bash scripts/tmux-dev.sh

# Or manually:
tmux new-session -d -s dev
tmux split-window -h -p 30 "mutsumi"
tmux select-pane -t 0
tmux attach -t dev
```

Now in the left pane, use your agent normally. Every time the agent writes to `tasks.json`, the right pane updates instantly.

### iTerm2 Alternative

1. `Cmd+D` to split vertically
2. Right pane: `mutsumi`
3. Left pane: your agent / shell

---

## 7. Agent Integration

### Option A: Manual (works with any agent)

Tell your agent this when starting a session:

> This project uses Mutsumi for task management. Tasks live in `./tasks.json`.
> Read the file, modify the `tasks` array, write the entire file back.
> Required fields: `id` (unique string), `title` (string), `status` ("pending" or "done").
> Optional: `scope` ("day"/"week"/"month"/"inbox"), `priority` ("high"/"normal"/"low"), `tags` (string[]), `description` (string).

### Option B: Auto-inject (Claude Code / Codex CLI / Gemini CLI)

```bash
cd ~/your-project
mutsumi setup --agent claude-code   # Appends rules to CLAUDE.md
mutsumi setup --agent codex-cli     # Appends to AGENTS.md
mutsumi setup --agent gemini-cli    # Appends to GEMINI.md
```

This appends a `## Mutsumi Task Integration` section to the agent's config file. The agent will automatically know how to read/write `tasks.json`.

Verify:
```bash
cat CLAUDE.md   # Should contain "## Mutsumi Task Integration" at the end
```

Running setup again is safe — it won't duplicate the section.

### Option C: Other agents (Aider / OpenCode / custom)

```bash
mutsumi setup --agent custom        # Prints the prompt to stdout
```

Copy the output and paste it into your agent's system prompt or config.

---

## 8. CLI Reference (Full)

```bash
# Task CRUD
mutsumi add "title" [-P high|normal|low] [-s day|week|month|inbox] [-t "tag1,tag2"] [-d "description"]
mutsumi done <id-prefix>            # Mark task as done
mutsumi edit <id-prefix> [--title "new"] [--priority high] [--scope week] [--tags "a,b"]
mutsumi rm <id-prefix>              # Delete task
mutsumi list                        # List all tasks

# Setup
mutsumi init                        # Interactive setup
mutsumi init --defaults             # Non-interactive, all defaults
mutsumi init --lang zh              # Set language
mutsumi setup --agent <name>        # Agent integration
mutsumi setup                       # List available agents

# Config
mutsumi config --edit               # Open in $EDITOR
mutsumi config --show               # Print config
mutsumi config --reset              # Reset to defaults
mutsumi config --path               # Print config file path

# Utility
mutsumi validate                    # Validate tasks.json
mutsumi schema                      # Print JSON Schema
mutsumi --version                   # Print version
```

**ID prefix matching**: You don't need to type the full 26-char task ID. Any unique prefix works:
```bash
mutsumi done 01EX    # Matches "01EXAMPLE000000000000000001" if unique
```

---

## 9. Configuration Reference

Config file: `~/.config/mutsumi/config.toml`

```toml
# Theme — "monochrome-zen" (default), "solarized", "nord", "dracula"
theme = "monochrome-zen"

# Keybindings — "vim" (default), "emacs", "arrows"
keybindings = "vim"

# Language — "en" (default), "zh", "ja"
language = "en"

# Default task file path (optional)
# default_path = "/path/to/tasks.json"

# Columns to show in task list
columns = ["checkbox", "title", "tags", "priority"]

# Event log (optional — JSONL format)
# event_log_path = "~/.local/share/mutsumi/events.jsonl"

# Custom CSS overrides (optional)
# custom_css_path = "~/.config/mutsumi/custom.tcss"
```

---

## 10. tasks.json Schema

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
      "created_at": "2026-03-21T08:00:00Z",
      "due_date": "2026-03-25",
      "completed_at": null,
      "description": "Optional description"
    }
  ]
}
```

| Field | Required | Type | Values |
|-------|----------|------|--------|
| `id` | yes | string | Unique, 26-char recommended |
| `title` | yes | string | Task title |
| `status` | yes | string | `"pending"` or `"done"` |
| `scope` | no | string | `"day"` `"week"` `"month"` `"inbox"` (default: `"inbox"`) |
| `priority` | no | string | `"high"` `"normal"` `"low"` (default: `"normal"`) |
| `tags` | no | string[] | Arbitrary tags |
| `children` | no | Task[] | Nested subtasks (same schema) |
| `due_date` | no | string | ISO date `"2026-03-25"` |
| `description` | no | string | Longer description |
| `created_at` | no | string | ISO datetime |
| `completed_at` | no | string | ISO datetime, set when done |

**Rule**: Unknown fields are preserved — Mutsumi never deletes fields it doesn't recognize.

---

## 11. Uninstall

```bash
uv tool uninstall mutsumi
rm -rf ~/.config/mutsumi/           # Config (optional)
rm -rf ~/.local/share/mutsumi/      # Logs (optional)
# tasks.json is YOUR data — keep or delete manually
```

---

## 12. Troubleshooting

### `mutsumi` command not found
```bash
export PATH="$HOME/.local/bin:$PATH"
# Add to ~/.bashrc or ~/.zshrc to persist
```

### TUI shows "Nothing here yet" but tasks.json has tasks
Check which tab you're on — tasks are filtered by scope. Press `2` for Week, `3` for Month, `4` for Inbox.

### Agent changes don't show up in TUI
- Ensure the agent writes to the same `tasks.json` path Mutsumi is watching
- Check that the JSON is valid: `mutsumi validate`

### Theme / keybindings not applied
- Run `mutsumi config --show` to verify config is loaded
- Config location: `~/.config/mutsumi/config.toml`

---

## 13. Feedback

File issues or feedback at: https://github.com/ywh555hhh/Mutsumi/issues

Or reach out directly to Wayne.

---

*mutsumi — "harmony, closeness". She doesn't tell you what to do. She just waits quietly.*
