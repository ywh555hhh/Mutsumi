# Mutsumi Agent 集成协议

| 版本   | 0.1.0              |
|--------|---------------------|
| 状态   | 草案                |
| 日期   | 2026-03-21          |

> **[English Version](./AGENT_PROTOCOL.md)** | **[日本語版](./AGENT_PROTOCOL_ja.md)**

---

## 1. 概述

本文档定义了外部 Agent（AI CLI 工具、自定义脚本等）如何与 Mutsumi 的 `tasks.json` 进行读写交互。

**核心原则：Mutsumi 不绑定任何 Agent。任何能正确读写 JSON 的程序都是合法的 Controller。**

## 2. 支持的 Agent（非穷举）

| Agent          | 类型              | 集成级别                   |
|----------------|-------------------|---------------------------|
| Claude Code    | AI CLI            | Native（推荐）             |
| Codex CLI      | AI CLI            | Native                    |
| Gemini CLI     | AI CLI            | Native                    |
| OpenCode       | AI CLI            | Native                    |
| Aider          | AI CLI            | Native                    |
| shell scripts  | 自定义            | Native                    |
| cron jobs      | 系统              | Native                    |

"Native" 意味着只需要读写 JSON 文件，无需安装任何 SDK 或插件。

## 3. 写入协议（Agent → Mutsumi）

### 3.1 工作流

```
1. 读取当前 tasks.json（全量）
2. 解析为 JSON
3. 修改 tasks 数组（增/改/删）
4. 回写整个文件（不要 partial write）
5. Mutsumi 的 watchdog 检测到变化 → 重新渲染
```

### 3.2 规则

| 规则                          | 说明                                                                     |
|-------------------------------|--------------------------------------------------------------------------|
| **保留未知字段**               | 不要删除你不认识的字段，原样保留                                            |
| **原子写入**                   | 推荐写入临时文件再 rename，避免 Mutsumi 读到半写状态                         |
| **合法 JSON**                 | 写入后文件必须是合法 JSON                                                  |
| **生成合法 ID**               | 新任务的 ID 推荐使用 UUIDv7，至少保证唯一性                                  |
| **必填字段**                   | 每个任务必须包含 `id`, `title`, `status`                                   |
| **枚举合规**                   | `status` 只能是 `"pending"` / `"done"`                                    |

### 3.3 添加任务

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

### 3.4 完成任务

```python
for task in data["tasks"]:
    if task["id"] == target_id:
        task["status"] = "done"
        task["completed_at"] = datetime.datetime.now(datetime.UTC).isoformat()
        break
```

### 3.5 Agent Prompt 模板

以下是推荐嵌入到 Agent system prompt 中的 Mutsumi 集成指令：

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

## 4. 读取协议（Mutsumi → Agent）

### 4.1 事件日志

当用户在 TUI 中操作时，Mutsumi 将事件追加到 `events.jsonl`（JSONL 格式，每行一个事件）：

```jsonl
{"ts":"2026-03-21T10:00:00Z","event":"task_completed","task_id":"01JQ...","title":"修复缓存 Bug","source":"tui"}
{"ts":"2026-03-21T10:01:22Z","event":"task_created","task_id":"01JQ...","title":"写单元测试","source":"tui"}
{"ts":"2026-03-21T10:05:00Z","event":"task_deleted","task_id":"01JQ...","title":"过时的任务","source":"tui"}
{"ts":"2026-03-21T10:06:30Z","event":"task_updated","task_id":"01JQ...","changes":{"priority":"high→low"},"source":"tui"}
```

### 4.2 事件类型

| 事件              | 字段                                      | 说明               |
|-------------------|-------------------------------------------|--------------------|
| `task_created`    | task_id, title                            | 新任务创建          |
| `task_completed`  | task_id, title                            | 任务标记完成        |
| `task_deleted`    | task_id, title                            | 任务删除           |
| `task_updated`    | task_id, changes (dict)                   | 任务字段修改        |
| `schema_error`    | file, message                             | JSON 校验失败       |

### 4.3 Agent 消费方式

Agent 可以通过以下方式消费事件流：

```bash
# 实时监听（shell）
tail -f events.jsonl | jq .

# 在 Agent prompt 中引用
"Check events.jsonl for recent user actions on tasks"
```

### 4.4 事件日志轮转

- 默认保留最近 1000 条事件
- 超出后自动截断旧事件
- 可在 `config.toml` 中配置 `events.max_lines`

## 5. Schema 发现

Agent 可以通过 CLI 获取当前的 JSON Schema：

```bash
mutsumi schema
# 输出 JSON Schema 到 stdout，供 Agent 理解数据结构

mutsumi schema --format markdown
# 输出 Markdown 格式的字段说明
```

## 6. 错误处理

### 6.1 当 Agent 写入错误数据时

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

### 6.2 自愈 Prompt

推荐在 Agent prompt 中加入：

```markdown
After writing to tasks.json, check ~/.local/share/mutsumi/error.log
for any schema validation errors. If errors exist, fix and rewrite.
```

## 7. 多 Agent 协同

当多个 Agent 同时操作同一个 `tasks.json` 时：

### 7.1 建议

1. **先读后写** — 每次写入前先读取最新版本
2. **最小化写入范围** — 只修改你关心的任务，不要重排其他任务
3. **幂等操作** — 标记完成等操作应当幂等（重复执行不报错）
4. **使用唯一 ID** — UUIDv7 保证不同 Agent 生成的 ID 不冲突

### 7.2 冲突解决

Mutsumi 不提供锁机制。冲突策略：**Last Write Wins**。

在实际使用中，由于 Agent 写入是离散的（通常间隔数秒到数分钟），冲突概率极低。
