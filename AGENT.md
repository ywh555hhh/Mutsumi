# Mutsumi — Agent Cheat Sheet

> One-page reference for AI agents that manage tasks via Mutsumi.

## Quick Start

Mutsumi is a local TUI that watches the active task file and re-renders on save.

- **Canonical project file:** `./mutsumi.json`
- **Legacy fallback:** `./tasks.json`
- **Preferred workflow:** use the `mutsumi` CLI when possible
- **Direct JSON is allowed:** read the whole file, update it, write it back atomically

If both files are absent, new projects should create **`mutsumi.json`**.

## Task File Discovery

Mutsumi resolves the active file in this order:

1. Explicit CLI `--path`
2. `./mutsumi.json`
3. `./tasks.json` (backward-compatible fallback)
4. Default target for new projects: `./mutsumi.json`

## Schema

| Field | Type | Required | Default | Notes |
|---|---|---:|---|---|
| `id` | string | Yes | — | Unique ID, UUIDv7 recommended |
| `title` | string | Yes | — | Task title |
| `status` | string | Yes | `"pending"` | `"pending"` or `"done"` |
| `scope` | string | No | `"inbox"` | `"day"`, `"week"`, `"month"`, `"inbox"` |
| `priority` | string | No | `"normal"` | `"high"`, `"normal"`, `"low"` |
| `tags` | string[] | No | `[]` | Free-form labels |
| `children` | Task[] | No | `[]` | Recursive subtasks |
| `due_date` | string | No | — | ISO date, e.g. `"2026-03-25"` |
| `description` | string | No | — | Longer text |
| `created_at` | string | No | auto | ISO timestamp |
| `completed_at` | string | No | — | Set when status becomes `done` |

## Behavioral Rules

1. **Preserve unknown fields.** Never delete fields you do not recognize.
2. **Write the whole file.** Do not attempt partial in-place edits.
3. **Use atomic writes.** Temp file + rename/replace.
4. **Prefer `mutsumi.json`.** Only use `tasks.json` when the project is still on the legacy filename.
5. **Keep enums valid.**
   - `status`: `pending` / `done`
   - `priority`: `high` / `normal` / `low`
   - `scope`: `day` / `week` / `month` / `inbox`

## CLI Commands

```bash
mutsumi add "title" --priority high --scope day --tags "dev,urgent"
mutsumi done <id-prefix>
mutsumi edit <id-prefix> --title "new title" --priority low
mutsumi rm <id-prefix>
mutsumi list
mutsumi validate
mutsumi schema
mutsumi init                  # create ./mutsumi.json
mutsumi init --personal       # create ~/.mutsumi/mutsumi.json
mutsumi init --project        # create ./mutsumi.json and register current repo
mutsumi setup --agent claude-code
mutsumi project add /path/to/repo
mutsumi migrate
```

## Direct JSON Protocol

When working without the CLI:

1. Detect the active file (`mutsumi.json` first, `tasks.json` fallback)
2. Read the entire JSON object
3. Modify the `tasks` array
4. Write the **entire file** back atomically
5. Keep all unknown top-level and task-level fields intact

File shape:

```json
{
  "version": 1,
  "tasks": [
    {
      "id": "01JQ8X7K3M0000000000000001",
      "title": "Refactor auth module",
      "status": "pending",
      "scope": "day",
      "priority": "high",
      "tags": ["dev", "backend"],
      "children": []
    }
  ]
}
```

## Minimal Python Example

```python
from __future__ import annotations

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
    "id": "task-001",
    "title": "Write weekly report",
    "status": "pending",
    "scope": "week",
    "priority": "normal",
    "tags": ["life"],
    "children": [],
}
data.setdefault("tasks", []).append(new_task)

with tempfile.NamedTemporaryFile("w", dir=".", suffix=".tmp", delete=False, encoding="utf-8") as tmp:
    json.dump(data, tmp, ensure_ascii=False, indent=2)
    tmp_path = Path(tmp.name)

os.replace(tmp_path, path)
```

## Agent Integration Setup

```bash
# Install Mutsumi skills into the agent's skill directory
mutsumi setup --agent claude-code
mutsumi setup --agent codex-cli
mutsumi setup --agent gemini-cli
mutsumi setup --agent opencode

# Install skills AND append project instructions to CLAUDE.md / AGENTS.md / etc.
mutsumi setup --agent claude-code --mode skills+project-doc

# Print a manual snippet for unsupported agents
mutsumi setup --agent aider --mode snippet
mutsumi setup --agent custom --mode snippet
```

### Mode Summary

- `skills` — install bundled `SKILL.md` packages only
- `skills+project-doc` — install skills and append a project snippet to the agent doc
- `snippet` — print copyable instructions to stdout

## Event Log

If event logging is enabled, Mutsumi appends JSONL records to the platform data directory.
By default this is typically:

```text
~/.local/share/mutsumi/events.jsonl
```

Example records:

```jsonl
{"timestamp":"2026-03-23T10:00:00+00:00","type":"task_added","task_id":"01JQ...","title":"Write tests"}
{"timestamp":"2026-03-23T10:02:00+00:00","type":"task_toggled","task_id":"01JQ..."}
{"timestamp":"2026-03-23T10:05:00+00:00","type":"priority_changed","task_id":"01JQ..."}
```

## Safe Defaults for Agents

- Prefer `mutsumi.json`
- Use the CLI when the task is simple CRUD
- If writing JSON directly, use atomic replace
- Preserve unknown fields exactly
- Do not silently delete user tasks
- Run `mutsumi validate` after large edits if you are unsure
