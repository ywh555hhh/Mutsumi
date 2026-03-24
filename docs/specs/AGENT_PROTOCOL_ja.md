# Mutsumi Agent 連携プロトコル

| バージョン | 1.0 |
|---|---|
| ステータス | ドラフト |
| 日付 | 2026-03-23 |

> **[English Version](./AGENT_PROTOCOL.md)** | **[中文版](./AGENT_PROTOCOL_cn.md)**

---

## 1. 概要

このドキュメントは、外部 agents——AI CLI、カスタムスクリプト、または単純な shell ツール——がどのように Mutsumi と統合するかを定義します。

**基本原則:** Mutsumi は agent-agnostic です。タスクファイルを正しく読み書きできる任意のプログラムが controller になれます。

### 1.1 アクティブファイル命名

- **正式なタスクファイル:** `mutsumi.json`
- **旧フォールバック:** `tasks.json`

新しいプロジェクトでは、agents は **`./mutsumi.json`** を対象にすべきです。
プロジェクトがまだ `tasks.json` を使っている場合は、その旧ファイルを読み書きし続けても構いません。

### 1.2 解決順序

明示的なパスが指定されていない場合、Mutsumi は次のようにアクティブタスクファイルを解決します。

1. CLI `--path`
2. `./mutsumi.json`
3. `./tasks.json`
4. 新規プロジェクトのデフォルトターゲット: `./mutsumi.json`

---

## 2. サポートされる Agents

| Agent | 連携レベル |
|---|---|
| Claude Code | Native |
| Codex CLI | Native |
| Gemini CLI | Native |
| OpenCode | Native |
| Aider | Native |
| Custom scripts | Native |

“Native” とは、ネットワークブリッジや SDK が不要で、ファイル I/O だけで十分という意味です。

---

## 3. 書き込みプロトコル（Agent → Mutsumi）

### 3.1 ワークフロー

```text
1. アクティブなタスクファイルを解決する
2. 現在の JSON オブジェクトを読む
3. tasks 配列を変更する
4. ファイル全体をアトミックに書き戻す
5. Mutsumi が保存を検知して再描画する
```

### 3.2 ルール

| ルール | 説明 |
|---|---|
| 未知フィールドを保持する | 認識できないフィールドは絶対に削除しない |
| アトミック書き込み | temp file + `os.replace()` / rename で書く |
| 正しい JSON | すべての書き込み後もファイルは正しい JSON でなければならない |
| 正しい ID | 新規タスクには UUIDv7 または別の一意な文字列を使うべき |
| 必須フィールド | すべてのタスクに `id`、`title`、`status` が必要 |
| 列挙値準拠 | `status`: `pending` / `done`; `priority`: `high` / `normal` / `low`; `scope`: `day` / `week` / `month` / `inbox` |

### 3.3 最小 Python 例

```python
from __future__ import annotations

import datetime as dt
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
    "id": f"task-{int(dt.datetime.now(dt.UTC).timestamp())}",
    "title": "Fix login bug",
    "status": "pending",
    "scope": "day",
    "priority": "high",
    "tags": ["bugfix"],
    "created_at": dt.datetime.now(dt.UTC).isoformat(),
    "children": [],
}
data.setdefault("tasks", []).append(new_task)

with tempfile.NamedTemporaryFile("w", dir=".", suffix=".tmp", delete=False, encoding="utf-8") as tmp:
    json.dump(data, tmp, ensure_ascii=False, indent=2)
    tmp_path = Path(tmp.name)

os.replace(tmp_path, path)
```

### 3.4 タスク完了

```python
for task in data["tasks"]:
    if task["id"] == target_id:
        task["status"] = "done"
        task["completed_at"] = dt.datetime.now(dt.UTC).isoformat()
        break
```

---

## 4. Prompt テンプレート

次のスニペットは agent instruction file に安全に含められます。

```markdown
## Mutsumi Task Integration

This project uses Mutsumi for task management.
Tasks live in `./mutsumi.json` (fallback: `./tasks.json`).

Rules:
- Read the whole file before writing
- Preserve unknown fields
- Write the ENTIRE file back atomically
- Required task fields: `id`, `title`, `status`
- Valid status values: `pending`, `done`
- Prefer `mutsumi` CLI commands for simple CRUD
```

