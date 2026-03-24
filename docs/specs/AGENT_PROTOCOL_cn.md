# Mutsumi Agent 集成协议

| 版本 | 1.0 |
|---|---|
| 状态 | 草案 |
| 日期 | 2026-03-23 |

> **[English Version](./AGENT_PROTOCOL.md)** | **[日本語版](./AGENT_PROTOCOL_ja.md)**

---

## 1. 概述

本文档定义了外部 agents——AI CLI、自定义脚本或简单 shell 工具——如何与 Mutsumi 集成。

**核心原则：** Mutsumi 与 agent 无关。任何能正确读取和写入任务文件的程序都可以充当 controller。

### 1.1 活动文件命名

- **规范任务文件：** `mutsumi.json`
- **旧回退文件：** `tasks.json`

对于新项目，agents 应以 **`./mutsumi.json`** 为目标。
如果项目仍在使用 `tasks.json`，agents 也可以继续读写这个旧文件。

### 1.2 解析顺序

当未显式给出路径时，Mutsumi 会按以下顺序解析当前活动任务文件：

1. CLI `--path`
2. `./mutsumi.json`
3. `./tasks.json`
4. 新项目默认目标：`./mutsumi.json`

---

## 2. 支持的 Agents

| Agent | 集成级别 |
|---|---|
| Claude Code | Native |
| Codex CLI | Native |
| Gemini CLI | Native |
| OpenCode | Native |
| Aider | Native |
| Custom scripts | Native |

“Native” 表示不需要网络桥接或 SDK。文件 I/O 就足够了。

---

## 3. 写入协议（Agent → Mutsumi）

### 3.1 工作流

```text
1. 解析当前活动任务文件
2. 读取当前 JSON 对象
3. 修改 tasks 数组
4. 以原子方式写回整个文件
5. Mutsumi 检测到保存并重新渲染
```

### 3.2 规则

| 规则 | 说明 |
|---|---|
| 保留未知字段 | 永远不要删除你不认识的字段 |
| 原子写入 | 写入 temp file + `os.replace()` / rename |
| 合法 JSON | 每次写入后文件都必须保持合法 JSON |
| 合法 ID | 新任务应使用 UUIDv7 或其他唯一字符串 |
| 必填字段 | 每个任务都必须有 `id`、`title`、`status` |
| 枚举合规 | `status`：`pending` / `done`；`priority`：`high` / `normal` / `low`；`scope`：`day` / `week` / `month` / `inbox` |

### 3.3 最小 Python 示例

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

### 3.4 完成任务

```python
for task in data["tasks"]:
    if task["id"] == target_id:
        task["status"] = "done"
        task["completed_at"] = dt.datetime.now(dt.UTC).isoformat()
        break
```

---

## 4. Prompt 模板

下面这个片段可以安全地放进 agent 指令文件。

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

## 5. CLI 优先集成

对于简单任务操作，agents 应优先使用 CLI，而不是手写 JSON 变更。

```bash
mutsumi add "Fix auth" --priority high --scope day --tags "dev,backend"
mutsumi done <id-prefix>
mutsumi edit <id-prefix> --title "New title" --priority low
mutsumi rm <id-prefix>
mutsumi list
mutsumi validate
mutsumi schema
```

优点：

- 更不容易发生 schema 漂移
- 更不容易出现部分写入
- 文件解析顺序一致（优先 `mutsumi.json`，回退 `tasks.json`）

---

## 6. 事件日志（可选）

Mutsumi 可以为本地审计/历史记录追加 JSONL 事件。
默认路径通常是：

```text
~/.local/share/mutsumi/events.jsonl
```

### 6.1 示例事件

```jsonl
{"timestamp":"2026-03-23T10:00:00+00:00","type":"task_added","task_id":"01JQ...","title":"Write tests"}
{"timestamp":"2026-03-23T10:05:00+00:00","type":"task_edited","task_id":"01JQ...","title":"Write more tests"}
{"timestamp":"2026-03-23T10:06:00+00:00","type":"task_deleted","task_id":"01JQ...","title":"Obsolete task"}
```

### 6.2 当前事件名

应用会发出的事件示例包括：

- `task_added`
- `child_task_added`
- `task_edited`
- `task_deleted`
- `task_toggled`
- `priority_changed`
- `task_reordered`
- `task_pasted`

事件日志是附加元数据，不属于任务文件契约的一部分。

---

## 7. 错误处理

### 7.1 如果 agent 写入了非法 JSON

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

### 7.2 推荐恢复流程

如果 agent 不确定自己的写入是否成功：

1. 运行 `mutsumi validate`
2. 检查当前活动任务文件
3. 如有需要，查看本地错误日志（默认：`~/.local/share/mutsumi/error.log`）

### 7.3 自修复指令

```markdown
After writing to the Mutsumi task file, run `mutsumi validate` if you are unsure the file is still valid JSON.
```

---

## 8. Setup 模式

`mutsumi setup --agent <name>` 支持三种模式：

| 模式 | 行为 |
|---|---|
| `skills` | 将内置的 Mutsumi skills 安装到 agent 的 skill 目录 |
| `skills+project-doc` | 安装 skills，并向 `CLAUDE.md`、`AGENTS.md`、`GEMINI.md` 或 `opencode.md` 追加集成片段 |
| `snippet` | 向 stdout 打印可复制的 prompt 片段 |

### 8.1 默认行为

```bash
mutsumi setup --agent claude-code
```

这只会安装 skills。
除非显式请求 `--mode skills+project-doc`，否则**不会**修改项目指令文件。

---

## 9. 多 Agent 协调

### 9.1 同一个项目文件

当多个 agents 操作同一个 `mutsumi.json` 时：

1. 始终先读再写
2. 尽量减少无关改动
3. 尽可能保持操作幂等
4. 如果两个写入者竞争，预期结果是 **last write wins**

### 9.2 不同项目文件

在多源场景下，每个项目都应保留自己的任务文件。
这是首选的隔离模型：

```text
project-a/mutsumi.json
project-b/mutsumi.json
~/.mutsumi/mutsumi.json   # personal tasks
```

Mutsumi 可以在 UI 中聚合这些文件，而不要求 agents 共享同一个文件。

---

## 10. 兼容性摘要

- `mutsumi.json` 与旧的 `tasks.json` 使用同一份 Schema
- 新文档、新示例和新项目应使用 `mutsumi.json`
- `tasks.json` 仅作为向后兼容继续受支持
