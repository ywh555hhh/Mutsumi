---
name: mutsumi-manage
description: >
  Add, edit, complete, or remove tasks in mutsumi.json — a local JSON task board.
  Use when the user asks to manage tasks, create new items, mark tasks done,
  change priority/scope/tags, or delete tasks.
---

# Mutsumi Task Management

You have access to a local task board stored in `mutsumi.json` (project root)
or `~/.mutsumi/mutsumi.json` (personal tasks).

## Preferred: CLI Commands

Use the `mutsumi` CLI for safe, validated operations:

```bash
# Add a task
mutsumi add "Fix login bug" --priority high --scope day --tags "bugfix,urgent"

# Mark task done (prefix matching — no need for full ID)
mutsumi done 01JQ

# Edit task fields
mutsumi edit 01JQ --title "New title" --priority low --scope week

# Remove task and its children
mutsumi rm 01JQ

# List tasks (with optional filters)
mutsumi list --scope day --no-done
```

## Alternative: Direct JSON Write

When CLI is not available or you need batch operations:

1. Read the current `mutsumi.json`
2. Modify the `tasks` array
3. Write the ENTIRE file back (never partial writes)
4. Use atomic write: write to temp file, then `os.rename()`
5. Generate a unique ID (ULID) for each new task
6. Set `created_at` to current ISO 8601 datetime for new tasks
7. Set `completed_at` when changing status to `"done"`

**CRITICAL: Preserve any fields you don't recognize — never delete unknown keys.**

For the complete schema, see [schema reference](../references/schema.md).
