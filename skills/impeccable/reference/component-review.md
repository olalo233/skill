# Plan and asset review

Use this checkpoint on comp-led builds once every raster region has its plate and the plates phase has passed, before any page code exists. The approved comp is the reference. The user reviews two things: the plates that will ship, and the production plan for everything else, meaning which regions code draws. A painted region planned as code is the most expensive mistake a comp-led build makes, and this is where the user catches it. Text, controls and chrome are judged later, in the assembled first viewport.

## Plan, present, record

Write `.impeccable/review/components.json` from the measured spec, the comp, and the plate files: one entry per region with its `id`, `kind`, `note`, spec box, and either its `plate` path or `"medium": "code"`. Refuse to proceed — naming each one — while any raster region lacks its plate. Never hand-edit the entries' geometry: the packet is derived from the spec, so every correction belongs in the regions file.

Present the review to the user:

- Show each raster region's plate next to its comp crop (open both images; where the harness cannot render images, list the paths side by side in a table).
- Show the code-drawn list: every `text`, `control`, `chrome`, and `container` region, flagging any region the map marked `painted-pixels` or `baked-composite` first.
- Ask, through the structured question tool or plainly in chat: which plates need work, and which planned-code regions should ship as rasters instead.

Record the decisions in `.impeccable/review/components.json` (`"decision": "approved" | "needs-work"` per entry, plus the user's notes). A paused request is waiting for the user; it is not a failed build or an approval. Never record approval on the user's behalf. Confirmation means every entry reads `approved`; pending, needs-work, or edited-since-presented input sends the affected regions back through the plates phase before page code starts.
