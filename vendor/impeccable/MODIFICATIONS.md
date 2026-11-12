# Modifications to pbakaus/impeccable

Upstream: pbakaus/impeccable @ b4bff1626c344067788c2679f048a20057c7cc5a (Apache-2.0).
`vendor/impeccable/` itself is verbatim upstream (LICENSE and NOTICE.md kept).

The derived copy installed by the `ui-kit` suite lives at `skills/impeccable/`
(synced from `.agents/skills/impeccable` via `.sync/upstreams.json`; local
adaptations survive upstream syncs through three-way merge). Differences from
upstream:

- Frontmatter gains `disable-model-invocation: true` and `triggers: [user]`
  (manual trigger only); `agents/openai.yaml` gains
  `policy.allow_implicit_invocation: false`.
- `scripts/` is not shipped: the `impeccable` launcher/binary and the
  live-browser helpers are an optional extra, not part of the default install.
  Setup reads PRODUCT.md / DESIGN.md directly when the launcher is absent.
- Commands that require the removed pieces are dropped from the command table:
  `live`, `generate` (live browser), Pin/Unpin, Hooks, and Doctor. Their
  reference files (`live.md`, `live-setup.md`, `generate.md`, `hooks.md`,
  `doctor.md`) are removed, as are the live/`generate` lines in
  `reference/routing.md`.
- `critique` gains one rule: when a Kimi design export exists in the project,
  it is the ground truth and the surface is compared against it item by item.
