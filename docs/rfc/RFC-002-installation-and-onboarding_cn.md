# RFC-002：安装、配置与入门体验

> **[English Version](./RFC-002-installation-and-onboarding.md)** | **[日本語版](./RFC-002-installation-and-onboarding_ja.md)**

| 字段     | 值                                                           |
|----------|--------------------------------------------------------------|
| **RFC**  | 002                                                          |
| **标题** | 安装、配置与入门体验                                          |
| **状态** | 草案                                                         |
| **作者** | Wayne (ywh)                                                  |
| **创建** | 2026-03-21                                                   |

---

## 1. 摘要

本 RFC 定义用户如何安装、配置和开始使用 Mutsumi。核心原则是**"脆爽"** — 每一步都要零摩擦：一条命令安装，一个屏幕配置，一秒钟启动。

## 2. 设计目标

| 目标 | 描述 |
|---|---|
| **零配置可用** | 无参数、无配置文件直接运行 — 直接能用 |
| **一屏式配置** | 不是一步步的向导。一个屏幕，所有选项，点击切换 |
| **Agent 自动安装** | Agent 跑一条命令，Mutsumi 就绑定好了 |
| **开箱即可定制** | 配置是 TOML，人类可读，可以 Git 管理 |
| **卸载干净** | 一条命令卸载干净，零残留 |

## 3. 安装方式

### 3.1 首选：`uv`

```bash
uv tool install mutsumi
```

- 无需预装 Python — `uv` 自动管理独立的 Python 环境。

安装后，`mutsumi` 作为全局 CLI 命令可用。

### 3.2 备选：`pipx`

```bash
pipx install mutsumi
```

面向偏好 `pipx` 的用户，同样的隔离环境行为。

### 3.3 手动安装：git clone

```bash
git clone https://github.com/<user>/mutsumi.git
cd mutsumi
uv sync
uv run mutsumi
```

面向想要修改源码的贡献者和极客。

### 3.4 脚本一行式安装

```bash
curl -fsSL https://mutsumi.dev/install.sh | sh
```

安装脚本执行逻辑：

1. 检测 `uv` 是否已安装，未安装则先装 `uv`
2. 执行 `uv tool install mutsumi`
3. 打印欢迎信息和下一步提示

## 4. 首次运行体验

### 4.1 零配置启动

```bash
mutsumi
```

无配置文件且无 `tasks.json` 时，Mutsumi：

1. 以全部默认值启动（英文、极简主题、vim 键位、静默通知）
2. 显示友好的空白状态提示
3. 询问是否在当前目录创建 `tasks.json`

```
┌──────────────────────────────────────────────┐
│  [Today] [Week] [Month] [Inbox]    mutsumi   │
├──────────────────────────────────────────────┤
│                                              │
│         Welcome to Mutsumi.                  │
│                                              │
│    No tasks.json found in this directory.     │
│                                              │
│    [Create tasks.json here]                  │
│    [Open setup]   [Browse files...]          │
│                                              │
└──────────────────────────────────────────────┘
```

### 4.2 交互式配置：`mutsumi init`

**这是"脆爽"体验的核心。**

`mutsumi init` 启动一个**单屏 TUI 设置面板**。所有选项一次性展示。没有多步向导，没有"下一步"按钮。直接点击/Tab 切换并选择。

#### 4.2.1 设置面板线框图

```
┌──────────────────────── mutsumi setup ─────────────────────────┐
│                                                                 │
│  ┌─ 基础设置 ─────────────────────────────────────────────┐    │
│  │                                                         │    │
│  │  语言                  (English)  中文                   │    │
│  │  主题                  ● 极简     ○ Catppuccin          │    │
│  │                        ○ Nord     ○ Dracula             │    │
│  │  键位                  ● vim   ○ emacs   ○ arrow        │    │
│  │                                                         │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                 │
│  ┌─ 行为设置 ─────────────────────────────────────────────┐    │
│  │                                                         │    │
│  │  默认视图              ● 今日  ○ 本周  ○ 本月  ○ 收件箱 │    │
│  │  通知方式              ● 静默  ○ 徽标  ○ 铃声  ○ 系统   │    │
│  │  任务 ID 格式          ● UUIDv7 ○ ULID  ○ 自增          │    │
│  │  事件日志              [x] 启用                         │    │
│  │                                                         │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                 │
│  ┌─ 路径设置 ─────────────────────────────────────────────┐    │
│  │                                                         │    │
│  │  监听路径              [./tasks.json                  ] │    │
│  │  配置目录              ~/.config/mutsumi/  (只读)       │    │
│  │  事件日志路径          [./events.jsonl                ] │    │
│  │                                                         │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                 │
│  ┌─ 预览 ─────────────────────────────────────────────────┐    │
│  │                                                         │    │
│  │   config.toml:                                          │    │
│  │   ┌──────────────────────────────────────────────────┐  │    │
│  │   │ [general]                                        │  │    │
│  │   │ language = "en"                                  │  │    │
│  │   │ default_scope = "day"                            │  │    │
│  │   │                                                  │  │    │
│  │   │ [theme]                                          │  │    │
│  │   │ name = "monochrome"                              │  │    │
│  │   │                                                  │  │    │
│  │   │ [keys]                                           │  │    │
│  │   │ preset = "vim"                                   │  │    │
│  │   └──────────────────────────────────────────────────┘  │    │
│  │                                                         │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                 │
│          [ 保存并启动 ]           [ 取消 ]                      │
│                                                                 │
│  配置已保存到 ~/.config/mutsumi/config.toml                     │
└─────────────────────────────────────────────────────────────────┘
```

