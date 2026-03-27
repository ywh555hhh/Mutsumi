# RFC-011: Plugin Runtime and Extension Architecture — Microkernel, Capabilities, and Controlled Extensibility

| Field | Value |
|---|---|
| **RFC** | 011 |
| **Title** | Plugin Runtime and Extension Architecture — Microkernel, Capabilities, and Controlled Extensibility |
| **Status** | Draft |
| **Author** | Wayne (ywh) |
| **Created** | 2026-03-25 |

---

## 1. Abstract

Mutsumi has reached the point where interaction semantics and multi-source behavior are no longer the only architectural concern.

The next structural question is bigger:

> **How should Mutsumi evolve from a useful local TUI into a stable, extensible platform without collapsing into an app-centered mess?**

This RFC proposes a **plugin-ready microkernel architecture** for Mutsumi built around six layers:

1. **Core domain/data layer**
2. **Runtime state layer**
3. **Capability layer**
4. **Interaction/activation layer**
5. **Plugin runtime**
6. **Presentation layer**

The goal is not to imitate Obsidian or VS Code mechanically.
The goal is to preserve Mutsumi's own product nature:

- local-first
- JSON-first
- agent-agnostic
- keyboard + mouse + CLI parity
- no network in the core product
- low-friction everyday use

This RFC records not only the final architecture direction, but also the **reading, extraction, tradeoff, and decision process** behind it.

---

## 2. Problem Statement

### 2.1 The current structure is too app-centered

Mutsumi already has good building blocks:

- `core/models.py` is a solid local data contract
- `core/loader.py` / `core/writer.py` already hold many domain operations
- `core/sources.py` and file watching provide a real runtime foundation
- RFC-010 introduced a semantic-first interaction vocabulary

However, the current runtime is still too concentrated inside `app.py`.

In practice, `MutsumiApp` is simultaneously acting as:

- bootstrap coordinator
- runtime state holder
- source manager
- watcher manager
- UI orchestrator
- interaction router
- capability executor
- error/notifier surface

That creates three architectural bottlenecks:

1. **Plugin entrypoints are unclear**
2. **Interaction semantics are only partially centralized**
3. **UI and capability logic remain too tightly coupled**

### 2.2 Why this matters now

This is no longer only about cleaning up code.
It is about enabling future product directions such as:

- reminder integrations
- custom commands
- task automations
- local LLM helpers
- additional source providers
- extra panels/widgets
- community extensions

Without a stable plugin boundary, every new feature pressures `app.py` harder and makes later cleanup more expensive.

### 2.3 The key design tension

A plugin system always creates a structural tension:

| Desire | Risk |
|---|---|
| Let plugins do powerful things | Plugins become invasive and destabilize the host |
| Keep the core stable and refactorable | Plugins become too weak to matter |

The right answer is **not** “maximum openness immediately.”
The right answer is **layered extensibility with controlled exposure**.

---

## 3. Goals

| Goal | Description |
|---|---|
| Stable plugin foundation | Define where plugins attach without exposing app internals |
| Capability-first extensibility | Plugins should trigger and contribute capabilities, not poke UI state directly |
| Controlled invasiveness | Plugins must not need direct access to `MutsumiApp` or Textual internals by default |
| Local-first preserved | Core product remains local-only and agent-agnostic |
| UI extensibility without chaos | Allow extension panels and actions without immediately exposing arbitrary widget injection |
| Event-driven growth | Core actions should produce events that plugins can react to |
| Future plugin ecosystem readiness | Create a path that can later support richer community plugins without locking the product too early |

---

## 4. Non-goals

This RFC does **not** propose:

- immediate VS Code-level extension power
- immediate Obsidian-level workspace/view API breadth
- exposing raw `MutsumiApp` or arbitrary Textual widget tree access as the default plugin model
- introducing network dependencies into the Mutsumi core
- committing to a full plugin marketplace in the first implementation
- building a security sandbox that Python cannot realistically guarantee in-process

