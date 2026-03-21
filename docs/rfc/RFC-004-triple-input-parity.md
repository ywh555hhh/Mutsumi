# RFC-004: Triple Input Parity — Keyboard, Mouse, CLI

| 项目 | 内容 |
|------|------|
| RFC  | 004 |
| 标题 | Triple Input Parity — Keyboard, Mouse, CLI |
| 状态 | Draft |
| 作者 | Wayne (ywh) |
| 创建 | 2026-03-21 |

[中文](RFC-004-triple-input-parity_cn.md) · [日本語](RFC-004-triple-input-parity_ja.md)

---

## 1. Abstract

Mutsumi 的每一个面向用户的功能，必须同时通过**键盘**、**鼠标**、**CLI** 三种表面可达。本 RFC 定义了 Triple Input Parity 原则，审计了当前实现的覆盖缺口，并为每个缺口制定了补齐方案。

### 1.1 Design Principle

> **If a user can do it one way, they can do it all three ways.**
>
> - **Keyboard**: Zero-mouse TUI workflow (vim/emacs/arrows presets).
> - **Mouse**: Point-and-click for casual or discovery-mode users.
> - **CLI**: Headless, scriptable, pipe-friendly for automation and agents.

这不是装饰性要求——Mutsumi 同时服务三类用户场景：

| 场景 | 主要输入 | 为什么需要另外两种 |
|------|---------|-------------------|
| 专注编码时 TUI 常驻 | Keyboard | 偶尔鼠标点一下比记快捷键快；CI/Agent 需要 CLI |
| tmux 分屏快速一瞥 | Mouse | 手不离鼠标时直接点；Agent 写脚本用 CLI |
| Agent/CI 自动化 | CLI | 人类复查时打开 TUI 用键盘/鼠标 |

---

## 2. Current State Audit

### 2.1 Full Parity (3/3) — Already Satisfied

These features are accessible via all three surfaces.

| Feature | Keyboard | Mouse | CLI |
|---------|----------|-------|-----|
| Toggle done/pending | `space` | Click checkbox area | `mutsumi done <ID>` |
| Create new task | `n` | Footer `[+New]` click | `mutsumi add <TITLE>` |
| Edit task (full form) | `e` | Detail panel `[Edit]` click | `mutsumi edit <ID>` |
| Delete task | `dd` | Detail panel `[Delete]` click | `mutsumi rm <ID>` |

### 2.2 Keyboard + Mouse only (no CLI)

| Feature | Keyboard | Mouse | CLI Gap |
|---------|----------|-------|---------|
| Switch tab (scope) | `1`/`2`/`3`/`4`, `tab`/`shift+tab` | Click tab header | — |
| Show detail panel | `enter` | Click title area | — |
| Close detail/search | `escape` | Click `[x]` on detail | — |
| Collapse/expand group | `h`/`l`, `z` | Click group header | — |
| Search/filter | `/` | Footer `[/Search]` click | — |

### 2.3 Keyboard only (no Mouse, no CLI)

| Feature | Keyboard | Mouse Gap | CLI Gap |
|---------|----------|-----------|---------|
| Inline edit title | `i` | 需要 double-click 触发 | 需要 `mutsumi edit <ID> --title` (已有) |
| Priority up/down | `+`/`-` | 需要上下文菜单或按钮 | 需要 `mutsumi priority <ID> up\|down` |
| Move task up/down | `J`/`K` | 需要拖拽或按钮 | 需要 `mutsumi move <ID> up\|down` |
| Copy task | `y` | 需要右键菜单或按钮 | 需要 `mutsumi clone <ID>` |
| Paste task | `p`/`P` | 需要右键菜单或按钮 | 需要 `mutsumi paste [--before <ID>]` |
| Sort tasks | `s` | 需要 header 可点击排序 | 需要 `mutsumi sort --by <field>` |
| Show help | `?` | 需要 footer 按钮 | 需要 `mutsumi help` (click 已有) |
| Add subtask | `A` | 需要右键菜单或按钮 | 需要 `mutsumi add --parent <ID>` |
| Navigate up/down | `j`/`k` | Textual scroll wheel 已覆盖 | N/A (TUI-only) |
| Go to top/bottom | `gg`/`G` | N/A (scroll) | N/A (TUI-only) |
| Quit | `q` | 终端 `Ctrl+C` 已覆盖 | N/A (TUI-only) |

