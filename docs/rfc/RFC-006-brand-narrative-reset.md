# RFC-006: Brand & Narrative Reset — "Never Lose a Thread"

| Field       | Value                                       |
|-------------|---------------------------------------------|
| **RFC**     | 006                                         |
| **Title**   | Brand & Narrative Reset                     |
| **Status**  | Accepted                                    |
| **Author**  | Wayne (ywh)                                 |
| **Created** | 2026-03-22                                  |

---

## Abstract

This RFC redefines Mutsumi's brand narrative from "a minimal TUI task board" to the View layer of a broader solution: **an always-on thread-keeper for multi-threaded humans**. The shift changes who the story is about (the user's brain, not the tool), what problem we solve (thread loss during context switching, not "task management friction"), and how we position within the ecosystem (one component in a zero-friction workflow, not a standalone product).

New tagline: **Never lose a thread.**

---

## 1. Motivation: Why Reset

### 1.1 The Old Narrative

The pre-reset narrative positioned Mutsumi as a product:

> "A minimal TUI task board that watches your `tasks.json` and stays out of your way."
> "Let your AI agent be the brain — Mutsumi is just the eyes."

This framing has two structural problems:

1. **It sells a component as a product.** Users don't want a TUI. They want to stop forgetting things when they context-switch. The TUI is an implementation detail.

2. **It competes on features.** "Better than Taskwarrior because..." pulls us into a red-ocean comparison. The real story is a new category that Taskwarrior doesn't address.

### 1.2 The Missed Insight

The old narrative correctly identified the user: multi-threaded super-individuals. But it misdiagnosed the pain.

Old diagnosis: *"The friction of summoning a task manager is too high."*

Real diagnosis: **"Your biological working memory has ~4 slots. You're running 12 threads. Threads get evicted every time you switch context. The forgotten thread is the one that bites you at 2 AM."**

The bottleneck isn't "opening Notion is slow." The bottleneck is that your brain physically cannot hold all active threads simultaneously. You need an external thread table — always visible, zero-cost to glance at, maintained by your agents.

### 1.3 Focus vs. Thread-Keeping

This is NOT a focus tool. The era of "do one thing deeply" is over for the target user.

| Concept | Focus (专注) | Thread-Keeping (聚焦) |
|---------|-------------|----------------------|
| Philosophy | Single-thread. Block distractions. | Multi-thread. Embrace context switching. |
| Metaphor | Noise-canceling headphones | Air traffic control radar |
| User model | "You're distracted, discipline yourself" | "You're parallel, let me hold your threads" |
| Products | Forest, Pomodoro, Deep Work | **Mutsumi** |
| Failure mode | Guilt when you check your phone | Forgotten thread that derails a deadline |

Thread-keeping accepts multi-threading as the user's superpower, not a flaw. It doesn't ask you to stop. It makes sure nothing falls off the stack.

---

## 2. The New Narrative

### 2.1 Story Structure

The narrative follows a three-layer structure, each targeting a different audience depth:

```
Layer 0: Emotional Story (README, Product Hunt, landing page)
  → Speaks to the user's brain. Pain → Relief → How.

Layer 1: Technical Story (Docs, Architecture)
  → Speaks to the developer. MVC. Agent Agnostic. Local Only.

Layer 2: Ecosystem Story (Integration guides, Roadmap)
  → Speaks to the workflow. Quake terminals. Raycast. Agent setup.
```

### 2.2 Layer 0 — The Emotional Pitch

> You don't need focus. You need to never lose a thread.
>
> The modern super-individual juggles a dozen contexts a day — coding, reviewing, messaging, running agents, scanning feeds. That's not a flaw. That's your operating mode.
>
> The real problem isn't that you do too many things. It's that the moment you switch away, the last thread starts fading from your brain. An hour later, the critical bug you meant to fix has evaporated. Not because you lack discipline — because human working memory only holds about four items, and you've got twelve threads open.
>
> Mutsumi doesn't ask you to slow down. Doesn't ask you to close your browser. Doesn't lecture you about "deep work."
>
> She does one thing: **keeps all your threads visible in the corner of your eye, always.**
>
> Switch contexts 40 times a day — it doesn't matter. Every time you glance back, you see exactly what's on your plate, what's waiting, what your agents have already pushed forward.
>
> Summon with a hotkey. Dismiss with a hotkey. So light you forget she exists — until you need her.
>
> **Never lose a thread.**

