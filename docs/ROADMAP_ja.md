# Mutsumi 開発ロードマップ

> **[English Version](./ROADMAP.md)** | **[中文版](./ROADMAP_cn.md)**

| ステータス | リビングドキュメント |
|-----------|---------------------|
| 日付       | 2026-03-21          |

---

## フェーズ概要

```
Phase 0          Phase 1          Phase 2          Phase 3          Phase 4
Foundations      Skeleton         Reactivity       CLI & Polish      Launch
────────────     ────────────     ────────────     ────────────     ────────────
docs & specs     static TUI       hot-reload       CLI CRUD         README
project setup    tab switching    file watcher     i18n             GIF demo
data model       task list        click → JSON     themes           Product Hunt
                 detail panel     JSON → re-draw   config system    community
```

---

## Phase 0: 基盤構築 ✅

**目標**: すべての設計ドキュメントを完成させ、プロジェクトの骨格を構築します。コーディングは行いません。

- [x] ビジョンドキュメント
- [x] RFC-001: コアアーキテクチャ
- [x] データコントラクト仕様 (`DATA_CONTRACT.md`)
- [x] エージェント統合プロトコル (`AGENT_PROTOCOL.md`)
- [x] TUI 仕様書 (`TUI_SPEC.md`)
- [x] ブランドアイデンティティ (`BRAND.md`)
- [x] ロードマップ（本ドキュメント）
- [x] `uv init` によるプロジェクト骨格の作成
- [x] `pyproject.toml` の依存関係宣言
- [x] サンプル `tasks.json`（フィクスチャ）
- [x] `CLAUDE.md` プロジェクトレベルの開発規約
- [x] CI: GitHub Actions（lint + 型チェック）

**完了条件**: `uv run mutsumi` で空の Textual ウィンドウが起動し、正常に終了できること。

---

## Phase 1: スケルトン ✅

**目標**: `tasks.json` を読み込んでタスクを表示する静的な TUI をレンダリングします。外部からの変更には反応しません。

- [x] Textual App 基盤フレームワーク (`app.py`)
- [x] ヘッダーウィジェット: タブ切り替え（Today / Week / Month / Inbox）
- [x] TaskList ウィジェット: 優先度別グループ表示
- [x] TaskRow ウィジェット: チェックボックス + タイトル + タグ + 優先度スター
- [x] フッターウィジェット: タスク統計情報
- [x] データ層: Task スキーマの pydantic モデル
- [x] データ層: `tasks.json` のパース
- [x] 基本キーボードナビゲーション: `j/k` 上下移動, `q` 終了
- [x] サブタスクのレンダリング: インデントされた子要素（最大3階層）
- [x] 空状態のプレースホルダーページ

**完了条件**: 手動で `tasks.json` を作成し、`uv run mutsumi` ですべてのタスクが正しくレンダリングされること。

---

## Phase 2: リアクティビティ ✅

**目標**: 双方向データフローを実装します。外部の JSON 変更が TUI の再レンダリングをトリガーし、TUI での操作が JSON に書き戻されます。

- [x] watchdog 統合: `tasks.json` の変更を監視
- [x] デバウンス機構（100ms）
- [x] ホットリロード: JSON の変更 → ちらつきのない TUI 再レンダリング
- [x] マウスクリックによるチェックボックス → ステータスの切り替え → JSON への書き戻し
- [x] アトミック書き込み（一時ファイル + `os.rename`）
- [x] スキーマバリデーション: 不正な JSON → エラーバナー表示
- [x] エラー状態: ファイルの欠落や不正形式に対するグレースフルデグラデーション
- [x] 詳細パネル: `Enter` でタスク詳細を展開
- [x] エンドツーエンドシナリオ: エージェントが別のターミナルで JSON を書き込む → TUI が自動更新

**完了条件**: 10秒の GIF を録画します。左側で Mutsumi を実行、右側で JSON を編集し、左側が即座に更新されること。

---

## Phase 3: CLI とポリッシュ（現在）

