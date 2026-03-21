# Contributing to Mutsumi

> **[中文版](./CONTRIBUTING_cn.md)** | **[日本語版](./CONTRIBUTING_ja.md)**

## 1. Quick Start

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

## 2. Development Workflow

1. Fork & clone the repo
2. Create a feature branch: `git checkout -b feat/my-feature`
3. Make changes following the conventions in `CLAUDE.md`
4. Write tests for new functionality
5. Run all checks: `uv run pytest && uv run ruff check . && uv run mypy mutsumi/`
6. Commit with conventional commit message
7. Open a PR

## 3. What We Accept

- Bug fixes
- New built-in themes
- New keyboard presets
- i18n translations
- Documentation improvements
- Performance improvements

## 4. What We Don't Accept (without prior discussion)

- Network features (sync, cloud, telemetry)
- Heavy dependencies
- Changes to the core data contract (open an RFC first)
- AI/LLM integrations baked into core (Mutsumi is agent-agnostic)

## 5. Layout Gallery

We love seeing how you use Mutsumi. Share your terminal layout in GitHub Discussions under "Show your layout":

- Include a screenshot
- Share your tmux/zellij config
- Describe your workflow

The best layouts get featured in the README.

## 6. Code of Conduct

Be kind. Write good code. Respect the "quiet" philosophy.