### 2.4 CLI only (no TUI equivalent needed)

These are headless-only operations that don't need TUI parity.

| Feature | CLI | Rationale |
|---------|-----|-----------|
| `mutsumi init` | Generate template | One-time setup; TUI auto-creates on first write |
| `mutsumi validate` | Schema check | Diagnostic tool; TUI shows error banner instead |
| `mutsumi schema` | Dump JSON Schema | Developer/agent tool, not interactive |
| `mutsumi list` | Print to stdout | Non-interactive listing for pipes/scripts |

---

## 3. Gap Analysis & Priority

### 3.1 Priority Classification

| Priority | Criteria |
|----------|----------|
| **P0 — Must** | Core CRUD + everyday workflow. Broken parity = broken UX. |
| **P1 — Should** | Power-user features. Parity improves discoverability. |
| **P2 — Nice** | Rarely used or has adequate workarounds. |
| **N/A** | Pure TUI navigation (scroll, focus) — inherently single-surface. |

### 3.2 Prioritized Gap List

| Gap | Surface(s) Missing | Priority | Solution |
|-----|--------------------|---------:|----------|
| Priority cycle | Mouse, CLI | P0 | Mouse: `[▲]`/`[▼]` in detail panel. CLI: `mutsumi priority <ID> up\|down` |
| Sort tasks | Mouse, CLI | P0 | Mouse: click priority group header column. CLI: `mutsumi list --sort <field>` |
| Search/filter | CLI | P0 | `mutsumi list --search <query>` (extend existing `list`) |
| Add subtask | Mouse, CLI | P0 | Mouse: `[+Sub]` button in detail panel. CLI: `mutsumi add <TITLE> --parent <ID>` |
| Move task up/down | Mouse, CLI | P1 | Mouse: drag-and-drop (Phase 5) or `[↑]`/`[↓]` buttons. CLI: `mutsumi move <ID> up\|down` |
| Copy/paste task | Mouse, CLI | P1 | Mouse: right-click context menu (Phase 5). CLI: `mutsumi clone <ID>` |
| Inline edit title | Mouse | P1 | Double-click title area → enter inline edit |
| Show help | Mouse | P2 | Footer `[?Help]` button (trivial) |
| Tab switching | CLI | P2 | `mutsumi list --scope day\|week\|month\|inbox` (already has `--scope`) |

---

## 4. Implementation Plan

### 4.1 CLI Additions (P0)

All new CLI commands follow the existing Click pattern in `mutsumi/cli/`.

#### 4.1.1 `mutsumi priority <TASK_ID> <up|down>`

```
mutsumi priority T001 up     # low → normal → high
mutsumi priority T001 down   # high → normal → low
```

Implementation: New file `mutsumi/cli/priority.py`. Calls `cycle_priority()` from `core/writer.py`.

#### 4.1.2 `mutsumi add --parent <PARENT_ID>`

```
mutsumi add "Fix tests" --parent T001
```

Implementation: Add `--parent` option to existing `mutsumi/cli/add.py`. Calls `add_child_task()` from `core/writer.py`.

#### 4.1.3 `mutsumi list --search <QUERY> --sort <FIELD>`

```
mutsumi list --search "deploy"
mutsumi list --sort priority
mutsumi list --sort due --reverse
```

Implementation: Add `--search` and `--sort` options to existing `mutsumi/cli/list_cmd.py`. Reuses `sort_tasks()` from `core/loader.py`.

#### 4.1.4 `mutsumi move <TASK_ID> <up|down>`

```
mutsumi move T001 up
mutsumi move T001 down
```

Implementation: New file `mutsumi/cli/move.py`. Calls `reorder_task()` from `core/writer.py`.

#### 4.1.5 `mutsumi clone <TASK_ID>`

```
mutsumi clone T001
```

Implementation: New file `mutsumi/cli/clone.py`. Calls `clone_task()` from `core/writer.py`.

### 4.2 Mouse Additions (P0)

