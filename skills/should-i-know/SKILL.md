---
name: should-i-know
description: "On explicit request, debrief the user on what they must decide, material actions and judgment calls, and what is unverified: quick from context by default, or a deep audit of the conversation's record when asked."
disable-model-invocation: true
triggers:
  - user
---

Run this only when the user explicitly asks for a debrief or invokes should-i-know. A routine end-of-task report is not a trigger. Do not continue the task, undo anything, or start new work.

## Two depths

**Quick (default).** Answer from what is already in your context. Run no tools. Open with one line saying it is from context, not audited. Use the three headings under "What to report" and the same materiality threshold. For a material item, state the consequence briefly and flag any permission or scope deviation. Evidence pointers, formal authorization labels, alternatives, and recovery details are required only in Deep.

Do not skip known hard-to-reverse or external actions, actual charges, or anything still running or billing. Say "not apparent from context", never "none". Report known attempts whose outcome is unknown, especially if they may have caused an external effect or a charge.

**Deep.** Use when the user asks for it (for example "deep", "strict", "严格", "仔细"). Follow every section below.

## Gather from the record, not from memory (Deep)

Walk back through this conversation's actual actions in order: tool calls and their results, files written or edited, commands run, messages sent, delegated or spawned agents and what they returned. Your own earlier summaries are claims to check, not evidence.

Use the visible record first. Check current state only when the check is within the user's scope, read-only, and has no side effects; otherwise mark the point unverified. Never open credential-bearing files or reproduce secrets; cite a sanitized location or action instead.

Part of the record may be missing: summarized or truncated history, a delegated agent that returned only a summary, a tool call that timed out. A missing record is not evidence that nothing happened. A failed or timed-out call does not prove the other side did nothing. Distinguish requested, attempted, and confirmed actions, and write "outcome unknown" when that is the truth.

## What to report

Three sections, always all three. In Deep, when a section is empty, write "None found in the reviewed record." If a gap in the record could change that answer, name the gap in that section.

**1. Needs you** — what blocks progress or must not proceed without the user: missing authorization, information only the user has, a choice the agent should not make alone. For each: what is needed, why, and a recommendation where one exists. For credentials, name the approved secure channel; never ask for the value in chat. Do not put optional suggestions here.

**2. Material actions, consequences, and judgment calls** — include an item if any of these hold:
- Hard to reverse or outward-facing: pushed, deleted, published, sent, changed a system outside the working repository, created a scheduled job, background service or persistent process.
- Real cost: a charge already incurred, ongoing billing, scarce quota, or clearly over budget. Ordinary calls within a subscription are not listed one by one.
- Departed from the user's authorization or scope, including attempts that failed and "while I was at it" changes.
- Chose between reasonable options where the user might have chosen differently.
- Introduced risk: broadened permissions, reused or exposed a credential, unattended behavior, effects on other threads, machines or people.
- Worked around a rule, a failed check, or a blocked tool instead of stopping.
- Ended in an unexpected or partial state: something still running, still billing, half-applied, or not rolled back.

In Deep, label each item: explicitly authorized by the user; decided by the agent within its authority; or should have been asked first and was not. If the record cannot establish authorization, write "authorization unknown". If it shows prior authorization was required and not obtained, say so plainly.

In Deep, lead each item with the consequence and a sanitized evidence pointer. For a choice, give the main alternative and the cost of switching now. For an action, give its current effect and any realistic recovery; if it cannot be undone, say so. If the rationale is not in the record, say so instead of supplying one.

**3. Unverified** — what was not tested or observed, which assumptions the result rests on, and what would confirm them. Separate "checked statically", "ran locally" and "observed in production" when relevant.

At the end of section 3, in either depth: if known history was summarized or truncated, a delegated agent took external actions or its summary is not enough to judge a material consequence, or production, credentials or actual charges are involved, give the reason and recommend Deep (when in Quick) or name what remains unknown (when in Deep). Do not escalate on your own.

## Threshold

Judge by consequence, not by count. Leave out routine choices with no material consequence (naming, formatting, ordering, which equivalent command was used). Never omit a permission or scope deviation because it was cheap. Similar items may be grouped, but keep the exceptions and the total effect.

## Form

Use the user's conversational language. If the user asked for a specific output format, express the same substance inside it. After any Quick scope note, start with section 1. Keep items brief. Do not repeat the full change log; point to it if one exists. End after section 3: no offers, no "shall I continue".
