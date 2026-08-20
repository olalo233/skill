# Agent Engineering Skills

A small, opinionated source repository for reusable coding-agent kits.

The first kit is **Engineering Core**: a model-agnostic workflow for repository reconnaissance, planning, implementation, debugging, verification, review, simplification, handoff, and shipping. It is designed primarily around Codex, while remaining portable to other agents that understand the open Agent Skills format.

## Repository layout

```text
kits/
  core/
    AGENTS.md
    README.md
    SOURCES.md
    .agents/skills/
scripts/
  validate_skills.py
```

`kits/core/` is the distributable unit. In HarnessKit, compose a kit from its `AGENTS.md` and the skill folders under `.agents/skills/`.

## Principles

- Keep persistent guidance short; load detailed workflows through skills.
- Inspect repository facts before locking implementation details.
- Work in complete, independently verifiable slices.
- Commit each verified slice by default; push, open a PR, or merge only when explicitly requested.
- Prefer focused evidence over ritual full-suite runs.
- Separate engineering-quality review from intent/spec review.
- Keep skills model-agnostic; model routing belongs in operator configuration, not workflow instructions.

## Validation

Run:

```sh
python3 scripts/validate_skills.py
```

The validator checks required frontmatter, folder/name consistency, duplicate names, and basic repository structure.