---

## 5. CLI 優先の統合

単純なタスク操作では、agents は手書きの JSON 変更よりも CLI を優先すべきです。

```bash
mutsumi add "Fix auth" --priority high --scope day --tags "dev,backend"
mutsumi done <id-prefix>
mutsumi edit <id-prefix> --title "New title" --priority low
mutsumi rm <id-prefix>
mutsumi list
mutsumi validate
mutsumi schema
```

利点:

- schema drift のリスクが低い
- 部分書き込みの可能性が低い
- ファイル解決順序が一貫する（`mutsumi.json` 優先、`tasks.json` フォールバック）

---

## 6. イベントログ（任意）

Mutsumi はローカル監査 / 履歴用途のために JSONL イベントを追記できます。
デフォルトパスは通常次の通りです。

```text
~/.local/share/mutsumi/events.jsonl
```

### 6.1 イベント例

```jsonl
{"timestamp":"2026-03-23T10:00:00+00:00","type":"task_added","task_id":"01JQ...","title":"Write tests"}
{"timestamp":"2026-03-23T10:05:00+00:00","type":"task_edited","task_id":"01JQ...","title":"Write more tests"}
{"timestamp":"2026-03-23T10:06:00+00:00","type":"task_deleted","task_id":"01JQ...","title":"Obsolete task"}
```

### 6.2 現在のイベント名

アプリが発行するイベント例:

- `task_added`
- `child_task_added`
- `task_edited`
- `task_deleted`
- `task_toggled`
- `priority_changed`
- `task_reordered`
- `task_pasted`

イベントログは追加的なメタデータであり、task-file contract の一部ではありません。

---

## 7. エラーハンドリング

### 7.1 agent が不正な JSON を書いた場合

```text
agent writes invalid JSON
        ↓
Mutsumi detects file change
        ↓
parse fails
        ↓
TUI shows an error banner instead of crashing
        ↓
last good state remains visible until the file is fixed
```

### 7.2 推奨される回復フロー

agent が自分の書き込み成功に確信を持てない場合:

1. `mutsumi validate` を実行する
2. アクティブなタスクファイルを確認する
3. 必要ならローカル error log を確認する（デフォルト: `~/.local/share/mutsumi/error.log`）

### 7.3 自己修復指示

```markdown
After writing to the Mutsumi task file, run `mutsumi validate` if you are unsure the file is still valid JSON.
```

---

## 8. Setup モード

`mutsumi setup --agent <name>` は 3 つのモードをサポートします。

| モード | 挙動 |
|---|---|
| `skills` | bundled Mutsumi skills を agent の skill directory にインストール |
| `skills+project-doc` | skills をインストールし、`CLAUDE.md`、`AGENTS.md`、`GEMINI.md`、`opencode.md` に integration snippet を追記 |
| `snippet` | コピー可能な prompt snippet を stdout に出力 |

### 8.1 デフォルト動作

```bash
mutsumi setup --agent claude-code
```

これは skills だけをインストールします。
`--mode skills+project-doc` を明示しない限り、project instruction files は**変更しません**。

---

## 9. マルチ Agent 協調

### 9.1 同じ project file

複数の agents が同じ `mutsumi.json` に触る場合:

1. 常に read before write
2. 無関係な変更を最小化する
3. 可能な限り操作を冪等に保つ
4. 2 つの writer が競合した場合は **last write wins** を想定する

### 9.2 別の project file

multi-source setup では、各 project が自分の task file を持つべきです。
これが推奨される分離モデルです。

```text
project-a/mutsumi.json
project-b/mutsumi.json
~/.mutsumi/mutsumi.json   # personal tasks
```

Mutsumi は agents に単一ファイル共有を強制することなく、これらを UI 上で集約できます。

---

## 10. 互換性サマリー

- `mutsumi.json` と旧 `tasks.json` は同じ Schema を使う
- 新しいドキュメント、新しい例、新しいプロジェクトは `mutsumi.json` を使うべき
- `tasks.json` は後方互換のためにのみ引き続きサポートされる
