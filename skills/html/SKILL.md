---
name: html
description: Create and edit visual explanatory documents in HTML for concepts, mechanisms, and research findings.
---

# Explanatory Documents in HTML

## Writing

The following skills are recommended to supplement the explanatory content and Japanese-language expression.

- `explain`: Terminology definitions, level of detail, and structure when explaining concepts and mechanisms
- [`japanese-tech-writing`](https://gist.github.com/k16shikano/fd287c3133457c4fd8f5601d34aa817d): Structure and writing standards for Japanese technical documents, articles, and explanatory writing
- [`cognitive-rhythm-writing`](https://gist.github.com/k16shikano/eb2929f13ed19c97188393d297be8432): Writing standards for long-form content that needs changes of pace to remain engaging

All of these are recommended skills and are not required dependencies of `html`.

## Deliverables

- Create HTML
- Make it directly renderable in a browser without a build step
- Follow the specified save location. If none is specified, save it in the current working directory
- Name the file `{yyyymmdd}-{kebab-case-description-of-content}.html`. Do not rename an existing file when updating it
- Follow the instructions of the parent skill that references this skill for rules concerning any individual document management system, metadata, viewer, or publishing destination

## Design System

Before creating the document, inspect `design-system/component-samples.html`. Treat `design-system/document.css` as authoritative for the component set and `design-system/math-copy.js` as authoritative for the math-copying functionality.

By default, place the required files alongside the deliverable and load them using the following relative paths. If a parent skill specifies paths for shared assets, follow those instructions instead.

```html
<link rel="stylesheet" href="./design-system/document.css">
<script src="./design-system/math-copy.js"></script>
<script async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.11.1/highlight.min.js"></script>
<script>document.addEventListener("DOMContentLoaded", () => hljs.highlightAll());</script>
```

The main rules are as follows.

- `document.css` imports the shared `theme.css`: copy both assets with the deliverable. Use semantic colors from that asset; new documents follow the system in light and dark mode with one DOM and one layout. Do not regenerate palettes per page.
- Reuse the asset's system sans-serif stack (including Chinese fallbacks); use monospace only for code. No font CDN is required.
- Use `--mb-link` for blue links and `--mb-accent` for red emphasis; their values adapt to the appearance.
- As a rule, use red emphasis in no more than one place per page
- Syntax highlighting and code-diff colors are functional colors that distinguish meaning and are exempt from this restriction
- Build hierarchy with type size, weight, readable line length, and vertical spacing. Keep ordinary prose open; reserve cards for meaningful groups. Do not add heavy heading bars, repeated boxed sections, or nested cards.
- Use `.mb-quote` for quotations, placing the original and translated text vertically with the same font size and color
- Use `.mb-chip` only for enumerating parallel proper names or classification names
- Do not use emoji or arrow characters as diagram symbols. Draw necessary symbols with inline SVG
- Use tables for short mappings and generally limit them to three columns
- Add `.mb-rowlabel` to row-heading cells to prevent line breaks within words
- Use `pre.mb-diff` for code diffs. Explain the reason for a change in prose before showing only the necessary fragment
- Keep page-specific `<style>` rules to the minimum necessary, such as adjustments to diagram placement

## Structure and Formatting

Choose among side-by-side layouts, diagrams, timelines, summaries, and collapsible sections according to the subject being explained.
Do not turn a simple one-way procedure into a flowchart without a clear need.

Use the following basic order.

1. Terminology list
2. Background
3. Main discussion
4. Concrete examples
5. Additional notes, limitations, and related matters

For long documents, place a `.mb-toc` table of contents after the h1 and lead paragraph, and give each h2 a corresponding `id`.
When terminology needs a separate list, use `aside.mb-glossary` inside `.mb-wrap`; otherwise omit the sidebar and keep the reading column compact.
Define technical terms in one or two sentences before using them in the main text.

## Figures

- `.mb-figure` is an outer container that groups visual material such as images or SVGs with a caption. It does not refer to any particular shape or to "boxes connected by arrows"
- `.mb-figure-frame` is the display surface for visual material, and `figcaption` is the area for the figure number, description, and source
- If the original source contains an important figure, quote it and clearly identify the source
- Do not create an imitation diagram when a figure from the original source is available
- Use inline SVG for original diagrams; for a simple sequence use the responsive `.mb-flow` asset (one list with SVG connectors). Keep labels readable on mobile; do not shrink an entire desktop diagram until its text becomes tiny. Do not use ASCII art.
- Use monochrome line drawings with `currentColor` or semantic theme tokens, placed on `.mb-figure-frame`; never hardcode black strokes or text.
- Prefer a vertical layout when there are many nodes
- Avoid layouts in which arrows cross
- Present simple sequential procedures as numbered explanations

## Code

- Always load Highlight.js and apply syntax highlighting appropriate to the language
- Always add a language class such as `language-javascript`, `language-python`, or `language-html` to `pre code`
- Use `language-plaintext` for text that should not be highlighted
- Do not decorate code with custom coloring; use the shared `.hljs-*` rules imported by `document.css`
- Add `nohighlight` to `pre.mb-diff code` and use the diff-specific colors and line-prefix symbols

## Mathematics

- Use MathJax 3
- Use `$...$` for inline mathematics and `$$...$$` for display mathematics
- Use `\boldsymbol{...}` for vectors and matrices
- Do not decorate scalars, subscripts, or set names
- Use `\mathtt{...}` for named operations, and use standard LaTeX commands as-is
- Use `math-copy.js` to make the original LaTeX source copyable from every formula
- Do not redefine `window.MathJax` on the page
- Do not arbitrarily replace unknown commands with different notation

## Printing and PDF

Use the `@media print` rules in `document.css` for print support.
Run `render-pdf.sh` to create a PDF only when the user explicitly requests it.

The component sample demonstrates a complete Chinese reading page, including a responsive article/sidebar, table, code, SVG, Canvas and working reading controls. Reuse component classes rather than writing one-off replacements. Design rationale and source links are in `references/design-rationale.md` (read only when changing the assets).

## Appearance coverage

- New HTML defaults to both light and dark appearances, following the system without a theme switch. Author one DOM and one layout; copy existing assets rather than outputting duplicate palettes or markup.
- For explicit website/image recreation, first ask whether to preserve the original appearance or add system-following light/dark support, unless the user already answered. Follow that choice.
- Reuse this skill's `design-system/theme.css` through `document.css`; no extra inline palette is needed. Copy assets with file tools, rather than reading and reproducing their contents in model output.
- Use its semantic tokens for surfaces, text, borders, shadows, controls, code, and diagrams: `--mb-bg`, `--mb-surface`, `--mb-ink`, `--mb-ink-body`, `--mb-border`, `--mb-rule`, `--mb-muted`, `--mb-link`, `--mb-accent`, `--mb-code-bg`, and `--mb-series-1` through `--mb-series-4`. SVG uses `currentColor` or these variables. Keep original photos/screenshots unchanged, using a suitable frame where needed; do not apply blanket inversion.
- Only for Canvas/chart libraries, also copy/load `theme.js` from that directory. Register `MBTheme.watch(palette => { /* draw/update using palette values */ })` after the chart exists. It runs immediately and on system appearance changes; use `palette['series-1']`, `palette['ink']`, etc., not CSS-variable strings in Canvas APIs. The returned function unsubscribes. Reuse chart instances on redraw.
- Check the same page in light and dark appearances, including code, SVG/chart labels, controls, and runtime theme changes. Print remains light. Do not generate separate light/dark pages or a UI test project.
