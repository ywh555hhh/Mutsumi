# Mutsumi v1.0.0 Beta — 内部テスト Playbook

> **[English Version](./BETA_V1.md)** | **[中文版](./BETA_V1_cn.md)**

| Status | Draft — Internal Only |
|---|---|
| Date | 2026-03-23 |
| Version | `1.0.0b1` |
| Package | `mutsumi-tui` |
| CLI | `mutsumi` |

---

## この文書について

これは現在の **`1.0.0b1`** beta ライン向けの日本語テスト playbook です。

焦点は 2 つのコアモーメントです。

1. **Out-of-the-box startup** — install、launch、onboarding、即利用可能
2. **Agent live sync** — agent と会話し、task file を更新し、Mutsumi が refresh するのを見る

この文書は、製品を**今実際に存在する姿**として記述する必要があります。
calendar のような planned work は roadmap / RFC の内容であり、shipped beta surface として扱ってはいけません。

---

## 2 つの Aha Moments

| # | Name | Promise |
|---|---|---|
| Aha 1 | Out-of-the-Box | 1 回の install、短い onboarding、すぐに使える board |
| Aha 2 | Agent Live Sync | Agent が task を更新すると、Mutsumi がほぼ即時に refresh する |

---

# Aha 1: Out-of-the-Box

## 1.1 Prerequisites

| Requirement | How to check |
|---|---|
| macOS / Linux terminal | `uname` |
| Python 3.12+ | `python3 --version` |
| `uv` or `pip` | `uv --version` or `pip --version` |

Windows users は beta 中は WSL を優先してください。

## 1.2 Install

```bash
# Recommended
uv tool install mutsumi-tui

# Alternative
pip install mutsumi-tui

# Contributor path
uv tool install git+https://github.com/ywh555hhh/Mutsumi.git
```

### Validation checklist — install

| # | Step | Expected | Pass? |
|---|---|---|---|
| 1.2.1 | `mutsumi --version` を実行 | `mutsumi, version 1.0.0b1` が出る | [ ] |
| 1.2.2 | `mutsumi --help` を実行 | help text と subcommands が出る | [ ] |
| 1.2.3 | `uv` で install | その後 command が使える | [ ] |
| 1.2.4 | `pip` で install | その後 command が使える | [ ] |

## 1.3 First Launch — Onboarding

```bash
cd ~/some-project
mutsumi
```

初回起動であれば、Mutsumi は onboarding flow を表示するはずです。

### Expected defaults

- language: 変更しない限り English
- keybindings: **Arrows**
- theme: Monochrome Zen
- task file preference: `mutsumi.json`

### Validation checklist — onboarding

| # | Step | Expected | Pass? |
|---|---|---|---|
| 1.3.1 | 最初の `mutsumi` で onboarding 表示 | 失敗せず onboarding が出る | [ ] |
| 1.3.2 | Settings を調整できる | Language、keybindings、theme、workspace、agent | [ ] |
| 1.3.3 | `中文` を選んで続行 | UI labels が切り替わる | [ ] |
| 1.3.4 | `Nord` を選んで続行 | Theme が更新される | [ ] |
| 1.3.5 | `Vim` を選んで続行 | Vim bindings がその後有効 | [ ] |
| 1.3.6 | keybindings を変更しない | default preset は `arrows` | [ ] |
| 1.3.7 | `Claude Code` agent を選ぶ | Claude Code 用 skills が install される | [ ] |
| 1.3.8 | onboarding を skip | usable defaults で app が開く | [ ] |
| 1.3.9 | multi-source setup を選ぶ | Main tab と追加 source tabs が期待通り表示 | [ ] |
| 1.3.10 | 2 回目の起動 | full onboarding は繰り返されない | [ ] |

## 1.4 First Interaction — Empty or Fresh Board

onboarding 後、ユーザーはすぐに task を作れるべきです。

### Validation checklist — first interaction

| # | Step | Expected | Pass? |
|---|---|---|---|
| 1.4.1 | task が無い状態 | friendly message + new-task affordance | [ ] |
| 1.4.2 | `n` を押す | task form が開く | [ ] |
| 1.4.3 | new-task UI をクリック | task form が開く | [ ] |
| 1.4.4 | title を submit | task が即表示される | [ ] |
| 1.4.5 | checkbox を toggle | done/pending が切り替わる | [ ] |
| 1.4.6 | `?` を押す | help UI が表示される | [ ] |

