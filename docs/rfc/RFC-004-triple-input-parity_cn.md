# RFC-004: 三端输入对等 — 键盘、鼠标、CLI

| 项目 | 内容 |
|------|------|
| RFC  | 004 |
| 标题 | 三端输入对等 — 键盘、鼠标、CLI |
| 状态 | Draft |
| 作者 | Wayne (ywh) |
| 创建 | 2026-03-21 |

> **[English Version](./RFC-004-triple-input-parity.md)** | **[日本語版](./RFC-004-triple-input-parity_ja.md)**

---

## 1. 摘要

Mutsumi 的每一个面向用户的功能，必须同时通过**键盘**、**鼠标**、**CLI** 三种表面可达。

### 1.1 设计原则

> **用户能用一种方式做到的事，三种方式都能做到。**

| 场景 | 主要输入 | 为什么需要另外两种 |
|------|---------|-------------------|
| 专注编码时 TUI 常驻 | 键盘 | 偶尔鼠标点一下比记快捷键快；CI/Agent 需要 CLI |
| tmux 分屏快速一瞥 | 鼠标 | 手不离鼠标时直接点；Agent 写脚本用 CLI |
| Agent/CI 自动化 | CLI | 人类复查时打开 TUI 用键盘/鼠标 |

---

## 2. 当前状态审计

### 2.1 完全对等 (3/3)

| 功能 | 键盘 | 鼠标 | CLI |
|------|------|------|-----|
| 切换完成状态 | `space` | 点击 checkbox | `mutsumi done <ID>` |
| 创建新任务 | `n` | Footer `[+New]` | `mutsumi add <TITLE>` |
| 编辑任务 | `e` | 详情面板 `[Edit]` | `mutsumi edit <ID>` |
| 删除任务 | `dd` | 详情面板 `[Delete]` | `mutsumi rm <ID>` |

### 2.2 仅键盘 — 缺鼠标和/或 CLI

| 功能 | 键盘 | 鼠标缺口 | CLI 缺口 |
|------|------|----------|----------|
| 优先级升降 | `+`/`-` | 需要按钮 | 需要 `mutsumi priority` |
| 任务排序 | `s` | 需要表头点击 | 需要 `mutsumi list --sort` |
| 搜索过滤 | `/` | Footer `[/Search]` ✅ | 需要 `mutsumi list --search` |
| 添加子任务 | `A` | 需要按钮 | 需要 `mutsumi add --parent` |
| 上下移动 | `J`/`K` | 需要拖拽/按钮 | 需要 `mutsumi move` |
| 复制粘贴 | `y`/`p`/`P` | 需要右键菜单 | 需要 `mutsumi clone` |
| 内联编辑 | `i` | 需要双击 | `edit --title` 已有 |
| 帮助屏 | `?` | 需要按钮 | `--help` 已有 |

### 2.3 仅 CLI — 无需 TUI 对等

| 功能 | CLI | 说明 |
|------|-----|------|
| `mutsumi init` | 生成模板 | 一次性操作 |
| `mutsumi validate` | 验证 schema | TUI 用 error banner 代替 |
| `mutsumi schema` | 输出 JSON Schema | 开发者/Agent 工具 |
| `mutsumi list` | 标准输出列表 | 管道/脚本用 |

---

## 3. 补齐方案

### 3.1 CLI 补齐 (P0)

| 新命令 | 示例 | 调用函数 |
|--------|------|----------|
| `mutsumi priority <ID> up\|down` | `mutsumi priority T001 up` | `cycle_priority()` |
| `mutsumi add --parent <ID>` | `mutsumi add "Fix" --parent T001` | `add_child_task()` |
| `mutsumi list --search <Q> --sort <F>` | `mutsumi list --search deploy --sort priority` | `sort_tasks()` |
| `mutsumi move <ID> up\|down` | `mutsumi move T001 up` | `reorder_task()` |
| `mutsumi clone <ID>` | `mutsumi clone T001` | `clone_task()` |

### 3.2 鼠标补齐 (P0)

| 补齐项 | 位置 | 交互 |
|--------|------|------|
| `[+Sub]` 按钮 | 详情面板 | 点击 → 打开 TaskForm(parent_id) |
| `[▲ Pri]` / `[▼ Pri]` 按钮 | 详情面板 | 点击 → cycle_priority |
| `[?Help]` 按钮 | Footer | 点击 → 打开 HelpScreen |
| 双击内联编辑 | TaskRow 标题区域 | 双击 → start_editing() |

### 3.3 延后项 (Phase 5)

- 拖拽排序 (Textual `on_mouse_move` + drop zones)
- 右键上下文菜单 (Textual 无原生支持，需自定义 overlay)
- 表头列点击排序

---

## 4. 设计约束

| 原则 | 说明 |
|------|------|
| CLI 无状态 | 每条命令读-改-写，无会话 |
| TUI 有状态 | 剪贴板、搜索词、排序在内存中 |
| 对等 ≠ 相同 UX | CLI `clone` ≈ TUI `y` 再 `p`，但 CLI 一条命令搞定 |
| CLI 输出管道友好 | 纯文本默认，未来支持 `--json` |
| 鼠标不添加视觉噪音 | 按钮在二级面板中，不破坏主界面简洁性 |

---

完整英文版本请参见 [RFC-004-triple-input-parity.md](RFC-004-triple-input-parity.md)。