---

## 5. Architectural Baseline Before Plugins

Before deciding how plugins should work, it is important to recognize what is already worth keeping.

### 5.1 Strong foundations that should be preserved

#### A. Local data contract

Mutsumi's local file contract remains the foundation:

- canonical file: `mutsumi.json`
- legacy fallback: `tasks.json`
- unknown fields preserved
- no database required

This remains a strategic advantage for:

- agent compatibility
- user hackability
- Git-friendliness
- offline operation

#### B. `extra="allow"` is strategically important

The permissive task model is not just implementation detail.
It is what allows future plugins to attach metadata such as:

- GitHub issue links
- review status
- reminder metadata
- external IDs
- plugin-owned annotations

without forcing a core schema rewrite every time.

#### C. RFC-010 already established the correct direction

RFC-010's “actions before inputs” principle remains authoritative.
This RFC extends that idea further:

> **Capabilities are not only the correct interaction architecture. They are also the correct extension architecture.**

---

## 6. Reading Log and Decision Extraction

This RFC was informed by several relevant ecosystems. The goal was not blind imitation, but careful extraction.

### 6.1 Pluggy — Hooks as explicit contract

What was read:

- Pluggy documentation and toy examples around `PluginManager`, `@hookspec`, and `@hookimpl`

What mattered:

- the host defines **what can be hooked**
- the plugin defines **how it implements that hook**
- host and plugin are decoupled through an explicit contract instead of direct imports into host internals

What we take:

- explicit extension-point contracts
- plugin registration through host-owned specs
- stable host/plugin separation via named interfaces

What we do **not** take directly as the whole solution:

- Pluggy alone is not a full runtime architecture
- it does not solve UI contribution, capability dispatch, or runtime state organization by itself

Decision:

> Mutsumi should adopt the **contract mindset** of Pluggy, whether or not it literally depends on Pluggy in the first implementation.

### 6.2 Home Assistant — Event bus + state machine separation

What was read:

- Home Assistant core architecture docs
- `EventBus` and `StateMachine` references in `homeassistant/core.py`

What mattered:

- clear separation between event emission and state ownership
- the system is not “random callbacks everywhere”; it is structured around central runtime objects
- extensions react to events without owning the host's full internal state

What we take:

- explicit event bus
- runtime state objects that are not the UI tree
- separation between “the world changed” and “what the UI should do now”

What we reject:

- a single giant `hass`-style omnipotent context object given to everything

Decision:

> Mutsumi should have an event bus and explicit runtime state services, but plugins should receive a **narrow plugin context**, not a god object.

### 6.3 NoneBot2 / AstrBot — Normalize inputs before plugin handling

What was read:

- NoneBot2 plugin/matcher/event docs
- AstrBot plugin, event, adapter, and OpenAPI docs

What mattered:

- external input is normalized into a common event model
- plugin handlers work on normalized events, not raw platform-specific chaos
- adapters and plugins are treated as extension surfaces, not as arbitrary host modifications

What we take:

- event-first extension style
- capability/event dispatch rather than host mutation
- adapter/provider model for external sources and integrations

Decision:

> Mutsumi should treat plugins primarily as **capability contributors, event listeners, providers, and declarative contributors**, not as code that freely mutates the app.

### 6.4 VS Code — Contributions, activation events, and host-controlled UI

What was read:

- VS Code extension API docs
- activation events docs
- API references for events and extension anatomy

What mattered:

- extensions are activated for specific reasons, not all eagerly by default
- the host owns the workbench and UI lifecycle
- many extensions contribute through manifests and structured contribution points instead of DOM ownership

What we take:

- manifest-driven plugin contributions
- activation triggers
- host-owned UI surfaces
- explicit command registration

What we reject for now:

- very large public workspace/view API surface from day one

Decision:

> Mutsumi should adopt a **manifest + contribution + activation** model, but keep the public UI surface much narrower in the first phases.

