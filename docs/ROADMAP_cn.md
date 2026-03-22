# Mutsumi 开发路线图

> **[English Version](./ROADMAP.md)** | **[日本語版](./ROADMAP_ja.md)**

| 状态    | 动态文档                |
|---------|------------------------|
| 日期    | 2026-03-22             |

---

## 阶段概览

```
Phase 0          Phase 1          Phase 2          Phase 3          Phase 3.5
Foundations      Skeleton         Reactivity       CLI & Polish     Friend Beta
────────────     ────────────     ────────────     ────────────     ────────────
docs & specs     static TUI       hot-reload       CLI CRUD         AGENT.md
project setup    tab switching    file watcher     i18n             setup command
data model       task list        click → JSON     themes           tmux scripts
                 detail panel     JSON → re-draw   config system    beta packaging

Phase 5          Phase 4
Multi-Source     Launch
────────────     ────────────
file rename      README
multi-source     GIF demo
project CLI      Product Hunt
tab redesign     community
dashboard
```

---

## Phase 0：基础设施 ✅

**目标**：完成所有设计文档，建立项目骨架，零代码阶段。

- [x] 产品白皮书
- [x] RFC-001：核心架构
- [x] 数据契约规范 (`DATA_CONTRACT.md`)
- [x] Agent 集成协议 (`AGENT_PROTOCOL.md`)
- [x] TUI 规范 (`TUI_SPEC.md`)
- [x] 品牌标识 (`BRAND.md`)
- [x] 路线图（本文档）
- [x] `uv init` 项目骨架
- [x] `pyproject.toml` 依赖声明
- [x] 示例 `tasks.json`（fixture）
- [x] `CLAUDE.md` 项目级开发规范
- [x] CI：GitHub Actions（lint + 类型检查）

**退出标准**：`uv run mutsumi` 能启动一个空白 Textual 窗口并正常退出。

---

## Phase 1：骨架 ✅

**目标**：画出静态 TUI，能读取 `tasks.json` 并渲染，但不响应外部变化。

- [x] Textual App 基础框架 (`app.py`)
- [x] Header 组件：Tab 切换（Today / Week / Month / Inbox）
- [x] TaskList 组件：按优先级分组渲染
- [x] TaskRow 组件：checkbox + 标题 + 标签 + 优先级星标
- [x] Footer 组件：任务统计
- [x] 数据层：Task schema 的 pydantic 模型
- [x] 数据层：读取并解析 `tasks.json`
- [x] 基础键盘导航：`j/k` 上/下，`q` 退出
- [x] 子任务缩进展示（最多 3 层）
- [x] 空白提示页

**退出标准**：手动创建一个 `tasks.json`，`uv run mutsumi` 能正确渲染所有任务。

---

## Phase 2：注入灵魂 ✅

**目标**：实现双向数据流 — 外部修改 JSON 自动重绘 + TUI 操作反写 JSON。

- [x] watchdog 集成：监听 `tasks.json` 文件变化
- [x] 防抖机制（100ms）
- [x] 热重载：JSON 变化 → 无闪烁 TUI 重绘
- [x] 鼠标点击 checkbox → 切换状态 → 反写 JSON
- [x] 原子写入（临时文件 + `os.rename`）
- [x] Schema 校验：非法 JSON → 错误提示横幅
- [x] 错误状态：文件缺失/格式错误时优雅降级
- [x] 详情面板：`Enter` 展开任务详情
- [x] 端到端场景：Agent 在另一个终端写 JSON → TUI 自动刷新

**退出标准**：录制一个 10 秒 GIF：左边 Mutsumi 运行，右边手动修改 JSON，左边瞬间刷新。

---

## Phase 3：打磨 ✅

**目标**：完善 CLI 子命令、CRUD 交互、配置系统。

- [x] TUI CRUD：`n` 新建 / `e` 编辑 / `dd` 删除
- [x] CLI：`mutsumi add` / `list` / `done` / `rm` / `edit`
- [x] CLI：`mutsumi init` — 生成模板 `tasks.json`
- [x] CLI：`mutsumi validate` — 校验文件
- [x] CLI：`mutsumi schema` — 输出 JSON Schema
- [x] 配置系统：`~/.config/mutsumi/config.toml`
- [x] 主题系统：4 个内置主题 + 自定义主题加载
- [x] 键位预设方案：vim / emacs / 方向键
- [x] 国际化：`en` + `zh` + `ja` 三语支持
- [x] 搜索：`/` 触发实时搜索过滤
- [x] 事件日志：TUI 操作 → 追加到 `events.jsonl`
- [x] 多项目：`--watch` 多路径聚合
- [x] `mutsumi --version` / `--help`

**退出标准**：`uv tool install mutsumi` 后，新用户能在 2 分钟内跑通完整流程。

