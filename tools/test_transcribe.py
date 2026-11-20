from faster_whisper import WhisperModel

model = WhisperModel("tiny", device="cpu", compute_type="int8")
for name in ["s01.wav", "s04.wav"]:
    path = f"reels/intro-gokulnath/audio/stems/{name}"
    segments, info = model.transcribe(path, language="hi")
    print(f"--- Transcription for {name} ---")
    for s in segments:
        print(f"[{s.start:.2f}s - {s.end:.2f}s]: {s.text}")
