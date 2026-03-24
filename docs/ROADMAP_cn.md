# Mutsumi 开发路线图

> **[English Version](./ROADMAP.md)** | **[日本語版](./ROADMAP_ja.md)**

| 状态 | 动态文档 |
|---|---|
| 日期 | 2026-03-23 |
| 当前 Beta | `1.0.0b1` |

---

## 产品状态

Mutsumi 当前处于 **`1.0.0b1` beta** 阶段。

这个 beta 中已经真实存在的内容：

- 规范任务文件：`mutsumi.json`
- 旧回退文件：`tasks.json`
- 默认键位预设：`arrows`
- multi-source hub：Main + Personal + project tabs
- 首次运行 onboarding
- skills-first agent setup

**尚未** shipped 的内容：

- 内置 calendar UI
- plugin system
- web companion

Calendar 现在通过 **RFC-009** 作为计划功能进行追踪。

---

## 阶段概览

```text
Phase 0   Foundations
Phase 1   Static TUI
Phase 2   Reactivity
Phase 3   CLI & Polish
Phase 3.5 Friend Beta
Phase 5   Multi-Source Hub
Phase 8   Out-of-Box Onboarding
Phase 9   Calendar View (planned)
Phase 10  Launch / GA polish
```

---

## Phase 0：基础 ✅

**目标：** 建立产品模型、规范文档和初始项目骨架。

- [x] 愿景与架构文档
- [x] RFC-001：核心架构
- [x] Data Contract 规范
- [x] Agent Integration Protocol
- [x] TUI 规范
- [x] 品牌识别
- [x] 路线图
- [x] `uv` 项目初始化
- [x] 示例 fixture task file
- [x] 项目开发规则（`CLAUDE.md`）
- [x] CI 基线

**退出标准：** `uv run mutsumi` 能干净地启动一个空白 Textual 窗口。

---

## Phase 1：Skeleton ✅

**目标：** 从本地 JSON 渲染一个静态任务面板。

- [x] Textual app shell
- [x] task list 渲染
- [x] priority grouping
- [x] task row UI
- [x] footer statistics
- [x] task schema models
- [x] file parsing
- [x] 基础键盘导航
- [x] 嵌套子任务渲染
- [x] 空状态

**退出标准：** 本地任务文件能在 TUI 中正确渲染。

---

## Phase 2：Reactivity ✅

**目标：** 让外部文件变化和本地交互都能正确更新面板。

- [x] watchdog 文件监听
- [x] debounce
- [x] hot reload
- [x] checkbox click → JSON write-back
- [x] atomic file writes
- [x] invalid JSON → error banner
- [x] graceful degradation
- [x] detail panel
- [x] 端到端 agent 写入 → TUI 刷新流程

**退出标准：** 当任务文件变化时，面板可以实时刷新。

---

## Phase 3：CLI & 打磨 ✅

**目标：** 提供可用的本地产品闭环，而不只是 demo UI。

- [x] TUI CRUD
- [x] CLI CRUD：`add`、`list`、`done`、`rm`、`edit`
- [x] `mutsumi init`
- [x] `mutsumi validate`
- [x] `mutsumi schema`
- [x] theme system
- [x] i18n（`en`、`zh`、`ja`）
- [x] config system
- [x] search
- [x] local event logging
- [x] version / help 输出

**退出标准：** 新用户可以快速安装并完成基础本地工作流。

---

## Phase 3.5：Friend Beta ✅

**目标：** 让早期测试者更容易理解 agent 驱动的使用方式。

- [x] `AGENT.md`
- [x] 示例 fixtures
- [x] `mutsumi setup --agent`
- [x] split-pane helper scripts
- [x] demo script
- [x] beta packaging 工作
- [x] 早期 beta 文档

**历史说明：** 这个阶段引入了更早的 friend-beta 版本线。当前产品已经超出那个阶段。

---

## Phase 5：Multi-Source Hub ✅

**目标：** 让 Mutsumi 从单项目查看器升级为多源指挥中心。

- [x] 将 `tasks.json` 重命名为 `mutsumi.json`，并保留兼容回退
- [x] 统一 home directory 到 `~/.mutsumi/`
- [x] 多源 registry 与 watchers
- [x] 项目注册 CLI
- [x] source-tab 重设计
- [x] Main dashboard 聚合

**退出标准：** Mutsumi 能在一个 UI 中聚合 personal 与多个 project task files。

---

## Phase 8：开箱 onboarding ✅

**目标：** 让 `mutsumi` 成为自然入口。

- [x] 首次运行 onboarding flow
- [x] 基于 onboarding 的偏好采集
- [x] 轻量项目 attach flow
- [x] skills-first agent integration path
- [x] 在适当时自动创建 Mutsumi 自有文件

**退出标准：** 首次启动成功，用户无需先学习复杂 setup graph。

---

## Phase 9：Calendar View（计划中）

**目标：** 为现有任务增加内置 calendar surface，用于按时间导航。

设计依据：

- [x] RFC-009：Calendar View

计划中的实现切片：

- [ ] Main 层 calendar mode
- [ ] month / agenda 基础
- [ ] 从日期 drill-down 到任务详情
- [ ] source-aware calendar aggregation
- [ ] 轻量日期驱动 create/edit flow
- [ ] 更丰富的 week/day 交互

范围说明：

- calendar 复用 `due_date`
- calendar 不引入第二套任务模型
- calendar 处于计划中，尚未在 `1.0.0b1` 中 shipped

---

## Phase 10：Launch / GA 打磨（下一步）

**目标：** 打磨产品、文档、打包与市场呈现，为更广泛发布做准备。

- [ ] 完成面向 beta/GA 路径的英文文档
- [ ] 录制打磨过的 demo 资产
- [ ] 发布 / 验证 `mutsumi-tui` 的 PyPI 安装流程
- [ ] 收紧 beta 测试清单与反馈闭环
- [ ] 在 GA 前补齐剩余 UX / 文档缺口
- [ ] 准备 launch copy 与 release materials

**退出标准：** 安装、onboarding、agent setup 与日常使用都足够连贯，可面向更广用户发布。

---

## 未来想法（GA 之后 / 未排期）

这些只是想法，不是已承诺的 roadmap。

| 功能 | 描述 | 优先级 |
|---|---|---|
| Plugin system | 用户自定义 widget 或扩展 | P2 |
| Task templates | 可复用的循环任务模板 | P2 |
| Archive | 将已完成任务移出活动文件 | P2 |
| Pomodoro timer | 关联任务的专注计时器 | P3 |
| Git sync helper | 可选的基于 Git 的任务文件工作流 | P3 |
| Dashboard widgets | 额外图表或汇总 | P3 |
| Web companion | 只读 Web 界面 | P3 |
| Taskwarrior import | 从现有系统导入 | P3 |
| Markdown tasks | 支持基于 Markdown 的 source format | P3 |

---

## 版本策略

| 版本 | 含义 |
|---|---|
| `0.1.x` | 静态渲染基线 |
| `0.2.x` | 响应式基线 |
| `0.3.x` | CLI / config 基线 |
| `0.4.0b1` | 更早的 friend-beta 里程碑 |
| `1.0.0b1` | 当前整合 beta 线 |
| `1.0.0` | beta 加固后的稳定版目标 |

---

## Beta 指南

对于当前周期，重要的事实源是：

- 当前 beta 版本：**`1.0.0b1`**
- 规范任务文件：**`mutsumi.json`**
- 默认 preset：**`arrows`**
- calendar 状态：**通过 RFC-009 规划中，尚未 shipped**
