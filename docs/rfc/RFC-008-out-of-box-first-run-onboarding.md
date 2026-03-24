# RFC-008: Out-of-Box First-Run Onboarding

> **[中文版](./RFC-008-out-of-box-first-run-onboarding_cn.md)** | **[日本語版](./RFC-008-out-of-box-first-run-onboarding_ja.md)**

| Field       | Value                                                  |
|-------------|--------------------------------------------------------|
| **RFC**     | 008                                                    |
| **Title**   | Out-of-Box First-Run Onboarding                        |
| **Status**  | Draft                                                  |
| **Author**  | Wayne (ywh)                                            |
| **Created** | 2026-03-22                                             |

---

## 1. Abstract

Mutsumi's current architecture is strong, but the end-to-end first-run flow is still too visible to the user: install, init, create files, register project, configure agent, maybe set up split panes, then finally open the board.

That is the opposite of Mutsumi's core promise: **zero friction**.

This RFC proposes a new onboarding model centered on a single command:

```bash
mutsumi
```

If the environment is already ready, Mutsumi opens immediately.
If it is not ready, Mutsumi must **bootstrap itself in-place** with a short, high-signal onboarding flow that asks only a few meaningful questions, creates the missing files automatically, and then launches into a usable state.

The goal is simple:

> **The user should feel like they opened a tool, not deployed a system.**

---

## 2. Problem Statement

### 2.1 Current Friction

Today, a new user may need to think about all of the following before Mutsumi feels useful:

- Is this a personal task flow or a project task flow?
- Does `~/.mutsumi/config.toml` exist?
- Does `~/.mutsumi/mutsumi.json` exist?
- Does the current project already have `mutsumi.json`?
- Has this project been registered?
- Does the current Agent know how to work with Mutsumi?
- Should they use tmux/zellij scripts?
- Should they manually edit `CLAUDE.md` / `AGENTS.md` / similar files?

Each individual step is reasonable. The combination is not.

### 2.2 Root Cause

The problem is not that Mutsumi lacks features.

The problem is that **setup is still a visible workflow** instead of being compressed into default behavior.

Users do not want to learn an initialization graph. They want to:

1. open Mutsumi,
2. glance at their tasks,
3. let their Agent interact with it naturally.

### 2.3 Product Principle

Mutsumi should optimize for **out-of-box usability**:

- one natural entrypoint,
- sane defaults,
- progressive disclosure,
- explicit consent only for invasive actions.

---

## 3. Goals

| Goal | Description |
|------|-------------|
| **Single natural entrypoint** | `mutsumi` is the default way to begin. Users should not be forced to learn `init` before the app becomes useful. |
| **Launch must succeed** | Running `mutsumi` should either open the app directly or open a short onboarding flow and then open the app. |
| **Few decisions, high value** | First-run should ask only the settings that materially affect the user's immediate comfort: language, input preset, theme, workspace mode, agent integration. |
| **No tmux assumption** | Terminal layout helpers remain optional utilities, not part of the primary path. |
| **Skills-first integration** | For supported agents, the default integration path should prefer skills/bridges over modifying project core instruction files. |
| **Explicit consent for core file modification** | Writing to `CLAUDE.md`, `AGENTS.md`, `GEMINI.md`, etc. must be opt-in, never implicit. |
| **No repeated init tax** | The user should not be forced to re-run full setup for every new repo. Subsequent project attachment should be lightweight. |
| **Agent-agnostic architecture preserved** | Mutsumi remains local-first and agent-agnostic. Onboarding improves UX; it does not bind the product to one model or one terminal workflow. |

---

## 4. Non-goals

This RFC does **not** propose:

- making tmux/zellij part of the primary onboarding path,
- binding Mutsumi to Claude Code only,
- requiring network calls, account login, or remote services,
- moving advanced settings into first-run,
- silently rewriting user-owned project instruction files,
- turning Mutsumi into a workspace/process manager.

Mutsumi remains a local task board and multi-source command center.

---

