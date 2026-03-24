# RFC-006: Brand & Narrative Reset — 「Never Lose a Thread」

> **[English Version](./RFC-006-brand-narrative-reset.md)** | **[中文版](./RFC-006-brand-narrative-reset_cn.md)**

| Field | Value |
|---|---|
| **RFC** | 006 |
| **Title** | Brand & Narrative Reset |
| **Status** | Accepted |
| **Author** | Wayne (ywh) |
| **Created** | 2026-03-22 |

---

## Abstract

この RFC は、Mutsumi のブランドナラティブを「ミニマルな TUI タスクボード」から、より大きな解決策の View layer へと再定義します。つまり、**マルチスレッドな人間のために常時そこにいる thread-keeper** です。

この転換によって変わるのは次の点です。

- 誰についての物語なのか —— ツールではなく、ユーザーの脳についての物語になる
- 何の問題を解くのか —— 「タスク管理の摩擦」ではなく、コンテキスト切り替え時の thread loss を解く
- エコシステム内でどう位置づけるのか —— 単体製品ではなく、zero-friction workflow を構成する 1 コンポーネントとして位置づける

新しい tagline: **Never lose a thread.**

---

## 1. Motivation: なぜリセットするのか

### 1.1 古いナラティブ

リセット前のナラティブは、Mutsumi を 1 つの製品として位置づけていました。

> “A minimal TUI task board that watches your `tasks.json` and stays out of your way.”
> “Let your AI agent be the brain — Mutsumi is just the eyes.”

この framing には 2 つの構造的な問題があります。

1. **コンポーネントを製品として売ってしまっている。** ユーザーが欲しいのは TUI ではありません。コンテキストを切り替えたときに物事を忘れないことです。TUI は実装ディテールにすぎません。
2. **機能競争に引き込まれてしまう。** 「Taskwarrior より優れている、なぜなら……」という語りは red-ocean な比較に持ち込みます。本当の物語は、Taskwarrior が扱っていない新しいカテゴリです。

### 1.2 見落としていた洞察

古いナラティブはターゲットユーザー——マルチスレッドな高並列個人——を正しく見つけていました。しかし痛みの診断を誤っていました。

古い診断: *「タスクマネージャーを呼び出す摩擦が高すぎる」*

本当の診断: **「人間の作業記憶にはだいたい 4 スロットしかない。そこに 12 本の thread を同時に走らせている。コンテキストを切り替えるたびに thread は追い出される。夜中の 2 時に噛みついてくるのは、その忘れられた thread だ。」**

ボトルネックは「Notion を開くのが遅い」ことではありません。脳が物理的に全アクティブ thread を同時保持できないことです。必要なのは外部 thread table —— 常に見えていて、一瞥コストがほぼゼロで、agents によって保守されるものです。

### 1.3 Focus vs. Thread-Keeping

これは**集中ツールではありません**。対象ユーザーにとって、「1 つのことを深くやる」時代はもう終わっています。

| Concept | Focus（专注） | Thread-Keeping（聚焦） |
|---|---|---|
| Philosophy | Single-thread. Block distractions. | Multi-thread. Embrace context switching. |
| Metaphor | Noise-canceling headphones | Air traffic control radar |
| User model | "You're distracted, discipline yourself" | "You're parallel, let me hold your threads" |
| Products | Forest, Pomodoro, Deep Work | **Mutsumi** |
| Failure mode | Guilt when you check your phone | Forgotten thread that derails a deadline |

Thread-keeping は multi-threading をユーザーの弱さではなく、強みとして受け入れます。止まれとは言いません。スタックから何も落ちないようにするのです。

---

## 2. 新しいナラティブ

### 2.1 ストーリー構造

ナラティブは 3 層構造を取ります。それぞれ異なる深さの受け手を対象にします。

```text
Layer 0: Emotional Story (README, Product Hunt, landing page)
  → ユーザーの脳に向けて話す。Pain → Relief → How。

Layer 1: Technical Story (Docs, Architecture)
  → 開発者に向けて話す。MVC。Agent Agnostic。Local Only。

Layer 2: Ecosystem Story (Integration guides, Roadmap)
  → workflow に向けて話す。Quake terminals。Raycast。Agent setup。
```

### 2.2 Layer 0 — Emotional Pitch

> あなたに必要なのは focus ではない。thread を失わないことだ。
>
> 現代の高並列な個人は、1 日に十数個のコンテキストを行き来する —— コードを書く、レビューする、メッセージを返す、agents を走らせる、フィードを眺める。それは欠点ではない。あなたの operating mode だ。
>
> 本当の問題は、やることが多すぎることではない。切り替えた瞬間に、さっきまでの thread が脳から薄れ始めることだ。1 時間後には、直すはずだった重要 bug が蒸発している。規律がないからではない。人間の working memory はせいぜい 4 個しか持てないのに、あなたは 12 本の thread を開いているからだ。
>
> Mutsumi は、あなたにスローダウンを求めない。ブラウザを閉じろとも言わない。「deep work」について説教もしない。
>
> 彼女がやることは 1 つだけだ。**あなたの全部の thread を、いつも余光の端に置いておくこと。**
>
> 1 日に 40 回コンテキストを切り替えても構わない。視線を戻すたびに、今抱えているもの、待っているもの、agents がすでに前に進めたものが正確に見える。
>
> ホットキー 1 つで summon。ホットキー 1 つで dismiss。軽すぎて存在を忘れる —— 必要になるまでは。
>
> **Never lose a thread.**

