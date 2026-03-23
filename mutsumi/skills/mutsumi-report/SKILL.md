---
name: mutsumi-report
description: >
  Read mutsumi.json and generate a concise status report of all tasks.
  Summarize pending, done, and blocked items. Highlight priorities and
  suggest next actions.
disable-model-invocation: true
---

# Mutsumi Status Report

Read the task board and generate a clear, actionable summary.

## Steps

1. Read `mutsumi.json` (project root) and `~/.mutsumi/mutsumi.json` (personal).
2. Count tasks by status: pending vs. done.
3. Group pending tasks by scope (day → week → month → inbox).
4. Highlight high-priority items.
5. Report subtask progress for parent tasks.

## Output Format

```
## Task Board Status

**Progress**: 12/20 tasks done (60%)

### Today (day)
- [x] Fix login bug (high)
- [ ] Write unit tests (normal)

### This Week (week)
- [ ] Implement auth middleware (high, 2/4 subtasks done)
- [ ] Update API docs (low)

### Inbox
- [ ] Research caching options (normal)

### Suggested Next
1. Finish "Implement auth middleware" — 2 subtasks remaining
2. "Write unit tests" — high priority, unblocked
```

Adapt the format based on what is actually in the file. If there are no tasks,
say so. If the file doesn't exist, tell the user how to create one.
