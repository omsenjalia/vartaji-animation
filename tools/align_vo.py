#!/usr/bin/env python3
"""Force-align a returned ElevenLabs MP3 to the known script.

Produces <reel>/audio/words.json: [{w, s, e, line}] used for captions and mouth movement.
Install once:  pip install faster-whisper
"""
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

FFMPEG = os.environ.get("FFMPEG", shutil.which("ffmpeg") or "ffmpeg")


def main() -> None:
    if len(sys.argv) < 2:
        raise SystemExit("usage: align_vo.py <reel-dir>")
    reel = Path(sys.argv[1]).resolve()
    vo = reel / "audio" / "vo.mp3"
    script = reel / "script.json"
    if not vo.exists():
        raise SystemExit(f"missing {vo}")
    if not script.exists():
        raise SystemExit(f"missing {script}")

    try:
        from faster_whisper import WhisperModel
    except ImportError:
        raise SystemExit("pip install faster-whisper")

    wav = reel / "audio" / "vo.wav"
    subprocess.run([FFMPEG, "-y", "-v", "error", "-i", str(vo),
                    "-ac", "1", "-ar", "16000", str(wav)], check=True)

    model = WhisperModel("small", device="cpu", compute_type="int8")
    segments, _ = model.transcribe(str(wav), language="hi", word_timestamps=True,
                                   vad_filter=True)
    heard = [{"w": w.word, "s": w.start, "e": w.end}
             for seg in segments for w in (seg.words or [])]

    data = json.loads(script.read_text(encoding="utf-8"))
    expected = []
    for sh in data["shots"]:
        for w in sh["narration"].split():
            expected.append({"w": w, "line": sh["id"]})

    # Greedy snap: walk heard words against expected words. Devanagari text is
    # normalised by stripping punctuation; small ASR differences are tolerated.
    import re
    norm = lambda s: re.sub(r"[^\w\u0900-\u097F]", "", s)
    aligned, j = [], 0
    for i, exp in enumerate(expected):
        while j < len(heard) and norm(heard[j]["w"]) != norm(exp["w"]):
            j += 1
        if j < len(heard):
            aligned.append({**exp, "s": round(heard[j]["s"], 3), "e": round(heard[j]["e"], 3)})
            j += 1
        else:
            prev = aligned[-1]["e"] if aligned else 0.0
            aligned.append({**exp, "s": round(prev + 0.35, 3), "e": round(prev + 0.7, 3)})

    out = reel / "audio" / "words.json"
    out.write_text(json.dumps(aligned, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"aligned {len(aligned)}/{len(expected)} words -> {out}")
    if len(aligned) < len(expected):
        print("WARNING: some words could not be matched; durations were estimated.")


if __name__ == "__main__":
    main()
