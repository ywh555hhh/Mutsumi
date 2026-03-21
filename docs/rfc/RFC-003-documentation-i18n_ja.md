# RFC-003: ドキュメント国際化 (i18n) 戦略

| 項目       | 内容                                     |
|------------|------------------------------------------|
| **RFC**    | 003                                      |
| **タイトル** | ドキュメント国際化 (i18n) 戦略             |
| **ステータス** | ドラフト                                |
| **著者**   | Wayne (ywh)                              |
| **作成日** | 2026-03-21                               |

> **[English Version](./RFC-003-documentation-i18n.md)** | **[中文版](./RFC-003-documentation-i18n_cn.md)**

---

## 1. 概要

Mutsumi は、ドキュメントおよび TUI テキストを英語（主言語）、中国語、日本語の3言語で提供します。各ドキュメントは言語ごとに個別のファイルとして管理されます — `FILENAME.md`（英語）、`FILENAME_cn.md`（中国語）、`FILENAME_ja.md`（日本語）。本 RFC では、命名規則、メンテナンスルール、および多言語対応の適用範囲を定義します。

## 2. 動機

Mutsumi は3つの主要市場をターゲットとしています：

- **グローバル**: Product Hunt、Hacker News、Reddit /r/commandline — 英語がデフォルトです
- **中国**: V2EX、即刻、WeChat/QQ 開発者コミュニティ — 中国語は膨大な開発者層にリーチできます
- **日本**: プロジェクト名が日本語（若叶睦）であるため、日本の開発者コミュニティは自然なターゲットです

1つのファイル内に複数言語を混在させる方式は、読みにくく管理も煩雑です。ファイルを分離することで、各言語版が明確で、独立してナビゲートでき、メンテナンスも容易になります。

## 3. 命名規則

ローカライズされたドキュメントはすべて、言語サフィックスのパターンに従います：

```
FILENAME.md        → English (primary, un-suffixed)
FILENAME_cn.md     → Chinese (中文)
FILENAME_ja.md     → Japanese (日本語)
```

### 3.1 ファイルマップ全体

```
Mutsumi/
├── README.md
├── README_cn.md
├── README_ja.md
├── CONTRIBUTING.md
├── CONTRIBUTING_cn.md
├── CONTRIBUTING_ja.md
├── CLAUDE.md                          ← English only (machine-consumed)
├── LICENSE                            ← English only (legal standard)
└── docs/
    ├── ROADMAP.md
    ├── ROADMAP_cn.md
    ├── ROADMAP_ja.md
    ├── BRAND.md
    ├── BRAND_cn.md
    ├── BRAND_ja.md
    ├── rfc/
    │   ├── RFC-001-mutsumi-core.md
    │   ├── RFC-001-mutsumi-core_cn.md
    │   ├── RFC-001-mutsumi-core_ja.md
    │   ├── RFC-002-installation-and-onboarding.md
    │   ├── RFC-002-installation-and-onboarding_cn.md
    │   ├── RFC-002-installation-and-onboarding_ja.md
    │   ├── RFC-003-documentation-i18n.md
    │   ├── RFC-003-documentation-i18n_cn.md
    │   └── RFC-003-documentation-i18n_ja.md
    └── specs/
        ├── DATA_CONTRACT.md
        ├── DATA_CONTRACT_cn.md
        ├── DATA_CONTRACT_ja.md
        ├── AGENT_PROTOCOL.md
        ├── AGENT_PROTOCOL_cn.md
        ├── AGENT_PROTOCOL_ja.md
        ├── TUI_SPEC.md
        ├── TUI_SPEC_cn.md
        └── TUI_SPEC_ja.md
```

### 3.2 相互参照ヘッダー

各ファイルには、メタデータテーブルの直後に言語切り替えリンクを設置します：

英語ファイル：
```markdown
> **[中文版](./FILENAME_cn.md)** | **[日本語版](./FILENAME_ja.md)**
```

中国語ファイル：
```markdown
> **[English Version](./FILENAME.md)** | **[日本語版](./FILENAME_ja.md)**
```

日本語ファイル：
```markdown
> **[English Version](./FILENAME.md)** | **[中文版](./FILENAME_cn.md)**
```

## 4. 適用範囲：多言語対応する / しないもの

