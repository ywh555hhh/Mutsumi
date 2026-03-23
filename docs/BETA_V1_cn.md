# Mutsumi v1.0.0 Beta — 内测手册

> **[English Version](./BETA_V1.md)**

| 状态    | 草稿 — 仅内部使用 |
|---------|-------------------|
| 日期    | 2026-03-23        |
| 版本    | 1.0.0-beta.1      |
| 包名    | `mutsumi-tui` (PyPI) |
| 命令行  | `mutsumi`         |

---

## 这是什么文档

这是 Mutsumi v1.0.0 beta 的**内测手册**。它定义了两个「爽点」（aha moment），在公开发布之前必须完美落地。每个爽点都有精确的验证清单 — 每一步都必须通过，没有例外。

内测人员应**从上到下**按照本文档引导完成体验。任何步骤失败，立即提 issue。

---

## 两个爽点

| # | 名称 | 一句话描述 | 时间预算 |
|---|------|-----------|----------|
| **Aha 1** | 开箱即用 | 一条命令安装，3 秒 onboarding，直接进入。 | < 60 秒 |
| **Aha 2** | Agent 实时同步 | 随口跟 Agent 说句话，Mutsumi 实时更新。 | < 30 秒 |

如果测试者完成两个爽点后说「就这？」（褒义）— 我们就成功了。

---

# Aha 1：开箱即用

**承诺**：从零到一个完全可用的任务看板，60 秒内搞定。不用写配置文件，不用 YAML，不用走 setup wizard 地狱。一条命令，一个屏幕，完事。

## 1.1 前置条件

| 要求 | 检查方式 |
|------|---------|
| macOS / Linux 终端 | `uname` |
| Python 3.12+ | `python3 --version` |
| `uv` 或 `pip` | `uv --version` 或 `pip --version` |

Windows 用户：请使用 WSL 或 PowerShell（原生 Windows 支持但不是本次 beta 的主要测试目标）。

## 1.2 安装 — 一条命令

```bash
# 方式 A：uv（推荐 — 快速、隔离）
uv tool install mutsumi-tui

# 方式 B：pip
pip install mutsumi-tui

# 方式 C：从源码（贡献者用）
uv tool install git+https://github.com/ywh555hhh/Mutsumi.git
```

### 验证清单 — 安装

| # | 步骤 | 预期结果 | 通过？ |
|---|------|---------|--------|
| 1.2.1 | 运行 `mutsumi --version` | 输出 `mutsumi, version 1.0.0b1` | [ ] |
| 1.2.2 | 运行 `mutsumi --help` | 显示帮助文本和子命令 | [ ] |
| 1.2.3 | 安装耗时 | < 15 秒 (uv) / < 30 秒 (pip) | [ ] |
| 1.2.4 | 无编译步骤 | 纯 Python，无需构建 C 扩展 | [ ] |

## 1.3 首次启动 — Onboarding

```bash
cd ~/some-project   # 或任意目录
mutsumi
```

因为是首次启动，Mutsumi 会显示一个**单页 onboarding 界面**。

### 你应该看到

```
┌─────────────────────────────────────────────────────────┐
│               Welcome to Mutsumi                        │
│      Your silent task board is ready to set up.          │
│                                                         │
│  Language       ● English  ○ 中文  ○ 日本語             │
│                                                         │
│  Keybindings    ● Arrows  ○ Vim  ○ Emacs                │
│                                                         │
│  Theme          ● Monochrome Zen  ○ Nord  ○ Dracula     │
│                 ○ Solarized                              │
│                                                         │
│  Workspace      ○ Personal only  ○ Project only         │
│                 ● Personal + Project                     │
│                                                         │
│  Agent          ○ Claude Code  ○ Codex CLI               │
│                 ○ Gemini CLI   ○ OpenCode  ● Skip        │
│                                                         │
│           [Start Mutsumi]           [Skip]               │
└─────────────────────────────────────────────────────────┘
```

### 验证清单 — Onboarding

