# RFC-009: Calendar View — Time Navigation for Multi-Source Tasks

| Field | Value |
|---|---|
| **RFC** | 009 |
| **Title** | Calendar View — Time Navigation for Multi-Source Tasks |
| **Status** | Draft |
| **Author** | Wayne (ywh) |
| **Created** | 2026-03-23 |

---

## 1. Abstract

Mutsumi already has the raw semantics needed for a calendar:

- `due_date` on tasks
- effective scope derived from dates
- a Main dashboard that aggregates multiple sources
- source tabs for focused editing
- a detail panel for drill-down

What is missing is the **time view itself**.

This RFC proposes adding a built-in **calendar view** as a first-class product capability. The calendar should not introduce a second task system or a separate data model. Instead, it should provide a new way to navigate the existing task model by date.

The calendar belongs naturally in the **Main/dashboard layer**: a cross-source, time-oriented view that complements the existing list-oriented source tabs.

The long-term goal is a full-featured calendar experience for task planning and review. The implementation, however, should land in phases.

---

## 2. Motivation

### 2.1 The current gap

Mutsumi can already answer questions like:

- what is due today?
- what belongs to this week?
- what belongs to this month?

But it answers them through **list buckets**, not through an actual time map.

That means users can filter tasks by `Today`, `Week`, or `Month`, yet still cannot:

- glance at distribution across dates
- see sparse vs crowded days
- jump from a specific date to its tasks
- understand scheduling pressure visually

### 2.2 Why this matters for a todo product

A todo system without a calendar forces users to mentally project deadlines from list rows into time.

That is fine for tiny lists. It gets worse when the user is juggling:

- personal tasks
- one or more active projects
- agent-written backlog churn
- due dates that span the next few days or weeks

For Mutsumi's target user — someone already living in multiple threads — the missing capability is not more task metadata. It is **a better temporal surface**.

### 2.3 Why Main/dashboard is the right home

The current architecture already distinguishes between:

- **Main** — cross-source summary
- **source tabs** — focused editing and inspection

A calendar is fundamentally a **cross-source time navigator**. That makes it a better fit for the Main layer than for replacing source-local task lists.

---

## 3. Goals

| Goal | Description |
|---|---|
| Multi-source time view | Show dated tasks from personal + project sources in one calendar surface |
| No new task model | Reuse existing `Task`, `due_date`, `scope`, and source semantics |
| Keyboard + mouse parity | Date navigation and drill-down must work from both input modes |
| Smooth drill-down | Users should move from date → tasks → detail/source tab without confusion |
| Keep list views relevant | Calendar complements existing list views; it does not replace them |
| Future-ready full target | Design for month/week/day/agenda capability even if implementation lands in phases |

---

## 4. Non-goals

This RFC does **not** propose:

- network calendar sync
- Google Calendar / iCal integration
- a separate calendar-specific JSON file
- converting Mutsumi into a meeting or event scheduler
- abandoning the current list-based source tabs
- changing the core task schema for the first release of calendar support

---

## 5. Data Semantics

### 5.1 Calendar anchor

The calendar uses **`due_date`** as its primary time anchor.

If a task has no `due_date`, it has no exact calendar placement and should not appear on a dated cell by default.

### 5.2 Relationship to `scope`

`scope` remains a planning bucket, not the canonical calendar coordinate.

Resolution rules stay unchanged:

```text
explicit scope > due_date auto-derivation > inbox
```

Implications:

- list views continue to use effective scope
- calendar views use `due_date` when present
- calendar should not reinterpret `scope` as a substitute for a missing date

### 5.3 Tasks without `due_date`

Tasks without `due_date`:

- stay visible in list views and dashboard summaries
- do not appear on the date grid by default
- may appear in an auxiliary “undated” agenda/sidebar in later phases

### 5.4 Invalid dates

If `due_date` is malformed:

- the task should not crash the calendar view
- the task should be excluded from date placement
- the existing graceful-degradation path remains authoritative

### 5.5 Overdue tasks

Overdue tasks remain anchored to their original `due_date`, but the calendar should clearly signal that they are overdue.

Examples:

- accent color
- overdue badge
- special density marker in month view

### 5.6 Recurring tasks

