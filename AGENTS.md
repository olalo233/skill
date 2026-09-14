# Development workflow

Use Open GSD as the only workflow, requirements, planning, execution-state, and project-memory system. Do not create a parallel task, spec, roadmap, handoff, or memory hierarchy. Preserve the user's explicit scope, existing project constraints, and normal safety/authorization checks.

## Discussion and GSD share one conversation

- Use `grill-me` only when requested to clarify or challenge a plan. It invokes `grilling`; do not run two interviews.
- Bound the interview to the requested deliverable: target behavior, essential design choices, acceptance, exclusions, and important constraints. Already answered questions stay answered. The agent researches facts and chooses reversible implementation details within the agreed design.
- `show-me` and `prototype` can clarify a particular question. Neither starts a second workflow; a prototype is not a verified production MVP.
- When the user says to proceed with GSD, keep the current parent conversation. Invoke the applicable installed native GSD workflow, using the existing discussion as its input. Do not ask the user to rewrite it, require an intermediate PRD, restart the interview, or clear context first.
- Keep GSD's initialization, repository inspection, and approval checks. Only ask about genuinely missing or contradictory decisions; do not use an automatic mode merely to avoid repeat questions.
- Let GSD write accepted goals, scope, exclusions, constraints, design choices, and their rationale directly into its native project/requirements/phase-context files. Preserve exact identifiers and consequential user wording. Do not promote an agent suggestion to an accepted requirement.
- Check those files against the still-visible discussion before the first context reset. Resolve material discrepancies, not every sentence. This is a review of GSD's own artifacts, not another specification stage.
- After persistence, use GSD's normal fresh-context planning/execution. Subagents do not automatically inherit the whole conversation; provide the relevant native artifacts. Do not replay the full transcript into every worker.
- Record later scope changes through GSD's existing process. Never hide newly requested capabilities inside an old task.

## Execution and explanation

Use native GSD quick work for a small, clear change and its phase lifecycle for larger work. An MVP is not automatically a single quick task. Keep execution units small enough for implementation, real validation, and necessary repair in a fresh context.

Use `show-me` for the smallest helpful visual and `wait-what` to explain an unclear message in the requested language. Explanation is not permission to redesign or implement. Distinguish proposed designs, prototypes, and observed working behavior.

Correctness and requested behavior come first. Use `ponytail-review` only when requested or when the current change shows a concrete complexity problem; it is not a mandatory stage. Apply only reductions that preserve behavior, safety, accessibility, and data integrity, then rerun affected checks.

Prefer existing code, standard libraries, native platform capabilities, and installed dependencies. Do not modify GSD internals or add schedulers, routing agents, protocols, or workflow stages to integrate this suite.

## Installation boundary

The root AGENTS.md is not installed automatically by a skill-folder installer. When applying this policy to another project, merge it with the project's existing instructions; never overwrite its AGENTS.md or CLAUDE.md wholesale. Install GSD only with its official runtime installer. Keep only one active version of each suite skill per intended scope.
