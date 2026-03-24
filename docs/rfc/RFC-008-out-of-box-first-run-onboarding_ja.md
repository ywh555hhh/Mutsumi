# RFC-008: Out-of-Box First-Run Onboarding

> **[English Version](./RFC-008-out-of-box-first-run-onboarding.md)** | **[中文版](./RFC-008-out-of-box-first-run-onboarding_cn.md)**

| Field | Value |
|---|---|
| **RFC** | 008 |
| **Title** | Out-of-Box First-Run Onboarding |
| **Status** | Draft |
| **Author** | Wayne (ywh) |
| **Created** | 2026-03-22 |

---

## 1. Abstract

Mutsumi の現在の architecture は強力ですが、end-to-end の first-run flow はまだユーザーに見えすぎています。install して、init して、files を作って、project を登録して、agent を設定して、場合によっては split pane も用意して、やっと board を開ける —— という流れです。

これは Mutsumi の core promise と正反対です。**zero friction** ではありません。

本 RFC は、1 つの command を中心にした新しい onboarding model を提案します。

```bash
mutsumi
```

環境がすでに ready なら、Mutsumi はすぐ開くべきです。
ready でないなら、Mutsumi は**その場で自分自身を bootstrap**しなければなりません。つまり、短く高信号な onboarding flow によって、本当に意味のある少数の質問だけを行い、不足している files を自動作成し、そのまま usable state で起動するべきです。

ゴールは単純です。

> **ユーザーが「システムをデプロイした」のではなく、「ツールを開いた」と感じること。**

---

## 2. Problem Statement

### 2.1 Current Friction

現在、新規ユーザーは Mutsumi が useful になる前に、次のようなことを考えなければならない場合があります。

- これは personal task flow なのか project task flow なのか？
- `~/.mutsumi/config.toml` は存在するか？
- `~/.mutsumi/mutsumi.json` は存在するか？
- 現在の project に `mutsumi.json` はすでにあるか？
- この project は登録済みか？
- 現在の Agent は Mutsumi とどう連携するか知っているか？
- tmux/zellij scripts を使うべきか？
- `CLAUDE.md` / `AGENTS.md` / 類似ファイルを手動で編集すべきか？

個々のステップは合理的でも、組み合わせるとそうではありません。

### 2.2 Root Cause

問題は、Mutsumi に機能が足りないことではありません。

問題は、**setup がまだ可視の workflow のまま**であり、default behavior の中に圧縮されていないことです。

ユーザーが学びたいのは initialization graph ではありません。やりたいのは：

1. Mutsumi を開く
2. task を一瞥する
3. Agent が自然にそれとやり取りするのを許す

### 2.3 Product Principle

Mutsumi は **out-of-box usability** を最適化すべきです。

- 1 つの自然な entrypoint
- sane defaults
- progressive disclosure
- 侵襲的な action にだけ明示的な consent

---

## 3. Goals

| Goal | Description |
|---|---|
| **Single natural entrypoint** | `mutsumi` を開始のデフォルトにする。app が useful になる前に `init` を学ばせてはならない。 |
| **Launch must succeed** | `mutsumi` は直接 app を開くか、短い onboarding flow のあと app を開くかのどちらかであるべき。 |
| **Few decisions, high value** | first-run では、language、input preset、theme、workspace mode、agent integration のように、すぐの快適さに効く設定だけを尋ねる。 |
| **No tmux assumption** | terminal layout helpers はあくまで optional utilities であり、primary path の一部ではない。 |
| **Skills-first integration** | supported agents では、default integration path は core instruction files の編集ではなく skills/bridges を優先する。 |
| **Explicit consent for core file modification** | `CLAUDE.md`、`AGENTS.md`、`GEMINI.md` などへの書き込みは opt-in であり、暗黙であってはならない。 |
| **No repeated init tax** | 新しい repo ごとに full setup をやり直させない。後続の project attachment は lightweight であるべき。 |
| **Agent-agnostic architecture preserved** | Mutsumi は local-first / agent-agnostic のままである。onboarding は UX を改善するだけで、1 モデルや 1 terminal workflow に bind しない。 |

---

## 4. Non-goals

本 RFC は次を**提案しません**。

- tmux/zellij を primary onboarding path の一部にすること
- Mutsumi を Claude Code のみに結びつけること
- network calls、account login、remote services を必須にすること
- advanced settings を first-run に持ち込むこと
- user-owned な project instruction files を黙って書き換えること
- Mutsumi を workspace/process manager に変えること

