# RFC-008：开箱即用的首次运行 Onboarding

> **[English Version](./RFC-008-out-of-box-first-run-onboarding.md)** | **[日本語版](./RFC-008-out-of-box-first-run-onboarding_ja.md)**

| 字段 | 值 |
|---|---|
| **RFC** | 008 |
| **标题** | 开箱即用的首次运行 Onboarding |
| **状态** | Draft |
| **作者** | Wayne (ywh) |
| **创建时间** | 2026-03-22 |

---

## 1. 摘要

Mutsumi 当前的架构已经很强，但端到端的首次运行流程对用户来说仍然过于“可见”：先安装、再 init、再创建文件、再注册项目、再配置 agent、也许还要设置分屏，最后才能打开看板。

这与 Mutsumi 的核心承诺正好相反：**零摩擦**。

本 RFC 提议引入一个新的 onboarding 模型，以一条命令为中心：

```bash
mutsumi
```

如果环境已经准备好，Mutsumi 应该立即打开。
如果尚未准备好，Mutsumi 必须**在原地自举**：通过一个短小但高信号的 onboarding flow，只询问少量真正重要的问题，自动创建缺失文件，然后进入可用状态。

目标很简单：

> **用户应该感觉自己是在打开一个工具，而不是部署一个系统。**

---

## 2. 问题陈述

### 2.1 当前的摩擦

今天，一个新用户在 Mutsumi 变得真正有用之前，可能要考虑所有这些事：

- 这是个人任务流，还是项目任务流？
- `~/.mutsumi/config.toml` 存在吗？
- `~/.mutsumi/mutsumi.json` 存在吗？
- 当前项目里已经有 `mutsumi.json` 了吗？
- 这个项目是否已经注册？
- 当前 Agent 知道怎么和 Mutsumi 配合吗？
- 需不需要用 tmux/zellij 脚本？
- 要不要手动去改 `CLAUDE.md` / `AGENTS.md` / 类似文件？

单看每一步都合理，但组合起来就不合理了。

### 2.2 根本原因

问题不是 Mutsumi 缺少功能。

问题在于，**setup 仍然是一个用户可见的工作流**，而没有被压缩进默认行为里。

用户并不想学习一张初始化关系图。他们只想：

1. 打开 Mutsumi
2. 扫一眼任务
3. 让 Agent 很自然地和它交互

### 2.3 产品原则

Mutsumi 应该为**开箱可用性**优化：

- 一个自然入口
- 合理默认值
- 渐进披露
- 只有对侵入性动作才要求明确同意

---

## 3. Goals

| Goal | Description |
|---|---|
| **单一自然入口** | `mutsumi` 应成为默认开始方式。用户不应在应用变得可用之前被迫先学 `init`。 |
| **启动必须成功** | 运行 `mutsumi` 时，要么直接打开应用，要么打开一个简短 onboarding flow，之后仍然打开应用。 |
| **少决策，高价值** | 首次运行只询问那些会直接影响用户即时舒适度的设置：语言、输入预设、主题、工作区模式、agent 集成。 |
| **不假设 tmux** | 终端布局辅助仍然是可选工具，而不是主路径的一部分。 |
| **skills-first 集成** | 对受支持的 agents，默认集成路径应优先使用 skills / bridges，而不是修改项目核心指令文件。 |
| **核心文件修改必须显式同意** | 写入 `CLAUDE.md`、`AGENTS.md`、`GEMINI.md` 等文件必须是 opt-in，绝不能隐式发生。 |
| **不重复征收 init 税** | 用户不该为每个新仓库都重新跑完整 setup。后续项目接入应该轻量。 |
| **保留 agent-agnostic 架构** | Mutsumi 仍然 local-first、agent-agnostic。Onboarding 只是改善 UX，而不是把产品绑定到某个模型或某种终端工作流。 |

---

## 4. Non-goals

本 RFC **不**提议：

- 把 tmux/zellij 变成主 onboarding 路径的一部分
- 把 Mutsumi 绑定到 Claude Code 单一工具
- 引入网络调用、账号登录或远程服务
- 把高级设置塞进 first-run
- 静默重写用户拥有的项目指令文件
- 把 Mutsumi 变成 workspace/process manager

Mutsumi 仍然是一个本地任务看板与多源 command center。

---

## 5. UX 模型

### 5.1 三种启动状态

运行 `mutsumi` 后，应该落入以下三条路径之一：

