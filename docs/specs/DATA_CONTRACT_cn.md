# Mutsumi 数据契约规范

| 版本   | 0.1.0              |
|--------|---------------------|
| 状态   | 草案                |
| 日期   | 2026-03-21          |

> **[English Version](./DATA_CONTRACT.md)** | **[日本語版](./DATA_CONTRACT_ja.md)**

---

## 1. 文件结构

一个 Mutsumi 数据源是一个合法的 JSON 文件，包含一个任务数组：

```json
{
  "$schema": "https://mutsumi.dev/schema/v1.json",
  "version": 1,
  "tasks": [
    { ... },
    { ... }
  ]
}
```

### 1.1 根字段

| 字段        | 类型     | 必填 | 说明                                      |
|-------------|----------|------|------------------------------------------|
| `$schema`   | string   | 否   | JSON Schema URL（可选，供编辑器提示）       |
| `version`   | integer  | 是   | 数据格式版本号，当前为 `1`                  |
| `tasks`     | array    | 是   | 任务对象数组                               |

## 2. 任务对象

### 2.1 基础字段（官方定义）

| 字段           | 类型       | 必填   | 默认值      | 说明                                       |
|----------------|------------|--------|-------------|-------------------------------------------|
| `id`           | string     | **是** | —           | UUIDv7 格式，如 `"01JQ8X7K3M..."`          |
| `title`        | string     | **是** | —           | 任务标题，建议 ≤ 120 字符                   |
| `status`       | string     | **是** | `"pending"` | 枚举: `"pending"`, `"done"`                |
| `scope`        | string     | 否     | `"inbox"`   | 枚举: `"day"`, `"week"`, `"month"`, `"inbox"` |
| `priority`     | string     | 否     | `"normal"`  | 枚举: `"high"`, `"normal"`, `"low"`        |
| `tags`         | string[]   | 否     | `[]`        | 自定义标签数组                              |
| `children`     | Task[]     | 否     | `[]`        | 子任务数组（递归嵌套）                       |
| `created_at`   | string     | 否     | 自动        | ISO 8601 时间戳                            |
| `due_date`     | string     | 否     | —           | ISO 8601 日期（如 `"2026-03-25"`）          |
| `completed_at` | string     | 否     | —           | 完成时间，状态变为 done 时自动填充           |
| `description`  | string     | 否     | —           | 任务详细描述（Markdown 格式）               |

### 2.2 自定义字段（用户自定义）

Mutsumi **保证**：
- 任何不在上表中的字段会被**保留**，不会被删除或修改
- TUI 渲染时忽略自定义字段
- Agent 可以自由添加自定义字段用于自己的逻辑

示例 — 用户添加自定义字段：

```json
{
  "id": "01JQ8X7K3M0000000000000000",
  "title": "训练模型 v2",
  "status": "pending",
  "scope": "week",
  "priority": "high",
  "tags": ["ml"],
  "estimated_minutes": 120,
  "energy_level": "high-focus",
  "pomodoro_count": 0,
  "context": "需要 GPU 机器"
}
```

以上 `estimated_minutes`、`energy_level`、`pomodoro_count`、`context` 均为用户自定义字段，Mutsumi 不干预。

## 3. ID 规范

### 3.1 UUIDv7

默认使用 UUIDv7（RFC 9562）：

```
01JQ8X7K3M0000000000000000
├──────────┤├──────────────┤
  时间部分       随机部分
  (ms 精度)
```

特性：
- 按创建时间自然排序
- 全局唯一，无需中央分配
- Agent 和 TUI 均可独立生成
- 紧凑的 26 字符 Crockford Base32 编码

### 3.2 备选格式（可配置）

用户可在 `config.toml` 中配置不同的 ID 格式：

| 格式            | 示例                                 | 适用场景       |
|-----------------|--------------------------------------|---------------|
| `uuidv7`        | `01JQ8X7K3M0000000000000000`         | 默认，推荐     |
| `ulid`          | `01ARZ3NDEKTSV4RRFFQ69G5FAV`        | ULID 爱好者    |
| `auto-increment`| `1`, `2`, `3`                        | 极简主义者     |

## 4. Scope 解析

### 4.1 优先级顺序

```
手动 scope > due_date 自动推导 > fallback "inbox"
```

### 4.2 自动推导规则

