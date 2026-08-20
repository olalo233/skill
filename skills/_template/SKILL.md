---
name: replace-me
description: Describe the concrete task this skill should be used for and the signals that should trigger it.
---

# Replace Me

## When to use

Use this skill when:

- the task clearly matches this skill's responsibility;
- the required inputs are available or can be discovered safely;
- using the skill is more reliable than applying generic agent behavior.

Do not use this skill when the task belongs to another, more specific skill.

## Goal

State the concrete outcome this skill is responsible for producing.

## Workflow

1. Inspect the relevant context and current state before changing anything.
2. Identify the smallest coherent plan that satisfies the task.
3. Execute the work using existing project conventions and mature tooling where possible.
4. Verify the result with the strongest practical checks available.
5. Report what changed, verification performed, and any remaining risks or follow-up work.

## Verification

At minimum, verify the parts directly affected by the change. Prefer project-native checks such as tests, linters, builds, type checks, rendered inspection, or targeted runtime validation.

Do not claim success when the relevant verification was skipped or failed; state the limitation explicitly.

## Output

Return a concise completion summary containing:

- what changed;
- what was verified;
- unresolved issues, assumptions, or risks that materially matter.
