# REMEMBER — Vartaji Reels Project Bible

Living document. Update as decisions are made; never delete a superseded decision without noting why.

---

## 1. What this project is

A series of short animated **films** — not explainers, not darshan slideshows — telling the stories in **चौरासी वैष्णवन की वार्ता** (the Vartas of the 84 Vaishnavs of Pushtimarg).

- **Source of truth:** `source/84 vaishnav.pdf`
- **Narration language:** Vrajbhasha / Hindi, in Devanagari
- **Output:** 9:16 vertical reels for Instagram
- **Target:** every prasang in the source. 84 is the guaranteed minimum (one per Vaishnav); prasang-level expansion follows.
- **Style:** **3D only (Zach D. Films Aesthetic with Pushtimarg Aesthetics).** Stick-figure, low-poly, and CSS trials were all trialled and dropped — user did not like them. All legacy engine folders (`engine/stick/`, `engine/lowpoly/`, `engine/hf/`, `engine/common/`) have been permanently removed. `engine/zach/` is the sole canonical production pipeline.

### The user's key creative direction (do not forget)

> "I want to convey the story of 84 vaishnavs, not an explainer or darshan video. Every varta-prasang will need its own unique template as each varta is unique."

So:

- ❌ No fixed hook/setup/turn/moral beat sheet
- ❌ No "इससे हमें यह सीख मिलती है" moral cards
- ❌ No narrator-as-teacher, no labelling captions
- ✅ One invisible spine only (cold open; one narrator voice; one motif object; the varta's own ending)
- ✅ Instagram Outro Hook: Every reel ends with the forward callout hook: `तो चलिए शुरुआत करते हैं श्री {name} वैष्णव की वार्ता {number} वार्ता प्रसंग {number} से... जय श्री कृष्ण!`
- ✅ Each prasang gets a **treatment sheet** before a script — structure, POV, motif, withholding, camera, ending come from the story
- ✅ Reels are short films about people. Theology enters through what happens.

---

## 2. Source facts

| Fact | Value |
|---|---|
| Primary source (clean scan) | `source/84-Vaishnav-Vaartaji-Vraj-Bhasha-Best-Quality-Indore-2005-Vaarta-Sahitya.pdf` — 616 pages, **no embedded text**, Devanagari scan. Read pages as images with vision. |
| Navigation source (OCR) | `source/84 vaishnav.pdf` — 564 pages, OCR'd but contaminated with Gujarati glyphs. Use for page ranges/index only. |
| Extracted text | `source_text/all.txt` (from the OCR PDF, page markers `=== PAGE n ===`) |
| Section index | `research/index/vaishnavs.json` (84 sections) |
| Prasang index | `research/index/prasangs.json` (84 placeholders, split during treatment) |
| Canonical names | `research/index/canonical_names.json` |
| Intro story | pages 1–2 |
| v01 Damodardas Harsani | pages 3–14 |
| v02 Krishnadas Meghan | pages 15–22 |
| v03 Damodardas Sambhalware | pages 23–36 |
| v04 Padmanabhadas | pages 37–47 |
| v81 Surdas | pages 358–419 |
| v82 Paramanand | pages 420–474 |
| v83 Kumbhandas | pages 475–522 |
| v84 Krishnadas Adhikari | pages 523–564 |

### OCR caveats — critical

The PDF is OCR'd and **contaminated with Gujarati glyphs** (દ, પ, ગ, ક્ષ, ઝ, etc.) mid-Hindi. Examples in the source: `પૂ આસય`, `કછુક`, `ક્ષત્રી`, `વાર્તા`.

Rules:

1. **Never copy raw OCR into a script.** Adapt into clean Vrajbhasha.
2. **Never trust an OCR'd name.** Cross-check with `canonical_names.json` and the printed book.
3. This edition **omits the Londi varta** (canonical #4) and **includes Jagannath Joshi's mother** (not in the common 84-list). Do not zip the canonical list 1:1 onto PDF sections.
4. Printed `वातप्रिसद्ध` prasang markers number only ~30 across the PDF. They are incomplete — prasang boundaries must be read from the prose.

---

## 3. Pushtimarg background (research notes)

- **Pushtimarg** ("the path of grace") is a Vaishnava tradition founded by **Shri Vallabhacharya** (Mahaprabhu, 1479–1531), centred on **Shrinathji** at Nathdwara and the **Ashtasakhas** (eight poet-saints).
- The **चौरासी वैष्णवन की वार्ता** is a Braj Bhasha prose work ofhagiographical anecdotes. Authorship is traditionally attributed mainly to **Goswami Gokulnathji** (Gusainji's son), with the **भावप्रकाश** commentary by **Shri Harirayji**. The text explicitly says Gokulnathji revealed the vartas and Harirayji speaks the bhav.
- Related works: **दो सौ बावन वैष्णवन की वार्ता** (252 Vaishnavs — a different, larger work; *not* this PDF) and **अष्ट सखान की वार्ता**.
- The number 84 is theological, not arbitrary: 84 lakh (crore) yonis/wombs, 84 kos of Braj, 84 varnas of rasa. The text says divine souls trapped in 84 lakh yonis were liberated through 84 Vaishnavs.
- The Vaishnavs span all castes and both genders — kings, merchants, potters, barbers, brahmins, women, a carpenter, a Kshatri, a largely blind poet. That social range is the point; don't sand it off in adaptation.
- **Four Ashtasakhas** were disciples of Vallabhacharya: Surdas, Kumbhandas, Krishnadas, Paramananddas. The other four were disciples of Gusainji. Surdas is said to have composed 125,000 kirtans over 108 years.
- Sources consulted: Hindi Wikipedia (Pushtimarg, चौरासी वैष्णवन की वार्ता), mahaprabhuji11.blogspot.com (84 list), krishnashray.weebly.com (prasang translations), pushtimarg.net, archive.org, YouTube series "84 Vaishnav Varta".

---

## 4. The intro story (pages 1–2) — FIRST REEL

Not part of any vaishnav's varta. It is the frame Gokulnathji placed before the 84.

**Clean paraphrase of the source:**

> One day Shri Gokulnathji was telling the varta of the 84 Vaishnavs, sitting with Kalyanbhatt and the other Vaishnavs. He was so absorbed in the rasa of it that he forgot to tell the Subodhini katha. Half the night passed. Then a Vaishnav said to him, "Maharajadhiraj — when will you tell the katha today?" It was already midnight. Shri Gokulnathji answered from his own mouth: "Today I am telling you the *fruit* of the katha. Know that the whole fruit lies in the words of the Vaishnavs. There is no other substance beyond the Vaishnav. This is Pushtimarg — it bears fruit through the Vaishnav. Shri Acharyaji said the same: 'Damla, I revealed the path for you.' Therefore know the Vaishnav's varta to be supreme."

**Why it belongs first:** it is the text's own answer to "why are we telling these stories at all?" It also introduces Gokulnathji (narrator), Kalyanbhatt (listener), Damodardas/"Damla" (the first Vaishnav), and the key word **वार्ता**.

**Doctrinal frame immediately before it (p1–2):** 84 lakh yonis → 4 kinds of souls (राजसी, तामसी, सात्विकी, निर्गुण) → Acharyaji manifesting 84 Vaishnavs to liberate the निर्र्गुण souls → 84 kos of Braj → the three gunamaya groups (252) belong to Gusainji.

**Archetype:** *The Meeting* — the whole reel is one exchange at midnight, with the assembly as witness.

---

## 5. Glossary — spell these correctly

| Braj / source form | Clean form | Meaning |
|---|---|---|
| श्रीआचार्यजी महाप्रभु | श्रीआचार्यजी महाप्रभु | Vallabhacharya |
| श्रीगुसांईजी / गुसांई | श्रीगुसांईजी | Gokulnathji (Gusainji) |
| श्रीगोकुलनाथजी | श्रीगोकुलनाथजी | Gokulnathji |
| श्रीहरिरायजी | श्रीहरिरायजी | Harirayji, author of the bhav-prakash |
| दमला | दमला | Damodardas Harsani's nickname |
| श्रीठाकुरजी / श्रीगोवर्धनधर | श्रीठाकुरजी / श्रीगोवर्धनधर | Shrinathji (never depict face) |
| श्रीसुबोधिनीजी | श्रीसुबोधिनी | Vallabhacharya's commentary on Bhagavata |
| वार्ता / वात | वार्ता | the story/account |
| प्रसंग | प्रसंग | episode/incident |
| भाव | भाव | inner sentiment, the point of the story |
| वैष्णव | वैष्णव | devotee |
| पुष्टिमार्ग | पुष्टिमार्ग | path of grace |
| ब्रह्मसम्बन्ध | ब्रह्मसम्बन्ध | initiation |
| अष्टछाप | अष्टछाप | the eight poet-saints |
| सेवा | सेवा | service/worship |
| कृपा | कृपा | grace |

---

## 6. Visual / cultural guardrails

- **Never render a face for Shrinathji, Krishna or any svaroop.** Use glow, silhouette, curtained sanctum, pichhwai frame, hands/feet, reflection. This is also the best-looking cinematic option.
- Vallabhacharya, Gokulnathji, Harirayji and the Vaishnavs are historical people — depict them respectfully in period dress.
- Avoid invented theology. Every doctrinal line in a script must trace to `sourceRef` in the reel's source text.
- Period setting: 15th–17th century North India / Vraj. Turbans, dhoti, jama, chowki, oil lamps, haveli courtyards, Yamuna ghats, kadamba trees, Govardhan.
- Captions stay inside Instagram safe margins: top 250px, bottom 320px clear on a 1080×1920 frame.

---

## 7. Voice (ElevenLabs, user-operated)

- User has **10,000 free credits = 10,000 characters**, not words. ≈ 8–9 reels/month at 90s.
- Model: **Multilingual** (not Turbo/Flash for final). Voice: male, 35–55, warm storyteller, slight rasp, North-Indian Hindi.
- Settings: Stability 40–45 · Similarity 78–85 · Style 15–25 · Speaker Boost ON · Speed 0.95.
- Audition text must include names: `दामोदरदास`, `हरसानी`, `गोवर्धनधर`, `गोकुलनाथजी`.
- **One continuous MP3 per prasang, no music.** Reuse the same file for both style renders.
- Pipeline: `narration_tts.txt` (clean, paste-ready) → user returns `audio/vo.mp3` → `tools/align_vo.py` (faster-whisper + forced snap to known text) → `audio/words.json` → captions and mouth movement.
- Until a VO exists, renders use estimated shot durations (`--silent` preview mode).

---

## 8. Typography

- **Noto Sans Devanagari** — Google's actual Devanagari UI face; use 600/700/800 for captions.
- **Google Sans** (OFL build from `googlefonts/googlesans`) for Latin numerals / any English.
- Alternates on trial: **Mukta ExtraBold**, **Baloo 2**.
- Google Sans itself has no Devanagari coverage in the public build; don't rely on it for Hindi.
- Font sample sheet: `out/font_sample.png`.

---

## 9. Pipeline / status

| Stage | Status |
|---|---|
| 0 Foundations — fonts, engines, scaffold | in progress |
| 1 Research bible + index | ✅ `remember.md`, 84-section index |
| 2 Character bible | pending (start with intro cast) |
| 2.5 Treatment sheets | pending |
| 3 Pilot — intro reel in both styles | in progress |
| 4 House style selection | pending user |
| 5 Batch waves | pending |
| 6 Packaging | pending |

### OCR fallback / source verification

When a passage looks corrupt or a name is doubtful, render the matching page
from the clean Indore scan and read it with vision:

```bash
python3 tools/render_source_pages.py 1 2          # writes PNGs to /tmp/opencode/source_pages/
```

The clean scan is authoritative for wording. The OCR PDF is authoritative only
for the section/page index built by `tools/build_index.py`.

### Commands (Run in WSL)

All Node/Chromium/Playwright/ffmpeg commands must run inside WSL (`GL=swiftshader`):

```bash
# Render timeline stills
wsl -e bash -lc "cd '/mnt/c/Users/Om Senjalia/Desktop/vartaji animation' && GL=swiftshader node engine/zach/render.mjs stills 0.5,6,15,48 reels/intro-gokulnath/stills"

# Render video clip
wsl -e bash -lc "cd '/mnt/c/Users/Om Senjalia/Desktop/vartaji animation' && GL=swiftshader node engine/zach/render.mjs video reels/intro-gokulnath/preview_v2.mp4 0 15"

# Mux audio
wsl -e bash -lc "cd '/mnt/c/Users/Om Senjalia/Desktop/vartaji animation' && node engine/zach/render.mjs mux reels/intro-gokulnath/preview_v2.mp4 reels/intro-gokulnath/audio/vo.mp4"
```

### 3D Engine v2 Architecture & Aesthetic Directives

The production engine in `engine/zach/` is fully modularized:
- **`lib/characters.js`**: Procedural stylized 3D figures.
  - Authentic **Padmasana / Sukhasana** posture seated on an embroidered *gaddi* (cushion).
  - Continuous cloth sleeves (`CatmullRomCurve3`) flowing naturally from shoulder to knee (no robot ball joints).
  - Sacred **Gyan / Upadesha Mudra** on right knee (thumb & index forming wisdom circle, 3 fingers extended forward) and peaceful resting **Dhyana** palm on left knee.
  - Multi-tiered sculptural Vraj Pagdi, expressive cartoon eyes with specular catchlights, sculpted nose, and authentic Pushtimarg Urdhva Pundra tilak.
- **`lib/lighting.js`**: 4-point chiaroscuro setup.
  - Warm campfire key light with organic noise flicker.
  - Frontal forest moonlight key (`#78a4d8`) aimed at tree line so trunks and Kadamba canopy are clearly visible.
  - Dedicated portrait key & rim lights for close-up and medium shots.
  - `UnrealBloomPass` + `CinematicGradeShader` with lifted shadow curve preserving night atmosphere without crushed blacks.
- **`lib/environment.js`**: Luminous night sky dome with vertical midnight-to-cobalt gradient, glowing moon with atmospheric halos, 110 sparkling stars, Great Kadamba tree with sprawling leafy canopy, framing forest trees, and soft ground mist.
- **`lib/camera.js`**: Handheld micro-motion (Perlin noise), smooth cubic transitions, cinematic portrait framing (`f=38°`).
- **`lib/animation.js`**: Breathing cycles, fire and ember physics, assembly presence, narrative-driven head turns.
- **`lib/captions.js`**: Word-level synchronized Devanagari subtitles with CSS fade transitions in the lower-third safe zone.

### User Feedback History & Resolutions (Do Not Regress)

1. **Face visibility in Shot 3**: Dedicated portrait key and rim lights ensure the teacher's face is luminous and clear; eyes stay wide and expressive with specular catchlights.
2. **Authentic Sadhu Seating**: Padmasana cross-legged base with horizontal shin folds and flowing jama skirt; hands rest solidly on knees in Gyan Mudra.
3. **Background Forest Visibility**: Twilight sky dome, glowing moon, stars, mist, and frontal moon light ensure the forest and Kadamba tree are richly visible behind characters.
4. **No legacy clutter**: All abandoned stick-figure, low-poly, and CSS trials have been purged from the repository. Only `engine/zach` remains.

### Output formats

Both formats are built from the **same** `script.json` and character bible.
Reels are being built now; long-form is a switch, not a rewrite.
See `production/formats.md` and `production/longform.example.json`.
A long-form episode = one Vaishnav's full varta, with each prasang as a chapter.
Nothing long-form-specific is created until the user asks.