#### A. Ready state

如果用户环境已经就绪，Mutsumi 立即启动。

条件可能包括：
- config 已存在
- personal file 已存在，或者当前模式下不需要它
- 当前项目已经被识别，或者与当前场景无关

#### B. 首次启动自举

如果这基本上是第一次启动，Mutsumi 在进入主 UI 前打开一个**简短的 onboarding wizard**。

这个 wizard 会创建缺失文件，并保存用户的核心偏好。

#### C. 轻量项目接入提示

如果用户已经完成过 onboarding，但在一个尚未注册的新仓库里启动 Mutsumi，就**不应**重新播放完整的首次向导。

取而代之，应显示一个轻量提示，例如：

- Register current folder as a project
- Create `./mutsumi.json`
- Skip for now

这样可以让项目 onboarding 变得轻量且不重复。

---

### 5.2 首次向导结构

首次运行体验应当**短而聚焦**。

把它做成向导是可以接受的，因为问题数量被刻意压缩，并按照对用户影响的大小排序。本 RFC 明确偏好一个短小的分步流程，而不是 RFC-002 中那种巨大的单屏设置页。

#### Step 1 —— 语言

语言应是第一步。

选项：
- English
- 中文
- 日本語

默认值：
- 匹配系统 locale，否则使用 English

理由：
- 后续 onboarding 文案应立即切换成用户语言
- 这是整个流程里建立信任最快的一步

#### Step 2 —— 输入预设

选项：
- Arrows
- Vim
- Emacs

默认值：
- **Arrows**

理由：
- 这符合产品规则：默认预设应服务于普通用户，而不仅仅是终端高手
- 用户不应该在应用已经打开后，才发现默认键位模型让自己不舒服

#### Step 3 —— 主题

选项：
- Monochrome Zen
- Nord
- Dracula
- Solarized

默认值：
- **Monochrome Zen**

理由：
- 主题风险低，但主观价值高
- 它能让首次体验更“属于自己”，而不会引入额外复杂度

#### Step 4 —— 工作区模式

选项：
- Personal only
- Current project only
- Personal + current project

智能默认值：
- 如果当前目录是 Git 仓库：**Personal + current project**
- 否则：**Personal only**

理由：
- 这是减少 personal tasks 和 project tasks 混淆所需的最小关键决策
- 它与 Mutsumi Phase 5 的多源模型相匹配

#### Step 5 —— Agent 集成

选项：
- Skip for now
- Register Mutsumi skills / bridge for current agent
- Register skills / bridge **and** append project integration instructions to agent core file

默认值：
- 当当前 agent 可检测且受支持时：**只注册 skills / bridge**
- 否则：Skip for now

重要说明：
- 修改 `CLAUDE.md`、`AGENTS.md`、`GEMINI.md` 或等价文件，必须是一个独立且显式的选择
- skills/bridge 注册与 project core-file 注入不是同一操作，不能混在一起

---

### 5.3 交互要求

onboarding flow 必须遵循 Mutsumi 的核心交互规则。

每一步都必须同时可通过键盘和鼠标完成。

| 动作 | 键盘 | 鼠标 |
|---|---|---|
| 在选项之间移动 | Arrow keys / Tab | 点击选项 |
| 确认选择 | Enter / Space | 点击按钮 |
| 返回上一步 | Escape / 专用 Back 操作 | 点击 Back |
| 接受推荐默认值 | Enter | 点击 Continue |
| 取消 onboarding | Escape | 点击 Skip / Cancel |

### 5.4 取消行为

取消 onboarding **不能**让 `mutsumi` 启动失败。

如果用户取消：
- Mutsumi 使用本次会话的临时默认值启动
- 显示一个可用的空白 UI
- 后续再提供一个轻量的 “Finish setup” 入口

这可以保持“主命令必须成功”的规则。

---

## 6. 自动创建的内容

取决于用户的选择，Mutsumi 可能会自动创建：

```text
~/.mutsumi/
├── config.toml
└── mutsumi.json

<current-project>/
└── mutsumi.json
```

### 6.1 始终可以安全创建

以下都是 Mutsumi 自有文件，因此允许在 onboarding 中自动创建：

- `~/.mutsumi/config.toml`
- `~/.mutsumi/mutsumi.json`
- 当前项目里的 `mutsumi.json`（仅当用户选择了需要它的模式）

### 6.2 未经明确同意绝不能自动创建

