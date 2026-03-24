# Mutsumi Brand Identity

> **[中文版](./BRAND_cn.md)** | **[日本語版](./BRAND_ja.md)**

| Status  | Draft               |
|---------|---------------------|
| Date    | 2026-03-21          |

---

## 1. Name

### 1.1 Primary

**Mutsumi** — The English identifier, used globally.

### 1.2 Japanese

**若叶睦** (わかば むつみ / Wakaba Mutsumi)

- **若叶 (Wakaba)** — Young leaf, sprout. Symbolizes new beginnings, lightness, and understated elegance.
- **睦 (Mutsumi)** — Harmony, closeness. Implies coexisting peacefully with your workflow.

### 1.3 Chinese

**睦** — From "和睦" (harmony). Also a phonetic nod to "默默" (silently) — a quiet, unobtrusive tool.

### 1.4 Tagline

*Never lose a thread.*

### 1.5 Elevator Pitch

> Your threads, always in sight. A terminal task board that your AI agents write to and you glance at — summoned in a keystroke, gone in another.

---

## 2. Personality

Mutsumi is not a product that shouts for attention. Her personality is:

| Trait         | Description                                                                        |
|---------------|------------------------------------------------------------------------------------|
| **Quiet**     | Runs silently. No unsolicited notifications — unless you ask.                      |
| **Present**   | Always there. One glance gives you the full picture.                               |
| **Peripheral**| She lives at the edge of your vision. Not center stage. Not hidden. Like a clock on the wall. |
| **Humble**    | She doesn't tell you how to manage tasks. You (and your Agent) are in charge.      |
| **Hackable**  | She loves being customized. The more you mod her, the more alive she gets.         |
| **Fast**      | Launches in an instant. Zero-latency interactions. Exits without a trace.          |

If Mutsumi were a person, she'd be like this:

> Sitting quietly next to you, holding a sticky note covered with your threads. When you glance at her, she lifts the note a little higher. When you look away, she just waits there in peace.

---

## 3. Visual Identity

### 3.1 Logo Concept

Core imagery: **A fusion of a young leaf and an abstract task list.**

Direction A — Minimal symbol:
```
  ✓ 🌱
```
A checkmark combined with a leaf, in minimal line art.

Direction B — ASCII Art (terminal use):
```
  mutsumi ♪
```
Plain text + a musical note (representing harmony). Terminal-friendly.

Direction C — Japanese minimalism:
```
  睦
```
A single kanji as the icon, calligraphy style.

> The final logo will be completed by a designer in Phase 4. During development, Direction B (text logotype) is used.

### 3.2 Color Palette

#### Primary (Monochrome Zen — Default Theme)

| Token        | Hex       | Usage                      |
|--------------|-----------|----------------------------|
| `bg`         | `#0f0f0f` | Main background            |
| `surface`    | `#1a1a1a` | Card/panel background      |
| `border`     | `#2a2a2a` | Divider lines              |
| `fg`         | `#e0e0e0` | Primary text               |
| `fg-muted`   | `#666666` | Secondary text             |
| `accent`     | `#5de4c7` | Accent (pale cyan/mint)    |
| `danger`     | `#e06c75` | Error / high priority      |
| `warning`    | `#e5c07b` | Warning                    |
| `success`    | `#98c379` | Completed status           |

#### Design Rationale

- Dark gray base to reduce visual noise, suited for extended terminal use.
- Accent color is mint green (`#5de4c7`) — high contrast on dark backgrounds without being harsh.
- Inspiration: Catppuccin Teal + Vercel's black-and-white minimalist aesthetic.
- Overall feel: **Quiet but not dull. Minimal but not cheap.**

### 3.3 Typography

Font choice in the terminal is determined by the user's terminal emulator. Recommendations:

- **JetBrains Mono** / **Cascadia Code** / **Fira Code** — Monospaced fonts with ligature support
- No non-monospaced characters in TUI (except emoji, used sparingly)

### 3.4 Iconography

Icons in the TUI use Unicode / Nerd Font symbols:

| Concept      | Symbol  | Fallback (no Nerd Font)                |
|--------------|---------|----------------------------------------|
| Pending      | `[ ]`   | `[ ]`                                  |
| Done         | `[x]`   | `[x]`                                  |
| High         | `★★★`   | `!!!`                                  |
| Normal       | `★★`    | `!!`                                   |
| Low          | `★`     | `!`                                    |
| Expand       | `▶`     | `>`                                    |
| Collapse     | `▼`     | `v`                                    |
| Search       | `🔍`    | `/`                                    |
| Error        | `⚠`     | `!`                                    |
| New          | `[+]`   | `[+]`                                  |

> Mutsumi does not require Nerd Font. All icons have ASCII fallbacks.

---

## 4. Voice & Tone

### 4.1 Documentation Tone

- **Concise and direct**: No fancy fluff. Get to the point.
- **Technically precise**: API docs follow standard Reference format.
- **Occasionally warm**: A bit of personality in the README is welcome ("Mutsumi is there, waiting for you").
- **Never condescending**: Avoid words like "simply", "just", "easy".

### 4.2 README Tone

The README is the core narrative for Product Hunt. More personality is welcome here:

```
Good: "Mutsumi watches your mutsumi.json and re-renders instantly."
Bad:  "Mutsumi is a revolutionary AI-powered task management solution."

Good: "Let your agent write the JSON. Mutsumi handles the rest."
Bad:  "Simply configure your preferred AI agent integration endpoint."
```

### 4.3 Error Messages

```
Good: "mutsumi.json has errors. Showing last valid state."
Bad:  "FATAL: Invalid JSON format detected in configuration file."

Good: "Task 'Fix auth' is missing an ID. Skipped."
Bad:  "ValidationError: Required field 'id' not found in task object at index 3."
```

---

## 5. Community Identity

### 5.1 GitHub Presence

- **Repository**: `github.com/<user>/mutsumi`
- **Topics**: `tui`, `task-manager`, `terminal`, `python`, `textual`, `cli`, `productivity`, `agent`
- **Description**: "A silent TUI task board that watches your JSON. Agent-agnostic. Layout-agnostic. Zero friction."

### 5.2 Social Hashtags

- `#mutsumi`
- `#terminalproductivity`
- `#tuiapps`

### 5.3 Community Rituals

Encourage users to show off their workspace layouts and build a "Layout Gallery":

- GitHub Discussions section: "Show your layout"
- Standardized screenshot template: `tmux` / `zellij` config + terminal screenshot
- Featured layouts get included in the README Gallery section

---

## 6. Naming Conventions (Code-level)

### 6.1 Package Name

```
PyPI: mutsumi
Import: import mutsumi
CLI: mutsumi
```

### 6.2 Internal Module Naming

```
mutsumi/
├── app.py          # Textual App entry point
├── tui/            # TUI widgets
├── cli/            # CLI commands
├── core/           # Data layer (models, file I/O)
├── config/         # Config loading
├── i18n/           # Internationalization
└── themes/         # Built-in themes
```

### 6.3 Commit Prefix Convention

```
feat:     New feature
fix:      Bug fix
docs:     Documentation
style:    Formatting/themes
refactor: Refactoring
test:     Tests
chore:    Build/tooling
i18n:     Internationalization
```