#### 4.2.2 交互模型

| 输入 | 行为 |
|---|---|
| `Tab` / `Shift+Tab` | 在选项组之间移动焦点 |
| `←` `→` 或鼠标点击 | 在组内选项间切换 |
| `Space` 或点击 | 切换复选框 |
| 文本输入框 | 直接输入，Tab 确认 |
| 在 [保存并启动] 上按 `Enter` | 写入配置 + 创建 tasks.json + 启动 TUI |
| `Escape` 或 [取消] | 不保存退出 |

#### 4.2.3 实时预览

底部区域显示将要生成的 `config.toml` 的**实时预览**。每次切换/修改都会即时更新预览。让用户完全透明、完全放心。

#### 4.2.4 `mutsumi init` 生成的文件

```
~/.config/mutsumi/
└── config.toml              ← 用户偏好

./tasks.json                 ← 示例任务（若不存在）
```

init 创建的示例 `tasks.json`：

```json
{
  "$schema": "https://mutsumi.dev/schema/v1.json",
  "version": 1,
  "tasks": [
    {
      "id": "01EXAMPLE000000000000000001",
      "title": "Welcome to Mutsumi! Toggle me with Space or click the checkbox.",
      "status": "pending",
      "scope": "day",
      "priority": "normal",
      "tags": ["tutorial"],
      "children": []
    },
    {
      "id": "01EXAMPLE000000000000000002",
      "title": "Try editing this task with 'e' key",
      "status": "pending",
      "scope": "day",
      "priority": "low",
      "tags": ["tutorial"],
      "children": []
    }
  ]
}
```

### 4.3 设置后修改配置

```bash
mutsumi config --edit       # 用 $EDITOR 打开 config.toml
mutsumi config --show       # 打印当前配置到标准输出
mutsumi config --reset      # 重置为默认值（需确认）
mutsumi init                # 重新运行设置面板（覆盖现有配置）
```

## 5. Agent 自动配置

### 5.1 问题

用户希望 AI Agent 自动知道 `tasks.json` 的存在以及如何读写它。手动设置（复制 prompt 模板、配置文件路径）是摩擦。

### 5.2 `mutsumi setup --agent` 命令

```bash
mutsumi setup --agent claude-code
mutsumi setup --agent codex-cli
mutsumi setup --agent aider
mutsumi setup --agent opencode
mutsumi setup --agent custom
```

#### 5.2.1 它做了什么

对每个支持的 Agent，`mutsumi setup --agent <name>` 执行：

| Agent | 操作 |
|---|---|
| `claude-code` | 将 Mutsumi 集成规则追加到项目级 `CLAUDE.md` |
| `codex-cli` | 创建/更新 `AGENTS.md` |
| `aider` | 打印到 stdout（手动集成） |
| `opencode` | 更新 `opencode.md` 指令 |
| `gemini-cli` | 创建/更新 `GEMINI.md` |
| `custom` | 打印 prompt 模板到标准输出供手动集成 |

#### 5.2.2 注入的 Prompt 模板

注入到 Agent 配置中的 prompt：

```markdown
## Mutsumi Task Integration

This project uses Mutsumi for task management. Tasks are stored in `./tasks.json`.

When the user asks you to manage tasks (add, complete, delete, organize):
1. Read `./tasks.json`
2. Modify the tasks array following this schema:
   - Required: `id` (unique string), `title` (string), `status` ("pending"|"done")
   - Optional: `scope` ("day"|"week"|"month"|"inbox"), `priority` ("high"|"normal"|"low"), `tags` (string[]), `children` (Task[]), `due_date` (ISO date), `description` (string)
3. Write the entire file back (preserve unknown fields)
4. Use atomic write (temp file + rename) when possible
5. Generate UUIDv7 or any unique string for new task IDs

The Mutsumi TUI watches this file and re-renders automatically.
```

