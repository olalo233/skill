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
2. Locate the pinned source — index paths resolve against it:
   - `source.json` next to this `SKILL.md` (written into copied installs). It carries `commit` (full SHA), `source_path` (this skill's qualified repository path), `snapshot_root` (path relative to the project root of the immutable exported tree it was installed from), and `repo` (portable identity: upstream slug or remote URL; `local` means the clone has no remote). First verify `<snapshot_root>/.snapshot-complete` equals `commit`; if it does, read all skill bodies from `<snapshot_root>/<path>` — that tree cannot drift. If the snapshot is missing, resolve `repo` to a local clone through local config (never guess a machine path), verify the clone can reach `commit` (`git -C <clone> cat-file -e <commit>`), and only trust its worktree when `git -C <clone> rev-parse HEAD` equals `commit`; otherwise warn that the checkout has drifted. If the source cannot be resolved at all, say so and stop.
   - Otherwise the repository root is `../../` (this file sits at `skills/ask-me/` inside the clone, directly or through a symlink); `commit` is `git -C <repo> rev-parse HEAD`.
3. From the user's request, recommend 1–3 entries. For each: name, one-line summary, and its relative `path`. Then **stop and wait**; do not read skill bodies yet.
4. **"Use it here" / "就在这里用"**: read the chosen `SKILL.md` at the verified source root from step 2 (`<snapshot_root>/<path>` when the snapshot verified), plus every entry in its `depends` list. Dependencies only need to sit beside it as directories (`eli5` and `show-me` need the sibling `html` directory; do not read a dependency's body). Then follow the loaded instructions here. This is degraded use: argument substitution and the skill's own relative-path handling are not guaranteed; for full fidelity install instead.
5. **"Install into this project" / "装进项目"**: do not copy files yourself. Tell the user to run, with every substituted path quoted:
   `python3 "<repo>/scripts/install-base" --apply --project --source "<repo>" --ref "<commit>" --skill "<name-or-path>"`
   It copies the skill and its dependencies into `.agents/skills/` and links them from `.claude/skills/`. For a declared suite use `--suite "<name>"` instead of `--skill` (or the `bin/install-<suite>` wrappers). When a bare name is ambiguous across sources (e.g. `tdd` exists in both matt and pstack), use the full repository path shown by `--list`.
6. **"Uninstall / update a suite"**: `python3 "<repo>/scripts/install-base" --apply --project --uninstall "<suite>"` removes only skills no other owner needs; `--update --suite "<suite>" --ref "<commit>"` refreshes a suite and refuses to clobber local edits unless `--force` is given (edited copies are moved into the backup dir first).

## Notes

- `matt` and `pstack` suites live under `vendor/`; index paths point there.
- pstack is a Cursor-native plugin (subagents, sibling paths, automations). On Cursor, recommend enabling the native plugin rather than reading the vendored copy. Elsewhere the text still reads, but features degrade; say so when recommending.
- A skill that is not vendored yet appears in the index only once its files exist.
