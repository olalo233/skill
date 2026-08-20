---
name: verify-change
description: Select and run the smallest credible evidence for the current diff before committing, pushing, or claiming completion. Expand checks by affected behavior, not by ritual.
---

# Verify Change

Match evidence to the outgoing change. A green unrelated suite is not proof.

## Inspect scope

1. Establish repository root, branch or change, working-tree state, and the intended comparison base.
2. Inspect committed and uncommitted changes, including generated files and configuration.
3. List the externally observable behaviors and contracts the diff can affect.

## Select evidence

Choose the narrowest owning evidence for each affected surface:

- behavior change: focused unit, integration, or end-to-end test at the owning seam;
- bug fix: original reproduction plus a regression test or equivalent negative control;
- type or API contract: typecheck, schema validation, compatibility test, or consumer build;
- database or persisted format: migration test, forward and rollback reasoning, and representative data;
- CLI, model-visible, or user-visible output: snapshot or runnable scenario that owns the output;
- documentation or generated catalogs: the repository's documentation and link gates;
- package, build, export, worker, or executable entry point: build plus a real artifact smoke test;
- frontend behavior: browser check, console check, and representative responsive or accessibility evidence when tools are available;
- operational configuration: parser or loader check and a safe dry run where possible.

Start focused. Expand to package or repository-wide checks only when the changed contract is shared, the focused evidence reveals wider risk, or repository policy requires it.

## Rules

- Record exact commands and results.
- Do not rerun a passing check merely because commit or push follows.
- Do not use `--passWithNoTests`, reduced thresholds, disabled gates, or broad ignores to manufacture success.
- Distinguish an environment failure from a product failure with evidence.
- If no meaningful automated check exists, use the strongest manual or static evidence available and state the gap.
- Do not claim an unrun check passed.

## Output

Report:

- comparison base and affected surfaces;
- checks run and results;
- failures and diagnosis;
- unverified surfaces;
- whether the change is ready to commit, publish, or review.
