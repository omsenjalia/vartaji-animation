"""
High-Fidelity Neural Voice Generator for Vartaji using Microsoft Edge Neural TTS
Provides broadcast-grade human speech with accurate Devanagari/Sanskrit enunciation,
sub-cent pitch/rate control for character differentiation, and automatic timeline muxing.
"""

import os
import sys
import json
import asyncio
import argparse
from pathlib import Path
import numpy as np
import soundfile as sf
import edge_tts

VOICE_PROFILES = {
    "narrator": {
        "voice": "hi-IN-MadhurNeural",
        "rate": "-8%",
        "pitch": "-2Hz"
    },
    "gokulnathji": {
        "voice": "hi-IN-MadhurNeural",
        "rate": "-14%",
        "pitch": "-5Hz"
    },
    "kalyanbhatt": {
        "voice": "hi-IN-MadhurNeural",
        "rate": "-10%",
        "pitch": "-4Hz"
    },
    "damodardas": {
        "voice": "hi-IN-MadhurNeural",
        "rate": "-6%",
        "pitch": "-2Hz"
    },
    "young-vaishnav": {
        "voice": "hi-IN-MadhurNeural",
        "rate": "+4%",
        "pitch": "+6Hz"
    }
}

async def generate_shot_audio(text: str, profile: dict, out_path: Path):
    communicate = edge_tts.Communicate(
        text,
        profile["voice"],
        rate=profile.get("rate", "+0%"),
        pitch=profile.get("pitch", "+0Hz")
    )
    mp3_path = out_path.with_suffix(".mp3")
    await communicate.save(str(mp3_path))
    
    # Convert mp3 to wav using ffmpeg for exact PCM manipulation
    cmd = f'ffmpeg -y -v error -i "{mp3_path}" -ar 24000 -ac 1 "{out_path}"'
    os.system(cmd)
    if mp3_path.exists():
        mp3_path.unlink()

async def main():
    parser = argparse.ArgumentParser(description="Generate high-fidelity neural VO for Vartaji reel")
    parser.add_argument("reel_dir", type=str, help="Path to reel directory")
    args = parser.parse_args()

    reel_path = Path(args.reel_dir).resolve()
    script_file = reel_path / "script.json"
    if not script_file.exists():
        print(f"Error: script.json not found at {script_file}")
        sys.exit(1)

    with open(script_file, "r", encoding="utf-8") as f:
        script = json.load(f)

    shots = script.get("shots", [])
    total_duration = float(script.get("duration", 94))
    sample_rate = 24000

    audio_dir = reel_path / "audio"
    shots_dir = audio_dir / "shots"
    audio_dir.mkdir(parents=True, exist_ok=True)
    shots_dir.mkdir(parents=True, exist_ok=True)

    print("--- Vartaji Neural Speech Generator (Broadcast Quality) ---")
    print(f"Reel: {script.get('title', reel_path.name)} ({total_duration}s, {len(shots)} shots)\n")

    total_samples = int(total_duration * sample_rate)
    timeline_audio = np.zeros(total_samples, dtype=np.float32)
    generated_shots = []

    for idx, shot in enumerate(shots):
        shot_id = shot.get("id", f"s{idx+1:02d}")
        text = shot.get("narration", "").strip()
        if not text:
            continue

        speaker_id = shot.get("speaker", "narrator")
        profile = VOICE_PROFILES.get(speaker_id, VOICE_PROFILES["narrator"])
        shot_start = float(shot.get("start", 0))
        shot_end = float(shot.get("end", total_duration))
        available_dur = shot_end - shot_start

        print(f"[{shot_id}] ({shot_start:.1f}s - {shot_end:.1f}s | max {available_dur:.1f}s)")
        print(f"  Speaker: {speaker_id} ({profile['voice']}, rate={profile['rate']}, pitch={profile['pitch']})")
        print(f"  Text: {text}")

        shot_wav = shots_dir / f"{shot_id}.wav"
        await generate_shot_audio(text, profile, shot_wav)

        data, sr = sf.read(str(shot_wav))
        dur = len(data) / sr
        print(f"  Generated duration: {dur:.2f}s")

        generated_shots.append({
            "id": shot_id,
            "speaker": speaker_id,
            "duration": dur,
            "start": shot_start,
            "end": shot_end
        })

        # Place onto master timeline
        start_sample = int(shot_start * sample_rate)
        end_sample = min(start_sample + len(data), total_samples)
        copied_len = end_sample - start_sample

        # 20ms micro-fade
        fade_len = min(int(sample_rate * 0.02), copied_len // 4)
        if fade_len > 0:
            data[:fade_len] *= np.linspace(0.0, 1.0, fade_len)
            data[copied_len - fade_len:copied_len] *= np.linspace(1.0, 0.0, fade_len)

        timeline_audio[start_sample:end_sample] += data[:copied_len]

    # Save full voiceover
    master_vo = audio_dir / "vo.wav"
    sf.write(str(master_vo), timeline_audio, sample_rate)
    print(f"\n Master VO saved: {master_vo} ({len(timeline_audio)/sample_rate:.1f}s)")

    # Save manifest
    with open(audio_dir / "manifest.json", "w", encoding="utf-8") as f:
        json.dump({
            "engine": "edge-neural",
            "sample_rate": sample_rate,
            "shots": generated_shots
        }, f, indent=2, ensure_ascii=False)

    # Auto-mux into video
    video_path = reel_path / "final_intro_reel_94s.mp4"
    if video_path.exists():
        out_mux = reel_path / "final_intro_reel_94s_with_vo.mp4"
        print(f"\nMuxing audio into video: {video_path.name} -> {out_mux.name}")
        cmd = f'ffmpeg -y -i "{video_path}" -i "{master_vo}" -c:v copy -c:a aac -b:a 192k -shortest "{out_mux}"'
        os.system(cmd)
        if out_mux.exists():
            print(f" Final Muxed Reel Complete: {out_mux} ({out_mux.stat().st_size / (1024*1024):.2f} MB)")

if __name__ == "__main__":
    asyncio.run(main())