**目標**: CLI サブコマンド、CRUD インタラクション、設定システムを充実させます。

- [ ] TUI CRUD: `n` 新規 / `e` 編集 / `dd` 削除
- [ ] CLI: `mutsumi add` / `list` / `done` / `rm` / `edit`
- [ ] CLI: `mutsumi init` — テンプレート `tasks.json` の生成
- [ ] CLI: `mutsumi validate` — ファイルの検証
- [ ] CLI: `mutsumi schema` — JSON Schema の出力
- [ ] 設定システム: `~/.config/mutsumi/config.toml`
- [ ] テーマシステム: 4つのビルトインテーマ + カスタムテーマ読み込み
- [ ] キーバインド: vim / emacs / arrow のプリセット
- [ ] i18n: `en` + `zh` の二言語対応
- [ ] 検索: `/` でリアルタイム検索フィルターを起動
- [ ] イベントログ: TUI 操作 → `events.jsonl` に追記
- [ ] マルチプロジェクト: `--watch` で複数パスを集約
- [ ] `mutsumi --version` / `--help`

**完了条件**: `uv tool install mutsumi` の後、新規ユーザーが2分以内に一連のワークフローを完了できること。

---

## Phase 4: ローンチ

**目標**: すべてのリリース素材を磨き上げ、Product Hunt でのローンチに向けてスプリントします。

- [ ] README.md: 魅力的なプロダクト紹介
- [ ] README「Pro Workflow」セクション（Typeless 音声ワークフロー）
- [ ] README「Layout Gallery」セクション（レイアウトスクリーンショット）
- [ ] ヒーロー GIF の録画: Claude Code + Mutsumi のスプリットスクリーンコラボレーション
- [ ] ボーナス GIF の録画: Typeless 音声 → エージェント → Mutsumi の更新
- [ ] Product Hunt ページのコピー
- [ ] PyPI への公開
- [ ] GitHub Release v0.1.0
- [ ] Hacker News / Reddit /r/commandline への投稿
- [ ] V2EX への投稿
- [ ] コミュニティテンプレートコレクション: ユーザーが自分の tmux/zellij レイアウトを共有

**完了条件**: Product Hunt ページが公開され、GitHub に最初のスターが付くこと。

---

## 将来の構想（ローンチ後のアイデア）

以下の機能は MVP のスコープ外です。参考としてここに記載します。

| 機能                 | 説明                                                     | 優先度   |
|----------------------|----------------------------------------------------------|----------|
| プラグインシステム    | ユーザーがカスタムビューウィジェットを作成可能             | P2       |
| タスクテンプレート    | デイリースタンドアップ / 週報テンプレート                  | P2       |
| アーカイブ           | 完了タスクを `archive.json` に自動アーカイブ              | P2       |
| ポモドーロタイマー    | タスクに連動するビルトインポモドーロタイマー               | P3       |
| Git 同期             | `tasks.json` の自動 Git コミット                          | P3       |
| カレンダービュー      | `due_date` を持つタスクのカレンダー表示                   | P3       |
| ダッシュボードウィジェット | 完了率チャート、日次トレンド                          | P3       |
| Web コンパニオン      | 読み取り専用 Web UI（閲覧のみ、操作不可）                 | P3       |
| Taskwarrior インポート | Taskwarrior からの既存タスクのインポート                  | P3       |
| Markdown タスク       | 代替データソースとしての `tasks.md` サポート              | P3       |

---

## バージョニング戦略

| バージョン | マイルストーン                                     |
|-----------|---------------------------------------------------|
| 0.1.0     | Phase 1 完了 — 静的レンダリングが利用可能          |
| 0.2.0     | Phase 2 完了 — ホットリロード + インタラクション    |
| 0.3.0     | Phase 3 完了 — CLI + 設定が完成                    |
| 0.5.0     | Phase 4 完了 — Product Hunt ローンチビルド          |
| 1.0.0     | コミュニティのフィードバックを経た安定リリース      |
