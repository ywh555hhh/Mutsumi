# Mutsumi データ契約仕様

| バージョン | 0.1.0              |
|-----------|---------------------|
| ステータス | ドラフト             |
| 日付       | 2026-03-21          |

> **[English Version](./DATA_CONTRACT.md)** | **[中文版](./DATA_CONTRACT_cn.md)**

---

## 1. ファイル構造

Mutsumi のデータソースは、タスクの配列を含む有効な JSON ファイルです。

```json
{
  "$schema": "https://mutsumi.dev/schema/v1.json",
  "version": 1,
  "tasks": [
    { ... },
    { ... }
  ]
}
```

### 1.1 ルートフィールド

| フィールド   | 型       | 必須   | 説明                                              |
|-------------|----------|--------|--------------------------------------------------|
| `$schema`   | string   | いいえ  | JSON Schema URL（任意、エディタ補完用）              |
| `version`   | integer  | はい    | データフォーマットバージョン、現在は `1`               |
| `tasks`     | array    | はい    | タスクオブジェクトの配列                              |

## 2. タスクオブジェクト

### 2.1 基本フィールド（公式）

| フィールド      | 型         | 必須     | デフォルト   | 説明                                        |
|----------------|------------|----------|-------------|---------------------------------------------|
| `id`           | string     | **はい** | —           | UUIDv7 形式、例: `"01JQ8X7K3M..."`           |
| `title`        | string     | **はい** | —           | タスクタイトル、120文字以内を推奨              |
| `status`       | string     | **はい** | `"pending"` | 列挙型: `"pending"`, `"done"`                |
| `scope`        | string     | いいえ   | `"inbox"`   | 列挙型: `"day"`, `"week"`, `"month"`, `"inbox"` |
| `priority`     | string     | いいえ   | `"normal"`  | 列挙型: `"high"`, `"normal"`, `"low"`        |
| `tags`         | string[]   | いいえ   | `[]`        | カスタムタグ配列                              |
| `children`     | Task[]     | いいえ   | `[]`        | サブタスク配列（再帰的なネスト）               |
| `created_at`   | string     | いいえ   | auto        | ISO 8601 タイムスタンプ                       |
| `due_date`     | string     | いいえ   | —           | ISO 8601 日付（例: `"2026-03-25"`）           |
| `completed_at` | string     | いいえ   | —           | 完了時刻、status が done になると自動設定       |
| `description`  | string     | いいえ   | —           | 詳細な説明（Markdown）                        |

### 2.2 カスタムフィールド（ユーザー定義）

Mutsumi は以下を**保証**します:
- 上記テーブルに含まれないフィールドは**保持**されます — 削除も変更もされません
- TUI の描画ではカスタムフィールドは無視されます
- Agent は独自のロジックのためにカスタムフィールドを自由に追加できます

例 — ユーザー定義のカスタムフィールド:

```json
{
  "id": "01JQ8X7K3M0000000000000000",
  "title": "训练模型 v2",
  "status": "pending",
  "scope": "week",
  "priority": "high",
  "tags": ["ml"],
  "estimated_minutes": 120,
  "energy_level": "high-focus",
  "pomodoro_count": 0,
  "context": "需要 GPU 机器"
}
```

上記の `estimated_minutes`、`energy_level`、`pomodoro_count`、`context` はすべてユーザー定義のカスタムフィールドです。Mutsumi はこれらに一切干渉しません。

## 3. ID 仕様

### 3.1 UUIDv7

デフォルトでは UUIDv7（RFC 9562）を使用します。

```
01JQ8X7K3M0000000000000000
├──────────┤├──────────────┤
  Time part     Random part
  (ms precision)
```

特性:
- 作成時刻で自然にソートされます
- グローバルに一意であり、中央管理が不要です
- Agent と TUI の両方が独立して生成できます
- コンパクトな26文字の Crockford Base32 エンコーディングです

### 3.2 代替フォーマット（設定可能）

ユーザーは `config.toml` で異なる ID フォーマットを設定できます。

| フォーマット      | 例                                    | 用途                 |
|-----------------|--------------------------------------|----------------------|
| `uuidv7`        | `01JQ8X7K3M0000000000000000`         | デフォルト、推奨       |
| `ulid`          | `01ARZ3NDEKTSV4RRFFQ69G5FAV`        | ULID 愛好家向け       |
| `auto-increment`| `1`, `2`, `3`                        | ミニマリスト向け       |

## 4. スコープの解決

### 4.1 優先順位

```
Manual scope > due_date auto-derivation > fallback "inbox"
```

### 4.2 自動導出ルール

