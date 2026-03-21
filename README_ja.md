# mutsumi ♪

> **[English Version](./README.md)** | **[中文版](./README_cn.md)**

**マルチスレッドなあなたのための、静かなタスクブレイン。**

`tasks.json` を監視するミニマルな TUI タスクボード。あなたの邪魔をしません。AI Agent が頭脳、Mutsumi はあなたの目。

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

一つのターミナルで Claude Code を、もう一つで Codex CLI を動かしながら、Reddit を見て Discord でチャットしている。あなたに必要なタスクボードは：

- **1 秒以内に起動** — ローディングなし、ログインなし、ネットワーク不要
- **AI Agent が `tasks.json` に書き込むと自動で更新**
- **邪魔しない** — ワークフローの押し付けも「こう管理すべき」という説教もなし
- **どんな Agent でも動く** — Claude Code、Codex CLI、Gemini CLI、Aider、シェルスクリプト

それが Mutsumi です。JSON を監視して、瞬時にレンダリングする。それだけ。

## インストール

```bash
uv tool install mutsumi
```

Python の事前インストールは不要です。`uv` がすべて自動で管理します。

```bash
# 代替手段
pipx install mutsumi

# ハッカー向け
git clone https://github.com/ywh555hhh/Mutsumi.git
cd Mutsumi && uv sync && uv run mutsumi
```

## クイックスタート

```bash
# TUI を起動（カレントディレクトリの tasks.json を監視）
mutsumi

# インタラクティブセットアップ（1 画面にすべてのオプションを表示）
mutsumi init

# Agent 連携の設定
mutsumi setup --agent claude-code
```

## 仕組み

```
┌──────────────┐        ┌────────────┐        ┌──────────────┐
│  AI Agent    │───────▶│ tasks.json │◀───────│  あなた(TUI) │
│  (Controller)│ 書込   │  (Model)   │ 監視   │  (View)      │
└──────────────┘        └────────────┘        └──────────────┘
```

**MVC 分離**：Agent が JSON を書く。Mutsumi が監視してレンダリングする。あなたが操作するとファイルに書き戻す。シンプル。

## 機能

- **ホットリロード**：ファイル変更で TUI を即座に再描画（100ms デバウンス）
- **Vim/Emacs/Arrow キーバインド**：好みのスタイルを選ぶか、カスタム定義
- **4 つの組み込みテーマ**：Monochrome Zen（デフォルト）、Solarized、Nord、Dracula
- **i18n**：英語、中国語、日本語を標準サポート
- **Agent 非依存**：JSON を書けるプログラムなら何でも Controller になれる
- **ゼロネットワーク**：100% ローカル。テレメトリなし。クラウドなし。データは永遠にあなたのもの。
- **ハック可能**：TOML 設定、カスタムテーマ、カスタムキーバインド — すべて自由に変更可能

## Agent 連携

AI Agent は `tasks.json` を読み書きするだけです：

```bash
# ワンライナー：インストール + 設定 + 連携
uv tool install mutsumi && mutsumi init --defaults && mutsumi setup --agent claude-code
```

対応 Agent：Claude Code、Codex CLI、Gemini CLI、OpenCode、Aider、または任意のカスタムスクリプト。

詳細は [Agent 連携プロトコル](docs/specs/AGENT_PROTOCOL_ja.md) をご覧ください。

## ドキュメント

| ドキュメント | 説明 |
|---|---|
| [RFC-001：コアアーキテクチャ](docs/rfc/RFC-001-mutsumi-core_ja.md) | プロダクト定義とアーキテクチャ |
| [RFC-002：インストール体験](docs/rfc/RFC-002-installation-and-onboarding_ja.md) | インストールとオンボーディング |
| [RFC-003：i18n 戦略](docs/rfc/RFC-003-documentation-i18n_ja.md) | ドキュメント国際化戦略 |
| [データ契約](docs/specs/DATA_CONTRACT_ja.md) | `tasks.json` スキーマ仕様 |
| [Agent プロトコル](docs/specs/AGENT_PROTOCOL_ja.md) | Agent 連携プロトコル |
| [TUI 仕様](docs/specs/TUI_SPEC_ja.md) | TUI インタラクション仕様 |
| [ロードマップ](docs/ROADMAP_ja.md) | 開発ロードマップ |
| [ブランド](docs/BRAND_ja.md) | ブランドアイデンティティ |

## コントリビューション

[CONTRIBUTING_ja.md](CONTRIBUTING_ja.md) をご覧ください。

## ライセンス

[MIT](LICENSE)

---

*mutsumi（若叶睦）—— "和睦、親しみ"。何をすべきかは言わない。ただ静かに、そこで待っている。*
