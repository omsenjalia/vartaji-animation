# Voice guide — ElevenLabs (user-operated)

## Model + settings

- **Model:** Multilingual (not Turbo/Flash). Best Devanagari prosody.
- **Voice:** male, 35–55, warm storyteller, slight rasp, North-Indian Hindi.
- Reject: newsreader-flat, teenaged, "energetic YouTuber", heavy Urdu accent.
- **Stability 40–45 · Similarity 78–85 · Style 15–25 · Speaker Boost ON · Speed 0.95**

## Audition

Test 6–8 voices on this paragraph. It is name-heavy on purpose — TTS breaks on names.

> अब श्रीआचार्यजी महाप्रभुनके सेवक दामोदरदास हरसानी, जिनकूँ महाप्रभुजी 'दमला' कहते, तिनकी वार्ता सुनो। एक दिन श्रीगोवर्धनधर स्वयं पधारे, और दामोदरदासने कहा — ठाकुरजी, निकट मति आवो, महाप्रभुजी जागेंगे।

Pick the voice that says `दामोदरदास`, `हरसानी`, `गोवर्धनधर` cleanly. Save it. Never change it — that consistency is channel identity.

## Budget

Free tier = **10,000 characters/month** (not words). One 90s reel ≈ 1,100 chars. ≈ 8–9 reels/month.

## Handoff

For each reel:

1. Paste `reels/<id>/narration_tts.txt` — clean text, no timestamps, no markdown.
2. Generate **one continuous MP3**, no music, no per-shot splitting.
3. Save as `reels/<id>/audio/vo.mp3`.
4. Run `python3 tools/align_vo.py reels/<id>` → `audio/words.json`.
5. Render. One VO serves both 3D and stick versions.

`narration_timed.txt` is for reference only. Do not paste it into ElevenLabs.
