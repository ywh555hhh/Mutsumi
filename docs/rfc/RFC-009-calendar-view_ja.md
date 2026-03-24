# RFC-009: Calendar View — Multi-Source Tasks のための Time Navigation

> **[English Version](./RFC-009-calendar-view.md)** | **[中文版](./RFC-009-calendar-view_cn.md)**

| Field | Value |
|---|---|
| **RFC** | 009 |
| **Title** | Calendar View — Time Navigation for Multi-Source Tasks |
| **Status** | Draft |
| **Author** | Wayne (ywh) |
| **Created** | 2026-03-23 |

---

## 1. Abstract

Mutsumi には、calendar を成立させるための生の意味論がすでに揃っています。

- task の `due_date`
- 日付から導出される effective scope
- 複数 source を集約する Main dashboard
- focused editing のための source tabs
- drill-down のための detail panel

足りていないのは、**time view そのもの**です。

本 RFC は、built-in の **calendar view** を一級の product capability として Mutsumi に追加することを提案します。calendar は second task system や separate data model を導入してはなりません。代わりに、既存の task model を日付ベースで navigate する新しい方法を提供するべきです。

calendar は **Main/dashboard layer** に自然に属します。つまり、既存の list-oriented な source tabs を補完する、cross-source で time-oriented な view です。

長期目標は、task planning と review のための full-featured な calendar experience です。ただし実装は phased rollout で進めるべきです。

---

## 2. Motivation

### 2.1 The current gap

Mutsumi はすでに、次のような問いに答えられます。

- 今日 due なものは何か？
- 今週に属するものは何か？
- 今月に属するものは何か？

しかし、それを **list buckets** で答えており、本当の time map ではありません。

そのため、ユーザーは `Today`、`Week`、`Month` で task を filter できても、なお次のことができません。

- 日付ごとの分布を glance する
- sparse な日と crowded な日を見分ける
- 特定の日付からその task 群へ jump する
- scheduling pressure を視覚的に理解する

### 2.2 Why this matters for a todo product

calendar を持たない todo system は、list row にある締切をユーザーの頭の中で時間へ射影させます。

それは tiny list なら問題ありません。しかし、次のものを同時に抱えていると悪化します。

- personal tasks
- 1 つ以上の active projects
- agent-written な backlog churn
- 次の数日〜数週間にまたがる due dates

Mutsumi の target user —— すでに multiple threads の中で生きている人 —— にとって足りないのは、task metadata を増やすことではありません。必要なのは **より良い temporal surface** です。

### 2.3 Why Main/dashboard is the right home

現在の architecture はすでに、次を区別しています。

- **Main** — cross-source summary
- **source tabs** — focused editing と inspection

calendar は本質的に **cross-source time navigator** です。したがって、source-local task list を置き換えるよりも、Main layer に置くほうが自然です。

---

## 3. Goals

| Goal | Description |
|---|---|
| Multi-source time view | personal + project sources の dated tasks を 1 つの calendar surface に表示する |
| No new task model | 既存の `Task`、`due_date`、`scope`、source semantics を再利用する |
| Keyboard + mouse parity | date navigation と drill-down は両 input mode から動作しなければならない |
| Smooth drill-down | ユーザーが date → tasks → detail/source tab を混乱なく移動できる |
| Keep list views relevant | calendar は既存の list views を補完し、置き換えない |
| Future-ready full target | 実装が phased でも、month/week/day/agenda を見据えて設計する |

---

## 4. Non-goals

本 RFC は次を**提案しません**。

- network calendar sync
- Google Calendar / iCal integration
- calendar 専用の別 JSON file
- Mutsumi を meeting / event scheduler に変えること
- 現在の list-based source tabs を捨てること
- calendar support の first release のために core task schema を変更すること

---

## 5. Data Semantics

### 5.1 Calendar anchor

calendar は **`due_date`** を primary time anchor として使います。

task に `due_date` がない場合、その task は exact calendar placement を持たないため、デフォルトでは dated cell に表示されるべきではありません。

### 5.2 Relationship to `scope`

`scope` は planning bucket のままであり、canonical な calendar coordinate ではありません。

resolution rules は変わりません。

```text
explicit scope > due_date auto-derivation > inbox
```

その意味は次の通りです。

- list views は引き続き effective scope を使う
- calendar views は `due_date` があるとき `due_date` を使う
- calendar は missing date の代わりとして `scope` を再解釈しない

### 5.3 Tasks without `due_date`

`due_date` のない task は：

- list views と dashboard summaries には引き続き表示される
- デフォルトでは date grid に現れない
- 後続フェーズでは補助的な “undated” agenda/sidebar に表示できる

### 5.4 Invalid dates

`due_date` が malformed な場合：

- calendar view は crash してはならない
- その task は日付配置から除外されるべき
- 既存の graceful-degradation path が引き続き authoritative である

### 5.5 Overdue tasks

