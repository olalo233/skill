# Modifications to pbakaus/impeccable (derived copy)

Upstream: pbakaus/impeccable @ b4bff1626c344067788c2679f048a20057c7cc5a (Apache-2.0).
Verbatim upstream, including this NOTICE set, is vendored at `vendor/impeccable/`;
the upstream ledger lives at `vendor/impeccable/MODIFICATIONS.md`. This directory is
the adapted copy installed by the `ui-kit` suite; local adaptations survive upstream
syncs through three-way merge. Differences from upstream:

- Frontmatter gains `disable-model-invocation: true` and `triggers: [user]` (manual
  trigger only); `agents/openai.yaml` gains `policy.allow_implicit_invocation: false`.
- `scripts/` is not shipped: the `impeccable` launcher/binary, the detector, and the
  live-browser helpers are an optional extra, not part of the default install.
  Every step that invoked them is rewritten for a scriptless install:
  - Session context (`impeccable context`, `impeccable signals`) is read directly
    from PRODUCT.md, DESIGN.md, `.impeccable/` files, and the project tree.
  - The direction/structure rolls (`impeccable concept-seed`) are dealt by the
    agent itself: a stated, recorded arbitrary draw over the candidate list; the
    mode files carry the MODE RULES text directly.
  - The decision page (`impeccable serve-question`) becomes the harness's
    structured question tool, or a written card menu in chat.
  - Spec measurement (`impeccable comp-spec`, `impeccable font-match`) is
    hand-authored region mapping per `reference/region-map.md`; the schema and
    verification steps are documented inline.
  - Build phases (`impeccable build-phase`) are a checklist the agent maintains
    in `.impeccable/build/state.json`; each phase's exit conditions are stated
    in `reference/new-work.md`.
  - Fidelity comparison (`impeccable comp-diff`) is a manual region-by-region
    pass with verdicts recorded in `.impeccable/review/diff/*/report.md`.
  - The slop detector (`impeccable detect`) is the mechanical pass: reading
    markup/CSS against `reference/craft-floor.md`'s Refuse list.
  - Report persistence (`impeccable critique-storage`, `audit-storage`,
    `surface-brief`, `component-review`) is ordinary file I/O under
    `.impeccable/` with documented layouts.
  - Asset provenance (`impeccable embed-prompt`) is a `<file>.prompt.txt`
    sidecar or a `.impeccable/provenance.md` entry per raster.
  - Image generation (`impeccable generate-image`) uses only a harness-native
    image tool; without one, plates come from user-provided/sourced imagery or
    the build goes code-led. No API fallback is wired.
- Commands that require the removed pieces are dropped from the command table:
  `live`, `generate` (live browser), Pin/Unpin, Hooks, and Doctor. Their
  reference files (`live.md`, `live-setup.md`, `generate.md`, `hooks.md`,
  `doctor.md`) are removed, as are the live/`generate` lines in
  `reference/routing.md`. The `impeccable_manual_edit_applier` agent and
  `reference/degraded/manual-edit-applier.md` are removed: they existed solely
  for the live manual-edit flow.
- `critique` gains one rule: when a Kimi design export exists in the project,
  it is the ground truth and the surface is compared against it item by item.
- This directory ships `LICENSE` and `NOTICE.md` verbatim from upstream, as
  Apache-2.0 requires for derivative works.
