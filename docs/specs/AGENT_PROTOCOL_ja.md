# Mutsumi Agent 連携プロトコル

| バージョン | 0.1.0              |
|-----------|---------------------|
| ステータス | ドラフト             |
| 日付       | 2026-03-21          |

> **[English Version](./AGENT_PROTOCOL.md)** | **[中文版](./AGENT_PROTOCOL_cn.md)**

---

## 1. 概要

このドキュメントは、外部 Agent（AI CLI ツール、カスタムスクリプトなど）が Mutsumi の `tasks.json` をどのように読み書きするかを定義します。

**基本原則: Mutsumi は特定の Agent にバインドされません。JSON を正しく読み書きできるプログラムであれば、すべて正当なコントローラーです。**

## 2. 対応 Agent（非網羅的）

| Agent          | 種別              | 連携レベル                  |
|----------------|-------------------|--------------------------|
| Claude Code    | AI CLI            | ネイティブ（推奨）           |
| Codex CLI      | AI CLI            | ネイティブ                  |
| Gemini CLI     | AI CLI            | ネイティブ                  |
| OpenCode       | AI CLI            | ネイティブ                  |
| Aider          | AI CLI            | ネイティブ                  |
| shell scripts  | カスタム           | ネイティブ                  |
| cron jobs      | システム           | ネイティブ                  |

「ネイティブ」とは、JSON ファイルの読み書きのみが必要であることを意味します — SDK やプラグインのインストールは不要です。

## 3. 書き込みプロトコル（Agent → Mutsumi）

### 3.1 ワークフロー

```
1. Read the current tasks.json (full content)
2. Parse as JSON
3. Modify the tasks array (add/update/delete)
4. Write the ENTIRE file back (no partial writes)
5. Mutsumi's watchdog detects change → re-renders
```

### 3.2 ルール

| ルール                          | 説明                                                                    |
|-------------------------------|--------------------------------------------------------------------------|
| **不明フィールドの保持**         | 認識できないフィールドを削除しないでください。そのまま保持してください              |
| **アトミック書き込み**           | 推奨: 一時ファイルに書き込んでからリネームし、Mutsumi が書き込み途中の状態を読むのを防ぎます |
| **有効な JSON**                | 書き込み後のファイルは有効な JSON でなければなりません                         |
| **有効な ID の生成**            | 新規タスクの ID には UUIDv7 を使用してください。最低限、一意性を確保してください    |
| **必須フィールド**              | すべてのタスクには `id`、`title`、`status` が必要です                       |
| **列挙型の遵守**               | `status` は `"pending"` / `"done"` のみ使用できます                       |

### 3.3 タスクの追加

```python
import json, uuid, datetime

# Read
with open("tasks.json") as f:
    data = json.load(f)

# Add
new_task = {
    "id": str(uuid.uuid7()),  # or any unique string
    "title": "修复登录 Bug",
    "status": "pending",
    "scope": "day",
    "priority": "high",
    "tags": ["bugfix"],
    "created_at": datetime.datetime.now(datetime.UTC).isoformat(),
    "children": []
}
data["tasks"].append(new_task)

# Write (atomic)
import tempfile, os
tmp = tempfile.NamedTemporaryFile(
    mode='w', dir='.', suffix='.tmp', delete=False
)
json.dump(data, tmp, ensure_ascii=False, indent=2)
tmp.close()
os.rename(tmp.name, "tasks.json")
```

### 3.4 タスクの完了

```python
for task in data["tasks"]:
    if task["id"] == target_id:
        task["status"] = "done"
        task["completed_at"] = datetime.datetime.now(datetime.UTC).isoformat()
        break
```

### 3.5 Agent プロンプトテンプレート

以下は、Agent のシステムプロンプトに埋め込むための推奨 Mutsumi 連携指示です。

```markdown
## Task Management (Mutsumi Integration)

You have access to a local task file at `./tasks.json`.
When the user asks you to manage tasks, read and write this file.

Schema:
- Required fields: id (unique string), title (string), status ("pending" | "done")
- Optional fields: scope ("day"|"week"|"month"|"inbox"), priority ("high"|"normal"|"low"), tags (string[]), children (Task[]), due_date (ISO date), description (string)
- Preserve any fields you don't recognize — do NOT delete them
- Use atomic write (temp file + rename) when possible
- Generate UUIDv7 for new task IDs

Example task:
{"id":"01JQ...","title":"Fix auth","status":"pending","scope":"day","priority":"high","tags":["dev"],"children":[]}
```

