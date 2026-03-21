# RFC-002: Installation, Setup & Onboarding Experience

> **[中文版](./RFC-002-installation-and-onboarding_cn.md)** | **[日本語版](./RFC-002-installation-and-onboarding_ja.md)**

| Field       | Value                                                       |
|-------------|--------------------------------------------------------------|
| **RFC**     | 002                                                          |
| **Title**   | Installation, Setup & Onboarding                             |
| **Status**  | Draft                                                        |
| **Author**  | Wayne (ywh)                                                  |
| **Created** | 2026-03-21                                                   |

---

## 1. Abstract

This RFC defines how users install, configure, and start using Mutsumi. The core principle is **"crisp and effortless"** — every step must feel zero-friction: one command to install, one screen to configure, one second to launch.

## 2. Design Goals

| Goal | Description |
|---|---|
| **Zero-config works** | `mutsumi` with no args, no config file — just works |
| **All-at-once setup** | NOT a step-by-step wizard. One screen, all options, click to toggle |
| **Agent auto-install** | Agent runs one command, Mutsumi is ready |
| **Hackable from day 1** | Config is TOML, human-readable, git-friendly |
| **Uninstall cleanly** | One command removes everything, zero residue |

## 3. Installation Methods

### 3.1 Primary: `uv`

```bash
uv tool install mutsumi
```

- No Python pre-install needed — `uv` manages an isolated Python environment automatically.

After install, `mutsumi` is available globally as a CLI command.

### 3.2 Fallback: `pipx`

```bash
pipx install mutsumi
```

For users who prefer `pipx` over `uv`. Same isolated environment behavior.

### 3.3 Manual: git clone

```bash
git clone https://github.com/<user>/mutsumi.git
cd mutsumi
uv sync
uv run mutsumi
```

For contributors and hackers who want to modify the source.

### 3.4 One-liner for scripts

```bash
curl -fsSL https://mutsumi.dev/install.sh | sh
```

The install script:

1. Detects if `uv` is installed; if not, installs `uv` first
2. Runs `uv tool install mutsumi`
3. Prints a welcome message with next steps

## 4. First-run Experience

### 4.1 Zero-config Start

```bash
mutsumi
```

With no config file and no `tasks.json`, Mutsumi:

1. Starts with all defaults (English, monochrome theme, vim keys, quiet notifications)
2. Shows the empty state with a friendly prompt
3. Offers to create a `tasks.json` in the current directory

```
┌──────────────────────────────────────────────┐
│  [Today] [Week] [Month] [Inbox]    mutsumi   │
├──────────────────────────────────────────────┤
│                                              │
│         Welcome to Mutsumi.                  │
│                                              │
│    No tasks.json found in this directory.     │
│                                              │
│    [Create tasks.json here]                  │
│    [Open setup]   [Browse files...]          │
│                                              │
└──────────────────────────────────────────────┘
```

### 4.2 Interactive Setup: `mutsumi init`

**This is the core of the "crisp" experience.**

`mutsumi init` launches a **single-screen TUI settings panel**. ALL options are visible at once. No multi-step wizard. No "Next" buttons. Just click/tab through options and toggle.

#### 4.2.1 Setup Panel Wireframe

```
┌──────────────────────── mutsumi setup ─────────────────────────┐
│                                                                 │
│  ┌─ Basics ───────────────────────────────────────────────┐    │
│  │                                                         │    │
│  │  Language              (English)  中文                   │    │
│  │  Theme                 ● Monochrome  ○ Catppuccin       │    │
│  │                        ○ Nord        ○ Dracula          │    │
│  │  Keymap                ● vim   ○ emacs   ○ arrow        │    │
│  │                                                         │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                 │
│  ┌─ Behavior ─────────────────────────────────────────────┐    │
│  │                                                         │    │
│  │  Default View          ● Today  ○ Week  ○ Month  ○ Inbox│    │
│  │  Notifications         ● Quiet  ○ Badge ○ Bell  ○ System│    │
│  │  Task ID Format        ● UUIDv7 ○ ULID  ○ Auto-incr    │    │
│  │  Event Log             [x] Enabled                      │    │
│  │                                                         │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                 │
│  ┌─ Paths ────────────────────────────────────────────────┐    │
│  │                                                         │    │
│  │  Watch Path            [./tasks.json                  ] │    │
│  │  Config Dir            ~/.config/mutsumi/  (read-only)  │    │
│  │  Event Log Path        [./events.jsonl                ] │    │
│  │                                                         │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                 │
│  ┌─ Preview ──────────────────────────────────────────────┐    │
│  │                                                         │    │
│  │   config.toml:                                          │    │
│  │   ┌──────────────────────────────────────────────────┐  │    │
│  │   │ [general]                                        │  │    │
│  │   │ language = "en"                                  │  │    │
│  │   │ default_scope = "day"                            │  │    │
│  │   │                                                  │  │    │
│  │   │ [theme]                                          │  │    │
│  │   │ name = "monochrome"                              │  │    │
│  │   │                                                  │  │    │
│  │   │ [keys]                                           │  │    │
│  │   │ preset = "vim"                                   │  │    │
│  │   └──────────────────────────────────────────────────┘  │    │
│  │                                                         │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                 │
│          [ Save & Start ]           [ Cancel ]                  │
│                                                                 │
│  Config saved to ~/.config/mutsumi/config.toml                  │
└─────────────────────────────────────────────────────────────────┘
```

