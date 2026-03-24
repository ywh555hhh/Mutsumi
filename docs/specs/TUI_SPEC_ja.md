# Mutsumi TUI 仕様

| バージョン | 1.0 |
|---|---|
| ステータス | ドラフト |
| 日付 | 2026-03-23 |

> **[English Version](./TUI_SPEC.md)** | **[中文版](./TUI_SPEC_cn.md)**

---

## 1. レイアウト

### 1.1 デフォルトレイアウト

multi-source mode では、Mutsumi は動的な source tabs と第 2 レベルの scope filter を使います。

```text
┌──────────────────────────────────────────────────────────────┐
│ [★ Main] [Personal] [saas-app] [docs-site]       mutsumi ♪  │
├──────────────────────────────────────────────────────────────┤
│ ★ Main │ [Today] [Week] [Month] [Inbox] [All]               │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  ▼ HIGH ───────────────────────────────────────────────      │
│  [ ] Refactor auth module                 dev,backend  ★★★   │
│  [x] Fix cache bug                        bugfix       ★★★   │
│                                                              │
│  ▼ NORMAL ─────────────────────────────────────────────      │
│  [ ] Write weekly report                  life         ★★    │
│  [ ] Review PR #42                        dev          ★★    │
│    └─ [ ] Check type safety                               │
│    └─ [x] Run tests                                        │
│                                                              │
├──────────────────────────────────────────────────────────────┤
│  6 tasks · 2 done · 4 pending                      🔇 quiet  │
└──────────────────────────────────────────────────────────────┘
```

### 1.2 Main dashboard view

アクティブな source tab が `Main` のとき、Mutsumi は編集可能な task list ではなく集約 dashboard を表示します。

```text
┌──────────────────────────────────────────────────────────────┐
│ [★ Main] [Personal] [saas-app] [docs-site]       mutsumi ♪  │
├──────────────────────────────────────────────────────────────┤
│                    ★ Main Dashboard                          │
│                                                              │
│  ★ Personal    3 pending                                     │
│  ████████░░░░░░░░░░ 40% (2/5)                                │
│    • Buy coffee beans                                        │
│    • Reply to advisor                                        │
│                                                              │
│  saas-app     5 pending                                      │
│  ███░░░░░░░░░░░░░░ 15% (1/7)                                 │
│    !!! • Fix token refresh                                   │
│    • Add rate limiting                                       │
└──────────────────────────────────────────────────────────────┘
```

### 1.3 レスポンシブ動作

| ターミナル幅 | 動作 |
|---|---|
| `>= 80` cols | フル行: title + tags + priority |
| `60-79` cols | メタデータを減らす |
| `40-59` cols | 最小行レイアウト |
| `< 40` cols | terminal-too-narrow 警告を表示 |

### 1.4 詳細パネル

タスクを選択して `Enter` を押すか、そのタイトルをクリックすると詳細パネルが開きます。

詳細パネルには次が表示されます。

- title
- status
- priority
- scope
- tags
- due date
- description
- child progress
- created / completed timestamps

また、クリック可能な操作も提供します。

- `[Edit]`
- `[+Sub]`
- `[Delete]`
- 閉じるための `[x]`

---

## 2. インタラクションモデル

### 2.1 マウス

| 操作 | 動作 |
|---|---|
| checkbox をクリック | done 状態を切り替える |
| task row をクリック | 行を選択する |
| task title をクリック | 詳細パネルを開く |
| source tab をクリック | source を切り替える |
| scope chip をクリック | scope filter を変更する |
| footer action をクリック | task form、search、sort を開く |
| dashboard card をクリック | その source tab にジャンプする |
| 詳細パネルの `[+Sub]` をクリック | subtask form を開く |

### 2.2 キーボードプリセット

Mutsumi には 3 つの built-in preset があります。

- `arrows` — **デフォルト**
- `vim`
- `emacs`

#### `arrows`（デフォルト）

| キー | 操作 |
|---|---|
| `Up` / `Down` | 選択を移動 |
| `Home` / `End` | 先頭 / 末尾へジャンプ |
| `Left` / `Right` | グループを折りたたむ / 展開する |
| `Shift+Up` / `Shift+Down` | タスクを上 / 下へ移動 |
| `Space` | done を切り替える |
| `Enter` | 詳細を表示 |
| `n` | 新規タスク |
| `e` | タスク編集 |
| `i` | タイトルのインライン編集 |
| `A` | サブタスク追加 |
| `Tab` / `Shift+Tab` | 次 / 前の source tab |
| `1-9` | 番号付き source tab へジャンプ |
| `f` | scope filter を循環 |
| `/` | 検索 |
| `s` | ソート |
| `?` | ヘルプ表示 |
| `q` | 終了 |

#### `vim`

| キー | 操作 |
|---|---|
| `j` / `k` | 選択を移動 |
| `gg` / `G` | 先頭 / 末尾 |
| `h` / `l` | グループを折りたたむ / 展開する |
| `J` / `K` | タスクを下 / 上へ移動 |
| `dd` | 確認付き削除 |
| `Space` | done を切り替える |
| `Enter` | 詳細を表示 |
| `n` / `e` / `i` | 新規 / 編集 / インライン編集 |
| `A` | サブタスク追加 |
| `Tab` / `Shift+Tab` | 次 / 前の source tab |
| `f` | scope filter を循環 |
| `/` | 検索 |
| `?` | ヘルプ |
| `q` | 終了 |

#### `emacs`

