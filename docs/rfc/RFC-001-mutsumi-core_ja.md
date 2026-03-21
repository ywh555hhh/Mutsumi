# RFC-001: Mutsumi コアアーキテクチャ

| フィールド | 値 |
|------------|----------------------------------------------|
| **RFC**    | 001                                          |
| **タイトル** | Mutsumi コアプロダクト定義 & アーキテクチャ |
| **ステータス** | ドラフト                                   |
| **著者**   | Wayne (ywh)                                  |
| **作成日** | 2026-03-21                                   |

> **[English Version](./RFC-001-mutsumi-core.md)** | **[中文版](./RFC-001-mutsumi-core_cn.md)**

---

## 概要

Mutsumi（若叶睦）は、**マルチスレッド型スーパー個人**のために設計されたサイレントタスク外脳です。ローカル JSON ファイルを監視することで、あらゆる AI Agent と疎結合に連携するスタンドアロンのターミナル TUI アプリケーションです。本 RFC では、Mutsumi のプロダクト境界、コアアーキテクチャ、データ契約、インタラクション仕様、および統合プロトコルを定義します。

## 1. 動機

### 1.1 課題の提示

現代の開発者（スーパー個人）の作業スタイルは、シングルスレッドからマルチスレッドへと移行しています：

- **断片化されたインプット**：ブラウザ、QQ グループ、Reddit、Discord、フォーラムなど複数の場所を同時に活動しています。
- **並行する Agent**：複数の AI Agent を異なるタスクで同時に実行しています（フロントエンドに Claude Code、テストに Codex CLI、ドキュメントに Gemini CLI）。
- **極度の時間圧迫**：毎日忙しすぎて、複雑なプロジェクト管理ツールをクリックする余裕がありません。

既存ツールの問題点：

| ツール種別 | 問題点 |
|---|---|
| Notion/Todoist | 重すぎる — 開くだけで負担、ターミナルワークフローと断絶 |
| Taskwarrior | 純粋な CLI のみ、視覚的なアンカーがなく直感的でない |
| GitHub Issues | プラットフォーム依存、ローカルオフライン非対応、「パーソナル」感に欠ける |
| IDE Todo プラグイン | エディタに依存、Agent が直接書き込めない |

### 1.2 核心的洞察

> **タスク管理のボトルネックは「管理」そのものではなく、「呼び出す」際の摩擦です。**

タスクの確認・更新のコストがゼロに近づけば（ワンキーで呼び出し、ワンキーでチェックオフ）、ユーザーは使うことに抵抗を感じなくなります。Mutsumi はこの摩擦をターミナルのホットキーレベルまで圧縮します。

### 1.3 ワンライナーポジショニング

> 「Mutsumi と Taskwarrior の違いは？」
> — **ゼロフリクションの呼び出し、お気に入りの Agent とのネイティブな適合。** Taskwarrior はコマンドの習得が必要なタスクデータベースです。一方、Mutsumi は静かなビジュアルかんばん — 何をすべきか指示しません。ただそこで、あなたがちらっと見てくれるのを待っています。

## 2. 設計原則

### 2.1 MVC 分離（コア哲学）

```
┌─────────────────────────────────────────────────┐
│                  User's Brain                    │
│   "Put fix-cache-bug at today's top priority"    │
└────────────────────┬────────────────────────────┘
                     │ natural language
                     ▼
┌─────────────────────────────────────────────────┐
│        Controller: AI Agent (decoupled)          │
│  Claude Code / Codex CLI / Gemini CLI / OpenCode │
│  Manual edit / custom scripts / anything that    │
│  writes JSON                                     │
└────────────────────┬────────────────────────────┘
                     │ writes/reads
                     ▼
┌─────────────────────────────────────────────────┐
│         Model: tasks.json (local file)           │
│     100% data sovereignty, plain text, Git-able   │
└────────────────────┬────────────────────────────┘
                     │ watchdog
                     ▼
┌─────────────────────────────────────────────────┐
│      View: Mutsumi TUI (minimal kanban)          │
│   Hot-reload render · mouse/keyboard interaction  │
│   State write-back to JSON                        │
└─────────────────────────────────────────────────┘
```

### 2.2 五つの戒律