### 6.5 Obsidian — Strong plugin ecosystem through commands and views

What was read:

- Obsidian developer docs
- sample plugin source
- API typings and custom-view related docs

What mattered:

- commands are a first-class plugin surface
- custom views/workspace integration can create very rich ecosystems
- a host can support serious extension without exposing DOM directly

What we take:

- command registration is a highly valuable extension point
- custom views are powerful, but should come after the host's internal workspace model is mature

What we reject for phase 1:

- broad workspace/view APIs immediately
- plugins depending on unstable host layout internals

Decision:

> Mutsumi should treat Obsidian as a **long-term inspiration**, not as a first-step compatibility target.

### 6.6 Typora — Restraint is also a design virtue

What was read:

- official Typora docs around themes, CSS, search services, and customization surfaces

What mattered:

- not every product should expose a deep general-purpose plugin API immediately
- restrained customization can preserve core simplicity and refactor freedom

What we take:

- early extension surfaces should be narrow and stable
- UI extensibility should begin conservatively

Decision:

> Mutsumi should be more conservative than Obsidian in early UI extensibility.

---

## 7. Final Judgment from the Reading Process

After comparing these models, the architectural conclusion is:

> **Mutsumi should not start by copying Obsidian's “let plugins deeply inhabit the workspace.”**
>
> **Mutsumi should start with an AstrBot/Home-Assistant-style event-and-capability core, plus a VS-Code-like manifest/contribution model, while keeping early UI extensibility closer to Typora's restraint.**

In short:

- **core plugin philosophy**: event-driven + capability-first
- **UI plugin philosophy**: host-controlled and conservative
- **advanced custom views**: later, optional, and explicitly experimental at first

---

## 8. Architectural Principles

### 8.1 Plugins never talk to `MutsumiApp` directly

This is the most important rule in the whole RFC.

Plugins must **not** rely on:

- `MutsumiApp`
- Textual screen stack internals
- direct widget tree traversal
- private app state mutation

Instead, plugins receive a **narrow plugin context**.

### 8.2 Capabilities are the primary execution boundary

Plugins should request or provide capabilities such as:

- create task
- archive task
- export tasks
- switch source
- open help-like view
- send reminder

They should not manually reimplement core writeback logic.

### 8.3 Events are the primary reaction boundary

Capabilities answer:

> **What can the system do?**

Events answer:

> **What just happened, so that another extension may react?**

Both are necessary.

### 8.4 UI remains host-owned by default

The host decides:

- where extension panels appear
- how focus works
- what visual grammar is allowed
- what the keyboard + mouse semantics remain

Plugins may contribute to UI surfaces, but the host retains final rendering and lifecycle control.

### 8.5 Extensibility must be layered, not binary

Mutsumi should not think in terms of:

- “plugin support off”
- “plugin support fully open”

It should define **levels of extension power**.

### 8.6 Local-first remains authoritative

The Mutsumi core remains:

- local-only
- file-first
- no telemetry
- no mandatory network

If a plugin chooses to talk to an outside system in the future, that is a plugin-level concern, not a core architectural requirement.

---

## 9. Target Architecture

The target architecture becomes:

```text
JSON / TOML / local files
  ↓
Core domain layer
  ↓
Runtime state layer
  ↓
Capability layer
  ↓
Interaction / activation layer
  ↓
Plugin runtime
  ↓
Presentation layer (TUI / CLI)
```

A more explicit view:

