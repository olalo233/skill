# GSD Development Suite

以原生 Open GSD 为唯一交付流程，组合少量社区 skill。`main` 是维护和安装主线；历史实验分支保留作参考，不与本套件同时加载。

## 清单与边界

| 组件 | 用途 |
| --- | --- |
| Open GSD（单独安装） | 需求、范围、阶段计划、执行、状态、验证与交付 |
| `grill-me` + `grilling` | 一个手动入口及其访谈方法，不是两轮讨论 |
| `wait-what` | 用中文或英文重新解释，保持事实与范围不变 |
| `show-me` | 用最小必要的图示说明当前问题 |
| `prototype` | 用一次性原型回答一个明确的问题，不冒充生产 MVP |
| `ponytail-review` | 按需审查当前改动的过度复杂性，不是强制交付阶段 |

本仓库不包含第二套 planner、worker 调度器、任务状态或记忆系统。GSD 的运行时文件由官方安装器负责，不从源码目录直接复制。

## 从讨论直接进入 GSD

**同一会话完成设计讨论和 GSD 首次落盘，之后用原生新上下文执行。**

已经在 `grill-me` 中讨论过，就在当前父会话要求 GSD 接续。也可以先进入 GSD 的讨论环节，再在同一会话调用 `grill-me` 澄清具体歧义。两者不应串成两轮完整访谈。

GSD 接手时使用当前全部可用讨论，保留必要的初始化、仓库检查和确认，只补真实缺口。不要求用户转写 PRD，不先清空上下文，不为省问答而启用跳过确认的自动模式。若当前会话已被压缩或缺少关键原文，应如实核对缺失内容，不声称无损继承。

设计讨论的目标是：目标行为和核心路径明确；本轮做与不做的边界明确；重要状态、数据、接口/交互和不可逆取舍明确；能判断什么算完成。不是提前设计所有模块、未来功能和低概率场景。普通可逆实现细节由执行者负责。

GSD 直接把已确认结论写入原生文件：项目目标/约束/关键决策进入 `PROJECT.md`，能力与范围进入 `REQUIREMENTS.md`，阶段顺序进入 `ROADMAP.md`，阶段设计决策进入相应 `CONTEXT.md`。不要预先伪造这些文件来绕过 GSD 初始化。

首次换上下文前，在仍能看到原讨论的会话里核对这批原生文件：特别检查排除项、决策理由、精确字段/条件，以及提议与已确认决定的区别。只指出实质差异，不再写一份平行规格。

随后让 GSD 用原生阶段计划和新 executor 上下文继续。子代理不会自动拥有主会话的完整聊天；向它提供相关原生文件，而不是每次重放全部访谈。大任务仍要拆成能完成实现、验证和必要修复的小 plan。

例如，在讨论已充分且用户准备推进时：

```text
设计和本轮范围已确认。请在当前会话继续适用的原生 GSD 流程，
复用以上回答，只补缺失或矛盾项；将结论直接写入 GSD 原生文件。
落盘并核对之前不要清空上下文，不要另写一份中间 PRD。
```

这是调用约定，不是新的命令、自动路由器或 GSD 补丁。具体命令拼写以已安装运行时的 GSD 帮助为准。

## 安装到项目仓库

在目标项目目录运行，先安装 GSD，再安装这六个辅助 skill：

```bash
npx -y @opengsd/gsd-core@latest
# 在官方安装器选择实际运行时和安装范围；已有正常工作的 GSD 不必重装。

npx skills add olalo233/skill --agent codex \
  --skill grill-me grilling wait-what show-me prototype ponytail-review --yes
```

Claude Code 将 `--agent codex` 改为 `--agent claude-code`；需要同时支持两者可传入两个 agent。默认是项目级安装，不要无差别使用 `--all` 安装到所有运行时。已有同名 skill 时先检查来源，避免全局和项目副本重复触发。

这是私有仓库，需要本机已有合法 Git/GitHub/SSH 访问。无需在命令、skill 或仓库里填写 token。也可以用 SSH Git URL 安装：

```bash
npx skills add git@github.com:olalo233/skill.git --agent codex \
  --skill grill-me grilling wait-what show-me prototype ponytail-review --yes
```

**下载一次、本地重复使用：**

```bash
git clone --depth 1 git@github.com:olalo233/skill.git "$HOME/skill-suite"
# 然后在任意目标项目目录：
npx skills add "$HOME/skill-suite" --agent codex \
  --skill grill-me grilling wait-what show-me prototype ponytail-review --yes
```

`npx skills add` 安装 skill 目录，不会自动安装本仓库根 `AGENTS.md`。要在整个项目采用套件约定，应将其中适用规则合并进现有 `AGENTS.md` / `CLAUDE.md`，保留项目原有约束；不要直接覆盖整份文件。`grill-me` 自身也包含同会话接续的调用边界。

`grill-me`、`grilling` 和 `wait-what` 提供 Codex 原生的显式调用配置；不把所有 SKILL.md 全文复制到项目总指令。安装后检查实际 skill 列表，需要时重启 Agent。先试一次中文、一次英文 `wait-what`，以及一次 `grill-me` 到 GSD 的接续。

## HarnessKit

HarnessKit 原生支持从 Git URL 或本地目录安装 skill，并从已有扩展、规则、记忆组成 Kit；不需要专用下载器。

- 已有本机仓库副本时，优先从本地 `skill-suite` 目录导入，选中六个 skill。
- Git URL 路径可使用 `https://github.com/olalo233/skill`，但私有仓库是否能直接拉取取决于本机 HarnessKit/Git 认证。失败时使用上面的已认证本地 clone；不要把 token 写进 URL。
- 在 HarnessKit 创建一个 `GSD Development` Kit，包含这六个 skill。需要统一项目规则时，将适用的 AGENTS 内容作为规则/记忆项合并管理；部署前检查现有文件冲突，不能覆盖项目原规则。
- GSD 本体继续用官方安装器管理；这个六-skill Kit 不等于已安装完整 GSD。
- Kit 建好后使用 HarnessKit 原生导出得到 `.hk-kit.zip`，可在其他机器导入。导出包是快照，不会自动跟踪主线。

不要在同一项目分别用多个安装器维护同一份 skill。可以由 skills CLI 安装、HarnessKit 查看，或者由 HarnessKit 负责部署；选定一个写入来源。

## 更新与验证

远端安装可以用 `npx skills update grill-me grilling wait-what show-me prototype ponytail-review`。本地源先 `git -C "$HOME/skill-suite" pull --ff-only`，再按原方式安装/刷新；不要假设拉取源码就更新了所有已部署 Kit。Kit 更新按 HarnessKit 的实际界面重新部署。

`main` 是发布来源，不是自动升级所有工作项目的承诺。正常交付期间固定已验证版本；升级后用真实小阶段验证再扩散。

当前维护检查包括格式、依赖和仓库内容核对。源码审查不等于已在用户本机通过 Codex/Claude Code/HarnessKit 实机验收。GSD 安装器版本与本仓库的辅助 skill 版本分别管理，参见 `SOURCES.md`。
