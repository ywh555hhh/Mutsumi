# Mutsumi TUI 规范

| 版本 | 1.0 |
|---|---|
| 状态 | 草案 |
| 日期 | 2026-03-23 |

> **[English Version](./TUI_SPEC.md)** | **[日本語版](./TUI_SPEC_ja.md)**

---

## 1. 布局

### 1.1 默认布局

在多源模式下，Mutsumi 使用动态 source tabs 和第二层 scope filter。

```text
┌──────────────────────────────────────────────────────────────┐
│ [★ Main] [Personal] [saas-app] [docs-site]       mutsumi ♪  │
├──────────────────────────────────────────────────────────────┤
│ ★ Main │ [Today] [Week] [Month] [Inbox] [All]               │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  ▼ HIGH ───────────────────────────────────────────────      │
│  [ ] Refactor auth module                 dev,backend  ★★★   │
│  [x] Fix cache bug                        bugfix       ★★★   │
│                                                              │
│  ▼ NORMAL ─────────────────────────────────────────────      │
│  [ ] Write weekly report                  life         ★★    │
│  [ ] Review PR #42                        dev          ★★    │
│    └─ [ ] Check type safety                               │
│    └─ [x] Run tests                                        │
│                                                              │
├──────────────────────────────────────────────────────────────┤
│  6 tasks · 2 done · 4 pending                      🔇 quiet  │
└──────────────────────────────────────────────────────────────┘
```

### 1.2 Main dashboard 视图

当活动 source tab 为 `Main` 时，Mutsumi 显示的是聚合 dashboard，而不是可编辑任务列表。

```text
┌──────────────────────────────────────────────────────────────┐
│ [★ Main] [Personal] [saas-app] [docs-site]       mutsumi ♪  │
├──────────────────────────────────────────────────────────────┤
│                    ★ Main Dashboard                          │
│                                                              │
│  ★ Personal    3 pending                                     │
│  ████████░░░░░░░░░░ 40% (2/5)                                │
│    • Buy coffee beans                                        │
│    • Reply to advisor                                        │
│                                                              │
│  saas-app     5 pending                                      │
│  ███░░░░░░░░░░░░░░ 15% (1/7)                                 │
│    !!! • Fix token refresh                                   │
│    • Add rate limiting                                       │
└──────────────────────────────────────────────────────────────┘
```

### 1.3 响应式行为

| 终端宽度 | 行为 |
|---|---|
| `>= 80` 列 | 完整行：标题 + tags + priority |
| `60-79` 列 | 减少元数据 |
| `40-59` 列 | 最小行布局 |
| `< 40` 列 | 显示终端过窄警告 |

### 1.4 详情面板

选中任务后按 `Enter` 或点击标题，会打开详情面板。

详情面板显示：

- title
- status
- priority
- scope
- tags
- due date
- description
- child progress
- created / completed timestamps

同时提供可点击操作：

- `[Edit]`
- `[+Sub]`
- `[Delete]`
- `[x]` 关闭

---

## 2. 交互模型

### 2.1 鼠标

| 操作 | 行为 |
|---|---|
| 点击 checkbox | 切换 done 状态 |
| 点击任务行 | 选中行 |
| 点击任务标题 | 打开详情面板 |
| 点击 source tab | 切换数据源 |
| 点击 scope chip | 更改 scope filter |
| 点击 footer action | 打开任务表单、搜索或排序 |
| 点击 dashboard card | 跳转到对应 source tab |
| 点击详情面板中的 `[+Sub]` | 打开子任务表单 |

### 2.2 键盘预设

Mutsumi 内置三个 preset：

- `arrows` —— **默认**
- `vim`
- `emacs`

#### `arrows`（默认）

| 键位 | 操作 |
|---|---|
| `Up` / `Down` | 移动选中 |
| `Home` / `End` | 跳到顶部 / 底部 |
| `Left` / `Right` | 折叠 / 展开分组 |
| `Shift+Up` / `Shift+Down` | 上移 / 下移任务 |
| `Space` | 切换 done |
| `Enter` | 显示详情 |
| `n` | 新建任务 |
| `e` | 编辑任务 |
| `i` | 行内编辑标题 |
| `A` | 添加子任务 |
| `Tab` / `Shift+Tab` | 下一个 / 上一个 source tab |
| `1-9` | 跳转到编号 source tab |
| `f` | 循环切换 scope filter |
| `/` | 搜索 |
| `s` | 排序 |
| `?` | 显示帮助 |
| `q` | 退出 |

#### `vim`

| 键位 | 操作 |
|---|---|
| `j` / `k` | 移动选中 |
| `gg` / `G` | 顶部 / 底部 |
| `h` / `l` | 折叠 / 展开分组 |
| `J` / `K` | 下移 / 上移任务 |
| `dd` | 带确认删除 |
| `Space` | 切换 done |
| `Enter` | 显示详情 |
| `n` / `e` / `i` | 新建 / 编辑 / 行内编辑 |
| `A` | 添加子任务 |
| `Tab` / `Shift+Tab` | 下一个 / 上一个 source tab |
| `f` | 循环切换 scope filter |
| `/` | 搜索 |
| `?` | 帮助 |
| `q` | 退出 |

#### `emacs`