## 5. UX Model

### 5.1 Three Startup States

Running `mutsumi` should result in one of three paths:

#### A. Ready state

If the user's environment is already ready, Mutsumi launches immediately.

Conditions may include:
- config exists,
- personal file exists or is not required for the chosen mode,
- current project is already known or not relevant.

#### B. First-ever launch bootstrap

If this is effectively the first launch, Mutsumi opens a **short onboarding wizard** before entering the main UI.

This wizard creates missing files and stores the user's core preferences.

#### C. Soft project attachment prompt

If the user already completed onboarding, but launches Mutsumi inside a new repo that is not yet registered, Mutsumi should **not** replay the full first-run wizard.

Instead, it shows a lightweight prompt such as:

- Register current folder as a project
- Create `./mutsumi.json`
- Skip for now

This keeps project onboarding lightweight and non-repetitive.

---

### 5.2 First-run Wizard Structure

The first-run experience should be **short and focused**.

It is acceptable as a wizard because the number of questions is intentionally tiny and ordered by user impact. This RFC explicitly prefers a short step flow over RFC-002's single giant settings screen.

#### Step 1 — Language

Language is the first step.

Choices:
- English
- 中文
- 日本語

Default:
- system locale match, else English

Rationale:
- All later onboarding text should immediately switch into the user's language.
- This is the fastest trust-building decision in the whole flow.

#### Step 2 — Input preset

Choices:
- Arrows
- Vim
- Emacs

Default:
- **Arrows**

Rationale:
- This matches the product rule that the default preset is for normal users, not only terminal power users.
- The user should not discover an uncomfortable key model only after the app has already opened.

#### Step 3 — Theme

Choices:
- Monochrome Zen
- Nord
- Dracula
- Solarized

Default:
- **Monochrome Zen**

Rationale:
- Theme is low-risk but high-perceived-value.
- It helps the first-run experience feel personal without adding complexity.

#### Step 4 — Workspace mode

Choices:
- Personal only
- Current project only
- Personal + current project

Smart default:
- if current directory is a Git repo: **Personal + current project**
- otherwise: **Personal only**

Rationale:
- This is the minimum meaningful decision needed to reduce confusion between personal tasks and project tasks.
- It matches Mutsumi's Phase 5 multi-source model.

#### Step 5 — Agent integration

Choices:
- Skip for now
- Register Mutsumi skills / bridge for current agent
- Register skills / bridge **and** append project integration instructions to agent core file

Default:
- **Register skills / bridge only** (when the current agent is detectable and supported)
- otherwise: Skip for now

Important:
- Modifying `CLAUDE.md`, `AGENTS.md`, `GEMINI.md`, or equivalent files must be a separate, explicit choice.
- Skills/bridge registration and project core-file injection are not the same operation and must not be conflated.

---

### 5.3 Interaction Requirements

The onboarding flow must follow Mutsumi's core interaction rules.

Every step must be reachable by both keyboard and mouse.

| Action | Keyboard | Mouse |
|--------|----------|-------|
| Move between options | Arrow keys / Tab | Click option |
| Confirm selection | Enter / Space | Click button |
| Go back | Escape / dedicated Back action | Click Back |
| Accept recommended default | Enter | Click Continue |
| Cancel onboarding | Escape | Click Skip / Cancel |

### 5.4 Cancellation Behavior

Canceling onboarding must **not** make `mutsumi` fail.

If the user cancels:
- Mutsumi launches with temporary defaults for the current session,
- shows an empty usable UI,
- offers a lightweight "Finish setup" entry point later.

This preserves the rule that the main command should always succeed.

---

## 6. What Gets Created Automatically

Depending on the user's choices, Mutsumi may create:

```text
~/.mutsumi/
├── config.toml
└── mutsumi.json

<current-project>/
└── mutsumi.json
```

### 6.1 Always safe to create

These are Mutsumi-owned files and may be created automatically during onboarding:

- `~/.mutsumi/config.toml`
- `~/.mutsumi/mutsumi.json`
- current project's `mutsumi.json` (only if the user selected a mode that needs it)

### 6.2 Never auto-create without explicit consent

These are user/project-owned instruction files and must not be modified implicitly:

- `CLAUDE.md`
- `AGENTS.md`
- `GEMINI.md`
- `opencode.md`
- equivalent agent instruction files

---

## 7. Agent Integration Boundary

### 7.1 Preferred order of integration

Mutsumi should prefer the following order:

1. **Mutsumi-owned bridge / skills registration**
2. **Printed snippet / copyable instructions**
3. **Project core-file injection** (explicit opt-in only)

### 7.2 Why skills-first

Skills/bridge registration is the better default because it:

- reduces project file pollution,
- avoids surprising edits to instruction files,
- is easier to evolve over time,
- feels more like enabling a capability than rewriting project policy.

### 7.3 Why core-file injection stays optional

Core instruction files are high-trust, high-sensitivity files.

Users may already have carefully written project conventions there. Mutsumi should not assume the right to append to them just because onboarding is happening.

Therefore:

> **Mutsumi may offer project core-file injection, but it must never be the default path.**

### 7.4 Supported integration modes

| Mode | Behavior |
|------|----------|
| `none` | No Agent integration is performed. |
| `skills` | Register Mutsumi task capabilities with the supported current Agent, without editing project instruction files. |
| `skills+project-doc` | Register skills/bridge and additionally append project integration instructions to the appropriate agent instruction file. |
| `snippet` | Show or copy manual instructions when automatic bridge registration is unavailable. |

---

## 8. Smart Defaults

The out-of-box experience depends more on defaults than on configurability.

Recommended defaults:

| Setting | Default |
|---------|---------|
| Language | system locale (fallback English) |
| Key preset | `arrows` |
| Theme | `monochrome-zen` |
| Notifications | `quiet` |
| Default tab | `main` |
| Workspace mode in Git repo | `personal + current project` |
| Workspace mode outside Git repo | `personal only` |
| Agent integration | `skills` when supported, else `none` |
| Core-file injection | `off` |

These defaults should let most users hit Enter several times and be done.

---

## 9. Command Behavior Changes

### 9.1 `mutsumi`

`mutsumi` becomes the primary onboarding entrypoint.

Behavior:
- detect readiness,
- run first-run bootstrap if necessary,
- optionally run a soft project attachment prompt,
- launch TUI.

### 9.2 `mutsumi init`

`mutsumi init` remains useful, but shifts from being a required prerequisite to being an explicit utility command.

Suggested meanings:
- force-run onboarding again,
- create files non-interactively with flags,
- reset or repair a setup.

### 9.3 `mutsumi setup --agent`

This command remains as an explicit, post-install integration path.

It should also be reusable from within onboarding, but it is no longer the only reasonable path to a working system.

---

## 10. Project Attachment Model

The first-run wizard solves the first launch. It must not create repetitive setup tax later.

When the user launches Mutsumi inside an unregistered Git repo after onboarding is already complete, Mutsumi should show a compact prompt:

```text
This folder looks like a project.
[ Register project ] [ Create local mutsumi.json ] [ Skip ]
```

Rules:
- this prompt is lightweight, not a full wizard,
- it appears at most once per repo unless explicitly re-triggered,
- it never blocks access to personal tasks.

This preserves the “open instantly” feel while still helping users adopt the multi-project model.

---

## 11. Default Routing for Semantic Task Operations

This RFC does not define the skill protocol itself, but onboarding should establish the routing rules used by future skills.

Recommended routing:

1. If the user is inside a registered project, semantic task actions default to that project's `mutsumi.json`.
2. If the user is outside a project context, semantic task actions default to personal tasks.
3. Explicit user targeting always overrides defaults.

Examples:
- inside `~/Code/saas-app`, “remember to fix refresh token” → project task
- outside any project, “tomorrow buy coffee beans” → personal task
- “add this to personal” → personal task regardless of cwd

