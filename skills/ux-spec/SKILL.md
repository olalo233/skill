---
name: ux-spec
description: "Write a UX specification — user journeys, page inventory, state matrix, interaction and copy details — into docs/ux/. Does not set visual style: the output is the input for external design work (e.g. Kimi) and the acceptance baseline for the ui-kit suite."
disable-model-invocation: true
triggers:
  - user
---

# UX Spec

Turn a settled spec or discussed feature into the UX document a visual designer
(or design agent) can build screens from. Structure and method distilled from
`bmad-ux` in bmad-code-org/BMAD-METHOD (MIT license,
vendor/bmad/skills/bmad-ux), reduced to the parts that run without the BMAD
framework: no scripts, no registry, no memlog.

**Capture; do not decorate.** This skill specifies *how the product works*: the
screens, the states, the words. It never specifies *how it looks*: color, type,
spacing, and component styling are decided downstream by the design tool
(e.g. Kimi) against the project design system. The document you produce is the
Kimi design input and the baseline `ui-kit`'s `impeccable` critiques against.

## Before writing

Open questions about users, scope, flows, or priorities belong to the interview,
not to guesses in the spec. When a question's answer changes the UX, call the
Skill tool with "grilling" and resolve it first. When a UX decision becomes an
architecture or vocabulary decision (a new domain term, a cross-cutting state
rule), call the Skill tool with "domain-modeling" so it lands in the glossary
or an ADR — do not bury architectural decisions in UX prose.

## Output

Write to `docs/ux/<slug>.md` (one file per feature or product; split into
`docs/ux/<slug>/` when several surfaces need separate specs). Four sections:

1. **User journeys** — named-protagonist narratives ("Mary, a returning admin,
   at 11pm"), numbered steps ending in a climax beat (the moment of value).
   One journey per core task; edge journeys only when they change the design.
2. **Page inventory** — every screen/state surface the journeys touch, as a
   table: `Page | Purpose | Journey step | Primary action | Data needed`.
   The inventory closes when every stated need has a surface and every surface
   sits on a journey.
3. **State matrix** — for each page or key component: the states it can be in
   (empty, loading, populated, error, permission-denied, edge variants) and
   what the user sees and can do in each.
4. **Interactions & copy** — the behavioral contract: inputs, validation rules,
   error text, empty-state text, calls to action, confirmations for
   destructive actions, keyboard/focus expectations. Write real copy, not
   placeholders.

Mark anything unconfirmed `[ASSUMPTION: ...]`; an assumption in the spec is a
question you owe grilling, not a decision.

## Boundaries

- No visual decisions: never name colors, fonts, radii, or layout grids beyond
  what the interaction requires ("primary action is visually dominant" is fine;
  "blue button, top right" is not).
- No architecture: component internals, data models, and service boundaries
  belong to `system-design` and `codebase-design`; ADRs belong to
  `domain-modeling`.
- No tickets: breaking the work down belongs to `to-tickets`.

## Done when

Every journey step lands on an inventoried page, every page's states are
enumerated, destructive and irreversible actions have explicit copy, and the
remaining `[ASSUMPTION]` list is stated at the top for the next grilling round.
