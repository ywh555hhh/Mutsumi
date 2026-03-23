# Mutsumi Agent Integration Protocol

| Version | 1.0 |
|---------|-----|
| Status  | Draft |
| Date    | 2026-03-23 |

> **[中文版](./AGENT_PROTOCOL_cn.md)** | **[日本語版](./AGENT_PROTOCOL_ja.md)**

---

## 1. Overview

This document defines how external agents — AI CLIs, custom scripts, or simple shell tooling — integrate with Mutsumi.

**Core principle:** Mutsumi is agent-agnostic. Any program that can correctly read and write the task file can act as a controller.

### 1.1 Active file naming

- **Canonical task file:** `mutsumi.json`
- **Legacy fallback:** `tasks.json`

For new projects, agents should target **`./mutsumi.json`**.
If a project still uses `tasks.json`, agents may continue to read and write that legacy file.

### 1.2 Resolution order

When no explicit path is given, Mutsumi resolves the active task file like this:

1. CLI `--path`
2. `./mutsumi.json`
3. `./tasks.json`
4. default target for new projects: `./mutsumi.json`

---

## 2. Supported Agents

| Agent | Integration level |
|---|---|
| Claude Code | Native |
| Codex CLI | Native |
| Gemini CLI | Native |
| OpenCode | Native |
| Aider | Native |
| Custom scripts | Native |

“Native” means no network bridge or SDK is required. File I/O is enough.

---

## 3. Write Protocol (Agent → Mutsumi)

### 3.1 Workflow

```text
1. Resolve the active task file
2. Read the current JSON object
3. Modify the tasks array
4. Write the ENTIRE file back atomically
5. Mutsumi detects the save and re-renders
```

### 3.2 Rules

| Rule | Description |
|---|---|
| Preserve unknown fields | Never delete fields you don't recognize |
| Atomic write | Write temp file + `os.replace()` / rename |
| Valid JSON | File must remain valid JSON after every write |
| Valid IDs | New tasks should use UUIDv7 or another unique string |
| Required fields | Every task must have `id`, `title`, `status` |
| Enum compliance | `status`: `pending` / `done`; `priority`: `high` / `normal` / `low`; `scope`: `day` / `week` / `month` / `inbox` |

### 3.3 Minimal Python example

```python
from __future__ import annotations

import datetime as dt
import json
import os
import tempfile
from pathlib import Path


def resolve_task_file() -> Path:
    preferred = Path("mutsumi.json")
    legacy = Path("tasks.json")
    if preferred.exists():
        return preferred
    if legacy.exists():
        return legacy
    return preferred


path = resolve_task_file()

data = {"version": 1, "tasks": []}
if path.exists():
    data = json.loads(path.read_text(encoding="utf-8"))

new_task = {
    "id": f"task-{int(dt.datetime.now(dt.UTC).timestamp())}",
    "title": "Fix login bug",
    "status": "pending",
    "scope": "day",
    "priority": "high",
    "tags": ["bugfix"],
    "created_at": dt.datetime.now(dt.UTC).isoformat(),
    "children": [],
}
data.setdefault("tasks", []).append(new_task)

with tempfile.NamedTemporaryFile("w", dir=".", suffix=".tmp", delete=False, encoding="utf-8") as tmp:
    json.dump(data, tmp, ensure_ascii=False, indent=2)
    tmp_path = Path(tmp.name)

os.replace(tmp_path, path)
```

### 3.4 Completing a task

```python
for task in data["tasks"]:
    if task["id"] == target_id:
        task["status"] = "done"
        task["completed_at"] = dt.datetime.now(dt.UTC).isoformat()
        break
```

---

## 4. Prompt Template

The following snippet is safe to include in an agent instruction file.

```markdown
## Mutsumi Task Integration

This project uses Mutsumi for task management.
Tasks live in `./mutsumi.json` (fallback: `./tasks.json`).

Rules:
- Read the whole file before writing
- Preserve unknown fields
- Write the ENTIRE file back atomically
- Required task fields: `id`, `title`, `status`
- Valid status values: `pending`, `done`
- Prefer `mutsumi` CLI commands for simple CRUD
```

---

## 5. CLI-First Integration

For simple task operations, agents should prefer the CLI over handwritten JSON mutation.

```bash
mutsumi add "Fix auth" --priority high --scope day --tags "dev,backend"
mutsumi done <id-prefix>
mutsumi edit <id-prefix> --title "New title" --priority low
mutsumi rm <id-prefix>
mutsumi list
mutsumi validate
mutsumi schema
```

Advantages:

- less schema drift risk
- less chance of partial writes
- consistent file resolution (`mutsumi.json` first, `tasks.json` fallback)

---

## 6. Event Log (Optional)

Mutsumi can append JSONL events for local audit/history use.
The default path is typically:

```text
~/.local/share/mutsumi/events.jsonl
```

### 6.1 Example events

```jsonl
{"timestamp":"2026-03-23T10:00:00+00:00","type":"task_added","task_id":"01JQ...","title":"Write tests"}
{"timestamp":"2026-03-23T10:05:00+00:00","type":"task_edited","task_id":"01JQ...","title":"Write more tests"}
{"timestamp":"2026-03-23T10:06:00+00:00","type":"task_deleted","task_id":"01JQ...","title":"Obsolete task"}
```

### 6.2 Current event names

Examples emitted by the app include:

- `task_added`
- `child_task_added`
- `task_edited`
- `task_deleted`
- `task_toggled`
- `priority_changed`
- `task_reordered`
- `task_pasted`

Event logging is additive metadata, not part of the task-file contract.

---

## 7. Error Handling

### 7.1 If an agent writes invalid JSON

```text
agent writes invalid JSON
        ↓
Mutsumi detects file change
        ↓
parse fails
        ↓
TUI shows an error banner instead of crashing
        ↓
last good state remains visible until the file is fixed
```

### 7.2 Recommended recovery flow

If an agent is unsure whether its write succeeded:

1. run `mutsumi validate`
2. inspect the active task file
3. check the local error log if needed (default: `~/.local/share/mutsumi/error.log`)

### 7.3 Self-healing instruction

```markdown
After writing to the Mutsumi task file, run `mutsumi validate` if you are unsure the file is still valid JSON.
```

---

## 8. Setup Modes

`mutsumi setup --agent <name>` supports three modes:

| Mode | Behavior |
|---|---|
| `skills` | Install bundled Mutsumi skills into the agent's skill directory |
| `skills+project-doc` | Install skills and append the integration snippet to `CLAUDE.md`, `AGENTS.md`, `GEMINI.md`, or `opencode.md` |
| `snippet` | Print a copyable prompt snippet to stdout |

### 8.1 Default behavior

```bash
mutsumi setup --agent claude-code
```

This installs skills only.
It does **not** modify project instruction files unless `--mode skills+project-doc` is explicitly requested.

---

## 9. Multi-Agent Coordination

### 9.1 Same project file

When multiple agents touch the same `mutsumi.json`:

1. always read before write
2. minimize unrelated edits
3. keep operations idempotent where possible
4. expect **last write wins** if two writers race

### 9.2 Different project files

In multi-source setups, each project should keep its own task file.
This is the preferred isolation model:

```text
project-a/mutsumi.json
project-b/mutsumi.json
~/.mutsumi/mutsumi.json   # personal tasks
```

Mutsumi can aggregate these in the UI without requiring agents to share a single file.

---

## 10. Compatibility Summary

- Schema is the same for `mutsumi.json` and legacy `tasks.json`
- New docs, new examples, and new projects should use `mutsumi.json`
- `tasks.json` remains supported for backward compatibility only
