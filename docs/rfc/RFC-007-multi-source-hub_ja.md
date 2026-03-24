# RFC-007: Multi-Source Hub — Tool から Command Center へ

> **[English Version](./RFC-007-multi-source-hub.md)** | **[中文版](./RFC-007-multi-source-hub_cn.md)**

| Field | Value |
|---|---|
| **RFC** | 007 |
| **Title** | Multi-Source Hub: Personal Todo + Multi-Project Agent Dashboard |
| **Status** | Draft |
| **Author** | Wayne (ywh) |
| **Created** | 2026-03-22 |

---

## Abstract

Mutsumi は現在、working directory 内の 1 つの `tasks.json` だけを監視しています —— 1 project、1 file、1 view。本 RFC は、Mutsumi を**single-project task viewer**から、次を集約する**personal command center**へ進化させることを提案します。

1. **グローバルな personal todo list** —— project に紐づかない life tasks
2. **複数の project dashboard** —— 各 project で Agent がそれぞれの `mutsumi.json` に書く
3. **Main tab** —— 今いちばん重要なものを一望できる unified at-a-glance view

これは「tool」から「hub」への自然なアップグレードです。

## 1. Motivation

### 1.1 Two-Scatter Problem

独立開発者や multi-project user は、2 種類の scatter に直面します。

| Scatter | Current State | Pain |
|---|---|---|
| **Personal todos** | Todoist、Obsidian、付箋、脳内 | personal task を確認するための context switch が flow を壊す |
| **Agent project progress** | 各 project directory にそれぞれ terminal がある | 3 project を vibe-coding？ 3 terminals を開いて、3 回 `cd` して、3 files を見る必要がある |

Mutsumi はすでに single project に対して “Agent → visual feedback” のループを解決しています。しかし 2 つ以上の project を同時に走らせる瞬間、その価値は下がります —— また tab-switching に戻ってしまうからです。

### 1.2 Core Insight

> **本当のボトルネックは project 内の task 管理ではなく、すべての threads を同時に見えるようにすることだ。**

project-A では Claude Code、project-B では Codex、そして個人的に「指導教員にメールを返す」も追っている開発者に必要なのは、一瞥できる**1 つの場所**です。3 つの terminal ではない。browser tab でもない。1 つの TUI です。

### 1.3 Positioning Shift

| Before | After |
|---|---|
| “1 つの Agent session のための external display” | “あなたの workload 全体のための personal command center” |
| single-project viewer | multi-source aggregator |
| cwd 内の `tasks.json` | global `mutsumi.json` + per-project `mutsumi.json` |

## 2. Design

### 2.1 File Rename: `tasks.json` → `mutsumi.json`

データ file は `mutsumi.json` に rename されます。理由は次の通りです。

- **Brand identity**: 所有が明確になり、他ツールの `tasks.json` と衝突しにくい
- **Discoverability**: project 内に `mutsumi.json` があると、その project が Mutsumi を使っていることがすぐわかる
- **Multi-source clarity**: 複数 file を監視するとき、名前だけで意図が見えやすい

**Migration**: Mutsumi は fallback として `tasks.json` を自動検出して読みます。`mutsumi migrate` コマンドは `tasks.json` をその場で `mutsumi.json` に rename します。

Schema は**完全に同一**です —— 変わるのは filename だけ。`version` フィールドは `1` のままです。

### 2.2 Data Architecture: Global + Per-Project

```text
~/.mutsumi/                          ← Platform-aware（Windows では APPDATA）
├── mutsumi.json                     ← Personal global tasks
└── config.toml                      ← ~/.config/mutsumi/ からここへ移動

~/Code/project-a/
└── mutsumi.json                     ← Agent-driven project tasks

~/Code/project-b/
└── mutsumi.json                     ← Agent-driven project tasks
```

**データソースは 2 カテゴリあります。**

| Source | Location | Writer | Purpose |
|---|---|---|---|
| **Personal** | `~/.mutsumi/mutsumi.json` | User（TUI/CLI） | life tasks、cross-project errands、personal reminders |
| **Project** | `<project-dir>/mutsumi.json` | Agent + User | AI Agents によって駆動される project-specific tasks |

各 file は同じ schema を持つ独立した `mutsumi.json` です。cross-file references も shared state もありません。各 file は standalone で使えます。

### 2.3 Project Registry

Projects は `~/.mutsumi/config.toml` に登録されます。

```toml
[[projects]]
name = "saas-app"
path = "~/Code/saas-app"

[[projects]]
name = "oshigrid"
path = "~/Code/oshigrid"

[[projects]]
name = "mutsumi"
path = "~/Code/Mutsumi"
```

**登録方法:**