Mutsumi は引き続き local task board と multi-source command center です。

---

## 5. UX Model

### 5.1 Three Startup States

`mutsumi` を実行すると、次の 3 パスのいずれかになるべきです。

#### A. Ready state

ユーザー環境がすでに ready なら、Mutsumi は即座に起動します。

条件の例：
- config が存在する
- personal file が存在する、または選択した mode では不要
- current project が既知、または無関係

#### B. First-ever launch bootstrap

事実上の first launch であれば、Mutsumi は main UI に入る前に**短い onboarding wizard**を開きます。

この wizard は不足 file を作成し、ユーザーの core preferences を保存します。

#### C. Soft project attachment prompt

ユーザーが onboarding をすでに完了していて、未登録の新しい repo の中で Mutsumi を起動した場合、full first-run wizard を再生してはいけません。

代わりに、次のような lightweight prompt を出します。

- Register current folder as a project
- Create `./mutsumi.json`
- Skip for now

これにより project onboarding は軽く、繰り返しの負担になりません。

---

### 5.2 First-run Wizard Structure

first-run 体験は**短く集中しているべき**です。

質問数が意図的に少なく、ユーザー影響順に並べられているので、wizard 形式は許容されます。本 RFC は、RFC-002 の巨大な単一 settings 画面より、短いステップフローを明確に好みます。

#### Step 1 — Language

最初のステップは language です。

選択肢：
- English
- 中文
- 日本語

デフォルト：
- system locale が一致すればそれ、なければ English

理由：
- 以後の onboarding text をすぐにユーザー言語へ切り替えるべきだから
- これはフロー全体で最も早く trust を生む決定だから

#### Step 2 — Input preset

選択肢：
- Arrows
- Vim
- Emacs

デフォルト：
- **Arrows**

理由：
- これは「デフォルト preset は普通のユーザー向けであるべき」という product rule に一致する
- ユーザーが app を開いてから uncomfortable な key model を知るべきではない

#### Step 3 — Theme

選択肢：
- Monochrome Zen
- Nord
- Dracula
- Solarized

デフォルト：
- **Monochrome Zen**

理由：
- theme は low-risk だが perceived value が高い
- complexity を増やさず first-run に personal 感を与える

#### Step 4 — Workspace mode

選択肢：
- Personal only
- Current project only
- Personal + current project

smart default：
- current directory が Git repo なら：**Personal + current project**
- そうでなければ：**Personal only**

理由：
- personal tasks と project tasks の混乱を減らすための最小限で意味ある決定
- Phase 5 の multi-source model に一致する

#### Step 5 — Agent integration

選択肢：
- Skip for now
- Register Mutsumi skills / bridge for current agent
- Register skills / bridge **and** append project integration instructions to agent core file

デフォルト：
- current agent が検出可能かつ supported なら：**skills / bridge のみ登録**
- それ以外：Skip for now

重要：
- `CLAUDE.md`、`AGENTS.md`、`GEMINI.md`、または同等ファイルの変更は独立した明示選択でなければならない
- skills/bridge registration と project core-file injection は同一 operation ではなく、混同してはいけない

---

### 5.3 Interaction Requirements

onboarding flow は Mutsumi の core interaction rules に従う必要があります。

すべての step は keyboard と mouse の両方で到達可能でなければなりません。

| Action | Keyboard | Mouse |
|---|---|---|
| options 間移動 | Arrow keys / Tab | option をクリック |
| selection 確定 | Enter / Space | button をクリック |
| 戻る | Escape / dedicated Back action | Back をクリック |
| 推奨 default を受け入れる | Enter | Continue をクリック |
| onboarding をキャンセル | Escape | Skip / Cancel をクリック |

### 5.4 Cancellation Behavior

onboarding をキャンセルしても `mutsumi` が失敗してはいけません。

ユーザーがキャンセルした場合：
- Mutsumi は current session 用の temporary defaults で起動する
- empty だが usable な UI を表示する
- あとで lightweight な “Finish setup” entry point を提示する

これにより、main command should always succeed という原則を守れます。

---

## 6. Automatically Created Files

ユーザーの選択に応じて、Mutsumi は次を作成する可能性があります。

```text
~/.mutsumi/
├── config.toml
└── mutsumi.json

<current-project>/
└── mutsumi.json
```

### 6.1 Always safe to create

次は Mutsumi-owned files であり、onboarding 中に自動作成してよいものです。

- `~/.mutsumi/config.toml`
- `~/.mutsumi/mutsumi.json`
- current project の `mutsumi.json`（その mode が必要な場合のみ）

