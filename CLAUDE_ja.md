# Mutsumi 開発ルール（CLAUDE.md）

> **[English Version](./CLAUDE.md)** | **[中文版](./CLAUDE_cn.md)**

## Project Overview
Mutsumi は `mutsumi.json` を監視する最小限の TUI task board であり、`tasks.json` は backward-compatible fallback として扱います。マルチスレッドな開発者のための、ゼロ摩擦な視覚アンカーを提供します。Python + Textual で構築されています。

## Architecture
- **MVC separation**: Mutsumi は View。AI Agents は Controllers。`mutsumi.json` は canonical Model file であり、`tasks.json` は legacy fallback として引き続き受け入れます。
- **Layout Agnostic**: Mutsumi は window splitting を管理しません。独立した terminal process です。
- **Agent Agnostic**: LLM や agent への依存はありません。JSON を書ける任意の program が valid controller です。

## Interaction Principles
- **Keyboard + Mouse full coverage**: すべての action は keyboard と mouse click の両方から到達可能でなければなりません。keyboard-only feature も mouse-only feature も禁止です。
- **Default preset is `arrows`**（vim ではない）: Arrow keys + Home/End + Shift+arrows。普通のユーザーは vim を知っているとは限りません。vim と emacs は power users 向け opt-in preset です。
- **Mouse is a first-class citizen**: clickable buttons、clickable tabs、clickable checkboxes、clickable list items。mouse users を second-class にしてはいけません。

## Tech Stack
- Python 3.12+、`uv` 管理
- TUI: Textual
- CLI: click
- Validation: pydantic v2
- File watching: watchdog
- Config: TOML（stdlib `tomllib`）

## Code Conventions
- type hints を everywhere で使う。`Any` は使わない。
- Textual widgets では inheritance より composition を優先する。
- すべての file I/O は `core/` module 経由 — TUI components は filesystem に直接触れない。
- atomic file writes: 必ず temp file + `os.replace()`（cross-platform）。
- platform paths: `core/paths.py` helpers を使い、`~/.config` や `~/.local/share` を hardcode しない。
- 可能な限り TUI components を stateless に保つ — state は data layer に置く。

## File Structure
```text
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
1. **No network calls.** Mutsumi は 100% local。telemetry、API calls、analytics は禁止。
2. **Preserve unknown fields.** `mutsumi.json` や legacy `tasks.json` に書くとき、認識しない field を削除しない。
3. **Graceful degradation.** active task file が invalid でも、error banner を出して crash しない。
4. **No heavy dependencies.** trivial な問題のために重い pip package を入れない。必要なら inline 実装する。
5. **Commit messages** は conventional commits に従う: `feat:`、`fix:`、`docs:`、`style:`、`refactor:`、`test:`、`chore:`、`i18n:`。
6. **One concern per file.** CLI logic を TUI file に入れない。逆も同じ。
7. **User data is sacred.** user task を auto-delete しない。custom fields を勝手に変えない。`mutsumi.json` や legacy `tasks.json` を壊さない。

## Testing
- unit tests には `pytest` を使う
- data models（pydantic）を重点的にテストする — それらが contract そのもの
- TUI tests は Textual の built-in testing framework（`app.run_test()`）を使う
- fixture files は `tests/fixtures/`

## Development Workflow
**大機能は RFC なしでは書かない。** すべての non-trivial feature は次の flow に従うこと。

1. **RFC** — 先に RFC document を書き、design discussion で合意する
2. **doc + code** — code と docs を同時に更新する
3. **test + 手動体験テスト** — automated tests + terminal 上での manual run
4. **bug fix** — test や体験で見つかった問題を直す
5. **doc + push** — 最終 docs 更新 + push

## Specs & Docs
- RFC: `docs/rfc/RFC-001-mutsumi-core.md`
- RFC: `docs/rfc/RFC-007-multi-source-hub.md`
- Data Contract: `docs/specs/DATA_CONTRACT.md`
- Agent Protocol: `docs/specs/AGENT_PROTOCOL.md`
- TUI Spec: `docs/specs/TUI_SPEC.md`
- Roadmap: `docs/ROADMAP.md`
- Brand: `docs/BRAND.md`
