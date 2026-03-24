# RFC-007：多源 Hub —— 从工具走向指挥中心

> **[English Version](./RFC-007-multi-source-hub.md)** | **[日本語版](./RFC-007-multi-source-hub_ja.md)**

| 字段 | 值 |
|---|---|
| **RFC** | 007 |
| **标题** | 多源 Hub：个人待办 + 多项目 Agent 仪表盘 |
| **状态** | Draft |
| **作者** | Wayne (ywh) |
| **创建时间** | 2026-03-22 |

---

## 摘要

Mutsumi 目前只监听工作目录中的一个 `tasks.json`——一个项目、一个文件、一个视图。本 RFC 提议把 Mutsumi 从**单项目任务查看器**演进为一个**个人指挥中心**，统一聚合：

1. **全局个人待办清单**——你的生活任务，不绑定任何项目
2. **多个项目仪表盘**——每个项目都由各自的 Agent 写入自己的 `mutsumi.json`
3. **一个 Main tab**——统一的一眼总览，展示此刻最重要的内容

这正是从“工具”升级为“hub”的自然方向。

## 1. 动机

### 1.1 双重分散问题

独立开发者和多项目用户会同时遭遇两类分散：

| 分散类型 | 当前状态 | 痛点 |
|---|---|---|
| **个人待办** | Todoist、Obsidian、便利贴、脑子里 | 查看个人任务时的上下文切换会打断工作流 |
| **Agent 项目进展** | 每个项目目录都有自己的终端 | 同时 vibe-code 3 个项目？就得开 3 个终端、`cd` 3 次、看 3 个文件 |

Mutsumi 已经解决了单项目的 “Agent → 可视反馈” 闭环。但一旦你同时跑 2 个以上项目，价值就会下降——你又回到了来回切 tab 的状态。

### 1.2 核心洞察

> **真正的瓶颈不在于管理一个项目内的任务，而在于同时看见你所有的线程。**

一个同时在 project-A 上跑 Claude Code、在 project-B 上跑 Codex、并且还要记着“回复导师邮件”的开发者，需要的是**一个**可以扫一眼的地方。不是三个终端。不是一个浏览器页签。是一整个 TUI。

### 1.3 定位转变

| 之前 | 之后 |
|---|---|
| “一个 Agent session 的外部显示器” | “你整个工作负载的个人指挥中心” |
| 单项目查看器 | 多源聚合器 |
| cwd 中的 `tasks.json` | 全局 `mutsumi.json` + 每项目 `mutsumi.json` |

## 2. 设计

### 2.1 文件重命名：`tasks.json` → `mutsumi.json`

数据文件重命名为 `mutsumi.json`，原因如下：

- **品牌识别**：归属清晰，避免与其他工具的 `tasks.json` 冲突
- **可发现性**：在项目里看到 `mutsumi.json`，立刻就知道“这个项目在用 Mutsumi”
- **多源清晰度**：同时监听多个文件时，文件名能更清楚表达意图

**迁移方式**：Mutsumi 会自动检测并读取 `tasks.json` 作为 fallback。`mutsumi migrate` 命令会就地把 `tasks.json` 重命名为 `mutsumi.json`。

Schema 保持**完全一致**——只改文件名，不改结构。`version` 字段仍然是 `1`。

### 2.2 数据架构：全局 + 每项目

```text
~/.mutsumi/                          ← 平台感知路径（Windows 上为 APPDATA）
├── mutsumi.json                     ← 个人全局任务
└── config.toml                      ← 从 ~/.config/mutsumi/ 迁移到这里

~/Code/project-a/
└── mutsumi.json                     ← Agent 驱动的项目任务

~/Code/project-b/
└── mutsumi.json                     ← Agent 驱动的项目任务
```

**两类数据源：**

| 来源 | 位置 | 写入者 | 用途 |
|---|---|---|---|
| **个人** | `~/.mutsumi/mutsumi.json` | 用户（TUI/CLI） | 生活任务、跨项目杂务、个人提醒 |
| **项目** | `<project-dir>/mutsumi.json` | Agent + 用户 | 由 AI Agents 驱动的项目任务 |

每个文件都是独立的 `mutsumi.json`，使用相同 schema。没有跨文件引用，没有共享状态，每个文件都能单独使用。

### 2.3 项目注册表

项目在 `~/.mutsumi/config.toml` 中注册：

```toml
[[projects]]
name = "saas-app"
path = "~/Code/saas-app"

[[projects]]
name = "oshigrid"
path = "~/Code/oshigrid"

[[projects]]
name = "mutsumi"
path = "~/Code/Mutsumi"
```

**注册方式：**

