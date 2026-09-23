# Sources

This suite assembles upstream work. Local adaptations are explicit below; do not present them as upstream defaults. Machine-readable paths and current merge baselines live in `.sync/upstreams.json`.

## Workflow engine

### Open GSD

- Repository: `open-gsd/gsd-core`
- Reviewed revision: `590edec7a7008f41f6db783541418b5b3e8eb297`
- Role: quick and phase workflows, requirements, research, plans, worker waves, state, review, UAT, and shipping.
- Packaging: not copied. Install through the official GSD installer for runtime-specific assets.
- Same-conversation integration is a suite invocation convention, not a new upstream command or a guarantee that every runtime suppresses repeated questions. Preserve native setup and approval checks; test on the installed runtime.

## Bundled skills

### Matt Pocock skills

- Repository: `mattpocock/skills`
- Current merge baseline: `.sync/upstreams.json`.
- Unmodified skill bodies:
  - `skills/productivity/grilling/`
  - `skills/engineering/prototype/`
- Added entry: `skills/productivity/grill-me/SKILL.md`.
  - Local adaptation: retain delegation to grilling; add a read-based invocation for runtimes without a Skill tool, a bounded decision scope, and same-parent-conversation GSD continuation only when explicitly requested. No scheduler or new state files.
- Added adaptation: `skills/productivity/wait-what/SKILL.md`.
  - Local changes: choose Chinese/English from the user's explicit request or conversation; bilingual only on request; replace the English-only ASD-STE100 instruction with natural clear language; preserve identifiers, uncertainty, and accepted scope; use existing context without requiring a new glossary; explanation does not authorize implementation.
- Host metadata: `agents/openai.yaml` for grill-me, grilling, and wait-what disables implicit Codex invocation. The upstream grilling body itself is unchanged.
- License: MIT, preserved under `licenses/mattpocock-skills-MIT.txt`.

### HumanLayer show-me

- Repository: `humanlayer/skills`
- Current merge baseline: `.sync/upstreams.json`.
- Copied path: `plugins/show-me/skills/show-me/`
- Local adaptation: system-following shared HTML appearance, sibling `html` dependency, and an original-vs-adapted appearance question for explicit recreations. Preserve automatic discovery rather than adopting upstream's newer manual-only policy.
- License: MIT, preserved under `licenses/humanlayer-skills-MIT.txt`.

### Ponytail review

- Repository: `DietrichGebert/ponytail`
- Current merge baseline: `.sync/upstreams.json`.
- Copied path: `skills/ponytail-review/`
- License: MIT, preserved under `licenses/ponytail-MIT.txt`.

Only the narrow review skill is bundled. The always-on Ponytail skill is not included. In this suite the review is optional; deleting lines is not a delivery metric.

## Installation references

- `vercel-labs/skills`: standard Git/SSH/local-directory installation, selected skills and runtimes, and updates. It installs skill folders, not this repository's root AGENTS.md.
- `RealZST/HarnessKit`: native Git/local skill import, project deployment, and portable `.hk-kit.zip` export/import. Use its actual UI and schema rather than inventing an import manifest.
- OpenAI Codex skill documentation: `agents/openai.yaml` / `policy.allow_implicit_invocation`, progressive disclosure, and repository-scoped discovery.

## Evaluated but not bundled

- `warpdotdev/common-skills` `skill-doctor`: external maintenance after real transcripts exist.
- `mattpocock/skills` `retro`: maintenance, not a delivery stage.
- `cursor/plugins` `unslop`: prose/presentation work, not essential to coding.
- `yizhiyanhua-ai/fireworks-open-eli5`: too heavy as a default alignment step.
- `inkboard/system-atlas`: not needed for ordinary implementation.
- `openai/skills` `define-goal`: tied to a goal runtime not assumed here.
- `to-spec`, `to-tickets`, `implement`, and another `code-review` workflow: duplicate GSD ownership.
- `grill-with-docs` / `domain-modeling`: specialist candidates, not a mandatory second documentation system.
- Legacy Engineering Core and external-worker controllers remain historical branches, not default dependencies.

## Update rule

Review upstream diffs, preserve licenses, record local changes, and test a real bounded GSD phase before adopting an update broadly. Mainline promotion and structural checks are not evidence of successful execution in every Agent or in the user's HarnessKit installation.

## HTML and explanations

### mathbullet HTML

- Repository: `mathbullet/skills`; path: `plugins/html/skills/html/`.
- Baseline: `.sync/upstreams.json` (a reviewed reference snapshot, not a claim of identical content).
- Local changes: English instructions with Chinese reading examples, system-following light/dark assets, redesigned typography/components, optional Canvas theme bridge, and portable asset reuse.
- License: MIT, preserved in `licenses/mathbullet-skills-MIT.txt`.
- The optional PDF helper currently targets macOS Chrome; ordinary HTML is browser-based and has no build requirement.

### Anthropic community ELI5

- Repository: `anthropics/claude-plugins-community`; path: `eli5/skills/eli5/`.
- Baseline: `.sync/upstreams.json`.
- Local changes: portable sibling `html` dependency, shared appearance contract and frontmatter cleanup. These modifications are not upstream defaults.
- License: Apache-2.0, preserved in `licenses/claude-plugins-community-Apache-2.0.txt`. This skill retains that license; the repository's MIT license does not relicense it.

Original repository maintenance code and original additions are MIT licensed. Bundled third-party materials retain their respective licenses and notices.
