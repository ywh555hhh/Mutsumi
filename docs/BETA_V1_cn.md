# Mutsumi v1.0.0 Beta — 内测手册

> **[English Version](./BETA_V1.md)** | **[日本語版](./BETA_V1_ja.md)**

| 状态 | 草稿 — 仅内部使用 |
|---|---|
| 日期 | 2026-03-23 |
| 版本 | `1.0.0b1` |
| 包名 | `mutsumi-tui` |
| CLI | `mutsumi` |

---

## 这份文档是什么

这是当前 **`1.0.0b1`** beta 版本线的中文测试 playbook。

它聚焦两个核心时刻：

1. **开箱启动** —— 安装、启动、onboarding、立即可用
2. **Agent 实时同步** —— 和 agent 对话、更新任务文件、看着 Mutsumi 刷新

这份文档应描述产品**当前真实存在的状态**。
像 calendar 这样的计划项应被视为 roadmap / RFC 内容，而不是已 shipped 的 beta surface。

---

## 两个 Aha 时刻

| # | 名称 | 承诺 |
|---|---|---|
| Aha 1 | 开箱即用 | 一次安装、简短 onboarding、立刻可用的任务看板 |
| Aha 2 | Agent 实时同步 | Agent 更新任务后，Mutsumi 几乎立刻刷新 |

---

# Aha 1：开箱即用

## 1.1 前置条件

| 要求 | 如何检查 |
|---|---|
| macOS / Linux 终端 | `uname` |
| Python 3.12+ | `python3 --version` |
| `uv` 或 `pip` | `uv --version` 或 `pip --version` |

Windows 用户在本次 beta 阶段应优先使用 WSL。

## 1.2 安装

```bash
# 推荐
uv tool install mutsumi-tui

# 备选
pip install mutsumi-tui

# 贡献者路径
uv tool install git+https://github.com/ywh555hhh/Mutsumi.git
```

### 验证清单 —— 安装

| # | 步骤 | 预期 | 通过？ |
|---|---|---|---|
| 1.2.1 | 运行 `mutsumi --version` | 输出 `mutsumi, version 1.0.0b1` | [ ] |
| 1.2.2 | 运行 `mutsumi --help` | 显示帮助文本和子命令 | [ ] |
| 1.2.3 | 使用 `uv` 安装成功 | 安装后命令可用 | [ ] |
| 1.2.4 | 使用 `pip` 安装成功 | 安装后命令可用 | [ ] |

## 1.3 首次启动 —— Onboarding

```bash
cd ~/some-project
mutsumi
```

如果这是首次启动，Mutsumi 应显示 onboarding 流程。

### 预期默认值

- language：除非用户修改，否则为 English
- keybindings：**Arrows**
- theme：Monochrome Zen
- task file preference：`mutsumi.json`

### 验证清单 —— onboarding

| # | 步骤 | 预期 | 通过？ |
|---|---|---|---|
| 1.3.1 | 第一次运行 `mutsumi` | 显示 onboarding，而不是失败退出 | [ ] |
| 1.3.2 | 设置项可调整 | language、keybindings、theme、workspace、agent | [ ] |
| 1.3.3 | 选择 `中文` 后继续 | UI 标签切换为中文 | [ ] |
| 1.3.4 | 选择 `Nord` 后继续 | 主题更新为对应样式 | [ ] |
| 1.3.5 | 选择 `Vim` 后继续 | 进入后 Vim 键位生效 | [ ] |
| 1.3.6 | 不改键位设置 | 默认预设是 `arrows` | [ ] |
| 1.3.7 | 选择 `Claude Code` agent | 为 Claude Code 安装 skills | [ ] |
| 1.3.8 | 跳过 onboarding | 应用仍以可用默认值打开 | [ ] |
| 1.3.9 | 选择 multi-source setup | Main tab 与其他 source tabs 按预期出现 | [ ] |
| 1.3.10 | 第二次启动 | 不会重复完整 onboarding | [ ] |

## 1.4 首次交互 —— 空白或全新看板

onboarding 结束后，用户应当可以立刻创建任务。

### 验证清单 —— 首次交互