| キー | 操作 |
|---|---|
| `Ctrl+n` / `Ctrl+p` | 選択を移動 |
| `Ctrl+a` / `Ctrl+e` | 先頭 / 末尾 |
| `Ctrl+b` / `Ctrl+f` | グループを折りたたむ / 展開する |
| `Ctrl+Shift+n` / `Ctrl+Shift+p` | タスクを移動 |
| `Space` | done を切り替える |
| `Enter` | 詳細を表示 |
| `n` / `e` / `i` | 新規 / 編集 / インライン編集 |
| `A` | サブタスク追加 |
| `Tab` / `Shift+Tab` | 次 / 前の source tab |
| `f` | scope filter を循環 |
| `/` | 検索 |
| `?` | ヘルプ |
| `Ctrl+q` | 終了 |

### 2.3 三入力等価

Mutsumi は、主要な操作が keyboard と mouse の両方から到達可能であり、関連する core task changes には適切な CLI もあるべきという製品ルールに従います。

例:

| Capability | Keyboard | Mouse | CLI |
|---|---|---|---|
| タスク作成 | `n` | footer action | `mutsumi add` |
| タスク編集 | `e` | `[Edit]` | `mutsumi edit` |
| タスク削除 | `dd` または削除フロー | `[Delete]` | `mutsumi rm` |
| done 切り替え | `Space` | checkbox | `mutsumi done` |
| ファイル検証 | — | — | `mutsumi validate` |

---

## 3. ビューとフィルター

### 3.1 Source tabs

Source tabs は time scope ではなく data source を表します。
例:

- `Main`
- `Personal`
- `saas-app` のような登録済みプロジェクト

### 3.2 Scope filter

編集可能な tab の中では、Mutsumi は第 2 レベルの filter を表示します。

- `Today`
- `Week`
- `Month`
- `Inbox`
- `All`

`Main` dashboard では scope filter は表示されません。

### 3.3 Scope の意味

Scope filtering には data contract の effective scope を使います。

```text
explicit scope > due_date auto-derivation > inbox
```

つまり、明示 scope がなくても `due_date` が list placement に影響します。

---

## 4. CRUD 挙動

### 4.1 タスク作成

トリガー:

- keyboard: `n`
- mouse: footer の new-task action

挙動:

- task form を開く
- `title` は必須
- 適用可能な場合、scope は現在の filter context をデフォルトにする
- submit 後、ファイルをアトミックに書く

### 4.2 タスク編集

トリガー:

- keyboard: `e`
- keyboard inline: `i`
- mouse: 詳細パネルの `[Edit]`

挙動:

- メモリ上でタスクを更新する
- アトミックに書き戻す
- 未知フィールドを保持する

### 4.3 タスク削除

トリガー:

- keyboard の削除フロー
- mouse の `[Delete]`

挙動:

- 確認が必要
- 選択中タスクを削除する
- アトミックに書き戻す

### 4.4 ステータス切り替え

トリガー:

- keyboard `Space`
- mouse checkbox click

挙動:

- `pending` → `done`: `completed_at` を埋める
- `done` → `pending`: `completed_at` を消す
- recurring task の処理では recurrence metadata に従って due date が更新される場合がある

---

## 5. ホットリロード

### 5.1 ファイル監視動作

Mutsumi は登録された各 source file を独立して監視します。

```text
external save
   ↓
watchdog event
   ↓
debounce
   ↓
re-read active source(s)
   ↓
re-render TUI
```

### 5.2 マルチソース動作

- single-source mode では 1 つのファイルを監視する
- multi-source mode では、登録されたすべての source file を監視する
- dashboard stats は読み込まれた全 source のタスクを集約する

### 5.3 自己書き込み抑制

Mutsumi は自分自身の atomic write の直後に発生する即時リロードを抑制し、冗長な refresh を避けます。

---

## 6. エラー状態と空状態

### 6.1 不正な JSON

アクティブな task file が不正な JSON になった場合:

- Mutsumi は error banner を表示する
- アプリはクラッシュしない
- ユーザーはファイルを修正して継続できる

例の banner:

```text
⚠ JSON is invalid — showing last valid state
```

### 6.2 ファイル欠如

アクティブファイルがまだ存在しない場合:

- UI は利用可能な空状態を表示する
- 初回の書き込みで task creation がファイルを作成できる
- 新しいプロジェクトでは `mutsumi.json` を作るべき

### 6.3 空状態

現在のビューにタスクが 1 つもない場合、Mutsumi は `+ New Task` アクション付きの親しみやすい空状態を表示します。

文言はアクティブな task flow を汎用的に参照すべきであり、`tasks.json` だけを前提にしてはいけません。

---

## 7. テーマと設定

### 7.1 ビルトインテーマ

- `monochrome-zen` — デフォルト
- `solarized`
- `nord`
- `dracula`

### 7.2 設定ホーム

優先される config / personal-data home:

```text
~/.mutsumi/
```

旧 config location も互換性のため引き続き読み取れます。

```text
~/.config/mutsumi/
```

### 7.3 キーバインディング設定

デフォルト preset は次の通りです。

```toml
keybindings = "arrows"
```

ユーザーは `vim` や `emacs` に切り替えられ、config で key override も定義できます。

---

## 8. Calendar への準備

この仕様はまだ calendar UI を定義しませんが、現在の TUI semantics は将来の time-based view と互換になるよう意図されています。

すでにある基盤:

- task model の `due_date`
- 日付に基づく effective scope derivation
- multi-source aggregation
- dashboard/source separation
- detail panel drill-down

将来の calendar view は、別の task model を発明するのではなく、これらの semantics の上に構築されるべきです。

---

## 9. 現在の Beta ノート

現在の beta line では:

- 正式 task file は `mutsumi.json`
- 旧フォールバックは `tasks.json`
- デフォルト preset は `arrows`
- multi-source dashboard はすでに product surface の一部
- calendar は planned capability であり、まだ shipped view ではない