| 方式 | 命令 | 行为 |
|---|---|---|
| CLI add | `mutsumi project add ~/Code/saas-app` | 注册路径，若缺失则自动创建 `mutsumi.json` |
| CLI add with name | `mutsumi project add ~/Code/saas-app --name saas` | 用自定义显示名注册 |
| TUI add | `P` → 文件夹选择器 / 路径输入 | 与 CLI 相同，但在 TUI 内完成 |
| CLI remove | `mutsumi project remove saas-app` | 取消注册（**不会**删除 `mutsumi.json`） |
| CLI list | `mutsumi project list` | 显示全部已注册项目 |

当添加一个项目时：

1. 路径会被解析为绝对路径并写入 config
2. 如果该路径下不存在 `mutsumi.json`，就自动创建一个默认空模板
3. 如果 TUI 正在运行，watchdog 会立刻开始监听新文件

### 2.4 Tab 结构

```text
[★ Main]  [Personal]  [saas-app]  [oshigrid]  [mutsumi]
```

| Tab | 数据源 | 内容 |
|---|---|---|
| **★ Main** | 所有源聚合 | 仪表盘：个人高优先级 + 各项目摘要卡片 |
| **Personal** | `~/.mutsumi/mutsumi.json` | 完整个人任务列表，带 day/week/month/inbox 子过滤 |
| **<project>** | `<project>/mutsumi.json` | 完整项目任务列表，带 day/week/month/inbox 子过滤 |

Tabs 是**动态的**——随着项目注册/移除而出现或消失。顺序遵循 config 文件中的顺序。Personal 永远排第二（仅次于 Main）。

#### 2.4.1 Main Tab 布局

Main tab 是一个**只读仪表盘**——用于一眼掌握整体情况。

```text
┌──────────────────────────────────────────────────────────┐
│  [★ Main]  [Personal]  [saas-app]  [oshigrid]  mutsumi  │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  ▸ Personal                                    2 tasks   │
│    ★★★ 写毕业论文 introduction                           │
│    ★★  回复导师邮件                                       │
│                                                          │
│  ▸ saas-app                              3/7 done  42%  │
│    ★★★ Fix auth token refresh                            │
│    ★★  Add rate limiting middleware                      │
│                                                          │
│  ▸ oshigrid                              1/4 done  25%  │
│    ★★★ Deploy staging environment                        │
│                                                          │
│  ▸ mutsumi                               5/5 done 100%  │
│    ✓ All tasks completed                                 │
│                                                          │
├──────────────────────────────────────────────────────────┤
│  16 tasks · 9 done · 7 pending · 4 sources    🔇 quiet  │
└──────────────────────────────────────────────────────────┘
```

**Main tab 规则：**

1. 每个项目显示为一个**可折叠 section**，包含：
   - 项目名 + 进度（`done/total` + 百分比条）
   - 优先级最高的前 N 个待办任务（默认 N=3，可配置）
2. Personal section 永远排在最前面
3. 已全部完成的项目显示 “✓ All tasks completed” 摘要
4. 点击项目 section 或按 Enter → 跳转到对应项目 tab
5. Main tab **不可编辑**——任务 CRUD 在具体 tab 中进行

#### 2.4.2 项目 Tab（以及 Personal Tab）

在每个 tab 内，现有的时间型 scope filter 会被保留：

```text
┌──────────────────────────────────────────────────────────┐
│  [★ Main]  [Personal]  [saas-app]  [oshigrid]  mutsumi  │
│            ──────────                                    │
│  Filter: [Today] [Week] [Month] [Inbox] [All]           │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  ▼ HIGH                                                  │
│  [ ] Fix auth token refresh           backend   ★★★     │
│  [ ] Patch SQL injection in /users    security  ★★★     │
│                                                          │
│  ▼ NORMAL                                                │
│  [ ] Add rate limiting middleware     backend   ★★      │
│  [x] Set up CI pipeline              devops    ★★      │
│                                                          │
├──────────────────────────────────────────────────────────┤
│  4 tasks · 1 done · 3 pending                  🔇 quiet │
└──────────────────────────────────────────────────────────┘
```

scope filter（Today/Week/Month/Inbox）会成为每个 tab 内部的**子过滤器**，而不是顶层 tab。新增的 **[All]** 用于显示未过滤任务。

### 2.5 输入：键盘 + 鼠标完整覆盖

每一个操作都必须同时能通过**键盘**和**鼠标**完成。鼠标是一等公民。

#### Tab 导航

| 动作 | 键盘 | 鼠标 |
|---|---|---|
| 跳转到 tab | `1-9` | 点击 tab |
| 上一个 / 下一个 tab | `H` / `L` 或 `Shift+Tab` / `Tab` | 点击 tab |

#### Main Tab

| 动作 | 键盘 | 鼠标 |
|---|---|---|
| 浏览 sections | `↑` / `↓` | 滚动 / 点击 section |
| 进入项目 | `Enter` | 点击项目名或 `→` 按钮 |
| 折叠/展开 section | `←` / `→` | 点击 `▸` / `▾` chevron |
| 添加新项目 | `P` | 点击 footer 的 `[+ Project]` 按钮 |

