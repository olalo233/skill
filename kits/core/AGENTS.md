# Engineering Core

These rules supplement the repository's own instructions. More specific repository or directory guidance wins.

## Start with facts

- Read the applicable `AGENTS.md` chain and the repository's setup, architecture, and contribution documentation before editing.
- Preserve unrelated working-tree changes. Never overwrite, stage, or commit work you do not own.
- Use existing domain language, patterns, and mature dependencies before inventing new abstractions.
- For unfamiliar or architecture-sensitive areas, use `$repo-scout` before locking an implementation plan.

## Route the work

- Small, clear, reversible work: implement directly and verify it.
- Unknown-cause bugs, failures, incidents, or regressions: use `$diagnose-bug` before changing code.
- Work with multiple independently deliverable behaviors: use `$plan-work`, then execute one slice at a time with `$implement-slice`.
- Long-running, multi-phase work with durable state, dependency waves, or formal UAT: use the project's dedicated workflow, such as GSD, rather than expanding this kit into a project manager.

## Execute in slices

- Prefer the smallest complete vertical slice that produces observable value.
- Test behavior at the highest stable seam available. Do not test implementation details merely to increase coverage.
- Avoid speculative generality, broad cleanup, and unrelated refactors while delivering a slice.
- Update affected contracts, documentation, schemas, examples, and operational notes with the behavior they describe.
- If the task's accepted intent conflicts with repository facts, stop and surface the conflict instead of silently redefining the task.

## Version-control checkpoints

- A verified slice is a version-control checkpoint. In Git, commit it by default; in Jujutsu, create and clearly describe an equivalent isolated change.
- For non-trivial work, do not commit directly to a protected or shared default branch. Create a feature branch according to repository convention unless the user explicitly authorizes direct work.
- Stage only files belonging to the slice. Do not use blanket staging in a mixed worktree.
- Do not commit failing work, secrets, generated residue, or unrelated edits.
- Keep useful intermediate commits on feature branches. Squash or otherwise rewrite history only at the integration boundary and according to repository policy.
- Do not push, force-push, open or update a pull request, merge, or rewrite another person's commits unless the user explicitly requests that action.

## Decision gates

Pause implementation and present evidence when the work requires an unapproved change to:

- a public API, wire format, persisted data format, or database schema;
- authentication, authorization, privacy, or another security boundary;
- a production dependency, framework, deployment topology, or compatibility promise;
- an irreversible migration, destructive operation, or broad refactor outside the accepted scope;
- the task's goal, non-goals, acceptance criteria, or externally visible behavior.

Use `$handoff` when the decision should move to ChatGPT, another agent, or a later session.

## Finish with evidence

- Use `$verify-change` before claiming completion or preparing to publish.
- Use `$review-change` for an independent review against both engineering standards and intended behavior.
- Report exact checks run, commits created, deviations from the accepted plan, unverified surfaces, and residual risks.
