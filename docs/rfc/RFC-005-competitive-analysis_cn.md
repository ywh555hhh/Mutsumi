# RFC-005: 竞品分析 — 借鉴了什么，保留了什么

| 项目 | 内容 |
|------|------|
| RFC  | 005 |
| 标题 | 竞品分析 — 借鉴了什么，保留了什么 |
| 状态 | Draft |
| 作者 | Wayne (ywh) |
| 创建 | 2026-03-21 |

> **[English Version](./RFC-005-competitive-analysis.md)** | **[日本語版](./RFC-005-competitive-analysis_ja.md)**

---

## 1. 摘要

Mutsumi 的 UX 不是凭空发明的。本 RFC 记录我们系统性分析了哪些竞品、借鉴了什么、拒绝了什么、以及每个决策的理由。

---

## 2. 竞品概览

| 产品 | 语言 | 存储 | 特色 |
|------|------|------|------|
| **Dooit** | Python | SQLite | 插件系统、紧迫度评分、Python 配置 |
| **Taskwarrior** | C++ | 平面文件 | 40+ 报表、UDA、hooks、同步 |
| **Ultralist** | Go | JSON | 自然语言输入 |
| **dstask** | Go | Git 仓库 | Git 原生同步 |
| **Calcure** | Python | JSON/iCal | 日历+任务混合 |

---

## 3. 借鉴清单 ✅

### 3.1 来自 Dooit

| 特性 | Dooit 方案 | Mutsumi 适配 |
|------|-----------|-------------|
| 多键序列引擎 | Key buffer + prefix matching | `KeyManager` 类，与 Textual Binding 共存 |
| 内联确认栏 | 底部 1 行 `"Delete 'xxx'? [y/N]"` | `ConfirmBar` widget，`dd` 触发 |
| 级联完成 | SQLite trigger | `cascade_toggle_status()` 纯 Python 实现 |
| 优先级快捷键 | `+`/`-` 循环 urgency | `+`/`-` 循环 `low→normal→high` 枚举 |
| 任务排序 | 排序菜单 | `SortBar` ModalScreen，h/l/j/k 导航 |
| 帮助屏 | 硬编码帮助文本 | 从 Binding + KeySequence 自动生成 |
| 键盘重排序 | shift+j/k | `J`/`K` (vim), `ctrl+shift+n/p` (emacs), `shift+↑/↓` (arrows) |

### 3.2 来自 Taskwarrior

| 特性 | 借鉴程度 |
|------|---------|
| CLI 每个操作一条命令 | 🔄 转化 — 我们是 TUI 优先，CLI 为辅 |
| UDA 自定义字段 | 🔄 转化 — 用 Pydantic `extra="allow"` 替代 |

### 3.3 来自 Vim

| 特性 | 说明 |
|------|------|
| `j`/`k` 导航 | vim 预设复用肌肉记忆 |
| `dd` 删除 | 多键序列 via KeyManager |
| `gg` 跳顶 | 多键序列 via KeyManager |
| `y`/`p` 复制粘贴 | 内部剪贴板 |
| `i` 编辑 | 内联编辑模式（仅限单行） |

---

## 4. 拒绝清单 🚫

| 被拒方案 | 来源 | 拒绝理由 |
|----------|------|----------|
| SQLite 存储 | Dooit | JSON 对 AI Agent 和人类都透明，可 `cat`/`jq`/git diff |
| Python 配置文件 | Dooit | 远程代码执行风险；TOML 声明式且安全 |
| 插件系统 | Dooit | 复杂度过高；Agent 写 JSON 即"插件" |
| 无界整数紧迫度 | Dooit | 认知负担；3 级枚举覆盖 99% 场景 |
| pyperclip 系统剪贴板 | Dooit | 额外依赖 + 平台兼容问题；内部剪贴板足够 |
| 双栏 Workspace 布局 | Dooit | 违反 Layout Agnostic 原则 |
| 同步服务器 | Taskwarrior | 违反 Local Only 原则 |
| Hook 脚本 | Taskwarrior | 用 events.jsonl 事件日志替代 |
| 40+ 报表类型 | Taskwarrior | 过度工程；Mutsumi 是安静仪表盘 |
| 自然语言日期解析 | Todoist/Ultralist | 跨地区歧义；ISO 8601 无歧义 |
| 云同步 / 账户 | Todoist/Notion | 100% 本地，无网络调用 |

---

## 5. 保留清单 📌 (Mutsumi 原创)

| 设计 | 说明 |
|------|------|
| **JSON 作为 Model** | AI Agent 的通用语言，人类可读，git 可 diff |
| **Agent Agnostic MVC 架构** | Mutsumi=View, Agent=Controller, tasks.json=Model |
| **TOML 配置** | 安全、可注释、有嵌套支持、stdlib 原生 |
| **三套键位预设** | vim/emacs/arrows — 不强迫用户改变肌肉记忆 |
| **`extra="allow"` 未知字段** | 零仪式地支持自定义字段（effort、sprint 等） |
| **Scope 混合解析** | 手动 scope > due_date 自动推导 > 兜底 inbox |
| **搜索即暗淡（不隐藏）** | 保留空间上下文，仪表盘不跳动 |
| **三语 i18n** | TUI 运行时（TOML locale）+ 文档（三语 Markdown） |
| **三端输入对等** | 键盘 + 鼠标 + CLI — 见 RFC-004 |

---

## 6. 核心教训

1. **偷交互，不偷架构** — Dooit 的 UX 极好，但 SQLite + Python config 服务不同目标
2. **`extra="allow"` 是秘密武器** — 一行配置消灭了 UDA 声明、Schema 迁移、插件钩子
3. **三端对等是独特定位** — 竞品集中没有任何一个同时满足键盘+鼠标+CLI
4. **「暗淡」优于「隐藏」** — 搜索时保留空间感，符合「安静仪表盘」哲学

---

完整英文版本请参见 [RFC-005-competitive-analysis.md](RFC-005-competitive-analysis.md)。
