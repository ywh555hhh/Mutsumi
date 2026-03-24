# Mutsumi 数据契约规范

| 版本 | 1.0 |
|---|---|
| 状态 | 草案 |
| 日期 | 2026-03-23 |

> **[English Version](./DATA_CONTRACT.md)** | **[日本語版](./DATA_CONTRACT_ja.md)**

---

## 1. 规范文件命名

Mutsumi 以符合下述 schema 的 JSON 对象存储任务。

### 1.1 首选文件名

- **规范文件名：** `mutsumi.json`
- **向后兼容回退：** `tasks.json`

对于新项目和新的示例，始终使用 **`mutsumi.json`**。
`tasks.json` 仅继续保留给旧环境兼容使用。

### 1.2 文件解析顺序

当未显式传入路径时，Mutsumi 按以下顺序解析当前活动任务文件：

1. CLI `--path`
2. `./mutsumi.json`
3. `./tasks.json`
4. 新项目默认目标：`./mutsumi.json`

---

## 2. 根结构

一个 Mutsumi 数据源是一个包含 `tasks` 数组的合法 JSON 对象。

```json
{
  "$schema": "https://mutsumi.dev/schema/v1.json",
  "version": 1,
  "tasks": [
    { "id": "01JQ...", "title": "Refactor auth", "status": "pending" }
  ]
}
```

### 2.1 根字段

| 字段 | 类型 | 必填 | 说明 |
|---|---|---:|---|
| `$schema` | string | 否 | 可选的 schema URL，用于编辑器提示 |
| `version` | integer | 是 | 数据格式版本，当前为 `1` |
| `tasks` | array | 是 | 任务对象数组 |

### 2.2 未知根字段

Mutsumi 在读取和写回任务文件时，会保留未知的根级字段。

---

## 3. 任务对象

### 3.1 官方字段

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---:|---|---|
| `id` | string | 是 | — | 唯一标识符，推荐 UUIDv7 |
| `title` | string | 是 | — | 任务标题 |
| `status` | string | 是 | `"pending"` | `"pending"` 或 `"done"` |
| `scope` | string | 否 | `"inbox"` | `"day"`、`"week"`、`"month"`、`"inbox"` |
| `priority` | string | 否 | `"normal"` | `"high"`、`"normal"`、`"low"` |
| `tags` | string[] | 否 | `[]` | 自由标签 |
| `children` | Task[] | 否 | `[]` | 嵌套子任务 |
| `created_at` | string | 否 | auto | ISO 8601 时间戳 |
| `due_date` | string | 否 | — | ISO 8601 日期，例如 `"2026-03-25"` |
| `completed_at` | string | 否 | — | 完成时间戳 |
| `description` | string | 否 | — | 更长的说明或备注 |

### 3.2 未知任务字段

Mutsumi 保证：

- **保留**未知任务字段
- TUI 渲染时忽略它不理解的字段
- agents 可以为自己的工作流添加额外元数据

示例：

```json
{
  "id": "01JQ8X7K3M0000000000000000",
  "title": "Train model v2",
  "status": "pending",
  "scope": "week",
  "priority": "high",
  "tags": ["ml"],
  "estimated_minutes": 120,
  "energy_level": "high-focus",
  "context": "Needs GPU"
}
```

---

## 4. Scope 解析

`scope` 仍然是列表视图和过滤器使用的计划分桶。

### 4.1 解析顺序

```text
explicit scope > due_date auto-derivation > fallback inbox
```

### 4.2 从 `due_date` 自动推导

当任务存在 `due_date`，但没有有意义的显式 scope 时，Mutsumi 会根据日期推导 scope。

| 条件 | 推导出的 scope |
|---|---|
| `due_date` 是今天 | `day` |
| `due_date` 早于今天 | `day` |
| `due_date` 落在当前周内 | `week` |
| `due_date` 落在当前月后段 | `month` |
| `due_date` 超出当前月 | `month` |
| `due_date` 字符串无效 | `inbox` |

### 4.3 过滤语义

| 过滤器 | 显示内容 |
|---|---|
| Today | effective scope 为 `day` 的任务 |
| Week | effective scope 为 `week` 的任务 |
| Month | effective scope 为 `month` 的任务 |
| Inbox | effective scope 为 `inbox` 的任务 |
| All | 所有任务，不论 scope |

---

## 5. 嵌套

### 5.1 结构

子任务通过 `children` 字段递归嵌套。

```json
{
  "id": "01JQ8X7K3M...",
  "title": "Refactor user system",
  "status": "pending",
  "children": [
    {
      "id": "01JQ8X7K4N...",
      "title": "Design schema",
      "status": "done",
      "children": []
    },
    {
      "id": "01JQ8X7K5P...",
      "title": "Write migration",
      "status": "pending",
      "children": []
    }
  ]
}
```

### 5.2 父子规则

- 所有子任务完成 **不会** 自动完成父任务
- TUI 可以显示如 `2/5 done` 的进度
- Agents 可以实现自己的更高层自动化，但基础契约保持显式

---

## 6. 校验规则

### 6.1 必填字段校验

任务缺少以下任一字段时即为无效：

- `id`
- `title`
- `status`

### 6.2 枚举校验

支持的取值：

- `status`：`pending`、`done`
- `priority`：`high`、`normal`、`low`
- `scope`：`day`、`week`、`month`、`inbox`

### 6.3 运行时行为

- 非法 JSON 会阻止文件加载
- 在弹性加载模式下，单个非法任务可能被跳过
- Mutsumi 会通过 UI 和日志输出报告校验问题，而不是直接崩溃

---

## 7. 写入语义

修改任务文件的 agents 和工具应遵循以下规则：

1. 读取整个文件
2. 在内存中修改 `tasks` 数组
3. 保留未知根字段和任务字段
4. 以原子方式写回**整个文件**
5. 新写入优先使用 `mutsumi.json`

---

## 8. 完整示例

```json
{
  "$schema": "https://mutsumi.dev/schema/v1.json",
  "version": 1,
  "tasks": [
    {
      "id": "01JQ8X7K3M0000000000000001",
      "title": "Refactor auth module",
      "status": "pending",
      "scope": "day",
      "priority": "high",
      "tags": ["dev", "backend"],
      "created_at": "2026-03-21T08:00:00Z",
      "due_date": "2026-03-21",
      "description": "Replace session-based auth with JWT",
      "children": [
        {
          "id": "01JQ8X7K3M0000000000000002",
          "title": "Install PyJWT",
          "status": "done",
          "priority": "normal",
          "tags": [],
          "completed_at": "2026-03-21T09:30:00Z",
          "children": []
        },
        {
          "id": "01JQ8X7K3M0000000000000003",
          "title": "Write middleware",
          "status": "pending",
          "priority": "normal",
          "tags": [],
          "children": []
        }
      ]
    },
    {
      "id": "01JQ8X7K3M0000000000000004",
      "title": "Buy coffee beans",
      "status": "pending",
      "scope": "inbox",
      "priority": "low",
      "tags": ["life"],
      "children": []
    }
  ]
}
```

---

## 9. 兼容性说明

- `mutsumi.json` 与旧的 `tasks.json` 共享**同一份 schema**
- 文件名迁移 **不意味着** schema 迁移
- 未来的视图，包括日历类时间视图，都应复用 `due_date` 和同一基础任务对象，而不是引入第二套任务模型
