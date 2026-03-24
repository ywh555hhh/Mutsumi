# RFC-002：インストール、セットアップ、オンボーディング体験

> **[English Version](./RFC-002-installation-and-onboarding.md)** | **[中文版](./RFC-002-installation-and-onboarding_cn.md)**

| フィールド | 値                                                           |
|------------|--------------------------------------------------------------|
| **RFC**    | 002                                                          |
| **タイトル** | インストール、セットアップ、オンボーディング                  |
| **ステータス** | ドラフト                                                   |
| **著者**   | Wayne (ywh)                                                  |
| **作成日** | 2026-03-21                                                   |

---

> **Historical note (2026-03-24):** この RFC は以前の onboarding model を反映したものです。内容の一部は、特に RFC-008 によって後続の product direction に置き換えられています。現在の onboarding / setup baseline については、`README.md`、`docs/BETA_USAGE.md`、`docs/specs/AGENT_PROTOCOL.md`、RFC-008 を優先してください。

## 1. 概要

本 RFC は、ユーザーが Mutsumi をインストール、設定、利用開始する方法を定義します。基本原則は**「軽快でストレスフリー」** — すべてのステップがゼロフリクションであること：コマンド一つでインストール、画面一つで設定、一秒で起動。

## 2. 設計目標

| 目標 | 説明 |
|---|---|
| **ゼロコンフィグで動作** | 引数なし、設定ファイルなしで `mutsumi` を実行 — そのまま動きます |
| **一画面で全設定** | ステップバイステップのウィザードではありません。一画面にすべてのオプションを表示し、クリックで切り替えます |
| **Agent 自動インストール** | Agent がコマンドを一つ実行すれば、Mutsumi の準備完了です |
| **初日からカスタマイズ可能** | 設定は TOML 形式で、人間が読めて、Git フレンドリーです |
| **クリーンにアンインストール** | コマンド一つですべて削除、残留物ゼロです |

## 3. インストール方法

### 3.1 推奨：`uv`

```bash
uv tool install mutsumi
```

- Python の事前インストールは不要です — `uv` が独立した Python 環境を自動的に管理します。

インストール後、`mutsumi` はグローバルな CLI コマンドとして利用可能になります。

### 3.2 代替手段：`pipx`

```bash
pipx install mutsumi
```

`uv` より `pipx` を好むユーザー向けです。同様の隔離環境で動作します。

### 3.3 手動インストール：git clone

```bash
git clone https://github.com/<user>/mutsumi.git
cd mutsumi
uv sync
uv run mutsumi
```

ソースコードを修正したいコントリビューターやハッカー向けです。

### 3.4 スクリプト用ワンライナー

```bash
curl -fsSL https://mutsumi.dev/install.sh | sh
```

インストールスクリプトの処理内容：

1. `uv` がインストール済みか検出し、未インストールの場合は先に `uv` をインストールします
2. `uv tool install mutsumi` を実行します
3. ウェルカムメッセージと次のステップを表示します

## 4. 初回起動体験

### 4.1 ゼロコンフィグ起動

```bash
mutsumi
```

設定ファイルも `tasks.json` もない状態で、Mutsumi は：

1. すべてデフォルト値で起動します（英語、モノクロテーマ、vim キーバインド、静音通知）
2. フレンドリーなプロンプトで空の状態を表示します
3. カレントディレクトリに `tasks.json` を作成するかどうかを提案します

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

### 4.2 インタラクティブセットアップ：`mutsumi init`

**これが「軽快」な体験の核心です。**

`mutsumi init` は**単一画面の TUI 設定パネル**を起動します。すべてのオプションが一度に表示されます。複数ステップのウィザードはありません。「次へ」ボタンもありません。クリックや Tab で項目を移動し、切り替えるだけです。

#### 4.2.1 設定パネルのワイヤーフレーム

