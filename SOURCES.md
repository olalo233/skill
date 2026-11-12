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
- Invocation frontmatter: `triggers: [user]` (Devin) added to grill-me and grilling; `disable-model-invocation: true` added to grilling to match its existing `agents/openai.yaml` user-invoked policy.
- Vendored mirror: `skills/`, `README.md`, and `LICENSE` land at `vendor/matt/` under the same baseline (`vendor_paths` in `.sync/upstreams.json`; the weekly three-way merge consumes them too — vendor destinations are confined to `vendor/` — so the mirror tracks the same revision as the promoted skills).
- Local addition: `vendor/matt/skills/engineering/matt-flow/` is the olalo233/mattpocock-skills fork's `ask-me` flow map, renamed to avoid colliding with `skills/ask-me`. It is fork content, not upstream; the merge leaves it alone because it is absent from the upstream snapshot.
- License: MIT, preserved under `licenses/mattpocock-skills-MIT.txt` and `vendor/matt/LICENSE`.

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
- Local adaptation: retain the narrow over-engineering review. The reviewed upstream update broadened it into a general correctness/security/performance review; that scope expansion is intentionally not adopted. Future updates merge against the reviewed baseline while preserving this local policy.
- License: MIT, preserved under `licenses/ponytail-MIT.txt`.

Only the narrow review skill is bundled. The always-on Ponytail skill is not included. In this suite the review is optional; deleting lines is not a delivery metric.

### Cursor pstack

- Repository: `cursor/plugins`; path: `pstack/` (whole directory, not split: it depends on sibling paths, subagents, and automations).
- Recorded revision: `2eaf46574b25cdf7ef8c849837099b866b7438ce` in `.sync/upstreams.json` (`vendor_seeded: true`); vendored whole at `vendor/pstack/` and indexed as one suite — on Cursor prefer the native plugin, elsewhere the text reads with degraded features.
- License file seeded into `licenses/cursor-plugins-pstack-MIT.txt` from the local 246bc508 plugin cache; assumed unchanged at 2eaf4657 — **unverified**.

## Base suite and invocation policy

- `skills/ask-me/` is a local skill: index router that recommends, then waits. User-invoked only.
- User-invoked skills carry all three configs: `disable-model-invocation: true` (Claude Code frontmatter, also read by Cursor per the shared skills spec — **unverified for Cursor**), `triggers: [user]` (Devin, per CLI docs), and `agents/openai.yaml` `policy.allow_implicit_invocation: false` (Codex). Applied to `ask-me`, `wait-what`, `eli5`; `grill-me` and `grilling` aligned to the same policy.
- `html` and `show-me` stay model-invocable; descriptions rewritten as passive conditional sentences (`Use when the user asks for …`). `html` gained an explicit `agents/openai.yaml` with `allow_implicit_invocation: true`.
- `wait-what` merged the divergent `~/.agents/skills` variant: consult `CONTEXT.md`/`CONTEXT-MAP.md` when present, and rephrase rather than repeat verbatim. The older `~/.claude` STE100 variant contributed nothing new.
- `INDEX.md` and `index.json` are generated by `scripts/build_index.py` from `skills/` and `vendor/`; suite membership, dependencies, and per-directory retired lists live in `.sync/index-source.json`. `scripts/install-base` installs the base suite from a pinned clean clone (`--source`, required `--ref`; dry-run by default). All changes — retired entries, replaced installs, root index files — are recorded in one manifest inside a single backup directory before apply, a failure restores from it, and `--rollback <backup-dir>` replays the restore. Retirement runs only for user-level installs; `--project` copies and never moves anything.

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
