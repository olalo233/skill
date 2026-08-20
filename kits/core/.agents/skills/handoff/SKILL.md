---
name: handoff
description: Produce a compact, evidence-backed handoff for another agent, ChatGPT design review, or a later session using repository state, commits, diff, checks, decisions, and blockers.
---

# Handoff

Transport facts, not conversational memory.

## Gather

1. Repository and workspace root.
2. Branch or Jujutsu change, comparison base, current head, and working-tree state.
3. Originating issue, spec, plan, and accepted decisions.
4. Commit list and the actual changed areas.
5. Exact checks run, their results, and unverified surfaces.
6. Deviations from the plan, unresolved decisions, blockers, and known risks.

Do not say work is clean, tested, or complete unless repository evidence supports it.

## Handoff format

Use these headings:

- **Goal**
- **Non-goals and accepted decisions**
- **Repository state**
- **Completed work**
- **Commits and changed areas**
- **Verification evidence**
- **Deviations**
- **Open decisions and blockers**
- **Next exact action**
- **Resume commands or files to read**

For a ChatGPT design review, add:

- **Repository facts that affect the design**
- **Decision requested**
- **Options already considered**
- **Recommendation and uncertainty**

## Destination

Return the handoff in the conversation by default. Write a file only when requested or when the repository already requires durable handoffs. Follow the repository convention; otherwise use `.agents/handoff/<date>-<slug>.md`.

Keep it concise enough to read at session start, but include enough evidence that the receiving agent can verify every material claim.
