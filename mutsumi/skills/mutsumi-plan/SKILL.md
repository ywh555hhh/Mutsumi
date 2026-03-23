---
name: mutsumi-plan
description: >
  Break down a complex goal into actionable subtasks in mutsumi.json.
  Use when the user describes a large feature, project, or multi-step task
  that needs to be decomposed into trackable steps.
---

# Mutsumi Task Planning

Decompose a complex goal into a structured task tree in `mutsumi.json`.

## Process

1. **Understand the goal**: Read the user's request carefully.
2. **Read current board**: Check `mutsumi.json` for existing related tasks.
3. **Decompose**: Break the goal into 3-8 concrete, actionable subtasks.
4. **Create the parent task** with subtasks as `children`:

```bash
# Create the parent task first
mutsumi add "Implement user auth" --priority high --scope week --tags "feature"
```

Then write the subtasks directly to `mutsumi.json` as `children` of the parent:

```json
{
  "id": "PARENT_ID",
  "title": "Implement user auth",
  "children": [
    { "id": "UNIQUE_1", "title": "Design DB schema", "status": "pending" },
    { "id": "UNIQUE_2", "title": "Write auth middleware", "status": "pending" },
    { "id": "UNIQUE_3", "title": "Add login endpoint", "status": "pending" },
    { "id": "UNIQUE_4", "title": "Write tests", "status": "pending" }
  ]
}
```

## Guidelines

- Each subtask should be completable in one focused work session.
- Use descriptive titles — someone reading the board should understand what to do.
- Set appropriate `scope` on the parent: `day` for today's work, `week` for this week.
- Set `priority` based on urgency and user input.
- Tag tasks for easy filtering (`feature`, `bugfix`, `docs`, `test`, etc.).
- Generate unique IDs for every task and subtask.
- Set `created_at` on all new tasks.

For the complete schema, see [schema reference](../references/schema.md).
