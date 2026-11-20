"""
Autonomous Voiceover Generator using ai4bharat/indic-parler-tts
Provides character-specific, deterministic voice memory across all Vartaji reels.
"""

import os
import sys
import json
import argparse
from pathlib import Path
import numpy as np
import soundfile as sf
import torch

WORKSPACE = Path(__file__).resolve().parent.parent
BIBLE_DIR = WORKSPACE / "bible" / "characters"

def load_character_voice(char_id: str):
    char_file = BIBLE_DIR / f"{char_id}.json"
    if not char_file.exists():
        # Fallback to narrator if specific character not found
        char_file = BIBLE_DIR / "narrator.json"
    
    with open(char_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    voice_cfg = data.get("voice", {})
    return {
        "speaker": voice_cfg.get("speaker", char_id),
        "prompt": voice_cfg.get("prompt", "An elderly Indian male speaker speaks with a calm, clear, slow and meditative voice. The recording is high quality and close-up."),
        "seed": voice_cfg.get("seed", 153500)
    }

def main():
    parser = argparse.ArgumentParser(description="Generate deterministic multi-character VO for Vartaji reel")
    parser.add_argument("reel_dir", type=str, help="Path to reel directory, e.g. reels/intro-gokulnath")
    parser.add_argument("--device", type=str, default="cpu", help="Device to run inference on (cpu/cuda)")
    parser.add_argument("--fp16", action="store_true", default=False, help="Use FP16 for reduced VRAM")
    parser.add_argument("--token", type=str, default=os.environ.get("HF_TOKEN"), help="Hugging Face access token (hf_...)")
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
    audio_dir = reel_path / "audio"
    shots_dir = audio_dir / "shots"
    audio_dir.mkdir(parents=True, exist_ok=True)
    shots_dir.mkdir(parents=True, exist_ok=True)

    print(f"--- Vartaji Autonomous VO Engine (ai4bharat/indic-parler-tts) ---")
    print(f"Reel: {script.get('title', reel_path.name)} ({total_duration}s, {len(shots)} shots)")
    print(f"Device: {args.device} (FP16: {args.fp16})")

    # Import parler-tts and transformers
    try:
        from parler_tts import ParlerTTSForConditionalGeneration
        from transformers import AutoTokenizer
    except ImportError as e:
        print(f"Error: Required packages not installed: {e}")
        print("Please ensure parler-tts and transformers are installed.")
        sys.exit(1)

    model_name = "ai4bharat/indic-parler-tts"
    print(f"Loading model {model_name}...")
    
    hf_token = args.token or os.environ.get("HF_TOKEN")
    torch_dtype = torch.float16 if (args.fp16 and args.device != "cpu") else torch.float32
    model = ParlerTTSForConditionalGeneration.from_pretrained(
        model_name,
        torch_dtype=torch_dtype,
        token=hf_token
    ).to(args.device)

    tokenizer = AutoTokenizer.from_pretrained(model_name, token=hf_token)
    description_tokenizer = AutoTokenizer.from_pretrained(model.config.text_encoder._name_or_path, token=hf_token)
    sample_rate = model.config.sampling_rate
    print(f"Model loaded. Sample rate: {sample_rate} Hz")

    total_samples = int(total_duration * sample_rate)
    timeline_audio = np.zeros(total_samples, dtype=np.float32)

    generated_shots = []

    for idx, shot in enumerate(shots):
        shot_id = shot.get("id", f"s{idx+1:02d}")
        text = shot.get("narration", "").strip()
        if not text:
            continue

        speaker_id = shot.get("speaker", script.get("speaker", "narrator"))
        char_voice = load_character_voice(speaker_id)
        shot_start = float(shot.get("start", 0))
        shot_end = float(shot.get("end", total_duration))
        available_dur = shot_end - shot_start

        print(f"\n[{shot_id}] ({shot_start:.1f}s - {shot_end:.1f}s, max {available_dur:.1f}s)")
        print(f"  Speaker: {speaker_id} ({char_voice['speaker']})")
        print(f"  Text: {text}")
        print(f"  Voice Prompt: {char_voice['prompt'][:60]}... (seed: {char_voice['seed']})")

        # Deterministic generation using character's permanent seed
        # We combine character seed with shot index to maintain distinct intonation per shot
        shot_seed = int(char_voice["seed"]) + idx * 7
        torch.manual_seed(shot_seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(shot_seed)

        desc_inputs = description_tokenizer(char_voice["prompt"], return_tensors="pt")
        prompt_inputs = tokenizer(text, return_tensors="pt")

        input_ids = desc_inputs.input_ids.to(args.device)
        attention_mask = desc_inputs.attention_mask.to(args.device)
        prompt_input_ids = prompt_inputs.input_ids.to(args.device)
        prompt_attention_mask = prompt_inputs.attention_mask.to(args.device)

        with torch.no_grad():
            generation = model.generate(
                input_ids=input_ids,
                attention_mask=attention_mask,
                prompt_input_ids=prompt_input_ids,
                prompt_attention_mask=prompt_attention_mask
            )
        
        audio_arr = generation.cpu().numpy().squeeze().astype(np.float32)
        dur = len(audio_arr) / sample_rate
        print(f"  Generated duration: {dur:.2f}s")

        shot_wav_path = shots_dir / f"{shot_id}.wav"
        sf.write(str(shot_wav_path), audio_arr, sample_rate)
        generated_shots.append({
            "id": shot_id,
            "speaker": speaker_id,
            "duration": dur,
            "start": shot_start,
            "end": shot_end
        })

        # Place on master timeline
        start_sample = int(shot_start * sample_rate)
        end_sample = min(start_sample + len(audio_arr), total_samples)
        copied_len = end_sample - start_sample

        # Subtle fade-in and fade-out to prevent clicks (20ms)
        fade_len = min(int(sample_rate * 0.02), copied_len // 4)
        if fade_len > 0:
            audio_arr[:fade_len] *= np.linspace(0.0, 1.0, fade_len)
            audio_arr[copied_len - fade_len:copied_len] *= np.linspace(1.0, 0.0, fade_len)

        timeline_audio[start_sample:end_sample] += audio_arr[:copied_len]

    # Normalize if any peaks occur
    max_amp = np.max(np.abs(timeline_audio))
    if max_amp > 0.95:
        print(f"\nNormalizing timeline audio (peak was {max_amp:.3f})...")
        timeline_audio = (timeline_audio / max_amp) * 0.92

    # Save full narration VO
    master_vo_path = audio_dir / "vo.wav"
    sf.write(str(master_vo_path), timeline_audio, sample_rate)
    print(f"\n Master VO saved: {master_vo_path} ({len(timeline_audio)/sample_rate:.1f}s)")

    # Save VO manifest
    manifest_path = audio_dir / "manifest.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump({
            "model": model_name,
            "sample_rate": sample_rate,
            "shots": generated_shots
        }, f, indent=2, ensure_ascii=False)
    print(f" Manifest saved: {manifest_path}")

    # Check for video file to auto-mux
    video_files = [
        reel_path / "final_intro_reel_94s.mp4",
        reel_path / "preview_v2.mp4",
        reel_path / "video.mp4"
    ]
    mux_target = None
    for vf in video_files:
        if vf.exists():
            mux_target = vf
            break

    if mux_target:
        out_mux = reel_path / "final_intro_reel_94s_with_vo.mp4"
        print(f"\nMuxing audio into video: {mux_target.name} -> {out_mux.name}")
        cmd = f"ffmpeg -y -i \"{mux_target}\" -i \"{master_vo_path}\" -c:v copy -c:a aac -b:a 192k -shortest \"{out_mux}\""
        os.system(cmd)
        if out_mux.exists():
            print(f" Final Muxed Reel Complete: {out_mux} ({out_mux.stat().st_size / (1024*1024):.2f} MB)")

if __name__ == "__main__":
    main()
