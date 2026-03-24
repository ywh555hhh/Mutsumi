# Mutsumi Friend Beta — 使用 SOP

> **[English Version](./BETA_USAGE.md)** | **[日本語版](./BETA_USAGE_ja.md)**

这是当前 **`1.0.0b1`** 版本线的中文 beta 使用指南。
用于内部测试与朋友内测 onboarding。

---

## 0. 前置条件

- macOS / Linux 终端
- Windows 用户：beta 阶段优先使用 WSL
- Python 3.12+
- `uv` 或 `pip`

如果没有安装 `uv`：

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

---

## 1. 安装

### 方式 A —— PyPI 包

```bash
uv tool install mutsumi-tui
# 或
pip install mutsumi-tui
```

### 方式 B —— 从源码 / git

```bash
uv tool install git+https://github.com/ywh555hhh/Mutsumi.git
```

验证：

```bash
mutsumi --version
# 预期输出：mutsumi, version 1.0.0b1
```

如果看到 `command not found`，请确认你的 tool bin 目录已经在 `PATH` 中。

---

## 2. 首次启动

```bash
cd ~/your-project
mutsumi
```

如果这是首次运行，Mutsumi 会显示 onboarding。
如果之前已经完成过 onboarding，则会直接打开。

### Onboarding 会配置什么

- language
- keybindings
- theme
- workspace mode
- 可选的 agent integration

### 当前默认值

- Theme：`monochrome-zen`
- Keybindings：`arrows`
- Language：`en`

---

## 3. 显式初始化任务文件（可选）

在使用 Mutsumi 前，你**不需要**先手动初始化文件，但 CLI 支持这样做。

```bash
mutsumi init                # 创建 ./mutsumi.json
mutsumi init --personal     # 创建 ~/.mutsumi/mutsumi.json
mutsumi init --project      # 创建 ./mutsumi.json 并注册当前仓库
```

对于旧项目，Mutsumi 仍会自动读取 `tasks.json` 作为回退。

---

## 4. 创建第一批任务

### 方式 A：CLI

```bash
mutsumi add "修复登录 Bug" --priority high --scope day --tags "bugfix"
mutsumi add "写周报" --priority normal --scope week --tags "life"
mutsumi add "更新文档" --priority low --scope month --tags "docs"
```

验证：

```bash
mutsumi list
mutsumi validate
```

### 方式 B：让 AI agent 写文件

告诉 Agent：

> 这个项目使用 Mutsumi。任务应该写入 `./mutsumi.json`。
> 如果只存在旧的 `tasks.json`，就改那个文件。
> 先读完整文件，再修改 `tasks` 数组，并以原子方式写回。

### 方式 C：创建个人任务

```bash
mutsumi init --personal
```

然后再次启动 Mutsumi，就能在多源模式中看到 personal source。

---

## 5. 启动 TUI

```bash
mutsumi
```

默认文件解析顺序：

1. 显式 `--path`
2. `./mutsumi.json`
3. `./tasks.json`
4. 新项目默认新建目标：`./mutsumi.json`

指定其他文件：

```bash
mutsumi --path /path/to/mutsumi.json
```

监听额外任务文件：

```bash
mutsumi --watch /path/to/project-a/mutsumi.json --watch /path/to/project-b/mutsumi.json
```

---

## 6. 你应该看到什么

### 单源视图

```text
[Today] [Week] [Month] [Inbox]                    mutsumi ♪
------------------------------------------------------------
▼ HIGH
[ ] 修复登录 Bug                        bugfix        ★★★

▼ NORMAL
[ ] 写周报                              life          ★★

▼ LOW
[ ] 更新文档                            docs          ★
------------------------------------------------------------
3 tasks · 0 done · 3 pending
```

### 多源视图

```text
[★ Main] [Personal] [your-project]                     mutsumi ♪
---------------------------------------------------------------
★ Main Dashboard

★ Personal      2 pending
  • 买咖啡豆
  • 回复导师

your-project    3 pending
  • 修复登录 Bug
  • 更新文档
```

---

## 7. 键盘控制

### 默认预设：`arrows`

| 按键 | 操作 |
|---|---|
| `Up` / `Down` | 移动选择 |
| `Home` / `End` | 跳到顶部 / 底部 |
| `Left` / `Right` | 折叠 / 展开 |
| `Space` | 切换完成状态 |
| `Enter` | 打开详情面板 |
| `n` | 新建任务 |
| `e` | 编辑任务 |
| `i` | 行内编辑标题 |
| `A` | 添加子任务 |
| `Tab` / `Shift+Tab` | 下一个 / 上一个 source 标签 |
| `1-9` | 跳转到 source 标签 |
| `f` | 循环切换 scope filter |
| `/` | 搜索 |
| `s` | 排序 |
| `?` | 帮助 |
| `q` | 退出 |

### 其他预设

- `vim`
- `emacs`

这些都是可选项，**不是**当前 beta 的默认预设。

