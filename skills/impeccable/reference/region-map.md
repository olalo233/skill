# Region map

A region map names what is actually visible in the approved comp before asset production. It is not a page build or an asset approval. The map is written by hand, reading the comp image directly; the build thread both authors and verifies it.

1. Open the approved comp image and read its pixel dimensions (`file`, `sips`, or any image tool the environment offers). Study the composition once before writing anything.
2. Write `regions.json` beside the comp with a `regions` array. Each region needs a stable `id`, a `kind`, a `note`, and exactly one box: `pixelBox` (`{"x": n, "y": n, "w": n, "h": n}`), normalized `box` (same keys, floats 0–1), or `grid` (`{"col": n, "row": n, "span": n}` against a stated column grid). Boxes use the comp's own pixel dimensions. Kinds: `container` (layout extent only, `container: true`), `text`, `control`, `chrome`, `image`, `plate`, `texture`. Optional fields: `parentId`, `codeDrawn` (painted material you chose to draw in code), `exclude` (a foreground box inside the region).
3. Verify the map before it is used: every box sits inside the comp bounds, boxes for independent elements do not overlap except through `parentId`/`exclude`, and the regions cover everything visible — walk the comp top to bottom and name what each pixel belongs to. Where the environment has an image tool, crop each region's box into `.impeccable/review/map-crops/` and open the crops against the map; where it does not, re-open the comp and check each region's box against it visually. Every overlapping non-container region is bound in full, including empty space inside it. Bound separate text elements separately so artwork in the gaps stays visible; a container describes their layout extent and never replaces its children. Correct the map and inspect again. Finding no errors does not certify accuracy; coverage notes are hints, not proof of completeness.

If the request ends at mapping, stop with the map and your unresolved findings. To continue a build, the verified map is the spec input; record it under `.impeccable/build/spec.json` as the `regions` list and follow [new-work.md](new-work.md).

Banding the comp into horizontal strips is an optional scaffolding trick when a blank page resists mapping; it does not replace authoring a map.

## Containment

`parentId` identifies an enclosing `container: true` region. Parent and children keep separate IDs and boxes. Containment never transfers approval.

## What varies independently

Split regions by what varies independently: content the site swaps (room photos, products, people), moving parts (anything a hover or the signature interaction moves), and structure (frames, surrounds, ornament). A window with open shutters onto a room is three kinds of region: the surround as a plate with a transparent opening, the room as an image region beneath it, and each shutter as its own plate. Overlapping regions are composited in the page. A raster region whose note names a frame and the view it opens onto is a `baked-composite` risk; flag it in the map's notes and show it to the user first in the plan and asset review.

## Painted material

When mapping, flag any `text`, `control` or `chrome` region, containers included, whose part of the comp looks painted (`painted-pixels`: many colours, soft gradients) in its note. The plan and asset review shows flagged regions, and those marked `codeDrawn` (painted material you chose to draw in code), to the user first. Do not leave the catch to them: if a region is painted material (a figure, a photograph, a metal or paper surface), classify it `plate`, `image` or `texture` now.

Comp crops are reference evidence only, never production assets. Name map crops under `.impeccable/review/map-crops/` so nothing mistakes them for plates.
