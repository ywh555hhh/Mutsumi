# RFC-001：Mutsumi 核心架构

| 字段       | 值                                       |
|------------|------------------------------------------|
| **RFC**    | 001                                      |
| **标题**   | Mutsumi 核心产品定义与架构                |
| **状态**   | 草案                                     |
| **作者**   | Wayne (ywh)                              |
| **创建日期** | 2026-03-21                             |

> **[English Version](./RFC-001-mutsumi-core.md)** | **[日本語版](./RFC-001-mutsumi-core_ja.md)**

---

## 摘要

Mutsumi (若叶睦) 是一个面向**多线程超级个体**的静默任务外脑。她是一个独立的终端 TUI 应用，通过监听本地 JSON 文件实现与任意 AI Agent 的解耦协作。本 RFC 定义了 Mutsumi 的产品边界、核心架构、数据契约、交互规范和集成协议。

## 1. 动机

### 1.1 问题陈述

现代开发者（超级个体）的工作模式已经从单线程变成了多线程：

- **输入源碎片化**：同时在浏览器、QQ 群、Reddit、Discord、论坛之间游走
- **Agent 并发化**：让多个 AI Agent 同时干不同的活（Claude Code 做前端、Codex CLI 跑测试、Gemini CLI 写文档）
- **时间高度压缩**：每天很忙碌，没时间在复杂的项目管理工具里点来点去

现有工具的问题：

| 工具类型 | 问题 |
|---|---|
| Notion/Todoist | 太重，打开就是负担，和终端工作流割裂 |
| Taskwarrior | 纯 CLI，没有视觉锚点，不够直观 |
| GitHub Issues | 绑定平台，不支持本地离线，不够"私人" |
| IDE Todo 插件 | 绑定编辑器，Agent 无法直接写入 |

### 1.2 核心洞察

> **任务管理的瓶颈不在 "管理" 本身，而在 "唤出" 的摩擦力。**

如果查看/更新任务的操作成本接近零（一键唤出、一键划掉），用户就不会抗拒使用它。Mutsumi 把这个摩擦力压缩到了终端快捷键级别。

### 1.3 一句话定位

> "Mutsumi 和 Taskwarrior 有什么区别？"
> — **无负担唤出，天然适配你最习惯的 Agent。** Taskwarrior 是一个需要你学命令的任务数据库；Mutsumi 是一个安静的视觉看板，她不教你做事，而是等你看她一眼。

## 2. 设计原则

### 2.1 MVC 分离（核心哲学）

```
┌─────────────────────────────────────────────────┐
│                  用户的大脑                       │
│   "把修复缓存 Bug 放进今天最高优先级"              │
└────────────────────┬────────────────────────────┘
                     │ 自然语言
                     ▼
┌─────────────────────────────────────────────────┐
│        Controller: AI Agent（解耦）              │
│  Claude Code / Codex CLI / Gemini CLI / OpenCode │
│  手动编辑 / 自定义脚本 / 任何能写 JSON 的东西      │
└────────────────────┬────────────────────────────┘
                     │ 读写
                     ▼
┌─────────────────────────────────────────────────┐
│         Model: tasks.json（本地文件）             │
│     100% 数据主权，纯文本，可 Git 管理              │
└────────────────────┬────────────────────────────┘
                     │ watchdog
                     ▼
┌─────────────────────────────────────────────────┐
│      View: Mutsumi TUI（极简看板）                │
│   热重载渲染 · 鼠标/键盘交互 · 状态反写 JSON       │
└─────────────────────────────────────────────────┘
```

### 2.2 五条戒律

1. **零摩擦** — 唤出到操作完成 < 2 秒。没有加载屏，没有登录，没有网络请求。
2. **布局无关** — Mutsumi 不管窗口怎么摆。她是一个独立进程，用户用 tmux/zellij/多显示器自由布局。
3. **Agent 无关** — 不绑定任何大模型或 Agent。任何能写 JSON 的程序都是合法的 Controller。
4. **可魔改优先** — 官方提供基础骨架，用户可以极其容易地魔改数据结构、主题、快捷键、视图。
5. **纯本地** — 零网络依赖。数据就是文件，文件就在本地。

## 3. 目标用户

**主要人群：多线程超级个体**

- 同时在浏览器、QQ 群、Reddit、Discord、论坛之间游走
- 让多个 Agent 同时干不同的活
- 每天很忙碌，一切操作追求"脆爽"
- 终端是主要工作环境（或者至少不排斥终端）
- 对极客工具有天然好感，喜欢 DIY 和定制

**不适用于：**

- 需要团队协作/共享看板的 PM（请用 Linear）
- 需要 Gantt 图和资源分配的项目经理（请用 Jira）
- 完全不碰终端的用户（请用 Todoist）

## 4. 架构总览

### 4.1 系统图