```text
┌─────────────────────────────────────────────┐
│           Core Data / Domain Layer          │
│ models, loader, writer, schema, file IO     │
└──────────────────────┬──────────────────────┘
                       │
┌──────────────────────▼──────────────────────┐
│             Runtime State Layer             │
│ session, sources, layers, focus, notify     │
└──────────────────────┬──────────────────────┘
                       │
┌──────────────────────▼──────────────────────┐
│              Capability Layer               │
│ create/edit/delete/toggle/switch/...        │
└──────────────────────┬──────────────────────┘
                       │
┌──────────────────────▼──────────────────────┐
│         Interaction / Activation Layer      │
│ semantic action, activation target, router  │
└──────────────────────┬──────────────────────┘
                       │
┌──────────────────────▼──────────────────────┐
│               Plugin Runtime                │
│ manifests, registry, hooks, providers       │
└──────────────────────┬──────────────────────┘
                       │
┌──────────────────────▼──────────────────────┐
│           Presentation / Surfaces           │
│ TUI widgets, panels, footer, CLI commands   │
└─────────────────────────────────────────────┘
```

---

## 10. Layer Responsibilities

### 10.1 Core domain layer

Owns:

- `Task`, `TaskFile`, validation
- read/write/load/save
- pure task operations
- source watching primitives
- data preservation guarantees

Does not own:

- UI
- app lifecycle
- focus
- plugin lifecycle

### 10.2 Runtime state layer

Owns:

- active source / active scope
- selected task / focused region
- layer stack (`detail`, `search`, `confirm`, `help`, `task_form`, `onboarding`)
- source runtime registry
- self-write suppression state
- notification sink abstraction
- clipboard / temporary session state

Does not own:

- concrete Textual widgets
- business capability implementation

### 10.3 Capability layer

Owns:

- explicit product actions
- availability checks
- side-effect orchestration through runtime + core services
- emitting post-action events

Examples:

- `task.create`
- `task.edit`
- `task.toggle_done`
- `task.delete`
- `task.add_child`
- `scope.switch`
- `source.switch`
- `layer.close_top`
- `onboarding.finish`
- `onboarding.skip`
- `reminder.fire`

### 10.4 Interaction / activation layer

Owns:

- semantic action vocabulary
- mapping key/mouse/CLI intent into capabilities
- focused activation resolution
- `Enter` / click / command dispatch coherence

This layer is what finally makes:

> **focused activation and click activation converge on the same capability path**

### 10.5 Plugin runtime

Owns:

- plugin discovery
- manifest parsing
- enable/disable lifecycle
- extension registration
- event subscription
- provider registries
- external/in-process plugin protocol boundaries

### 10.6 Presentation layer

Owns:

- TUI widgets and screens
- CLI parsing surfaces
- view rendering
- host-controlled layout slots
- converting runtime/capability results into visible UI

---

## 11. Plugin Types and Power Levels

Mutsumi should support plugins in **layers of invasiveness**.

### 11.1 Level 0 — Configuration-style extensions

Examples:

- themes
- keybinding presets
- reminder rules
- view preferences
- task field display rules

Properties:

- safest
- easiest to keep compatible
- not code-heavy

### 11.2 Level 1 — Headless plugins

Examples:

- reminder channels
- custom commands
- task automation
- local LLM summarizers or rewriters
- exporters/importers
- source providers
- validators / transformers
- metadata renderers

Properties:

- extend behavior without owning UI tree
- ideal first plugin tier for Mutsumi

### 11.3 Level 2 — Declarative UI contributions

Examples:

- dashboard cards
- footer actions
- side panels
- help sections
- status widgets
- local LLM panel defined through a host-rendered panel spec

Properties:

- richer than headless plugins
- host still owns rendering and focus
- recommended first UI extension model

### 11.4 Level 3 — Experimental native view plugins

Examples:

- full custom interactive views
- advanced workspace panels with their own complex behavior

Properties:

- most powerful
- most invasive
- highest compatibility burden
- should begin as experimental or trusted-only

---

## 12. Why Declarative Panels Before Native Widgets

A major architectural decision in this RFC is:

> **Do not begin by allowing arbitrary plugin-provided Textual widgets.**

### 12.1 Why direct widget injection is dangerous early

If plugins can directly mount arbitrary widgets into the live app, they can interfere with:

- focus semantics
- keyboard routing
- click routing
- layout consistency
- style/theme assumptions
- crash isolation
- host refactor freedom

### 12.2 The better first step: `PanelSpec`

Instead of returning raw widgets, plugins should first contribute a declarative structure such as:

```text
PanelSpec
  -> title
  -> blocks
  -> inputs
  -> action rows
  -> lists
  -> badges
  -> status lines
```

The host then renders that spec using native Mutsumi UI conventions.

This preserves:

- visual consistency
- focus consistency
- activation consistency
- host control over layout evolution

### 12.3 Example: local LLM panel

If a user wants a local LLM input area, the plugin should ideally contribute:

- one input block
- one action button row
- one output list or transcript block
- one status line

The host renders it natively.

This still feels “native” to the user, but does not yet require a fully open widget API.

---

## 13. Capabilities vs Hooks vs Events

This distinction must be explicit.

### 13.1 Capabilities

Capabilities answer:

> **What can be done?**

Examples:

- create a task
- delete a task
- fire a reminder
- open a panel
- switch source

### 13.2 Events / hooks

Events answer:

> **What has happened?**

Examples:

- `task.created`
- `task.updated`
- `task.deleted`
- `task.completed`
- `source.changed`
- `onboarding.finished`
- `reminder.triggered`
- `app.started`

### 13.3 Why both are required

A plugin system with only capabilities cannot support passive reactions.
A plugin system with only hooks cannot support stable command-style execution.

Mutsumi needs both:

- **capability dispatcher** for doing things
- **event bus** for reacting to things

---

## 14. Plugin Context Boundary

Plugins must receive a limited `PluginContext`, not internal host objects.

Recommended shape:

```python
class PluginContext(Protocol):
    def execute_capability(self, capability_id: str, payload: Mapping[str, object] | None = None) -> object: ...
    def subscribe_event(self, event_name: str, handler: EventHandler) -> None: ...
    def publish_event(self, event_name: str, payload: Mapping[str, object]) -> None: ...
    def register_command(self, command: CommandSpec) -> None: ...
    def register_panel(self, provider: PanelProvider) -> None: ...
    def register_reminder_channel(self, channel: ReminderChannel) -> None: ...
    def register_source_provider(self, provider: SourceProvider) -> None: ...
```

Principle:

- enough power to extend the product
- not enough power to own the host internals

---

## 15. Manifest and Lifecycle Model

Plugins should be manifest-driven.

### 15.1 Manifest fields

Recommended minimal manifest:

```toml
id = "local-llm-panel"
name = "Local LLM Panel"
version = "0.1.0"
api_version = "1"
entrypoint = "plugin.py"
plugin_type = "external"

permissions = [
  "task.read",
  "task.write",
  "panel.register",
  "event.subscribe",
  "capability.execute",
]

activation = [
  "on_startup",
  "on_command:local-llm.open",
  "on_panel:main.sidebar",
]
```

### 15.2 Lifecycle stages

A plugin should conceptually move through:

1. discovered
2. validated
3. enabled
4. activated
5. running
6. deactivated / disabled

### 15.3 Activation events

Not every plugin should be loaded at maximum cost immediately.
Possible activation triggers:

- startup
- when a command is invoked
- when a panel slot becomes visible
- when a specific event fires
- when a source type is requested

This keeps startup fast and mirrors the best lesson from VS Code.

---

## 16. Provider Registries

Several extension surfaces should be modeled explicitly as registries.

### 16.1 Capability registry

Purpose:

- register built-in and plugin-defined capabilities
- resolve capability IDs
- run availability checks
- dispatch execution

### 16.2 Reminder channel registry

Purpose:

- register delivery handlers for reminder events
- allow multiple channel implementations

Examples:

- terminal bell
- desktop notification
- sound player
- custom local script
- overlay banner

### 16.3 Source provider registry

Purpose:

- support future source backends or source discovery models

Examples:

