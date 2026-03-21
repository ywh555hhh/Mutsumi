# Mutsumi へのコントリビュート

> **[English Version](./CONTRIBUTING.md)** | **[中文版](./CONTRIBUTING_cn.md)**

## 1. クイックスタート

```bash
# Clone
git clone https://github.com/<user>/mutsumi.git
cd mutsumi

# Install dependencies
uv sync

# Run
uv run mutsumi

# Run tests
uv run pytest

# Lint
uv run ruff check .

# Type check
uv run mypy mutsumi/
```

## 2. 開発ワークフロー

1. リポジトリを Fork & Clone します
2. フィーチャーブランチを作成します: `git checkout -b feat/my-feature`
3. `CLAUDE.md` の規約に従って変更を行います
4. 新しい機能にはテストを書きます
5. すべてのチェックを実行します: `uv run pytest && uv run ruff check . && uv run mypy mutsumi/`
6. Conventional Commit メッセージでコミットします
7. PR を作成します

## 3. 受け入れる内容

- バグ修正
- 新しいビルトインテーマ
- 新しいキーボードプリセット
- i18n 翻訳
- ドキュメントの改善
- パフォーマンスの改善

## 4. 事前の議論なしに受け入れない内容

- ネットワーク機能（同期、クラウド、テレメトリ）
- 重い依存関係
- コアデータコントラクトへの変更（先に RFC を作成してください）
- コアに組み込む AI/LLM 統合（Mutsumi はエージェント非依存です）

## 5. Layout Gallery

Mutsumi をどのように使っているか、ぜひ見せてください。GitHub Discussions の「Show your layout」でターミナルレイアウトを共有しましょう:

- スクリーンショットを含めてください
- tmux/zellij の設定を共有してください
- ワークフローについて説明してください

優れたレイアウトは README に掲載されます。

## 6. 行動規範

思いやりを持ちましょう。良いコードを書きましょう。「静か」という哲学を尊重しましょう。
