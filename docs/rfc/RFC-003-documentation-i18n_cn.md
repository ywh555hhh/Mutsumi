# RFC-003: 文档国际化策略

| Field       | Value                                    |
|-------------|------------------------------------------|
| **RFC**     | 003                                      |
| **Title**   | 文档国际化策略                             |
| **Status**  | Draft                                    |
| **Author**  | Wayne (ywh)                              |
| **Created** | 2026-03-21                               |

> **[English Version](./RFC-003-documentation-i18n.md)** | **[日本語版](./RFC-003-documentation-i18n_ja.md)**

---

## 1. 摘要

Mutsumi 的所有文档和 TUI 界面文本提供三种语言版本：英文（主版本）、中文和日文。每份文档以独立文件存在 — `FILENAME.md`（英文）、`FILENAME_cn.md`（中文）、`FILENAME_ja.md`（日文）。本 RFC 定义命名规范、维护规则和多语言支持的覆盖范围。

## 2. 动机

Mutsumi 面向三个核心市场：

- **全球市场**：Product Hunt、Hacker News、Reddit /r/commandline — 英文是默认语言
- **中国市场**：V2EX、即刻、微信/QQ 开发者社区 — 中文触达庞大的开发者群体
- **日本市场**：项目名称取自日语（若叶睦），日本开发者社区是天然的受众

在一个文件里混写多语言既嘈杂又难以阅读。独立文件让每个版本保持干净、独立可导航、易于维护。

## 3. 命名规范

所有多语言文档遵循语言后缀模式：

```
FILENAME.md        → English（主版本，无后缀）
FILENAME_cn.md     → 中文版
FILENAME_ja.md     → 日本語版
```

### 3.1 完整文件结构

```
Mutsumi/
├── README.md
├── README_cn.md
├── README_ja.md
├── CONTRIBUTING.md
├── CONTRIBUTING_cn.md
├── CONTRIBUTING_ja.md
├── CLAUDE.md                          ← 仅英文（供 AI Agent 消费）
├── LICENSE                            ← 仅英文（法律标准）
└── docs/
    ├── ROADMAP.md
    ├── ROADMAP_cn.md
    ├── ROADMAP_ja.md
    ├── BRAND.md
    ├── BRAND_cn.md
    ├── BRAND_ja.md
    ├── rfc/
    │   ├── RFC-001-mutsumi-core.md
    │   ├── RFC-001-mutsumi-core_cn.md
    │   ├── RFC-001-mutsumi-core_ja.md
    │   ├── RFC-002-installation-and-onboarding.md
    │   ├── RFC-002-installation-and-onboarding_cn.md
    │   ├── RFC-002-installation-and-onboarding_ja.md
    │   ├── RFC-003-documentation-i18n.md
    │   ├── RFC-003-documentation-i18n_cn.md
    │   └── RFC-003-documentation-i18n_ja.md
    └── specs/
        ├── DATA_CONTRACT.md
        ├── DATA_CONTRACT_cn.md
        ├── DATA_CONTRACT_ja.md
        ├── AGENT_PROTOCOL.md
        ├── AGENT_PROTOCOL_cn.md
        ├── AGENT_PROTOCOL_ja.md
        ├── TUI_SPEC.md
        ├── TUI_SPEC_cn.md
        └── TUI_SPEC_ja.md
```

### 3.2 互链标头

每个文件在元数据表之后包含语言切换链接：

英文文件：
```markdown
> **[中文版](./FILENAME_cn.md)** | **[日本語版](./FILENAME_ja.md)**
```

中文文件：
```markdown
> **[English Version](./FILENAME.md)** | **[日本語版](./FILENAME_ja.md)**
```

日文文件：
```markdown
> **[English Version](./FILENAME.md)** | **[中文版](./FILENAME_cn.md)**
```

## 4. 覆盖范围：哪些文件需要多语言