---

## Phase 3.5：朋友内测 ✅

**目标**：准备小规模朋友内测 — 任何 Agent 都能 2 分钟内学会操控 Mutsumi。

- [x] `AGENT.md` — Agent 一页速查表（schema、CLI、JSON 协议）
- [x] `examples/` — 示例 `config.toml` 和 `tasks.json`
- [x] `mutsumi setup --agent` — 注入集成说明到 Agent 配置文件
- [x] `scripts/tmux-dev.sh` — 一条命令 tmux 分屏开发
- [x] `scripts/demo.sh` — 演示脚本展示实时刷新
- [x] 版本升级到 `0.4.0b1`
- [x] README：Terminal Integration 章节（tmux + iTerm2）
- [x] `pyproject.toml`：Beta classifier

**退出标准**：朋友 `uv tool install git+...` 后，运行 `mutsumi setup --agent claude-code`，2 分钟内开始使用。

---

## Phase 5：多源指挥中心 ✅（当前）

**目标**：将 Mutsumi 从单文件任务查看器升级为个人指挥中心 — 全局个人待办 + 多项目 Agent 仪表盘 + 聚合 Main tab。

- [x] **5a** — 文件重命名：`tasks.json` → `mutsumi.json`，保留向后兼容 fallback
- [x] **5f** — 配置迁移：`~/.config/mutsumi/` → `~/.mutsumi/` 统一目录
- [x] **5b** — 多源数据层：`SourceRegistry` 管理 N 个数据源
- [x] **5c** — 项目注册 CLI：`mutsumi project add/remove/list`
- [x] **5d** — Tab 重设计：动态 source tab + scope 子过滤器
- [x] **5e** — Main 仪表盘：跨所有源的聚合进度视图

**退出标准**：`uv run mutsumi` 注册多个项目后，Main tab 显示仪表盘，各源 tab 支持 scope 过滤，全部 239 个测试通过。

---

## Phase 4：包装上市（下一步）

**目标**：打磨发布物料，冲刺 Product Hunt。

- [ ] README.md：极具煽动性的产品介绍
- [ ] README「Pro Workflow」章节（Typeless 语音工作流）
- [ ] README「Layout Gallery」章节（布局截图展示）
- [ ] 录制 Hero GIF：Claude Code + Mutsumi 分屏协作
- [ ] 录制 Bonus GIF：Typeless 语音 → Agent → Mutsumi 刷新
- [ ] Product Hunt 页面文案
- [ ] 发布到 PyPI，包名 `mutsumi-tui`（`mutsumi` 已被占用）；CLI 命令仍为 `mutsumi`（通过 `[project.scripts]` 配置）；安装：`uv tool install mutsumi-tui` / `pip install mutsumi-tui`
- [ ] GitHub Release v0.5.0
- [ ] Hacker News / Reddit /r/commandline 发帖
- [ ] V2EX 发帖
- [ ] 社区模板征集：用户展示自己的 tmux/zellij 布局

**退出标准**：Product Hunt 页面上线，GitHub 获得首批 star。

---

## 未来（发布后的想法）

以下功能不在 MVP 范围内，仅作记录。

| 功能              | 描述                                              | 优先级 |
|-------------------|--------------------------------------------------|--------|
| 插件系统          | 用户可编写自定义视图组件                            | P2     |
| 任务模板          | 每日 standup / 周报模板                            | P2     |
| 归档              | 已完成任务自动归档到 `archive.json`                 | P2     |
| 番茄钟            | 内置番茄钟，关联任务                               | P3     |
| Git 同步          | `tasks.json` 自动 Git commit                      | P3     |
| 日历视图          | 按日历展示有 `due_date` 的任务                      | P3     |
| 仪表盘组件        | 完成率图表、每日趋势                               | P3     |
| Web 伴侣界面      | 只读 Web 界面（查看不操作）                         | P3     |
| Taskwarrior 导入  | 从 Taskwarrior 导入已有任务                        | P3     |
| Markdown 任务     | 支持 `tasks.md` 作为可选数据源                      | P3     |

---

## 版本策略

| 版本    | 里程碑                                          |
|---------|------------------------------------------------|
| 0.1.0   | Phase 1 完成 — 静态渲染可用                     |
| 0.2.0   | Phase 2 完成 — 热重载 + 交互可用                |
| 0.3.0   | Phase 3 完成 — CLI + 配置完整                   |
| 0.4.0b1 | Phase 3.5 完成 — 朋友内测                        |
| 0.6.0   | Phase 5 完成 — 多源指挥中心                       |
| 0.5.0   | Phase 4 完成 — Product Hunt 发布版本            |
| 1.0.0   | 社区反馈后的稳定版                               |