| # | 步骤 | 预期 | 通过？ |
|---|---|---|---|
| 1.4.1 | 没有任务时显示空状态 | 友好的提示 + 新建任务入口 | [ ] |
| 1.4.2 | 按 `n` | 打开任务表单 | [ ] |
| 1.4.3 | 点击新建任务 UI 入口 | 打开任务表单 | [ ] |
| 1.4.4 | 提交标题 | 任务立即出现在列表中 | [ ] |
| 1.4.5 | 切换复选框 | 任务在 done / pending 间切换 | [ ] |
| 1.4.6 | 按 `?` | 显示帮助界面 | [ ] |

## 1.5 Aha 1 总结

**通过条件：** 一个第一次接触 Mutsumi 的测试者，无需先阅读深度文档，就能完成安装、走完 onboarding，并创建自己的第一个任务。

---

# Aha 2：Agent 实时同步

## 2.0 分屏终端准备

使用你喜欢的任意分屏终端工作流即可。

### tmux

```bash
bash scripts/tmux-dev.sh
```

### 手动方式

```bash
tmux new-session -d -s dev
tmux split-window -h -p 35 "mutsumi"
tmux select-pane -t 0
tmux attach -t dev
```

### 其他终端

- iTerm2 split pane
- VS Code integrated terminal split
- Cursor integrated terminal split

## 2.1 Agent 设置

### 推荐：skills-first

```bash
mutsumi setup --agent claude-code
mutsumi setup --agent codex-cli
mutsumi setup --agent gemini-cli
mutsumi setup --agent opencode
```

### 可选：skills + project doc

```bash
mutsumi setup --agent claude-code --mode skills+project-doc
```

### 手动 snippet

```bash
mutsumi setup --agent aider --mode snippet
mutsumi setup --agent custom --mode snippet
```

### 验证清单 —— setup

| # | 步骤 | 预期 | 通过？ |
|---|---|---|---|
| 2.1.1 | `mutsumi setup --agent claude-code` | 成功安装 skill 文件 | [ ] |
| 2.1.2 | 重复运行 setup | 足够幂等，可重复使用 | [ ] |
| 2.1.3 | `mutsumi setup` 不带参数 | 列出支持的 agents 与 modes | [ ] |
| 2.1.4 | `--mode skills+project-doc` | 还会追加项目集成片段 | [ ] |
| 2.1.5 | `--mode snippet` | 打印可复制的说明文本 | [ ] |

## 2.2 核心循环 —— 说 → 写 → 看

### 场景 A：随手加一个任务

示例：

```text
你："帮我加个 todo，明天交周报"
```

预期的 agent 行为：

- 优先使用 `./mutsumi.json`
- 如果仓库仍使用旧的 `tasks.json`，则改那个文件
- 修改任务数据，并以原子方式写回

预期的 Mutsumi 行为：

- 检测到文件变化
- 刷新看板
- 无需重启就显示新任务

### 场景 B：批量添加多个任务

```text
你："把这三个 bug 都加进去：登录页白屏、支付超时、头像上传失败，都是 high priority"
```

预期结果：更新后所有任务都显示出来。

### 场景 C：标记完成

```text
你："登录页白屏修好了，帮我标记完成"
```

预期结果：UI 中该任务变为已完成。

### 场景 D：编辑元数据

```text
你："把支付超时的优先级降到 normal，加个 tag 叫 backend"
```

预期结果：优先级和标签更新后能及时显示。

### 验证清单 —— 实时同步

| # | 步骤 | 预期 | 通过？ |
|---|---|---|---|
| 2.2.1 | Agent 添加 1 个任务 | 很快出现在 Mutsumi 中 | [ ] |
| 2.2.2 | Agent 添加多个任务 | 全部正确显示 | [ ] |
| 2.2.3 | Agent 标记任务完成 | 状态立即更新 | [ ] |
| 2.2.4 | Agent 修改优先级 | 优先级显示更新 | [ ] |
| 2.2.5 | Agent 修改标签 | 标签显示正确更新 | [ ] |
| 2.2.6 | Agent 添加子任务 | 子任务显示在父任务下方 | [ ] |
| 2.2.7 | Agent 写入无效 JSON | 显示错误横幅，应用仍存活 | [ ] |
| 2.2.8 | Agent 修复 JSON | 错误消失，任务恢复显示 | [ ] |
| 2.2.9 | 未知字段被保留 | 自定义元数据在后续写入后仍存在 | [ ] |

## 2.3 反向方向 —— TUI → 文件 → Agent

同步体验应当是双向的。

