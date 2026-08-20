---
name: review-change
description: Review a branch, pull request, or diff against both repository engineering standards and the intended spec. Report correctness-first findings with locations, impact, and evidence.
---

# Review Change

Review from a fixed comparison point and keep engineering quality separate from intent compliance.

## Establish the review

1. Resolve the exact base and head. Prefer a merge-base comparison for a feature branch.
2. Capture the commit list and complete diff. Include relevant uncommitted changes only when the user asks.
3. Read the applicable `AGENTS.md`, contribution rules, architecture decisions, and testing policy.
4. Locate the originating issue, spec, accepted plan, or user request. If none exists, state that the intent axis is limited.

## Run two independent passes

Use parallel subagents when available. Otherwise perform two sequential passes and do not let conclusions from one substitute for the other.

### Engineering pass

Prioritize:

- correctness and broken required behavior;
- ownership, lifecycle, concurrency, cancellation, and cleanup;
- error handling and observability;
- data integrity, migration, compatibility, and rollback;
- authentication, authorization, privacy, and trust boundaries;
- public API and consumer impact;
- test strength and missing negative controls;
- duplicated, speculative, overbuilt, or hand-rolled complexity.

Repository rules override generic preferences. Omit formatting and lint issues already enforced by tooling.

### Intent pass

Check for:

- missing or partial requirements;
- behavior that contradicts the spec;
- scope creep and unrequested public surface;
- accepted decisions that were silently changed;
- acceptance criteria that appear implemented but are not actually proven.

## Findings

For each finding provide:

- severity: blocker, major, or minor;
- tight location: file and line or diff hunk;
- defect;
- user or system impact;
- evidence;
- safe correction direction.

Do not inflate the report with weak guesses or style nits. A short review with one substantiated blocker is better than a long list of noise.

## Output

Keep separate headings:

- **Engineering**
- **Intent / Spec**
- **Evidence gaps**
- **Summary**

Do not fix findings during a review unless the user separately asks for changes.
