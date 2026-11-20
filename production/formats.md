# Output formats — readiness spec

The project has **one canonical source per prasang** and **two output formats**.
Nothing in the content layer is format-specific. A prasang is written once in
`script.json`, then rendered into whichever format is requested.

Long-form is **not being built yet**. This doc and the tooling hooks below are
the contract so that when it is requested, no content or character work is
thrown away.

---

## 1. Reels (building now)

| Property | Value |
|---|---|
| Aspect | 9:16, 1080×1920 |
| Runtime | 60–150 s, decided by the story |
| Structure | One prasang, bespoke treatment, no fixed beat sheet |
| Caption safe zone | bottom 17%, top 250px clear |
| Renderer | `FORMAT=reel node engine/zach/render.mjs video <out.mp4>` |
| Style candidates | `zach` (3D), `stick` (2D) |

## 2. Long-form (ready, not started)

| Property | Value |
|---|---|
| Aspect | 16:9, 1920×1080 |
| Runtime | 8–20 min per episode |
| Structure | One **varta** (a full Vaishnav) = episode. Its prasangs = chapters. |
| Source | The exact same `script.json` files already written for the reels |
| Renderer | `FORMAT=long node engine/zach/render.mjs video <chapter.mp4>` per chapter |
| Assembly | `python3 tools/assemble_longform.py <manifest.json>` |
| Extra assets | Title card, chapter cards, transition sting, end card — generated, not hand-made |

### Why this is cheap later

- Character models are already format-independent (`bible/characters/*.json`).
- The scene kit is already aspect-independent — Three.js uses the viewport aspect.
- Scripts carry `sourceRef` per shot, so a long-form narration can be the same
  words or an expanded version without losing provenance.
- The only new work at long-form time is: chapter manifests, a title card, and
  a longer voice session (more ElevenLabs characters — budget it separately).

### Long-form manifest shape

See `production/longform.example.json`. A manifest lists chapters in order,
each pointing at a reel directory. The assembler concatenates chapter MP4s with
a crossfade, adds chapter-card stills, and writes ffmpeg chapter metadata.

### Voice budget note

A 12-minute long-form episode needs ~1,600 words ≈ 11,000–14,000 characters —
more than one month of the free ElevenLabs tier. Long-form therefore waits for
either a paid tier or a smaller episode scope (e.g. 6 minutes / 3 chapters).
Plan this when the user actually asks.

---

## 3. Shared rules (never differ by format)

- Vrajbhasha narration, Devanagari captions.
- No cartoon face for Shrinathji / Krishna / any svaroop.
- Every doctrinal line traces to a `sourceRef`.
- Character IDs are stable across both formats and all reels.
- One motif object per story, chosen in the treatment.
