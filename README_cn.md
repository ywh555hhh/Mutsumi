# mutsumi ♪

> **[English Version](./README.md)** | **[日本語版](./README_ja.md)**

**多线程的你，需要一个安静的任务大脑。**

一个极简的 TUI 任务看板，监听你的 `mutsumi.json`，并尽量不打扰你。对于旧项目，Mutsumi 仍会回退到 `tasks.json`。让 AI Agent 做大脑——Mutsumi 只做你的眼睛。

```
┌─────────────────────────────────────────────────────┐
│  [今天] [本周] [本月] [收件箱]            mutsumi ♪  │
├─────────────────────────────────────────────────────┤
│                                                     │
│  ▼ HIGH ─────────────────────────────────────────   │
│  [ ] 重构 Auth 模块                dev,backend ★★★  │
│  [x] 修复缓存穿透 Bug             bugfix      ★★★  │
│                                                     │
│  ▼ NORMAL ───────────────────────────────────────   │
│  [ ] 写周报                        life        ★★   │
│  [ ] Review PR #42                 dev         ★★   │
│    └─ [ ] 检查类型安全             (1/2)            │
│    └─ [x] 跑通测试                                  │
│                                                     │
│  ▼ LOW ──────────────────────────────────────────   │
│  [ ] 更新 README                   docs        ★    │
│                                                     │
├─────────────────────────────────────────────────────┤
│  6 个任务 · 2 已完成 · 4 待办                       │
└─────────────────────────────────────────────────────┘
```

## 为什么选 Mutsumi？

你在一个终端跑 Claude Code，另一个跑 Codex CLI，同时刷着 Reddit、在 Discord 聊天——全都一起发生。你需要一个任务看板，它应该：

- **1 秒内唤起** —— 无加载、无登录、无网络
- **当 AI Agent 写入 `mutsumi.json` 时自动刷新**
- **不干涉你** —— 不对工作流指手画脚，也不强行规定做事方式
- **适配任何 Agent** —— Claude Code、Codex CLI、Gemini CLI、Aider，或一个 shell 脚本

这就是 Mutsumi。她监听你的 JSON，瞬间重绘。仅此而已。

## 安装

```bash
# Beta 安装（从 git）
uv tool install git+https://github.com/ywh555hhh/Mutsumi.git
```

不需要预装 Python——`uv` 会处理好一切。

```bash
# 备选
pipx install mutsumi-tui

# 黑客路径
git clone https://github.com/ywh555hhh/Mutsumi.git
cd Mutsumi && uv sync && uv run mutsumi
```

## 快速开始

```bash
# 启动 TUI（优先使用 mutsumi.json，回退到 tasks.json）
mutsumi

# 交互式设置
mutsumi init

# 配置 Agent 集成
mutsumi setup --agent claude-code
```

## 工作原理

```
┌──────────────┐        ┌──────────────┐        ┌──────────────┐
│  AI Agent    │───────▶│ mutsumi.json │◀───────│  你 (TUI)    │
│  (Controller)│ 写入   │  (Model)     │ 监听   │  (View)      │
└──────────────┘        └──────────────┘        └──────────────┘
```

**MVC 分离**：Agent 写 JSON。Mutsumi 监听并渲染。你点击后它再写回。对于旧项目，`tasks.json` 仍作为兼容回退被支持。

## 特性

- **热重载**：文件变化会立即触发 TUI 重绘（100ms 防抖）
- **Arrows / Vim / Emacs 键位**：默认预设是 `arrows`；高级用户可以切换风格或自定义按键
- **4 套内置主题**：Monochrome Zen（默认）、Solarized、Nord、Dracula
- **多语言**：英文、中文、日文开箱即用
- **Agent 无关**：任何能写 JSON 的程序，都是合法 Controller
- **多源仪表盘**：Main + Personal + project 标签页与聚合进度
- **零网络**：100% 本地。无遥测，无云端。数据始终在你手里。
- **可 Hack**：TOML 配置、自定义主题、自定义键位——想改就改

## Agent 集成

你的 AI Agent 只需要读写 `mutsumi.json`。如果项目仍使用旧的 `tasks.json`，Mutsumi 也会自动识别。

```bash
# 一行命令：安装 + 配置 + 集成
uv tool install git+https://github.com/ywh555hhh/Mutsumi.git && mutsumi init && mutsumi setup --agent claude-code
```

支持的 Agent：Claude Code、Codex CLI、Gemini CLI、OpenCode、Aider，或任意自定义脚本。

详见 [Agent 协议](docs/specs/AGENT_PROTOCOL_cn.md)。也可查看 [AGENT_cn.md](AGENT_cn.md) 获取一页速查表。

## 终端集成

### tmux（推荐）

```bash
# 一条命令：左侧 shell + 右侧 Mutsumi 分屏
bash scripts/tmux-dev.sh

# 自定义 session 名称与宽度
MUTSUMI_WIDTH=40 bash scripts/tmux-dev.sh my-project
```

### iTerm2

1. `Cmd+D` 竖向分屏
2. 右侧 pane：`mutsumi`
3. 左侧 pane：你的 agent / shell

### Demo

```bash
# 在左侧 pane 运行 demo 脚本，查看实时刷新
bash scripts/demo.sh
```

## 文档

| 文档 | 说明 |
|---|---|
| [AGENT 速查](AGENT_cn.md) | 面向 Agent 的一页集成速查表 |
| [开发规则](CLAUDE_cn.md) | 项目开发约束与工作流 |
| [Beta 使用 SOP](docs/BETA_USAGE_cn.md) | 当前 `1.0.0b1` beta 的使用与测试流程 |
| [Beta 内测手册](docs/BETA_V1_cn.md) | beta 测试 playbook 与边界说明 |
| [RFC-001：核心架构](docs/rfc/RFC-001-mutsumi-core_cn.md) | 产品定义与架构 |
| [RFC-002：安装与引导](docs/rfc/RFC-002-installation-and-onboarding_cn.md) | 安装与 onboarding 体验 |
| [RFC-003：i18n 策略](docs/rfc/RFC-003-documentation-i18n_cn.md) | 文档国际化策略 |
| [RFC-004：三输入等价](docs/rfc/RFC-004-triple-input-parity_cn.md) | 键盘 / 鼠标 / CLI 等价原则 |
| [RFC-007：多源 Hub](docs/rfc/RFC-007-multi-source-hub_cn.md) | Main 仪表盘与多源架构 |
| [RFC-008：开箱 onboarding](docs/rfc/RFC-008-out-of-box-first-run-onboarding_cn.md) | 首次运行与 onboarding 设计 |
| [RFC-009：日历视图](docs/rfc/RFC-009-calendar-view_cn.md) | 计划中的内置日历架构 |
| [数据契约](docs/specs/DATA_CONTRACT_cn.md) | `mutsumi.json` schema 与兼容性规则 |
| [Agent 协议](docs/specs/AGENT_PROTOCOL_cn.md) | Agent 集成协议 |
| [TUI 规格](docs/specs/TUI_SPEC_cn.md) | TUI 交互规范 |
| [路线图](docs/ROADMAP_cn.md) | 开发路线图 |
| [品牌](docs/BRAND_cn.md) | 品牌识别 |

## 参与贡献

详见 [CONTRIBUTING_cn.md](CONTRIBUTING_cn.md)。

## 许可证

[MIT](LICENSE)

---

*mutsumi（若叶睦）—— “和睦，亲近”。她不告诉你该怎么做。她只是安静地在那里等你。*
