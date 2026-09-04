# Sources

This suite is an assembly of upstream work. The copied skill files are intentionally unmodified in V1.

## Workflow engine

### Open GSD

- Repository: `open-gsd/gsd-core`
- Reviewed revision: `590edec7a7008f41f6db783541418b5b3e8eb297`
- Role: quick and full workflows, requirements, research, plans, worker waves, state, review, UAT, and shipping
- Packaging: not copied. Install through the official GSD installer because it generates runtime-specific assets.

## Bundled skills

### Matt Pocock skills

- Repository: `mattpocock/skills`
- Revision: `6654f6b60cd9d5be8b54c6fafe44346dabeb3b76`
- Copied paths:
  - `skills/productivity/grilling/`
  - `skills/engineering/prototype/`
- License: MIT, preserved under `licenses/mattpocock-skills-MIT.txt`

### HumanLayer show-me

- Repository: `humanlayer/skills`
- Revision: `3c2629142c5d437428269b1b722b08c0b87f574d`
- Copied path: `plugins/show-me/skills/show-me/`
- License: MIT, preserved under `licenses/humanlayer-skills-MIT.txt`

### Ponytail review

- Repository: `DietrichGebert/ponytail`
- Revision: `2ed6c52c9d7e5e56942508591085fd45dea277d3`
- Copied path: `skills/ponytail-review/`
- License: MIT, preserved under `licenses/ponytail-MIT.txt`

Only the narrow review skill is bundled. The always-on Ponytail skill is not included because an always-on simplification persona can distort requirements and over-steer reasoning-heavy models.

## Evaluated but not bundled

These may be useful later, but they are not part of the first runtime suite:

- `warpdotdev/common-skills` `skill-doctor`: use externally after enough real transcripts exist; it is a suite-evaluation tool, not a development stage.
- `mattpocock/skills` `retro`: lightweight session retrospective; also a maintenance tool rather than a runtime stage.
- `cursor/plugins` `unslop`: useful for prose and presentation work, not required for the coding workflow.
- `yizhiyanhua-ai/fireworks-open-eli5`: strong evidence-aware visual explainer, but too heavy as a default alignment step.
- `inkboard/system-atlas`: useful for long, multi-round architecture design, but not required for ordinary implementation.
- `openai/skills` `define-goal`: good goal-quality guidance, but its tool calls are tied to a goal runtime that is not assumed in local Codex.
- Matt Pocock's `to-spec`, `to-tickets`, `implement`, and `code-review`: intentionally omitted because GSD already owns those artifacts and stages. Including both would create competing workflows.

## Update rule

Do not merge upstreams casually. Re-review changes, update the pinned revision here, preserve the relevant license, and test both the quick and full paths on real work before adopting an update.
