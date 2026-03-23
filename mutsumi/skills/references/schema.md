# mutsumi.json Schema Reference

## File Structure

```json
{
  "version": 1,
  "tasks": [ /* Task objects */ ]
}
```

## Task Object

| Field          | Type       | Required | Values / Default                           |
|----------------|------------|----------|--------------------------------------------|
| `id`           | string     | yes      | Unique ID (ULID recommended)               |
| `title`        | string     | yes      | Task title                                 |
| `status`       | string     | yes      | `"pending"` (default), `"done"`            |
| `scope`        | string     | no       | `"day"`, `"week"`, `"month"`, `"inbox"` (default) |
| `priority`     | string     | no       | `"high"`, `"normal"` (default), `"low"`    |
| `tags`         | string[]   | no       | `[]`                                       |
| `description`  | string     | no       | Free text                                  |
| `due_date`     | string     | no       | ISO 8601 date (`YYYY-MM-DD`)               |
| `created_at`   | string     | no       | ISO 8601 datetime                          |
| `completed_at` | string     | no       | ISO 8601 datetime (auto-filled on done)    |
| `children`     | Task[]     | no       | Nested subtasks (same schema, recursive)   |

## Critical Rules

- **Preserve unknown fields.** `mutsumi.json` may contain fields you don't recognize. Never delete them.
- **Atomic writes.** Write to a temp file first, then `os.rename()` / `os.replace()` to the target path.
- **File is watched.** The Mutsumi TUI watches `mutsumi.json` and re-renders on every save. No notification needed.
- **Unique IDs.** Generate a unique string ID for every new task. ULIDs are preferred.
