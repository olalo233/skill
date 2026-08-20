---
name: repo-scout
description: Map an unfamiliar repository or inspect the implementation area before planning a non-trivial or architecture-sensitive change. Produce evidence and decision questions without modifying files.
---

# Repository Scout

Build the smallest evidence-backed map needed to make the next design or implementation decision safely.

## Rules

- This is a read-only workflow. Do not edit files, install dependencies, create commits, or alter repository state.
- Do not map the entire repository. Follow the task's likely execution path and stop when the important facts are established.
- Cite repository evidence with paths and symbols. Distinguish facts from inferences.
- Preserve and report any dirty working-tree state you find.

## Process

1. Establish the repository root, current branch or change, working-tree state, and applicable instruction files.
2. Read the minimum setup and architecture material needed: root README, manifests, build and test configuration, relevant ADRs, and the nearest applicable `AGENTS.md`.
3. Trace the task's path through the system:
   - entry point or caller;
   - domain or state owner;
   - persistence, network, process, or other side effects;
   - current tests and operational evidence.
4. Search for nearby implementations that solve a similar problem. Name reusable seams and conventions instead of proposing parallel abstractions.
5. Identify:
   - assumptions confirmed or disproved;
   - likely blast radius;
   - compatibility, migration, lifecycle, concurrency, or security concerns;
   - questions that require a product or architecture decision.
6. Recommend the next workflow: direct implementation, `$plan-work`, `$diagnose-bug`, a prototype, or escalation to a long-running project harness.

## Output

Use these headings:

- **Repository state**
- **Relevant flow**
- **Existing seams and prior art**
- **Constraints**
- **Risks and unknowns**
- **Decision questions**
- **Recommended next step**

Do not turn the report into a detailed file-by-file implementation plan unless the user explicitly asks for one.
