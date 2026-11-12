---
name: ask-me
description: "Use when the user asks which skill fits a task, or invokes /ask-me to pick and load a skill from this repository's index."
disable-model-invocation: true
triggers:
  - user
---

# ask-me

Route to skills through this repository's index. Recommend only; never install or load anything on your own.

1. Read the index, resolving in this order:
   - `index.json` next to this `SKILL.md` (installed copies carry it),
   - `../index.json` (a copy placed at the install root),
   - `../../index.json` (running from a clone, at `skills/ask-me/`).
   If none exists, say the index is missing and stop.
2. From the user's request, recommend 1–3 entries. For each: name, one-line summary, and its relative `path`. Then **stop and wait**; do not read skill bodies yet.
3. **"Use it here" / "就在这里用"**: read the chosen `SKILL.md` at its indexed path under the repository root, plus every entry in its `depends` list. Dependencies only need to sit beside it as directories (`eli5` and `show-me` need the sibling `html` directory; do not read a dependency's body). Then follow the loaded instructions here. This is degraded use: argument substitution and the skill's own relative-path handling are not guaranteed; for full fidelity install instead.
4. **"Install into this project" / "装进项目"**: do not copy files yourself. Tell the user to run:
   `python3 <path-to-this-repo>/scripts/install-base --apply --project --skill <name>`
   It copies the skill and its dependencies into `.agents/skills/` and `.claude/skills/`.

## Notes

- `matt` and `pstack` suites live under `vendor/`; index paths point there.
- pstack is a Cursor-native plugin (subagents, sibling paths, automations). On Cursor, recommend enabling the native plugin rather than reading the vendored copy. Elsewhere the text still reads, but features degrade; say so when recommending.
- A skill that is not vendored yet appears in the index only once its files exist.
