# skill

面向 AI coding agent 的个人可复用 skill / rules 源码仓库。

这个仓库的目标不是绑定某一个 harness，而是维护一套可移植、可审查、可组合的 agent 能力源码；HarnessKit 主要负责发现、安装、分发和组合。

## 设计原则

- **Portable first**：优先使用通用的 `SKILL.md` / `AGENTS.md` 等纯文本约定。
- **Harness-agnostic source**：源码不依赖 HarnessKit 的私有格式；`.hk-kit.zip` 视为分发产物，不作为主要源码。
- **Small, composable skills**：一个 skill 解决一类清晰任务，避免做成巨型万能 prompt。
- **Evidence over ceremony**：关键步骤必须有验证方式，减少无意义流程。
- **Model-aware, not model-locked**：允许针对模型能力做适配，但核心工作流应尽量可跨 Codex、Claude Code、Gemini CLI、OpenCode 等复用。

## 目录

```text
.
├── AGENTS.md                 # 维护本仓库时给 coding agent 的规则
├── skills/
│   └── _template/
│       └── SKILL.md          # 新 skill 的最小模板
└── README.md
```

后续计划按实际使用逐步形成 3–4 组核心能力，例如：

- architecture / requirements
- backend engineering
- frontend engineering
- delivery / verification

先从真实任务中抽取，再决定最终边界，不提前堆大量模板。

## HarnessKit

HarnessKit 可从 Git URL 安装 skills，并会根据仓库来源进行分组。仓库保持标准目录和纯文本源码，HarnessKit 负责本地安装、启停、审计以及 Kit 打包。

## 变更方式

建议使用短生命周期分支开发，完成验证后通过 squash merge 合入 `main`，让主分支历史保持清晰。
