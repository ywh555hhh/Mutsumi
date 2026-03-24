# RFC-006：品牌与叙事重置 —— “Never Lose a Thread”

> **[English Version](./RFC-006-brand-narrative-reset.md)** | **[日本語版](./RFC-006-brand-narrative-reset_ja.md)**

| 字段 | 值 |
|---|---|
| **RFC** | 006 |
| **标题** | 品牌与叙事重置 |
| **状态** | Accepted |
| **作者** | Wayne (ywh) |
| **创建时间** | 2026-03-22 |

---

## 摘要

本 RFC 将 Mutsumi 的品牌叙事，从“一个极简 TUI 任务看板”重新定义为更大解决方案中的 View 层：**为多线程人类常驻在线的 thread-keeper**。

这次转向改变了几个核心问题：

- 故事的主角是谁——是用户的大脑，而不是工具本身
- 我们解决的到底是什么问题——是上下文切换时丢线程，而不是“任务管理有摩擦”
- 我们如何在生态中定位自己——是零摩擦工作流中的一个组件，而不是孤立的单体产品

新的 tagline：**Never lose a thread.**

---

## 1. 动机：为什么要重置

### 1.1 旧叙事

重置之前的叙事把 Mutsumi 当作一个产品来介绍：

> “一个极简的 TUI 任务看板，监听你的 `tasks.json`，并尽量不打扰你。”
> “让你的 AI agent 当大脑——Mutsumi 只是眼睛。”

这种 framing 有两个结构性问题：

1. **它把一个组件当成了完整产品来卖。** 用户并不想要一个 TUI。他们想要的是在频繁切换上下文时别再忘事。TUI 只是实现细节。
2. **它把竞争拉回功能对比。** “比 Taskwarrior 更好，因为……”会把我们拖进红海。真正的故事是一个 Taskwarrior 并未覆盖的新类别。

### 1.2 被错过的洞察

旧叙事正确识别了目标用户：多线程的高并发个体。但它错判了痛点。

旧诊断：*“唤出一个任务管理器的摩擦太高。”*

真实诊断：**“你的生物工作记忆大约只有 4 个槽位。你却同时运行着 12 条线程。每次切换上下文，线程都会被挤出去。真正会在凌晨 2 点反咬你一口的，就是那个被遗忘的线程。”**

瓶颈不在于“打开 Notion 太慢”。瓶颈在于你的大脑物理上不可能同时维持所有活跃线程。你需要一个外部线程表——始终可见、扫一眼几乎零成本、并且由你的 agents 持续维护。

### 1.3 Focus vs. Thread-Keeping

这**不是**一个专注工具。对于目标用户来说，“一次只做一件事”的时代已经结束了。

| 概念 | Focus（专注） | Thread-Keeping（守线程） |
|---|---|---|
| 哲学 | 单线程，屏蔽干扰 | 多线程，拥抱上下文切换 |
| 隐喻 | 降噪耳机 | 空中交通管制雷达 |
| 用户模型 | “你分心了，要自律一点” | “你本来就是并行的，让我帮你托住线程” |
| 产品 | Forest、Pomodoro、Deep Work | **Mutsumi** |
| 失败模式 | 看了一眼手机就开始内疚 | 遗忘线程，最后拖垮截止期 |

Thread-keeping 把多线程视为用户的超能力，而不是缺陷。它不会要求你停下来。它做的是确保没有东西从栈上掉下去。

---

## 2. 新叙事

### 2.1 叙事结构

新叙事采用三层结构，每一层面向不同深度的受众：

```text
Layer 0: Emotional Story（README、Product Hunt、落地页）
  → 对用户的大脑说话。Pain → Relief → How。

Layer 1: Technical Story（文档、架构）
  → 对开发者说话。MVC、Agent Agnostic、Local Only。

Layer 2: Ecosystem Story（集成指南、Roadmap）
  → 对工作流说话。Quake terminals、Raycast、Agent setup。
```

### 2.2 Layer 0 —— 情绪层讲述

> 你不需要“专注”。你需要的是永远不要丢掉一条线程。
>
> 现代的高并发个体每天要在十几个上下文之间切换——写代码、review、发消息、跑 agents、扫信息流。这不是缺陷。这就是你的运行模式。
>
> 真正的问题不是你做的事情太多，而是你一旦切走，上一条线程就开始从脑子里褪色。一小时后，你原本打算修的关键 bug 蒸发了。不是因为你不自律，而是因为人的工作记忆大约只能同时放四件事，而你此刻开着十二条线程。
>
> Mutsumi 不会让你慢下来。不会让你关浏览器。也不会对你讲“深度工作”的大道理。
>
> 她只做一件事：**始终把你的所有线程放在余光里。**
>
> 一天切换 40 次上下文也没关系。每次你回头扫一眼，都能立刻看到手头有什么、有什么在等待、你的 agents 已经把什么往前推进了。
>
> 一个热键唤出。一个热键收起。轻到你会忘记她存在——直到你需要她。
>
> **Never lose a thread.**

