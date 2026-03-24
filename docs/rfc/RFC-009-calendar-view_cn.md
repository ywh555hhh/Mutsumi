# RFC-009：Calendar View —— 面向多源任务的时间导航

> **[English Version](./RFC-009-calendar-view.md)** | **[日本語版](./RFC-009-calendar-view_ja.md)**

| 字段 | 值 |
|---|---|
| **RFC** | 009 |
| **标题** | Calendar View —— 面向多源任务的时间导航 |
| **状态** | Draft |
| **作者** | Wayne (ywh) |
| **创建时间** | 2026-03-23 |

---

## 1. 摘要

Mutsumi 已经具备构建 calendar 所需的原始语义基础：

- 任务上的 `due_date`
- 可由日期推导出的 effective scope
- 聚合多个来源的 Main dashboard
- 用于聚焦编辑的 source tabs
- 用于深入查看的 detail panel

真正缺失的是**时间视图本身**。

本 RFC 提议把内建的 **calendar view** 作为一项一等产品能力加入 Mutsumi。calendar 不应引入第二套任务系统，也不应引入独立的数据模型。相反，它应当以日期为轴，为现有任务模型提供一种新的导航方式。

calendar 很自然地属于 **Main/dashboard layer**：它是一个跨来源、面向时间的视图，与现有面向列表的 source tabs 形成互补。

长期目标是提供一个适合任务规划与回顾的完整 calendar 体验。不过在实现上，应该分阶段落地。

---

## 2. 动机

### 2.1 当前的缺口

Mutsumi 其实已经能回答这样的问题：

- 今天到期的是什么？
- 这周的任务有哪些？
- 这个月的任务有哪些？

但它是通过**列表 bucket**来回答这些问题，而不是通过真正的时间地图。

这意味着用户虽然能按 `Today`、`Week`、`Month` 过滤任务，却仍然无法：

- 一眼看出任务在不同日期上的分布
- 看见哪些日子稀疏、哪些日子拥挤
- 从某个具体日期跳到对应任务
- 用视觉方式理解调度压力

### 2.2 为什么这对 todo 产品很重要

没有 calendar 的 todo 系统，会迫使用户在脑中把列表里的截止时间投影到时间轴上。

对于很小的列表，这还能接受。但当用户同时 juggling：

- personal tasks
- 一个或多个活跃项目
- agent 持续写入、不断变化的 backlog
- 横跨未来几天或几周的 due dates

问题就会变得更严重。

对于 Mutsumi 的目标用户——一个本来就在多线程中生活的人——真正缺少的并不是更多任务元数据，而是**一个更好的时间表面**。

### 2.3 为什么 Main/dashboard 是合适的位置

当前架构已经区分了：

- **Main** —— 跨来源摘要
- **source tabs** —— 聚焦编辑与检查

calendar 本质上是一个**跨来源的时间导航器**。因此，它比起替换 source-local task lists，更适合放在 Main 层里。

---

## 3. Goals

| Goal | Description |
|---|---|
| 多源时间视图 | 在一个 calendar surface 中同时展示 personal + project sources 的带日期任务 |
| 不引入新的任务模型 | 复用现有的 `Task`、`due_date`、`scope` 和 source 语义 |
| 键盘 + 鼠标等价 | 日期导航与 drill-down 必须同时支持两种输入方式 |
| 顺滑 drill-down | 用户应该能无困惑地从日期 → 任务 → 详情/source tab |
| 保持列表视图的价值 | calendar 是对现有列表视图的补充，而不是替代 |
| 面向未来的完整目标 | 即便实现分阶段落地，设计上也要面向 month/week/day/agenda 全能力 |

---

## 4. Non-goals

本 RFC **不**提议：

- 网络 calendar 同步
- Google Calendar / iCal 集成
- 单独的 calendar 专用 JSON 文件
- 把 Mutsumi 变成会议或事件调度器
- 放弃当前基于列表的 source tabs
- 在第一版 calendar 支持中修改核心任务 schema

---

## 5. 数据语义

### 5.1 Calendar anchor

calendar 以 **`due_date`** 作为主要时间锚点。

如果一个任务没有 `due_date`，它就没有精确的 calendar 落点，因此默认不应出现在某个具体日期格子里。

### 5.2 与 `scope` 的关系

`scope` 仍然是规划 bucket，而不是规范性的 calendar 坐标。

解析规则保持不变：

```text
explicit scope > due_date auto-derivation > inbox
```

这意味着：

- list views 继续使用 effective scope
- calendar views 在存在 `due_date` 时使用 `due_date`
- calendar 不应把 `scope` 重新解释为缺失日期时的替代物

### 5.3 没有 `due_date` 的任务

没有 `due_date` 的任务：

- 仍然会出现在 list views 和 dashboard summaries 中
- 默认不会出现在日期网格中
- 在后续阶段里，可以出现在辅助性的 “undated” agenda/sidebar 中

### 5.4 无效日期

如果 `due_date` 格式错误：

