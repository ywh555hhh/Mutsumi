# Mutsumi Friend Beta — 使用 SOP

> **[English Version](./BETA_USAGE.md)** | **[中文版](./BETA_USAGE_cn.md)**

これは現在の **`1.0.0b1`** ライン向けの日本語 beta 利用ガイドです。
内部テストおよび friend beta onboarding 用です。

---

## 0. 前提条件

- macOS / Linux ターミナル
- Windows ユーザーは beta 期間中は WSL を推奨
- Python 3.12+
- `uv` または `pip`

`uv` がない場合:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

---

## 1. インストール

### Option A — PyPI package

```bash
uv tool install mutsumi-tui
# または
pip install mutsumi-tui
```

### Option B — source / git から

```bash
uv tool install git+https://github.com/ywh555hhh/Mutsumi.git
```

確認:

```bash
mutsumi --version
# Expected: mutsumi, version 1.0.0b1
```

`command not found` が出る場合は、tool bin directory が `PATH` に入っていることを確認してください。

---

## 2. 初回起動

```bash
cd ~/your-project
mutsumi
```

初回なら Mutsumi は onboarding を表示します。
すでに onboarding を完了している場合は、そのまま開きます。

### onboarding が設定するもの

- language
- keybindings
- theme
- workspace mode
- optional agent integration

### 現在のデフォルト

- Theme: `monochrome-zen`
- Keybindings: `arrows`
- Language: `en`

---

## 3. タスクファイルの明示的初期化（任意）

Mutsumi を使う前に手動で初期化する必要は**ありません**が、CLI で作成できます。

```bash
mutsumi init                # create ./mutsumi.json
mutsumi init --personal     # create ~/.mutsumi/mutsumi.json
mutsumi init --project      # create ./mutsumi.json and register current repo
```

古いセットアップでは、Mutsumi は `tasks.json` もフォールバックとして自動で読みます。

---

## 4. 最初のタスクを作る

### Option A: CLI

```bash
mutsumi add "ログインバグを修正" --priority high --scope day --tags "bugfix"
mutsumi add "週報を書く" --priority normal --scope week --tags "life"
mutsumi add "ドキュメント更新" --priority low --scope month --tags "docs"
```

確認:

```bash
mutsumi list
mutsumi validate
```

### Option B: AI agent に書かせる

Agent にこう伝えてください:

> This project uses Mutsumi. Tasks should go into `./mutsumi.json`.
> If only legacy `tasks.json` exists, use that instead.
> Read the whole file, modify the `tasks` array, and write it back atomically.

### Option C: personal tasks を作る

```bash
mutsumi init --personal
```

その後もう一度 Mutsumi を起動すると、multi-source mode で personal source が見えるようになります。

---

## 5. TUI を起動する

```bash
mutsumi
```

デフォルトのファイル解決順序:

1. explicit `--path`
2. `./mutsumi.json`
3. `./tasks.json`
4. new-project の default target: `./mutsumi.json`

別のファイルを指定する場合:

```bash
mutsumi --path /path/to/mutsumi.json
```

追加の task file を watch する場合:

```bash
mutsumi --watch /path/to/project-a/mutsumi.json --watch /path/to/project-b/mutsumi.json
```

---

## 6. 表示されるもの

### Single-source view

```text
[Today] [Week] [Month] [Inbox]                    mutsumi ♪
------------------------------------------------------------
▼ HIGH
[ ] ログインバグを修正                  bugfix        ★★★

▼ NORMAL
[ ] 週報を書く                          life          ★★

▼ LOW
[ ] ドキュメント更新                    docs          ★
------------------------------------------------------------
3 tasks · 0 done · 3 pending
```

### Multi-source view

```text
[★ Main] [Personal] [your-project]                     mutsumi ♪
---------------------------------------------------------------
★ Main Dashboard

★ Personal      2 pending
  • コーヒー豆を買う
  • 指導教員に返信する

your-project    3 pending
  • ログインバグを修正
  • ドキュメント更新
```

---

## 7. キーボード操作

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