### 6.2 Never auto-create without explicit consent

次は user/project-owned な instruction files であり、暗黙に変更してはいけません。

- `CLAUDE.md`
- `AGENTS.md`
- `GEMINI.md`
- `opencode.md`
- 同等の agent instruction files

---

## 7. Agent Integration Boundary

### 7.1 Preferred order of integration

Mutsumi は次の順序を優先すべきです。

1. **Mutsumi-owned bridge / skills registration**
2. **Printed snippet / copyable instructions**
3. **Project core-file injection**（明示的 opt-in のみ）

### 7.2 Why skills-first

skills/bridge registration が better default である理由：

- project file pollution を減らせる
- instruction files への surprise edits を避けられる
- 時間とともに進化しやすい
- project policy を書き換えるより、capability を有効にする感覚に近い

### 7.3 Why core-file injection stays optional

core instruction files は高信頼・高感度のファイルです。

ユーザーはすでにそこに慎重な project conventions を書いているかもしれません。onboarding が走っているからといって、Mutsumi が勝手に追記する権利を持つべきではありません。

したがって：

> **Mutsumi は project core-file injection を提案してよいが、決して default path にしてはならない。**

### 7.4 Supported integration modes

| Mode | Behavior |
|---|---|
| `none` | Agent integration を行わない |
| `skills` | supported current Agent に Mutsumi task capabilities を登録し、project instruction files は編集しない |
| `skills+project-doc` | skills/bridge を登録し、加えて適切な agent instruction file に project integration instructions を追記する |
| `snippet` | 自動 bridge registration が不可能なときに manual instructions を表示またはコピーする |

---

## 8. Smart Defaults

out-of-box 体験は configurability より defaults に強く依存します。

推奨 defaults：

| Setting | Default |
|---|---|
| Language | system locale（fallback English） |
| Key preset | `arrows` |
| Theme | `monochrome-zen` |
| Notifications | `quiet` |
| Default tab | `main` |
| Git repo 内での workspace mode | `personal + current project` |
| Git repo 外での workspace mode | `personal only` |
| Agent integration | supported なら `skills`、そうでなければ `none` |
| Core-file injection | `off` |

これらの defaults により、多くのユーザーは Enter を数回押すだけで完了できるはずです。

---

## 9. Command Behavior Changes

### 9.1 `mutsumi`

`mutsumi` は primary onboarding entrypoint になります。

挙動：
- readiness を検出する
- 必要なら first-run bootstrap を実行する
- 必要に応じて soft project attachment prompt を出す
- TUI を起動する

### 9.2 `mutsumi init`

`mutsumi init` は引き続き有用ですが、必須 prerequisite から explicit utility command へと位置づけが変わります。

意味の例：
- onboarding を強制再実行する
- flags で non-interactive に file を作成する
- setup を reset / repair する

### 9.3 `mutsumi setup --agent`

この command は明示的な post-install integration path として残ります。

onboarding から再利用可能でもあるべきですが、working system を得るための唯一の合理的 path ではなくなります。

---

## 10. Project Attachment Model

first-run wizard は最初の起動を解決します。しかし後で繰り返し setup tax を生み出してはいけません。

ユーザーが onboarding 完了後、未登録の Git repo 内で Mutsumi を起動した場合、Mutsumi は次のような compact prompt を表示すべきです。

```text
This folder looks like a project.
[ Register project ] [ Create local mutsumi.json ] [ Skip ]
```

ルール：
- これは lightweight prompt であり、full wizard ではない
- 明示的再トリガーがない限り、repo ごとに最大 1 回だけ表示
- personal tasks へのアクセスは絶対に妨げない

これにより “open instantly” の感覚を保ちながら multi-project model の採用を助けます。

---

## 11. Default Routing for Semantic Task Operations

この RFC 自体は skill protocol を定義しませんが、onboarding は将来の skills が使う routing rules を確立しておくべきです。

推奨 routing：

1. ユーザーが登録済み project 内にいるなら、semantic task actions はその project の `mutsumi.json` をデフォルト対象にする
2. project context 外なら、semantic task actions は personal tasks をデフォルト対象にする
3. 明示的な user targeting は常に defaults より優先される

例：
- `~/Code/saas-app` 内で “remember to fix refresh token” → project task
- どの project context にもいない状態で “tomorrow buy coffee beans” → personal task
- “add this to personal” → cwd に関係なく personal task

