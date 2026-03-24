# mutsumi ♪

> **[English Version](./README.md)** | **[中文版](./README_cn.md)**

**マルチスレッドなあなたのための、静かなタスクブレイン。**

`mutsumi.json` を監視し、できるだけ邪魔をしないミニマルな TUI タスクボードです。古いプロジェクトでは `tasks.json` にもフォールバックします。AI Agent を頭脳に、Mutsumi を目にしてください。

```
┌─────────────────────────────────────────────────────┐
│  [今日] [今週] [今月] [受信箱]            mutsumi ♪  │
├─────────────────────────────────────────────────────┤
│                                                     │
│  ▼ HIGH ─────────────────────────────────────────   │
│  [ ] Auth モジュールのリファクタリング dev,backend ★★★│
│  [x] キャッシュ貫通バグの修正        bugfix      ★★★│
│                                                     │
│  ▼ NORMAL ───────────────────────────────────────   │
│  [ ] 週報を書く                      life        ★★ │
│  [ ] PR #42 のレビュー               dev         ★★ │
│    └─ [ ] 型安全性の確認             (1/2)          │
│    └─ [x] テストを通す                               │
│                                                     │
│  ▼ LOW ──────────────────────────────────────────   │
│  [ ] README の更新                   docs        ★  │
│                                                     │
├─────────────────────────────────────────────────────┤
│  6 件のタスク · 2 件完了 · 4 件未完了               │
└─────────────────────────────────────────────────────┘
```

## なぜ Mutsumi なのか？

1 つのターミナルで Claude Code を、別のターミナルで Codex CLI を動かしながら、Reddit を見て Discord で会話している。そんなときに必要なのは、次のようなタスクボードです。

- **1 秒未満で呼び出せる** — ローディングなし、ログインなし、ネットワーク不要
- **AI Agent が `mutsumi.json` に書き込むと自動更新される**
- **邪魔をしない** — ワークフローを押しつけず、やり方を説教しない
- **どんな Agent とも使える** — Claude Code、Codex CLI、Gemini CLI、Aider、または shell script

それが Mutsumi です。JSON を監視し、すぐに再描画する。それだけです。

## インストール

```bash
# Beta install (from git)
uv tool install git+https://github.com/ywh555hhh/Mutsumi.git
```

Python を事前に入れておく必要はありません。`uv` が全部面倒を見ます。

```bash
# 代替
pipx install mutsumi-tui

# ハッカーパス
git clone https://github.com/ywh555hhh/Mutsumi.git
cd Mutsumi && uv sync && uv run mutsumi
```

## クイックスタート

```bash
# TUI を起動（mutsumi.json を優先し、tasks.json にフォールバック）
mutsumi

# 対話式セットアップ
mutsumi init

# Agent 連携の設定
mutsumi setup --agent claude-code
```

## 仕組み

```
┌──────────────┐        ┌──────────────┐        ┌──────────────┐
│  AI Agent    │───────▶│ mutsumi.json │◀───────│  あなた(TUI) │
│  (Controller)│ 書込   │  (Model)     │ 監視   │  (View)      │
└──────────────┘        └──────────────┘        └──────────────┘
```

**MVC 分離**：Agent が JSON を書き、Mutsumi が監視して描画し、あなたの操作は再びファイルに書き戻されます。古いプロジェクトでは `tasks.json` も互換フォールバックとして扱われます。

## 機能

- **ホットリロード**：ファイル変更で TUI を即座に再描画（100ms デバウンス）
- **Arrows / Vim / Emacs キーバインド**：デフォルトは `arrows`。上級ユーザーは切り替えやカスタム定義が可能
- **4 つの内蔵テーマ**：Monochrome Zen（デフォルト）、Solarized、Nord、Dracula
- **多言語対応**：英語、中国語、日本語を標準搭載
- **Agent 非依存**：JSON を書けるプログラムなら何でも controller になれる
- **マルチソースダッシュボード**：Main + Personal + project タブと集約進捗
- **ゼロネットワーク**：100% ローカル。テレメトリなし。クラウドなし。データは常にあなたのもの
- **Hackable**：TOML 設定、カスタムテーマ、カスタムキーバインドを自由に変更可能