### 2.3 Layer 1 —— 技术层讲述（沿用旧叙事）

现有的技术叙事仍然成立，而且依然锋利：

- **MVC Separation**：Mutsumi 是 View。`tasks.json` 是 Model。你的 Agent 是 Controller。
- **Agent Agnostic**：任何能写 JSON 的程序都是合法 controller。
- **Local Only**：零网络。数据就是文件。
- **Hackable First**：TOML 配置、自定义主题、自定义键位。

变化的是 framing。它们不再只是“为什么 Mutsumi 是一个好 TUI”，而是“为什么 Mutsumi 是 thread-keeping 工作流中正确的 View 层”。

### 2.4 Layer 2 —— 生态层讲述（新增）

Mutsumi 只是一个组件。完整工作流还需要：

| 层 | 组件 | 示例 |
|---|---|---|
| **Summon** | 即时唤起终端 | Quake-mode terminal（macOS iTerm2 / Windows Terminal Quake / Linux guake）、Raycast/Alfred/Spotlight 集成、tmux popup |
| **View** | 可视线程表 | **Mutsumi TUI** |
| **Control** | 创建与管理任务 | AI Agents（Claude Code、Codex CLI、Gemini CLI）、CLI（`mutsumi add`）、脚本 |
| **Model** | 持久化数据 | `tasks.json`（本地、纯文本、可 Git 化） |
| **Notify** | 被动反向通知 | `events.jsonl` tailing、OS notifications（未来） |

用户并不是在安装“Mutsumi”。用户是在搭建一个**工作流**，其流程是：

1. 一个热键唤出正在运行 Mutsumi 的下拉终端
2. 他们的 agents 在工作时写入任务
3. 扫一眼就能看见所有活跃线程
4. 一个热键把它收起

Mutsumi 填补的是 View 这一层。其余部分由生态提供。

---

## 3. 品牌更新

### 3.1 Tagline

| 之前 | 之后 |
|---|---|
| *The silent task brain for the multi-threaded you.* | **Never lose a thread.** |

### 3.2 Elevator Pitch

| 之前 | 之后 |
|---|---|
| 一个极简的 TUI 任务看板，监听你的 JSON，并尽量不打扰你。 | 你的线程，始终在视野里。一个由 AI agents 写入、你只需扫一眼的终端任务看板——一个按键唤出，再一个按键消失。 |

### 3.3 人格特质（保留，但重构 framing）

现有的人格特质（Quiet、Present、Humble、Hackable、Fast）都保留。新增一项：

| 特质 | 描述 |
|---|---|
| **Peripheral** | 她住在你视野边缘。不是舞台中央，也不是被藏起来。她就在那里——像墙上的一只钟。 |

便利贴隐喻继续保留：

> 安静地坐在你旁边，拿着一张写满你线程的便利贴。你扫她一眼时，她会把那张纸微微举高一点。你移开视线时，她就安静地继续等着。

### 3.4 我们不再说的话

| 旧说法 | 退役原因 |
|---|---|
| “task exo-brain” | 过度承诺。她不是大脑，她是 thread-keeper。 |
| “Let your AI agent be the brain — Mutsumi is just the eyes.” | 通过否定来定义 Mutsumi，本质上低估了她。 |
| “stays out of your way” | 防御式 framing。应该说她**是什么**，而不是她**不是什么**。 |
| “multi-threaded super-individuals” | 保留 “multi-threaded”，去掉 “super-individuals”——太端着。 |

### 3.5 我们开始说的话

| 新说法 | 使用场景 |
|---|---|
| “thread” 而不是 “task” | 情绪/叙事语境中用。技术/API 语境里仍然用 “task”。 |
| “thread-keeper” | 描述 Mutsumi 在工作流中的角色。 |
| “summon / dismiss” | 描述调用模式，而不是 “open/close”。 |
| “glance” | 描述交互方式，而不是 “check” 或 “review”。 |
| “peripheral vision” | 描述 Mutsumi 在工作空间里的位置。 |

---

## 4. 对现有文档的影响

| 文档 | 动作 |
|---|---|
| `BRAND.md` | 更新 tagline、elevator pitch，并加入 Layer 0 叙事 |
| `docs/site/index.mdx`（所有语言） | 重写 hero、feature cards、flow diagram |
| `docs/site/what-is-mutsumi.mdx`（所有语言） | 围绕“丢线程”问题重写 |
| `README.md` | 后续在 Phase 4 中按 Layer 0 叙事重写 |
| `RFC-001` | 不变——技术架构没有变化 |
| `ROADMAP.md` | 后续——在 post-launch 中提高生态集成优先级 |

---

## 5. 决议

**Accepted。** 这次叙事重置不会改变任何代码、架构或数据契约。它改变的是我们如何描述已经构建出来的东西。实施将从文档站点和 `BRAND.md` 开始。
