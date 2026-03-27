# Mutsumi 開発ロードマップ

> **[English Version](./ROADMAP.md)** | **[中文版](./ROADMAP_cn.md)**

| ステータス | リビングドキュメント |
|---|---|
| 日付 | 2026-03-25 |
| Current Beta | `1.1.0b1` |

---

## Product State

Mutsumi は現在 **`1.1.0b1` beta** フェーズにあります。

この beta ですでに現実のものとなっている内容:

- canonical task file: `mutsumi.json`
- legacy fallback: `tasks.json`
- default keybinding preset: `arrows`
- semantic-first interaction layer（`confirm` / `back` / `create` / `edit`）
- confirm/search/detail の layered close ordering
- multi-source hub: Main + Personal + project tabs
- source-aware task creation（`source/project -> scope -> task fields`）
- first-run onboarding と、その完了時の即時 preset hot-reload
- skills-first agent setup

まだ **shipped** されていない内容:

- built-in calendar UI
- plugin system
- web companion

Calendar は現在 **RFC-009** を通じた planned feature として管理されています。

---

## Phase Overview

```text
Phase 0   Foundations
Phase 1   Static TUI
Phase 2   Reactivity
Phase 3   CLI & Polish
Phase 3.5 Friend Beta
Phase 5   Multi-Source Hub
Phase 8   Out-of-Box Onboarding
Phase 9   Calendar View (planned)
Phase 10  Launch / GA polish
```

---

## Phase 0: Foundations ✅

**Goal**: product model、specs、初期 project skeleton を確立すること。

- [x] vision と architecture docs
- [x] RFC-001: Core Architecture
- [x] Data Contract spec
- [x] Agent Integration Protocol
- [x] TUI spec
- [x] brand identity
- [x] roadmap
- [x] `uv` project setup
- [x] sample fixture task file
- [x] project development rules (`CLAUDE.md`)
- [x] CI baseline

**Exit criteria**: `uv run mutsumi` で空の Textual window が clean に起動できること。

---

## Phase 1: Skeleton ✅

**Goal**: local JSON から static task board を描画すること。

- [x] Textual app shell
- [x] task list rendering
- [x] priority grouping
- [x] task row UI
- [x] footer statistics
- [x] task schema models
- [x] file parsing
- [x] basic keyboard navigation
- [x] nested child rendering
- [x] empty state

**Exit criteria**: local task file が TUI に正しく描画されること。

---

## Phase 2: Reactivity ✅

**Goal**: 外部ファイル変更とローカル操作の両方で board が正しく更新されること。

- [x] watchdog file watching
- [x] debounce
- [x] hot reload
- [x] checkbox click → JSON write-back
- [x] atomic file writes
- [x] invalid JSON → error banner
- [x] graceful degradation
- [x] detail panel
- [x] end-to-end agent write → TUI refresh flow

**Exit criteria**: task file が変わると board が live に refresh されること。

---

## Phase 3: CLI & Polish ✅

**Goal**: demo UI ではなく、使える local product loop を提供すること。

- [x] TUI CRUD
- [x] CLI CRUD: `add`, `list`, `done`, `rm`, `edit`
- [x] `mutsumi init`
- [x] `mutsumi validate`
- [x] `mutsumi schema`
- [x] theme system
- [x] i18n (`en`, `zh`, `ja`)
- [x] config system
- [x] search
- [x] local event logging
- [x] version / help output

**Exit criteria**: 新規ユーザーが素早く install し、基本的な local workflow を完了できること。

---

## Phase 3.5: Friend Beta ✅

**Goal**: early tester にとって agent-driven usage を理解しやすくすること。

- [x] `AGENT.md`
- [x] sample fixtures
- [x] `mutsumi setup --agent`
- [x] split-pane helper scripts
- [x] demo script
- [x] beta packaging work
- [x] early beta docs

**Historical note**: この phase で earlier friend-beta line が導入されました。現在の product はすでにその段階を越えています。

