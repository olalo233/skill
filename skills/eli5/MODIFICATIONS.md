# Modifications to anthropics/claude-plugins-community eli5 (derived copy)

Upstream: anthropics/claude-plugins-community @ 163301d1904c0a994539f5226ce0fcd65b8652bf
(Apache-2.0), path `eli5/skills/eli5`. Differences from upstream:

- Frontmatter gains `disable-model-invocation: true` and `triggers: [user]`
  (manual trigger only); `agents/openai.yaml` pins
  `policy.allow_implicit_invocation: false`.
- The body is rewritten around this repository's shared `html` skill:
  output is a HTML artifact reusing `../html/design-system/theme.css`, and
  the missing-dependency case must be reported instead of silently
  producing light-only output.
- This directory ships `LICENSE` verbatim from upstream, as Apache-2.0
  requires for derivative works.