#### 4.2.2 Interaction Model

| Input | Behavior |
|---|---|
| `Tab` / `Shift+Tab` | Move focus between option groups |
| `←` `→` or mouse click | Toggle between choices within a group |
| `Space` or click | Toggle checkbox |
| Text fields | Direct typing, tab to confirm |
| `Enter` on [Save & Start] | Write config + create tasks.json + launch TUI |
| `Escape` or [Cancel] | Exit without saving |

#### 4.2.3 Live Preview

The bottom section shows a **live preview** of the `config.toml` that will be generated. Every toggle/change updates the preview instantly. This gives the user full transparency and confidence.

#### 4.2.4 What `mutsumi init` Creates

```
~/.config/mutsumi/
└── config.toml              ← User preferences

./tasks.json                 ← Sample tasks (if doesn't exist)
```

Sample `tasks.json` created by init:

```json
{
  "$schema": "https://mutsumi.dev/schema/v1.json",
  "version": 1,
  "tasks": [
    {
      "id": "01EXAMPLE000000000000000001",
      "title": "Welcome to Mutsumi! Toggle me with Space or click the checkbox.",
      "status": "pending",
      "scope": "day",
      "priority": "normal",
      "tags": ["tutorial"],
      "children": []
    },
    {
      "id": "01EXAMPLE000000000000000002",
      "title": "Try editing this task with 'e' key",
      "status": "pending",
      "scope": "day",
      "priority": "low",
      "tags": ["tutorial"],
      "children": []
    }
  ]
}
```

### 4.3 Config Edit After Setup

```bash
mutsumi config --edit       # Opens config.toml in $EDITOR
mutsumi config --show       # Prints current config to stdout
mutsumi config --reset      # Reset to defaults (with confirmation)
mutsumi init                # Re-run setup panel (overwrites existing config)
```

## 5. Agent Auto-setup

### 5.1 The Problem

Users want their AI agents to automatically know about `tasks.json` and how to read/write it. Setting this up manually (copying prompt templates, configuring file paths) is friction.

### 5.2 `mutsumi setup --agent`

```bash
mutsumi setup --agent claude-code
mutsumi setup --agent codex-cli
mutsumi setup --agent aider
mutsumi setup --agent opencode
mutsumi setup --agent custom
```

#### 5.2.1 What It Does

For each supported agent, `mutsumi setup --agent <name>` performs:

| Agent | Action |
|---|---|
| `claude-code` | Appends Mutsumi integration rules to project-level `CLAUDE.md` |
| `codex-cli` | Creates/updates `codex.md` or agent instructions |
| `aider` | Appends to `.aider.conf.yml` conventions |
| `opencode` | Updates `opencode.md` instructions |
| `custom` | Prints the prompt template to stdout for manual integration |

#### 5.2.2 Injected Prompt Template

The prompt injected into agent configs:

```markdown
## Mutsumi Task Integration

This project uses Mutsumi for task management. Tasks are stored in `./tasks.json`.

When the user asks you to manage tasks (add, complete, delete, organize):
1. Read `./tasks.json`
2. Modify the tasks array following this schema:
   - Required: `id` (unique string), `title` (string), `status` ("pending"|"done")
   - Optional: `scope` ("day"|"week"|"month"|"inbox"), `priority` ("high"|"normal"|"low"), `tags` (string[]), `children` (Task[]), `due_date` (ISO date), `description` (string)
3. Write the entire file back (preserve unknown fields)
4. Use atomic write (temp file + rename) when possible
5. Generate UUIDv7 or any unique string for new task IDs

The Mutsumi TUI watches this file and re-renders automatically.
```

