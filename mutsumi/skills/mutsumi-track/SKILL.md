---
name: mutsumi-track
description: >
  Automatically track your work progress by updating mutsumi.json as you
  complete steps. Use when executing a multi-step task to keep the task board
  in sync with actual progress.
user-invocable: false
---

# Mutsumi Progress Tracking

When you are working on a task that exists in `mutsumi.json`, keep the board
in sync with your actual progress.

## When to Update

- **Starting work**: If the task exists but has no subtasks, consider whether
  the work should be broken into trackable steps first (see mutsumi-plan).
- **Completing a step**: Mark the corresponding subtask as done.
- **Finishing the whole task**: Mark the parent task as done.
- **Encountering a blocker**: Add a note to the task description.

## How to Update

Prefer CLI commands for individual updates:

```bash
mutsumi done 01JQ          # Mark a task/subtask complete
mutsumi edit 01JQ -d "Blocked: waiting for API key"
```

For batch progress updates (multiple subtasks at once), use direct JSON write
with atomic file operations.

## Rules

- Only update tasks that correspond to your current work.
- Do not create new top-level tasks — that is mutsumi-plan's job.
- Set `completed_at` to current ISO 8601 datetime when marking done.
- Preserve all unknown fields in the JSON.

For the complete schema, see [schema reference](../references/schema.md).