- calendar view 不应因此崩溃
- 该任务不应被放入具体日期
- 现有的 graceful-degradation 路径仍然是权威行为

### 5.5 逾期任务

逾期任务仍然锚定在它原本的 `due_date` 上，但 calendar 应该清楚地表达出它已经 overdue。

例子：

- 强调色
- overdue badge
- 在 month view 中使用特殊密度标记

### 5.6 重复任务

Mutsumi 已经在 writer layer 支持 recurrence metadata。calendar 应该把 recurrence 视为任务生成/更新层面的责任，而不是引入第二套渲染模型。

这意味着：

- calendar 读取当前任务状态
- calendar 不会独立展开 recurrence rules，生成幻影事件
- 未来可以在此基础上逐步叠加更高级的 recurrence 可视化

### 5.7 多源语义

calendar entries 必须保留 source identity。

calendar 中渲染的每个任务都应该仍然知道：

- 它来自哪个 source
- 它是 personal 还是 project-owned
- 如何跳回对应的 source tab 或 detail view

---

## 6. 信息架构

### 6.1 放置位置

calendar 应作为一种 **Main-layer view mode** 被引入，而不是替代 source tabs。

推荐结构：

```text
[★ Main] [Personal] [project-a] [project-b]
          └─ Main view modes: Dashboard / Calendar
```

可能的 UI 形式：

- Main 内部的 segmented control
- 在 Main 激活时用键盘切换
- 在聚焦 Main 时使用 footer action / header action

### 6.2 为什么不是顶层 tab

单独做一个顶层 `Calendar` tab 当然可行，但更弱，因为它会把 Main 这个心智模型拆成两个相互竞争的聚合表面。

Main 应继续作为跨来源层，包含：

- summary/dashboard view
- time/calendar view

### 6.3 与 source tabs 的关系

source tabs 仍然是直接 task CRUD 与 source-scoped filtering 的地方。

calendar 作为导航与规划表面，可以跳转到：

- source tab
- detail panel
- 未来的 inline quick-create/edit flows

---

## 7. 交互模型

### 7.1 核心交互

calendar 必须支持：

1. 在日期之间导航
2. 查看某一天上的任务
3. 打开任务详情
4. 跳转到 source 上下文
5. 切换 calendar 粒度 / 模式

### 7.2 键盘要求

所需键盘支持示例：

| Action | Keyboard expectation |
|---|---|
| 按天移动 | arrow keys 或与当前 preset 对应的等价导航 |
| 按周移动 | up/down 或 week-jump keys |
| 打开选中日期 | `Enter` |
| 切换 calendar mode | 专用快捷键或可聚焦切换控件 |
| 返回 list/dashboard | `Escape` 或显式 back action |
| 跳入 source tab | 在选中任务上使用 `Enter` / secondary action |

具体按键仍应遵循当前 preset 哲学：

- `arrows` 仍是默认值
- `vim` 和 `emacs` 仍然是 opt-in

### 7.3 鼠标要求

所需鼠标支持示例：

| Action | Mouse expectation |
|---|---|
| 选择日期 | 点击日期格子 |
| 打开日期内容 | 点击日期格子或 task chip |
| 打开任务详情 | 点击 task chip |
| 切换模式 | 点击 segmented control / tab |
| 跳转到 source | 点击 source badge 或相应 action |

### 7.4 Triple input parity

calendar 必须遵守 RFC-004 的原则。

如果用户能通过一种交互表面抵达某个 calendar 动作，就不应该被困在那里面。

例如：

- 选择日期不能只支持鼠标
- 切换 calendar mode 不能只支持键盘
- source drill-down 只有在合理的时候才需要对应 CLI-adjacent 解释，但交互式导航本身仍然是 TUI 特有的

---

## 8. View Modes（完整目标）

产品目标是一个完整的 calendar system，即便落地要分阶段进行。

### 8.1 Month view

最适合：

- 扫描密度
- 观察跨周分布
- 识别过载日期

预期行为：

- 日期网格
- 每个格子的任务摘要或密度指标
- 对拥挤日期的溢出处理

### 8.2 Week view

最适合：

- 操作型规划
- 更紧凑地查看未来 7 天
- 比较不同来源的近期承诺

### 8.3 Day view

最适合：

- 聚焦执行
- 以更丰富的细节查看单日任务

### 8.4 Agenda view

最适合：

- 按时间顺序阅读带日期任务
- 低密度终端布局
- 可访问性 / 窄终端 fallback

---

## 9. 功能矩阵（产品目标）

| Capability | Target state |
|---|---|
| Month / week / day / agenda | Supported |
| 多源聚合 | Supported |
| Source badges | Supported |
| 日期 drill-down | Supported |
| Detail panel integration | Supported |
| 在日期上快速创建 | Supported |
| 从日期快速编辑 | Supported |
| 拖拽重新安排日期 | Supported later |
| 逾期可视化 | Supported |
| Undated task companion view | Supported later |
| Recurrence-aware rendering | Supported incrementally |

---

## 10. 分阶段发布

calendar 应当被设计为完整的产品能力，但实现上按阶段推进。