| Method | Command | Behavior |
|---|---|---|
| CLI add | `mutsumi project add ~/Code/saas-app` | path を登録し、なければ `mutsumi.json` を自動作成 |
| CLI add with name | `mutsumi project add ~/Code/saas-app --name saas` | custom display name で登録 |
| TUI add | `P` → folder picker / path input | CLI と同じことを TUI 内で行う |
| CLI remove | `mutsumi project remove saas-app` | 登録解除（`mutsumi.json` は**削除しない**） |
| CLI list | `mutsumi project list` | 登録済み project を一覧表示 |

project が追加されると：

1. path は absolute に解決され、config に保存される
2. その path に `mutsumi.json` が存在しなければ、default empty template で作成する
3. TUI 実行中なら、watchdog が即座に新 file の監視を開始する

### 2.4 Tab Structure

```text
[★ Main]  [Personal]  [saas-app]  [oshigrid]  [mutsumi]
```

| Tab | Data Source | Content |
|---|---|---|
| **★ Main** | 全 source の aggregate | dashboard: personal 高優先度タスク + 各 project summary cards |
| **Personal** | `~/.mutsumi/mutsumi.json` | day/week/month/inbox sub-filter 付きの full personal task list |
| **<project>** | `<project>/mutsumi.json` | day/week/month/inbox sub-filter 付きの full project task list |

Tabs は**dynamic**です —— project の登録/解除に応じて現れたり消えたりします。tab order は config file の順序に従います。Personal は常に 2 番目（Main の次）です。

#### 2.4.1 Main Tab Layout

Main tab は**read-only dashboard**です —— 全体を一瞥するための summary surface です。

```text
┌──────────────────────────────────────────────────────────┐
│  [★ Main]  [Personal]  [saas-app]  [oshigrid]  mutsumi  │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  ▸ Personal                                    2 tasks   │
│    ★★★ 写毕业论文 introduction                           │
│    ★★  回复导师邮件                                       │
│                                                          │
│  ▸ saas-app                              3/7 done  42%  │
│    ★★★ Fix auth token refresh                            │
│    ★★  Add rate limiting middleware                      │
│                                                          │
│  ▸ oshigrid                              1/4 done  25%  │
│    ★★★ Deploy staging environment                        │
│                                                          │
│  ▸ mutsumi                               5/5 done 100%  │
│    ✓ All tasks completed                                 │
│                                                          │
├──────────────────────────────────────────────────────────┤
│  16 tasks · 9 done · 7 pending · 4 sources    🔇 quiet  │
└──────────────────────────────────────────────────────────┘
```

**Main tab のルール:**

1. 各 project は**折りたたみ可能 section**として表示し、次を含む：
   - Project name + progress（`done/total` + percentage bar）
   - pending tasks のうち最上位 N 件（デフォルト N=3、設定可能）
2. Personal section は常に最初に表示する
3. すべての task が done の project は “✓ All tasks completed” を表示する
4. project section をクリック / Enter すると、その project tab にジャンプする
5. Main tab は**編集不可** —— task CRUD は各 specific tab で行う

#### 2.4.2 Project Tab（および Personal Tab）

各 tab の内部では、既存の時間ベース scope filter を維持します。

```text
┌──────────────────────────────────────────────────────────┐
│  [★ Main]  [Personal]  [saas-app]  [oshigrid]  mutsumi  │
│            ──────────                                    │
│  Filter: [Today] [Week] [Month] [Inbox] [All]           │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  ▼ HIGH                                                  │
│  [ ] Fix auth token refresh           backend   ★★★     │
│  [ ] Patch SQL injection in /users    security  ★★★     │
│                                                          │
│  ▼ NORMAL                                                │
│  [ ] Add rate limiting middleware     backend   ★★      │
│  [x] Set up CI pipeline              devops    ★★      │
│                                                          │
├──────────────────────────────────────────────────────────┤
│  4 tasks · 1 done · 3 pending                  🔇 quiet │
└──────────────────────────────────────────────────────────┘
```

scope filter（Today/Week/Month/Inbox）は top-level tab ではなく、各 tab 内の**sub-filter**になります。新しい **[All]** は unfiltered tasks を表示します。

### 2.5 Input: Keyboard + Mouse Full Coverage

すべての action は**keyboard と mouse の両方**から到達可能でなければなりません。mouse は一等市民です。

#### Tab Navigation

| Action | Keyboard | Mouse |
|---|---|---|
| tab へジャンプ | `1-9` | tab をクリック |
| 前 / 次の tab | `H` / `L` or `Shift+Tab` / `Tab` | tab をクリック |

#### Main Tab

