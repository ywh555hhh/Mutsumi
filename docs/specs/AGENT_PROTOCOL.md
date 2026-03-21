# Mutsumi Agent Integration Protocol

| Version | 0.1.0              |
|---------|---------------------|
| Status  | Draft               |
| Date    | 2026-03-21          |

> **[中文版](./AGENT_PROTOCOL_cn.md)** | **[日本語版](./AGENT_PROTOCOL_ja.md)**

---

## 1. Overview

This document defines how external Agents (AI CLI tools, custom scripts, etc.) read from and write to Mutsumi's `tasks.json`.

**Core principle: Mutsumi does not bind to any specific Agent. Any program that can correctly read and write JSON is a legitimate Controller.**

## 2. Supported Agents (Non-exhaustive)

| Agent          | Type              | Integration Level        |
|----------------|-------------------|--------------------------|
| Claude Code    | AI CLI            | Native (recommended)     |
| Codex CLI      | AI CLI            | Native                   |
| Gemini CLI     | AI CLI            | Native                   |
| OpenCode       | AI CLI            | Native                   |
| Aider          | AI CLI            | Native                   |
| shell scripts  | Custom            | Native                   |
| cron jobs      | System            | Native                   |

"Native" means only JSON file read/write is needed — no SDK or plugin installation required.

## 3. Write Protocol (Agent → Mutsumi)

### 3.1 Workflow

```
1. Read the current tasks.json (full content)
2. Parse as JSON
3. Modify the tasks array (add/update/delete)
4. Write the ENTIRE file back (no partial writes)
5. Mutsumi's watchdog detects change → re-renders
```

### 3.2 Rules

| Rule                          | Description                                                              |
|-------------------------------|--------------------------------------------------------------------------|
| **Preserve unknown fields**   | Do not delete fields you don't recognize; keep them as-is                |
| **Atomic write**              | Recommended: write to a temp file then rename, to avoid Mutsumi reading a half-written state |
| **Valid JSON**                | The file must be valid JSON after writing                                |
| **Generate valid IDs**        | New task IDs should use UUIDv7; at minimum, ensure uniqueness            |
| **Required fields**           | Every task must include `id`, `title`, `status`                          |
| **Enum compliance**           | `status` can only be `"pending"` / `"done"`                              |

### 3.3 Adding a Task

```python
import json, uuid, datetime

# Read
with open("tasks.json") as f:
    data = json.load(f)

# Add
new_task = {
    "id": str(uuid.uuid7()),  # or any unique string
    "title": "修复登录 Bug",
    "status": "pending",
    "scope": "day",
    "priority": "high",
    "tags": ["bugfix"],
    "created_at": datetime.datetime.now(datetime.UTC).isoformat(),
    "children": []
}
data["tasks"].append(new_task)

# Write (atomic)
import tempfile, os
tmp = tempfile.NamedTemporaryFile(
    mode='w', dir='.', suffix='.tmp', delete=False
)
json.dump(data, tmp, ensure_ascii=False, indent=2)
tmp.close()
os.rename(tmp.name, "tasks.json")
```

### 3.4 Completing a Task

```python
for task in data["tasks"]:
    if task["id"] == target_id:
        task["status"] = "done"
        task["completed_at"] = datetime.datetime.now(datetime.UTC).isoformat()
        break
```

### 3.5 Agent Prompt Template

The following is a recommended Mutsumi integration instruction to embed in your Agent's system prompt.

```markdown
## Task Management (Mutsumi Integration)

You have access to a local task file at `./tasks.json`.
When the user asks you to manage tasks, read and write this file.

Schema:
- Required fields: id (unique string), title (string), status ("pending" | "done")
- Optional fields: scope ("day"|"week"|"month"|"inbox"), priority ("high"|"normal"|"low"), tags (string[]), children (Task[]), due_date (ISO date), description (string)
- Preserve any fields you don't recognize — do NOT delete them
- Use atomic write (temp file + rename) when possible
- Generate UUIDv7 for new task IDs

Example task:
{"id":"01JQ...","title":"Fix auth","status":"pending","scope":"day","priority":"high","tags":["dev"],"children":[]}
```

## 4. Read Protocol (Mutsumi → Agent)

### 4.1 Event Log

When the user operates in the TUI, Mutsumi appends events to `events.jsonl` (JSONL format, one event per line).

```jsonl
{"ts":"2026-03-21T10:00:00Z","event":"task_completed","task_id":"01JQ...","title":"修复缓存 Bug","source":"tui"}
{"ts":"2026-03-21T10:01:22Z","event":"task_created","task_id":"01JQ...","title":"写单元测试","source":"tui"}
{"ts":"2026-03-21T10:05:00Z","event":"task_deleted","task_id":"01JQ...","title":"过时的任务","source":"tui"}
{"ts":"2026-03-21T10:06:30Z","event":"task_updated","task_id":"01JQ...","changes":{"priority":"high→low"},"source":"tui"}
```

### 4.2 Event Types

| Event             | Fields                                    | Description              |
|-------------------|-------------------------------------------|--------------------------|
| `task_created`    | task_id, title                            | New task created         |
| `task_completed`  | task_id, title                            | Task marked done         |
| `task_deleted`    | task_id, title                            | Task deleted             |
| `task_updated`    | task_id, changes (dict)                   | Task fields modified     |
| `schema_error`    | file, message                             | JSON validation failed   |

### 4.3 Agent Consumption

Agents can consume the event stream in the following ways:

```bash
# Real-time monitoring (shell)
tail -f events.jsonl | jq .

# Reference in Agent prompt
"Check events.jsonl for recent user actions on tasks"
```

### 4.4 Event Log Rotation

- Retains the most recent 1000 events by default
- Older events are automatically truncated
- Configurable via `events.max_lines` in `config.toml`

## 5. Schema Discovery

Agents can retrieve the current JSON Schema via CLI.

```bash
mutsumi schema
# Outputs JSON Schema to stdout for Agent to understand the data structure

mutsumi schema --format markdown
# Outputs field descriptions in Markdown format
```

## 6. Error Handling

### 6.1 When Agent Writes Bad Data

```
Agent writes invalid JSON
       │
       ▼
Mutsumi watchdog detects change
       │
       ▼
Parse fails → TUI shows error banner
       │       "tasks.json has errors, showing last valid state"
       │
       ▼
Error logged to stderr + error.log
       │
       ▼
Event emitted: {"event":"schema_error","file":"tasks.json","message":"..."}
       │
       ▼
Agent can read error.log or events.jsonl to self-correct
```

### 6.2 Self-healing Prompt

It is recommended to include the following in the Agent prompt:

```markdown
After writing to tasks.json, check ~/.local/share/mutsumi/error.log
for any schema validation errors. If errors exist, fix and rewrite.
```

## 7. Multi-Agent Coordination

When multiple Agents operate on the same `tasks.json` simultaneously:

### 7.1 Recommendations

1. **Read-before-write** — Always read the latest version before writing
2. **Minimize write scope** — Only modify the tasks you care about; don't reorder others
3. **Idempotent operations** — Operations like marking complete should be idempotent (no error on repeat)
4. **Use unique IDs** — UUIDv7 ensures IDs from different Agents never collide

### 7.2 Conflict Resolution

Mutsumi does not provide a locking mechanism. Conflict strategy: **Last Write Wins**.

In practice, since Agent writes are discrete (typically seconds to minutes apart), the probability of conflict is extremely low.