以下属于用户/项目拥有的指令文件，绝不能被隐式修改：

- `CLAUDE.md`
- `AGENTS.md`
- `GEMINI.md`
- `opencode.md`
- 等价的 agent instruction files

---

## 7. Agent 集成边界

### 7.1 推荐的集成顺序

Mutsumi 应优先采用如下顺序：

1. **Mutsumi 自有 bridge / skills 注册**
2. **打印 snippet / 可复制说明**
3. **项目核心文件注入**（仅显式 opt-in）

### 7.2 为什么是 skills-first

skills/bridge 注册是更好的默认值，因为它：

- 减少项目文件污染
- 避免对 instruction files 的意外修改
- 更容易随时间演进
- 更像“开启一种能力”，而不是“重写项目政策”

### 7.3 为什么 core-file 注入必须保持可选

核心指令文件是高信任、高敏感度文件。

用户可能已经在里面仔细写好了项目约定。Mutsumi 不应仅仅因为在跑 onboarding，就默认自己有权向里面追加内容。

因此：

> **Mutsumi 可以提供 project core-file injection，但绝不能把它设为默认路径。**

### 7.4 支持的集成模式

| Mode | Behavior |
|---|---|
| `none` | 不执行任何 Agent 集成。 |
| `skills` | 为当前受支持 Agent 注册 Mutsumi 任务能力，不编辑项目 instruction files。 |
| `skills+project-doc` | 注册 skills/bridge，并额外向合适的 agent instruction file 追加项目集成说明。 |
| `snippet` | 当无法自动注册 bridge 时，显示或复制手动说明。 |

---

## 8. 智能默认值

开箱体验更多依赖默认值，而不是可配置性。

推荐默认值：

| 设置 | 默认值 |
|---|---|
| Language | system locale（回退 English） |
| Key preset | `arrows` |
| Theme | `monochrome-zen` |
| Notifications | `quiet` |
| Default tab | `main` |
| Git 仓库中的 workspace mode | `personal + current project` |
| 非 Git 目录中的 workspace mode | `personal only` |
| Agent integration | 支持时使用 `skills`，否则 `none` |
| Core-file injection | `off` |

这些默认值应让大多数用户一路按 Enter 就能完成。

---

## 9. 命令行为变化

### 9.1 `mutsumi`

`mutsumi` 会成为主要的 onboarding 入口。

行为：
- 检测 readiness
- 必要时执行首次启动 bootstrap
- 可选执行软性项目接入提示
- 启动 TUI

### 9.2 `mutsumi init`

`mutsumi init` 仍然有用，但从“必备前置步骤”转变为一个显式的实用命令。

建议语义：
- 强制重新运行 onboarding
- 通过 flags 非交互地创建文件
- 重置或修复某个 setup

### 9.3 `mutsumi setup --agent`

这个命令仍保留，作为安装后的显式集成路径。

它也应当能在 onboarding 内被复用，但它不再是得到一个可用系统的唯一合理路径。

---

## 10. 项目接入模型

首次向导解决的是第一次启动。它不能在后续继续制造重复 setup 税。

当用户已经完成 onboarding 后，又在一个未注册的 Git 仓库里启动 Mutsumi，Mutsumi 应显示一个简短提示：

```text
This folder looks like a project.
[ Register project ] [ Create local mutsumi.json ] [ Skip ]
```

规则：
- 这是轻量提示，不是完整向导
- 除非用户显式重新触发，否则每个 repo 最多只出现一次
- 它绝不能阻止用户访问 personal tasks

这样既保留“瞬间打开”的感觉，又帮助用户逐步采用多项目模型。

---

## 11. 语义化任务操作的默认路由

本 RFC 不定义 skill protocol 本身，但 onboarding 应建立未来 skills 使用的默认路由规则。

推荐路由：

1. 如果用户位于一个已注册项目中，语义化任务操作默认指向该项目的 `mutsumi.json`
2. 如果用户不在项目上下文中，语义化任务操作默认指向 personal tasks
3. 用户显式指定目标时，总是覆盖默认值

例子：
- 在 `~/Code/saas-app` 里说“记得修 refresh token” → 作为项目任务
- 不在任何项目上下文中说“明天买咖啡豆” → 作为个人任务
- 说“把这个加到 personal” → 无论 cwd 是什么，都进入个人任务

这些默认值能减少心智负担，让后续基于 skills 的交互更自然。

---

## 12. 与 RFC-002 的关系