1. **ゼロフリクション** — 呼び出しからアクション完了まで 2 秒以内。ローディング画面なし、ログインなし、ネットワークリクエストなし。
2. **レイアウト非依存** — Mutsumi はウィンドウの配置を気にしません。独立プロセスなので、tmux/zellij/マルチモニターなど自由に使えます。
3. **Agent 非依存** — 特定の LLM や Agent に束縛されません。JSON を書けるプログラムならすべて正当な Controller です。
4. **ハッカブル・ファースト** — 公式スケルトンを提供しつつ、ユーザーはデータ構造、テーマ、キーバインド、ビューを簡単にカスタマイズできます。
5. **ローカルオンリー** — ネットワーク依存ゼロ。データはファイル、ファイルはローカルに。

## 3. ターゲットユーザー

**プライマリペルソナ：マルチスレッド型個人**

- ブラウザ、QQ グループ、Reddit、Discord、フォーラムなど複数の場所を同時に巡回している
- 複数の Agent を異なるタスクで同時に実行している
- 毎日とても忙しく、すべてのインタラクションが「サクサク」であることが必要
- ターミナルが主な作業環境（少なくとも抵抗感がない）
- ギークツールへの自然な親和性があり、DIY やカスタマイズが好き

**対象外：**

- チームコラボレーション/共有ボードが必要な PM（Linear を使ってください）
- ガントチャートやリソース配分が必要なプロジェクトマネージャー（Jira を使ってください）
- ターミナルに一切触れないユーザー（Todoist を使ってください）

## 4. アーキテクチャ概要

### 4.1 システム構成図

```
                    ┌──────────────────────┐
                    │   Agent A (write)     │
                    │   Claude Code         │
                    └──────────┬───────────┘
                               │
┌──────────────┐               ▼              ┌──────────────┐
│  Agent B     │        ┌────────────┐        │  Agent C     │
│  Codex CLI   │───────▶│ tasks.json │◀───────│  custom script│
└──────────────┘        └─────┬──────┘        └──────────────┘
                              │
                    ┌─────────┼─────────┐
                    │   watchdog watch   │
                    ▼                   ▼
             ┌────────────┐     ┌────────────┐
             │ Mutsumi TUI│     │ event.log  │
             │ (render+UX) │     │ (reverse   │
             │             │     │  notify)   │
             └─────┬──────┘     └────────────┘
                   │
                   │ user clicks done
                   ▼
             write back tasks.json
```

### 4.2 コンポーネント詳細

| コンポーネント | 責務 | 技術 |
|---|---|---|
| **TUI レンダラー** | タスクリストの描画、ユーザーインタラクションの処理 | Textual (Python) |
| **ファイルウォッチャー** | tasks.json の変更を監視し、再描画をトリガー | watchdog |
| **データレイヤー** | tasks.json の読み書き、スキーマバリデーション | pydantic |
| **CLI インターフェース** | 非 TUI のコマンドライン CRUD を提供 | click / typer |
| **設定ローダー** | ユーザー設定の読み込み（テーマ、キーバインド、言語） | tomllib (stdlib) |
| **i18n エンジン** | UI テキストの多言語切り替え | カスタム（シンプルな dict） |
| **イベントエミッター** | Agent への逆通知（オプション） | ファイルの追記書き込み |

### 4.3 技術スタック

| レイヤー | 選択 | 理由 |
|---|---|---|
| 言語 | Python 3.12+ | Textual エコシステム、開発速度、uv とのゼロフリクション |
| パッケージマネージャー | uv | 超高速、モダン、ギーク美学にマッチ |
| TUI フレームワーク | Textual | マウスサポート、アニメーション、CSS ライクなスタイリング、最小限のコード |
| CLI フレームワーク | click | 成熟・安定、Textual と競合せず共存可能 |
| バリデーション | pydantic v2 | JSON スキーマバリデーション、超高速、型安全 |
| ファイル監視 | watchdog | クロスプラットフォーム、成熟、イベント駆動 |
| 設定フォーマット | TOML | 人間が読みやすい、Python 標準ライブラリにネイティブ対応 (tomllib) |
| 配布 | uv tool install | 依存関係ゼロのインストール体験 |

## 5. データ契約

> 詳細なスキーマ定義は `docs/specs/DATA_CONTRACT.md` を参照してください。

### 5.1 設計思想

- **公式スケルトンを提供しつつ、ユーザーが簡単にカスタマイズ可能**
- ベースフィールドには明確なセマンティクスとバリデーションルールがあります
- ユーザーは任意のカスタムフィールドを追加可能 — Mutsumi は無視しますが、決して削除しません
- ネスト（サブタスク）は理論上無制限。TUI はデフォルトで 3 レベルまで描画しますが、設定変更可能です