これらの defaults は mental overhead を減らし、後の skill-based interaction を自然に感じさせます。

---

## 12. Relationship to RFC-002

この RFC は RFC-002 で導入された onboarding 方向性を更新します。

### 12.1 Superseded ideas

RFC-002 のうち次の部分は superseded とみなされます。

- onboarding は主に `mutsumi init` 経由で行うべき、という前提
- 1 枚の大きな setup panel が最良の first-run UX だ、という前提
- agent setup は常に明確に分離された post-init action だ、という前提

### 12.2 Preserved ideas

次の考え方はそのまま有効です。

- zero-config は動くべき
- config は人間に読めて local であるべき
- onboarding は transparent で non-magical であるべき
- Mutsumi は local-first で hackable なままであるべき

要するに：

> RFC-002 は goal に関しては正しかった。
> この RFC は、その goal をよりうまく達成する interaction model に更新する。

---

## 13. Implementation Strategy

### 13.1 Likely code areas

| Area | Change |
|---|---|
| `mutsumi/cli/__init__.py` | app 起動前に startup readiness detection を追加 |
| `mutsumi/config/settings.py` | onboarding 関連 config fields を追加または整理 |
| `mutsumi/config/__init__.py` | 新しい defaults をきれいに load/save |
| `mutsumi/cli/setup.py` | skills/bridge registration と project core-file injection modes を分離 |
| `mutsumi/cli/project.py` | soft-attach prompt から project registration logic を再利用 |
| `mutsumi/core/paths.py` | lazy init 中に personal path helpers を再利用 |
| `mutsumi/tui/` | onboarding widgets と lightweight project-attach UI を追加 |

### 13.2 Minimal implementation phases

| Phase | Scope | Deliverable |
|---|---|---|
| **8a** | Readiness detection | `mutsumi` が first-run / attach-needed states を判定できる |
| **8b** | First-run wizard | Language、key preset、theme、workspace mode、agent integration |
| **8c** | Lazy file creation | config/personal/project task files の自動作成 |
| **8d** | Skills-first agent bridge | core files を編集しない default integration path |
| **8e** | Optional core-file injection | 明示 opt-in の project doc modification |
| **8f** | Soft project attach prompt | onboarding 後の lightweight repo registration |

---

## 14. Testing Strategy

### 14.1 First-run tests

- config なし・task files なしで起動 → wizard が出る
- wizard を完了 → 期待される files が作られ、app に入る
- wizard をキャンセル → temporary defaults で app に入る
- language choice によって onboarding copy が即座に切り替わる

### 14.2 Safety tests

- `skills` を選んでも `CLAUDE.md` / `AGENTS.md` は変更されない
- `skills+project-doc` を選ぶと期待する file だけが変更される
- 既存の project instruction files は repeated setup でも重複しない

### 14.3 Project attach tests

- onboarding 後に未登録 repo 内で起動 → full wizard ではなく soft prompt を表示
- Skip を選んでも app launch はブロックされない
- Register を選ぶと project entry と optional local `mutsumi.json` が作られる

### 14.4 Input parity tests

- onboarding は keyboard only で完全に使える
- onboarding は mouse only でも完全に使える
- 推奨 defaults は Enter 連打で素早く受け入れられる

---

## 15. Open Questions

1. theme step は live miniature preview を含むべきか、それとも name-only で十分か？
2. Mutsumi は agent-specific にならずに “current Agent” をどう検出するのが最善か？
3. onboarding をキャンセルしたとき、何も永続化しないべきか、そこまでの選択だけでも保存すべきか？
4. project attachment prompt に “この repo では二度と聞かない” option を持たせるべきか？
5. skill/bridge mechanism を持たない Agents に対して最良の fallback は何か？ snippet 表示、clipboard copy、あるいは explicit doc injection prompt か？

---

## 16. Conclusion

Mutsumi は、ユーザーにとって静かにそこにあるツールのように感じられるべきです。

install、initialization、project registration、Agent configuration がすべて別々の visible tasks のままだと、その感覚は壊れてしまいます。

この RFC は、それらをより単純なモデルへ圧縮します。

- `mutsumi` が唯一自然な entrypoint
- onboarding は短く humane
- 不足 files は自動作成
- skills/bridges は core project files の編集より優先
- tmux などの layout helpers は optional のまま
- 後続の project adoption は repetitive ではなく lightweight

得られるのは、よりよい setup flow だけではありません。

それは product 自体の、より良い表現でもあります。

> **Open instantly. Understand instantly. Use instantly.**