### 2.3 Layer 1 — Technical Pitch（旧ナラティブを保持）

既存の technical narrative は依然として有効で、十分に鋭いままです。

- **MVC Separation**: Mutsumi is View. `tasks.json` is Model. Your Agent is Controller.
- **Agent Agnostic**: JSON を書けるどんな program も正当な controller。
- **Local Only**: Zero network。データは files。
- **Hackable First**: TOML config、custom themes、custom keybindings。

変わるのは framing です。これはもはや「なぜ Mutsumi が良い TUI なのか」ではなく、「なぜ Mutsumi が thread-keeping workflow における正しい View layer なのか」を語るものになります。

### 2.4 Layer 2 — Ecosystem Pitch（新規）

Mutsumi は 1 コンポーネントにすぎません。完全な workflow には次が必要です。

| Layer | Component | Examples |
|---|---|---|
| **Summon** | Instant terminal invocation | Quake-mode terminal (macOS iTerm2 / Windows Terminal Quake / Linux guake), Raycast/Alfred/Spotlight integration, tmux popup |
| **View** | Visual thread table | **Mutsumi TUI** |
| **Control** | Task creation & management | AI Agents (Claude Code, Codex CLI, Gemini CLI), CLI (`mutsumi add`), scripts |
| **Model** | Persistent data | `tasks.json` (local, plain-text, Git-able) |
| **Notify** | Passive reverse-notify | `events.jsonl` tailing, OS notifications (future) |

ユーザーがセットアップするのは「Mutsumi」ではなく、次のような**workflow**です。

1. 1 つの hotkey で Mutsumi を動かしている dropdown terminal を summon する
2. agents が作業しながら task を書く
3. 一瞥で全 active threads がわかる
4. 1 つの hotkey で dismiss する

Mutsumi は View のギャップを埋める役割です。残りは ecosystem が提供します。

---

## 3. Brand Updates

### 3.1 Tagline

| Before | After |
|---|---|
| *The silent task brain for the multi-threaded you.* | **Never lose a thread.** |

### 3.2 Elevator Pitch

| Before | After |
|---|---|
| A minimal TUI task board that watches your JSON and stays out of your way. | Your threads, always in sight. A terminal task board that your AI agents write to and you glance at — summoned in a keystroke, gone in another. |

### 3.3 Personality（保持しつつ再 framing）

既存の personality traits（Quiet, Present, Humble, Hackable, Fast）はそのまま残します。追加されるのは 1 つです。

| Trait | Description |
|---|---|
| **Peripheral** | 彼女はあなたの視界の端に住んでいる。主役でもないし、隠れてもいない。ただそこにいる —— 壁の時計のように。 |

付箋のメタファーも維持します。

> あなたのそばで静かに、thread が書かれた付箋を持って座っている。あなたが一瞥すると、その紙を少し高く持ち上げる。目を離せば、ただ穏やかに待っている。

### 3.4 もう言わないこと

| Old language | 退役理由 |
|---|---|
| "task exo-brain" | 言い過ぎ。彼女は brain ではなく thread-keeper。 |
| "Let your AI agent be the brain — Mutsumi is just the eyes." | 否定形で Mutsumi を定義し、価値を過小評価してしまう。 |
| "stays out of your way" | 防御的な framing。彼女が**何ではないか**ではなく、**何であるか**を言うべき。 |
| "multi-threaded super-individuals" | "multi-threaded" は残し、"super-individuals" は落とす —— 気取りすぎている。 |

### 3.5 これから言うこと

| New language | 使う場面 |
|---|---|
| "thread"（"task" ではなく） | emotional / narrative context で。technical / API context では "task" を使う。 |
| "thread-keeper" | workflow における Mutsumi の役割を説明するとき。 |
| "summon / dismiss" | invocation pattern の説明に使う。"open/close" ではない。 |
| "glance" | interaction mode の説明に使う。"check" や "review" ではない。 |
| "peripheral vision" | workspace のどこに Mutsumi が住むかを説明するとき。 |

---

## 4. 既存ドキュメントへの影響

| Document | Action |
|---|---|
| `BRAND.md` | tagline と elevator pitch を更新し、Layer 0 narrative を追加 |
| `docs/site/index.mdx`（全 locale） | hero、feature cards、flow diagram を書き換える |
| `docs/site/what-is-mutsumi.mdx`（全 locale） | thread-loss problem を中心に書き換える |
| `README.md` | 今後 —— Phase 4 で Layer 0 narrative を使って書き換える |
| `RFC-001` | 変更なし —— technical architecture は変わらない |
| `ROADMAP.md` | 今後 —— post-launch で ecosystem integration の優先順位を調整 |

---

## 5. Decision

**Accepted.** この narrative reset はコード、アーキテクチャ、データコントラクトを一切変えません。変わるのは、すでに作ったものをどう語るかです。実装は documentation site と `BRAND.md` から始まります。