### 2.3 Layer 1 — The Technical Pitch (preserved from old narrative)

The existing technical narrative remains valid and sharp:

- **MVC Separation**: Mutsumi is View. `tasks.json` is Model. Your Agent is Controller.
- **Agent Agnostic**: Any program that writes JSON is a legitimate controller.
- **Local Only**: Zero network. Data is files.
- **Hackable First**: TOML config, custom themes, custom keybindings.

What changes: the framing. These are no longer "why Mutsumi is a good TUI." They are "why Mutsumi is the right View layer for the thread-keeping workflow."

### 2.4 Layer 2 — The Ecosystem Pitch (new)

Mutsumi is one component. The full workflow requires:

| Layer | Component | Examples |
|-------|-----------|----------|
| **Summon** | Instant terminal invocation | Quake-mode terminal (macOS iTerm2 / Windows Terminal Quake / Linux guake), Raycast/Alfred/Spotlight integration, tmux popup |
| **View** | Visual thread table | **Mutsumi TUI** |
| **Control** | Task creation & management | AI Agents (Claude Code, Codex CLI, Gemini CLI), CLI (`mutsumi add`), scripts |
| **Model** | Persistent data | `tasks.json` (local, plain-text, Git-able) |
| **Notify** | Passive reverse-notify | `events.jsonl` tailing, OS notifications (future) |

The user doesn't install "Mutsumi." The user sets up a **workflow** where:
1. One hotkey summons a dropdown terminal with Mutsumi running
2. Their agents write tasks as they work
3. A glance tells them all active threads
4. One hotkey dismisses it

Mutsumi fills the View gap. The ecosystem provides the rest.

---

## 3. Brand Updates

### 3.1 Tagline

| Before | After |
|--------|-------|
| *The silent task brain for the multi-threaded you.* | **Never lose a thread.** |

### 3.2 Elevator Pitch

| Before | After |
|--------|-------|
| A minimal TUI task board that watches your JSON and stays out of your way. | Your threads, always in sight. A terminal task board that your AI agents write to and you glance at — summoned in a keystroke, gone in another. |

### 3.3 Personality (preserved, reframed)

The existing personality traits (Quiet, Present, Humble, Hackable, Fast) are preserved. One addition:

| Trait | Description |
|-------|-------------|
| **Peripheral** | She lives at the edge of your vision. Not center stage. Not hidden. Just there — like a clock on the wall. |

The sticky-note metaphor is preserved:

> Sitting quietly next to you, holding a sticky note covered with your threads. When you glance at her, she lifts the note a little higher. When you look away, she just waits there in peace.

### 3.4 What We Stop Saying

| Old language | Why it's retired |
|---|---|
| "task exo-brain" | Overpromises. She's not a brain, she's a thread-keeper. |
| "Let your AI agent be the brain — Mutsumi is just the eyes." | Undersells Mutsumi by defining her through negation. |
| "stays out of your way" | Defensive framing. Say what she IS, not what she ISN'T. |
| "multi-threaded super-individuals" | Keep "multi-threaded." Drop "super-individuals" — too pretentious. |

### 3.5 What We Start Saying

| New language | When to use |
|---|---|
| "thread" (not "task") | In emotional/narrative contexts. "Task" in technical/API contexts. |
| "thread-keeper" | Describing Mutsumi's role in the workflow. |
| "summon / dismiss" | Describing the invocation pattern. Not "open/close." |
| "glance" | Describing the interaction mode. Not "check" or "review." |
| "peripheral vision" | Describing where Mutsumi lives in your workspace. |

---

## 4. Impact on Existing Documents

| Document | Action |
|----------|--------|
| `BRAND.md` | Update tagline, elevator pitch, add Layer 0 narrative |
| `docs/site/index.mdx` (all locales) | Rewrite hero, feature cards, flow diagram |
| `docs/site/what-is-mutsumi.mdx` (all locales) | Rewrite around thread-loss problem |
| `README.md` | Future — Phase 4 rewrite using Layer 0 narrative |
| `RFC-001` | No change — technical architecture is unchanged |
| `ROADMAP.md` | Future — reprioritize ecosystem integration in post-launch |

---

## 5. Decision

**Accepted.** The narrative reset does not change any code, architecture, or data contract. It changes how we talk about what we already built. Implementation begins with the documentation site and BRAND.md.