Mutsumi already supports recurrence metadata in the writer layer. The calendar should treat recurrence as a task-generation/update concern, not as a second rendering model.

That means:

- calendar reads the current task state
- calendar does not independently expand recurrence rules into phantom events
- future advanced recurrence visualization may be layered on top later

### 5.7 Multi-source semantics

Calendar entries must preserve source identity.

Every rendered task in the calendar should still know:

- which source it came from
- whether it is personal or project-owned
- how to jump back to that source tab or detail view

---

## 6. Information Architecture

### 6.1 Placement

Calendar should be introduced as a **Main-layer view mode**, not as a replacement for source tabs.

Recommended structure:

```text
[★ Main] [Personal] [project-a] [project-b]
          └─ Main view modes: Dashboard / Calendar
```

Possible UI forms:

- segmented control inside Main
- keyboard toggle while Main is active
- footer action / header action when focused on Main

### 6.2 Why not a top-level tab

A separate top-level `Calendar` tab is possible, but weaker, because it splits the Main mental model into two competing aggregation surfaces.

Main should remain the cross-source layer, with:

- summary/dashboard view
- time/calendar view

### 6.3 Relationship to source tabs

Source tabs remain the place for direct task CRUD and source-scoped filtering.

Calendar acts as a navigation and planning surface that can jump into:

- the source tab
- the detail panel
- eventually inline quick-create/edit flows

---

## 7. Interaction Model

### 7.1 Core interactions

The calendar must support:

1. navigate across dates
2. inspect tasks on a date
3. open task detail
4. jump to source context
5. switch calendar granularity / mode

### 7.2 Keyboard requirements

Examples of required keyboard support:

| Action | Keyboard expectation |
|---|---|
| Move day-to-day | arrow keys or preset-equivalent navigation |
| Move across weeks | up/down or week-jump keys |
| Open selected date | `Enter` |
| Switch calendar mode | dedicated shortcut or focusable toggle |
| Return to list/dashboard | `Escape` or explicit back action |
| Jump into source tab | `Enter` / secondary action on selected task |

The exact keys should follow the active preset philosophy:

- `arrows` remains default
- `vim` and `emacs` remain opt-in

### 7.3 Mouse requirements

Examples of required mouse support:

| Action | Mouse expectation |
|---|---|
| Select a date | click date cell |
| Open date contents | click date cell or task chip |
| Open task detail | click task chip |
| Switch mode | click segmented control / tab |
| Jump to source | click source badge or action |

### 7.4 Triple input parity

The calendar must respect RFC-004 principles.

If a user can reach a calendar action with one surface, they should not be trapped there.

Examples:

- selecting a date cannot be mouse-only
- switching calendar modes cannot be keyboard-only
- source drill-down should have a CLI-adjacent interpretation only where it makes sense, but interactive navigation itself is TUI-specific

---

## 8. View Modes (Full Target)

The product goal is a full-featured calendar system, even if rollout is phased.

### 8.1 Month view

Best for:

- density scanning
- seeing spread across weeks
- identifying overloaded days

Expected behavior:

- grid of dates
- per-cell task summaries or density indicators
- overflow treatment for crowded days

### 8.2 Week view

Best for:

- operational planning
- a tighter look at the next 7 days
- comparing near-term commitments across sources

### 8.3 Day view

Best for:

- focused execution
- viewing one day's items with richer detail

### 8.4 Agenda view

Best for:

- chronological reading of dated tasks
- low-density terminal setups
- accessibility / narrow terminal fallback

---

## 9. Feature Matrix (Product Target)

| Capability | Target state |
|---|---|
| Month / week / day / agenda | Supported |
| Multi-source aggregation | Supported |
| Source badges | Supported |
| Date drill-down | Supported |
| Detail panel integration | Supported |
| Quick create on date | Supported |
| Quick edit from date | Supported |
| Drag to reschedule | Supported later |
| Overdue visualization | Supported |
| Undated task companion view | Supported later |
| Recurrence-aware rendering | Supported incrementally |

---

## 10. Phased Rollout

The calendar should be designed as a full product capability, but implemented in phases.

### Phase A — Read-only calendar foundation

Scope:

- Main-layer calendar mode
- Month view and/or agenda fallback
- multi-source aggregation
- select date → inspect tasks
- task chip → open detail panel
- source jump from selected task

