# RFC-010: Capability-First Interaction Architecture — Actions Before Inputs

| Field | Value |
|---|---|
| **RFC** | 010 |
| **Title** | Capability-First Interaction Architecture — Actions Before Inputs |
| **Status** | Implemented in `1.1.0b1` |
| **Author** | Wayne (ywh) |
| **Created** | 2026-03-24 |
| **Implementation note** | Landed in the `1.1.0b1` beta line with semantic-first bindings, onboarding contract updates, source-aware create flow, and layered confirm/back/cancel behavior. |

---

## 1. Abstract

Mutsumi already believes in keyboard, mouse, and CLI parity, but parity alone is not enough.

The current interaction model still shows a structural weakness: in too many places, input behavior is defined **per widget** or **per screen** instead of being derived from a stable capability model. The result is user-visible inconsistency:

- `Enter` does not always feel like the primary confirm/select action
- arrow-key navigation is not always mapped to a clear spatial model
- onboarding and TUI flows can feel locally implemented rather than systemically coherent
- power shortcuts and focus-based navigation are mixed without a stable hierarchy

This RFC proposes a stronger interaction philosophy:

> **Define capabilities first. Define input mappings second.**

Mutsumi should first define what actions the product supports, independent of any specific surface. Only after that should it define how those actions are expressed through:

1. keyboard navigation + confirm
2. keyboard power shortcuts
3. mouse
4. CLI

This creates a capability-first interaction architecture that makes the app more predictable, more teachable, and more extensible.

---

## 2. Problem Statement

### 2.1 Current symptom: keyboard feels inconsistent

Recent user feedback shows that the keyboard model feels confusing in practice.

Examples:

- `Enter` often should mean **confirm / select / open the focused thing**, but does not always behave that way
- `Up` / `Down` in onboarding do not always behave like basic vertical navigation
- `Left` / `Right` and `Up` / `Down` can blur together instead of expressing distinct spatial roles
- some flows feel built around ad-hoc key handlers instead of a shared interaction contract

This is not just a keybinding bug. It is a design-layer issue.

### 2.2 Root cause

The root problem is that the system is still too close to this model:

```text
screen/widget -> local key handling -> local behavior
```

Instead of this model:

```text
capability -> semantic action -> surface-specific mapping -> rendered interaction
```

When interaction is defined widget-first, semantic drift is almost guaranteed.

### 2.3 Why parity alone does not solve this

RFC-004 correctly argues that user-facing functionality should be reachable across keyboard, mouse, and CLI where appropriate.

However, parity by itself answers only:

- **Can the user reach the action?**

It does not fully answer:

- **Does the action mean the same thing across contexts?**
- **Does the user understand what the primary action is?**
- **Is keyboard interaction internally coherent?**

This RFC therefore extends the interaction philosophy beyond parity into semantic consistency.

---

## 3. Design Principle

### 3.1 Core rule

> **Actions before inputs. Semantics before bindings.**

The system must define product actions first, then map them into each input surface.

### 3.2 The four interaction surfaces

Mutsumi should recognize four first-class interaction surfaces:

| Surface | Role |
|---|---|
| **Keyboard — navigation/confirm** | Focus movement + primary action, analogous to mouse interaction in keyboard form |
| **Keyboard — power shortcuts** | Fast direct commands for experienced users |
| **Mouse** | Click-driven interaction with full core coverage |
| **CLI** | Headless, scriptable, non-interactive access to product capabilities |

These are not four separate products. They are four mappings over the same capability model.

### 3.3 The capability hierarchy

The architecture should look like this:

```text
Capability layer
  -> Semantic actions
    -> Surface mappings
      -> UI/CLI implementation
```

That means:

1. define what the user can do
2. define the semantic actions required
3. define how each surface expresses them
4. implement concrete controls, bindings, and commands

---

## 4. Capability Layer

The capability layer is input-agnostic.

Example capability categories:

### 4.1 Navigation capabilities

- move focus
- move within a list
- move within a grid
- move between sections
- move between top-level contexts
- go back
- cancel

### 4.2 Selection / confirmation capabilities

- select focused item
- confirm current choice
- open focused item
- apply highlighted default

### 4.3 View / mode capabilities

- switch tab
- switch sub-filter
- switch Main mode
- open help
- open search
- close panel

### 4.4 Task operation capabilities

- create task
- choose target source/project
- choose scope
- edit task
- delete task
- toggle done
- reorder task
- inspect task detail

### 4.5 Routing capabilities

Especially in a multi-source Mutsumi, task creation and editing must reflect the source model clearly.

