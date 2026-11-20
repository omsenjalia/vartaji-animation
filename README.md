# Vartaji Reels — 3D Animation Engine

Animated 3D short films of the 84 Vaishnav Varta in authentic Vrajbhasha / Hindi.
Production House Style: **3D Stylized (Zach D. Films Aesthetic with 16th-century Pushtimarg Aesthetics)**.

## Project Structure

```
remember.md              Research bible & canonical decisions (authoritative)
source/                  Two PDFs: clean scan (vision fallback) + OCR (navigation)
source_text/             Page-anchored OCR text of the 84 Vartas
research/index/          84 sections, prasangs, canonical names
bible/characters/        Locked character models (JSON) — reused across reels
engine/zach/             Canonical 3D Production Renderer (Three.js + Playwright)
  index.html             Stage shell, font imports, WebGL viewport
  app.js                 Main orchestrator wiring modules and character palettes
  render.mjs             Headless renderer (stills, frame-accurate video, audio mux)
  lib/characters.js      Procedural sculpted figures, authentic Padmasana posture, Gyan Mudra, Vraj pagdi
  lib/lighting.js        4-point chiaroscuro, portrait key/rim, UnrealBloomPass, cinematic film grade
  lib/environment.js     Twilight sky dome, moon & halos, 110 stars, Great Kadamba, framing forest, mist
  lib/camera.js          Handheld Perlin breathing, cubic bezier easing, cinematic portrait framing
  lib/animation.js       Breathing cycles, flame flickers, spark physics, natural blinks, mudras
  lib/captions.js        Word-level Devanagari sync, smooth CSS fade transitions, safe zones
  lib/math.js            Noise functions, Hermite/Cubic interpolation, seeded PRNG
  lib/materials.js       Shared PBR material definitions (skin, cloth, foliage, wood, embers)
reels/<id>/              source.md, treatment.md, script.json, captions.json, audio/, stills/, renders
production/              Format contracts, voice guidelines, manifests, tracker
tools/                   Index builder, source page renderer, VO aligner, longform assembler
```

## Environment & Commands

> **Note**: Build and render commands are executed inside **WSL (Debian)** where Node, Chromium/Playwright, and ffmpeg are pre-installed. Do not run package managers on the Windows host.

### Rendering Commands (via WSL)

```bash
# 1. Render specific timeline stills (seconds)
wsl -e bash -lc "cd '/mnt/c/Users/Om Senjalia/Desktop/vartaji animation' && GL=swiftshader node engine/zach/render.mjs stills 0.5,6,15,48 reels/intro-gokulnath/stills"

# 2. Render 30 FPS video clip (from_sec to_sec)
wsl -e bash -lc "cd '/mnt/c/Users/Om Senjalia/Desktop/vartaji animation' && GL=swiftshader node engine/zach/render.mjs video reels/intro-gokulnath/preview.mp4 0 15"

# 3. Render full video reel (all shots)
wsl -e bash -lc "cd '/mnt/c/Users/Om Senjalia/Desktop/vartaji animation' && GL=swiftshader node engine/zach/render.mjs video reels/intro-gokulnath/full_reel.mp4"

# 4. Mux video with voiceover audio track
wsl -e bash -lc "cd '/mnt/c/Users/Om Senjalia/Desktop/vartaji animation' && node engine/zach/render.mjs mux reels/intro-gokulnath/full_reel.mp4 reels/intro-gokulnath/audio/vo.mp4"
```

## Visual Architecture

1. **Character Modeling & Posing**:
   - Authentic **Padmasana / Sukhasana** cross-legged seating on an embroidered *gaddi* (meditation cushion) atop the wooden *chowki*.
   - Continuous cloth sleeve tubes (`CatmullRomCurve3`) flowing seamlessly from shoulders to knees.
   - **Mudra system**: Sacred *Gyan / Upadesha Mudra* on the right knee (thumb and index finger meeting in a circle of divine wisdom) and resting *Dhyana* palm on the left.
   - Multi-layered sculptural *Vraj Pagdi* (turban) with authentic rolls and crest.
   - Expressive cartoon facial features: warm catchlight eyes, sculpted nose, Pushtimarg Urdhva Pundra tilak, and dignified jawline beard.

2. **Chiaroscuro Night Lighting**:
   - **Key light**: Dynamic warm campfire flickering light (`PointLight`).
   - **Forest Frontal Moon Key**: Directional cool moonlight (`#78a4d8`, intensity `1.45`) illuminating tree trunks and Kadamba foliage facing the camera.
   - **Portrait Key & Rim**: Dedicated warm key (`#ffb366`) and cool rim (`#9ec2f2`) illuminating the teacher's face in close-up/medium shots.
   - **Atmospheric Sky**: Inverted sky dome with vertical midnight-to-cobalt gradient, glowing moon with soft atmospheric halos, 110 sparkling stars, and ground mist.
   - **Post-Processing**: `UnrealBloomPass` for selective fire/spark glow + `CinematicGradeShader` with lifted shadow tone curve.