| # | 步骤 | 预期结果 | 通过？ |
|---|------|---------|--------|
| 1.3.1 | 首次 `mutsumi` 显示 onboarding | 单页表单，不是多步向导 | [ ] |
| 1.3.2 | 5 个设置项全部可见 | 语言、快捷键、主题、工作区、Agent | [ ] |
| 1.3.3 | 方向键在 RadioButton 间导航 | 不崩溃，焦点移动流畅 | [ ] |
| 1.3.4 | 选择「中文」→ 点击「Start Mutsumi」 | UI 立即显示中文标签 | [ ] |
| 1.3.5 | 选择「Nord」主题 → 点击 Start | 颜色立即变化（蓝调 Nord 配色） | [ ] |
| 1.3.6 | 选择「Vim」快捷键 → Start | 进入 TUI 后 `j`/`k` 可用于导航 | [ ] |
| 1.3.7 | 选择「Claude Code」Agent → Start | Skill 文件创建在 `~/.claude/skills/mutsumi-*/SKILL.md` | [ ] |
| 1.3.8 | 点击「Skip」按钮 | 以默认设置进入 TUI，不崩溃 | [ ] |
| 1.3.9 | Onboarding 后 Main tab 可见 | 多源标签页：`[★ Main] [Personal] ...` | [ ] |
| 1.3.10 | 第二次启动跳过 onboarding | 直接进入 TUI | [ ] |
| 1.3.11 | 从命令到 TUI 总耗时 | < 5 秒（含 onboarding 交互） | [ ] |

## 1.4 首次交互 — 空看板

Onboarding 完成后，你进入主任务看板。它是空的 — 没关系。

### 验证清单 — 空状态

| # | 步骤 | 预期结果 | 通过？ |
|---|------|---------|--------|
| 1.4.1 | 空状态显示友好提示 | 「Nothing here yet」+ `[+ New Task]` 按钮 | [ ] |
| 1.4.2 | 点击 `[+ New Task]` 按钮 | 打开任务创建表单 | [ ] |
| 1.4.3 | 输入标题 → 点击 Create | 任务立即出现在列表中 | [ ] |
| 1.4.4 | 按 `n`（或方向键预设的对应键） | 通过键盘打开任务创建表单 | [ ] |
| 1.4.5 | 点击任务复选框 | 任务切换为已完成 | [ ] |
| 1.4.6 | 按 `?` | 帮助界面显示所有快捷键 | [ ] |

## 1.5 Aha 1 — 通过标准

**通过条件**：一个对 Mutsumi 一无所知的测试者，从 `uv tool install mutsumi-tui` 到在屏幕上看到自己创建的第一个任务，全程不超过 60 秒，不需要阅读任何文档。

---

# Aha 2：Agent 实时同步

**承诺**：你用自然语言跟 AI Agent 说话。Agent 写 JSON。Mutsumi 热重载。你还没读完 Agent 的回复，任务看板就已经更新了。

## 2.0 准备 — 分屏终端

你需要左右两个窗格：

```
┌──────────────────────────┬──────────────────────────┐
│                          │                          │
│   AI Agent               │   Mutsumi TUI            │
│   (Claude Code 等)       │                          │
│                          │                          │
└──────────────────────────┴──────────────────────────┘
```

### 快速配置

```bash
# tmux（推荐）
tmux new-session -d -s dev
tmux split-window -h -p 35 "mutsumi"
tmux select-pane -t 0
tmux attach -t dev

# iTerm2
# Cmd+D 分屏 → 右边窗格：mutsumi → 左边窗格：你的 agent

# VS Code / Cursor
# 拆分终端 → 右边：mutsumi → 左边：agent
```

## 2.1 Agent 认识 Mutsumi — Skill 注入

Agent 需要知道 Mutsumi 的 JSON 协议。如果用户在 onboarding 中选择了 agent，这会自动完成；也可以手动注入：

```bash
# 自动注入（将 SKILL.md 写入 agent 的 skill 目录）
mutsumi setup --agent claude-code
mutsumi setup --agent codex-cli
mutsumi setup --agent gemini-cli
mutsumi setup --agent opencode

# 检查是否生效
ls ~/.claude/skills/mutsumi-*/SKILL.md    # Claude Code
ls ~/.codex/skills/mutsumi-*/SKILL.md     # Codex CLI
```

### 验证清单 — Skill 注入

| # | 步骤 | 预期结果 | 通过？ |
|---|------|---------|--------|
| 2.1.1 | `mutsumi setup --agent claude-code` | 输出成功信息，创建 skill 文件 | [ ] |
| 2.1.2 | Agent 会话读取 skill | Agent 无需提示即知道 `mutsumi.json` 的 schema | [ ] |
| 2.1.3 | 重复运行 setup | 幂等，不产生重复文件 | [ ] |
| 2.1.4 | `mutsumi setup`（不带参数） | 列出可用的 agent | [ ] |