- local JSON
- generated virtual source
- SQLite plugin source
- read-only snapshot provider

### 16.4 Panel provider registry

Purpose:

- collect panel/dashboard/footer/side-panel contributions
- let host decide where and how they render

### 16.5 Metadata renderer registry

Purpose:

- render plugin-owned task metadata in a controlled way

---

## 17. Reminder System as the First Plugin-Friendly Feature

The reminder example is especially useful because it naturally demonstrates the right plugin boundary.

### 17.1 Core responsibility

The core should define:

- reminder scheduling semantics
- reminder event payload shape
- reminder triggering flow
- enabled channel selection

### 17.2 Plugin responsibility

Plugins should define **how** delivery happens.

Examples:

- play sound
- show desktop notification
- ring terminal bell
- run local script
- write to file
- show host overlay banner

### 17.3 Why this is a good first extension surface

Because it is:

- useful immediately
- narrow in scope
- easy to test
- highly extensible
- low-risk to core architecture

This RFC recommends:

> **Reminder channels should be one of the first real plugin APIs shipped.**

---

## 18. Data Extension Rules

Because Mutsumi preserves unknown fields, plugins need a convention for writing metadata.

Recommended rule:

- plugin-owned fields should be namespaced

Examples:

```json
{
  "title": "Review PR",
  "plugins.github.issue_id": 123,
  "plugins.reminder.next_fire_at": "2026-03-25T18:00:00",
  "plugins.local_llm.summary": "Needs follow-up"
}
```

Alternative structured convention may also be allowed:

```json
{
  "title": "Review PR",
  "plugins": {
    "github": {"issue_id": 123},
    "reminder": {"next_fire_at": "2026-03-25T18:00:00"}
  }
}
```

Final exact convention may be defined later in a plugin data spec, but the principle is already clear:

> **plugin metadata must survive round-trips without requiring core schema updates.**

---

## 19. In-Process vs External Plugins

A hard truth must be acknowledged:

> **Python in-process plugins are not meaningfully sandboxed.**

If arbitrary Python runs in-process, it can:

- read files
- mutate globals
- block the app
- monkey-patch modules
- crash the host

### 19.1 Therefore Mutsumi should support two plugin modes

#### A. Trusted in-process plugins

Best for:

- built-in plugins
- highly trusted local extensions
- performance-sensitive integrations

Tradeoff:

- most powerful
- least isolated

#### B. External-process plugins

Best for:

- user-authored automations
- local agents
- reminder channels
- tooling integrations
- experimental panels backed by data providers

Tradeoff:

- safer boundary
- more protocol design required
- slightly more overhead

### 19.2 Recommended strategic direction

For long-term ecosystem health:

> **Headless and automation-style plugins should have a strong external-process path.**

This keeps the core safer and the boundary clearer.

---

## 20. Recommended Initial Directory Shape

A future architecture aligned with this RFC could look like:

```text
mutsumi/
├── app.py
├── core/
├── runtime/
│   ├── app_session.py
│   ├── source_runtime.py
│   ├── layer_stack.py
│   ├── selection.py
│   ├── notifications.py
│   └── clipboard.py
├── capabilities/
│   ├── base.py
│   ├── context.py
│   ├── result.py
│   ├── registry.py
│   ├── tasks/
│   ├── sources/
│   ├── layers/
│   └── onboarding/
├── interaction/
│   ├── semantics.py
│   ├── activation.py
│   ├── router.py
│   └── focus.py
├── plugins/
│   ├── api.py
│   ├── manifest.py
│   ├── registry.py
│   ├── loader.py
│   ├── manager.py
│   ├── context.py
│   ├── event_bus.py
│   ├── reminders.py
│   ├── panels.py
│   ├── sources.py
│   └── protocol/
│       ├── in_process.py
│       └── external_rpc.py
├── tui/
└── cli/
```

This is a direction, not a promise that all modules land at once.

---

## 21. Migration Strategy