| # | 步骤 | 预期 | 通过？ |
|---|---|---|---|
| 2.3.1 | 在 TUI 中切换任务状态 | 任务文件正确更新 | [ ] |
| 2.3.2 | 在 TUI 中创建任务 | 任务文件正确更新 | [ ] |
| 2.3.3 | 在 TUI 中删除任务 | 任务文件正确更新 | [ ] |
| 2.3.4 | 行内编辑任务标题 | 文件以原子方式更新 | [ ] |

## 2.4 Aha 2 总结

**通过条件：** 测试者会觉得 Mutsumi 像是 agent 的实时视觉脑扩展，而不是一个额外分离的手工工具。

---

# 预发布检查清单

在推进到当前 beta cut 之后，下面所有项目都应变绿。

## 代码质量

| # | 项目 | 状态 |
|---|---|---|
| C1 | 自动化测试通过 | [ ] |
| C2 | 共享 CSS 中没有硬编码的 monochrome-only 假设 | [ ] |
| C3 | 主要 TUI 文案使用 i18n | [ ] |
| C4 | 主题切换正常 | [ ] |
| C5 | i18n 切换正常 | [ ] |
| C6 | 键位切换正常（`arrows` / `vim` / `emacs`） | [ ] |
| C7 | Onboarding 设置正确生效 | [ ] |
| C8 | 多源模式下 Main dashboard 正常工作 | [ ] |
| C9 | 文件监听在较长会话中保持稳定 | [ ] |
| C10 | 原子写入避免部分损坏 | [ ] |

## 打包

| # | 项目 | 状态 |
|---|---|---|
| P1 | `pyproject.toml` 版本为 `1.0.0b1` | [ ] |
| P2 | `uv tool install mutsumi-tui` 正常 | [ ] |
| P3 | `pip install mutsumi-tui` 正常 | [ ] |
| P4 | 安装后 `mutsumi` 命令可用 | [ ] |
| P5 | sdist 排除了不必要的内部目录 | [ ] |
| P6 | 强制要求 Python 3.12+ | [ ] |

## 文档

| # | 项目 | 状态 |
|---|---|---|
| D1 | 本手册准确反映当前 beta | [ ] |
| D2 | README 与当前产品行为一致 | [ ] |
| D3 | AGENT.md 与当前文件命名和 setup modes 一致 | [ ] |
| D4 | specs 与 canonical `mutsumi.json` + legacy fallback 一致 | [ ] |
| D5 | RFC-009 已存在，且 calendar 被明确标为 planned 而非 shipped | [ ] |

## 平台测试

| # | 平台 | 测试者 | 通过？ |
|---|---|---|---|
| T1 | macOS + iTerm2 | Wayne | [ ] |
| T2 | macOS + tmux |  | [ ] |
| T3 | Ubuntu + tmux |  | [ ] |
| T4 | Windows WSL |  | [ ] |
| T5 | VS Code integrated terminal |  | [ ] |
| T6 | Cursor integrated terminal |  | [ ] |

## Agent 兼容性

| # | Agent | Skill setup | Live sync | 通过？ |
|---|---|---|---|---|
| A1 | Claude Code | [ ] | [ ] | [ ] |
| A2 | Codex CLI | [ ] | [ ] | [ ] |
| A3 | Gemini CLI | [ ] | [ ] | [ ] |
| A4 | OpenCode | [ ] | [ ] | [ ] |
| A5 | Manual / custom | N/A | [ ] | [ ] |

---

# 已知问题 / 阻塞项

在 beta 测试期间，把阻塞项记录在这里。

| # | 问题 | 严重性 | 状态 |
|---|---|---|---|
| | | | |

---

# Beta 时间线

| 里程碑 | Owner | 状态 |
|---|---|---|
| `1.0.0b1` 的内部 beta 加固 | Wayne |  |
| 朋友内测 | Wayne |  |
| Bug 修复冲刺 | Wayne |  |
| 下一轮 beta / release candidate 决策 | Wayne |  |
| `1.0.0` GA 发布 | Wayne |  |

---

# 重要范围边界

对于当前 beta 版本线：

- 当前已 shipped：multi-source hub、onboarding、skills-first setup、实时文件同步
- 尚未 shipped：内置 calendar view
- calendar 状态：**通过 RFC-009 规划中**

这个区分在所有面向 beta 的沟通中都应保持明确。

---

# 反馈模板

```markdown
## 环境
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
