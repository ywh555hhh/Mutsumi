---
name: mutsumi-context
description: >
  Load the current task board state from mutsumi.json to understand project
  priorities and active work. Use at the beginning of a session or when you
  need context about what the project is working on.
user-invocable: false
---

# Mutsumi Context Loader

Before starting work, read the task board to understand current priorities.

## Steps

1. Check for `mutsumi.json` in the project root (current directory).
2. If found, read it and note:
   - How many tasks are pending vs. done
   - What scope the pending tasks are in (day = urgent, week = soon)
   - Any high-priority pending tasks
   - Parent tasks with incomplete subtasks (active work in progress)
3. Use this context to:
   - Prioritize the user's request relative to existing tasks
   - Avoid duplicating work that is already tracked
   - Update relevant tasks as you complete work

## Do Not

- Do not modify any tasks during context loading.
- Do not create new tasks unless the user asks.
- Do not output the full task list — just internalize the priorities.

For the complete schema, see [schema reference](../references/schema.md).
