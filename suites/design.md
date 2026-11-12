# design suite — placeholder, no members yet

Deliberately not implemented. Per the install-base review, the skills
that would form a design suite are not vendored in this repository yet
(`brainstorming`, `adr`, `project-design-dossier`, `repo-eval`), and
several candidates still need source and license review before their
paths can be pinned in a suite file. `domain-modeling` has clear
dependency value and already ships inside `matt-dev` as a shared
sibling; whether it is promoted to a standalone design member stays open.

When the members land, `suites/design.json` will list them with explicit
paths and the dependency closure parsed from their SKILL.md references,
exactly like `suites/matt-dev.json`. Until then `--suite design` fails
with "no suite 'design' in source".
