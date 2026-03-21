# Mutsumi 朋友内测 — 使用 SOP

> **[English Version](./BETA_USAGE.md)**

这是内测使用手册，从头到尾跟着走就行。

---

## 0. 前置条件

- macOS / Linux 终端（Windows 用 WSL）
- 已安装 `uv`——没有的话：
  ```bash
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```

---

## 1. 安装

```bash
uv tool install git+https://github.com/ywh555hhh/Mutsumi.git
```

验证：
```bash
mutsumi --version
# 应输出: mutsumi, version 0.4.0b1
```

如果提示 `command not found`，确保 `~/.local/bin` 在 PATH 里：
```bash
export PATH="$HOME/.local/bin:$PATH"
```

---

## 2. 初始化配置（可选）

```bash
mutsumi init --defaults
```

这会创建 `~/.config/mutsumi/config.toml`，默认值：
- 主题：`monochrome-zen`
- 键位：`vim`
- 语言：`en`

自定义语言：
```bash
mutsumi init --lang zh          # 中文
mutsumi init --lang ja          # 日语
```

或者直接编辑：
```bash
mutsumi config --edit           # 用 $EDITOR 打开
mutsumi config --show           # 打印当前配置
```

**完全跳过这步也行——Mutsumi 不需要任何配置文件就能用。**

---

## 3. 创建第一批任务

### 方式 A：命令行（推荐快速上手）

```bash
cd ~/your-project

mutsumi add "修复登录 Bug" --priority high --scope day --tags "bugfix"
mutsumi add "写周报" --priority normal --scope week --tags "life"
mutsumi add "更新文档" --priority low --scope month --tags "docs"
```

验证：
```bash
mutsumi list
# 应显示 3 个任务
cat tasks.json
# 应该是合法 JSON，包含 3 个任务
```

### 方式 B：让 AI Agent 创建

直接告诉你的 Agent：
> "在当前目录创建一个 tasks.json，加几个示例任务。"

Agent 会直接写 `tasks.json`，Mutsumi 会自动监听这个文件。

### 方式 C：复制示例文件

```bash
# 如果你 clone 了仓库
cp examples/tasks.json ./tasks.json
```

---

## 4. 启动 TUI

```bash
mutsumi
```

自动监听当前目录的 `./tasks.json` 并渲染任务看板。

监听其他路径：
```bash
mutsumi --path /path/to/tasks.json
```

### 你应该看到的界面

```
[Today] Week  Month  Inbox              mutsumi
─────────────────────────────────────────────────
▼ HIGH ─────────────────────────────────────
[ ] 修复登录 Bug                   bugfix  ★★★

▼ NORMAL ───────────────────────────────────
[ ] 写周报                         life    ★★

▼ LOW ──────────────────────────────────────
[ ] 更新文档                       docs    ★

─────────────────────────────────────────────────
3 tasks · 0 done · 3 pending
```

---

## 5. 键盘操作

### 导航（vim 键位——默认）

| 按键 | 操作 |
|------|------|
| `j` / `k` | 下移 / 上移 |
| `G` | 跳到底部 |
| `gg` | 跳到顶部 |
| `1` `2` `3` `4` | 切换到 Today / Week / Month / Inbox 标签 |
| `Tab` / `Shift+Tab` | 下一个 / 上一个标签 |
| `q` | 退出 |

### 任务操作

| 按键 | 操作 |
|------|------|
| `Space` | 切换完成/待办 |
| `n` | 新建任务（弹出表单） |
| `e` | 编辑任务（弹出表单） |
| `dd` | 删除任务（按 `y` 确认） |
| `i` | 行内编辑标题 |
| `Enter` | 显示任务详情面板 |
| `Escape` | 关闭详情面板 |

### 其他

| 按键 | 操作 |
|------|------|
| `/` | 打开搜索栏（按标题/标签过滤） |
| `+` / `-` | 提升 / 降低优先级 |
| `J` / `K` | 在列表中下移 / 上移任务 |
| `h` / `l` | 折叠 / 展开优先级分组 |
| `z` | 切换折叠（显示/隐藏子任务） |
| `y` | 复制任务 |
| `p` | 粘贴任务（在下方） |
| `A` (Shift+a) | 添加子任务 |
| `s` | 排序任务 |
| `?` | 显示帮助界面 |

### 鼠标操作

- **点击** 顶部标签按钮切换标签
- **点击** 任务行选中
- **点击** 底部 `[+New]` / `[/Search]` 按钮
- **点击** 复选框区域切换完成/待办
- **点击** 标题区域打开详情面板

---

## 6. tmux 分屏设置（推荐）

左边跑 Agent，右边跑 Mutsumi：

```bash
# 如果你 clone 了仓库：
bash scripts/tmux-dev.sh

# 或者手动：
tmux new-session -d -s dev
tmux split-window -h -p 30 "mutsumi"
tmux select-pane -t 0
tmux attach -t dev
```

在左侧 pane 正常使用你的 Agent，每次 Agent 写入 `tasks.json`，右侧 Mutsumi 即时更新。

### iTerm2 替代方案

1. `Cmd+D` 垂直分屏
2. 右侧 pane：`mutsumi`
3. 左侧 pane：你的 Agent / shell

---

## 7. Agent 集成

### 方式 A：手动（适用于任何 Agent）

开始会话时告诉你的 Agent：

> 这个项目使用 Mutsumi 做任务管理。任务存在 `./tasks.json` 里。
> 读取文件，修改 `tasks` 数组，把整个文件写回去。
> 必填字段：`id`（唯一字符串），`title`（字符串），`status`（"pending" 或 "done"）。
> 可选：`scope`（"day"/"week"/"month"/"inbox"），`priority`（"high"/"normal"/"low"），`tags`（字符串数组），`description`（字符串）。

