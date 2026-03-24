# Mutsumi — Agent チートシート

> Mutsumi 経由でタスクを管理する AI agents 向けの 1 ページリファレンス。
>
> **[English Version](./AGENT.md)** | **[中文版](./AGENT_cn.md)**

## Quick Start

Mutsumi はローカル TUI で、現在の active task file を監視し、保存時に再描画します。

- **Canonical project file:** `./mutsumi.json`
- **Legacy fallback:** `./tasks.json`
- **Preferred workflow:** 可能なら `mutsumi` CLI を使う
- **Direct JSON is allowed:** file 全体を読み、更新し、atomic に書き戻す

両方の file が無い場合、新しい project では **`mutsumi.json`** を作成してください。

## Task File Discovery

Mutsumi は active file を次の順序で解決します。

1. explicit CLI `--path`
2. `./mutsumi.json`
3. `./tasks.json`（backward-compatible fallback）
4. new project の default target: `./mutsumi.json`

## Schema

| Field | Type | Required | Default | Notes |
|---|---|---:|---|---|
| `id` | string | Yes | — | Unique ID, UUIDv7 推奨 |
| `title` | string | Yes | — | Task title |
| `status` | string | Yes | `"pending"` | `"pending"` または `"done"` |
| `scope` | string | No | `"inbox"` | `"day"`, `"week"`, `"month"`, `"inbox"` |
| `priority` | string | No | `"normal"` | `"high"`, `"normal"`, `"low"` |
| `tags` | string[] | No | `[]` | Free-form labels |
| `children` | Task[] | No | `[]` | Recursive subtasks |
| `due_date` | string | No | — | ISO date, 例 `"2026-03-25"` |
| `description` | string | No | — | Longer text |
| `created_at` | string | No | auto | ISO timestamp |
| `completed_at` | string | No | — | `done` になったとき設定 |

## Behavioral Rules

1. **Preserve unknown fields.** 認識しない field を削除しない。
2. **Write the whole file.** 部分更新ではなく file 全体を書き戻す。
3. **Use atomic writes.** temp file + rename/replace。
4. **Prefer `mutsumi.json`.** project が legacy filename のときだけ `tasks.json` を使う。
5. **Keep enums valid.**
   - `status`: `pending` / `done`
   - `priority`: `high` / `normal` / `low`
   - `scope`: `day` / `week` / `month` / `inbox`

## CLI Commands

```bash
mutsumi add "title" --priority high --scope day --tags "dev,urgent"
mutsumi done <id-prefix>
mutsumi edit <id-prefix> --title "new title" --priority low
mutsumi rm <id-prefix>
mutsumi list
mutsumi validate
mutsumi schema
mutsumi init                  # create ./mutsumi.json
mutsumi init --personal       # create ~/.mutsumi/mutsumi.json
mutsumi init --project        # create ./mutsumi.json and register current repo
mutsumi setup --agent claude-code
mutsumi project add /path/to/repo
mutsumi migrate
```

## Direct JSON Protocol

CLI を使わない場合:

1. active file を見つける（`mutsumi.json` 優先、`tasks.json` fallback）
2. JSON object 全体を読む
3. `tasks` array を修正する
4. **entire file** を atomic に書き戻す
5. unknown top-level fields と task-level fields を保持する

File shape:

```json
{
  "version": 1,
  "tasks": [
    {
      "id": "01JQ8X7K3M0000000000000001",
      "title": "Refactor auth module",
      "status": "pending",
      "scope": "day",
      "priority": "high",
      "tags": ["dev", "backend"],
      "children": []
    }
  ]
}
```

## Minimal Python Example

```python
from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path


def resolve_task_file() -> Path:
    preferred = Path("mutsumi.json")
    legacy = Path("tasks.json")
    if preferred.exists():
        return preferred
    if legacy.exists():
        return legacy
    return preferred


path = resolve_task_file()

data = {"version": 1, "tasks": []}
if path.exists():
    data = json.loads(path.read_text(encoding="utf-8"))

new_task = {
    "id": "task-001",
    "title": "Write weekly report",
    "status": "pending",
    "scope": "week",
    "priority": "normal",
    "tags": ["life"],
    "children": [],
}
data.setdefault("tasks", []).append(new_task)

with tempfile.NamedTemporaryFile("w", dir=".", suffix=".tmp", delete=False, encoding="utf-8") as tmp:
    json.dump(data, tmp, ensure_ascii=False, indent=2)
    tmp_path = Path(tmp.name)

os.replace(tmp_path, path)
```

## Agent Integration Setup

```bash
# Install Mutsumi skills into the agent's skill directory
mutsumi setup --agent claude-code
mutsumi setup --agent codex-cli
mutsumi setup --agent gemini-cli
mutsumi setup --agent opencode

# Install skills AND append project instructions to CLAUDE.md / AGENTS.md / etc.
mutsumi setup --agent claude-code --mode skills+project-doc

# Print a manual snippet for unsupported agents
mutsumi setup --agent aider --mode snippet
mutsumi setup --agent custom --mode snippet
```

### Mode Summary

- `skills` — bundled `SKILL.md` packages だけを install
- `skills+project-doc` — skills を install し、agent doc に project snippet を追記
- `snippet` — コピー可能な instructions を stdout に出力

## Event Log

event logging が有効な場合、Mutsumi は JSONL records を platform data directory に追記します。
通常の default path は次の通りです。

```text
~/.local/share/mutsumi/events.jsonl
```

Example records:

```jsonl
{"timestamp":"2026-03-23T10:00:00+00:00","type":"task_added","task_id":"01JQ...","title":"Write tests"}
{"timestamp":"2026-03-23T10:02:00+00:00","type":"task_toggled","task_id":"01JQ..."}
{"timestamp":"2026-03-23T10:05:00+00:00","type":"priority_changed","task_id":"01JQ..."}
```

## Safe Defaults for Agents

- `mutsumi.json` を優先する
- simple CRUD では CLI を使う
- JSON を直接書く場合は atomic replace を使う
- unknown fields を正確に保持する
- user task を黙って削除しない
- 大きな編集後に不安なら `mutsumi validate` を実行する