---

## Phase 5: Multi-Source Hub ✅

**Goal**: Mutsumi を single-project viewer から multi-source command center に変えること。

- [x] `tasks.json` → `mutsumi.json` への rename と compatibility fallback
- [x] home directory を `~/.mutsumi/` に統一
- [x] multi-source registry と watchers
- [x] project registration CLI
- [x] source-tab redesign
- [x] Main dashboard aggregation

**Exit criteria**: personal と project の task files を 1 つの UI に集約できること。

---

## Phase 8: Out-of-Box Onboarding ✅

**Goal**: `mutsumi` を自然な entrypoint にすること。

- [x] first-run onboarding flow
- [x] onboarding-based preference capture
- [x] lightweight project attach flow
- [x] skills-first agent integration path
- [x] 適切な場面での Mutsumi-owned files の自動作成
- [x] onboarding 完了時に theme、i18n、keybinding preset を即時 hot-reload

**Exit criteria**: 初回起動が成功し、ユーザーが先に setup graph を学ばなくてもよいこと。

---

## Phase 9: Calendar View (Planned)

**Goal**: 既存タスクを time-based にナビゲートするための built-in calendar surface を追加すること。

Design authority:

- [x] RFC-009: Calendar View

Planned implementation slices:

- [ ] Main-layer calendar mode
- [ ] month / agenda foundation
- [ ] date drill-down into task detail
- [ ] source-aware calendar aggregation
- [ ] lightweight date-based create/edit flows
- [ ] richer week/day interactions

Scope notes:

- calendar は `due_date` を再利用する
- calendar は second task model を導入しない
- calendar は planned であり、現在の `1.1.0b1` beta line にはまだ shipped されていない

---

## Phase 10: Launch / GA Polish (Next)

**Goal**: broader release に向けて、product、docs、packaging、marketing surfaces を磨くこと。

- [ ] beta/GA path 向けの英語ドキュメントを仕上げる
- [ ] polished demo assets を記録する
- [ ] `mutsumi-tui` の PyPI install flow を publish / verify する
- [ ] beta testing checklist と feedback loop を引き締める
- [ ] GA 前に残る UX / documentation gaps を埋める
- [ ] launch copy と release materials を準備する

**Exit criteria**: install、onboarding、agent setup、day-to-day usage がより広い public release に十分な一貫性を持つこと。

---

## Future Ideas (Post-GA / Unscheduled)

これらはアイデアであり、committed roadmap promise ではありません。

| Feature | Description | Priority |
|---|---|---|
| Plugin system | ユーザー定義 widget / extension | P2 |
| Task templates | 再利用可能な recurring task setup | P2 |
| Archive | 完了タスクを active file から移す | P2 |
| Pomodoro timer | タスク連動の focus timer | P3 |
| Git sync helper | 任意の Git-based task-file workflow | P3 |
| Dashboard widgets | 追加の charts / summaries | P3 |
| Web companion | read-only web surface | P3 |
| Taskwarrior import | 既存システムからの import | P3 |
| Markdown tasks | markdown-based source format のサポート | P3 |

---

## Versioning Strategy

| Version | Meaning |
|---|---|
| `0.1.x` | static rendering baseline |
| `0.2.x` | reactivity baseline |
| `0.3.x` | CLI/config baseline |
| `0.4.0b1` | earlier friend-beta milestone |
| `1.0.0b1` | RFC-010 の interaction convergence 前の integrated beta line |
| `1.1.0b1` | current semantic-first beta line |
| `1.0.0` | beta hardening 後の stable release target |

---

## Beta Guidance

現在の cycle で重要な source of truth は次の通りです。

- current beta version: **`1.1.0b1`**
- canonical task file: **`mutsumi.json`**
- default preset: **`arrows`**
- semantic-first interaction は beta product line に入っている
- calendar status: **RFC-009 により planned であり、まだ shipped されていない**