```
                    ┌──────────────────────┐
                    │   Agent A (write)     │
                    │   Claude Code         │
                    └──────────┬───────────┘
                               │
┌──────────────┐               ▼              ┌──────────────┐
│  Agent B     │        ┌────────────┐        │  Agent C     │
│  Codex CLI   │───────▶│ tasks.json │◀───────│  custom script│
└──────────────┘        └─────┬──────┘        └──────────────┘
                              │
                    ┌─────────┼─────────┐
                    │   watchdog watch   │
                    ▼                   ▼
             ┌────────────┐     ┌────────────┐
             │ Mutsumi TUI│     │ event.log  │
             │ (渲染+交互)  │     │ (反向通知) │
             └─────┬──────┘     └────────────┘
                   │
                   │ 用户点击完成
                   ▼
             反写 tasks.json
```

### 4.2 组件拆分

| 组件 | 职责 | 技术选型 |
|---|---|---|
| **TUI 渲染器** | 渲染任务列表、处理用户交互 | Textual (Python) |
| **文件监听器** | 监听 tasks.json 变化并触发重绘 | watchdog |
| **数据层** | 读写 tasks.json、schema 校验 | pydantic |
| **CLI 接口** | 提供非 TUI 的命令行 CRUD | click / typer |
| **配置加载器** | 加载用户配置（主题、快捷键、语言） | tomllib (stdlib) |
| **i18n 引擎** | 界面文本多语言切换 | 自实现 (简单 dict) |
| **事件发射器** | 反向通知 Agent（可选） | 文件追加写入 |

### 4.3 技术栈

| 层级 | 选型 | 理由 |
|---|---|---|
| 语言 | Python 3.12+ | Textual 生态、开发速度、uv 加持后零摩擦 |
| 包管理 | uv | 极快、现代、符合极客审美 |
| TUI 框架 | Textual | 鼠标支持、动画、CSS-like 样式、代码量极小 |
| CLI 框架 | click | 成熟稳定、与 Textual 共存无冲突 |
| 校验 | pydantic v2 | JSON schema 校验、极快、类型安全 |
| 文件监听 | watchdog | 跨平台、成熟、事件驱动 |
| 配置格式 | TOML | 人类可读、Python stdlib 原生支持 (tomllib) |
| 分发 | uv tool install | 零依赖安装体验 |

## 5. 数据契约

> 详细 schema 定义见 `docs/specs/DATA_CONTRACT.md`

### 5.1 设计哲学

- **官方提供基础骨架，用户可以极其容易地魔改**
- 基础字段有明确语义和校验规则
- 用户可添加任意自定义字段，Mutsumi 会忽略但不删除它们
- 嵌套（子任务）理论上无限层级，TUI 默认渲染 3 层并可配置

### 5.2 最小任务对象

```json
{
  "id": "01JQ8X7K3M0000000000000000",
  "title": "重构 Auth 模块",
  "status": "pending",
  "scope": "day",
  "priority": "high",
  "tags": ["dev"],
  "children": []
}
```

### 5.3 ID 策略

采用 **UUIDv7**（时间排序的 UUID）：

- 天然按创建时间排序
- 无需中央协调即可保证唯一性
- Agent 和 TUI 都可以独立生成
- Python 3.12+ 原生支持（`uuid.uuid7()` — 或 fallback `uuid7` 库）

### 5.4 Scope：混合模式

`scope` 字段支持混合模式：

- 用户/Agent 可以**手动**设置 `scope: "day"` 作为静态标签
- 如果任务包含 `due_date` 字段，TUI **自动**根据当前日期推导归属视图
- 手动 `scope` 优先级高于自动推导
- 无 `scope` 且无 `due_date` 的任务归入 `inbox`

### 5.5 并发写入策略

| 场景 | 处理方式 |
|---|---|
| TUI 修改 → 写入 | 读取最新文件 → 修改目标字段 → 原子写入（临时文件 + rename） |
| Agent 修改 → watchdog | 检测文件变化 → 重新加载 → 重绘 TUI |
| 同时写入（极小概率） | Last Write Wins，TUI 下次 watchdog 触发时自愈 |
| JSON 格式损坏 | TUI 显示 error badge，保留上一次有效状态，不覆盖 |

原子写入流程：

```
TUI click → read tasks.json → modify in memory → write to .tasks.json.tmp → os.rename() → watchdog detects → re-render
```

`os.rename()` 在 POSIX 系统上是原子操作，可以防止读到半写状态的文件。

## 6. TUI 规格

> 详细交互规范见 `docs/specs/TUI_SPEC.md`

### 6.1 视图标签