| 内容 | 需要多语言？ | 原因 |
|---|---|---|
| `docs/rfc/*.md` | 是 | 核心规范，所有受众都需要 |
| `docs/specs/*.md` | 是 | 技术契约 |
| `docs/ROADMAP.md` | 是 | 项目进度跟踪 |
| `docs/BRAND.md` | 是 | 品牌标识 |
| `README.md` | 是 | 项目门面 |
| `CONTRIBUTING.md` | 是 | 社区参与 |
| `CLAUDE.md` | **否**（仅英文） | 供 AI Agent 机器消费 |
| `LICENSE` | **否**（仅英文） | 法律标准 |
| 代码注释 | **否**（仅英文） | 开发标准 |
| Commit 消息 | **否**（仅英文） | Git 约定 |
| TUI 界面文本 | 独立系统 | 运行时 `locales/*.toml` 文件 |

## 5. TUI 国际化 vs 文档国际化

这是两个完全独立的系统：

| 方面 | TUI 国际化 | 文档国际化 |
|---|---|---|
| 位置 | `mutsumi/i18n/locales/` | `_cn.md` / `_ja.md` 后缀文件 |
| 格式 | TOML 语言包文件 | 独立 Markdown 文件 |
| 切换 | 运行时配置 / `$LANG` 环境变量 | 读者自行选择文件 |
| 语言 | `en`、`zh`、`ja`（可扩展） | EN + ZH + JA |
| 维护者 | 代码贡献者 | 文档贡献者 |

## 6. 贡献规则

### 6.1 新增文档

1. 先写英文版本：`FEATURE.md`
2. 创建中文版本：`FEATURE_cn.md`
3. 创建日文版本：`FEATURE_ja.md`（可以先创建框架，标注 "translation wanted"）
4. 在所有文件中都添加互链标头
5. 所有文件保持相同的章节结构（相同的章节、相同的标题层级）

### 6.2 更新现有文档

修改文档时，**应当**同时更新所有语言版本。如果 PR 只更新了一种语言，应在 PR 描述中注明，以便 Reviewer 标记。

### 6.3 翻译质量

- 翻译应当**自然流畅**，不要逐字机械翻译
- 中文版可以使用更口语化的开发者用语（如"跑通"而不是"成功执行运行"）
- 日文版应使用标准的技术日语（文档使用です/ます体）
- 技术术语保留英文：`watchdog`、`TUI`、`JSON`、`pydantic`、`TOML`、`CLI`、`UUID`
- 产品名保留原样：`Mutsumi`、`Product Hunt`、`Textual`、`Claude Code`

### 6.4 结构对等

所有语言文件必须保持相同的章节结构：
- 相同的章节数量
- 相同的标题层级
- 相同的代码块和示例（代码是语言无关的）
- 表格的描述性文字可以不同，但必须覆盖相同的字段

## 7. 支持语言（当前）

Mutsumi 从第一天起支持三种语言：

| 语言 | 文档后缀 | TUI 语言包文件 | 优先级 |
|---|---|---|---|
| English | `.md`（无后缀） | `locales/en.toml` | 主版本（默认） |
| 中文（简体） | `_cn.md` | `locales/zh.toml` | Day 1 |
| 日本語 | `_ja.md` | `locales/ja.toml` | Day 1 |

TUI `config.toml` 的语言字段：
```toml
[general]
language = "auto"   # "auto" | "en" | "zh" | "ja"
```

`"auto"` 从 `$LANG` / `$LC_ALL` 环境变量自动检测：
- `ja_JP.*` → 日文
- `zh_CN.*` / `zh_TW.*` → 中文
- 其他 → 英文

## 8. 未来：更多语言

如果社区对韩语、西班牙语等有需求：

```
FILENAME.md        → English（主版本）
FILENAME_cn.md     → 中文
FILENAME_ja.md     → 日本語
FILENAME_ko.md     → 한국어
FILENAME_es.md     → Español
```

`_xx` 后缀使用 ISO 639-1 语言代码。英文保持为无后缀的主版本。
