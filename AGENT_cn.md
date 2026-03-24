# Mutsumi — Agent 速查表

> 面向通过 Mutsumi 管理任务的 AI agents 的一页参考。
>
> **[English Version](./AGENT.md)** | **[日本語版](./AGENT_ja.md)**

## 快速开始

Mutsumi 是一个本地 TUI，会监听当前激活的任务文件，并在保存后重新渲染。

- **规范项目文件：** `./mutsumi.json`
- **旧回退文件：** `./tasks.json`
- **推荐工作流：** 能用 `mutsumi` CLI 时优先用 CLI
- **允许直接写 JSON：** 先读完整文件，更新它，再以原子方式整体写回

如果这两个文件都不存在，新项目应创建 **`mutsumi.json`**。

## 任务文件发现顺序

Mutsumi 按以下顺序解析当前激活文件：

1. 显式 CLI `--path`
2. `./mutsumi.json`
3. `./tasks.json`（向后兼容回退）
4. 新项目默认目标：`./mutsumi.json`

## Schema

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---:|---|---|
| `id` | string | 是 | — | 唯一 ID，推荐 UUIDv7 |
| `title` | string | 是 | — | 任务标题 |
| `status` | string | 是 | `"pending"` | `"pending"` 或 `"done"` |
| `scope` | string | 否 | `"inbox"` | `"day"`、`"week"`、`"month"`、`"inbox"` |
| `priority` | string | 否 | `"normal"` | `"high"`、`"normal"`、`"low"` |
| `tags` | string[] | 否 | `[]` | 自由标签 |
| `children` | Task[] | 否 | `[]` | 递归子任务 |
| `due_date` | string | 否 | — | ISO 日期，例如 `"2026-03-25"` |
| `description` | string | 否 | — | 更长的文本说明 |
| `created_at` | string | 否 | auto | ISO 时间戳 |
| `completed_at` | string | 否 | — | 当状态变为 `done` 时设置 |

## 行为规则

1. **保留未知字段。** 绝不要删除不认识的字段。
2. **整体写回文件。** 不要尝试局部原地修改。
3. **使用原子写入。** 临时文件 + rename/replace。
4. **优先 `mutsumi.json`。** 只有项目仍使用旧文件名时才使用 `tasks.json`。
5. **保持枚举值合法。**
   - `status`: `pending` / `done`
   - `priority`: `high` / `normal` / `low`
   - `scope`: `day` / `week` / `month` / `inbox`

## CLI 命令

```bash
mutsumi add "title" --priority high --scope day --tags "dev,urgent"
mutsumi done <id-prefix>
mutsumi edit <id-prefix> --title "new title" --priority low
mutsumi rm <id-prefix>
mutsumi list
mutsumi validate
mutsumi schema
mutsumi init                  # 创建 ./mutsumi.json
mutsumi init --personal       # 创建 ~/.mutsumi/mutsumi.json
mutsumi init --project        # 创建 ./mutsumi.json 并注册当前仓库
mutsumi setup --agent claude-code
mutsumi project add /path/to/repo
mutsumi migrate
```

## 直接 JSON 协议

在不通过 CLI 工作时：

1. 先检测激活文件（优先 `mutsumi.json`，回退到 `tasks.json`）
2. 读取完整 JSON 对象
3. 修改 `tasks` 数组
4. 以原子方式把**整个文件**写回
5. 保留所有未知的顶层字段和任务级字段

文件结构：

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

## 最小 Python 示例

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

## Agent 集成设置

```bash
# 将 Mutsumi skills 安装到 agent 的 skill 目录
mutsumi setup --agent claude-code
mutsumi setup --agent codex-cli
mutsumi setup --agent gemini-cli
mutsumi setup --agent opencode

# 安装 skills，同时向 CLAUDE.md / AGENTS.md / 等文件追加项目说明
mutsumi setup --agent claude-code --mode skills+project-doc

# 为不受支持的 agent 打印手工 snippet
mutsumi setup --agent aider --mode snippet
mutsumi setup --agent custom --mode snippet
```

### 模式摘要

- `skills` —— 只安装内置 `SKILL.md` 包
- `skills+project-doc` —— 安装 skills，并向 agent 文档追加项目片段
- `snippet` —— 向 stdout 打印可复制说明

## 事件日志

如果启用了事件日志，Mutsumi 会把 JSONL 记录追加到平台数据目录。
默认通常是：

```text
~/.local/share/mutsumi/events.jsonl
```

示例记录：

```jsonl
{"timestamp":"2026-03-23T10:00:00+00:00","type":"task_added","task_id":"01JQ...","title":"Write tests"}
{"timestamp":"2026-03-23T10:02:00+00:00","type":"task_toggled","task_id":"01JQ..."}
{"timestamp":"2026-03-23T10:05:00+00:00","type":"priority_changed","task_id":"01JQ..."}
```

## Agent 的安全默认做法

- 优先 `mutsumi.json`
- 简单 CRUD 优先使用 CLI
- 如果直接写 JSON，使用原子替换
- 精确保留未知字段
- 不要静默删除用户任务
- 如果不确定大改后文件是否仍有效，运行 `mutsumi validate`