### 5.2 最小タスクオブジェクト

```json
{
  "id": "01JQ8X7K3M0000000000000000",
  "title": "重構 Auth 模組",
  "status": "pending",
  "scope": "day",
  "priority": "high",
  "tags": ["dev"],
  "children": []
}
```

### 5.3 ID 戦略

**UUIDv7**（時刻ソート可能な UUID）を使用します：

- 作成時刻順に自然にソートされます
- 中央コーディネーションなしで一意性が保証されます
- Agent と TUI の両方が独立して ID を生成できます
- Python 3.12+ でネイティブサポート（`uuid.uuid7()` — またはフォールバックとして `uuid7` ライブラリ）

### 5.4 スコープ：ハイブリッドモード

`scope` フィールドはハイブリッドモードをサポートします：

- ユーザー/Agent は **手動で** `scope: "day"` を静的ラベルとして設定できます
- タスクに `due_date` フィールドが含まれている場合、TUI は現在の日付に基づいてビュー割り当てを **自動推論** します
- 手動の `scope` は自動推論より優先されます
- `scope` も `due_date` も持たないタスクは `inbox` に振り分けられます

### 5.5 並行書き込み戦略

| シナリオ | 処理方法 |
|---|---|
| TUI が変更 → 書き込み | 最新ファイルを読み取り → 対象フィールドを変更 → アトミック書き込み（一時ファイル + リネーム） |
| Agent が変更 → watchdog | ファイル変更を検知 → リロード → TUI を再描画 |
| 同時書き込み（極めて稀） | Last Write Wins; 次の watchdog トリガーで TUI が自己修復 |
| JSON フォーマットの破損 | TUI がエラーバッジを表示し、最後の有効な状態を保持。上書きは行わない |

アトミック書き込みのフロー：

```
TUI click → read tasks.json → modify in memory → write to .tasks.json.tmp → os.rename() → watchdog detects → re-render
```

`os.rename()` は POSIX システムにおいてアトミックであり、書き込み途中のファイルが読み取られることを防ぎます。

## 6. TUI 仕様

> 詳細なインタラクション仕様は `docs/specs/TUI_SPEC.md` を参照してください。

### 6.1 ビュータブ

```
┌─────────────────────────────────────────────┐
│  [Today] [Week] [Month] [Inbox]    mutsumi  │
├─────────────────────────────────────────────┤
│                                             │
│  ▼ HIGH                                     │
│  [ ] 重構 Auth 模組              dev   ★★★  │
│  [x] 修復快取穿透 Bug           bugfix ★★★  │
│                                             │
│  ▼ NORMAL                                   │
│  [ ] 寫週報                      life  ★★   │
│  [ ] Review PR #42               dev   ★★   │
│    └─ [ ] 検査型別安全                      │
│    └─ [x] 跑通測試                          │
│                                             │
│  ▼ LOW                                      │
│  [ ] 更新 README                 docs  ★    │
│                                             │
├─────────────────────────────────────────────┤
│  6 tasks · 1 done · 5 pending    🔇 quiet   │
└─────────────────────────────────────────────┘
```

### 6.2 TUI での CRUD

TUI はフル CRUD をサポートしており、外部 Agent なしで単独で使用できます。

| アクション | マウス | キーボード |
|---|---|---|
| 作成 | 下部の [+New] ボタン | `n` → ポップアップ入力 |
| 表示 | タスク行をクリックして展開 | `Enter` で展開 |
| 編集 | タイトルをダブルクリック | `e` で選択中のタスクを編集 |
| 削除 | 右クリックメニュー → 削除 | `dd`（vim スタイル） |
| 完了 | チェックボックスをクリック | `Space` |
| 移動 | ドラッグ＆ドロップ（v2） | `j/k` で上下移動 |

### 6.3 キーボードスキーム：マルチプリセット

複数のプリセットキーバインドスキームを提供しています。ユーザーはスキーム間を切り替えたり、設定で完全にカスタマイズしたりできます：

- **vim**（デフォルト）：`j/k/g/G/dd/Space/n/e/q`
- **emacs**：`C-n/C-p/C-d/C-Space`
- **arrow**：矢印キー + Enter + Delete
- **custom**：`config.toml` でユーザー定義

### 6.4 テーマシステム