```
┌──────────────────────── mutsumi setup ─────────────────────────┐
│                                                                 │
│  ┌─ 基本設定 ───────────────────────────────────────────────┐    │
│  │                                                         │    │
│  │  言語                  (English)  中文                   │    │
│  │  テーマ                ● モノクロ  ○ Catppuccin          │    │
│  │                        ○ Nord      ○ Dracula             │    │
│  │  キーマップ            ● vim   ○ emacs   ○ arrow        │    │
│  │                                                         │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                 │
│  ┌─ 動作設定 ───────────────────────────────────────────────┐    │
│  │                                                         │    │
│  │  デフォルトビュー      ● 今日  ○ 週間  ○ 月間  ○ 受信箱  │    │
│  │  通知                  ● 静音  ○ バッジ ○ ベル  ○ システム│    │
│  │  タスク ID 形式        ● UUIDv7 ○ ULID  ○ 自動採番      │    │
│  │  イベントログ          [x] 有効                          │    │
│  │                                                         │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                 │
│  ┌─ パス設定 ───────────────────────────────────────────────┐    │
│  │                                                         │    │
│  │  監視パス              [./tasks.json                  ] │    │
│  │  設定ディレクトリ      ~/.config/mutsumi/  (読み取り専用) │    │
│  │  イベントログパス      [./events.jsonl                ] │    │
│  │                                                         │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                 │
│  ┌─ プレビュー ─────────────────────────────────────────────┐    │
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
│          [ 保存して起動 ]           [ キャンセル ]                │
│                                                                 │
│  設定は ~/.config/mutsumi/config.toml に保存されました            │
└─────────────────────────────────────────────────────────────────┘
```

#### 4.2.2 操作モデル

| 入力 | 動作 |
|---|---|
| `Tab` / `Shift+Tab` | オプショングループ間でフォーカスを移動します |
| `←` `→` またはマウスクリック | グループ内の選択肢を切り替えます |
| `Space` またはクリック | チェックボックスを切り替えます |
| テキストフィールド | 直接入力し、Tab で確定します |
| [保存して起動] で `Enter` | 設定を書き込み + tasks.json を作成 + TUI を起動します |
| `Escape` または [キャンセル] | 保存せずに終了します |

#### 4.2.3 リアルタイムプレビュー

下部セクションには、生成される `config.toml` の**リアルタイムプレビュー**が表示されます。すべての切り替え・変更がプレビューに即座に反映されます。これにより、ユーザーは完全な透明性と安心感を得られます。

#### 4.2.4 `mutsumi init` が生成するファイル

```
~/.config/mutsumi/
└── config.toml              ← ユーザー設定

./tasks.json                 ← サンプルタスク（存在しない場合）
```

init が作成するサンプル `tasks.json`：

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

### 4.3 セットアップ後の設定変更

```bash
mutsumi config --edit       # $EDITOR で config.toml を開きます
mutsumi config --show       # 現在の設定を標準出力に表示します
mutsumi config --reset      # デフォルト値にリセットします（確認あり）
mutsumi init                # 設定パネルを再実行します（既存の設定を上書きします）
```

## 5. Agent 自動セットアップ

### 5.1 課題

ユーザーは AI Agent が `tasks.json` の存在と読み書き方法を自動的に認識することを望んでいます。手動でのセットアップ（プロンプトテンプレートのコピー、ファイルパスの設定）はフリクションになります。

### 5.2 `mutsumi setup --agent`

```bash
mutsumi setup --agent claude-code
mutsumi setup --agent codex-cli
mutsumi setup --agent aider
mutsumi setup --agent opencode
mutsumi setup --agent custom
```

#### 5.2.1 実行内容

サポートされている各 Agent に対して、`mutsumi setup --agent <name>` は以下を実行します：

| Agent | アクション |
|---|---|
| `claude-code` | Mutsumi 統合ルールをプロジェクトレベルの `CLAUDE.md` に追記します |
| `codex-cli` | `AGENTS.md` を作成・更新します |
| `aider` | プロンプトを標準出力に表示します（手動統合） |
| `opencode` | `opencode.md` の指示を更新します |
| `gemini-cli` | `GEMINI.md` を作成・更新します |
| `custom` | プロンプトテンプレートを標準出力に表示し、手動で統合できるようにします |

#### 5.2.2 注入されるプロンプトテンプレート

Agent 設定に注入されるプロンプト：

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

#### 5.2.3 インタラクティブな Agent セットアップ

Agent 名を指定せずに実行すると、選択画面が起動します：

```
┌──────────── Agent を選択してください ──────────────────────────┐
│                                                                │
│  使用している Agent を選んでください（クリックまたは矢印+Enter） │
│                                                                │
│  ● Claude Code     → CLAUDE.md に書き込みます                   │
│  ○ Codex CLI       → AGENTS.md に書き込みます                     │
│  ○ Aider           → 標準出力に表示します                          │
│  ○ OpenCode        → opencode.md に書き込みます                 │
│  ○ Gemini CLI      → GEMINI.md に書き込みます                   │
│  ○ Custom          → プロンプトを標準出力に表示します             │
│                                                                │
│  [セットアップ]  [キャンセル]                                    │
│                                                                │
│  ヒント：複数の Agent に対してこのコマンドを繰り返し実行できます。 │
└────────────────────────────────────────────────────────────────┘
```