overdue task は元の `due_date` に anchored されたままですが、calendar はそれが overdue であることを明確に示すべきです。

例：

- accent color
- overdue badge
- month view での特別な density marker

### 5.6 Recurring tasks

Mutsumi は writer layer ですでに recurrence metadata をサポートしています。calendar は recurrence を task-generation/update concern として扱うべきであり、second rendering model として扱うべきではありません。

つまり：

- calendar は current task state を読む
- recurrence rules を独立に展開して phantom events を作らない
- 将来はその上に高度な recurrence visualization を重ねられる

### 5.7 Multi-source semantics

calendar entries は source identity を保持しなければなりません。

calendar 上に描画されるすべての task は、引き続き次を知っているべきです。

- どの source から来たか
- personal か project-owned か
- どの source tab / detail view に戻るべきか

---

## 6. Information Architecture

### 6.1 Placement

calendar は source tabs の置き換えではなく、**Main-layer view mode** として導入されるべきです。

推奨構造：

```text
[★ Main] [Personal] [project-a] [project-b]
          └─ Main view modes: Dashboard / Calendar
```

あり得る UI 形態：

- Main 内の segmented control
- Main が active のときの keyboard toggle
- Main に focus があるときの footer action / header action

### 6.2 Why not a top-level tab

独立した top-level `Calendar` tab も可能ですが、Main という mental model を 2 つの competing aggregation surfaces に分裂させるため、弱い案です。

Main は引き続き cross-source layer として、次を含むべきです。

- summary/dashboard view
- time/calendar view

### 6.3 Relationship to source tabs

source tabs は、direct task CRUD と source-scoped filtering の場であり続けます。

calendar は navigation / planning surface として次へ jump します。

- source tab
- detail panel
- 将来的には inline quick-create/edit flows

---

## 7. Interaction Model

### 7.1 Core interactions

calendar は次をサポートしなければなりません。

1. 日付間を移動する
2. 特定日の task を inspect する
3. task detail を開く
4. source context へ jump する
5. calendar granularity / mode を切り替える

### 7.2 Keyboard requirements

必要な keyboard support の例：

| Action | Keyboard expectation |
|---|---|
| 日単位で移動 | arrow keys または preset に対応する等価 navigation |
| 週単位で移動 | up/down または week-jump keys |
| 選択日を開く | `Enter` |
| calendar mode を切り替える | dedicated shortcut または focusable toggle |
| list/dashboard に戻る | `Escape` または explicit back action |
| source tab へ jump | 選択 task に対する `Enter` / secondary action |

正確な key は active preset philosophy に従うべきです。

- `arrows` が引き続き default
- `vim` と `emacs` は opt-in

### 7.3 Mouse requirements

必要な mouse support の例：

| Action | Mouse expectation |
|---|---|
| 日付を選ぶ | date cell を click |
| 日付内容を開く | date cell または task chip を click |
| task detail を開く | task chip を click |
| mode を切り替える | segmented control / tab を click |
| source へ jump | source badge または action を click |

### 7.4 Triple input parity

calendar は RFC-004 の原則を守らなければなりません。

1 つの surface で到達できる calendar action なら、そこで閉じ込められてはなりません。

例：

- 日付選択が mouse-only になってはならない
- calendar mode 切り替えが keyboard-only になってはならない
- source drill-down は意味がある範囲でのみ CLI-adjacent な解釈を持てばよいが、interactive navigation 自体は TUI-specific である

---

## 8. View Modes (Full Target)

product goal は phased rollout であっても full-featured な calendar system です。

### 8.1 Month view

向いている用途：

- density scanning
- 週をまたいだ spread の把握
- overloaded days の発見

期待される挙動：

- 日付グリッド
- 各 cell の task summary または density indicator
- crowded day に対する overflow handling

### 8.2 Week view

向いている用途：

- operational planning
- 次の 7 日間をより密に見ること
- source をまたいだ near-term commitments の比較

### 8.3 Day view

向いている用途：

- focused execution
- 1 日分の item をより豊かな detail で見ること

### 8.4 Agenda view

向いている用途：

- dated tasks を chronological に読むこと
- low-density terminal setup
- accessibility / narrow terminal fallback

---

## 9. Feature Matrix (Product Target)

| Capability | Target state |
|---|---|
| Month / week / day / agenda | Supported |
| Multi-source aggregation | Supported |
| Source badges | Supported |
| Date drill-down | Supported |
| Detail panel integration | Supported |
| Quick create on date | Supported |
| Quick edit from date | Supported |
| Drag to reschedule | Supported later |
| Overdue visualization | Supported |
| Undated task companion view | Supported later |
| Recurrence-aware rendering | Supported incrementally |

---

## 10. Phased Rollout

calendar は full product capability として設計しつつ、実装は phase ごとに進めるべきです。

### Phase A — Read-only calendar foundation

Scope:

- Main-layer calendar mode
- Month view と/または agenda fallback
- multi-source aggregation
- 日付選択 → task inspection
- task chip → detail panel を開く
- 選択 task から source へ jump

これが証明すること：

- data semantics が sound である
- calendar が Main に自然に属する
- CRUD flow を書き換えなくても即時価値が出る

### Phase B — Lightweight task actions

Scope:

- 選択日付へ直接 task を作成する
- calendar context から task の due date を編集する
- calendar detail path から quick に priority/tag を変更する
- より良い week/day navigation

これが加えるもの：

- calendar が observational ではなく operational になる

### Phase C — Full interaction layer

Scope:

- drag または keyboard による move-to-date
- より密な day/week rendering
- より良い overflow handling
- recurring-task cues
- optional な undated companion lane / agenda enhancement

これが完成させるもの：

- calendar が first-class な planning / maintenance surface になる

---

## 11. Alternatives Considered

### 11.1 Separate top-level Calendar tab

**Rejected for now.**

理由：

- Main-layer aggregation concept を重複させる
- cross-source overview としての “Main” と “Calendar” の間に曖昧さを作る

### 11.2 Replace scope filters with calendar

**Rejected.**

理由：

- source-local list filters は依然として fast textual workflow に有効
- ユーザーには list buckets と time navigation の両方が必要

### 11.3 Add a separate calendar data model

**Rejected.**

理由：

- elegant な single-source-of-truth model を壊す
- `due_date` にすでにある意味論を重複させる
- migration と consistency の risk を不必要に増やす

---

## 12. Implementation Sketch

この section は厳密な code structure を固定しませんが、自然な anchor はすでに codebase に見えています。

### 12.1 Existing foundations to reuse

| Area | Existing responsibility | Calendar relevance |
|---|---|---|
| `mutsumi/core/loader.py` | file resolution、loading、scope derivation | `due_date` semantics と filtering helpers を再利用 |
| `mutsumi/core/sources.py` | multi-source registry | aggregation source map を再利用 |
| `mutsumi/app.py` | source-tab orchestration | Main/dashboard/calendar mode switching のホスト |
| `mutsumi/tui/main_dashboard.py` | Main aggregated surface | calendar UI の sibling または extension point になり得る |
| `mutsumi/tui/scope_filter.py` | source-local filters | secondary navigation patterns の参考 |
| `mutsumi/tui/detail_panel.py` | task drill-down | calendar からの task inspection endpoint として再利用 |

### 12.2 Likely UI shape

あり得る path：

- `MainDashboard` を summary surface として維持する
- calendar surface のための新 widget を追加する
- `app.py` に Main の dashboard mode / calendar mode 切り替えを持たせる
- source tabs と detail panel interactions を保つ

### 12.3 Data transformation layer

calendar rendering には、次を写像する軽い projection layer が必要になります。

```text
(source_name, task) → date bucket → rendered cell/task summary
```

これは schema change ではなく、view transformation です。

---

## 13. Testing Strategy

### 13.1 Data semantics tests

- valid な `due_date` を持つ task が正しい日付に載る
- invalid な `due_date` を持つ task が安全に degrade する
- overdue task が正しくマークされる
- `due_date` のない task が dated cell に現れない
- multi-source aggregation が source identity を保持する

### 13.2 TUI behavior tests

- keyboard-only の calendar navigation が動作する
- mouse-only の date selection が動作する
- Main dashboard と calendar の切り替えが動作する
- calendar task の選択で detail が正しく開く
- source drill-down が正しい tab に到達する

### 13.3 Manual beta scenarios

- personal + 複数 project sources に日付付き task がある
- crowded な week と sparse な week がある
- overdue、due-today、future、undated tasks が混在する
- narrow terminal fallback behavior

---

## 14. Open Questions

1. 最初に shipped する版は **month view**、**agenda view**、それとも両方を先頭に置くべきか？
2. undated tasks は最初から calendar の横に出すべきか、それとも deferred にするべきか？
3. 最初の interactive release ではどこまで inline editing を含めるべきか？ それとも edit は detail panel / task form に留めるべきか？
4. terminal UI の dense な month cell に対する最良の overflow model は何か？
5. calendar mode は Main の segmented control、hotkey、あるいは両方に置くべきか？

---

## 15. Conclusion

Mutsumi はすでに時間を semantic には理解していますが、まだ visual には理解していません。

built-in calendar は自然な次の一歩です。なぜなら、それは：

- 既存の `due_date` semantics を再利用し
- Main-layer の command-center vision を強化し
- multi-threaded user に scheduling pressure をより見やすくし
- list views を置き換えずに補完する

したがって、正しい方向は次です。

- **one task model**
- **one source architecture**
- **multiple view surfaces**

List view が答えるのは “what is here?”。
Calendar view が答えるのは “when does it land?”。

Mutsumi には両方あるべきです。