## 1.5 Aha 1 summary

**Pass condition:** 初見の tester が、深い docs を読まなくても install、onboarding、最初の task 作成まで完了できること。

---

# Aha 2: Agent Live Sync

## 2.0 Split Terminal Setup

好きな split-terminal workflow を使って構いません。

### tmux

```bash
bash scripts/tmux-dev.sh
```

### Manual

```bash
tmux new-session -d -s dev
tmux split-window -h -p 35 "mutsumi"
tmux select-pane -t 0
tmux attach -t dev
```

### Other terminals

- iTerm2 split pane
- VS Code integrated terminal split
- Cursor integrated terminal split

## 2.1 Agent Setup

### Recommended: skills-first

```bash
mutsumi setup --agent claude-code
mutsumi setup --agent codex-cli
mutsumi setup --agent gemini-cli
mutsumi setup --agent opencode
```

### Optional: skills + project doc

```bash
mutsumi setup --agent claude-code --mode skills+project-doc
```

### Manual snippet

```bash
mutsumi setup --agent aider --mode snippet
mutsumi setup --agent custom --mode snippet
```

### Validation checklist — setup

| # | Step | Expected | Pass? |
|---|---|---|---|
| 2.1.1 | `mutsumi setup --agent claude-code` | skill files が正常に install される | [ ] |
| 2.1.2 | setup を 2 回実行 | repeat use に十分 idempotent | [ ] |
| 2.1.3 | `mutsumi setup` with no flags | supported agents と modes が表示される | [ ] |
| 2.1.4 | `--mode skills+project-doc` | project integration snippet も追加される | [ ] |
| 2.1.5 | `--mode snippet` | copyable instructions が出る | [ ] |

## 2.2 Core Loop — Talk → Write → See

### Scenario A: 気軽に 1 task 追加

```text
You: "帮我加个 todo，明天交周报"
```

Expected agent behavior:

- `./mutsumi.json` を優先する
- repo が legacy `tasks.json` を使っているならその file を使う
- task data を更新し、atomically write back する

Expected Mutsumi behavior:

- change を検知する
- board を refresh する
- restart なしで new task を表示する

### Scenario B: 複数 task を一括追加

```text
You: "把这三个 bug 都加进去：登录页白屏、支付超时、头像上传失败，都是 high priority"
```

Expected result: すべての task が update 後に現れる。

### Scenario C: Mark done

```text
You: "登录页白屏修好了，帮我标记完成"
```

Expected result: UI で task が done になる。

### Scenario D: Edit metadata

```text
You: "把支付超时的优先级降到 normal，加个 tag 叫 backend"
```

Expected result: updated priority と tags がすぐに表示される。

### Validation checklist — live sync

| # | Step | Expected | Pass? |
|---|---|---|---|
| 2.2.1 | Agent が 1 task 追加 | すばやく Mutsumi に表示 | [ ] |
| 2.2.2 | Agent が複数 task 追加 | すべて正しく表示 | [ ] |
| 2.2.3 | Agent が done にする | status が即時更新 | [ ] |
| 2.2.4 | Agent が priority 変更 | priority 表示が更新 | [ ] |
| 2.2.5 | Agent が tags 変更 | tags 表示が更新 | [ ] |
| 2.2.6 | Agent が subtask 追加 | parent の下に child が表示 | [ ] |
| 2.2.7 | Agent が invalid JSON を書く | error banner が出て app は生きる | [ ] |
| 2.2.8 | Agent が JSON を修正 | error が消えて task が戻る | [ ] |
| 2.2.9 | unknown fields preserved | custom metadata が後続 write でも残る | [ ] |

## 2.3 Reverse Direction — TUI → File → Agent

sync は双方向に感じられるべきです。

| # | Step | Expected | Pass? |
|---|---|---|---|
| 2.3.1 | TUI で task toggle | task file が正しく更新 | [ ] |
| 2.3.2 | TUI で task create | task file が正しく更新 | [ ] |
| 2.3.3 | TUI で task delete | task file が正しく更新 | [ ] |
| 2.3.4 | inline edit title | file が atomically update される | [ ] |