### 方式 B：自动注入（Claude Code / Codex CLI / Gemini CLI）

```bash
cd ~/your-project
mutsumi setup --agent claude-code   # 追加规则到 CLAUDE.md
mutsumi setup --agent codex-cli     # 追加到 AGENTS.md
mutsumi setup --agent gemini-cli    # 追加到 GEMINI.md
```

这会在 Agent 的配置文件末尾追加一段 `## Mutsumi Task Integration`。Agent 会自动知道怎么读写 `tasks.json`。

验证：
```bash
cat CLAUDE.md   # 末尾应包含 "## Mutsumi Task Integration"
```

重复执行是安全的——不会重复注入。

### 方式 C：其他 Agent（Aider / OpenCode / 自定义）

```bash
mutsumi setup --agent custom        # 打印 prompt 到标准输出
```

复制输出内容，粘贴到你的 Agent 的系统提示词或配置里。

---

## 8. CLI 完整参考

```bash
# 任务 CRUD
mutsumi add "标题" [-P high|normal|low] [-s day|week|month|inbox] [-t "tag1,tag2"] [-d "描述"]
mutsumi done <id前缀>              # 标记完成
mutsumi edit <id前缀> [--title "新标题"] [--priority high] [--scope week] [--tags "a,b"]
mutsumi rm <id前缀>                # 删除任务
mutsumi list                        # 列出所有任务

# 设置
mutsumi init                        # 交互式设置
mutsumi init --defaults             # 非交互，全部默认值
mutsumi init --lang zh              # 设置中文
mutsumi setup --agent <名称>        # Agent 集成
mutsumi setup                       # 列出可选 Agent

# 配置
mutsumi config --edit               # 用编辑器打开
mutsumi config --show               # 打印配置
mutsumi config --reset              # 重置为默认值
mutsumi config --path               # 打印配置文件路径

# 工具
mutsumi validate                    # 验证 tasks.json
mutsumi schema                      # 打印 JSON Schema
mutsumi --version                   # 打印版本号
```

**ID 前缀匹配**：不需要输入完整的 26 位任务 ID，任何唯一前缀都行：
```bash
mutsumi done 01EX    # 匹配 "01EXAMPLE000000000000000001"（如果唯一）
```

---

## 9. 配置参考

配置文件：`~/.config/mutsumi/config.toml`

```toml
# 主题 — "monochrome-zen"（默认）、"solarized"、"nord"、"dracula"
theme = "monochrome-zen"

# 键位 — "vim"（默认）、"emacs"、"arrows"
keybindings = "vim"

# 语言 — "en"（默认）、"zh"、"ja"
language = "en"

# 默认任务文件路径（可选）
# default_path = "/path/to/tasks.json"

# 任务列表显示的列
columns = ["checkbox", "title", "tags", "priority"]

# 事件日志（可选——JSONL 格式）
# event_log_path = "~/.local/share/mutsumi/events.jsonl"

# 自定义 CSS 覆盖（可选）
# custom_css_path = "~/.config/mutsumi/custom.tcss"
```

---

## 10. tasks.json 数据格式

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
      "created_at": "2026-03-21T08:00:00Z",
      "due_date": "2026-03-25",
      "completed_at": null,
      "description": "可选的描述"
    }
  ]
}
```

| 字段 | 必填 | 类型 | 可选值 |
|------|------|------|--------|
| `id` | 是 | string | 唯一标识，建议 26 位 |
| `title` | 是 | string | 任务标题 |
| `status` | 是 | string | `"pending"` 或 `"done"` |
| `scope` | 否 | string | `"day"` `"week"` `"month"` `"inbox"`（默认 `"inbox"`） |
| `priority` | 否 | string | `"high"` `"normal"` `"low"`（默认 `"normal"`） |
| `tags` | 否 | string[] | 任意标签 |
| `children` | 否 | Task[] | 嵌套子任务（相同格式） |
| `due_date` | 否 | string | ISO 日期 `"2026-03-25"` |
| `description` | 否 | string | 详细描述 |
| `created_at` | 否 | string | ISO 时间戳 |
| `completed_at` | 否 | string | ISO 时间戳，完成时设置 |

**规则**：Mutsumi 不认识的字段会被原样保留——永远不会删除你自定义的字段。

---

## 11. 卸载

```bash
uv tool uninstall mutsumi
rm -rf ~/.config/mutsumi/           # 配置（可选）
rm -rf ~/.local/share/mutsumi/      # 日志（可选）
# tasks.json 是你的数据——自己决定要不要删
```

---

## 12. 常见问题

### `mutsumi` 命令找不到
```bash
export PATH="$HOME/.local/bin:$PATH"
# 加到 ~/.bashrc 或 ~/.zshrc 里永久生效
```

### TUI 显示 "Nothing here yet" 但 tasks.json 里有任务
看看你在哪个标签页——任务按 scope 过滤。按 `2` 看 Week，`3` 看 Month，`4` 看 Inbox。

### Agent 改了 tasks.json 但 TUI 没更新
- 确认 Agent 写入的是 Mutsumi 正在监听的同一个 `tasks.json` 路径
- 检查 JSON 是否合法：`mutsumi validate`

### 主题 / 键位没生效
- 运行 `mutsumi config --show` 确认配置加载正确
- 配置位置：`~/.config/mutsumi/config.toml`

---

## 13. 反馈

在 GitHub 提 Issue：https://github.com/ywh555hhh/Mutsumi/issues

或直接找 Wayne。

---

*mutsumi（若叶睦）—— "和睦，亲近"。她不告诉你该怎么做，只是安静地在那里等你。*
