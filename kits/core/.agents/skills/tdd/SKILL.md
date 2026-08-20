---
name: tdd
description: Develop a behavior through a red-green-refactor loop at an agreed stable seam. Use when TDD is requested or a risky behavior needs an executable contract; do not test implementation details.
---

# Test-Driven Development

Use a tight red-green-refactor loop to establish behavior, not to maximize test count.

## Choose the seam

- Prefer the highest stable seam that exposes the behavior to a real consumer.
- Reuse an existing seam when possible.
- Avoid adding interfaces solely to make private implementation easy to mock.
- For legacy behavior, characterize the current contract before changing it.

## Loop

1. **Red**
   - Write the smallest test that expresses one missing behavior.
   - Run the focused test.
   - Confirm it fails for the intended reason, not from setup, syntax, or an unrelated defect.
2. **Green**
   - Implement the smallest production change that makes the test pass.
   - Run the focused test and the nearest relevant checks.
3. **Refactor**
   - Improve names and structure only while the suite remains green.
   - Remove duplication or awkwardness revealed by the new behavior; do not expand scope.
4. Repeat for the next behavior.

## Test quality

- Assert observable outcomes, state, events, errors, or side effects.
- Use real collaborators at the chosen seam when practical. Mock external boundaries, not the code under test.
- Prefer deterministic inputs and explicit clocks, IDs, randomness, and concurrency control.
- Use snapshots only when the serialized or visible output is itself a maintained contract.
- Include negative controls and edge cases that would fail on the intended regression.
- Do not weaken assertions, lower thresholds, skip tests, or add sleeps merely to obtain green output.

Report the seam chosen, red evidence, implementation step, and final commands run.