タスクに `due_date` があるが手動の `scope` がない場合:

| 条件                              | 導出されるスコープ    |
|-----------------------------------|--------------------|
| `due_date` == 今日                 | `day`              |
| `due_date` が今週以内              | `week`             |
| `due_date` が今月以内              | `month`            |
| `due_date` が過去（期限超過）       | `day`（エスカレート） |
| `due_date` が今月以降              | `month`            |

### 4.3 スコープタブのセマンティクス

| タブ      | 表示内容                                            |
|---------|------------------------------------------------------|
| Today   | `scope == "day"` または（今日と自動導出された場合）      |
| Week    | `scope == "week"` または（今週と自動導出された場合）     |
| Month   | `scope == "month"` または（今月と自動導出された場合）    |
| Inbox   | `scope == "inbox"` または（scope なし + due_date なし） |

## 5. ネスト

### 5.1 構造

サブタスクは `children` 配列を通じて再帰的にネストされます。

```json
{
  "id": "01JQ8X7K3M...",
  "title": "重构用户系统",
  "status": "pending",
  "children": [
    {
      "id": "01JQ8X7K4N...",
      "title": "设计新的数据库 schema",
      "status": "done",
      "children": []
    },
    {
      "id": "01JQ8X7K5P...",
      "title": "实现 migration 脚本",
      "status": "pending",
      "children": [
        {
          "id": "01JQ8X7K6Q...",
          "title": "备份现有数据",
          "status": "pending",
          "children": []
        }
      ]
    }
  ]
}
```

### 5.2 描画ルール

| ネスト深度      | デフォルト動作                                           | 設定可能 |
|---------------|---------------------------------------------------------------|----------|
| 1-3 階層      | インデント付きで完全に描画されます                             | —        |
| 4 階層以上     | 「3 subtasks...」と折りたたまれ、クリックで展開できます          | はい      |
| 無制限         | データ層では制限なし、描画層で設定可能な上限があります            | はい      |

### 5.3 親子ステータスルール

- すべての子タスクが `done` になっても、親は**自動的には** done にマークされません（ユーザーが明示的に制御します）。
- TUI は `2/5 done` のような進捗インジケーターを表示できます。
- Agent は独自の自動完了ロジックを実装できます。

## 6. 完全な例

```json
{
  "$schema": "https://mutsumi.dev/schema/v1.json",
  "version": 1,
  "tasks": [
    {
      "id": "01JQ8X7K3M0000000000000001",
      "title": "重构 Auth 模块",
      "status": "pending",
      "scope": "day",
      "priority": "high",
      "tags": ["dev", "backend"],
      "created_at": "2026-03-21T08:00:00Z",
      "due_date": "2026-03-21",
      "description": "把 session-based auth 改成 JWT",
      "children": [
        {
          "id": "01JQ8X7K3M0000000000000002",
          "title": "安装 PyJWT",
          "status": "done",
          "priority": "normal",
          "tags": [],
          "completed_at": "2026-03-21T09:30:00Z",
          "children": []
        },
        {
          "id": "01JQ8X7K3M0000000000000003",
          "title": "写 middleware",
          "status": "pending",
          "priority": "normal",
          "tags": [],
          "children": []
        }
      ]
    },
    {
      "id": "01JQ8X7K3M0000000000000004",
      "title": "买咖啡豆",
      "status": "pending",
      "scope": "inbox",
      "priority": "low",
      "tags": ["life"],
      "children": []
    }
  ]
}
```

## 7. スキーマ検証ルール

### 7.1 厳密度レベル

| レベル    | 動作                                                          | 用途                |
|----------|--------------------------------------------------------------|---------------------|
| `strict` | 無効なフィールドや値をすべて拒否します                            | CI/CD バリデーション  |
| `normal` | 無効なタスクをスキップし、有効なもののみ描画します（デフォルト）      | TUI の日常使用       |
| `loose`  | ベストエフォートで描画し、不明なフィールドを暗黙的に無視します       | ラピッドプロトタイピング |

### 7.2 必須フィールドの検証

- `id` — 空でない文字列
- `title` — 空でない文字列
- `status` — `"pending"` または `"done"` でなければなりません

上記のフィールドのいずれかが欠けているタスクは**無効**とみなされ、厳密度レベルに応じて処理されます。

### 7.3 エラー報告

検証エラーは stderr に出力され、`~/.local/share/mutsumi/error.log` に記録されます。

```
[2026-03-21T10:00:00Z] WARN: Task at index 3 missing required field "id", skipped
[2026-03-21T10:00:00Z] WARN: Task "01JQ..." has unknown status "wip", rendered with warning badge
```