本 RFC 更新了 RFC-002 中提出的 onboarding 方向。

### 12.1 被替换的思路

RFC-002 中以下部分应视为已被替换：

- onboarding 主要通过 `mutsumi init` 发生的假设
- “一个大而全的设置面板”是最佳首次体验的假设
- agent setup 永远是 init 之后明确分离的后置动作这一假设

### 12.2 被保留的思路

以下思路仍然成立：

- zero-config 应该能工作
- config 必须保持人类可读、保持本地
- onboarding 应保持透明而不带魔法感
- Mutsumi 应保持 local-first 且 hackable

简而言之：

> RFC-002 在目标上是对的。
> 本 RFC 更新的是实现这一目标的交互模型。

---

## 13. 实现策略

### 13.1 可能涉及的代码区域

| 区域 | 变化 |
|---|---|
| `mutsumi/cli/__init__.py` | 在启动 app 前加入 readiness 检测 |
| `mutsumi/config/settings.py` | 新增或规范化与 onboarding 相关的配置字段 |
| `mutsumi/config/__init__.py` | 干净地加载/保存新的默认值 |
| `mutsumi/cli/setup.py` | 把 skills/bridge 注册与项目 core-file 注入模式拆开 |
| `mutsumi/cli/project.py` | 复用软接入提示中的项目注册逻辑 |
| `mutsumi/core/paths.py` | 在惰性初始化时复用 personal path helpers |
| `mutsumi/tui/` | 新增 onboarding widgets 与轻量 project-attach UI |

### 13.2 最小实现阶段

| 阶段 | 范围 | 交付物 |
|---|---|---|
| **8a** | Readiness detection | `mutsumi` 能检测 first-run / 需要 attach 的状态 |
| **8b** | First-run wizard | Language、key preset、theme、workspace mode、agent integration |
| **8c** | Lazy file creation | 自动创建 config / personal / project task files |
| **8d** | Skills-first agent bridge | 默认集成路径不编辑 core files |
| **8e** | Optional core-file injection | 显式 opt-in 的项目文档修改 |
| **8f** | Soft project attach prompt | onboarding 之后的轻量 repo 注册提示 |

---

## 14. 测试策略

### 14.1 首次运行测试

- 无 config 且无 task files 启动 → wizard 出现
- 完成 wizard → 创建预期文件并进入 app
- 取消 wizard → 仍以临时默认值进入 app
- 语言选择后 onboarding 文案立即切换

### 14.2 安全性测试

- 选择 `skills` 时不会修改 `CLAUDE.md` / `AGENTS.md`
- 选择 `skills+project-doc` 时只修改预期文件
- 现有项目 instruction files 在重复 setup 时不会被重复注入

### 14.3 项目接入测试

- onboarding 完成后，在未注册 repo 内启动，只显示 soft prompt，而不是完整 wizard
- 选择 Skip 不会阻止 app 启动
- 选择 Register 会创建项目条目以及可选的本地 `mutsumi.json`

### 14.4 输入等价测试

- onboarding 可完全用键盘操作
- onboarding 可完全用鼠标操作
- 推荐默认值可通过连续 Enter 快速接受

---

## 15. 开放问题

1. 主题步骤是否应带一个实时小预览，还是首次运行中只显示名字就够了？
2. 在不变成 agent-specific 的前提下，Mutsumi 应如何可靠检测“当前 Agent”？
3. 取消 onboarding 时，应该什么都不持久化，还是保存截至当前已做的选择？
4. 项目接入提示是否应提供 “这个 repo 再也别问我” 选项？
5. 对于没有 skill/bridge 机制的 Agents，最佳 fallback 是什么：显示 snippet、复制到剪贴板，还是显式提示注入文档？

---

## 16. 结论

Mutsumi 应该让用户觉得：这是一个安静地早已在那里等着自己的工具。

而当安装、初始化、项目注册、Agent 配置都仍然是分离且可见的任务时，这种感觉就会被打断。

本 RFC 把这些问题压缩进一个更简单的模型：

- `mutsumi` 是唯一自然入口
- onboarding 简短而有人味
- 缺失文件自动创建
- skills/bridges 优先于修改项目核心文件
- tmux 和其他布局辅助保持可选
- 后续项目接入是轻量的，而不是重复征税

结果不只是更好的 setup flow。

它也是产品本身更好的表达：

> **Open instantly. Understand instantly. Use instantly.**