The user should understand that task placement has at least two levels:

1. **source/project selection**
2. **scope selection within that source**

The interaction architecture should preserve this hierarchy across TUI and CLI flows.

---

## 5. Semantic Action Model

Once capabilities are defined, Mutsumi should define a stable semantic action vocabulary.

Suggested semantic actions:

| Semantic action | Meaning |
|---|---|
| `move_prev` / `move_next` | move in the primary linear direction |
| `move_up` / `move_down` / `move_left` / `move_right` | move in spatially meaningful directions |
| `confirm` | accept, open, or choose the focused thing |
| `secondary` | alternate contextual action on focused item |
| `back` | return to previous layer or parent view |
| `cancel` | dismiss current flow without committing |
| `toggle` | flip binary state |
| `switch_mode` | change view mode / filter / tab |
| `create` | begin creation flow |
| `edit` | begin edit flow |
| `delete` | remove selected item |
| `jump_to_source` | move from aggregate view to source-local context |

### 5.1 `Enter` should map to `confirm` by default

This RFC recommends an explicit product rule:

> **`Enter` is the default expression of `confirm`.**

In most flows, `confirm` means one of:

- choose the focused option
- open the focused item
- advance using the highlighted primary action
- enter the focused context

Exceptions are allowed, but they should be rare and deliberate.

### 5.2 Arrow keys should reflect actual space

Arrow keys must not be treated as generic "some movement happened" signals.

They should map to spatial meaning:

- `Up` / `Down` for vertical movement
- `Left` / `Right` for horizontal movement

If a screen behaves like a vertical option list, `Up` / `Down` should be primary.
If a screen behaves like a segmented horizontal chooser, `Left` / `Right` should be primary.
If a screen behaves like a grid, all four directions should express real spatial movement.

This is especially important for onboarding.

---

## 6. Two Keyboard Models, Not One

A critical part of this RFC is recognizing that keyboard interaction is not a single surface. It has two valid modes.

### 6.1 Keyboard model A — Navigation + confirm

This is the keyboard analogue of mouse interaction.

Characteristics:

- focus-driven
- spatially understandable
- discoverable
- good for onboarding and general users

Core expectations:

- arrows move
- `Enter` confirms
- `Escape` goes back/cancels
- `Tab` may move between major controls where appropriate

This should be the default mental model for basic keyboard usability.

### 6.2 Keyboard model B — Power shortcuts

This is the direct-command model for experienced users.

Characteristics:

- fast
- low-travel
- memorized
- bypasses some focus traversal

Examples:

- `n` = new
- `e` = edit
- `space` = toggle done
- `/` = search
- `?` = help

### 6.3 Relationship between the two

These two keyboard models must coexist without conflict.

The principle should be:

> **Navigation/confirm is the baseline. Power shortcuts are accelerators layered on top.**

That means:

- the product must remain fully operable without memorizing shortcuts
- shortcut users should be faster, not put on a separate behavioral island
- shortcuts must not undermine the semantic stability of baseline controls

---

## 7. Mouse Philosophy

Mouse is not a fallback. Mouse is a first-class interaction surface.

Implications:

- clickable controls must expose the same core capabilities as keyboard baseline flows where appropriate
- mouse users should not need to switch to keyboard just to complete common actions
- hover-only or hidden-only behaviors should be avoided for critical actions

The mouse expression of the capability model should feel direct and literal:

- click item to select/open
- click button to confirm action
- click tabs or segmented controls to switch views
- click explicit source/project selectors in creation flows

---

## 8. CLI Philosophy

CLI is not a TUI patch. It is the non-interactive expression of the same capability layer.

CLI should primarily expose:

- creation
- editing
- routing to source/project
- scope selection
- listing/filtering/sorting
- diagnostics and validation

CLI does not need to replicate every TUI focus transition, but it should represent product capabilities in scriptable form.

That means the product question is not:

> "What commands happen to exist?"

It is:

> "Which product capabilities need a headless expression?"

---

## 9. Onboarding as the First Test Case

Onboarding is where interaction philosophy becomes visible immediately.

### 9.1 Why onboarding matters disproportionately

Onboarding is the user's first contact with the product's interaction model.

If onboarding keyboard behavior is inconsistent, users learn the wrong lesson:

- the app feels unpredictable
- keyboard support feels accidental
- trust drops before the core product is even explored

### 9.2 Required onboarding interaction contract

Onboarding should obey a simple baseline contract:

