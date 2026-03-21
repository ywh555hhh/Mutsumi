# Mutsumi — Agent Cheat Sheet

> One-page reference for AI agents that manage tasks via Mutsumi.

## Quick Start

Mutsumi is a TUI that watches `./tasks.json` and re-renders on every change.
Your job: read/write that file. Mutsumi handles the display.

## Schema

| Field          | Type       | Required | Default     | Values / Notes                              |
|----------------|------------|----------|-------------|---------------------------------------------|
| `id`           | string     | **Yes**  | —           | Unique, e.g. UUIDv7 / ULID / any string    |
| `title`        | string     | **Yes**  | —           | ≤ 120 chars recommended                     |
| `status`       | string     | **Yes**  | `"pending"` | `"pending"` or `"done"` only                |
| `scope`        | string     | No       | `"inbox"`   | `"day"` / `"week"` / `"month"` / `"inbox"`  |
| `priority`     | string     | No       | `"normal"`  | `"high"` / `"normal"` / `"low"`             |
| `tags`         | string[]   | No       | `[]`        | Free-form labels                            |
| `children`     | Task[]     | No       | `[]`        | Nested subtasks (same schema, max 3 levels) |
| `due_date`     | string     | No       | —           | ISO 8601 date, e.g. `"2026-03-25"`          |
| `description`  | string     | No       | —           | Markdown supported                          |
| `created_at`   | string     | No       | auto        | ISO 8601 timestamp                          |
| `completed_at` | string     | No       | —           | Auto-filled when status → done              |

## CLI Commands

```bash
mutsumi add "title" --priority high --scope day --tags "dev,urgent"
mutsumi done <id-prefix>          # Mark task as done (prefix match)
mutsumi edit <id-prefix> --title "new title" --priority low
mutsumi rm <id-prefix>            # Delete task
mutsumi list                      # List all tasks as table
mutsumi validate                  # Validate tasks.json
mutsumi schema                    # Print JSON Schema
mutsumi init                      # Create template tasks.json
```

## Direct JSON Protocol

When writing `tasks.json` directly (without CLI):

1. **Read** the entire `./tasks.json`
2. **Modify** the `tasks` array (add, remove, or update items)
3. **Write the ENTIRE file** back — never partial writes
4. **Atomic write**: write to a temp file first, then `os.rename()` to `tasks.json`
5. **Generate a unique ID** for every new task (UUID, ULID, or any unique string)

File format:
```json
{
  "version": 1,
  "tasks": [ ... ]
}
```

## Examples

### Add a task (JSON)
```json
{
  "id": "task-001",
  "title": "Refactor Auth module",
  "status": "pending",
  "scope": "day",
  "priority": "high",
  "tags": ["dev", "backend"],
  "children": []
}
```

### Mark a task as done (JSON)
```json
{
  "id": "task-001",
  "status": "done",
  "completed_at": "2026-03-22T15:30:00Z"
}
```

### Add a task (CLI)
```bash
mutsumi add "Refactor Auth module" -P high -s day -t "dev,backend"
```

### Complete a task (CLI)
```bash
mutsumi done task-001
```

## Rules

1. **Preserve unknown fields** — if a task has fields you don't recognize, keep them as-is
2. **Status values** — only `"pending"` and `"done"` are valid
3. **Unique IDs** — every task must have a unique `id`; use UUIDv7, ULID, or any unique string
4. **Don't delete the file** — always overwrite, never delete and recreate
5. **version field** — always include `"version": 1` at the root level
6. **Encoding** — UTF-8, no BOM

## Agent Integration Setup

```bash
# Inject Mutsumi instructions into your agent's config:
mutsumi setup --agent claude-code   # → appends to CLAUDE.md
mutsumi setup --agent codex-cli     # → appends to AGENTS.md
mutsumi setup --agent gemini-cli    # → appends to GEMINI.md
mutsumi setup --agent opencode      # → appends to opencode.md
mutsumi setup --agent aider         # → prints to stdout
mutsumi setup --agent custom        # → prints to stdout
```