All mouse additions are TUI widget changes.

#### 4.2.1 Detail Panel: `[+Sub]` Button

Add a `[+Sub]` button to `detail_panel.py` next to `[Edit]` and `[Delete]`. Click posts a `AddChildRequested(task_id)` message. App handler opens `TaskForm(parent_id=task_id)`.

#### 4.2.2 Detail Panel: `[▲ Pri]` / `[▼ Pri]` Buttons

Add priority cycle buttons to `detail_panel.py`. Click posts `PriorityChangeRequested(task_id, direction=+1|-1)`. App handler calls `cycle_priority()`.

#### 4.2.3 Footer: `[?Help]` Button

Add a third `_ClickableAction` to `footer_bar.py` that posts `ActionRequested("show_help")`.

#### 4.2.4 TaskRow: Double-Click to Inline Edit

In `task_row.py`, track click timing. If two clicks within 400ms on the title area, call `start_editing()` instead of opening the detail panel.

### 4.3 Mouse Additions (P1 — Phase 5)

These require more complex interaction patterns and are deferred.

| Feature | Approach | Complexity |
|---------|----------|------------|
| Drag-and-drop reorder | Textual `on_mouse_move` + drop zones | High |
| Right-click context menu | Textual doesn't natively support; custom overlay | Medium |
| Column header click-to-sort | Add clickable header row above task list | Medium |

---

## 5. Parity Audit Table (Target State)

After implementing all P0 and P1 items, the matrix should look like this:

| Feature | Keyboard | Mouse | CLI | Status |
|---------|:--------:|:-----:|:---:|--------|
| Toggle done | `space` | Click checkbox | `done` | ✅ Done |
| Create task | `n` | `[+New]` click | `add` | ✅ Done |
| Edit task | `e` | `[Edit]` click | `edit` | ✅ Done |
| Delete task | `dd` | `[Delete]` click | `rm` | ✅ Done |
| Priority cycle | `+`/`-` | `[▲]`/`[▼]` click | `priority` | 🔧 Need mouse+CLI |
| Sort tasks | `s` | Header click | `list --sort` | 🔧 Need mouse+CLI |
| Search/filter | `/` | `[/Search]` click | `list --search` | 🔧 Need CLI |
| Add subtask | `A` | `[+Sub]` click | `add --parent` | 🔧 Need mouse+CLI |
| Move up/down | `J`/`K` | Buttons / drag | `move` | 🔧 Need mouse+CLI |
| Copy task | `y` | Context menu | `clone` | 🔧 Need mouse+CLI |
| Paste task | `p`/`P` | Context menu | — | 🔧 Phase 5 |
| Inline edit | `i` | Double-click | `edit --title` | 🔧 Need mouse |
| Show help | `?` | `[?Help]` click | — | 🔧 Need mouse |
| Tab switch | `1-4` | Tab click | `list --scope` | ✅ Done |
| Navigate | `j`/`k` | Scroll | N/A | ✅ N/A |
| Quit | `q` | `Ctrl+C` | N/A | ✅ N/A |

---

## 6. Testing Strategy

### 6.1 CLI Tests

Each new CLI command gets a test class in `tests/test_cli_commands.py`:

```python
class TestCliPriority:
    def test_priority_up(self) -> None: ...
    def test_priority_down(self) -> None: ...
    def test_priority_clamp(self) -> None: ...
    def test_priority_not_found(self) -> None: ...

class TestCliMove:
    def test_move_up(self) -> None: ...
    def test_move_down(self) -> None: ...
    def test_move_boundary(self) -> None: ...

class TestCliClone:
    def test_clone(self) -> None: ...
    def test_clone_with_children(self) -> None: ...

class TestCliListExtended:
    def test_list_with_search(self) -> None: ...
    def test_list_with_sort(self) -> None: ...
    def test_list_with_sort_reverse(self) -> None: ...
```

### 6.2 TUI Mouse Tests

