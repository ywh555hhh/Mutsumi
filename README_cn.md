# mutsumi ♪

> **[English Version](./README.md)** | **[日本語版](./README_ja.md)**

**多线程的你，需要一个安静的任务大脑。**

一个极简的 TUI 任务看板，监听你的 `tasks.json`，从不打扰你。让 AI Agent 做大脑——Mutsumi 只做你的眼睛。

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

你在一个终端跑 Claude Code，另一个跑 Codex CLI，同时刷着 Reddit、在 Discord 聊天。你需要一个任务看板：

- **不到 1 秒唤起** — 无加载、无登录、无网络
- **Agent 写入 `tasks.json` 后自动刷新**
- **不干涉你** — 没有预设工作流，没有「该怎么管理」的说教
- **适配任何 Agent** — Claude Code、Codex CLI、Gemini CLI、Aider，或一个 shell 脚本

这就是 Mutsumi。她监听你的 JSON，瞬间渲染。仅此而已。

## 安装

```bash
uv tool install mutsumi
```

不需要预装 Python——`uv` 自动搞定一切。

```bash
# 备选
pipx install mutsumi

# 极客模式
git clone https://github.com/ywh555hhh/Mutsumi.git
cd Mutsumi && uv sync && uv run mutsumi
```

## 快速开始

```bash
# 启动 TUI（监听当前目录的 tasks.json）
mutsumi

# 交互式设置（一屏展示所有选项）
mutsumi init

# 配置 Agent 集成
mutsumi setup --agent claude-code
```

## 工作原理

```
┌──────────────┐        ┌────────────┐        ┌──────────────┐
│  AI Agent    │───────▶│ tasks.json │◀───────│  你 (TUI)    │
│  (Controller)│ 写入   │  (Model)   │ 监听   │  (View)      │
└──────────────┘        └────────────┘        └──────────────┘
```

**MVC 分离**：Agent 写 JSON。Mutsumi 监听并渲染。你点击操作后写回文件。简单。

## 特性

- **热重载**：文件变化即时刷新 TUI（100ms 防抖）
- **Vim/Emacs/Arrow 键位**：选你习惯的，或自定义
- **4 套内置主题**：Monochrome Zen（默认）、Solarized、Nord、Dracula
- **三语言**：英文、中文、日文开箱即用
- **Agent 无关**：任何能写 JSON 的程序都是合法的 Controller
- **零网络**：100% 本地，无遥测，无云端，数据永远在你手里
- **可 Hack**：TOML 配置、自定义主题、自定义键位——随便改

## Agent 集成

你的 AI Agent 只需要读写 `tasks.json`：

```bash
# 一行命令：安装 + 配置 + 集成
uv tool install mutsumi && mutsumi init --defaults && mutsumi setup --agent claude-code
```

支持的 Agent：Claude Code、Codex CLI、Gemini CLI、OpenCode、Aider，或任何自定义脚本。

详见 [Agent 集成协议](docs/specs/AGENT_PROTOCOL_cn.md)。

## 文档

| 文档 | 说明 |
|---|---|
| [RFC-001：核心架构](docs/rfc/RFC-001-mutsumi-core_cn.md) | 产品定义与架构 |
| [RFC-002：安装体验](docs/rfc/RFC-002-installation-and-onboarding_cn.md) | 安装与引导体验 |
| [RFC-003：国际化策略](docs/rfc/RFC-003-documentation-i18n_cn.md) | 文档国际化策略 |
| [数据契约](docs/specs/DATA_CONTRACT_cn.md) | `tasks.json` Schema 规范 |
| [Agent 协议](docs/specs/AGENT_PROTOCOL_cn.md) | Agent 集成协议 |
| [TUI 规格](docs/specs/TUI_SPEC_cn.md) | TUI 交互规范 |
| [路线图](docs/ROADMAP_cn.md) | 开发路线图 |
| [品牌](docs/BRAND_cn.md) | 品牌标识 |

## 参与贡献

详见 [CONTRIBUTING_cn.md](CONTRIBUTING_cn.md)。

## 许可证

[MIT](LICENSE)

---

*mutsumi（若叶睦）—— "和睦，亲近"。她不告诉你该怎么做，只是安静地在那里等你。*