## 2.2 核心循环 — 说 → 写 → 看

这是最关键的体验。测试者应该在这里感受到魔法。

### 场景 A：随口加个任务

```
你（对 agent 说）："帮我加个 todo，明天交周报"
```

Agent 应该：
1. 读取 `mutsumi.json`（或通过 skill 知道 schema）
2. 添加一个新任务：标题「明天交周报」，scope「day」，合理的优先级
3. 原子写回文件

Mutsumi 应该：
- 通过 watchdog 检测到文件变化（< 200ms）
- 重新渲染任务列表
- 新任务无闪烁、无重启地出现

### 场景 B：批量操作

```
你（对 agent 说）："把这三个 bug 都加进去：登录页白屏、支付超时、头像上传失败，都是 high priority"
```

Agent 一次写入 3 个任务。Mutsumi 单次重渲染后全部显示。

### 场景 C：标记完成

```
你（对 agent 说）："登录页白屏修好了，帮我标记完成"
```

Agent 设置 `status: "done"`。Mutsumi 显示复选框勾选、任务变灰。

### 场景 D：编辑和重组

```
你（对 agent 说）："把支付超时的优先级降到 normal，加个 tag 叫 backend"
```

Agent 更新字段。Mutsumi 重渲染，显示新的优先级星星和标签。

### 验证清单 — 实时同步

| # | 步骤 | 预期结果 | 通过？ |
|---|------|---------|--------|
| 2.2.1 | Agent 添加 1 个任务 | 1 秒内出现在 Mutsumi 中 | [ ] |
| 2.2.2 | Agent 一次添加 3 个任务 | 单次重渲染后全部出现 | [ ] |
| 2.2.3 | Agent 标记任务完成 | 复选框 + 删除线立即更新 | [ ] |
| 2.2.4 | Agent 修改优先级 | 优先级星星立即变化 | [ ] |
| 2.2.5 | Agent 修改标签 | 标签列立即更新 | [ ] |
| 2.2.6 | Agent 添加子任务 (children) | 缩进的子任务出现在父任务下方 | [ ] |
| 2.2.7 | Agent 删除一个任务 | 任务从列表消失 | [ ] |
| 2.2.8 | Agent 写入无效 JSON | Mutsumi 显示错误横幅，不崩溃 | [ ] |
| 2.2.9 | Agent 修复回有效 JSON | 错误横幅消失，任务重新出现 | [ ] |
| 2.2.10 | 任何更新过程无闪烁 | 光标位置保持，无全屏闪烁 | [ ] |
| 2.2.11 | 未知字段保留 | Agent 添加 `"effort": "2h"` → Mutsumi 下次写入时保留 | [ ] |

## 2.3 反向同步 — TUI → JSON → Agent

同步是双向的。用户在 Mutsumi 中操作时，JSON 会更新，Agent 可以读取最新状态。

| # | 步骤 | 预期结果 | 通过？ |
|---|------|---------|--------|
| 2.3.1 | 在 TUI 中切换完成状态 | `mutsumi.json` 更新，Agent 可以看到变化 | [ ] |
| 2.3.2 | 在 TUI 中创建任务（按 `n`） | 新任务写入 JSON，Agent 可以读取 | [ ] |
| 2.3.3 | 在 TUI 中删除任务 | 任务从 JSON 中移除 | [ ] |
| 2.3.4 | 在 TUI 中内联编辑任务标题 | JSON 原子更新 | [ ] |

## 2.4 Aha 2 — 通过标准

**通过条件**：测试者在分屏终端中随口对 Agent 说「加几个 todo」，Mutsumi 在 Agent 还没打完回复时任务就已经出现在屏幕上。测试者的反应：「哦这也太爽了吧」。

---

# 发布前检查清单

以下所有项目必须全部通过，才能打 `v1.0.0-beta.1` 标签。

## 代码质量