#### 5.2.3 交互式 Agent 配置

不指定 Agent 名称时启动选择器：

```
┌──────────── 选择你的 Agent ───────────────────────────────────┐
│                                                                │
│  你使用哪个 Agent？（点击或方向键+回车）                        │
│                                                                │
│  ● Claude Code     → 写入 CLAUDE.md                            │
│  ○ Codex CLI       → 写入 AGENTS.md                              │
│  ○ Aider           → 打印到 stdout                               │
│  ○ OpenCode        → 写入 opencode.md                          │
│  ○ Gemini CLI      → 写入 GEMINI.md                            │
│  ○ Custom          → 打印 prompt 到标准输出                     │
│                                                                │
│  [配置]  [取消]                                                 │
│                                                                │
│  提示：你可以多次运行此命令来配置多个 Agent。                    │
└────────────────────────────────────────────────────────────────┘
```

### 5.3 Agent 一行式安装+配置

终极零摩擦 Agent 体验：

```bash
# Agent（如 Claude Code）只需执行这一条命令：
uv tool install mutsumi && mutsumi init --defaults && mutsumi setup --agent claude-code
```

执行效果：

1. 全局安装 Mutsumi
2. 以默认值创建配置（无交互界面）
3. 注入集成 prompt 到 Agent 配置

`--defaults` 标志跳过交互式设置面板，使用全部默认值。

## 6. 升级

```bash
uv tool upgrade mutsumi          # 升级到最新版
uv tool upgrade mutsumi==0.3.0   # 指定版本
```

### 6.1 配置迁移

当新版本引入配置变更时：

- 新字段：自动用默认值填充，现有配置不动
- 移除的字段：静默忽略，不报错
- 不自动重写配置文件 — 用户的文件是神圣的

### 6.2 破坏性变更

如果 `tasks.json` schema 有破坏性变更（v1.0 前不太可能）：

```bash
mutsumi migrate            # 交互式迁移
mutsumi migrate --dry-run  # 预览变更
```

## 7. 卸载

```bash
uv tool uninstall mutsumi
```

这会移除 CLI 二进制文件。配置文件和数据文件**不会**自动删除。

完全清理：

```bash
uv tool uninstall mutsumi
rm -rf ~/.config/mutsumi/                    # 配置
rm -rf ~/.local/share/mutsumi/               # 日志
# tasks.json 是你的数据 — 如需删除请手动处理
```

## 8. 平台特殊说明

### 8.1 macOS

```bash
# 若未安装 uv：
curl -LsSf https://astral.sh/uv/install.sh | sh
uv tool install mutsumi
```

配置位置：`~/.config/mutsumi/`（XDG）或 `~/Library/Application Support/mutsumi/`

### 8.2 Linux

与 macOS 相同。`~/.config/mutsumi/` 遵循 XDG 标准。

### 8.3 Windows

```powershell
# 安装 uv
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
uv tool install mutsumi
```

配置位置：`%APPDATA%\mutsumi\`

Windows Terminal Quake Mode 设置（推荐）：

1. 打开 Windows Terminal 设置 → 添加新配置文件
2. 设置 `mutsumi` 为启动命令
3. 启用 Quake Mode 快捷键（默认：`` Win+` ``）

## 9. 设计原理

### 9.1 为什么一屏式而不是分步向导？

分步向导制造焦虑："还剩几步？能返回吗？是不是漏了什么？"一屏式面板彻底消除了这些。你看到一切，改你想改的，完事。

### 9.2 为什么要实时预览？

安装 Mutsumi 的用户大概率是终端重度用户，理解 TOML。展示实际生成的配置文件既建立信任，也同时教会用户配置格式。

### 9.3 为什么 Agent 配置是独立的？

Agent 配置修改的是 Mutsumi 领域之外的文件（`CLAUDE.md`、`AGENTS.md` 等）。将其与 `mutsumi init` 分离遵循最小惊讶原则 — init 只碰 Mutsumi 自己的配置。

---

## 附录 A：配置相关 CLI 完整参考

```
mutsumi init                    启动交互式设置面板
mutsumi init --defaults         以全部默认值创建配置（非交互）
mutsumi init --lang zh          以中文为默认语言创建配置
mutsumi setup --agent <name>    配置 Agent 集成
mutsumi setup --agent           交互式 Agent 选择器
mutsumi config --edit           用 $EDITOR 打开配置
mutsumi config --show           打印当前配置
mutsumi config --reset          重置配置为默认值
mutsumi config --path           打印配置文件路径
mutsumi validate                校验 tasks.json 格式
mutsumi schema                  输出 tasks.json 的 JSON Schema
mutsumi schema --format md      以 Markdown 格式输出 schema
```
