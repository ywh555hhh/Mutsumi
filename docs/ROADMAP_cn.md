# Mutsumi 开发路线图

> **[English Version](./ROADMAP.md)** | **[日本語版](./ROADMAP_ja.md)**

| 状态    | 动态文档                |
|---------|------------------------|
| 日期    | 2026-03-21             |

---

## 阶段概览

```
Phase 0          Phase 1          Phase 2          Phase 3          Phase 4
Foundations      Skeleton         Reactivity       CLI & Polish      Launch
────────────     ────────────     ────────────     ────────────     ────────────
docs & specs     static TUI       hot-reload       CLI CRUD         README
project setup    tab switching    file watcher     i18n             GIF demo
data model       task list        click → JSON     themes           Product Hunt
                 detail panel     JSON → re-draw   config system    community
```

---

## Phase 0：基础设施（当前）

**目标**：完成所有设计文档，建立项目骨架，零代码阶段。

- [x] 产品白皮书
- [x] RFC-001：核心架构
- [x] 数据契约规范 (`DATA_CONTRACT.md`)
- [x] Agent 集成协议 (`AGENT_PROTOCOL.md`)
- [x] TUI 规范 (`TUI_SPEC.md`)
- [x] 品牌标识 (`BRAND.md`)
- [x] 路线图（本文档）
- [ ] `uv init` 项目骨架
- [ ] `pyproject.toml` 依赖声明
- [ ] 示例 `tasks.json`（fixture）
- [ ] `CLAUDE.md` 项目级开发规范
- [ ] CI：GitHub Actions（lint + 类型检查）

**退出标准**：`uv run mutsumi` 能启动一个空白 Textual 窗口并正常退出。

---

## Phase 1：骨架

**目标**：画出静态 TUI，能读取 `tasks.json` 并渲染，但不响应外部变化。

- [ ] Textual App 基础框架 (`app.py`)
- [ ] Header 组件：Tab 切换（Today / Week / Month / Inbox）
- [ ] TaskList 组件：按优先级分组渲染
- [ ] TaskRow 组件：checkbox + 标题 + 标签 + 优先级星标
- [ ] Footer 组件：任务统计
- [ ] 数据层：Task schema 的 pydantic 模型
- [ ] 数据层：读取并解析 `tasks.json`
- [ ] 基础键盘导航：`j/k` 上/下，`q` 退出
- [ ] 子任务缩进展示（最多 3 层）
- [ ] 空白提示页

**退出标准**：手动创建一个 `tasks.json`，`uv run mutsumi` 能正确渲染所有任务。

---

## Phase 2：注入灵魂

**目标**：实现双向数据流 — 外部修改 JSON 自动重绘 + TUI 操作反写 JSON。

- [ ] watchdog 集成：监听 `tasks.json` 文件变化
- [ ] 防抖机制（100ms）
- [ ] 热重载：JSON 变化 → 无闪烁 TUI 重绘
- [ ] 鼠标点击 checkbox → 切换状态 → 反写 JSON
- [ ] 原子写入（临时文件 + `os.rename`）
- [ ] Schema 校验：非法 JSON → 错误提示横幅
- [ ] 错误状态：文件缺失/格式错误时优雅降级
- [ ] 详情面板：`Enter` 展开任务详情
- [ ] 端到端场景：Agent 在另一个终端写 JSON → TUI 自动刷新

**退出标准**：录制一个 10 秒 GIF：左边 Mutsumi 运行，右边手动修改 JSON，左边瞬间刷新。

---

## Phase 3：打磨

**目标**：完善 CLI 子命令、CRUD 交互、配置系统。

- [ ] TUI CRUD：`n` 新建 / `e` 编辑 / `dd` 删除
- [ ] CLI：`mutsumi add` / `list` / `done` / `rm` / `edit`
- [ ] CLI：`mutsumi init` — 生成模板 `tasks.json`
- [ ] CLI：`mutsumi validate` — 校验文件
- [ ] CLI：`mutsumi schema` — 输出 JSON Schema
- [ ] 配置系统：`~/.config/mutsumi/config.toml`
- [ ] 主题系统：4 个内置主题 + 自定义主题加载
- [ ] 键位预设方案：vim / emacs / 方向键
- [ ] 国际化：`en` + `zh` 双语支持
- [ ] 搜索：`/` 触发实时搜索过滤
- [ ] 事件日志：TUI 操作 → 追加到 `events.jsonl`
- [ ] 多项目：`--watch` 多路径聚合
- [ ] `mutsumi --version` / `--help`

**退出标准**：`uv tool install mutsumi` 后，新用户能在 2 分钟内跑通完整流程。

---

## Phase 4：包装上市

**目标**：打磨发布物料，冲刺 Product Hunt。

- [ ] README.md：极具煽动性的产品介绍
- [ ] README「Pro Workflow」章节（Typeless 语音工作流）
- [ ] README「Layout Gallery」章节（布局截图展示）
- [ ] 录制 Hero GIF：Claude Code + Mutsumi 分屏协作
- [ ] 录制 Bonus GIF：Typeless 语音 → Agent → Mutsumi 刷新
- [ ] Product Hunt 页面文案
- [ ] 发布到 PyPI
- [ ] GitHub Release v0.1.0
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
| 0.5.0   | Phase 4 完成 — Product Hunt 发布版本            |
| 1.0.0   | 社区反馈后的稳定版                               |