### Phase A —— 只读 calendar foundation

范围：

- Main-layer calendar mode
- Month view 和/或 agenda fallback
- 多源聚合
- 选择日期 → 查看任务
- task chip → 打开 detail panel
- 从选中任务跳转到 source

它验证的是：

- 数据语义是可靠的
- calendar 天然属于 Main
- 不重写 CRUD flows 也能立刻给用户带来价值

### Phase B —— 轻量任务操作

范围：

- 为选中日期直接创建任务
- 在 calendar 上下文中编辑任务 due date
- 通过 calendar detail path 快速修改 priority/tag
- 更好的 week/day 导航

它新增的是：

- calendar 不再只是观察面，而开始成为操作面

### Phase C —— 完整交互层

范围：

- 拖拽或通过键盘 move-to-date
- 更密集的 day/week 渲染
- 更好的溢出处理
- recurring-task cues
- 可选的 undated companion lane / agenda 增强

它完成的是：

- calendar 成为一等的规划与维护表面

---

## 11. 备选方案

### 11.1 单独的顶层 Calendar tab

**暂不采用。**

原因：

- 会重复 Main-layer 的聚合概念
- 会在 “Main” 和 “Calendar” 两个跨来源总览之间制造歧义

### 11.2 用 calendar 替换 scope filters

**不采用。**

原因：

- source-local list filters 仍然很适合快速文本工作流
- 用户同时需要 list buckets 和 time navigation

### 11.3 添加单独的 calendar 数据模型

**不采用。**

原因：

- 会破坏优雅的 single-source-of-truth 模型
- 会重复 `due_date` 已经表达的语义
- 会不必要地提高迁移与一致性风险

---

## 12. 实现草图

本节不会锁定精确的代码结构，但代码库里已经能看到自然的锚点。

### 12.1 可复用的现有基础

| Area | Existing responsibility | Calendar relevance |
|---|---|---|
| `mutsumi/core/loader.py` | 文件解析、加载、scope 推导 | 复用 `due_date` 语义与过滤辅助工具 |
| `mutsumi/core/sources.py` | 多源注册表 | 复用聚合 source map |
| `mutsumi/app.py` | source-tab 编排 | 承载 Main/dashboard/calendar mode 的切换 |
| `mutsumi/tui/main_dashboard.py` | Main 聚合表面 | 很可能成为 calendar UI 的 sibling 或扩展点 |
| `mutsumi/tui/scope_filter.py` | source-local filters | 可作为次级导航模式的参考 |
| `mutsumi/tui/detail_panel.py` | 任务 drill-down | 复用为 calendar 的任务检查终点 |

### 12.2 可能的 UI 形态

一个合理路径是：

- 保持 `MainDashboard` 作为 summary surface
- 为 calendar surface 新增一个 widget
- 由 `app.py` 负责在 Main 中切换 dashboard mode 与 calendar mode
- 保留 source tabs 和 detail panel 交互

### 12.3 数据变换层

calendar 渲染会需要一层轻量投影，把：

```text
(source_name, task) → date bucket → rendered cell/task summary
```

这只是 view transformation，不是 schema change。

---

## 13. 测试策略

### 13.1 数据语义测试

- 带有效 `due_date` 的任务会落到正确日期
- 带无效 `due_date` 的任务会安全降级
- 逾期任务会被正确标记
- 没有 `due_date` 的任务不会出现在日期格子里
- 多源聚合会保留 source identity

### 13.2 TUI 行为测试

- 纯键盘 calendar 导航可用
- 纯鼠标日期选择可用
- Main dashboard 与 calendar 之间切换可用
- 选择 calendar task 后能正确打开 detail
- source drill-down 能到达正确 tab

### 13.3 手动 beta 场景

- personal + 多个 project sources 都有日期任务
- 一个很拥挤的周和一个很稀疏的周
- 混合 overdue、today、future 与 undated tasks
- 窄终端 fallback 行为

---

## 14. 开放问题

1. 第一版 shipped 的版本应该以 **month view**、**agenda view**，还是两者一起作为主入口？
2. undated tasks 是否应该从一开始就与 calendar 并列显示，还是推迟？
3. 第一版交互式发布中，应该包含多少 inline editing？还是先把编辑保持在 detail panel/task form 中？
4. 对终端 UI 中高密度 month cells，最佳 overflow model 是什么？
5. calendar mode 最适合放在 Main 中的 segmented control、hotkey，还是两者都支持？

---

## 15. 结论

Mutsumi 已经在语义上理解了时间，但还没有在视觉上理解它。

内建 calendar 是自然的下一步，因为它：

- 复用了现有的 `due_date` 语义
- 强化了 Main-layer command-center 愿景
- 让多线程用户更好地看见调度压力
- 补充列表视图，而不是取代它们

因此正确的方向是：

- **一套任务模型**
- **一套 source 架构**
- **多种 view surfaces**

List view 回答的是 “这里有什么？”
Calendar view 回答的是 “它什么时候落下？”

Mutsumi 应该同时拥有两者。
