"""
Aligns and assembles Indic Parler-TTS stems into master vo.wav with tight cinematic pacing.
Enforces user directive: MAX PAUSE BETWEEN SPEECHES <= 0.5s (set to 0.35s natural breath).
Computes word-level synchronized captions with faster-whisper,
and updates script.json with clean, non-overlapping shot timing.
"""

import os
import json
import soundfile as sf
import numpy as np
from faster_whisper import WhisperModel

def resample_audio(data, orig_sr, target_sr):
    if orig_sr == target_sr:
        return data
    target_len = int(len(data) * target_sr / orig_sr)
    return np.interp(
        np.linspace(0, len(data), target_len, endpoint=False),
        np.arange(len(data)),
        data
    ).astype(np.float32)

def main():
    manifest_file = "reels/intro-gokulnath/audio/parler_stems/manifest.json"
    if not os.path.exists(manifest_file):
        print(f"Error: {manifest_file} not found!")
        return

    with open(manifest_file, "r", encoding="utf-8") as f:
        stems = json.load(f)

    print(f"Loaded {len(stems)} stems from manifest.")
    print("Loading faster-whisper model on CPU...")
    whisper = WhisperModel("tiny", device="cpu", compute_type="int8")

    # Tight pacing schedule:
    # Initial lead-in before s01 speech: 0.20s
    # Max pause between any two speeches: 0.35s (strictly <= 0.5s)
    # Final outro hold after s11 speech: ~0.75s
    PAUSE_BETWEEN_SPEECH = 0.35 # max 0.5s
    INITIAL_LEAD_IN = 0.20

    current_audio_time = INITIAL_LEAD_IN
    shot_schedule = {}
    prev_shot_id = None

    for i, stem in enumerate(stems):
        sid = stem["id"]
        dur = stem["duration"]

        audio_start = current_audio_time
        audio_end = audio_start + dur

        if i == 0:
            shot_start = 0.0
        else:
            # Camera cut halfway through the 0.35s gap
            shot_start = round(audio_start - (PAUSE_BETWEEN_SPEECH / 2.0), 3)
            # Update previous shot's end to match this shot's start
            shot_schedule[prev_shot_id]["shot_end"] = shot_start

        shot_schedule[sid] = {
            "shot_start": shot_start,
            "shot_end": None, # will be set by next shot or final
            "audio_start": round(audio_start, 3),
            "audio_end": round(audio_end, 3),
            "dur": dur,
            "stem": stem
        }

        prev_shot_id = sid
        current_audio_time = audio_end + PAUSE_BETWEEN_SPEECH

    # Final shot (s11) outro hold
    last_audio_end = shot_schedule[prev_shot_id]["audio_end"]
    # Round total duration to a clean 30fps frame count
    raw_total = last_audio_end + 0.75
    total_frames = int(np.ceil(raw_total * 30))
    total_duration = round(total_frames / 30.0, 2)
    shot_schedule[prev_shot_id]["shot_end"] = total_duration

    print(f"\nTotal calculated duration: {total_duration:.2f}s ({total_frames} frames @ 30fps)")
    print(f"Speech pause between all shots: {PAUSE_BETWEEN_SPEECH}s (Max allowed: 0.5s)\n")

    master_sr = 48000
    total_samples = int(total_duration * master_sr)
    master_timeline = np.zeros(total_samples, dtype=np.float32)

    all_captions = []
    updated_shots = []

    for sid, info in shot_schedule.items():
        stem = info["stem"]
        spk = stem["speaker"]
        txt = stem["text"]
        dur = info["dur"]
        path = stem["path"]
        shot_start = info["shot_start"]
        shot_end = info["shot_end"]
        audio_start = info["audio_start"]
        audio_end = info["audio_end"]
        lead_in = round(audio_start - shot_start, 3)
        tail_hold = round(shot_end - audio_end, 3)

        print(f"[{sid}] ({spk}) | Speech: {dur:.2f}s | Shot: [{shot_start:.2f}s - {shot_end:.2f}s] | Audio: [{audio_start:.2f}s - {audio_end:.2f}s] | Lead: {lead_in:.2f}s, Tail: {tail_hold:.2f}s")

        # Read stem audio
        data, orig_sr = sf.read(path)
        if data.ndim > 1:
            data = data.mean(axis=1)
        data = data.astype(np.float32)

        # Microfade 8ms
        fade_samples = min(int(orig_sr * 0.008), len(data) // 4)
        if fade_samples > 0:
            data[:fade_samples] *= np.linspace(0.0, 1.0, fade_samples)
            data[-fade_samples:] *= np.linspace(1.0, 0.0, fade_samples)

        # Resample to master 48kHz
        data_48k = resample_audio(data, orig_sr, master_sr)

        # Place onto master timeline
        start_samp = int(audio_start * master_sr)
        end_samp = min(start_samp + len(data_48k), total_samples)
        copied = end_samp - start_samp
        master_timeline[start_samp:end_samp] += data_48k[:copied]

        # Resample to 16kHz for Whisper
        data_16k = resample_audio(data, orig_sr, 16000)

        # Transcribe with Whisper for word timestamps
        segments, _ = whisper.transcribe(data_16k, language="hi", word_timestamps=True)
        word_events = []
        for s in segments:
            if s.words:
                for w in s.words:
                    word_events.append({
                        "word": w.word.strip(),
                        "start": w.start,
                        "end": w.end
                    })

        # Map chunks
        chunks = stem.get("caption_chunks", [])
        num_chunks = len(chunks)
        if word_events and num_chunks > 0:
            words_per_chunk = max(1, len(word_events) // num_chunks)
            for c_idx, chunk in enumerate(chunks):
                w_start_idx = c_idx * words_per_chunk
                w_end_idx = (c_idx + 1) * words_per_chunk if c_idx < num_chunks - 1 else len(word_events)

                if w_start_idx < len(word_events):
                    s_rel = word_events[w_start_idx]["start"]
                    e_rel = word_events[min(w_end_idx - 1, len(word_events) - 1)]["end"]
                else:
                    s_rel = (c_idx / num_chunks) * dur
                    e_rel = ((c_idx + 1) / num_chunks) * dur

                s_abs = round(audio_start + s_rel, 2)
                e_abs = round(min(audio_start + e_rel + 0.08, shot_end - 0.04), 2)

                all_captions.append({
                    "text": chunk["text"],
                    "s": s_abs,
                    "e": e_abs,
                    "shot": sid
                })
        else:
            # Fallback proportional
            for c_idx, chunk in enumerate(chunks):
                s_rel = (c_idx / num_chunks) * dur
                e_rel = ((c_idx + 1) / num_chunks) * dur
                s_abs = round(audio_start + s_rel, 2)
                e_abs = round(min(audio_start + e_rel + 0.08, shot_end - 0.04), 2)
                all_captions.append({
                    "text": chunk["text"],
                    "s": s_abs,
                    "e": e_abs,
                    "shot": sid
                })

        updated_shots.append({
            "id": sid,
            "speaker": spk,
            "start": shot_start,
            "end": shot_end
        })

    # Normalize master audio to peak -1.0 dBFS
    peak = np.max(np.abs(master_timeline))
    if peak > 0:
        target_peak = 10.0 ** (-1.0 / 20.0) # ~0.891
        master_timeline = master_timeline * (target_peak / peak)
        print(f"\nAudio normalized: original peak {peak:.3f} -> adjusted to {target_peak:.3f}")

    # Save master vo.wav
    master_vo = "reels/intro-gokulnath/audio/vo.wav"
    sf.write(master_vo, master_timeline, master_sr)
    print(f"Master VO saved to {master_vo} ({len(master_timeline)/master_sr:.2f}s, 48kHz)")

    # Save captions.json
    captions_file = "reels/intro-gokulnath/captions.json"
    with open(captions_file, "w", encoding="utf-8") as f:
        json.dump(all_captions, f, ensure_ascii=False, indent=2)
    print(f"Synced captions saved to {captions_file} ({len(all_captions)} entries)")

    # Update script.json
    script_file = "reels/intro-gokulnath/script.json"
    with open(script_file, "r", encoding="utf-8") as f:
        script = json.load(f)

    for shot in script.get("shots", []):
        for u in updated_shots:
            if u["id"] == shot["id"]:
                shot["start"] = u["start"]
                shot["end"] = u["end"]
                break

    script["duration"] = total_duration
    with open(script_file, "w", encoding="utf-8") as f:
        json.dump(script, f, ensure_ascii=False, indent=2)
    print(f"Updated script.json saved with total duration {total_duration}s and tight shot cuts!")

if __name__ == "__main__":
    main()
