# Mutsumi Development Rules (CLAUDE.md)

> **[中文版](./CLAUDE_cn.md)** | **[日本語版](./CLAUDE_ja.md)**

## Project Overview
Mutsumi is a minimal TUI task board that watches `mutsumi.json` (with `tasks.json` as a backward-compatible fallback) and provides a zero-friction visual anchor for multi-threaded developers. Built with Python + Textual.

## Architecture
- **MVC separation**: Mutsumi is the View. AI Agents are Controllers. `mutsumi.json` is the canonical Model file, with `tasks.json` still accepted as a legacy fallback.
- **Layout Agnostic**: Mutsumi does NOT manage window splitting. She is an independent terminal process.
- **Agent Agnostic**: No LLM or agent dependency. Any program that writes JSON is a valid controller.

## Interaction Principles
- **Keyboard + Mouse full coverage**: Every action MUST be reachable by BOTH keyboard AND mouse click. No keyboard-only features, no mouse-only features.
- **Default preset is `arrows`** (not vim): Arrow keys + Home/End + Shift+arrows. Normal people don't know vim. Vim and emacs are opt-in presets for power users.
- **Mouse is a first-class citizen**: Clickable buttons, clickable tabs, clickable checkboxes, clickable list items. Mouse users should never feel like second-class.

## Tech Stack
- Python 3.12+, managed by `uv`
- TUI: Textual
- CLI: click
- Validation: pydantic v2
- File watching: watchdog
- Config: TOML (stdlib tomllib)

## Code Conventions
- Use type hints everywhere. Never use `Any`.
- Prefer composition over inheritance for Textual widgets.
- All file I/O through the `core/` module — TUI components never touch the filesystem directly.
- Atomic file writes: always write to temp file + `os.replace()` (cross-platform).
- Platform paths: use `core/paths.py` helpers — never hardcode `~/.config` or `~/.local/share`.
- Keep TUI components stateless where possible — state lives in the data layer.

## File Structure
```
mutsumi/
├── app.py          # Textual App entry point
├── tui/            # TUI components (widgets)
├── cli/            # CLI commands (click)
├── core/           # Data models, file I/O, validation
├── config/         # Config loading & defaults
├── i18n/           # Locale files
└── themes/         # Built-in theme files
```

## Rules
1. **No network calls.** Mutsumi is 100% local. No telemetry, no API calls, no analytics.
2. **Preserve unknown fields.** When writing `mutsumi.json` or legacy `tasks.json`, never delete fields you don't recognize.
3. **Graceful degradation.** If the active task file is invalid, show error banner but don't crash.
4. **No heavy dependencies.** If a pip package solves a trivial problem, write it inline instead.
5. **Commit messages** follow conventional commits: `feat:`, `fix:`, `docs:`, `style:`, `refactor:`, `test:`, `chore:`, `i18n:`.
6. **One concern per file.** Don't put CLI logic in TUI files or vice versa.
7. **User data is sacred.** Never auto-delete tasks, never modify user's custom fields, never corrupt `mutsumi.json` or legacy `tasks.json`.

## Testing
- Use `pytest` for unit tests
- Test data models (pydantic) extensively — they are the contract
- TUI tests via Textual's built-in testing framework (`app.run_test()`)
- Fixture files in `tests/fixtures/`

## Development Workflow
**大功能无 RFC 不写。** 所有非 trivial 的功能必须遵循以下流程：

1. **RFC** — 先写 RFC 文档，设计讨论达成共识
2. **doc + code** — 同步写代码和更新文档
3. **test + 人工体验测试** — 自动化测试 + 手动在终端里跑一遍
4. **bug fix** — 修复测试和体验中发现的问题
5. **doc + push** — 最终文档更新 + 推送

## Specs & Docs
- RFC: `docs/rfc/RFC-001-mutsumi-core.md`
- RFC: `docs/rfc/RFC-007-multi-source-hub.md`
- Data Contract: `docs/specs/DATA_CONTRACT.md`
- Agent Protocol: `docs/specs/AGENT_PROTOCOL.md`
- TUI Spec: `docs/specs/TUI_SPEC.md`
- Roadmap: `docs/ROADMAP.md`
- Brand: `docs/BRAND.md`
