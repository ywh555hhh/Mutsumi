# Mutsumi ブランドアイデンティティ

> **[English Version](./BRAND.md)** | **[中文版](./BRAND_cn.md)**

| ステータス | ドラフト             |
|-----------|---------------------|
| 日付       | 2026-03-21          |

---

## 1. 名前

### 1.1 英語名

**Mutsumi** — グローバルで使用される英語識別子です。

### 1.2 日本語名

**若叶睦** (わかば むつみ / Wakaba Mutsumi)

- **若叶 (わかば)** — 若い葉、芽吹き。新しい始まり、軽やかさ、そして控えめな美しさの象徴です。
- **睦 (むつみ)** — 和やか、親しみ。ワークフローと穏やかに共存することを意味します。

### 1.3 中国語名

**睦** — 「和睦（調和）」から。また「默默（静かに）」との音の類似もあり、静かで控えめなツールを表現しています。

### 1.4 タグライン

*マルチスレッドなあなたのための、静かなタスクブレイン。*

### 1.5 エレベーターピッチ

> ミニマルな TUI タスクボード。あなたの JSON を見守り、邪魔をしません。
> AI エージェントに頭脳を任せましょう — Mutsumi はただ、あなたの目になるだけです。

---

## 2. パーソナリティ

Mutsumi は注目を集めようとするプロダクトではありません。その性格は次のとおりです：

| 特性           | 説明                                                                               |
|---------------|------------------------------------------------------------------------------------|
| **静か**       | 静かに動きます。求められない限り、通知は送りません。                                    |
| **そこにいる** | いつもそこにいます。一目見れば、全体像がわかります。                                    |
| **謙虚**       | タスクの管理方法を指図しません。あなた（とあなたのエージェント）が主導権を握ります。       |
| **カスタム自在** | カスタマイズされることを好みます。手を入れるほど、生き生きとしてきます。               |
| **速い**       | 一瞬で起動。ゼロレイテンシのインタラクション。終了しても痕跡を残しません。               |

Mutsumi を人に喩えるなら、こんな女の子です：

> あなたの隣にそっと座って、やることリストが書かれた付箋を手にしている。あなたがふと目を向けると、少しだけ付箋を持ち上げてくれる。視線をそらすと、彼女はただ静かに、そこで待っている。

---

## 3. ビジュアルアイデンティティ

### 3.1 ロゴコンセプト

コアイメージ: **若葉と抽象的なタスクリストの融合。**

ディレクション A — ミニマルシンボル:
```
  ✓ 🌱
```
チェックマークと葉を、ミニマルなラインアートで組み合わせます。

ディレクション B — ASCII アート（ターミナル用）:
```
  mutsumi ♪
```
プレーンテキスト + 音符（調和を表現）。ターミナルフレンドリーです。

ディレクション C — 和のミニマリズム:
```
  睦
```
一文字の漢字をアイコンとして、書道スタイルで表現します。

> 最終的なロゴは Phase 4 でデザイナーが作成します。開発中はディレクション B（テキストロゴタイプ）を使用します。

### 3.2 カラーパレット

#### プライマリ（Monochrome Zen — デフォルトテーマ）

| トークン      | Hex       | 用途                       |
|--------------|-----------|----------------------------|
| `bg`         | `#0f0f0f` | メイン背景                  |
| `surface`    | `#1a1a1a` | カード/パネル背景            |
| `border`     | `#2a2a2a` | 区切り線                    |
| `fg`         | `#e0e0e0` | プライマリテキスト           |
| `fg-muted`   | `#666666` | セカンダリテキスト           |
| `accent`     | `#5de4c7` | アクセント（淡いシアン/ミント）|
| `danger`     | `#e06c75` | エラー / 高優先度            |
| `warning`    | `#e5c07b` | 警告                        |
| `success`    | `#98c379` | 完了ステータス               |

#### デザインの根拠

- ダークグレーのベースで視覚的ノイズを軽減し、長時間のターミナル使用に適しています。
- アクセントカラーはミントグリーン (`#5de4c7`) — ダーク背景で高コントラストでありながら、目に優しい色合いです。
- インスピレーション: Catppuccin Teal + Vercel のモノクロミニマリスト美学。
- 全体的な印象: **静かだが退屈ではない。ミニマルだが安っぽくない。**