```
┌─────────────────────────────────────────────┐
│  [Today] [Week] [Month] [Inbox]    mutsumi  │
├─────────────────────────────────────────────┤
│                                             │
│  ▼ HIGH                                     │
│  [ ] 重构 Auth 模块              dev   ★★★  │
│  [x] 修复缓存穿透 Bug           bugfix ★★★  │
│                                             │
│  ▼ NORMAL                                   │
│  [ ] 写周报                      life  ★★   │
│  [ ] Review PR #42               dev   ★★   │
│    └─ [ ] 检查类型安全                      │
│    └─ [x] 跑通测试                          │
│                                             │
│  ▼ LOW                                      │
│  [ ] 更新 README                 docs  ★    │
│                                             │
├─────────────────────────────────────────────┤
│  6 tasks · 1 done · 5 pending    🔇 quiet   │
└─────────────────────────────────────────────┘
```

### 6.2 TUI 中的增删改查

TUI 支持完整的增删改查，不依赖外部 Agent 即可独立使用：

| 操作 | 鼠标 | 键盘 |
|---|---|---|
| 创建 | 底部 [+New] 按钮 | `n` → 弹出输入框 |
| 查看 | 点击任务行展开详情 | `Enter` 展开 |
| 编辑 | 双击标题编辑 | `e` 编辑选中任务 |
| 删除 | 右键菜单 → Delete | `dd` (vim style) |
| 完成 | 点击 checkbox | `Space` |
| 移动 | 拖拽（v2） | `j/k` 上下移动 |

### 6.3 键位方案：多预设

提供多套预设键位方案，用户可在配置中切换或完全自定义：

- **vim**（默认）：`j/k/g/G/dd/Space/n/e/q`
- **emacs**：`C-n/C-p/C-d/C-Space`
- **arrow**：方向键 + Enter + Delete
- **custom**：用户在 `config.toml` 中自定义

### 6.4 主题系统

- 官方默认主题：**Monochrome Zen** — 极简黑白灰，accent 色为淡青（类似 Catppuccin 的 Teal）
- 内置可选：`monochrome`, `catppuccin-mocha`, `nord`, `dracula`
- 用户可在 `~/.config/mutsumi/themes/` 下添加自定义 `.toml` 主题文件
- 主题定义遵循 Textual CSS 变量映射

### 6.5 通知系统（可配置）

| 模式 | 行为 | 配置值 |
|---|---|---|
| **quiet** | 完全静默，底部状态栏只显示计数（默认） | `quiet` |
| **badge** | 到期任务在 TUI 内闪烁高亮 | `badge` |
| **bell** | 发送终端 bell（`\a`），由终端应用决定如何处理 | `bell` |
| **system** | 调用系统通知 API（macOS/Linux/Windows） | `system` |

## 7. CLI 规格

### 7.1 主要命令

```bash
# 启动 TUI（核心用法）
mutsumi                           # watch 当前目录的 tasks.json
mutsumi --watch ./project/tasks.json  # 指定路径
mutsumi --watch ~/a.json ~/b.json     # 多项目聚合

# CRUD（非 TUI 模式，供脚本/Agent 调用）
mutsumi add "修复登录 Bug" --priority high --scope day --tags dev,urgent
mutsumi list                      # 列出所有任务
mutsumi list --scope today        # 按 scope 过滤
mutsumi done <task-id>            # 标记完成
mutsumi edit <task-id> --title "新标题" --priority low
mutsumi rm <task-id>              # 删除

# 工具
mutsumi init                      # 在当前目录生成 tasks.json 模板
mutsumi validate                  # 校验 tasks.json 格式
mutsumi config --edit             # 打开配置文件
mutsumi schema                    # 输出 JSON Schema（供 Agent 参考）
```

### 7.2 多项目聚合

当 `--watch` 接收多个路径时，TUI 在 Tab 栏增加项目维度：

```
[Project A] [Project B] [All]  ·  [Today] [Week] [Month] [Inbox]
```

或者在任务列表中以分组方式展示来源项目。

## 8. Agent 集成协议

> 详细协议见 `docs/specs/AGENT_PROTOCOL.md`

### 8.1 写入协议 (Agent → Mutsumi)

Agent 只需要做一件事：**按照 schema 正确地写入 `tasks.json`。**

```
Agent reads tasks.json → modifies in memory → writes entire file back
```

要求：

- 必须保留不认识的自定义字段（不能丢弃）
- 写入后文件必须是合法 JSON
- 推荐使用原子写入（临时文件 + rename）

### 8.2 读取协议 (Mutsumi → Agent)

**Event Log 机制**：当用户在 TUI 中操作时，Mutsumi 可选地追加写入 `events.jsonl`：

```jsonl
{"ts":"2026-03-21T10:00:00Z","event":"task_completed","task_id":"01JQ8X7K3M...","title":"修复缓存 Bug"}
{"ts":"2026-03-21T10:01:00Z","event":"task_created","task_id":"01JQ8X7K4N...","title":"写单元测试"}
```

