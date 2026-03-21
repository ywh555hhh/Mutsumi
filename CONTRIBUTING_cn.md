# 参与贡献 Mutsumi

> **[English Version](./CONTRIBUTING.md)** | **[日本語版](./CONTRIBUTING_ja.md)**

## 1. 快速上手

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

## 2. 开发流程

1. Fork 并 clone 仓库
2. 新建功能分支：`git checkout -b feat/my-feature`
3. 按 `CLAUDE.md` 规范开发
4. 为新功能编写测试
5. 运行全部检查：`uv run pytest && uv run ruff check . && uv run mypy mutsumi/`
6. 使用约定式提交信息
7. 提交 PR

## 3. 我们接受的贡献

- Bug 修复
- 新的内置主题
- 新的键位预设
- 国际化翻译
- 文档改进
- 性能优化

## 4. 需要事先讨论的内容

- 网络功能（同步、云、遥测）
- 重量级依赖
- 对核心数据契约的修改（请先提 RFC）
- 在核心代码中硬编码 AI/LLM 集成（Mutsumi 保持 agent 无关性）

## 5. 布局画廊

我们很想看看你是怎么用 Mutsumi 的。在 GitHub Discussions 的 "Show your layout" 板块分享你的终端布局：

- 附上截图
- 分享你的 tmux/zellij 配置
- 描述你的工作流

精选布局会被收录进 README。

## 6. 行为准则

善待他人。写好代码。尊重 Mutsumi「安静」的产品哲学。