### 3.3 タイポグラフィ

ターミナルでのフォント選択は、ユーザーのターミナルエミュレータによって決まります。推奨フォント:

- **JetBrains Mono** / **Cascadia Code** / **Fira Code** — リガチャ対応の等幅フォント
- TUI 内では等幅以外の文字は使用しません（絵文字を除く、使用は控えめに）

### 3.4 アイコノグラフィ

TUI のアイコンには Unicode / Nerd Font シンボルを使用します:

| 概念          | シンボル  | フォールバック（Nerd Font なし）  |
|--------------|---------|--------------------------------|
| 未完了        | `[ ]`   | `[ ]`                          |
| 完了          | `[x]`   | `[x]`                          |
| 高優先度      | `★★★`   | `!!!`                          |
| 通常          | `★★`    | `!!`                           |
| 低優先度      | `★`     | `!`                            |
| 展開          | `▶`     | `>`                            |
| 折りたたみ    | `▼`     | `v`                            |
| 検索          | `🔍`    | `/`                            |
| エラー        | `⚠`     | `!`                            |
| 新規          | `[+]`   | `[+]`                          |

> Mutsumi は Nerd Font を必須としません。すべてのアイコンには ASCII フォールバックがあります。

---

## 4. ボイス & トーン

### 4.1 ドキュメントのトーン

- **簡潔で直接的**: 飾り立てた表現は不要です。要点を伝えます。
- **技術的に正確**: API ドキュメントは標準的なリファレンス形式に従います。
- **時折温かく**: README にちょっとした個性を加えるのは歓迎です（「Mutsumi はそこで、あなたを待っています」）。
- **決して見下さない**: 「簡単に」「ただ」「すぐに」といった言葉は避けます。

### 4.2 README のトーン

README は Product Hunt におけるコアナラティブです。ここではより多くの個性が歓迎されます:

```
Good: "Mutsumi watches your tasks.json and re-renders instantly."
Bad:  "Mutsumi is a revolutionary AI-powered task management solution."

Good: "Let your agent write the JSON. Mutsumi handles the rest."
Bad:  "Simply configure your preferred AI agent integration endpoint."
```

### 4.3 エラーメッセージ

```
Good: "tasks.json has errors. Showing last valid state."
Bad:  "FATAL: Invalid JSON format detected in configuration file."

Good: "Task 'Fix auth' is missing an ID. Skipped."
Bad:  "ValidationError: Required field 'id' not found in task object at index 3."
```

---

## 5. コミュニティアイデンティティ

### 5.1 GitHub プレゼンス

- **リポジトリ**: `github.com/<user>/mutsumi`
- **トピック**: `tui`, `task-manager`, `terminal`, `python`, `textual`, `cli`, `productivity`, `agent`
- **説明**: "A silent TUI task board that watches your JSON. Agent-agnostic. Layout-agnostic. Zero friction."

### 5.2 ソーシャルハッシュタグ

- `#mutsumi`
- `#terminalproductivity`
- `#tuiapps`

### 5.3 コミュニティの習慣

ユーザーに自分のワークスペースレイアウトを披露してもらい、「Layout Gallery」を構築します:

- GitHub Discussions セクション: 「Show your layout」
- 標準化されたスクリーンショットテンプレート: tmux / zellij の設定 + ターミナルスクリーンショット
- 優れたレイアウトは README の Gallery セクションに掲載されます

---

## 6. 命名規約（コードレベル）

### 6.1 パッケージ名

```
PyPI: mutsumi
Import: import mutsumi
CLI: mutsumi
```

### 6.2 内部モジュールの命名

```
mutsumi/
├── app.py          # Textual App entry point
├── tui/            # TUI widgets
├── cli/            # CLI commands
├── core/           # Data layer (models, file I/O)
├── config/         # Config loading
├── i18n/           # Internationalization
└── themes/         # Built-in themes
```

### 6.3 コミットプレフィックス規約

```
feat:     New feature
fix:      Bug fix
docs:     Documentation
style:    Formatting/themes
refactor: Refactoring
test:     Tests
chore:    Build/tooling
i18n:     Internationalization
```