Agent 可以 `tail -f events.jsonl` 来感知用户在 TUI 侧的操作，实现双向通信。

### 8.3 Schema 校验行为

当 `tasks.json` 包含非法数据时：

| 错误类型 | Mutsumi 行为 |
|---|---|
| JSON 语法错误 | TUI 显示 error banner，保留上一次有效快照 |
| 未知 status 值 | TUI 在该任务上显示 warning badge |
| 缺少必填字段 (id/title) | 跳过该任务，TUI 底部显示 "1 task skipped" |
| 未知自定义字段 | 正常渲染，忽略自定义字段（不删除） |

同时，所有校验错误会写入 stderr 和 `~/.local/share/mutsumi/error.log`，Agent 可据此自我纠正。

## 9. 配置系统

### 9.1 配置路径

遵循 XDG Base Directory 规范（参考 starship、lazygit、bat 等主流 CLI 工具）：

```
~/.config/mutsumi/
├── config.toml          # 主配置
├── themes/
│   └── my-theme.toml    # 自定义主题
└── keys/
    └── my-keys.toml     # 自定义键位
```

平台特例：

- macOS：`~/Library/Application Support/mutsumi/`（也接受 `~/.config/mutsumi/`）
- Windows：`%APPDATA%\mutsumi\`

### 9.2 配置 Schema

```toml
[general]
language = "auto"          # "auto" | "en" | "zh" | "ja"
default_watch = "."        # 默认 watch 路径
default_scope = "day"      # 启动时默认显示的 Tab

[theme]
name = "monochrome"        # 内置主题名 或自定义主题文件名
accent_color = "#94e2d5"   # 可覆盖 accent 色

[keys]
preset = "vim"             # "vim" | "emacs" | "arrow" | "custom"

[notifications]
mode = "quiet"             # "quiet" | "badge" | "bell" | "system"

[data]
id_format = "uuidv7"      # "uuidv7" | "ulid" | "auto-increment"

[events]
enabled = true             # 是否写入 events.jsonl
path = "./events.jsonl"    # event log 路径
```

## 10. 国际化策略

### 10.1 实现

```
locales/
├── en.toml
├── zh.toml
└── ja.toml
```

```toml
# locales/en.toml
[tabs]
today = "Today"
week = "Week"
month = "Month"
inbox = "Inbox"

[status]
tasks = "{count} tasks"
done = "{count} done"
pending = "{count} pending"

[actions]
new_task = "New Task"
confirm_delete = "Delete this task?"
```

### 10.2 语言检测

优先级：`config.toml` 设置 > `$LANG` 环境变量 > fallback `en`

## 11. 分发

### 11.1 主要渠道

```bash
uv tool install mutsumi
```

用户无需预装 Python，`uv` 自动管理独立的 Python 环境。

### 11.2 次要渠道（MVP 之后）

| 渠道 | 优先级 | 备注 |
|---|---|---|
| `pipx` | P1 | uv 不可用时的 fallback |
| `brew` | P2 | macOS 用户习惯 |
| `nix` | P3 | NixOS 社区 |
| GitHub Releases | P1 | 直接下载 wheel |

## 12. 安全与隐私

- **零网络**：Mutsumi 不发起任何网络请求，不包含 telemetry
- **零云端**：所有数据存储在本地文件系统
- **文件权限**：tasks.json 建议权限 `0600`（仅用户读写）
- **无 eval**：永远不会执行 tasks.json 中的任何字段内容

## 13. 待定问题

以下问题留待后续 RFC 解决：

1. **插件系统** — 是否引入插件机制（如自定义视图组件）？
2. **同步** — 是否提供可选的跨设备同步（通过 Git 或 Syncthing）？
3. **任务模板** — 是否支持任务模板（如每日 standup 模板）？
4. **时间追踪** — 是否集成番茄钟/时间追踪？
5. **归档** — 已完成任务的归档策略（留在文件中 vs 移到 archive.json）？

---

## 附录 A：被否决的备选方案

| 备选方案 | 否决原因 |
|---|---|
| Electron GUI | 违反"极简"原则，启动慢，资源占用高 |
| SQLite 存储 | 对 Agent 不友好，无法直接 cat/编辑 |
| Rust TUI (ratatui) | 开发速度慢，Textual 的 CSS 样式更适合快速迭代 |
| 内置 Agent | 违反"解耦"原则，绑定模型就失去了通用性 |
| WebSocket 通信 | 过度工程化，文件系统就是最好的 IPC |
| Markdown tasks.md | 解析复杂度高，嵌套支持差，留作 v2 考虑 |

## 附录 B：命名与品牌

> 详见 `docs/BRAND.md`

**Mutsumi (若叶睦)** — 取自日语"睦"（和睦、亲近），寓意与用户的工作流和谐共处，不打扰、不教育、只是安静地在那里。
