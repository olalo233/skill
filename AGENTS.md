# AGENTS.md

This repository contains reusable agent skills and related instructions.

## Working rules

- Keep skills focused, composable, and easy to review.
- Prefer mature external tools and established conventions over bespoke frameworks.
- Do not introduce harness-specific lock-in unless the benefit is explicit and documented.
- Treat `skills/<name>/SKILL.md` as the primary skill source format.
- A skill should state when it applies, what it does, what it must verify, and what it should return.
- Avoid copying large generic instruction sets into every skill; factor shared guidance only when repetition becomes real.
- Preserve compatibility with Codex first, while keeping instructions usable by other coding-agent harnesses when practical.

## Change discipline

- Make the smallest coherent change that solves the problem.
- Verify changed paths before committing.
- Prefer feature branches and squash merge into `main`.
- Do not commit generated archives, local caches, credentials, or editor state.

## Skill quality bar

A useful skill should be:

1. Triggerable: its intended use is obvious.
2. Operational: it gives concrete steps, not only principles.
3. Verifiable: success/failure can be checked.
4. Bounded: it has a clear responsibility and avoids becoming a universal agent prompt.
5. Portable: it minimizes assumptions about one model or one harness unless those assumptions are necessary.
