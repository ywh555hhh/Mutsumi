# RFC-003: Documentation i18n Strategy

| Field       | Value                                    |
|-------------|------------------------------------------|
| **RFC**     | 003                                      |
| **Title**   | Documentation i18n Strategy              |
| **Status**  | Draft                                    |
| **Author**  | Wayne (ywh)                              |
| **Created** | 2026-03-21                               |

---

## 1. Abstract

Mutsumi ships documentation and TUI text in three languages: English (primary), Chinese, and Japanese. Each document exists as separate files per language — `FILENAME.md` (English), `FILENAME_cn.md` (Chinese), `FILENAME_ja.md` (Japanese). This RFC defines the naming convention, maintenance rules, and scope of multilingual support.

## 2. Motivation

Mutsumi targets three primary markets:

- **Global**: Product Hunt, Hacker News, Reddit /r/commandline — English is the default
- **China**: V2EX, JiKe, WeChat/QQ developer communities — Chinese reaches a massive dev audience
- **Japan**: Given the project's Japanese naming (若叶睦), Japanese developer communities are a natural audience

Inline multilingual (mixing languages in one file) is noisy and hard to read. Separate files keep each version clean, independently navigable, and easy to maintain.

## 3. Naming Convention

Every localized document follows a language suffix pattern:

```
FILENAME.md        → English (primary, un-suffixed)
FILENAME_cn.md     → Chinese (中文)
FILENAME_ja.md     → Japanese (日本語)
```

### 3.1 Full File Map

```
Mutsumi/
├── README.md
├── README_cn.md
├── README_ja.md
├── CONTRIBUTING.md
├── CONTRIBUTING_cn.md
├── CONTRIBUTING_ja.md
├── CLAUDE.md                          ← English only (machine-consumed)
├── LICENSE                            ← English only (legal standard)
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

### 3.2 Cross-reference Header

Each file includes a language switcher at the top, right after the metadata table:

English file:
```markdown
> **[中文版](./FILENAME_cn.md)** | **[日本語版](./FILENAME_ja.md)**
```

Chinese file:
```markdown
> **[English Version](./FILENAME.md)** | **[日本語版](./FILENAME_ja.md)**
```

Japanese file:
```markdown
> **[English Version](./FILENAME.md)** | **[中文版](./FILENAME_cn.md)**
```

## 4. Scope: What Is / Is Not Bilingual

| Content | Bilingual? | Reason |
|---|---|---|
| `docs/rfc/*.md` | Yes | Core specs, both audiences |
| `docs/specs/*.md` | Yes | Technical contracts |
| `docs/ROADMAP.md` | Yes | Project tracking |
| `docs/BRAND.md` | Yes | Brand identity |
| `README.md` | Yes | The face of the project |
| `CONTRIBUTING.md` | Yes | Community participation |
| `CLAUDE.md` | **No** (EN only) | Machine-consumed by AI agents |
| `LICENSE` | **No** (EN only) | Legal standard |
| Code comments | **No** (EN only) | Dev standard |
| Commit messages | **No** (EN only) | Git convention |
| TUI interface text | Separate system | Runtime `locales/*.toml` files |

## 5. TUI i18n vs Doc i18n

These are two completely independent systems:

| Aspect | TUI i18n | Doc i18n |
|---|---|---|
| Location | `mutsumi/i18n/locales/` | `_cn.md` / `_ja.md` suffix files |
| Format | TOML locale files | Separate Markdown files |
| Switching | Runtime config / `$LANG` env var | Reader picks the file |
| Languages | `en`, `zh`, `ja` (extensible) | EN + ZH + JA |
| Maintainer | Code contributors | Doc contributors |

## 6. Contribution Rules

### 6.1 Adding New Documentation

1. Write the English version first: `FEATURE.md`
2. Create the Chinese version: `FEATURE_cn.md`
3. Create the Japanese version: `FEATURE_ja.md` (can be a stub initially with a "translation wanted" note)
4. Add the cross-reference header to all files
5. All files share the same structure (same sections, same heading numbers)

### 6.2 Updating Existing Documentation

When modifying a document, you **should** update both language versions. PRs that update only one language should note this in the PR description so reviewers can flag it.

### 6.3 Translation Quality

- Translations should be **natural**, not word-for-word mechanical translations
- Chinese versions can use more colloquial developer language (e.g., "跑通" instead of "成功运行")
- Japanese versions should use standard technical Japanese (です/ます form for docs)
- Technical terms remain in English: `watchdog`, `TUI`, `JSON`, `pydantic`, `TOML`, `CLI`, `UUID`
- Product names remain as-is: `Mutsumi`, `Product Hunt`, `Textual`, `Claude Code`

### 6.4 Structural Parity

Both language files must maintain the same section structure:
- Same number of sections
- Same heading hierarchy
- Same code blocks and examples (code is language-neutral)
- Tables can differ in descriptive text but must cover the same fields

## 7. Supported Languages (Current)

Mutsumi supports three languages from day one:

| Language | Doc suffix | TUI locale file | Priority |
|---|---|---|---|
| English | `.md` (un-suffixed) | `locales/en.toml` | Primary (default) |
| Chinese (Simplified) | `_cn.md` | `locales/zh.toml` | Day 1 |
| Japanese | `_ja.md` | `locales/ja.toml` | Day 1 |

The TUI `config.toml` language field:
```toml
[general]
language = "auto"   # "auto" | "en" | "zh" | "ja"
```

`"auto"` detects from `$LANG` / `$LC_ALL` environment variables:
- `ja_JP.*` → Japanese
- `zh_CN.*` / `zh_TW.*` → Chinese
- Everything else → English

## 8. Future: Additional Languages

If community demand grows for Korean, Spanish, etc.:

```
FILENAME.md        → English (primary)
FILENAME_cn.md     → Chinese
FILENAME_ja.md     → Japanese
FILENAME_ko.md     → Korean
```

The `_xx` suffix uses ISO 639-1 language codes. English remains the un-suffixed primary.