### 鼠标

- 点击 source tabs 切换来源
- 点击 scope chips 切换过滤器
- 点击任务行进行选择
- 点击标题打开详情面板
- 点击复选框切换完成状态
- 点击 footer actions，例如新建任务或搜索

---

## 8. Agent 集成

### 方式 A：skills-first setup（推荐）

```bash
mutsumi setup --agent claude-code
mutsumi setup --agent codex-cli
mutsumi setup --agent gemini-cli
mutsumi setup --agent opencode
```

这会把内置的 Mutsumi skills 安装到对应 agent 的 skill 目录。
它**不会**修改 `CLAUDE.md`、`AGENTS.md` 等项目文件。

### 方式 B：skills + project doc injection

```bash
mutsumi setup --agent claude-code --mode skills+project-doc
```

这会安装 skills，并向 agent 的项目说明文件追加一段 Mutsumi 集成片段。

### 方式 C：manual snippet

```bash
mutsumi setup --agent aider --mode snippet
mutsumi setup --agent custom --mode snippet
```

这会打印可复制的说明文本。

### 快速手工提示词

```text
This project uses Mutsumi for task management.
Prefer ./mutsumi.json; use ./tasks.json only if the project is still on the legacy filename.
Read the whole file, modify the tasks array, preserve unknown fields, and write the file back atomically.
```

---

## 9. tmux / 分屏终端设置

### tmux（推荐）

```bash
bash scripts/tmux-dev.sh
```

### 手动分屏

```bash
tmux new-session -d -s dev
tmux split-window -h -p 35 "mutsumi"
tmux select-pane -t 0
tmux attach -t dev
```

### iTerm2 / VS Code / Cursor

- 竖向拆分终端
- 右侧 pane：`mutsumi`
- 左侧 pane：你的 agent 或 shell

然后让 agent 添加或更新任务。TUI 应该会自动刷新。

---

## 10. CLI 参考

```bash
# CRUD
mutsumi add "title" [-P high|normal|low] [-s day|week|month|inbox] [-t "tag1,tag2"] [-d "description"]
mutsumi done <id-prefix>
mutsumi edit <id-prefix> [--title "new"] [--priority high] [--scope week] [--tags "a,b"]
mutsumi rm <id-prefix>
mutsumi list

# Setup / onboarding
mutsumi init
mutsumi init --personal
mutsumi init --project
mutsumi setup --agent <name>
mutsumi setup --agent <name> --mode skills+project-doc
mutsumi setup --agent <name> --mode snippet
mutsumi project add /path/to/repo
mutsumi project list
mutsumi migrate

# Validation / schema
mutsumi validate
mutsumi schema
mutsumi --version
```

对于 CLI 命令来说，通常任何唯一的任务 ID 前缀都够用。

---

## 11. 配置参考

首选配置路径：

```text
~/.mutsumi/config.toml
```

旧回退路径：

```text
~/.config/mutsumi/config.toml
```

示例：

```toml
theme = "monochrome-zen"
keybindings = "arrows"
language = "en"
default_scope = "day"
default_tab = "main"
notification_mode = "quiet"
```

---

## 12. 任务文件 Schema

规范文件名：`mutsumi.json`
旧回退文件名：`tasks.json`

```json
{
  "version": 1,
  "tasks": [
    {
      "id": "01EXAMPLE000000000000000001",
      "title": "任务标题",
      "status": "pending",
      "scope": "day",
      "priority": "normal",
      "tags": ["dev", "urgent"],
      "children": [],
      "created_at": "2026-03-23T08:00:00Z",
      "due_date": "2026-03-25",
      "completed_at": null,
      "description": "可选描述"
    }
  ]
}
```

未知字段会被保留。

---

## 13. 故障排查

### 找不到 `mutsumi` 命令

确保你的 tool bin 目录已经在 `PATH` 中。

### TUI 没有显示内容，但文件存在

- 检查当前在哪个 source 标签页
- 检查激活的 scope filter
- 运行 `mutsumi validate`

### Agent 改动没有出现

- 确保 agent 写入的是 Mutsumi 正在监听的同一个文件
- 优先使用 `mutsumi.json`
- 如果仓库仍在使用旧的 `tasks.json`，确保监听的是那个文件
- 用 `mutsumi validate` 验证文件

### 主题或键位没有生效

- 如果你的工作流里提供了 `mutsumi config --show`，可以运行它
- 检查 `~/.mutsumi/config.toml`
- 记住默认键位预设是 `arrows`

---

## 14. 当前 Beta 定位

对于当前 beta 版本线：

- 版本号是 **`1.0.0b1`**
- 规范任务文件是 **`mutsumi.json`**
- 旧回退文件是 **`tasks.json`**
- 默认预设是 **`arrows`**
- 多源仪表盘已经属于当前已 shipped 的 beta 能力
- calendar 是计划中的功能，还不是已 shipped 的 beta 视图