| コンテンツ | 多言語対応？ | 理由 |
|---|---|---|
| `docs/rfc/*.md` | はい | コア仕様、すべてのユーザーに必要 |
| `docs/specs/*.md` | はい | 技術的な契約仕様 |
| `docs/ROADMAP.md` | はい | プロジェクト進捗管理 |
| `docs/BRAND.md` | はい | ブランドアイデンティティ |
| `README.md` | はい | プロジェクトの顔 |
| `CONTRIBUTING.md` | はい | コミュニティ参加ガイド |
| `CLAUDE.md` | **いいえ**（英語のみ） | AI エージェントが読み取る機械向けファイル |
| `LICENSE` | **いいえ**（英語のみ） | 法律上の標準 |
| コード内コメント | **いいえ**（英語のみ） | 開発標準 |
| コミットメッセージ | **いいえ**（英語のみ） | Git の慣例 |
| TUI インターフェーステキスト | 別システム | ランタイムの `locales/*.toml` ファイルで管理 |

## 5. TUI i18n とドキュメント i18n

これらは完全に独立した2つのシステムです：

| 観点 | TUI i18n | ドキュメント i18n |
|---|---|---|
| 配置場所 | `mutsumi/i18n/locales/` | `_cn.md` / `_ja.md` サフィックス付きファイル |
| フォーマット | TOML ロケールファイル | 個別の Markdown ファイル |
| 切り替え方法 | ランタイム設定 / `$LANG` 環境変数 | 読者がファイルを選択 |
| 対応言語 | `en`, `zh`, `ja`（拡張可能） | EN + ZH + JA |
| メンテナー | コードコントリビューター | ドキュメントコントリビューター |

## 6. コントリビューションルール

### 6.1 新規ドキュメントの追加

1. まず英語版を作成します：`FEATURE.md`
2. 中国語版を作成します：`FEATURE_cn.md`
3. 日本語版を作成します：`FEATURE_ja.md`（最初はスタブとして「翻訳募集中」の注記を付けることも可能です）
4. すべてのファイルに相互参照ヘッダーを追加します
5. すべてのファイルは同じ構造を維持します（同じセクション、同じ見出し番号）

### 6.2 既存ドキュメントの更新

ドキュメントを変更する際は、すべての言語版を同時に更新**すべき**です。一部の言語のみを更新した PR は、その旨を PR の説明に記載し、レビュアーがフラグを立てられるようにしてください。

### 6.3 翻訳品質

- 翻訳は逐語訳ではなく、**自然な表現**を心がけてください
- 中国語版では、より口語的な開発者向け表現を使用できます（例：「成功运行」の代わりに「跑通」）
- 日本語版では、標準的な技術日本語を使用してください（ドキュメントにはです/ます体）
- 技術用語は英語のまま残します：`watchdog`, `TUI`, `JSON`, `pydantic`, `TOML`, `CLI`, `UUID`
- 製品名はそのまま使用します：`Mutsumi`, `Product Hunt`, `Textual`, `Claude Code`

### 6.4 構造の一貫性

すべての言語版で同じセクション構造を維持する必要があります：
- 同じセクション数
- 同じ見出し階層
- 同じコードブロックとサンプル（コードは言語に依存しません）
- テーブルの説明文は異なっていても構いませんが、同じフィールドをカバーする必要があります

## 7. 対応言語（現在）

Mutsumi は初日から3言語をサポートします：

| 言語 | ドキュメントサフィックス | TUI ロケールファイル | 優先度 |
|---|---|---|---|
| 英語 | `.md`（サフィックスなし） | `locales/en.toml` | 主言語（デフォルト） |
| 中国語（簡体字） | `_cn.md` | `locales/zh.toml` | 初日対応 |
| 日本語 | `_ja.md` | `locales/ja.toml` | 初日対応 |

TUI `config.toml` の言語設定フィールド：
```toml
[general]
language = "auto"   # "auto" | "en" | "zh" | "ja"
```

`"auto"` は `$LANG` / `$LC_ALL` 環境変数から検出します：
- `ja_JP.*` → 日本語
- `zh_CN.*` / `zh_TW.*` → 中国語
- その他すべて → 英語

## 8. 将来：追加言語の対応

韓国語やスペイン語などのコミュニティ需要が高まった場合：

```
FILENAME.md        → English (primary)
FILENAME_cn.md     → Chinese
FILENAME_ja.md     → Japanese
FILENAME_ko.md     → Korean
```

`_xx` サフィックスには ISO 639-1 言語コードを使用します。英語はサフィックスなしの主言語として維持されます。
