# QA gates — every reel before publish

Run in order. A failed gate blocks publish.

## Content

- [ ] Names and terms checked against the **clean Indore scan** (vision), not the OCR PDF.
- [ ] Every doctrinal line has a `sourceRef` in `script.json`.
- [ ] No invented theology, no moral-card ending.
- [ ] Structure comes from the treatment sheet, not a fixed beat template.
- [ ] Narration is Vrajbhasha/Hindi; Devanagari renders correctly (no tofu boxes).

## Characters

- [ ] Every recurring character uses its stored ID from `bible/characters/`.
- [ ] No new character invented without a JSON model + seed.
- [ ] Same ID looks identical in both styles.
- [ ] No face rendered for Shrinathji / Krishna / any svaroop.

## Picture

- [ ] Captions 1–4 words, bottom third, inside IG safe zone.
- [ ] No English text leakage from the engine defaults.
- [ ] All 10 shots render; no black frames, no foreground objects blocking faces.
- [ ] One motif object visible across the story.

## Sound

- [ ] `audio/vo.mp3` present and aligned → `audio/words.json`.
- [ ] Caption timing drift < 80 ms against words.
- [ ] No music under narration unless the treatment calls for it.
- [ ] Final loudness −14 LUFS, peak ≤ −1.5 dBTP.

## Output

- [ ] 1080×1920, 30 fps, H.264, yuv420p.
- [ ] Silent preview is not published by mistake.
- [ ] Thumbnail frame chosen.
- [ ] `production/tracker.csv` updated.