| 键位 | 操作 |
|---|---|
| `Ctrl+n` / `Ctrl+p` | 移动选中 |
| `Ctrl+a` / `Ctrl+e` | 顶部 / 底部 |
| `Ctrl+b` / `Ctrl+f` | 折叠 / 展开分组 |
| `Ctrl+Shift+n` / `Ctrl+Shift+p` | 移动任务 |
| `Space` | 切换 done |
| `Enter` | 显示详情 |
| `n` / `e` / `i` | 新建 / 编辑 / 行内编辑 |
| `A` | 添加子任务 |
| `Tab` / `Shift+Tab` | 下一个 / 上一个 source tab |
| `f` | 循环切换 scope filter |
| `/` | 搜索 |
| `?` | 帮助 |
| `Ctrl+q` | 退出 |

### 2.3 三输入等价

Mutsumi 遵循产品规则：关键操作既要能通过键盘和鼠标完成，相关核心任务变更在适用时也应提供 CLI 对应方式。

示例：

| 能力 | 键盘 | 鼠标 | CLI |
|---|---|---|---|
| 创建任务 | `n` | footer action | `mutsumi add` |
| 编辑任务 | `e` | `[Edit]` | `mutsumi edit` |
| 删除任务 | `dd` 或删除流程 | `[Delete]` | `mutsumi rm` |
| 切换 done | `Space` | checkbox | `mutsumi done` |
| 校验文件 | — | — | `mutsumi validate` |

---

## 3. 视图与过滤器

### 3.1 Source tabs

Source tabs 表示数据源，而不是时间范围。
示例：

- `Main`
- `Personal`
- 已注册项目，如 `saas-app`

### 3.2 Scope filter

在可编辑 tab 内，Mutsumi 显示第二层过滤器：

- `Today`
- `Week`
- `Month`
- `Inbox`
- `All`

`Main` dashboard 会隐藏 scope filter。

### 3.3 Scope 语义

Scope 过滤使用数据契约中的 effective scope：

```text
explicit scope > due_date auto-derivation > inbox
```

这意味着即使没有显式设置 scope，`due_date` 也会影响列表归类位置。

---

## 4. CRUD 行为

### 4.1 创建任务

触发方式：

- 键盘：`n`
- 鼠标：footer 新建任务操作

行为：

- 打开任务表单
- `title` 为必填
- 在适用时，scope 默认取当前过滤上下文
- 提交后以原子方式写文件

### 4.2 编辑任务

触发方式：

- 键盘：`e`
- 键盘行内：`i`
- 鼠标：详情面板中的 `[Edit]`

行为：

- 在内存中更新任务
- 原子写回
- 保留未知字段

### 4.3 删除任务

触发方式：

- 键盘删除流程
- 鼠标 `[Delete]`

行为：

- 需要确认
- 移除选中任务
- 原子写回

### 4.4 切换状态

触发方式：

- 键盘 `Space`
- 鼠标点击 checkbox

行为：

- `pending` → `done`：填写 `completed_at`
- `done` → `pending`：清除 `completed_at`
- 对循环任务的处理可能会根据 recurrence metadata 更新 due date

---

## 5. 热重载

### 5.1 文件监听行为

Mutsumi 会独立监听每一个已注册 source file。

```text
external save
   ↓
watchdog event
   ↓
debounce
   ↓
re-read active source(s)
   ↓
re-render TUI
```

### 5.2 多源行为

- 单源模式下，只监听一个文件
- 多源模式下，会监听所有已注册 source file
- dashboard 统计会聚合所有已加载 source 的任务

### 5.3 自写入抑制

Mutsumi 会在自己的原子写入附近抑制立即触发的自刷新，以避免冗余刷新。

---

## 6. 错误与空状态

### 6.1 非法 JSON

如果当前活动任务文件变成非法 JSON：

- Mutsumi 会显示错误横幅
- 应用不会崩溃
- 用户可以修复文件后继续使用

示例横幅：

```text
⚠ JSON is invalid — showing last valid state
```

### 6.2 文件缺失

如果活动文件尚不存在：

- UI 会显示可用的空状态
- 首次写入任务时可创建文件
- 新项目应创建 `mutsumi.json`

### 6.3 空状态

当当前视图中没有任务时，Mutsumi 会显示友好的空状态，并提供 `+ New Task` 操作。

文案应泛指当前任务流，不应假设只有 `tasks.json`。

---

## 7. 主题与配置

### 7.1 内置主题

- `monochrome-zen` —— 默认
- `solarized`
- `nord`
- `dracula`

### 7.2 配置主目录

首选的配置与个人数据主目录：

```text
~/.mutsumi/
```

旧配置位置仍可读取以保持兼容：

```text
~/.config/mutsumi/
```

### 7.3 键位配置

默认 preset 为：

```toml
keybindings = "arrows"
```

用户可以切换到 `vim` 或 `emacs`，并在配置中定义键位覆盖。

---

## 8. 日历准备度

本规范尚未定义日历 UI，但当前 TUI 语义有意保持与未来时间视图兼容。

现有基础包括：

- 任务模型中的 `due_date`
- 基于日期的 effective scope 推导
- 多源聚合
- dashboard/source 分离
- detail panel 下钻

未来的 calendar view 应建立在这些语义上，而不是发明第二套任务模型。

---

## 9. 当前 Beta 说明

对于当前 beta 线：

- 规范任务文件是 `mutsumi.json`
- 旧回退文件是 `tasks.json`
- 默认 preset 是 `arrows`
- multi-source dashboard 已是产品 surface 的一部分
- calendar 是计划中的能力，还不是已 shipped 的视图