- デフォルトテーマ：**Monochrome Zen** — ミニマルな白黒グレー、アクセントカラーはライトティール（Catppuccin Teal に近い）
- 内蔵オプション：`monochrome-zen`、`solarized`、`nord`、`dracula`
- ユーザーは `~/.config/mutsumi/themes/` 配下にカスタム `.toml` テーマファイルを追加可能
- テーマ定義は Textual CSS 変数マッピングに準拠

### 6.5 通知システム（設定可能）

| モード | 動作 | 設定値 |
|---|---|---|
| **quiet** | 完全サイレント。ステータスバーにカウントのみ表示（デフォルト） | `quiet` |
| **badge** | 期限切れタスクが TUI 内で点滅/ハイライト | `badge` |
| **bell** | ターミナルベル（`\a`）を送信。ターミナルアプリが処理方法を決定 | `bell` |
| **system** | システム通知 API を呼び出し（macOS/Linux/Windows） | `system` |

## 7. CLI 仕様

### 7.1 主要コマンド

```bash
# TUI の起動（コアとなる使い方）
mutsumi                           # カレントディレクトリの tasks.json を監視
mutsumi --watch ./project/tasks.json  # パスを指定
mutsumi --watch ~/a.json ~/b.json     # マルチプロジェクト集約

# CRUD（非 TUI モード、スクリプト/Agent 向け）
mutsumi add "修復登入 Bug" --priority high --scope day --tags dev,urgent
mutsumi list                      # 全タスクを一覧表示
mutsumi list --scope today        # スコープでフィルター
mutsumi done <task-id>            # 完了をマーク
mutsumi edit <task-id> --title "新しいタイトル" --priority low
mutsumi rm <task-id>              # 削除

# ユーティリティ
mutsumi init                      # カレントディレクトリに tasks.json テンプレートを生成
mutsumi validate                  # tasks.json のフォーマットを検証
mutsumi setup --agent claude-code    # Agent 統合手順を注入
mutsumi schema                    # JSON Schema を出力（Agent 参照用）
```

### 7.2 マルチプロジェクト集約

`--watch` が複数のパスを受け取った場合、TUI はタブバーにプロジェクトディメンションを追加します：

```
[Project A] [Project B] [All]  ·  [Today] [Week] [Month] [Inbox]
```

または、タスクリスト内でソースプロジェクトをグループとして表示します。

## 8. Agent 統合プロトコル

> 詳細なプロトコルは `docs/specs/AGENT_PROTOCOL.md` を参照してください。

### 8.1 書き込みプロトコル（Agent → Mutsumi）

Agent がやるべきことは一つだけです：**スキーマに従って `tasks.json` に正しく書き込む。**

```
Agent reads tasks.json → modifies in memory → writes entire file back
```

要件：

- 認識できないカスタムフィールドを保持すること（決して破棄しないこと）
- 書き込み後のファイルは有効な JSON であること
- アトミック書き込み（一時ファイル + リネーム）を推奨

### 8.2 読み取りプロトコル（Mutsumi → Agent）

**イベントログメカニズム**：ユーザーが TUI 上で操作を行った際、Mutsumi はオプションで `events.jsonl` に追記します：

```jsonl
{"ts":"2026-03-21T10:00:00Z","event":"task_completed","task_id":"01JQ8X7K3M...","title":"修復快取 Bug"}
{"ts":"2026-03-21T10:01:00Z","event":"task_created","task_id":"01JQ8X7K4N...","title":"寫單元測試"}
```

Agent は `tail -f events.jsonl` を実行することで、TUI 側のユーザーアクションを感知でき、双方向のコミュニケーションを実現します。

### 8.3 スキーマバリデーションの挙動

`tasks.json` に無効なデータが含まれている場合：

| エラー種別 | Mutsumi の動作 |
|---|---|
| JSON 構文エラー | TUI がエラーバナーを表示し、最後の有効なスナップショットを保持 |
| 不明な status 値 | TUI が該当タスクに警告バッジを表示 |
| 必須フィールドの欠落（id/title） | 該当タスクをスキップ。TUI フッターに "1 task skipped" を表示 |
| 不明なカスタムフィールド | 正常に描画し、カスタムフィールドを無視（決して削除しない） |

すべてのバリデーションエラーは stderr および `~/.local/share/mutsumi/error.log` にも書き出されるため、Agent が自己修正を行うことができます。

## 9. 設定システム

### 9.1 設定ファイルの場所

XDG Base Directory 仕様に準拠しています（starship、lazygit、bat など主流の CLI ツールと同様）：

