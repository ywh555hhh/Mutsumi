# Mutsumi 开发规则（CLAUDE.md）

> **[English Version](./CLAUDE.md)** | **[日本語版](./CLAUDE_ja.md)**

## 项目概览
Mutsumi 是一个极简 TUI 任务看板，监听 `mutsumi.json`（并以 `tasks.json` 作为向后兼容回退），为多线程开发者提供一个零摩擦的可视化锚点。基于 Python + Textual 构建。

## 架构
- **MVC 分离**：Mutsumi 是 View。AI Agents 是 Controllers。`mutsumi.json` 是规范 Model 文件，`tasks.json` 仍作为 legacy fallback 被接受。
- **布局无关**：Mutsumi **不**负责管理窗口分屏。她是一个独立的终端进程。
- **Agent 无关**：不依赖任何 LLM 或 agent。任何能写 JSON 的程序都是合法 controller。

## 交互原则
- **键盘 + 鼠标完整覆盖**：每个动作都**必须**同时可通过键盘和鼠标点击到达。不能有只支持键盘或只支持鼠标的功能。
- **默认预设是 `arrows`**（不是 vim）：方向键 + Home/End + Shift+arrows。普通人并不懂 vim。vim 和 emacs 是面向高级用户的可选预设。
- **鼠标是一等公民**：按钮可点、标签可点、复选框可点、列表项可点。鼠标用户不应被当作二等公民。

## 技术栈
- Python 3.12+，使用 `uv` 管理
- TUI：Textual
- CLI：click
- 校验：pydantic v2
- 文件监听：watchdog
- 配置：TOML（stdlib `tomllib`）

## 代码约定
- 到处使用类型标注。绝不使用 `Any`。
- Textual widgets 优先组合而不是继承。
- 所有文件 I/O 都通过 `core/` 模块——TUI 组件绝不能直接接触文件系统。
- 原子写入：始终先写临时文件，再用 `os.replace()`（跨平台）。
- 平台路径：使用 `core/paths.py` 帮助函数——不要硬编码 `~/.config` 或 `~/.local/share`。
- 尽可能保持 TUI 组件无状态——状态属于数据层。

## 文件结构
```text
mutsumi/
├── app.py          # Textual App 入口
├── tui/            # TUI 组件（widgets）
├── cli/            # CLI 命令（click）
├── core/           # 数据模型、文件 I/O、校验
├── config/         # 配置加载与默认值
├── i18n/           # 语言文件
└── themes/         # 内置主题文件
```

## 规则
1. **禁止网络调用。** Mutsumi 是 100% 本地产品。没有遥测、没有 API 调用、没有分析上报。
2. **保留未知字段。** 写入 `mutsumi.json` 或 legacy `tasks.json` 时，绝不能删除不认识的字段。
3. **优雅降级。** 如果当前激活的任务文件无效，应显示错误横幅，而不是崩溃。
4. **不要引入重依赖。** 如果一个 pip 包只是解决琐碎问题，就直接内联实现。
5. **提交信息** 使用 conventional commits：`feat:`、`fix:`、`docs:`、`style:`、`refactor:`、`test:`、`chore:`、`i18n:`。
6. **一个文件只关心一件事。** 不要把 CLI 逻辑放进 TUI 文件，反之亦然。
7. **用户数据神圣不可侵犯。** 绝不自动删除任务，绝不修改用户自定义字段，绝不损坏 `mutsumi.json` 或 legacy `tasks.json`。

## 测试
- 单元测试使用 `pytest`
- 充分测试数据模型（pydantic）——它们是契约本身
- TUI 测试使用 Textual 内置测试框架（`app.run_test()`）
- fixture 文件放在 `tests/fixtures/`

## 开发工作流
**大功能无 RFC 不写。** 所有非 trivial 的功能都必须遵循以下流程：

1. **RFC** —— 先写 RFC 文档，设计讨论达成共识
2. **doc + code** —— 同步写代码并更新文档
3. **test + 人工体验测试** —— 自动化测试 + 手动在终端里跑一遍
4. **bug fix** —— 修复测试和体验中发现的问题
5. **doc + push** —— 最终文档更新 + 推送

## 规范与文档
- RFC：`docs/rfc/RFC-001-mutsumi-core.md`
- RFC：`docs/rfc/RFC-007-multi-source-hub.md`
- Data Contract：`docs/specs/DATA_CONTRACT.md`
- Agent Protocol：`docs/specs/AGENT_PROTOCOL.md`
- TUI Spec：`docs/specs/TUI_SPEC.md`
- Roadmap：`docs/ROADMAP.md`
- Brand：`docs/BRAND.md`
