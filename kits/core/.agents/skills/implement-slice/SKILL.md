---
name: implement-slice
description: Implement one approved vertical slice from a plan or issue, run focused checks, inspect the diff, and create a verified commit. Use only when scope and acceptance criteria are already clear.
---

# Implement Slice

Deliver exactly one accepted slice. Do not redesign the task while implementing it.

## Before editing

1. Read the applicable instructions, accepted plan or issue, and the current slice's acceptance criteria.
2. Inspect branch or change state and the working tree. For non-trivial work on a protected or shared default branch, create a feature branch according to repository convention before committing.
3. Identify unrelated edits and leave them untouched. If your files cannot be isolated safely, stop and report the conflict.
4. Confirm the intended test seam and the smallest useful check that can fail for this slice.

## Implement

1. Build the smallest complete path that satisfies the slice.
2. Follow existing domain language and repository patterns. Prefer a mature existing dependency over hand-rolling when it genuinely removes owned complexity.
3. Use `$tdd` when the user requested TDD, a regression needs to be pinned, or the behavior is risky enough to benefit from a red-green loop.
4. Run focused tests, type checks, or other owning checks while iterating rather than deferring all evidence to the end.
5. Update affected contracts, documentation, schemas, examples, and operational guidance in the same slice.
6. Avoid unrelated cleanup, speculative abstractions, compatibility shims without a requirement, and broad formatting churn.

## Decision gates

Stop and present evidence before making an unapproved change to a public API, wire or persisted format, database schema, security boundary, production dependency, compatibility promise, deployment topology, destructive operation, or accepted requirement.

## Verify and commit

1. Inspect the complete diff for scope creep, secrets, generated residue, and accidental edits.
2. Use `$verify-change`.
3. Do not commit while relevant evidence is failing.
4. Stage only files owned by this slice.
5. Create a commit by default after the slice passes. Use a message that states the delivered behavior.
6. Do not push, open a pull request, merge, force-push, or rewrite unrelated history unless explicitly requested.
7. If a durable plan exists, update its progress consistently with the repository's convention.

## Report

Return:

- delivered behavior;
- commit identifier or clearly described Jujutsu change;
- exact checks run and results;
- deviations from the accepted plan;
- unverified surfaces or residual risks;
- the next unblocked slice.
