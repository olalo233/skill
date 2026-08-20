---
name: simplify-change
description: Find evidence-backed simplifications in a diff or code area by removing dead, duplicated, speculative, overbuilt, or hand-rolled surfaces without changing required behavior.
---

# Simplify Change

Prefer a few proven simplifications over a long list of aesthetic opinions.

## Establish authority

Read the applicable contracts, consumers, tests, documentation, ADRs, and repository rules before judging complexity. Do not delete an intentional seam merely because its value is not obvious locally.

## Find candidates

Strong candidates include:

- public or internal surfaces with no production consumer;
- tests or documentation as the only consumer of behavior that is not a maintained contract;
- two representations of the same fact;
- duplicated lifecycle or state machinery;
- speculative options, hooks, registries, compatibility paths, or abstractions with no current owner;
- a package or layer that only delegates and adds no policy;
- hand-rolled infrastructure that a maintained dependency or standard library can replace with net deletion;
- behavior added and later removed while support artifacts remain.

Formatting changes, vague "this looks complex" reactions, and tiny dead-code findings are not enough for a broad simplification proposal.

## Prove each candidate

1. Search exact symbols, call sites, configuration keys, wire values, and runtime registration paths.
2. Classify consumers as production, test/documentation, or ambiguous; inspect ambiguous uses.
3. Check architecture decisions and compatibility obligations.
4. Estimate net deletion, migration cost, behavior change, and verification needed.
5. Reject or downgrade the candidate when evidence does not beat the existing rationale.

## Apply only when requested

When the user asks to implement simplifications:

- make one independently verifiable simplification at a time;
- preserve required behavior;
- update tests and documentation that own the removed surface;
- run `$verify-change`;
- commit the verified simplification as its own checkpoint when it is independent of delivery work.

## Output

For each retained candidate state:

- current cost;
- production-consumer evidence;
- proposed deletion or collapse;
- behavior or capability given up;
- risk;
- verification plan.

Also list representative candidates you rejected and why.
