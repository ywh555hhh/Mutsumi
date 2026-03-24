# Mutsumi データ契約仕様

| バージョン | 1.0 |
|---|---|
| ステータス | ドラフト |
| 日付 | 2026-03-23 |

> **[English Version](./DATA_CONTRACT.md)** | **[中文版](./DATA_CONTRACT_cn.md)**

---

## 1. 正式なファイル命名

Mutsumi は以下の schema で定義された JSON オブジェクトにタスクを保存します。

### 1.1 推奨ファイル名

- **正式ファイル名:** `mutsumi.json`
- **後方互換のフォールバック:** `tasks.json`

新しいプロジェクトと新しいサンプルでは、常に **`mutsumi.json`** を使用します。
`tasks.json` は古いセットアップとの互換性のためにのみサポートされ続けます。

### 1.2 ファイル解決順序

明示的なパスが渡されていない場合、Mutsumi は次の順序でアクティブなタスクファイルを解決します。

1. CLI `--path`
2. `./mutsumi.json`
3. `./tasks.json`
4. 新規プロジェクトのデフォルトターゲット: `./mutsumi.json`

---

## 2. ルート構造

Mutsumi のデータソースは、`tasks` 配列を含む有効な JSON オブジェクトです。

```json
{
  "$schema": "https://mutsumi.dev/schema/v1.json",
  "version": 1,
  "tasks": [
    { "id": "01JQ...", "title": "Refactor auth", "status": "pending" }
  ]
}
```

### 2.1 ルートフィールド

| フィールド | 型 | 必須 | 説明 |
|---|---|---:|---|
| `$schema` | string | いいえ | エディタ補完用の任意 schema URL |
| `version` | integer | はい | データフォーマットのバージョン。現在は `1` |
| `tasks` | array | はい | タスクオブジェクトの配列 |

### 2.2 未知のルートフィールド

Mutsumi はタスクファイルの読み込みと書き戻し時に、未知のルートレベルフィールドを保持します。

---

## 3. タスクオブジェクト

### 3.1 公式フィールド

| フィールド | 型 | 必須 | デフォルト | 説明 |
|---|---|---:|---|---|
| `id` | string | はい | — | 一意な識別子。UUIDv7 推奨 |
| `title` | string | はい | — | タスクタイトル |
| `status` | string | はい | `"pending"` | `"pending"` または `"done"` |
| `scope` | string | いいえ | `"inbox"` | `"day"`、`"week"`、`"month"`、`"inbox"` |
| `priority` | string | いいえ | `"normal"` | `"high"`、`"normal"`、`"low"` |
| `tags` | string[] | いいえ | `[]` | 自由形式のタグ |
| `children` | Task[] | いいえ | `[]` | ネストされたサブタスク |
| `created_at` | string | いいえ | auto | ISO 8601 タイムスタンプ |
| `due_date` | string | いいえ | — | ISO 8601 日付。例: `"2026-03-25"` |
| `completed_at` | string | いいえ | — | 完了タイムスタンプ |
| `description` | string | いいえ | — | より長い説明やメモ |

### 3.2 未知のタスクフィールド

Mutsumi は次を保証します。

- 未知のタスクフィールドは**保持**される
- TUI 描画は理解できないフィールドを無視する
- agents は自分のワークフロー向けに追加メタデータを加えてよい

例:

```json
{
  "id": "01JQ8X7K3M0000000000000000",
  "title": "Train model v2",
  "status": "pending",
  "scope": "week",
  "priority": "high",
  "tags": ["ml"],
  "estimated_minutes": 120,
  "energy_level": "high-focus",
  "context": "Needs GPU"
}
```

---

## 4. Scope 解決

`scope` は、リストビューやフィルターで使われる計画バケットです。

### 4.1 解決順序

```text
explicit scope > due_date auto-derivation > fallback inbox
```

### 4.2 `due_date` からの自動導出

タスクに `due_date` があり、意味のある明示 scope がない場合、Mutsumi は日付から scope を導出します。