#### 项目 / Personal Tabs

| 动作 | 键盘 | 鼠标 |
|---|---|---|
| 浏览任务 | `↑` / `↓` | 点击任务行 |
| 切换 done | `Space` | 点击 checkbox |
| 查看详情 | `Enter` | 点击任务标题 |
| 新建任务 | `n` | 点击 `[+ New]` 按钮 |
| 编辑任务 | `e` | 双击标题 |
| 删除任务 | `Delete` | 右键 → Delete |
| 切换 scope filter | `f` | 点击过滤 chips（Today/Week/Month/Inbox/All） |
| 提高/降低优先级 | `+` / `-` | 点击 priority stars |
| 上移/下移任务 | `Shift+↑` / `Shift+↓` | 拖拽（未来） |

#### 默认键位预设：`arrows`

默认 preset 使用**方向键**——不需要任何 vim 知识。高级用户可以在 config 中切换到 `vim` 或 `emacs`：

```toml
[keys]
preset = "arrows"   # 默认 —— arrow keys, Home/End, Shift+arrows
# preset = "vim"    # j/k/G/dd
# preset = "emacs"  # C-n/C-p/C-a/C-e
```

### 2.6 配置迁移

config 目录会迁移，以与 personal data file 保持统一：

| 之前 | 之后 |
|---|---|
| `~/.config/mutsumi/config.toml` | `~/.mutsumi/config.toml` |
| `~/.config/mutsumi/themes/` | `~/.mutsumi/themes/` |
| （没有个人任务文件） | `~/.mutsumi/mutsumi.json` |

在 Windows 上：`%APPDATA%\mutsumi\`（不变，本来就正确）。

Mutsumi 会把旧路径作为 fallback 检查，并提供 `mutsumi migrate` 来迁移 config。

### 2.7 更新后的配置 schema

```toml
[general]
language = "auto"
default_tab = "main"              # 启动时显示哪个 tab

[theme]
name = "monochrome-zen"

[keys]
preset = "vim"

[notifications]
mode = "quiet"

[dashboard]
max_tasks_per_project = 3         # Main tab 中每个项目展示多少个顶部任务
show_completed_projects = true    # 是否显示 100% 完成的项目

[[projects]]
name = "saas-app"
path = "~/Code/saas-app"

[[projects]]
name = "oshigrid"
path = "~/Code/oshigrid"

[[projects]]
name = "mutsumi"
path = "~/Code/Mutsumi"
```

## 3. Agent 协议变更

### 3.1 文件名

Agents 应写入 `mutsumi.json`（不再是 `tasks.json`）。为保持向后兼容，如果找不到 `mutsumi.json`，Mutsumi 仍会读取 `tasks.json`。

### 3.2 不改 Schema

`mutsumi.json` 的 schema 与当前 `tasks.json` **完全一致**。不会新增或移除字段。`scope` 字段继续保留其时间语义（day/week/month/inbox）。

### 3.3 Agent Setup

`mutsumi setup --agent` 命令会更新为引用 `mutsumi.json`：

```text
# In your project directory, create and manage tasks in mutsumi.json
# Schema: { "version": 1, "tasks": [...] }
# Mutsumi watches this file and renders a live TUI dashboard
```

### 3.4 多 Agent 隔离

每个项目都有自己的 `mutsumi.json`。两个在不同项目上工作的 Agents **永远不会**写入同一个文件——从设计上就是零冲突。

```text
Terminal 1: claude-code → 写入 ~/Code/saas-app/mutsumi.json
Terminal 2: codex       → 写入 ~/Code/oshigrid/mutsumi.json
Terminal 3: mutsumi     → 同时监听二者，并渲染统一视图
```

## 4. CLI 变更

### 4.1 新的 `project` 命令组

```bash
mutsumi project add <path> [--name <display-name>]
mutsumi project remove <name>
mutsumi project list
```

### 4.2 更新后的 `init` 命令

```bash
mutsumi init                    # 在 cwd 创建 mutsumi.json
mutsumi init --global           # 创建 ~/.mutsumi/mutsumi.json
mutsumi init --project <path>   # 创建 mutsumi.json + 注册项目
```

### 4.3 更新后的 `add` / `list` / `done` 命令

```bash
mutsumi add "Buy coffee" --personal          # 加到 personal tasks
mutsumi add "Fix bug" --project saas-app     # 加到指定项目
mutsumi add "Fix bug"                        # 加到 cwd 的 mutsumi.json（当前行为）