```
~/.config/mutsumi/
├── config.toml          # メイン設定
├── themes/
│   └── my-theme.toml    # カスタムテーマ
└── keys/
    └── my-keys.toml     # カスタムキーバインド
```

プラットフォーム例外：

- macOS：`~/Library/Application Support/mutsumi/`（`~/.config/mutsumi/` も受け付けます）
- Windows：`%APPDATA%\mutsumi\`

### 9.2 設定スキーマ

```toml
[general]
language = "auto"          # "auto" | "en" | "zh"
default_watch = "."        # デフォルトの監視パス
default_scope = "day"      # 起動時のデフォルトタブ

[theme]
name = "monochrome-zen"   # 内蔵テーマ名またはカスタムテーマファイル名
accent_color = "#94e2d5"   # アクセントカラーの上書き

[keys]
preset = "vim"             # "vim" | "emacs" | "arrow" | "custom"

[notifications]
mode = "quiet"             # "quiet" | "badge" | "bell" | "system"

[data]
id_format = "uuidv7"      # "uuidv7" | "ulid" | "auto-increment"

[events]
enabled = true             # events.jsonl に書き出すかどうか
path = "./events.jsonl"    # イベントログのパス
```

## 10. i18n 戦略

### 10.1 実装

```
locales/
├── en.toml
└── zh.toml
```

```toml
# locales/en.toml
[tabs]
today = "Today"
week = "Week"
month = "Month"
inbox = "Inbox"

[status]
tasks = "{count} tasks"
done = "{count} done"
pending = "{count} pending"

[actions]
new_task = "New Task"
confirm_delete = "Delete this task?"
```

### 10.2 言語検出

優先順位：`config.toml` の設定 > `$LANG` 環境変数 > フォールバック `en`

## 11. 配布

### 11.1 メインチャネル

```bash
uv tool install mutsumi
```

ユーザーは Python をあらかじめインストールする必要がありません — `uv` が分離された Python 環境を自動的に管理します。

### 11.2 セカンダリチャネル（MVP 以降）

| チャネル | 優先度 | 備考 |
|---|---|---|
| `pipx` | P1 | uv が利用できない場合のフォールバック |
| `brew` | P2 | macOS ユーザーの習慣に合わせて |
| `nix` | P3 | NixOS コミュニティ向け |
| GitHub Releases | P1 | wheel の直接ダウンロード |

## 12. セキュリティとプライバシー

- **ゼロネットワーク**：Mutsumi はネットワークリクエストを一切行わず、テレメトリも含みません
- **ゼロクラウド**：すべてのデータはローカルファイルシステムに保存されます
- **ファイルパーミッション**：tasks.json のパーミッションは `0600`（オーナーのみ読み書き可能）を推奨します
- **No eval**：tasks.json のフィールド内容を実行することは決してありません

## 13. 未解決の課題

以下の課題は将来の RFC に委ねます：

1. **プラグインシステム** — プラグインメカニズム（例：カスタムビューコンポーネント）を導入すべきか？
2. **同期** — オプションのクロスデバイス同期（Git や Syncthing 経由）を提供すべきか？
3. **タスクテンプレート** — タスクテンプレート（例：デイリースタンドアップテンプレート）をサポートすべきか？
4. **時間管理** — ポモドーロ/タイムトラッキングを統合すべきか？
5. **アーカイブ** — 完了タスクのアーカイブ戦略（ファイル内に保持 vs. archive.json に移動）は？

---

## 付録 A：却下された代替案

| 代替案 | 却下理由 |
|---|---|
| Electron GUI | 「ミニマル」原則に違反 — 起動が遅く、リソース消費が大きい |
| SQLite ストレージ | Agent フレンドリーでない — 直接 cat/edit できない |
| Rust TUI (ratatui) | 開発速度が遅い。Textual の CSS スタイリングの方が高速イテレーションに適している |
| 組み込み Agent | 「疎結合」原則に違反 — モデルをバインドすると汎用性を失う |
| WebSocket 通信 | 過剰設計 — ファイルシステムが最良の IPC である |
| Markdown tasks.md | パース複雑度が高く、ネストサポートが不十分 — v2 に延期 |

## 付録 B：ネーミングとブランディング

> 詳細は `docs/BRAND.md` を参照してください。

**Mutsumi（若叶睦）** — 日本語の「睦」（調和、親しみ）に由来しています。ユーザーのワークフローと調和して共存するという理念を伝えています — 押し付けず、指図せず、ただ静かにそこにいるのです。
