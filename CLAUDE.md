# Mutsumi Development Rules (CLAUDE.md)

## Project Overview
Mutsumi is a minimal TUI task board that watches `tasks.json` and provides a zero-friction visual anchor for multi-threaded developers. Built with Python + Textual.

## Architecture
- **MVC separation**: Mutsumi is the View. AI Agents are Controllers. `tasks.json` is the Model.
- **Layout Agnostic**: Mutsumi does NOT manage window splitting. She is an independent terminal process.
- **Agent Agnostic**: No LLM or agent dependency. Any program that writes JSON is a valid controller.

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
- Atomic file writes: always write to temp file + `os.rename()`.
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
2. **Preserve unknown fields.** When writing `tasks.json`, never delete fields you don't recognize.
3. **Graceful degradation.** If `tasks.json` is invalid, show error banner but don't crash.
4. **No heavy dependencies.** If a pip package solves a trivial problem, write it inline instead.
5. **Commit messages** follow conventional commits: `feat:`, `fix:`, `docs:`, `style:`, `refactor:`, `test:`, `chore:`, `i18n:`.
6. **One concern per file.** Don't put CLI logic in TUI files or vice versa.
7. **User data is sacred.** Never auto-delete tasks, never modify user's custom fields, never corrupt `tasks.json`.

## Testing
- Use `pytest` for unit tests
- Test data models (pydantic) extensively — they are the contract
- TUI tests via Textual's built-in testing framework (`app.run_test()`)
- Fixture files in `tests/fixtures/`

## Specs & Docs
- RFC: `docs/rfc/RFC-001-mutsumi-core.md`
- Data Contract: `docs/specs/DATA_CONTRACT.md`
- Agent Protocol: `docs/specs/AGENT_PROTOCOL.md`
- TUI Spec: `docs/specs/TUI_SPEC.md`
- Roadmap: `docs/ROADMAP.md`
- Brand: `docs/BRAND.md`