これらは opt-in であり、現在の beta の default preset ではありません。

### Mouse

- click source tabs to switch sources
- click scope chips to change the filter
- click a task row to select it
- click a title to open the detail panel
- click a checkbox to toggle done
- click footer actions such as new task or search

---

## 8. Agent 連携

### Option A: Skills-first setup（推奨）

```bash
mutsumi setup --agent claude-code
mutsumi setup --agent codex-cli
mutsumi setup --agent gemini-cli
mutsumi setup --agent opencode
```

これは bundled Mutsumi skills を各 agent の skill directory にインストールします。
`CLAUDE.md`、`AGENTS.md` などの project files は**変更しません**。

### Option B: Skills + project doc injection

```bash
mutsumi setup --agent claude-code --mode skills+project-doc
```

これは skills を入れ、agent の project instruction file に Mutsumi integration snippet を追加します。

### Option C: Manual snippet

```bash
mutsumi setup --agent aider --mode snippet
mutsumi setup --agent custom --mode snippet
```

これはコピー可能な instructions を出力します。

### Quick manual prompt

```text
This project uses Mutsumi for task management.
Prefer ./mutsumi.json; use ./tasks.json only if the project is still on the legacy filename.
Read the whole file, modify the tasks array, preserve unknown fields, and write the file back atomically.
```

---

## 9. tmux / split-pane セットアップ

### tmux（推奨）

```bash
bash scripts/tmux-dev.sh
```

### 手動 split

```bash
tmux new-session -d -s dev
tmux split-window -h -p 35 "mutsumi"
tmux select-pane -t 0
tmux attach -t dev
```

### iTerm2 / VS Code / Cursor

- ターミナルを縦分割する
- 右ペイン: `mutsumi`
- 左ペイン: your agent or shell

その後、agent に task の追加や更新を依頼します。TUI は自動更新されるはずです。

---

## 10. CLI リファレンス

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

CLI command では、通常は一意な task ID prefix だけで十分です。

---

## 11. 設定リファレンス

優先される設定パス:

```text
~/.mutsumi/config.toml
```

legacy fallback path:

```text
~/.config/mutsumi/config.toml
```

例:

```toml
theme = "monochrome-zen"
keybindings = "arrows"
language = "en"
default_scope = "day"
default_tab = "main"
notification_mode = "quiet"
```

---

## 12. Task file schema

canonical filename: `mutsumi.json`
legacy fallback: `tasks.json`

```json
{
  "version": 1,
  "tasks": [
    {
      "id": "01EXAMPLE000000000000000001",
      "title": "タスクタイトル",
      "status": "pending",
      "scope": "day",
      "priority": "normal",
      "tags": ["dev", "urgent"],
      "children": [],
      "created_at": "2026-03-23T08:00:00Z",
      "due_date": "2026-03-25",
      "completed_at": null,
      "description": "任意の説明"
    }
  ]
}
```

unknown fields は保持されます。

---

## 13. トラブルシューティング

### `mutsumi` command not found

tool bin directory が `PATH` に入っていることを確認してください。

### TUI が空だがファイルは存在する

- 今どの source tab にいるか確認する
- active scope filter を確認する
- `mutsumi validate` を実行する

### Agent の変更が反映されない

- agent が Mutsumi が watch している同じ file に書いていることを確認する
- `mutsumi.json` を優先する
- repo が legacy `tasks.json` をまだ使っているなら、その file が watch 対象になっていることを確認する
- `mutsumi validate` で検証する

### テーマや keybindings が適用されない

- workflow に `mutsumi config --show` があるなら実行する
- `~/.mutsumi/config.toml` を確認する
- default keybinding preset は `arrows` であることを思い出す

---

## 14. 現在の Beta ポジショニング

現行 beta line では:

- version string は **`1.0.0b1`**
- canonical task file は **`mutsumi.json`**
- legacy fallback は **`tasks.json`**
- default preset は **`arrows`**
- multi-source dashboard はすでに shipped beta surface に含まれる
- calendar は planned feature であり、まだ shipped beta view ではない
