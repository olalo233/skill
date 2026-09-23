# Personal skills

可跨 agent 安装的自有技能与资产。发布及安装入口为 **https://github.com/olalo233/skill**。保留上游来源、许可证和我们的定制；不从本机配置目录整包发布。

## 选择需要的技能

| 组合 | 技能 | 用途 |
| --- | --- | --- |
| 可视化解释 | `html`、`show-me`、`eli5` | 中文阅读排版、图解与浅显解释；共享跟随系统的双色资产 |
| 开发讨论 | `grill-me`、`grilling`、`wait-what` | 明确问题、审视方案、重新解释 |
| 原型与审查 | `prototype`、`ponytail-review` | 验证具体想法、按需检查过度复杂性 |

通用解释技能不依赖 GSD。采用 GSD 的开发项目参见 [开发套件](docs/gsd-suite.md)；其 [项目规则](docs/gsd-project-policy.md) 仅按需合并进项目，不自动安装或覆盖用户规则。

## 一个 URL，按环境安装

公开仓可通过 HTTPS 匿名下载，无需配置 GitHub token。支持标准 `skills/<name>/SKILL.md` 目录的工具也可直接导入本仓 URL。

```bash
# 全局安装到当前机器的 Codex
npx skills add https://github.com/olalo233/skill --global --agent codex \
  --skill html show-me eli5 --yes

# 同一台机器的多个 agent；只选择实际使用的运行时
npx skills add https://github.com/olalo233/skill --global \
  --agent codex claude-code gemini-cli opencode \
  --skill html show-me eli5 --yes
```

`show-me` 和 `eli5` 的 HTML 模式依赖同级 `html`。三个一起安装；只需要 HTML 文档时可仅安装 `html`。其他组合也是可选的，不要用 `--all` 把无关技能或 agent 一起装入。

项目级安装去掉 `--global`。已有同名技能时先核对并备份本地改动，避免重复副本；后续更新以本仓为来源。无需同时安装原作者仓的同名技能。

不能运行 Node/npm 的环境也可以：

```bash
git clone --depth 1 https://github.com/olalo233/skill.git
```

然后把选中的 `skills/` 子目录一起放入该 agent 的标准技能目录；不要把整个仓库及其维护文件放进技能扫描目录。网络受限时可从已下载副本导入。仓库 URL 提供统一来源，并不保证每个网络都能直连 GitHub。

## 更新

```bash
npx skills update html show-me eli5
```

更新使用安装器登记的来源，先检查本地是否有未回传的定制。复制安装或离线快照需要重新部署；只有 clone 更新不代表所有 agent 的副本都已更新。

## 上游自动合并

每周一 03:23 UTC（香港时间 11:23），GitHub Actions 获取 `.sync/upstreams.json` 登记的上游目录，以记录的 commit 为基线进行三方合并。

- 只导入已登记的技能路径和许可证；保留本地新增文件与可合并的定制。
- 合并测试、结构/便携性检查、凭据扫描全部通过后，自动提交到 `main`。
- 冲突、路径消失、不支持的文件类型、许可证变更或检查失败时停止发布；当前 `main` 不受影响。Actions 日志和摘要保留原因。
- 使用 GitHub 自带的短期 `GITHUB_TOKEN`，无需长期 PAT；依赖 Action 固定到 commit。
- 自动检查是确定性检查，不代表 AI 语义审查或所有 agent 的实机验收。修改重叠时由维护者解决并推进基线。

可在 Actions → **Sync upstreams** 手动运行。不强推；同步期间若 `main` 被他人更新，推送会失败并留待下次运行。GitHub 对长期无活动公开仓可能暂停计划任务，需从 Actions 重新启用。

## 维护

```bash
python3 scripts/validate.py
python3 -m unittest discover -s tests -v
gitleaks git . --redact
```

敏感文件、私有环境清单和会话日志不属于本仓。技能上游与许可证见 [SOURCES.md](SOURCES.md)。HTML 示例为 `skills/html/design-system/component-samples.html`，下载后用浏览器打开即可。