当任务有 `due_date` 且没有手动 `scope` 时：

| 条件                             | 推导出的 Scope    |
|----------------------------------|-------------------|
| `due_date` == 今天               | `day`             |
| `due_date` 在本周内              | `week`            |
| `due_date` 在本月内              | `month`           |
| `due_date` 已过期                | `day`（升级）      |
| `due_date` 超出本月              | `month`           |

### 4.3 Scope Tab 语义

| Tab     | 显示内容                                             |
|---------|------------------------------------------------------|
| Today   | `scope == "day"` 或（自动推导为今天）                  |
| Week    | `scope == "week"` 或（自动推导为本周）                 |
| Month   | `scope == "month"` 或（自动推导为本月）                |
| Inbox   | `scope == "inbox"` 或（无 scope + 无 due_date）       |

## 5. 嵌套

### 5.1 结构

子任务通过 `children` 数组递归嵌套：

```json
{
  "id": "01JQ8X7K3M...",
  "title": "重构用户系统",
  "status": "pending",
  "children": [
    {
      "id": "01JQ8X7K4N...",
      "title": "设计新的数据库 schema",
      "status": "done",
      "children": []
    },
    {
      "id": "01JQ8X7K5P...",
      "title": "实现 migration 脚本",
      "status": "pending",
      "children": [
        {
          "id": "01JQ8X7K6Q...",
          "title": "备份现有数据",
          "status": "pending",
          "children": []
        }
      ]
    }
  ]
}
```

### 5.2 渲染规则

| 嵌套深度  | 默认行为                                     | 可配置 |
|-----------|---------------------------------------------|--------|
| 1-3 层    | 完整渲染，缩进展示                            | —      |
| 4+ 层     | 折叠为 "3 subtasks..."，点击展开               | 是     |
| 无限层    | 数据层无限制，渲染层有配置上限                  | 是     |

### 5.3 父子任务状态规则

- 子任务全部 `done` 时，父任务**不**自动标记为 done（用户显式控制）
- TUI 可显示 `2/5 done` 的进度指示器
- Agent 可以实现自己的自动完成逻辑

## 6. 完整示例

```json
{
  "$schema": "https://mutsumi.dev/schema/v1.json",
  "version": 1,
  "tasks": [
    {
      "id": "01JQ8X7K3M0000000000000001",
      "title": "重构 Auth 模块",
      "status": "pending",
      "scope": "day",
      "priority": "high",
      "tags": ["dev", "backend"],
      "created_at": "2026-03-21T08:00:00Z",
      "due_date": "2026-03-21",
      "description": "把 session-based auth 改成 JWT",
      "children": [
        {
          "id": "01JQ8X7K3M0000000000000002",
          "title": "安装 PyJWT",
          "status": "done",
          "priority": "normal",
          "tags": [],
          "completed_at": "2026-03-21T09:30:00Z",
          "children": []
        },
        {
          "id": "01JQ8X7K3M0000000000000003",
          "title": "写 middleware",
          "status": "pending",
          "priority": "normal",
          "tags": [],
          "children": []
        }
      ]
    },
    {
      "id": "01JQ8X7K3M0000000000000004",
      "title": "买咖啡豆",
      "status": "pending",
      "scope": "inbox",
      "priority": "low",
      "tags": ["life"],
      "children": []
    }
  ]
}
```

## 7. Schema 校验规则

### 7.1 严格程度级别

| 级别     | 行为                                      | 适用场景       |
|----------|------------------------------------------|---------------|
| `strict` | 拒绝任何非法字段/值                        | CI/CD 校验     |
| `normal` | 跳过非法任务，渲染有效任务（默认）           | TUI 日常使用   |
| `loose`  | 尽力渲染，未知字段静默忽略                   | 快速原型       |

### 7.2 必填字段校验

- `id` — 非空字符串
- `title` — 非空字符串
- `status` — 必须是 `"pending"` 或 `"done"`

缺少以上任一字段的任务视为 **invalid**，按 strictness level 处理。

### 7.3 错误报告

校验错误写入 stderr 并记录到 `~/.local/share/mutsumi/error.log`：

```
[2026-03-21T10:00:00Z] WARN: Task at index 3 missing required field "id", skipped
[2026-03-21T10:00:00Z] WARN: Task "01JQ..." has unknown status "wip", rendered with warning badge
```