#### 5.2.3 Interactive Agent Setup

Running `mutsumi setup --agent` with no agent name launches a picker:

```
┌──────────── Select your Agent ────────────────────────────────┐
│                                                                │
│  Which agent do you use? (click or arrow+enter)                │
│                                                                │
│  ● Claude Code     → writes to CLAUDE.md                       │
│  ○ Codex CLI       → writes to codex.md                        │
│  ○ Aider           → writes to .aider.conf.yml                 │
│  ○ OpenCode        → writes to opencode.md                     │
│  ○ Gemini CLI      → writes to GEMINI.md                       │
│  ○ Custom          → prints prompt to stdout                   │
│                                                                │
│  [Setup]  [Cancel]                                             │
│                                                                │
│  Hint: You can run this for multiple agents.                   │
└────────────────────────────────────────────────────────────────┘
```

### 5.3 Agent One-liner Install+Setup

For the ultimate zero-friction agent experience:

```bash
# Agent (e.g., Claude Code) can run this single command:
uv tool install mutsumi && mutsumi init --defaults && mutsumi setup --agent claude-code
```

This:

1. Installs Mutsumi globally
2. Creates config with defaults (no interactive UI)
3. Injects the integration prompt into agent config

The `--defaults` flag skips the interactive setup panel and uses all defaults.

## 6. Upgrade

```bash
uv tool upgrade mutsumi          # Upgrade to latest
uv tool upgrade mutsumi==0.3.0   # Pin specific version
```

### 6.1 Config Migration

When a new version introduces config changes:

- New fields: auto-populated with defaults, existing config untouched
- Removed fields: silently ignored, no error
- No automatic config rewriting — user's file is sacred

### 6.2 Breaking Changes

If `tasks.json` schema has breaking changes (unlikely before v1.0):

```bash
mutsumi migrate            # Interactive migration
mutsumi migrate --dry-run  # Preview changes
```

## 7. Uninstall

```bash
uv tool uninstall mutsumi
```

This removes the CLI binary. Config and data files are NOT deleted automatically.

To fully clean up:

```bash
uv tool uninstall mutsumi
rm -rf ~/.config/mutsumi/                    # Config
rm -rf ~/.local/share/mutsumi/               # Logs
# tasks.json is YOUR data — delete manually if you want
```

## 8. Platform-specific Notes

### 8.1 macOS

```bash
# If uv is not installed:
curl -LsSf https://astral.sh/uv/install.sh | sh
uv tool install mutsumi
```

Config location: `~/.config/mutsumi/` (XDG) or `~/Library/Application Support/mutsumi/`

### 8.2 Linux

Same as macOS. `~/.config/mutsumi/` follows XDG standard.

### 8.3 Windows

```powershell
# Install uv
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
uv tool install mutsumi
```

Config location: `%APPDATA%\mutsumi\`

Windows Terminal Quake Mode setup (recommended):

1. Open Windows Terminal Settings → Add new profile
2. Set `mutsumi` as the command
3. Enable Quake Mode keybind (default: `` Win+` ``)

## 9. Design Rationale

### 9.1 Why All-at-once, Not Step-by-step?

Step-by-step wizards create anxiety: "How many steps are left? Can I go back? Did I miss something?" The all-at-once panel eliminates this entirely. You see everything, you change what you want, you're done.

### 9.2 Why Live Preview?

Users who install Mutsumi are likely terminal power users who understand TOML. Showing the actual config file being generated builds trust and teaches the config format simultaneously.

### 9.3 Why Agent Setup is Separate?

Agent setup modifies files outside Mutsumi's domain (`CLAUDE.md`, `codex.md`, etc.). Keeping it separate from `mutsumi init` follows the principle of least surprise — init only touches Mutsumi's own config.

---

## Appendix A: Complete CLI Reference for Setup

```
mutsumi init                    Launch interactive setup panel
mutsumi init --defaults         Create config with all defaults (non-interactive)
mutsumi init --lang zh          Create config with Chinese as default language
mutsumi setup --agent <name>    Configure agent integration
mutsumi setup --agent           Interactive agent picker
mutsumi config --edit           Open config in $EDITOR
mutsumi config --show           Print current config
mutsumi config --reset          Reset config to defaults
mutsumi config --path           Print config file path
mutsumi validate                Validate tasks.json schema
mutsumi schema                  Output JSON Schema for tasks.json
mutsumi schema --format md      Output schema as markdown
```