| # | 项目 | 状态 |
|---|------|------|
| C1 | 所有测试通过 (`pytest tests/ -v`) | [ ] |
| C2 | DEFAULT_CSS 中无硬编码的 monochrome-zen 颜色 | [ ] |
| C3 | 所有主要 TUI 字符串使用 i18n (`get_i18n().t()`) | [ ] |
| C4 | 主题切换正常（onboarding + 配置修改） | [ ] |
| C5 | i18n 切换正常（en → zh → ja） | [ ] |
| C6 | 快捷键切换正常（arrows / vim / emacs） | [ ] |
| C7 | Onboarding 热重载：所有设置立即生效 | [ ] |
| C8 | 首次 onboarding 后 Main tab 可见 | [ ] |
| C9 | 文件监听器：运行 10 分钟以上稳定 | [ ] |
| C10 | 原子写入：无 JSON 部分损坏 | [ ] |

## 打包

| # | 项目 | 状态 |
|---|------|------|
| P1 | `pyproject.toml` version = `1.0.0b1` | [ ] |
| P2 | `uv tool install mutsumi-tui` 从 PyPI 安装正常 | [ ] |
| P3 | `pip install mutsumi-tui` 安装正常 | [ ] |
| P4 | 安装后 `mutsumi` 命令可用 | [ ] |
| P5 | sdist 中不包含多余文件（docs/, tests/, .claude/） | [ ] |
| P6 | Python 3.12+ 版本要求已强制 | [ ] |

## 文档

| # | 项目 | 状态 |
|---|------|------|
| D1 | 本手册 (BETA_V1_cn.md) — 完成 | [ ] |
| D2 | 英文版 (BETA_V1.md) — 完成 | [ ] |
| D3 | README.md — 已更新至 v1.0.0 | [ ] |
| D4 | AGENT.md — 已更新 JSON schema (mutsumi.json) | [ ] |
| D5 | CHANGELOG.md — v1.0.0-beta.1 条目 | [ ] |

## 平台测试

| # | 平台 | 测试者 | 通过？ |
|---|------|--------|--------|
| T1 | macOS + iTerm2 | Wayne | [ ] |
| T2 | macOS + tmux | | [ ] |
| T3 | Ubuntu + tmux | | [ ] |
| T4 | Windows WSL | | [ ] |
| T5 | VS Code 内置终端 | | [ ] |
| T6 | Cursor 内置终端 | | [ ] |

## Agent 兼容性

| # | Agent | Skill 注入 | 实时同步 | 通过？ |
|---|-------|-----------|---------|--------|
| A1 | Claude Code | [ ] | [ ] | [ ] |
| A2 | Codex CLI | [ ] | [ ] | [ ] |
| A3 | Gemini CLI | [ ] | [ ] | [ ] |
| A4 | OpenCode | [ ] | [ ] | [ ] |
| A5 | 手动（无 skill） | N/A | [ ] | [ ] |

---

# 已知问题 / 阻塞项

在 beta 测试期间在此追踪阻塞项。GA 前必须全部解决。

| # | 问题 | 严重程度 | 状态 |
|---|------|---------|------|
| | | | |

---

# Beta 时间线

| 里程碑 | 目标日期 | 负责人 |
|--------|---------|--------|
| 代码冻结（所有功能完成） | | Wayne |
| 内部试用（Wayne 独自） | | Wayne |
| v1.0.0-beta.1 标签 + PyPI 发布 | | Wayne |
| 朋友内测（3-5 人） | | Wayne |
| Bug 修复冲刺 | | Wayne |
| v1.0.0 正式发布 | | Wayne |

---

# 反馈模板

内测人员：报告时请复制此模板。

```markdown
## 环境
- 操作系统：
- 终端：
- Python 版本：
- 安装方式：uv / pip / 源码
- Agent（如果测试 Aha 2）：

## Aha 1（开箱即用）
- 安装耗时：
- Onboarding：顺畅 / 有问题
- 第一个任务创建成功：是 / 否
- 整体感受（1-5）：
- 问题：

## Aha 2（Agent 实时同步）
- 使用的 Agent：
- 分屏方式：tmux / iTerm2 / VS Code / 其他
- 通过 Agent 添加任务：成功 / 失败
- 热重载速度：即时 / 有明显延迟 / 不工作
- 整体感受（1-5）：
- 问题：

## 总体
- 你会每天使用吗？会 / 可能 / 不会
- 什么让你惊喜（好的或坏的）？
- 缺少什么？
```

---

*mutsumi — 「睦」，和睦、亲近。她不会告诉你该做什么。她只是静静地等待，在你准备好的时候更新。*