| Action | Keyboard | Mouse |
|---|---|---|
| section 間移動 | `↑` / `↓` | スクロール / section をクリック |
| project に入る | `Enter` | project 名または `→` ボタンをクリック |
| section の折りたたみ/展開 | `←` / `→` | `▸` / `▾` chevron をクリック |
| 新規 project 追加 | `P` | footer の `[+ Project]` ボタンをクリック |

#### Project / Personal Tabs

| Action | Keyboard | Mouse |
|---|---|---|
| task 間移動 | `↑` / `↓` | task row をクリック |
| done 切り替え | `Space` | checkbox をクリック |
| detail 表示 | `Enter` | task title をクリック |
| 新規 task | `n` | `[+ New]` ボタンをクリック |
| task 編集 | `e` | title をダブルクリック |
| task 削除 | `Delete` | 右クリック → Delete |
| scope filter 切り替え | `f` | filter chips（Today/Week/Month/Inbox/All）をクリック |
| priority 上げ/下げ | `+` / `-` | priority stars をクリック |
| task を上/下へ移動 | `Shift+↑` / `Shift+↓` | drag & drop（future） |

#### デフォルト Keybinding Preset: `arrows`

デフォルト preset は**arrow keys**を使います —— vim の知識は不要です。power users は config で `vim` または `emacs` に切り替えられます。

```toml
[keys]
preset = "arrows"   # default — arrow keys, Home/End, Shift+arrows
# preset = "vim"    # j/k/G/dd
# preset = "emacs"  # C-n/C-p/C-a/C-e
```

### 2.6 Config Migration

config directory は personal data file と統合するために移動します。

| Before | After |
|---|---|
| `~/.config/mutsumi/config.toml` | `~/.mutsumi/config.toml` |
| `~/.config/mutsumi/themes/` | `~/.mutsumi/themes/` |
| （personal tasks なし） | `~/.mutsumi/mutsumi.json` |

Windows では `%APPDATA%\mutsumi\`（変更なし、すでに正しい）。

Mutsumi は旧 path も fallback として確認し、config を移動するための `mutsumi migrate` を提供します。

### 2.7 Updated Config Schema

```toml
[general]
language = "auto"
default_tab = "main"              # 起動時に表示する tab

[theme]
name = "monochrome-zen"

[keys]
preset = "vim"

[notifications]
mode = "quiet"

[dashboard]
max_tasks_per_project = 3         # Main tab で各 project に表示する top tasks 数
show_completed_projects = true    # 100% 完了 project を表示するか

[[projects]]
name = "saas-app"
path = "~/Code/saas-app"

[[projects]]
name = "oshigrid"
path = "~/Code/oshigrid"

[[projects]]
name = "mutsumi"
path = "~/Code/Mutsumi"
```

## 3. Agent Protocol Changes

### 3.1 File Name

Agents は `mutsumi.json` に書くべきです（`tasks.json` ではない）。後方互換のため、`mutsumi.json` が見つからない場合は Mutsumi が `tasks.json` を読みます。

### 3.2 No Schema Changes

`mutsumi.json` schema は現在の `tasks.json` schema と**完全に同一**です。追加・削除される field はありません。`scope` field は時間ベースの意味（day/week/month/inbox）を維持します。

### 3.3 Agent Setup

`mutsumi setup --agent` コマンドは `mutsumi.json` を参照するよう更新されます。

```text
# In your project directory, create and manage tasks in mutsumi.json
# Schema: { "version": 1, "tasks": [...] }
# Mutsumi watches this file and renders a live TUI dashboard
```

### 3.4 Multi-Agent Isolation

各 project は独自の `mutsumi.json` を持ちます。異なる project 上の 2 つの Agents が同じ file に書くことは**ありません** —— 設計上ゼロ競合です。

```text
Terminal 1: claude-code → writes ~/Code/saas-app/mutsumi.json
Terminal 2: codex       → writes ~/Code/oshigrid/mutsumi.json
Terminal 3: mutsumi     → watches both, renders unified view
```

## 4. CLI Changes

### 4.1 新しい `project` Command Group

```bash
mutsumi project add <path> [--name <display-name>]
mutsumi project remove <name>
mutsumi project list
```

### 4.2 Updated `init` Command

```bash
mutsumi init                    # cwd に mutsumi.json を作成
mutsumi init --global           # ~/.mutsumi/mutsumi.json を作成
mutsumi init --project <path>   # mutsumi.json を作成して project 登録
```

### 4.3 Updated `add` / `list` / `done` Commands

```bash
mutsumi add "Buy coffee" --personal          # personal tasks に追加
mutsumi add "Fix bug" --project saas-app     # 特定 project に追加
mutsumi add "Fix bug"                        # cwd の mutsumi.json に追加（現行動作）

