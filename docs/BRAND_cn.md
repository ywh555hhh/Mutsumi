# Mutsumi 品牌标识

> **[English Version](./BRAND.md)** | **[日本語版](./BRAND_ja.md)**

| 状态    | 草案                 |
|---------|---------------------|
| 日期    | 2026-03-21          |

---

## 1. 名称

### 1.1 主标识

**Mutsumi** — 英文标识，全球通用。

### 1.2 日语名

**若叶睦** (わかば むつみ / Wakaba Mutsumi)

- **若叶 (Wakaba)** — 新芽、嫩叶。象征新生、轻盈、不张扬。
- **睦 (Mutsumi)** — 和睦、亲近。寓意与用户的工作流和谐共处。

### 1.3 中文名

**睦** — 取"和睦"之意，也暗含"默默"的谐音（静默型工具）。

### 1.4 标语

*为多线程的你打造的静默任务外脑。*

### 1.5 一句话介绍

> 一个极简的 TUI 任务看板，监听你的 JSON，绝不碍事。
> 让你的 AI agent 做大脑 — Mutsumi 只负责做眼睛。

---

## 2. 人格特质

Mutsumi 不是一个高声呐喊的产品。她的人格是：

| 特质         | 描述                                                    |
|-------------|--------------------------------------------------------|
| **安静**     | 静默运行，不主动打扰，不发通知（除非你要求）               |
| **在场**     | 她一直在那里，只要你看一眼就能获取信息                    |
| **谦逊**     | 她不教你怎么管理任务，你（和你的 Agent）才是主人            |
| **可改造**   | 她乐于被改造，越被魔改越有活力                            |
| **快速**     | 启动瞬间完成，操作零延迟，退出无残留                      |

如果 Mutsumi 是一个人，她是那种：

> 安静坐在你旁边，手里拿着一张写满了你待办事项的便签纸，你看她一眼她就把纸举高一点，你不看她她就安安静静等着。

---

## 3. 视觉标识

### 3.1 Logo 概念

核心意象：**一片嫩叶 + 任务列表的抽象融合。**

方向 A — 极简符号：
```
  ✓ 🌱
```
一个 checkmark 和一片叶子的组合，极简线条。

方向 B — ASCII Art（终端环境）：
```
  mutsumi ♪
```
纯文字 + 一个音符符号（表示和谐），适合终端显示。

方向 C — 日式极简：
```
  睦
```
单个汉字作为图标，书法风格。

> 最终 logo 将在 Phase 4 由设计师完成。当前开发阶段使用方向 B 的文字标识。

### 3.2 调色板

#### 主色调（Monochrome Zen — 默认主题配色）

| Token        | Hex       | 用途                        |
|--------------|-----------|----------------------------|
| `bg`         | `#0f0f0f` | 主背景                     |
| `surface`    | `#1a1a1a` | 卡片/面板背景               |
| `border`     | `#2a2a2a` | 分隔线                     |
| `fg`         | `#e0e0e0` | 主文字                     |
| `fg-muted`   | `#666666` | 次要文字                   |
| `accent`     | `#5de4c7` | 强调色（淡青/薄荷绿）       |
| `danger`     | `#e06c75` | 错误/高优先级               |
| `warning`    | `#e5c07b` | 警告                       |
| `success`    | `#98c379` | 完成状态                   |

#### 设计理念

- 以黑灰为主底，减少视觉噪音，适应终端长时间使用。
- accent 色选用薄荷绿（`#5de4c7`），在暗色背景上辨识度高且不刺眼。
- 灵感来源：Catppuccin Teal + Vercel 的黑白极简美学。
- 整体气质：**安静但不沉闷，极简但不寒酸。**

### 3.3 字体

终端环境下字体由用户的终端模拟器决定。推荐：

- **JetBrains Mono** / **Cascadia Code** / **Fira Code** — 等宽字体，连字支持
- TUI 内不使用非等宽字符（emoji 除外，且 emoji 使用应保守）

### 3.4 图标

TUI 中的图标使用 Unicode / Nerd Font 符号：

| 概念         | 符号    | 回退方案（无 Nerd Font）                |
|--------------|---------|----------------------------------------|
| 待办         | `[ ]`   | `[ ]`                                  |
| 完成         | `[x]`   | `[x]`                                  |
| 高优先级     | `★★★`   | `!!!`                                  |
| 普通         | `★★`    | `!!`                                   |
| 低优先级     | `★`     | `!`                                    |
| 展开         | `▶`     | `>`                                    |
| 折叠         | `▼`     | `v`                                    |
| 搜索         | `🔍`    | `/`                                    |
| 错误         | `⚠`     | `!`                                    |
| 新建         | `[+]`   | `[+]`                                  |

> Mutsumi 不强制要求 Nerd Font。所有图标均有 ASCII 回退方案。

---

## 4. 语气与风格

### 4.1 文档语气

- **简洁直接**：不用花哨的修饰，直奔主题。
- **技术精准**：API 文档用标准的 Reference 格式。
- **偶尔温暖**：README 中允许一点人格化叙述（"Mutsumi 在那里等你"）。
- **不居高临下**：不用"简单地""只需要""很容易"这类词。

### 4.2 README 语气

README 是 Product Hunt 的核心叙事，允许更有个性：

```
Good: "Mutsumi watches your tasks.json and re-renders instantly."
Bad:  "Mutsumi is a revolutionary AI-powered task management solution."

Good: "Let your agent write the JSON. Mutsumi handles the rest."
Bad:  "Simply configure your preferred AI agent integration endpoint."
```

### 4.3 错误信息

```
Good: "tasks.json has errors. Showing last valid state."
Bad:  "FATAL: Invalid JSON format detected in configuration file."

Good: "Task 'Fix auth' is missing an ID. Skipped."
Bad:  "ValidationError: Required field 'id' not found in task object at index 3."
```

---

## 5. 社区形象

### 5.1 GitHub 信息

- **仓库**: `github.com/<user>/mutsumi`
- **Topics**: `tui`, `task-manager`, `terminal`, `python`, `textual`, `cli`, `productivity`, `agent`
- **描述**: "A silent TUI task board that watches your JSON. Agent-agnostic. Layout-agnostic. Zero friction."

### 5.2 社交标签

- `#mutsumi`
- `#terminalproductivity`
- `#tuiapps`

### 5.3 社区仪式

鼓励用户晒自己的工作区布局，建立 "Layout Gallery"：

- GitHub Discussions 专区："Show your layout"
- 标准化截图模板：`tmux` / `zellij` 配置 + 终端截图
- 精选布局收录进 README 的 Gallery 章节

---

## 6. 命名规范（代码层面）

### 6.1 包名

```
PyPI: mutsumi
Import: import mutsumi
CLI: mutsumi
```

### 6.2 内部模块命名

```
mutsumi/
├── app.py          # Textual App 入口
├── tui/            # TUI 组件
├── cli/            # CLI 命令
├── core/           # 数据层（模型、文件 I/O）
├── config/         # 配置加载
├── i18n/           # 多语言
└── themes/         # 内置主题
```

### 6.3 提交前缀约定

```
feat:     新功能
fix:      Bug 修复
docs:     文档
style:    格式/主题
refactor: 重构
test:     测试
chore:    构建/工具
i18n:     国际化
```
