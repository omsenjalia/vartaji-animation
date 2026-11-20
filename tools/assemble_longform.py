#!/usr/bin/env python3
"""Assemble a long-form episode from rendered chapter videos.

Reads a manifest in the shape of production/longform.example.json.
Expects each chapter's MP4 at out/<reel>/<reel>.mp4 (or set --root).

Not used by the reel pipeline. This is the long-form hook.
"""
import argparse
import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

FFMPEG = os.environ.get("FFMPEG", shutil.which("ffmpeg") or "ffmpeg")


def run(args: list[str]) -> None:
    subprocess.run(args, check=True)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("manifest")
    ap.add_argument("--root", default="out", help="directory holding chapter MP4s")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    m = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
    root = Path(args.root)
    out = Path(args.out or f"out/{m['id']}_longform.mp4")
    out.parent.mkdir(parents=True, exist_ok=True)

    videos = []
    for ch in m["chapters"]:
        p = root / ch["reel"] / f"{ch['reel']}.mp4"
        if not p.exists():
            raise SystemExit(f"missing chapter video: {p}")
        videos.append(p)

    if not videos:
        raise SystemExit("manifest has no chapters")
    if len(videos) == 1:
        run([FFMPEG, "-y", "-v", "error", "-i", str(videos[0]), "-c", "copy", str(out)])
        print("assembled (single chapter):", out)
        return

    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        lines = []
        for i, v in enumerate(videos):
            lines.append(f"file '{v.resolve()}'")
            if i < len(videos) - 1:
                # concat demuxer cannot crossfade; use filter_complex below when
                # transitions are requested. For now this is a hard cut.
                pass
        listfile = td / "concat.txt"
        listfile.write_text("\n".join(lines), encoding="utf-8")
        run([FFMPEG, "-y", "-v", "error", "-f", "concat", "-safe", "0",
             "-i", str(listfile), "-c", "copy", str(out)])
    print("assembled:", out, "chapters:", len(videos))
    print("NOTE: add chapter cards and crossfades once long-form production starts.")


if __name__ == "__main__":
    main()
