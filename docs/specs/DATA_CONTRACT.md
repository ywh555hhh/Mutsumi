# Mutsumi Data Contract Specification

| Version | 0.1.0              |
|---------|---------------------|
| Status  | Draft               |
| Date    | 2026-03-21          |

> **[中文版](./DATA_CONTRACT_cn.md)** | **[日本語版](./DATA_CONTRACT_ja.md)**

---

## 1. File Structure

A Mutsumi data source is a valid JSON file containing an array of tasks.

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

### 1.1 Root Fields

| Field       | Type     | Required | Description                                      |
|-------------|----------|----------|--------------------------------------------------|
| `$schema`   | string   | No       | JSON Schema URL (optional, for editor hints)     |
| `version`   | integer  | Yes      | Data format version, currently `1`               |
| `tasks`     | array    | Yes      | Array of task objects                             |

## 2. Task Object

### 2.1 Base Fields (Official)

| Field          | Type       | Required | Default     | Description                                |
|----------------|------------|----------|-------------|--------------------------------------------|
| `id`           | string     | **Yes**  | —           | UUIDv7 format, e.g. `"01JQ8X7K3M..."`     |
| `title`        | string     | **Yes**  | —           | Task title, recommended ≤ 120 chars        |
| `status`       | string     | **Yes**  | `"pending"` | Enum: `"pending"`, `"done"`                |
| `scope`        | string     | No       | `"inbox"`   | Enum: `"day"`, `"week"`, `"month"`, `"inbox"` |
| `priority`     | string     | No       | `"normal"`  | Enum: `"high"`, `"normal"`, `"low"`        |
| `tags`         | string[]   | No       | `[]`        | Custom tag array                           |
| `children`     | Task[]     | No       | `[]`        | Subtask array (recursive nesting)          |
| `created_at`   | string     | No       | auto        | ISO 8601 timestamp                         |
| `due_date`     | string     | No       | —           | ISO 8601 date (e.g., `"2026-03-25"`)      |
| `completed_at` | string     | No       | —           | Completion time, auto-filled when status becomes done |
| `description`  | string     | No       | —           | Detailed description (Markdown)            |

### 2.2 Custom Fields (User-defined)

Mutsumi **guarantees**:
- Any field not in the table above will be **preserved** — never deleted or modified
- TUI rendering ignores custom fields
- Agents are free to add custom fields for their own logic

Example — user-defined custom fields:

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

The fields `estimated_minutes`, `energy_level`, `pomodoro_count`, and `context` above are all user-defined custom fields. Mutsumi will not interfere with them.

## 3. ID Specification

### 3.1 UUIDv7

UUIDv7 (RFC 9562) is used by default.

```
01JQ8X7K3M0000000000000000
├──────────┤├──────────────┤
  Time part     Random part
  (ms precision)
```

Properties:
- Naturally sorted by creation time
- Globally unique, no central authority needed
- Both Agent and TUI can generate independently
- Compact 26-char Crockford Base32 encoding

### 3.2 Alternative Formats (Configurable)

Users can configure different ID formats in `config.toml`.

| Format          | Example                              | Use Case             |
|-----------------|--------------------------------------|----------------------|
| `uuidv7`        | `01JQ8X7K3M0000000000000000`         | Default, recommended |
| `ulid`          | `01ARZ3NDEKTSV4RRFFQ69G5FAV`        | ULID enthusiasts     |
| `auto-increment`| `1`, `2`, `3`                        | Minimalists          |

## 4. Scope Resolution

### 4.1 Priority Order

```
Manual scope > due_date auto-derivation > fallback "inbox"
```

### 4.2 Auto-derivation Rules

When a task has `due_date` but no manual `scope`:

| Condition                        | Derived Scope      |
|----------------------------------|--------------------|
| `due_date` == today              | `day`              |
| `due_date` within this week      | `week`             |
| `due_date` within this month     | `month`            |
| `due_date` in the past (overdue) | `day` (escalated)  |
| `due_date` beyond this month     | `month`            |

### 4.3 Scope Tab Semantics

| Tab     | Shows                                                |
|---------|------------------------------------------------------|
| Today   | `scope == "day"` OR (auto-derived as today)          |
| Week    | `scope == "week"` OR (auto-derived as this week)     |
| Month   | `scope == "month"` OR (auto-derived as this month)   |
| Inbox   | `scope == "inbox"` OR (no scope + no due_date)       |

## 5. Nesting

### 5.1 Structure

Subtasks are recursively nested via the `children` array.

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

### 5.2 Rendering Rules

| Nesting Depth | Default Behavior                                              | Configurable |
|---------------|---------------------------------------------------------------|--------------|
| 1-3 levels    | Fully rendered with indentation                               | —            |
| 4+ levels     | Collapsed to "3 subtasks...", click to expand                 | Yes          |
| Unlimited     | No limit at data layer, configurable cap at render layer      | Yes          |

### 5.3 Parent-Child Status Rules

- When all children are `done`, the parent is **not** automatically marked done (user has explicit control).
- TUI can display a `2/5 done` progress indicator.
- Agents can implement their own auto-completion logic.

## 6. Full Example

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

## 7. Schema Validation Rules

### 7.1 Strictness Levels

| Level    | Behavior                                                        | Use Case            |
|----------|----------------------------------------------------------------|---------------------|
| `strict` | Reject any invalid fields/values                                | CI/CD validation    |
| `normal` | Skip invalid tasks, render valid ones (default)                 | TUI daily use       |
| `loose`  | Best-effort rendering, silently ignore unknown fields           | Rapid prototyping   |

### 7.2 Required Field Validation

- `id` — non-empty string
- `title` — non-empty string
- `status` — must be `"pending"` or `"done"`

Any task missing one of the above fields is considered **invalid** and handled according to the strictness level.

### 7.3 Error Reporting

Validation errors are written to stderr and logged to `~/.local/share/mutsumi/error.log`.

```
[2026-03-21T10:00:00Z] WARN: Task at index 3 missing required field "id", skipped
[2026-03-21T10:00:00Z] WARN: Task "01JQ..." has unknown status "wip", rendered with warning badge
```
