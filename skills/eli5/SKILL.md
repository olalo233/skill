---
name: eli5
license: Apache-2.0
description: Explain a topic like I'm a 5 year old. Use when the user types /eli5 topic or asks for a dead-simple picture explainer of how something works.
---

# eli5

Explain like I'm someone who knows nothing about this topic, using a HTML artifact with big pictures and few words.

Topic: $ARGUMENTS

## Shared appearance assets

- New HTML defaults to both light and dark appearances, following the system without a theme switch. Author one DOM and one layout; copy existing assets rather than outputting duplicate palettes or markup.
- For explicit website/image recreation, first ask whether to preserve the original appearance or add system-following light/dark support, unless the user already answered. Follow that choice.
- Reuse the installed `html` skill's `design-system/theme.css` (resolve `../html/design-system/theme.css` relative to this installed skill's directory; install `html` alongside this skill): copy it next to the output under `design-system/` and link it. It supplies both palettes and minimal element defaults, without the document layout. If it is unavailable, report the missing dependency rather than silently producing light-only HTML.
- Use its semantic tokens for surfaces, text, borders, shadows, controls, code, and diagrams: `--mb-bg`, `--mb-surface`, `--mb-ink`, `--mb-ink-body`, `--mb-border`, `--mb-rule`, `--mb-muted`, `--mb-link`, `--mb-accent`, `--mb-code-bg`, and `--mb-series-1` through `--mb-series-4`. SVG uses `currentColor` or these variables. Keep original photos/screenshots unchanged, using a suitable frame where needed; do not apply blanket inversion.
- Only for Canvas/chart libraries, also copy/load `theme.js` from that directory. Register `MBTheme.watch(palette => { /* draw/update using palette values */ })` after the chart exists. It runs immediately and on system appearance changes; use `palette['series-1']`, `palette['ink']`, etc., not CSS-variable strings in Canvas APIs. The returned function unsubscribes. Reuse chart instances on redraw.
- Check the same page in light and dark appearances, including code, SVG/chart labels, controls, and runtime theme changes. Print remains light. Do not generate separate light/dark pages or a UI test project.

Local modifications (2026): shared system-following appearance, portable sibling asset references, and frontmatter cleanup.
