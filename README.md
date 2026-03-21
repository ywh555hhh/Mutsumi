# mutsumi ♪

> **[中文版](./README_cn.md)** | **[日本語版](./README_ja.md)**

**The silent task brain for the multi-threaded you.**

A minimal TUI task board that watches your `tasks.json` and stays out of your way. Let your AI agent be the brain — Mutsumi is just the eyes.

```
┌─────────────────────────────────────────────────────┐
│  [Today] [Week] [Month] [Inbox]          mutsumi ♪  │
├─────────────────────────────────────────────────────┤
│                                                     │
│  ▼ HIGH ─────────────────────────────────────────   │
│  [ ] Refactor Auth module             dev,backend ★★★│
│  [x] Fix cache penetration bug        bugfix      ★★★│
│                                                     │
│  ▼ NORMAL ───────────────────────────────────────   │
│  [ ] Write weekly report              life        ★★ │
│  [ ] Review PR #42                    dev         ★★ │
│    └─ [ ] Check type safety           (1/2)          │
│    └─ [x] Run tests                                  │
│                                                     │
│  ▼ LOW ──────────────────────────────────────────   │
│  [ ] Update README                    docs        ★  │
│                                                     │
├─────────────────────────────────────────────────────┤
│  6 tasks · 2 done · 4 pending                       │
└─────────────────────────────────────────────────────┘
```

## Why Mutsumi?

You're running Claude Code in one terminal, Codex CLI in another, browsing Reddit, chatting on Discord — all at the same time. You need a task board that:

- **Summons in < 1 second** — no loading, no login, no network
- **Auto-refreshes** when your AI agent writes to `tasks.json`
- **Stays out of your way** — no opinions, no workflow enforcement
- **Works with any agent** — Claude Code, Codex CLI, Gemini CLI, Aider, or a shell script

That's Mutsumi. She watches your JSON and re-renders instantly. That's it.

## Install

```bash
uv tool install mutsumi
```

No Python pre-install needed — `uv` manages everything.

```bash
# Alternative
pipx install mutsumi

# For hackers
git clone https://github.com/ywh555hhh/Mutsumi.git
cd Mutsumi && uv sync && uv run mutsumi
```

## Quick Start

```bash
# Launch the TUI (watches tasks.json in current dir)
mutsumi

# Interactive setup (one screen, all options)
mutsumi init

# Setup agent integration
mutsumi setup --agent claude-code
```

## How It Works

```
┌──────────────┐        ┌────────────┐        ┌──────────────┐
│  AI Agent    │───────▶│ tasks.json │◀───────│  You (TUI)   │
│  (Controller)│ write  │  (Model)   │ watch  │  (View)      │
└──────────────┘        └────────────┘        └──────────────┘
```

**MVC separation**: Agents write JSON. Mutsumi watches and renders. You click and it writes back. Simple.

## Features

- **Hot-reload**: File changes re-render the TUI instantly (100ms debounce)
- **Vim/Emacs/Arrow keybindings**: Choose your style, or define custom keys
- **4 built-in themes**: Monochrome (default), Catppuccin Mocha, Nord, Dracula
- **i18n**: English, Chinese, Japanese out of the box
- **Agent-agnostic**: Any program that writes JSON is a valid controller
- **Zero network**: 100% local. No telemetry. No cloud. Your data stays yours.
- **Hackable**: TOML config, custom themes, custom keybindings — mod everything

## Agent Integration

Your AI agent just needs to read/write `tasks.json`:

```bash
# One-liner: install + configure + integrate
uv tool install mutsumi && mutsumi init --defaults && mutsumi setup --agent claude-code
```

Supported agents: Claude Code, Codex CLI, Gemini CLI, OpenCode, Aider, or any custom script.

See [Agent Protocol](docs/specs/AGENT_PROTOCOL.md) for details.

## Documentation

| Document | Description |
|---|---|
| [RFC-001: Core Architecture](docs/rfc/RFC-001-mutsumi-core.md) | Product definition & architecture |
| [RFC-002: Installation](docs/rfc/RFC-002-installation-and-onboarding.md) | Install & onboarding experience |
| [RFC-003: i18n Strategy](docs/rfc/RFC-003-documentation-i18n.md) | Documentation internationalization |
| [Data Contract](docs/specs/DATA_CONTRACT.md) | `tasks.json` schema specification |
| [Agent Protocol](docs/specs/AGENT_PROTOCOL.md) | Agent integration protocol |
| [TUI Spec](docs/specs/TUI_SPEC.md) | TUI interaction specification |
| [Roadmap](docs/ROADMAP.md) | Development roadmap |
| [Brand](docs/BRAND.md) | Brand identity |

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

[MIT](LICENSE)

---

*mutsumi (若叶睦) — "harmony, closeness." She doesn't tell you what to do. She just waits there, quietly.*
