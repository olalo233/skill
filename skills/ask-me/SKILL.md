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
   - `source.json` next to this `SKILL.md` (written into both project and user installs). It carries `commit` (full SHA), `source_path` (this skill's qualified repository path), `snapshot_root` (path relative to the install parent/project root of the exported tree it was installed from), `repo` (portable identity: upstream slug or remote URL; `local` means the clone has no remote), `skill_digests` (per-skill tree sha256), and `file_digests` (per-file sha256 of every indexed skill file at `commit`). `<snapshot_root>/.snapshot-complete` equal to `commit` only marks that the export finished; it does NOT prove file contents — the snapshot is a writable directory. Before reading any `<snapshot_root>/<path>`, verify it: the file's sha256 must equal `file_digests[path]` (or run `python3 <repo>/scripts/install-base --verify-source <this skill's dir>` once to check the whole snapshot, including the marker). A mismatch means the snapshot was tampered with: warn, do not read it, and fall back. Fallback when the snapshot is missing or fails verification: resolve `repo` to a local clone through local config (never guess a machine path) and require `git -C <clone> cat-file -e <commit>` to succeed. Then read skill bodies straight from the pinned commit object (`git -C <clone> show <commit>:<path>`); a worktree file may only be used after its blob hash is verified against the commit (e.g. `git -C <clone> ls-tree <commit> -- <path>` vs `git -C <clone> hash-object <worktree-path>`). Never trust a writable worktree just because `git -C <clone> rev-parse HEAD` equals `commit` — uncommitted edits sit at the same HEAD. If the source cannot be resolved at all, say so and stop.
   - Otherwise the repository root is `../../` (this file sits at `skills/ask-me/` inside a clone, where `../../.git` exists); `commit` is `git -C <repo> rev-parse HEAD`. Read skill bodies from `git -C <repo> show <commit>:<path>` (or verify `git -C <repo> hash-object` matches `git -C <repo> ls-tree <commit> -- <path>`) — never trust uncommitted worktree edits at `HEAD`.
3. From the user's request, recommend 1–3 entries. For each: name, one-line summary, and its relative `path`. Then **stop and wait**; do not read skill bodies yet.
4. **"Use it here" / "就在这里用"**: read the chosen `SKILL.md` at the verified source root from step 2 (`<snapshot_root>/<path>` only after its `file_digests` sha256 checks out; `git -C <clone> show <commit>:<path>` on the clone fallback — never a worktree file taken on faith), plus every entry in its `depends` list. Dependencies only need to sit beside it as directories (`eli5` and `show-me` need the sibling `html` directory; do not read a dependency's body). Then follow the loaded instructions here. This is degraded use: argument substitution and the skill's own relative-path handling are not guaranteed; for full fidelity install instead.
5. **"Install into this project" / "装进项目"**: do not copy files yourself. Tell the user to run, with every substituted path quoted:
   `python3 "<repo>/scripts/install-base" --apply --project --source "<repo>" --ref "<commit>" --skill "<name-or-path>"`
   It copies the skill and its dependencies into `.agents/skills/` and links them from `.claude/skills/`. For a declared suite use `--suite "<name>"` instead of `--skill` (or the `bin/install-<suite>` wrappers). When a bare name is ambiguous across sources (e.g. `tdd` exists in both matt and pstack), use the full repository path shown by `--list`.
6. **"Uninstall / update a suite"**: `python3 "<repo>/scripts/install-base" --apply --project --uninstall "<suite>"` removes only skills no other owner needs; `--update --suite "<suite>" --ref "<commit>"` refreshes a suite and refuses to clobber local edits unless `--force` is given (edited copies are moved into the backup dir first).

## Which suite for what task

- `design` — turning a vague idea into decided work: clarify (grill-with-docs), spec (to-spec), UX spec into docs/ux/ (ux-spec), system design (system-design), interface contracts (api-and-interface-design), tickets (to-tickets). Includes the `matt-plan` sub-suite; install with `bin/install-design`.
- `matt-dev` — implementing the tickets: implement, tdd, code-review, diagnosing-bugs, matt-flow. Includes `matt-plan`, so members shared with `design` land only once and survive either suite's uninstall; install with `bin/install-matt-dev`.
- `matt-plan` — the shared planning half alone (clarify/spec/tickets and their primitives). Rarely the right choice on its own; prefer `design` or `matt-dev`.
- `ui-kit` — visual direction and prototypes: impeccable (PRODUCT.md/DESIGN.md, critique/audit; the detector CLI is an optional extra) and prototype. dataviz is pending source verification. Install with `bin/install-ui-kit`.
- `pstack` — a Cursor-native plugin vendored whole (subagents, sibling paths, automations). On Cursor, recommend enabling the native plugin rather than reading the vendored copy. Elsewhere the text still reads, but features degrade; say so when recommending.

## Notes

- `matt` and `pstack` suites live under `vendor/`; index paths point there.
- A skill that is not vendored yet appears in the index only once its files exist.