## Agent 連携

AI Agent は `mutsumi.json` を読み書きするだけで十分です。プロジェクトがまだ古い `tasks.json` を使っている場合でも、Mutsumi は自動で認識します。

```bash
# ワンライナー: install + configure + integrate
uv tool install git+https://github.com/ywh555hhh/Mutsumi.git && mutsumi init && mutsumi setup --agent claude-code
```

対応 Agent：Claude Code、Codex CLI、Gemini CLI、OpenCode、Aider、または任意のカスタムスクリプト。

詳細は [Agent Protocol](docs/specs/AGENT_PROTOCOL_ja.md) を参照してください。1 ページの速見表として [AGENT_ja.md](AGENT_ja.md) もあります。

## ターミナル連携

### tmux（推奨）

```bash
# 1 コマンド: 左側 shell + 右側 Mutsumi split-pane
bash scripts/tmux-dev.sh

# セッション名と幅をカスタマイズ
MUTSUMI_WIDTH=40 bash scripts/tmux-dev.sh my-project
```

### iTerm2

1. `Cmd+D` で縦分割
2. 右ペイン: `mutsumi`
3. 左ペイン: agent / shell

### Demo

```bash
# 左ペインで demo スクリプトを実行して live-reload を確認
bash scripts/demo.sh
```

## ドキュメント

| ドキュメント | 説明 |
|---|---|
| [AGENT チートシート](AGENT_ja.md) | Agent 向けの 1 ページ統合ガイド |
| [開発ルール](CLAUDE_ja.md) | プロジェクト開発ルールとワークフロー |
| [Beta 使用 SOP](docs/BETA_USAGE_ja.md) | 現行 `1.0.0b1` beta の利用・テスト手順 |
| [Beta 内部テスト手引き](docs/BETA_V1_ja.md) | beta playbook とスコープ境界 |
| [RFC-001: コアアーキテクチャ](docs/rfc/RFC-001-mutsumi-core_ja.md) | プロダクト定義とアーキテクチャ |
| [RFC-002: インストールと導入](docs/rfc/RFC-002-installation-and-onboarding_ja.md) | install と onboarding 体験 |
| [RFC-003: i18n 戦略](docs/rfc/RFC-003-documentation-i18n_ja.md) | ドキュメント国際化戦略 |
| [RFC-004: 三入力等価](docs/rfc/RFC-004-triple-input-parity_ja.md) | keyboard / mouse / CLI の等価原則 |
| [RFC-007: マルチソース Hub](docs/rfc/RFC-007-multi-source-hub_ja.md) | Main ダッシュボードとマルチソース構成 |
| [RFC-008: 開箱オンボーディング](docs/rfc/RFC-008-out-of-box-first-run-onboarding_ja.md) | 初回起動と onboarding 設計 |
| [RFC-009: カレンダービュー](docs/rfc/RFC-009-calendar-view_ja.md) | 計画中の組み込みカレンダー構成 |
| [Data Contract](docs/specs/DATA_CONTRACT_ja.md) | `mutsumi.json` schema と互換ルール |
| [Agent Protocol](docs/specs/AGENT_PROTOCOL_ja.md) | Agent 連携プロトコル |
| [TUI Spec](docs/specs/TUI_SPEC_ja.md) | TUI インタラクション仕様 |
| [Roadmap](docs/ROADMAP_ja.md) | 開発ロードマップ |
| [Brand](docs/BRAND_ja.md) | ブランドアイデンティティ |

## コントリビューション

[CONTRIBUTING_ja.md](CONTRIBUTING_ja.md) を参照してください。

## ライセンス

[MIT](LICENSE)

---

*mutsumi（若叶睦）—— 「和睦、親しみ」。何をすべきかは言わない。ただ静かに、そこで待っている。*
