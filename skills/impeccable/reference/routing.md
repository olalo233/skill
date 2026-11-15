<!-- Modified from pbakaus/impeccable (Apache-2.0) for this repository; see MODIFICATIONS.md. -->

# Command guidance

## Workflow questions

Give advice without executing commands; the menu below is only for bare invocations. Consult relevant command references as needed for prerequisites and scope. If the user also requests execution, follow that request.

## No-argument routing: the context-aware menu

Read this when the user invokes `$impeccable` with no argument. They are asking "what should I do?" Make the menu context-aware instead of static.

Setup has already read the project context. If PRODUCT.md is missing, the project has no captured context yet: lead the menu with `$impeccable init` as the top recommendation (one line on why) and still show the rest below; don't silently jump into init. Otherwise, gather the signals below from the project files yourself, then lead with the **2-3 highest-value next commands**, each with a one-line reason pulled from the signals, followed by the full menu (the Commands table in SKILL.md, grouped by category). **Never auto-run a command; the recommendation is a suggestion the user confirms.**

Read the signals from the files; there is no score to obey:

- DESIGN.md absent while real UI code exists → `document` (capture the visual system).
- No `.impeccable/critique/` snapshots → the project has never been critiqued; for a set-up project with a real surface, offering `$impeccable critique <surface>` is a strong default.
- The latest critique snapshot's frontmatter has a low `total_score` or non-zero `p0` / `p1` → `polish` (it reads that snapshot as its backlog and closes it when stale or cleared).
- Recently changed files (the project's own change list, e.g. `git status` where the harness permits it) pointing at one surface → scope `audit` or `polish` to those files specifically, naming them.
- Otherwise group by intent (build new / improve what's there), tailored to the current surface and platform.

**Where the changed-file list names markup or style files and the platform is not `ios`/`android`/`adaptive`, run the mechanical pass on them once** (read the files against [craft-floor.md](craft-floor.md)'s Refuse list and source-checkable Verify items: no extra tooling, just reading the local files; skip it for native projects). Fold the hits into your picks: many quality / contrast hits → `audit` or `polish`; a specific slop family → the matching command (gradient text or eyebrows → `quieter` / `typeset`, flat or gray palette → `colorize`, and so on). It's a real, current signal that beats guessing. If the tree is large, skim the highest-churn files and recommend the user run `audit` themselves; never block the suggestion on it.

Keep it to 2-3 pointed picks with the exact command to type. The menu stays the fallback; the recommendation is the lede.
