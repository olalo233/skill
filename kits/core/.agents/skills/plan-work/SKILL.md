---
name: plan-work
description: Turn an approved goal, issue, or design into executable vertical slices with dependencies, acceptance criteria, verification, decision gates, and commit boundaries. Use for non-trivial work, not tiny edits.
---

# Plan Work

Create an implementation plan that a coding agent can execute one verified slice at a time without redefining the task.

## Inputs

Use the context already available: user decisions, issue or spec, repository instructions, and `$repo-scout` findings. Do not repeat an interview when the answers are already known.

## Process

1. Restate the implementation contract:
   - goal and observable outcome;
   - explicit non-goals;
   - constraints and accepted decisions;
   - unresolved decisions that genuinely block implementation.
2. Identify the highest stable seams where behavior can be verified. Prefer existing seams over introducing new ones.
3. Separate one-way or costly decisions from ordinary implementation details. Add a decision gate before the slice that would cross one.
4. Break the work into tracer-bullet vertical slices:
   - each slice delivers a narrow but complete behavior;
   - each slice is independently demonstrable or verifiable;
   - each slice fits a fresh agent context;
   - dependencies are explicit;
   - the end of each verified slice is a commit boundary.
5. For wide mechanical changes that cannot land green as vertical slices, use expand-migrate-contract:
   - expand with a compatible new form;
   - migrate callers in bounded batches;
   - contract only after all callers have moved.
6. Keep speculative cleanup out of the plan. Record it separately rather than hiding it inside delivery work.

## Slice format

For every slice include:

- **Outcome**
- **Blocked by**
- **Scope**
- **Acceptance criteria**
- **Verification**
- **Likely touchpoints** — guidance, not an immutable file list
- **Decision gates**
- **Commit intent**

## Persistence

Use an existing issue, plan, or task file when the repository already has one. Create a new durable plan only when the user requests it or the work clearly spans sessions; follow the repository convention, or use `.agents/work/<slug>.md` when no convention exists.

Do not modify production code while planning.