## 2.4 Aha 2 summary

**Pass condition:** tester が、Mutsumi を別の手作業ツールではなく、agent の live visual brain extension のように感じること。

---

# Pre-Release Checklist

現在の beta cut を進める前に、以下がすべて green であるべきです。

## Code Quality

| # | Item | Status |
|---|---|---|
| C1 | automated tests pass | [ ] |
| C2 | shared CSS に monochrome-only assumption がない | [ ] |
| C3 | major TUI strings が i18n を使う | [ ] |
| C4 | theme switching works | [ ] |
| C5 | i18n switching works | [ ] |
| C6 | keybinding switching works (`arrows` / `vim` / `emacs`) | [ ] |
| C7 | onboarding settings apply correctly | [ ] |
| C8 | Main dashboard works in multi-source mode | [ ] |
| C9 | file watching remains stable over longer sessions | [ ] |
| C10 | atomic writes prevent partial corruption | [ ] |

## Packaging

| # | Item | Status |
|---|---|---|
| P1 | `pyproject.toml` version is `1.0.0b1` | [ ] |
| P2 | `uv tool install mutsumi-tui` works | [ ] |
| P3 | `pip install mutsumi-tui` works | [ ] |
| P4 | `mutsumi` command is available after install | [ ] |
| P5 | sdist excludes unnecessary internal directories | [ ] |
| P6 | Python 3.12+ requirement is enforced | [ ] |

## Documentation

| # | Item | Status |
|---|---|---|
| D1 | この playbook が current beta を正確に反映 | [ ] |
| D2 | README が current product behavior と一致 | [ ] |
| D3 | AGENT.md が current file naming と setup modes と一致 | [ ] |
| D4 | specs が canonical `mutsumi.json` + legacy fallback と一致 | [ ] |
| D5 | RFC-009 が存在し、calendar が planned であって shipped ではない | [ ] |

## Platform Testing

| # | Platform | Tester | Pass? |
|---|---|---|---|
| T1 | macOS + iTerm2 | Wayne | [ ] |
| T2 | macOS + tmux |  | [ ] |
| T3 | Ubuntu + tmux |  | [ ] |
| T4 | Windows WSL |  | [ ] |
| T5 | VS Code integrated terminal |  | [ ] |
| T6 | Cursor integrated terminal |  | [ ] |

## Agent Compatibility

| # | Agent | Skill setup | Live sync | Pass? |
|---|---|---|---|---|
| A1 | Claude Code | [ ] | [ ] | [ ] |
| A2 | Codex CLI | [ ] | [ ] | [ ] |
| A3 | Gemini CLI | [ ] | [ ] | [ ] |
| A4 | OpenCode | [ ] | [ ] | [ ] |
| A5 | Manual / custom | N/A | [ ] | [ ] |

---

# Known Issues / Blockers

beta testing 中の blocker はここに記録します。

| # | Issue | Severity | Status |
|---|---|---|---|
| | | | |

---

# Beta Timeline

| Milestone | Owner | Status |
|---|---|---|
| Internal beta hardening for `1.0.0b1` | Wayne |  |
| Friend beta testing | Wayne |  |
| Bug-fix sprint | Wayne |  |
| Next beta / release candidate decision | Wayne |  |
| `1.0.0` GA release | Wayne |  |

---

# Important Scope Boundary

現在の beta line では:

- shipped now: multi-source hub、onboarding、skills-first setup、live file sync
- not shipped yet: built-in calendar view
- calendar status: **planned via RFC-009**

この区別は、すべての beta 向けコミュニケーションで明示されていなければなりません。

---

# Feedback Template

```markdown
## Environment
- OS:
- Terminal:
- Python version:
- Install method: uv / pip / source
- Agent (if testing Aha 2):

## Aha 1
- Install smoothness:
- Onboarding smoothness:
- First task created:
- Overall feeling (1-5):
- Issues:

## Aha 2
- Agent used:
- Split-pane method:
- Add task via agent:
- Hot-reload speed:
- Overall feeling (1-5):
- Issues:

## General
- Would you use this daily?
- What surprised you?
- What is still missing?
```