| Semantic action | Default keyboard expression |
|---|---|
| move vertically through options | `Up` / `Down` |
| move horizontally between horizontal controls | `Left` / `Right` |
| confirm current choice | `Enter` |
| alternate confirm/toggle where appropriate | `Space` |
| go back | `Escape` or explicit Back action |
| cancel flow | explicit cancel action + `Escape` where safe |

If the onboarding screen is structurally vertical, `Up` / `Down` must work as vertical movement.
They should not collapse into the same role as `Left` / `Right`.

---

## 10. Source and Scope Must Be Explicitly Hierarchical

For task creation and routing, Mutsumi should reflect its actual architecture clearly.

In a multi-source world, the system should treat task placement as hierarchical:

1. choose the **source/project**
2. choose the **scope within that source**

This should be visible in creation flows rather than implied indirectly.

### 10.1 Why this matters

If the UI exposes only `scope` but not `source`, the user is forced to infer where the task is being created.

That is especially problematic now that Mutsumi has:

- personal tasks
- per-project tasks
- Main aggregate views
- project-aware routing

### 10.2 Product rule

Creation flows should not flatten source and scope into one ambiguous layer.

They should reflect the real model:

```text
source/project
  -> scope
    -> task fields
```

---

## 11. Relationship to Existing RFCs

### 11.1 RFC-004 remains valid, but incomplete

RFC-004 correctly establishes multi-surface parity.

This RFC extends it by adding:

- semantic consistency
- capability-first architecture
- dual keyboard model framing
- explicit baseline rules for `Enter` and arrows

### 11.2 RFC-008 should inherit this interaction model

RFC-008 defines onboarding structure and interaction requirements.

This RFC sharpens those requirements by specifying:

- how onboarding should interpret arrow directions
- why `Enter` must be the default confirm action
- why wizard flows should follow baseline navigation semantics

### 11.3 RFC-007 multi-source architecture strengthens this need

RFC-007 makes source/project identity central to the product.

That makes explicit source → scope routing in creation flows more important, not less.

---

## 12. Implementation Strategy

### 12.1 Introduce an interaction semantics layer

Mutsumi should define a small internal interaction vocabulary rather than letting each widget invent its own behavior.

Possible shape:

- semantic action constants or enums
- view-level action maps
- surface-specific binding tables
- shared handling for confirm/back/cancel/navigation patterns

### 12.2 Audit core screens first

Priority screens:

1. onboarding
2. Main/dashboard
3. task list views
4. detail panel
5. new/edit task flows

### 12.3 Define baseline contracts per screen type

Screen types may include:

- vertical option list
- horizontal segmented chooser
- grid/calendar surface
- form/dialog
- aggregate dashboard

Each screen type should declare how navigation semantics work.

### 12.4 Keep power shortcuts additive

Shortcut mappings should be layered on top of the baseline interaction contract, not used as a substitute for it.

---

## 13. Testing Strategy

### 13.1 Semantic tests

Add tests that verify semantic consistency, not just raw key presses.

Examples:

- `Enter` on focused selectable item triggers the screen's primary confirm path
- `Escape` returns or cancels consistently according to context
- onboarding vertical lists accept `Up` / `Down` as expected
- creation flow exposes source selection before scope selection where required

### 13.2 Screen-contract tests

For each screen type, verify that directional navigation matches the declared spatial model.

Examples:

- vertical list: `Up` / `Down` move between items
- segmented horizontal control: `Left` / `Right` switch segments
- grid surface: all four arrows navigate spatially

### 13.3 Multi-surface capability tests

For important capabilities, verify coverage across surfaces where applicable.

Examples:

- create task in selected source/project via TUI and CLI
- switch mode via keyboard and mouse
- confirm highlighted onboarding choice via keyboard and mouse

---

## 14. Open Questions

1. Should Mutsumi explicitly display the current interaction mode or keep the model invisible?
2. How much should `Tab` participate in baseline navigation versus reserving it for major control groups?
3. Which power shortcuts should be globally stable, and which may remain screen-local?
4. Should source/project selection in task creation always be explicit, or only when multiple writable sources exist?
5. Is an internal action enum enough, or should screen contracts be declared in a more formal schema-like way?

---

## 15. Conclusion

Mutsumi should not be designed as a collection of local keybindings.

It should be designed as a product with:

- one capability model
- one semantic action layer
- multiple interaction surfaces
- multiple mappings over the same underlying meaning

The right order is:

1. define what the user can do
2. define the meaning of each action
3. map those meanings into keyboard navigation, keyboard shortcuts, mouse, and CLI
4. implement the concrete controls

In short:

> **Do not start with keys. Start with capabilities.**

That is the interaction architecture Mutsumi should grow into.
