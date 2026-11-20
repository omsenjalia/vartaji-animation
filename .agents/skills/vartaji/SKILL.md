---
name: vartaji
description: >-
  Autonomous director and producer for Vartaji 3D short animated reels.
  Use when the user asks to make, generate, or produce a Vartaji reel
  (e.g. "make vaishnav 1 vartaprasang 1", "generate reel for Damodardas Harsani",
  "produce prasang 2 of vaishnav 4").
---

# Vartaji Reel Production Skill

Orchestrates the creation of 3D animated short reels of the 84 Vaishnav Varta in authentic Vrajbhasha/Hindi using the Zach D. Films stylized aesthetic.

## Quick Trigger Reference

When requested:
`make vaishnav <N> vartaprasang <M>`

Follow the 8-phase production sequence:
1. **Source Discovery**: Look up `research/index/vaishnavs.json` and read `source_text/all.txt` for page range.
2. **Treatment**: Draft `reels/v<NN>-p<MM>/treatment.md` with cinematic arc, motif object, setting, and POV.
3. **Cast, Models & Voice Profiles**: Ensure character JSONs exist in `bible/characters/` with deterministic `indic-parler-tts` voice prompts and seeds.
4. **Script & Captions**: Write `script.json` (60–90s, 8–12 shots) with mandatory Instagram outro callout, and word-level aligned `captions.json`.
5. **3D Staging**: Configure shot cameras in `engine/zach/lib/camera.js` and lighting/animation cues.
6. **WSL Headless Render**: Run `GL=swiftshader node engine/zach/render.mjs stills ...` to verify frames, then `video` to render 30 FPS MP4.
7. **Voice Synthesis & Muxing**: Run `tools/generate_vo.py` to synthesize character voices with `ai4bharat/indic-parler-tts` and auto-mux into `final_with_vo.mp4`.
8. **Delivery**: Present clickable links to stills, master VO audio, and MP4; update `production/tracker.csv`.

See [agent.md](../../agent.md) for full operational rules, aesthetic directives, and exact CLI commands.