What this proves:

- the data semantics are sound
- the calendar belongs naturally in Main
- users get immediate value without rewriting CRUD flows

### Phase B — Lightweight task actions

Scope:

- create task directly for selected date
- edit task due date from calendar context
- quick priority/tag changes from calendar detail path
- better week/day navigation

What this adds:

- calendar becomes operational, not just observational

### Phase C — Full interaction layer

Scope:

- drag or keyboard move-to-date
- denser day/week rendering
- better overflow handling
- recurring-task cues
- optional undated companion lane / agenda enhancements

What this completes:

- calendar becomes a first-class planning and maintenance surface

---

## 11. Alternatives Considered

### 11.1 Separate top-level Calendar tab

**Rejected for now.**

Reason:

- duplicates the Main-layer aggregation concept
- creates ambiguity between “Main” and “Calendar” as the cross-source overview

### 11.2 Replace scope filters with calendar

**Rejected.**

Reason:

- source-local list filters still serve fast textual workflows well
- users need both list buckets and time navigation

### 11.3 Add a separate calendar data model

**Rejected.**

Reason:

- breaks the elegant single-source-of-truth model
- duplicates semantics already present in `due_date`
- increases migration and consistency risk unnecessarily

---

## 12. Implementation Sketch

This section does not lock exact code structure, but the natural anchors are already visible in the codebase.

### 12.1 Existing foundations to reuse

| Area | Existing responsibility | Calendar relevance |
|---|---|---|
| `mutsumi/core/loader.py` | file resolution, loading, scope derivation | reuse `due_date` semantics and filtering helpers |
| `mutsumi/core/sources.py` | multi-source registry | reuse aggregation source map |
| `mutsumi/app.py` | source-tab orchestration | host Main/dashboard/calendar mode switching |
| `mutsumi/tui/main_dashboard.py` | Main aggregated surface | likely sibling or extension point for calendar UI |
| `mutsumi/tui/scope_filter.py` | source-local filters | reference for secondary navigation patterns |
| `mutsumi/tui/detail_panel.py` | task drill-down | reuse as task-inspection endpoint from calendar |

### 12.2 Likely UI shape

A plausible path is:

- keep `MainDashboard` as the summary surface
- add a new widget for the calendar surface
- let `app.py` switch Main between dashboard mode and calendar mode
- preserve source tabs and detail panel interactions

### 12.3 Data transformation layer

Calendar rendering will need a light projection layer that maps:

```text
(source_name, task) → date bucket → rendered cell/task summary
```

This is a view transformation, not a schema change.

---

## 13. Testing Strategy

### 13.1 Data semantics tests

- tasks with valid `due_date` land on correct dates
- tasks with invalid `due_date` degrade safely
- overdue tasks are marked correctly
- tasks without `due_date` do not appear in dated cells
- multi-source aggregation preserves source identity

### 13.2 TUI behavior tests

- keyboard-only calendar navigation works
- mouse-only date selection works
- switching between Main dashboard and calendar works
- selecting a calendar task opens detail correctly
- source drill-down reaches the correct tab

### 13.3 Manual beta scenarios

- personal + multiple project sources populated with dates
- one crowded week and one sparse week
- mix of overdue, due-today, future, and undated tasks
- narrow terminal fallback behavior

---

## 14. Open Questions

1. Should the first shipped version lead with **month view**, **agenda view**, or both?
2. Should undated tasks be visible beside the calendar from the start, or deferred?
3. How much inline editing belongs in the first interactive release versus keeping edits in the detail panel/task form?
4. What is the best overflow model for dense month cells in a terminal UI?
5. Should calendar mode live behind a segmented control in Main, a hotkey, or both?

---

## 15. Conclusion

Mutsumi already understands time semantically, but not yet visually.

A built-in calendar is the natural next step because it:

- reuses existing `due_date` semantics
- strengthens the Main-layer command-center vision
- gives multi-threaded users a better way to see scheduling pressure
- complements list views without replacing them

The right direction is therefore:

- **one task model**
- **one source architecture**
- **multiple view surfaces**

List view answers “what is here?”
Calendar view answers “when does it land?”

Mutsumi should have both.
