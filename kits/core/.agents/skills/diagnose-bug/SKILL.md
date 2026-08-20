---
name: diagnose-bug
description: Diagnose a bug, failing test, incident, flaky behavior, or performance regression from evidence before changing code. Use when the root cause is unknown; avoid speculative fixes.
---

# Diagnose Bug

Find and prove the root cause before broadening the change.

## Process

1. Define the symptom precisely:
   - observed behavior;
   - expected behavior;
   - impact and scope;
   - reproduction conditions;
   - first known good or bad state when available.
2. Preserve evidence before changing the system: logs, error output, traces, metrics, failing inputs, configuration, and relevant versions.
3. Reproduce at the smallest credible seam. If reproduction is not possible, say what evidence substitutes for it.
4. Build a short ranked hypothesis list. For each hypothesis, name the observation that would distinguish it from the others.
5. Run the cheapest discriminating checks first. Trace the symptom to the component that owns the broken state or contract.
6. Inspect recent changes and adjacent code only after the failure path is understood; do not equate correlation with cause.
7. When feasible, add a regression test that fails for the demonstrated bug at the highest stable behavioral seam.
8. Apply the smallest fix that addresses the root cause. Do not hide the symptom with retries, fallbacks, sleeps, broader exception handling, or disabled checks unless that is the actual contract.
9. Verify:
   - the original reproduction now passes;
   - the regression test fails without the fix and passes with it;
   - relevant neighboring behavior still works;
   - production-safe rollback or mitigation is clear when applicable.

## Safety

Do not run destructive production operations, delete evidence, rotate credentials, or change live data without explicit authorization.

## Report

Separate:

- **Root cause**
- **Evidence**
- **Fix**
- **Verification**
- **Residual risk or follow-up**

If the evidence is insufficient, report the leading hypotheses and the next discriminating test instead of presenting a guess as a diagnosis.
