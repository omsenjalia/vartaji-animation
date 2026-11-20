# Reel review — 4 independent reviewers

Run after every rendered reel. `tools/review_frames.py` extracts every frame to
PNG and builds timestamped contact sheets at 2 fps. Spawn four reviewers, each
with the same sheets plus its own brief. No reviewer sees the others' output.

Paths for a reel: `reels/<id>/review/<style>/sheets/sheet_*.png`,
full frames at `reels/<id>/review/<style>/frames/f_*.png`.

## Reviewer 1 — Caption and timing

Inputs: contact sheets, `reels/<id>/captions.json`, `reels/<id>/script.json`.
Check: caption text matches the narration phrase for that time; 2–3 words per
caption; no broken Devanagari; no caption lingering after its beat; no caption
appearing before the beat; caption inside bottom safe zone; no English leakage.
Output: `path:time: severity: problem. fix.`

## Reviewer 2 — Character consistency

Inputs: contact sheets, `bible/characters/*.json`, `reels/<id>/treatment.md`.
Check: same named character looks the same in every shot; clothes are period
(jama/dhoti/pagdi in stick, robe/turban in 3D); no striped "pyjama" torsos; no
face rendered for Shrinathji/Krishna; no accidental hero shot of an unnamed
extra; face reveal happens only at the specified beat.
Output: same format.

## Reviewer 3 — Pacing and dead time

Inputs: contact sheets, `reels/<id>/script.json`.
Check: every beat shows visible change within ~1 s; no static hold longer than
2 s; the story advances (setup → question → answer → image); no empty frames;
transitions carry motion; the reel does not stop after a beat is "done".
Output: same format.

## Reviewer 4 — Craft and QA

Inputs: contact sheets, selected full frames, `production/qa.md`.
Check: composition, framing, faces not blocked by foreground figures, lighting,
no black frames, no clipping through geometry, no duplicate limbs, readable
captions, motif object visible, end image lands, technical artifacts.
Output: same format.

## Gate

Any **high** severity finding blocks publish. Fix, re-render affected shots,
re-run all four reviewers. Keep the reports in `reels/<id>/review/reports/`.