## 4. 読み取りプロトコル（Mutsumi → Agent）

### 4.1 イベントログ

ユーザーが TUI で操作を行うと、Mutsumi は `events.jsonl`（JSONL 形式、1行1イベント）にイベントを追記します。

```jsonl
{"ts":"2026-03-21T10:00:00Z","event":"task_completed","task_id":"01JQ...","title":"修复缓存 Bug","source":"tui"}
{"ts":"2026-03-21T10:01:22Z","event":"task_created","task_id":"01JQ...","title":"写单元测试","source":"tui"}
{"ts":"2026-03-21T10:05:00Z","event":"task_deleted","task_id":"01JQ...","title":"过时的任务","source":"tui"}
{"ts":"2026-03-21T10:06:30Z","event":"task_updated","task_id":"01JQ...","changes":{"priority":"high→low"},"source":"tui"}
```

### 4.2 イベントタイプ

| イベント           | フィールド                               | 説明                    |
|-------------------|-------------------------------------------|--------------------------|
| `task_created`    | task_id, title                            | 新規タスクが作成されました   |
| `task_completed`  | task_id, title                            | タスクが完了にマークされました |
| `task_deleted`    | task_id, title                            | タスクが削除されました       |
| `task_updated`    | task_id, changes (dict)                   | タスクのフィールドが変更されました |
| `schema_error`    | file, message                             | JSON 検証に失敗しました     |

### 4.3 Agent による消費

Agent は以下の方法でイベントストリームを消費できます:

```bash
# Real-time monitoring (shell)
tail -f events.jsonl | jq .

# Reference in Agent prompt
"Check events.jsonl for recent user actions on tasks"
```

### 4.4 イベントログのローテーション

- デフォルトでは直近の1000イベントを保持します
- 古いイベントは自動的に切り捨てられます
- `config.toml` の `events.max_lines` で設定可能です

## 5. スキーマディスカバリー

Agent は CLI を通じて現在の JSON Schema を取得できます。

```bash
mutsumi schema
# Outputs JSON Schema to stdout for Agent to understand the data structure

mutsumi schema --format markdown
# Outputs field descriptions in Markdown format
```

## 6. エラーハンドリング

### 6.1 Agent が不正なデータを書き込んだ場合

```
Agent writes invalid JSON
       │
       ▼
Mutsumi watchdog detects change
       │
       ▼
Parse fails → TUI shows error banner
       │       "tasks.json has errors, showing last valid state"
       │
       ▼
Error logged to stderr + error.log
       │
       ▼
Event emitted: {"event":"schema_error","file":"tasks.json","message":"..."}
       │
       ▼
Agent can read error.log or events.jsonl to self-correct
```

### 6.2 自己修復プロンプト

Agent プロンプトに以下を含めることを推奨します:

```markdown
After writing to tasks.json, check ~/.local/share/mutsumi/error.log
for any schema validation errors. If errors exist, fix and rewrite.
```

## 7. マルチ Agent の協調

複数の Agent が同じ `tasks.json` を同時に操作する場合:

### 7.1 推奨事項

1. **書き込み前に読み取り** — 書き込み前に必ず最新バージョンを読み取ってください
2. **書き込み範囲の最小化** — 自分が関心のあるタスクのみを変更し、他のタスクの順序を変更しないでください
3. **冪等な操作** — 完了マークなどの操作は冪等であるべきです（繰り返してもエラーにならないこと）
4. **一意の ID を使用** — UUIDv7 により、異なる Agent からの ID が衝突しないことが保証されます

### 7.2 競合の解決

Mutsumi はロック機構を提供しません。競合戦略: **Last Write Wins**（最後の書き込みが優先）。

実際には、Agent の書き込みは離散的（通常は数秒から数分間隔）であるため、競合の発生確率は極めて低いです。