mutsumi list --all                           # 列出所有来源
mutsumi list --project saas-app              # 列出指定项目
```

### 4.4 迁移命令

```bash
mutsumi migrate                  # 在 cwd 中把 tasks.json → mutsumi.json
mutsumi migrate --config         # 把 ~/.config/mutsumi/ → ~/.mutsumi/
mutsumi migrate --all            # 两者都做
```

## 5. 实现策略

### 5.1 数据层变化

| 组件 | 变化 |
|---|---|
| `core/loader.py` | 接受多个文件路径，返回带标签的 `(source_name, TaskFile)` 元组 |
| `core/watcher.py` | 监听多个文件，并为事件打上 source name 标签 |
| `core/writer.py` | 根据当前活动 tab 上下文，把写入路由到正确文件 |
| `core/models.py` | 不变——schema 没变 |
| `core/paths.py` | 新增 `mutsumi_home()` → `~/.mutsumi/` |

### 5.2 TUI 变化

| 组件 | 变化 |
|---|---|
| `app.py` | 管理多个数据源、动态创建 tabs |
| `tui/header_bar.py` | 渲染动态项目 tabs |
| `tui/main_dashboard.py` | **新 widget**——聚合 dashboard 视图 |
| `tui/task_list_panel.py` | 不变——仍然渲染单一 source 的任务 |
| `tui/scope_filter.py` | **新 widget**——子过滤条（Today/Week/Month/Inbox/All） |

### 5.3 分阶段实施

| 阶段 | 范围 | 可交付物 |
|---|---|---|
| **5a** | 文件重命名 + fallback | 支持 `mutsumi.json`，同时兼容旧 `tasks.json` |
| **5b** | 多源数据层 | Loader/watcher 能处理 N 个文件，并带 source 标签 |
| **5c** | 项目注册表 | `mutsumi project add/remove/list` CLI 命令 |
| **5d** | Tab 重设计 | 动态 tabs：Main + Personal + 每项目 |
| **5e** | Main dashboard widget | 带进度条的聚合摘要视图 |
| **5f** | 配置迁移 | 统一到 `~/.mutsumi/` + `mutsumi migrate` |

## 6. 向后兼容

| 关注点 | 处理方式 |
|---|---|
| 现有 `tasks.json` 用户 | 自动检测为 fallback；用 `mutsumi migrate` 重命名 |
| 现有 `~/.config/mutsumi/` 配置 | 自动检测为 fallback；用 `mutsumi migrate --config` 迁移 |
| 单项目用法（未注册项目） | 行为与以前完全相同——监听 cwd 中的 `mutsumi.json` |
| Agent Protocol | schema 不变——Agents 只需要改文件名 |
| `scope` 字段语义 | 不变——仍然是时间语义（day/week/month/inbox） |
| `--watch` 标志 | 仍可使用，但更推荐 `project add` |

## 7. 这不是什么

- **不是团队协作工具。** 全部数据都在本地。没有共享 board、没有权限、没有同步。
- **不是项目管理平台。** 没有甘特图、没有 sprint、没有资源分配。只有任务。
- **不是替代 Agent。** Mutsumi 仍然是 View。Agents 仍然是 Controllers。`mutsumi.json` 仍然是 Model。
- **不是 workspace manager。** Mutsumi 不管理终端、窗口或进程。

## 8. 开放问题

1. **项目健康指标**——Main tab 是否应该显示 “last updated” 时间戳，以识别停滞项目？
2. **跨项目移动任务**——用户是否应该能把一个任务从一个项目移动到另一个项目？（v1 大概率不做。）
3. **项目归档**——已完成项目如何处理？从 registry 移除？还是打 archive flag？
4. **按项目通知**——notification mode 是否应支持 per-project 配置？
5. **项目数量上限**——是否存在实际可用上限？tab bar overflow 策略怎么做？

---

## 附录 A：迁移路径

```text
v0.4.x（当前）            v0.5.0（本 RFC）
─────────────────          ──────────────────
tasks.json          →      mutsumi.json（自动 fallback）
~/.config/mutsumi/  →      ~/.mutsumi/（自动 fallback）
[Today][Week][Month][Inbox] → [★ Main][Personal][proj-a][proj-b]
                                       └─ [Today][Week][Month][Inbox][All]
Single file watcher  →      Multi-file watcher
No personal tasks    →      ~/.mutsumi/mutsumi.json
```

## 附录 B：竞争格局

目前没有现成的终端工具能同时做到这组能力：

| 工具 | 个人待办 | 多项目 Agent 视图 | 统一仪表盘 |
|---|:---:|:---:|:---:|
| Todoist | ✅ | ❌ | ❌ |
| Taskwarrior | ✅ | ❌ | ❌ |
| GitHub Projects | ❌ | Partial | ❌ |
| Linear | ❌ | ✅ | ✅（但面向团队，不是个人） |
| **Mutsumi v0.5** | **✅** | **✅** | **✅** |