| 条件 | 導出される scope |
|---|---|
| `due_date` が今日 | `day` |
| `due_date` が今日より前 | `day` |
| `due_date` が今週内 | `week` |
| `due_date` が今月後半 | `month` |
| `due_date` が今月を超える | `month` |
| `due_date` 文字列が不正 | `inbox` |

### 4.3 フィルターの意味

| フィルター | 表示内容 |
|---|---|
| Today | effective scope が `day` のタスク |
| Week | effective scope が `week` のタスク |
| Month | effective scope が `month` のタスク |
| Inbox | effective scope が `inbox` のタスク |
| All | scope に関係なくすべてのタスク |

---

## 5. ネスト

### 5.1 構造

サブタスクは `children` フィールドを通じて再帰的にネストされます。

```json
{
  "id": "01JQ8X7K3M...",
  "title": "Refactor user system",
  "status": "pending",
  "children": [
    {
      "id": "01JQ8X7K4N...",
      "title": "Design schema",
      "status": "done",
      "children": []
    },
    {
      "id": "01JQ8X7K5P...",
      "title": "Write migration",
      "status": "pending",
      "children": []
    }
  ]
}
```

### 5.2 親子ルール

- すべての子タスクを完了しても、親タスクは**自動では**完了しない
- TUI は `2/5 done` のような進捗表示を行ってよい
- agents は独自の上位自動化を実装できるが、基本契約は明示的なまま保つ

---

## 6. バリデーションルール

### 6.1 必須フィールドの検証

次のいずれかが欠けているタスクは無効です。

- `id`
- `title`
- `status`

### 6.2 列挙値の検証

サポートされる値:

- `status`: `pending`、`done`
- `priority`: `high`、`normal`、`low`
- `scope`: `day`、`week`、`month`、`inbox`

### 6.3 実行時の挙動

- 不正な JSON はファイルの読み込みを妨げる
- 回復力のある読み込みでは、無効な個別タスクはスキップされる場合がある
- Mutsumi はクラッシュせず、UI とログ出力を通じてバリデーション問題を報告する

---

## 7. 書き込みセマンティクス

タスクファイルを変更する agents やツールは、次のルールに従うべきです。

1. ファイル全体を読む
2. メモリ上で `tasks` 配列を変更する
3. 未知のルートフィールドとタスクフィールドを保持する
4. **ファイル全体**をアトミックに書き戻す
5. 新規書き込みでは `mutsumi.json` を優先する

---

## 8. 完全な例

```json
{
  "$schema": "https://mutsumi.dev/schema/v1.json",
  "version": 1,
  "tasks": [
    {
      "id": "01JQ8X7K3M0000000000000001",
      "title": "Refactor auth module",
      "status": "pending",
      "scope": "day",
      "priority": "high",
      "tags": ["dev", "backend"],
      "created_at": "2026-03-21T08:00:00Z",
      "due_date": "2026-03-21",
      "description": "Replace session-based auth with JWT",
      "children": [
        {
          "id": "01JQ8X7K3M0000000000000002",
          "title": "Install PyJWT",
          "status": "done",
          "priority": "normal",
          "tags": [],
          "completed_at": "2026-03-21T09:30:00Z",
          "children": []
        },
        {
          "id": "01JQ8X7K3M0000000000000003",
          "title": "Write middleware",
          "status": "pending",
          "priority": "normal",
          "tags": [],
          "children": []
        }
      ]
    },
    {
      "id": "01JQ8X7K3M0000000000000004",
      "title": "Buy coffee beans",
      "status": "pending",
      "scope": "inbox",
      "priority": "low",
      "tags": ["life"],
      "children": []
    }
  ]
}
```

---

## 9. 互換性メモ

- `mutsumi.json` と旧 `tasks.json` は**同じ schema** を共有する
- ファイル名移行は schema 移行を意味しない
- 将来のビューには、カレンダーのような時間ベースのビューも含め、別のタスクモデルを導入するのではなく、`due_date` と同じ基本タスクオブジェクトを再利用すべきである
