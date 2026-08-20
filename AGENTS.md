# Skill repository instructions

This repository is the source of truth for reusable agent kits.

## Authoring rules

- A distributable kit lives under `kits/<kit-name>/`.
- Each skill lives at `kits/<kit-name>/.agents/skills/<skill-name>/SKILL.md`.
- The skill folder name and frontmatter `name` must match exactly.
- Every `SKILL.md` must have concise `name` and trigger-oriented `description` fields.
- Keep each skill focused on one job. Prefer instructions over scripts unless deterministic execution is necessary.
- Skills must be self-contained. Do not depend on files outside their own folder unless the kit README explicitly declares the dependency.
- Do not hardcode model names, subscription tiers, personal paths, credentials, or machine-specific commands into reusable skills.
- Keep always-loaded `AGENTS.md` guidance short. Put detailed procedures in skills.
- Record upstream influence and pinned revisions in the kit's `SOURCES.md`.
- Do not edit deployed copies in agent directories. Change this repository, validate, then redistribute through HarnessKit.

## Change workflow

- Work on a feature branch.
- Run `python3 scripts/validate_skills.py` after changing skills.
- Commit coherent, verified changes. Preserve intermediate commits; integration branches may squash according to repository policy.
- Do not push, open a pull request, or merge unless explicitly requested.