These defaults reduce mental overhead and make later skill-based interactions feel natural.

---

## 12. Relationship to RFC-002

This RFC updates the onboarding direction introduced in RFC-002.

### 12.1 Superseded ideas

The following parts of RFC-002 should be considered superseded:

- the assumption that onboarding should primarily happen through `mutsumi init`,
- the assumption that a single large setup panel is the best first-run UX,
- the assumption that agent setup is always a clearly separate post-init action.

### 12.2 Preserved ideas

The following ideas remain valid:

- zero-config should work,
- config must stay human-readable and local,
- onboarding should remain transparent and non-magical,
- Mutsumi should stay local-first and hackable.

In short:

> RFC-002 was correct about the goal.
> This RFC updates the interaction model to better achieve it.

---

## 13. Implementation Strategy

### 13.1 Likely code areas

| Area | Change |
|------|--------|
| `mutsumi/cli/__init__.py` | Add startup readiness detection before launching the app |
| `mutsumi/config/settings.py` | Add or normalize onboarding-related config fields |
| `mutsumi/config/__init__.py` | Load/save new defaults cleanly |
| `mutsumi/cli/setup.py` | Split skills/bridge registration from project core-file injection modes |
| `mutsumi/cli/project.py` | Reuse project registration logic from soft-attach prompt |
| `mutsumi/core/paths.py` | Reuse personal path helpers during lazy init |
| `mutsumi/tui/` | Add onboarding widgets and lightweight project-attach UI |

### 13.2 Minimal implementation phases

| Phase | Scope | Deliverable |
|-------|-------|-------------|
| **8a** | Readiness detection | `mutsumi` can detect first-run / attach-needed states |
| **8b** | First-run wizard | Language, key preset, theme, workspace mode, agent integration |
| **8c** | Lazy file creation | Automatic creation of config/personal/project task files |
| **8d** | Skills-first agent bridge | Default integration path without editing core files |
| **8e** | Optional core-file injection | Explicit opt-in project doc modification |
| **8f** | Soft project attach prompt | Lightweight repo registration after onboarding |

---

## 14. Testing Strategy

### 14.1 First-run tests

- launch with no config and no task files → wizard appears
- completing wizard creates expected files and enters app
- canceling wizard still enters app with temporary defaults
- language choice changes onboarding copy immediately

### 14.2 Safety tests

- selecting `skills` does not modify `CLAUDE.md` / `AGENTS.md`
- selecting `skills+project-doc` only modifies the expected file
- existing project instruction files are not duplicated on repeated setup

### 14.3 Project attach tests

- launching inside an unregistered repo after onboarding shows soft prompt, not full wizard
- choosing Skip does not block app launch
- choosing Register creates project entry and optional local `mutsumi.json`

### 14.4 Input parity tests

- onboarding is fully usable with keyboard only
- onboarding is fully usable with mouse only
- recommended defaults can be accepted quickly via Enter

---

## 15. Open Questions

1. Should the theme step include a live miniature preview, or is name-only enough for first-run?
2. How should Mutsumi detect the “current Agent” reliably without becoming agent-specific?
3. Should canceling onboarding persist nothing, or persist the choices made so far?
4. Should project attachment prompts support a “never ask for this repo again” option?
5. For Agents without a skill/bridge mechanism, what is the best fallback: snippet display, clipboard copy, or explicit doc injection prompt?

---

## 16. Conclusion

Mutsumi should feel like a quiet tool that is already there for the user.

That feeling is broken when installation, initialization, project registration, and Agent configuration all remain separate visible tasks.

This RFC compresses those concerns into a simpler model:

- `mutsumi` is the one natural entrypoint,
- onboarding is short and humane,
- missing files are created automatically,
- skills/bridges are preferred over editing core project files,
- tmux and other layout helpers stay optional,
- subsequent project adoption is lightweight instead of repetitive.

The outcome is not merely a nicer setup flow.

It is a better expression of the product itself:

> **Open instantly. Understand instantly. Use instantly.**
