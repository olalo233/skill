# Development workflow

Use Open GSD as the only workflow, planning, execution-state, and project-memory system. Do not create a parallel task, plan, spec, roadmap, handoff, or memory hierarchy.

## Choose one path

- For a small, clear change, use `/gsd-quick <task>`.
- Add `--discuss`, `--research`, or `--validate` only when that capability is actually needed. Do not silently promote quick work to `--full`.
- For a substantial project or feature, use the normal GSD lifecycle: discuss, plan, execute, review, verify, and ship.
- Use `$prototype` only to answer one explicit logic, state-model, or UI question with throwaway code.
- Use `$grilling` only when the user asks to stress-test an idea or the unresolved decisions justify it.

## Keep humans aligned

Use `$show-me` whenever the user asks what the agent changed, how the code or architecture works, how options differ, or what a proposed change will look like. Pick the smallest useful view; do not turn every explanation into a polished artifact.

## Keep the result lean

First make the requested behavior correct and verify it. Then run `$ponytail-review` as a separate complexity-only pass. Apply only findings that preserve requirements, safety, accessibility, and data integrity, and rerun the same checks afterward.

Before adding a mechanism, check the current repository, standard library, native platform, and installed dependencies. Do not reimplement a capability already supported by the stack.

## Preserve upstream behavior

Prefer the installed upstream skills and GSD commands over local wrappers. Do not invent new workflow stages, aliases, files, or fallback paths unless actual failed sessions show that the upstream behavior is insufficient.

The user's explicit requested artifact and deadline take precedence over optional process steps.
