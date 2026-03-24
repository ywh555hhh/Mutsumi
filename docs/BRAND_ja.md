# Mutsumi ブランドアイデンティティ

> **[English Version](./BRAND.md)** | **[中文版](./BRAND_cn.md)**

| ステータス | ドラフト |
|---|---|
| 日付 | 2026-03-21 |

---

## 1. 名前

### 1.1 Primary

**Mutsumi** — グローバルで使われる英語識別子です。

### 1.2 Japanese

**若叶睦** (わかば むつみ / Wakaba Mutsumi)

- **若叶 (Wakaba)** — 若い葉、新芽。新しい始まり、軽やかさ、控えめな優雅さを象徴します。
- **睦 (Mutsumi)** — 調和、親しさ。あなたの workflow と穏やかに共存することを意味します。

### 1.3 Chinese

**睦** — 「和睦（調和）」から。また「默默（静かに）」を連想させる音の響きもあり、静かで邪魔をしないツールらしさを表します。

### 1.4 Tagline

*Never lose a thread.*

### 1.5 Elevator Pitch

> Your threads, always in sight. AI agents が書き込み、あなたが glance する terminal task board。1 つの keystroke で summon され、もう 1 つで消える。

---

## 2. Personality

Mutsumi は attention を叫んで奪う product ではありません。彼女の personality は次の通りです。

| Trait | Description |
|---|---|
| **Quiet** | 静かに動く。あなたが求めない限り、通知を押しつけない。 |
| **Present** | いつもそこにいる。一目見れば全体像が分かる。 |
| **Peripheral** | 彼女は視界の端に住んでいる。主役でもなければ、隠れてもいない。壁の時計のように。 |
| **Humble** | タスクの管理方法を指図しない。決めるのはあなたと Agent。 |
| **Hackable** | カスタマイズされることを喜ぶ。手を入れるほど生き生きしてくる。 |
| **Fast** | 一瞬で起動する。ゼロレイテンシで反応し、痕跡なく閉じる。 |

もし Mutsumi が人なら、こんな感じです。

> あなたの隣に静かに座り、threads が書かれた付箋を持っている。あなたが glance すると、その紙を少しだけ高く持ち上げる。視線を外せば、ただ穏やかに待っている。

---

## 3. Visual Identity

### 3.1 Logo Concept

コアイメージ：**若葉と抽象的な task list の融合。**

Direction A — Minimal symbol:
```
  ✓ 🌱
```
checkmark と葉をミニマルなラインアートで組み合わせる。

Direction B — ASCII Art（terminal 用）:
```
  mutsumi ♪
```
プレーンテキスト + 音符（調和を表す）。terminal-friendly。

Direction C — Japanese minimalism:
```
  睦
```
1 つの漢字をアイコンにし、書のようなスタイルで見せる。

> 最終ロゴは Phase 4 で designer が完成させる。開発中は Direction B（text logotype）を使う。

### 3.2 Color Palette

#### Primary（Monochrome Zen — Default Theme）

| Token | Hex | Usage |
|---|---|---|
| `bg` | `#0f0f0f` | メイン背景 |
| `surface` | `#1a1a1a` | カード/パネル背景 |
| `border` | `#2a2a2a` | 区切り線 |
| `fg` | `#e0e0e0` | 主テキスト |
| `fg-muted` | `#666666` | 副テキスト |
| `accent` | `#5de4c7` | アクセント（淡いシアン/ミント） |
| `danger` | `#e06c75` | エラー / 高優先度 |
| `warning` | `#e5c07b` | 警告 |
| `success` | `#98c379` | 完了状態 |

#### Design Rationale

- 長時間の terminal 利用に合うよう、ダークグレー基調で視覚ノイズを減らす。
- accent color は mint green（`#5de4c7`）。暗い背景で十分に見えつつ、きつすぎない。
- インスピレーション：Catppuccin Teal + Vercel の黒白ミニマリズム。
- 全体の印象：**静かだが退屈ではない。ミニマルだが安っぽくない。**

### 3.3 Typography

terminal の font choice はユーザーの terminal emulator に委ねられます。推奨：

- **JetBrains Mono** / **Cascadia Code** / **Fira Code** — ligature 対応の monospaced fonts
- TUI では non-monospaced characters は使わない（emoji は例外、ただし控えめに）

### 3.4 Iconography

TUI の icons には Unicode / Nerd Font symbols を使います。

| Concept | Symbol | Fallback (no Nerd Font) |
|---|---|---|
| Pending | `[ ]` | `[ ]` |
| Done | `[x]` | `[x]` |
| High | `★★★` | `!!!` |
| Normal | `★★` | `!!` |
| Low | `★` | `!` |
| Expand | `▶` | `>` |
| Collapse | `▼` | `v` |
| Search | `🔍` | `/` |
| Error | `⚠` | `!` |
| New | `[+]` | `[+]` |

> Mutsumi は Nerd Font を必須にしない。すべての icon に ASCII fallback がある。

---

## 4. Voice & Tone

### 4.1 Documentation Tone

- **簡潔で直接的**: 余計な飾りは不要。要点に行く。
- **技術的に正確**: API docs は標準的な Reference 形式に従う。
- **ときどき温かい**: README に少し personality があるのは歓迎（「Mutsumi はそこで待っている」など）。
- **決して見下さない**: 「簡単に」「ただ」「すぐ」などの言葉は避ける。

### 4.2 README Tone

README は Product Hunt に向けた core narrative。ここでは少し多めの personality が歓迎される。

```
Good: "Mutsumi watches your mutsumi.json and re-renders instantly."
Bad:  "Mutsumi is a revolutionary AI-powered task management solution."

Good: "Let your agent write the JSON. Mutsumi handles the rest."
Bad:  "Simply configure your preferred AI agent integration endpoint."
```

### 4.3 Error Messages

```
Good: "mutsumi.json has errors. Showing last valid state."
Bad:  "FATAL: Invalid JSON format detected in configuration file."

Good: "Task 'Fix auth' is missing an ID. Skipped."
Bad:  "ValidationError: Required field 'id' not found in task object at index 3."
```

---

## 5. Community Identity

### 5.1 GitHub Presence

- **Repository**: `github.com/<user>/mutsumi`
- **Topics**: `tui`, `task-manager`, `terminal`, `python`, `textual`, `cli`, `productivity`, `agent`
- **Description**: "A silent TUI task board that watches your JSON. Agent-agnostic. Layout-agnostic. Zero friction."

### 5.2 Social Hashtags

- `#mutsumi`
- `#terminalproductivity`
- `#tuiapps`

### 5.3 Community Rituals

ユーザーに自分の workspace layout を見せてもらい、「Layout Gallery」を育てていく。

- GitHub Discussions セクション: "Show your layout"
- 標準化された screenshot template: `tmux` / `zellij` config + terminal screenshot
- featured layout は README の Gallery section に載せる

---

## 6. Naming Conventions（Code-level）

### 6.1 Package Name

```
PyPI: mutsumi
Import: import mutsumi
CLI: mutsumi
```

### 6.2 Internal Module Naming

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

### 6.3 Commit Prefix Convention

```
feat:     New feature
fix:      Bug fix
docs:     Documentation
style:    Formatting/themes
refactor: Internal refactor
test:     Add/update tests
chore:    Tooling / build / housekeeping
```

---

## 7. What This Is NOT

Mutsumi は次のようなものではありません。

- 騒がしい productivity mascot
- 何でも入りの project management suite
- cloud / account / sync 前提の system
- 「AI が全部やってくれる」系の black box

彼女は静かな thread-keeper です。