```python
@pytest.mark.asyncio
async def test_detail_panel_add_subtask_button(tmp_path: Path) -> None:
    """Click [+Sub] in detail panel should open TaskForm with parent_id."""

@pytest.mark.asyncio
async def test_detail_panel_priority_buttons(tmp_path: Path) -> None:
    """Click [▲ Pri] should increase priority."""

@pytest.mark.asyncio
async def test_double_click_inline_edit(tmp_path: Path) -> None:
    """Double-click title area should start inline editing."""

@pytest.mark.asyncio
async def test_footer_help_button(tmp_path: Path) -> None:
    """Click [?Help] in footer should open help screen."""
```

### 6.3 Parity Matrix Test

A meta-test that programmatically verifies the parity matrix:

```python
def test_parity_matrix_no_regressions() -> None:
    """Ensure every action in PARITY_MATRIX has all three surfaces."""
    for action in PARITY_MATRIX:
        assert action.has_keyboard, f"{action.name} missing keyboard"
        assert action.has_mouse, f"{action.name} missing mouse"
        assert action.has_cli, f"{action.name} missing CLI"
```

---

## 7. Design Constraints

### 7.1 Not Everything is Parity-Eligible

Some operations are inherently single-surface:

| Operation | Surface | Why |
|-----------|---------|-----|
| TUI cursor navigation (j/k/arrows) | Keyboard + scroll wheel | No CLI equivalent needed — it's spatial |
| `mutsumi init` | CLI | One-time file generation; TUI auto-creates |
| `mutsumi validate` | CLI | Diagnostic; TUI shows error banner |
| `mutsumi schema` | CLI | Developer/agent tool |
| Quit | Keyboard + Ctrl+C | No CLI equivalent needed |

These are explicitly excluded from the parity requirement.

### 7.2 CLI Semantics vs TUI Semantics

| Principle | Explanation |
|-----------|-------------|
| CLI is **stateless** | Each command reads, modifies, writes. No session. |
| TUI is **stateful** | Clipboard, search query, sort order live in memory. |
| Parity ≠ identical UX | CLI `clone` ≈ TUI `y` then `p`, but CLI does it in one shot. |
| CLI output is **pipe-friendly** | JSON output for `list --json`, plain text by default. |

### 7.3 Mouse Interaction Budget

Mutsumi is a keyboard-first TUI. Mouse support must not:

- Add visual clutter (buttons hidden until hover or in secondary panels).
- Break keyboard flow (focus traps, modal overlays from clicks).
- Require mouse-only gestures (no drag-only features without keyboard alternative).

---

## 8. Implementation Order

```
P0 CLI (priority, add --parent, list --search/--sort, move, clone)
  │
  ├── Can be done independently, one file per command
  │
P0 Mouse (detail panel buttons, footer help button)
  │
  ├── Small widget changes, testable in isolation
  │
P1 Mouse (double-click inline edit)
  │
P1 CLI (move, clone — if not in P0 batch)
  │
P2 (deferred to Phase 5)
  └── Drag-and-drop, right-click context menu, column header sorting
```

---

## 9. Open Questions

1. **Paste via CLI**: Should `mutsumi clone` also support `--before <ID>` to match `P` (paste above)?
2. **Sort persistence**: Should `mutsumi list --sort` also modify the file order, or just display order?
3. **Context menu**: Textual has no native right-click support. Worth building a custom overlay, or skip for v1?

---

## Appendix A: File Impact

| File | Change |
|------|--------|
| `mutsumi/cli/priority.py` | **New** — `priority` subcommand |
| `mutsumi/cli/move.py` | **New** — `move` subcommand |
| `mutsumi/cli/clone.py` | **New** — `clone` subcommand |
| `mutsumi/cli/add.py` | **Modify** — add `--parent` option |
| `mutsumi/cli/list_cmd.py` | **Modify** — add `--search`, `--sort`, `--reverse` |
| `mutsumi/cli/__init__.py` | **Modify** — register new subcommands |
| `mutsumi/tui/detail_panel.py` | **Modify** — add `[+Sub]`, `[▲ Pri]`/`[▼ Pri]` buttons |
| `mutsumi/tui/footer_bar.py` | **Modify** — add `[?Help]` button |
| `mutsumi/tui/task_row.py` | **Modify** — double-click detection |
| `tests/test_cli_commands.py` | **Modify** — new test classes |
| `tests/test_tui_crud.py` | **Modify** — mouse interaction tests |