### 5.3 Agent ワンライナーでインストール+セットアップ

究極のゼロフリクション Agent 体験：

```bash
# Agent（例：Claude Code）がこの一つのコマンドを実行するだけです：
uv tool install mutsumi && mutsumi init --defaults && mutsumi setup --agent claude-code
```

この処理は：

1. Mutsumi をグローバルにインストールします
2. デフォルト値で設定を作成します（インタラクティブ UI なし）
3. 統合プロンプトを Agent 設定に注入します

`--defaults` フラグはインタラクティブな設定パネルをスキップし、すべてのデフォルト値を使用します。

## 6. アップグレード

```bash
uv tool upgrade mutsumi          # 最新版にアップグレードします
uv tool upgrade mutsumi==0.3.0   # 特定のバージョンに固定します
```

### 6.1 設定のマイグレーション

新しいバージョンで設定の変更が導入された場合：

- 新しいフィールド：デフォルト値で自動的に補完され、既存の設定はそのまま維持されます
- 削除されたフィールド：サイレントに無視され、エラーは発生しません
- 設定ファイルの自動書き換えは行いません — ユーザーのファイルは神聖なものです

### 6.2 破壊的変更

`tasks.json` のスキーマに破壊的変更がある場合（v1.0 以前ではほぼありません）：

```bash
mutsumi migrate            # インタラクティブなマイグレーション
mutsumi migrate --dry-run  # 変更のプレビュー
```

## 7. アンインストール

```bash
uv tool uninstall mutsumi
```

これにより CLI バイナリが削除されます。設定ファイルとデータファイルは自動的には削除**されません**。

完全にクリーンアップするには：

```bash
uv tool uninstall mutsumi
rm -rf ~/.config/mutsumi/                    # 設定
rm -rf ~/.local/share/mutsumi/               # ログ
# tasks.json はあなたのデータです — 必要であれば手動で削除してください
```

## 8. プラットフォーム固有の注意事項

### 8.1 macOS

```bash
# uv がインストールされていない場合：
curl -LsSf https://astral.sh/uv/install.sh | sh
uv tool install mutsumi
```

設定ファイルの場所：`~/.config/mutsumi/`（XDG）または `~/Library/Application Support/mutsumi/`

### 8.2 Linux

macOS と同じです。`~/.config/mutsumi/` は XDG 標準に準拠します。

### 8.3 Windows

```powershell
# uv をインストール
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
uv tool install mutsumi
```

設定ファイルの場所：`%APPDATA%\mutsumi\`

Windows Terminal Quake Mode のセットアップ（推奨）：

1. Windows Terminal の設定を開き、新しいプロファイルを追加します
2. コマンドに `mutsumi` を設定します
3. Quake Mode のキーバインドを有効にします（デフォルト：`` Win+` ``）

## 9. 設計根拠

### 9.1 なぜステップバイステップではなく一画面方式なのか？

ステップバイステップのウィザードは不安を生みます：「残り何ステップ？戻れるの？何か見落とした？」一画面方式のパネルはこうした不安を完全に排除します。すべてが見え、変更したいところを変更し、それで完了です。

### 9.2 なぜリアルタイムプレビューなのか？

Mutsumi をインストールするユーザーは、おそらくターミナルのパワーユーザーであり、TOML を理解しています。実際に生成される設定ファイルを表示することで、信頼を構築すると同時に、設定フォーマットを自然に学んでもらえます。

### 9.3 なぜ Agent セットアップは分離されているのか？

Agent セットアップは Mutsumi のドメイン外のファイル（`CLAUDE.md`、`AGENTS.md` など）を変更します。`mutsumi init` と分離することで、最小驚き原則に従います — init は Mutsumi 自身の設定のみを操作します。

---

## 付録 A：セットアップ関連 CLI 完全リファレンス

```
mutsumi init                    インタラクティブな設定パネルを起動します
mutsumi init --defaults         すべてデフォルト値で設定を作成します（非インタラクティブ）
mutsumi init --lang zh          中国語をデフォルト言語として設定を作成します
mutsumi setup --agent <name>    Agent 統合を設定します
mutsumi setup --agent           インタラクティブな Agent 選択画面を起動します
mutsumi config --edit           $EDITOR で設定ファイルを開きます
mutsumi config --show           現在の設定を表示します
mutsumi config --reset          設定をデフォルト値にリセットします
mutsumi config --path           設定ファイルのパスを表示します
mutsumi validate                tasks.json のスキーマを検証します
mutsumi schema                  tasks.json の JSON Schema を出力します
mutsumi schema --format md      Markdown 形式でスキーマを出力します
```