This RFC does **not** recommend a single giant rewrite.
It recommends staged extraction.

### Phase 1 — Extract runtime and capability boundaries

Move business actions out of `app.py` into:

- runtime services
- capability handlers

Primary target:

- make `app.py` stop being the place where business logic lives

### Phase 2 — Introduce activation routing

Make:

- click
- `Enter`
- command invocation

resolve into the same capability dispatch path.

Primary target:

- finally make focused activation and click activation structurally converge

### Phase 3 — Introduce plugin runtime core

Ship:

- manifest parsing
- registry
- event bus
- lifecycle manager
- narrow plugin context

Primary target:

- host/plugin boundary becomes explicit before lots of plugin features exist

### Phase 4 — Ship first stable extension surfaces

Recommended order:

1. reminder channels
2. commands
3. task automations
4. source providers
5. metadata renderers

### Phase 5 — Add declarative UI contributions

Ship:

- dashboard cards
- footer actions
- side panels
- local LLM panel-like surfaces via `PanelSpec`

### Phase 6 — Evaluate experimental native views

Only after the host runtime/workspace model becomes mature enough.

---

## 22. Why This RFC Does Not Start With “Native Widget Plugins”

Because that is the fastest way to lose architectural control.

If native widget injection ships too early, the host will immediately inherit:

- incompatible focus expectations
- routing inconsistencies
- plugin breakage on internal UI refactors
- inability to evolve the workbench safely

That is a cost mature products pay only after their workspace and extension API are already stable.
Mutsumi is not there yet.

---

## 23. Final Architectural Position

The final decision of this RFC is:

### 23.1 Mutsumi should become plugin-ready through a microkernel shape

The kernel is:

- local data model
- runtime state
- capability dispatcher
- event bus
- host-owned interaction routing

### 23.2 The first plugin priority is not arbitrary UI injection

The first priority is:

- headless extensions
- reminder channels
- commands
- task automation
- source providers
- declarative panels

### 23.3 UI extensibility should be host-controlled first

Before exposing raw widgets, expose:

- commands
- slots
- actions
- panel specs
- metadata renderers

### 23.4 Obsidian-level openness is a later-stage decision

That level of openness becomes appropriate only when:

- runtime boundaries are stable
- capability contracts are stable
- workspace/view lifecycle is stable
- plugin compatibility burden is acceptable

Until then, Mutsumi should choose **clarity over maximal openness**.

---

## 24. Summary of the Decision Process

This RFC intentionally records the decision path, not just the result.

### What was learned

- **Pluggy** taught the value of explicit host-defined hook contracts
- **Home Assistant** taught the value of event bus and state separation
- **NoneBot2 / AstrBot** reinforced normalized event-driven extension models
- **VS Code** taught manifest, activation, and host-controlled contribution points
- **Obsidian** showed the power of commands and custom views, but also implied the weight of a large API promise
- **Typora** showed that restraint is a valid and often wise product choice

### What was rejected

- exposing `MutsumiApp` to plugins
- starting with arbitrary widget injection
- pretending Python in-process plugins are safely sandboxed
- chasing a maximal ecosystem before core runtime boundaries are stable

### What was chosen

> **A capability-first, event-driven, host-controlled, layered plugin architecture.**

That is the architecture that best matches Mutsumi's nature.

---

## 25. Related RFCs

- RFC-001: core product and local-first architecture baseline
- RFC-004: triple input parity across keyboard, mouse, and CLI
- RFC-007: multi-source hub architecture
- RFC-008: onboarding and first-run bootstrap model
- RFC-009: calendar as a new built-in product surface
- RFC-010: capability-first interaction architecture

RFC-011 extends those directions by answering a new question:

> **How can Mutsumi remain simple at the center while becoming extensible at the edges?**

This RFC's answer is:

> **By making capabilities, runtime state, and event contracts the real extension boundary — not `app.py`, and not arbitrary widget access.**
