# Mutsumi 品牌标识

> **[English Version](./BRAND.md)** | **[日本語版](./BRAND_ja.md)**

| 状态 | 草案 |
|---|---|
| 日期 | 2026-03-21 |

---

## 1. 名称

### 1.1 主标识

**Mutsumi** —— 英文标识，全球通用。

### 1.2 日语名

**若叶睦** (わかば むつみ / Wakaba Mutsumi)

- **若叶 (Wakaba)** —— 年轻的叶子、新芽。象征新开始、轻盈感与克制的优雅。
- **睦 (Mutsumi)** —— 和睦、亲近。意味着与用户工作流和平共处。

### 1.3 中文名

**睦** —— 取自“和睦”，也在语音上轻轻联想到“默默”，表达一种安静、不打扰的工具气质。

### 1.4 标语

*Never lose a thread.*

### 1.5 一句话介绍

> 你的 threads，始终在视野里。一个由 AI agents 写入、由你随手 glance 的 terminal task board —— 一个按键 summon，再一个按键 dismiss。

---

## 2. 人格特质

Mutsumi 不是一个会大声争夺注意力的产品。她的人格是：

| 特质 | 描述 |
|---|---|
| **安静** | 静默运行。除非你明确要求，否则不会发起任何打扰性的通知。 |
| **在场** | 她一直都在。只需一眼，你就能看见全貌。 |
| **边缘感** | 她住在你余光的边缘，不抢主舞台，也不刻意隐藏，像墙上的时钟。 |
| **谦逊** | 她不会教你怎么管理任务。真正做决定的是你，以及你的 Agent。 |
| **可改造** | 她乐于被定制。你越是魔改她，她就越有生命力。 |
| **快速** | 瞬间启动。交互零延迟。退出不留痕迹。 |

如果 Mutsumi 是一个人，她会像这样：

> 安静地坐在你旁边，手里拿着一张写满你 threads 的便签。你看她一眼，她就把那张纸微微举高一点；你移开视线，她就继续平静地等在那里。

---

## 3. 视觉标识

### 3.1 Logo 概念

核心意象：**一片嫩叶与抽象任务列表的融合。**

方向 A —— 极简符号：
```
  ✓ 🌱
```
一个 checkmark 与一片叶子的组合，以极简线条表现。

方向 B —— ASCII Art（终端环境）：
```
  mutsumi ♪
```
纯文字加一个音符，象征和谐；非常适合终端。

方向 C —— 日式极简：
```
  睦
```
用一个汉字作为图标，以书法感呈现。

> 最终 logo 会在 Phase 4 由设计师完成。开发阶段使用方向 B（文字 logotype）。

### 3.2 调色板

#### 主色（Monochrome Zen —— 默认主题）

| Token | Hex | 用途 |
|---|---|---|
| `bg` | `#0f0f0f` | 主背景 |
| `surface` | `#1a1a1a` | 卡片/面板背景 |
| `border` | `#2a2a2a` | 分隔线 |
| `fg` | `#e0e0e0` | 主文本 |
| `fg-muted` | `#666666` | 次级文本 |
| `accent` | `#5de4c7` | 强调色（淡青/薄荷绿） |
| `danger` | `#e06c75` | 错误 / 高优先级 |
| `warning` | `#e5c07b` | 警告 |
| `success` | `#98c379` | 完成状态 |

#### 设计理由

- 用深灰作为底色，降低视觉噪音，适合长时间终端使用。
- 强调色选薄荷绿（`#5de4c7`），在深背景上对比足够，但不刺眼。
- 灵感来源：Catppuccin Teal + Vercel 的黑白极简美学。
- 整体气质：**安静但不沉闷，极简但不廉价。**

### 3.3 字体

终端中的字体选择由用户自己的 terminal emulator 决定。推荐：

- **JetBrains Mono** / **Cascadia Code** / **Fira Code** —— 支持 ligature 的等宽字体
- TUI 内不使用非等宽字符（emoji 除外，且应谨慎使用）

### 3.4 图标系统

TUI 图标使用 Unicode / Nerd Font 符号：

| 概念 | 符号 | 回退（无 Nerd Font） |
|---|---|---|
| Pending | `[ ]` | `[ ]` |
| Done | `[x]` | `[x]` |
| High | `★★★` | `!!!` |
| Normal | `★★` | `!!` |
| Low | `★` | `!` |
| Expand | `▶` | `>` |
| Collapse | `▼` | `v` |
| Search | `🔍` | `/` |
| Error | `⚠` | `!` |
| New | `[+]` | `[+]` |

> Mutsumi 不要求 Nerd Font。所有图标都提供 ASCII 回退。

---

## 4. 语气与文风

### 4.1 文档语气

- **简洁直接**：不要花哨修辞，直达重点。
- **技术精确**：API 文档遵循标准 Reference 形式。
- **偶尔温暖**：README 里允许一点人格化表达（比如 “Mutsumi 在那里等你”）。
- **绝不居高临下**：避免 “简单地”“只要”“很容易” 之类的措辞。

### 4.2 README 语气

README 是 Product Hunt 的核心叙事，这里欢迎更多一点 personality：

```
Good: "Mutsumi watches your mutsumi.json and re-renders instantly."
Bad:  "Mutsumi is a revolutionary AI-powered task management solution."

Good: "Let your agent write the JSON. Mutsumi handles the rest."
Bad:  "Simply configure your preferred AI agent integration endpoint."
```

### 4.3 错误信息

```
Good: "mutsumi.json has errors. Showing last valid state."
Bad:  "FATAL: Invalid JSON format detected in configuration file."

Good: "Task 'Fix auth' is missing an ID. Skipped."
Bad:  "ValidationError: Required field 'id' not found in task object at index 3."
```

---

## 5. 社区身份

### 5.1 GitHub 形象

- **仓库**：`github.com/<user>/mutsumi`
- **Topics**：`tui`, `task-manager`, `terminal`, `python`, `textual`, `cli`, `productivity`, `agent`
- **描述**："A silent TUI task board that watches your JSON. Agent-agnostic. Layout-agnostic. Zero friction."

### 5.2 社交标签

- `#mutsumi`
- `#terminalproductivity`
- `#tuiapps`

### 5.3 社区仪式

鼓励用户晒自己的 workspace layout，并形成一个 “Layout Gallery”：

- GitHub Discussions 分区：“Show your layout”
- 标准截图模板：`tmux` / `zellij` 配置 + 终端截图
- 被选中的布局会进入 README 的 Gallery 部分

---

## 6. 命名约定（代码层）

### 6.1 包名

```
PyPI: mutsumi
Import: import mutsumi
CLI: mutsumi
```

### 6.2 内部模块命名

```
mutsumi/
├── app.py          # Textual App entry point
├── tui/            # TUI widgets
├── cli/            # CLI commands
├── core/           # Data layer (models, file I/O)
├── config/         # Config loading
├── i18n/           # Internationalization
└── themes/         # Built-in themes
```

### 6.3 Commit 前缀约定

```
feat:     New feature
fix:      Bug fix
docs:     Documentation
style:    Formatting/themes
refactor: Internal refactor
test:     Add/update tests
chore:    Tooling / build / housekeeping
```

---

## 7. 不是什么

Mutsumi 不是：

- 吵闹的 productivity mascot
- 全都要的 project management suite
- 依赖云端、账号体系和同步服务的系统
- 一个“AI 替你做一切”的黑盒

她是一个安静的 thread-keeper。
