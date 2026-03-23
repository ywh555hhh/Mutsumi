# Mutsumi Data Contract Specification

| Version | 1.0 |
|---------|-----|
| Status  | Draft |
| Date    | 2026-03-23 |

> **[中文版](./DATA_CONTRACT_cn.md)** | **[日本語版](./DATA_CONTRACT_ja.md)**

---

## 1. Canonical File Naming

Mutsumi stores tasks in a JSON object with the schema defined below.

### 1.1 Preferred filename

- **Canonical filename:** `mutsumi.json`
- **Backward-compatible fallback:** `tasks.json`

For new projects and new examples, always use **`mutsumi.json`**.
`tasks.json` remains supported only for compatibility with older setups.

### 1.2 File resolution order

When no explicit path is passed, Mutsumi resolves the active task file in this order:

1. CLI `--path`
2. `./mutsumi.json`
3. `./tasks.json`
4. default target for new projects: `./mutsumi.json`

---

## 2. Root Structure

A Mutsumi data source is a valid JSON object containing a `tasks` array.

```json
{
  "$schema": "https://mutsumi.dev/schema/v1.json",
  "version": 1,
  "tasks": [
    { "id": "01JQ...", "title": "Refactor auth", "status": "pending" }
  ]
}
```

### 2.1 Root fields

| Field | Type | Required | Description |
|---|---|---:|---|
| `$schema` | string | No | Optional schema URL for editor hints |
| `version` | integer | Yes | Data format version, currently `1` |
| `tasks` | array | Yes | Array of task objects |

### 2.2 Unknown root fields

Mutsumi preserves unknown root-level fields when loading and writing task files.

---

## 3. Task Object

### 3.1 Official fields

| Field | Type | Required | Default | Description |
|---|---|---:|---|---|
| `id` | string | Yes | — | Unique identifier, UUIDv7 recommended |
| `title` | string | Yes | — | Task title |
| `status` | string | Yes | `"pending"` | `"pending"` or `"done"` |
| `scope` | string | No | `"inbox"` | `"day"`, `"week"`, `"month"`, `"inbox"` |
| `priority` | string | No | `"normal"` | `"high"`, `"normal"`, `"low"` |
| `tags` | string[] | No | `[]` | Free-form tags |
| `children` | Task[] | No | `[]` | Nested subtasks |
| `created_at` | string | No | auto | ISO 8601 timestamp |
| `due_date` | string | No | — | ISO 8601 date, e.g. `"2026-03-25"` |
| `completed_at` | string | No | — | Completion timestamp |
| `description` | string | No | — | Longer text or notes |

### 3.2 Unknown task fields

Mutsumi guarantees:

- unknown task fields are **preserved**
- TUI rendering ignores fields it does not understand
- agents may add extra metadata for their own workflows

Example:

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

## 4. Scope Resolution

`scope` remains the planning bucket used by list views and filters.

### 4.1 Resolution order

```text
explicit scope > due_date auto-derivation > fallback inbox
```

### 4.2 Auto-derivation from `due_date`

When a task has `due_date` but no meaningful explicit scope, Mutsumi derives scope from the date.

| Condition | Derived scope |
|---|---|
| `due_date` is today | `day` |
| `due_date` is earlier than today | `day` |
| `due_date` falls within the current week | `week` |
| `due_date` falls later in the current month | `month` |
| `due_date` is beyond the current month | `month` |
| invalid `due_date` string | `inbox` |

### 4.3 Filter semantics

| Filter | Shows |
|---|---|
| Today | tasks whose effective scope is `day` |
| Week | tasks whose effective scope is `week` |
| Month | tasks whose effective scope is `month` |
| Inbox | tasks whose effective scope is `inbox` |
| All | all tasks, regardless of scope |

---

## 5. Nesting

### 5.1 Structure

Subtasks are recursively nested through the `children` field.

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

### 5.2 Parent-child rules

- Completing all children does **not** automatically complete the parent
- The TUI may show progress such as `2/5 done`
- Agents may implement their own higher-level automation, but the base contract stays explicit

---

## 6. Validation Rules

### 6.1 Required field validation

A task is invalid if it is missing any of the following:

- `id`
- `title`
- `status`

### 6.2 Enum validation

Supported values:

- `status`: `pending`, `done`
- `priority`: `high`, `normal`, `low`
- `scope`: `day`, `week`, `month`, `inbox`

### 6.3 Runtime behavior

- invalid JSON prevents the file from loading
- invalid individual tasks may be skipped during resilient loading
- Mutsumi reports validation problems through the UI and log output instead of crashing

---

## 7. Write Semantics

Agents and tools that modify the task file should follow these rules:

1. Read the whole file
2. Modify the `tasks` array in memory
3. Preserve unknown root and task fields
4. Write the **entire file** back atomically
5. Prefer `mutsumi.json` for new writes

---

## 8. Full Example

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

## 9. Compatibility Notes

- `mutsumi.json` and legacy `tasks.json` share the **same schema**
- the filename migration does **not** imply a schema migration
- future views, including calendar-style time views, should reuse `due_date` and the same base task object rather than introducing a separate task model