mutsumi list --all                           # 全 source を一覧表示
mutsumi list --project saas-app              # 特定 project を一覧表示
```

### 4.4 Migration Command

```bash
mutsumi migrate                  # cwd で tasks.json → mutsumi.json に rename
mutsumi migrate --config         # ~/.config/mutsumi/ → ~/.mutsumi/ に移動
mutsumi migrate --all            # 両方
```

## 5. Implementation Strategy

### 5.1 Data Layer Changes

| Component | Change |
|---|---|
| `core/loader.py` | 複数 file path を受け入れ、タグ付き `(source_name, TaskFile)` tuples を返す |
| `core/watcher.py` | 複数 file を監視し、events に source name を付ける |
| `core/writer.py` | active tab context に応じて正しい file に書き込む |
| `core/models.py` | 変更なし —— schema は不変 |
| `core/paths.py` | `mutsumi_home()` → `~/.mutsumi/` を追加 |

### 5.2 TUI Changes

| Component | Change |
|---|---|
| `app.py` | 複数 data source を管理し、dynamic tab を生成 |
| `tui/header_bar.py` | dynamic project tabs を描画 |
| `tui/main_dashboard.py` | **新 widget** —— aggregated dashboard view |
| `tui/task_list_panel.py` | 変更なし —— 1 source の tasks を描画 |
| `tui/scope_filter.py` | **新 widget** —— sub-filter bar（Today/Week/Month/Inbox/All） |

### 5.3 Phases

| Phase | Scope | Deliverable |
|---|---|---|
| **5a** | file rename + fallback | `mutsumi.json` support と `tasks.json` backward compat |
| **5b** | multi-source data layer | Loader/watcher が N files を source タグ付きで扱える |
| **5c** | project registry | `mutsumi project add/remove/list` CLI commands |
| **5d** | tab redesign | Main + Personal + per-project の dynamic tabs |
| **5e** | Main dashboard widget | progress bars 付き aggregated summary view |
| **5f** | config migration | `~/.mutsumi/` への統合 + `mutsumi migrate` |

## 6. Backward Compatibility

| Concern | Handling |
|---|---|
| 既存 `tasks.json` users | fallback として自動検出。rename には `mutsumi migrate` |
| 既存 `~/.config/mutsumi/` config | fallback として自動検出。移動には `mutsumi migrate --config` |
| single-project usage（未登録 project） | 以前と同じように動作 —— cwd の `mutsumi.json` を監視 |
| Agent Protocol | schema は不変 —— Agents は filename を変えるだけでよい |
| `scope` field semantics | 不変 —— 依然として time-based（day/week/month/inbox） |
| `--watch` flag | 引き続き使えるが、`project add` のほうが推奨 |

## 7. What This Is NOT

- **team collaboration tool ではない。** すべて local data。shared boards、permissions、sync はない。
- **project management tool ではない。** Gantt charts も sprint も resource allocation もない。あるのは tasks だけ。
- **Agent の代替ではない。** Mutsumi は引き続き View。Agents は Controllers。`mutsumi.json` は引き続き Model。
- **workspace manager ではない。** Mutsumi は terminals、windows、processes を管理しない。

## 8. Open Questions

1. **Project health indicators** —— Main tab に “last updated” timestamp を出して stale projects を検出すべきか？
2. **Cross-project task moving** —— task を project 間で移動できるようにすべきか？（おそらく v1 では不要。）
3. **Project archival** —— 終了した project をどう扱うか？ registry から外す？ archive flag？
4. **Notification per-project** —— notification mode は project ごとに設定できるべきか？
5. **Max projects** —— 実用上の上限はあるか？ tab bar overflow をどう処理するか？

---

## Appendix A: Migration Path

```text
v0.4.x（current）          v0.5.0（this RFC）
─────────────────          ──────────────────
tasks.json          →      mutsumi.json（auto-fallback）
~/.config/mutsumi/  →      ~/.mutsumi/（auto-fallback）
[Today][Week][Month][Inbox] → [★ Main][Personal][proj-a][proj-b]
                                       └─ [Today][Week][Month][Inbox][All]
Single file watcher  →      Multi-file watcher
No personal tasks    →      ~/.mutsumi/mutsumi.json
```

## Appendix B: Competitive Landscape

この組み合わせを実現している terminal tool はまだありません。

| Tool | Personal Todo | Multi-Project Agent View | Unified Dashboard |
|---|:---:|:---:|:---:|
| Todoist | ✅ | ❌ | ❌ |
| Taskwarrior | ✅ | ❌ | ❌ |
| GitHub Projects | ❌ | Partial | ❌ |
| Linear | ❌ | ✅ | ✅（ただし team 向けであり、personal ではない） |
| **Mutsumi v0.5** | **✅** | **✅** | **✅** |
