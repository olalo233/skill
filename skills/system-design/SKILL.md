---
name: system-design
description: "Design a system from a vague brief to a justified architecture: clarify requirements, estimate scale, lay out components with a C4 Mermaid diagram, weigh trade-offs. Use when asked for system design or high-level architecture. Stops at component boundaries; internals belong to codebase-design."
disable-model-invocation: true
triggers:
  - user
---

# System Design

Drive a vague "design X" brief to a justified, written-down architecture —
by reasoning, not by recalling a diagram. Method distilled from
proyecto26/system-design-skills (MIT license, vendor/system-design), reduced to
the reasoning loop and stripped of its building-block plugin and orchestrator
plumbing.

> There is no single correct design. An architecture is a *hypothesis* that
> holds until a constraint changes; a design right for 1k users may fail at 1M.
> The deliverable is the reasoning: requirements, numbers, components,
> trade-offs.

## The loop

Work it out loud; it is a loop, not a checklist — later steps routinely send
you back.

1. **Clarify** — turn the brief into functional requirements, non-functional
   constraints, and an explicit *out of scope*. Scope to a few core features
   and say so. When an answer changes the design, do not guess: call the
   Skill tool with "grilling" and let the interview close the frontier.
2. **Estimate** — back-of-the-envelope QPS, storage, bandwidth, read/write
   ratio. Numbers decide the design; "high traffic" does not. Order-of-magnitude
   reference points: `references/estimation.md`.
3. **Propose components** — the boxes and arrows: clients, gateway, services,
   stores, caches, queues, plus the user-facing API shape. Get buy-in on the
   high-level layout before going deeper. Draw it as a C4 diagram in Mermaid;
   conventions and an example: `references/diagramming.md`.
4. **Weigh trade-offs** — for every major choice state what it *solves*, what
   it *worsens*, and *when you would change it*. Never name a tool without
   these three columns.
5. **Stress-test** — find single points of failure, decide the degradation
   story, plan recovery. Assume every component breaks.
6. **Iterate** — let new constraints ("writes 10x?", "lose a region?") drive a
   redesign of the affected part only.

## Boundaries

- **Stops at component boundaries.** How a module is cut internally — its
  depth, seams, interface shape — is `codebase-design`'s vocabulary; do not
  deep-dive module internals here.
- **Decisions get recorded.** When a choice settles into an architectural
  decision, call the Skill tool with "domain-modeling" so it is written as an
  ADR (and new terms into the glossary). Do not leave decisions only in the
  conversation or the design doc.
- **External contracts** — once components are placed, endpoint/event/schema
  design and versioning policy belong to `api-and-interface-design`.

## Guardrails (the ways designs fail)

- Clarify before designing; rushing signals memorization.
- Quantify before choosing; convert "heavy traffic" into numbers first.
- Justify every component: solves / worsens / change-it-when. "Industry
  standard" is not a justification.
- Design for failure; "add more retries" usually amplifies an outage.
- Make interfaces concrete: if you cannot write the request, response, and
  primary key, the diagram is guesswork.

## Producing the answer

- **Diagrams**: C4 in Mermaid — a Context view (system vs. actors and external
  systems) and a Container view (deployable units and their protocols).
  Zoom deeper only for the fragile component, not the whole map.
- **Decisions table** — one row per major choice (at least three for a full
  design): `Decision | Solves | Worsens | Change it when…`. The last column is
  a concrete trigger (a number or observable signal), never "if needed".
- **Weakest-point line** — end with the part of this design that breaks first
  as load or requirements grow, and the move you would make then.
- **Persist** the settled artifacts — scope, design doc, decisions table,
  diagram — to `docs/design/<system>.md` (ask where if unsure); keep open
  exploration in the conversation. Recorded decisions then go to
  `domain-modeling` for ADRs.
