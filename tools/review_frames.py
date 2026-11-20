#!/usr/bin/env python3
"""Extract every frame of a reel to PNG, then build review contact sheets.

After each reel is rendered, run this, then spawn 3–4 reviewers over the
contact sheets. Full frame set is kept for pixel-level checks.

Usage:
  python3 tools/review_frames.py reels/intro-gokulnath/preview_stick.mp4 stick
  python3 tools/review_frames.py reels/intro-gokulnath/preview_zach.mp4 zach
"""
import argparse
import subprocess
import os
import shutil
from pathlib import Path

from PIL import Image, ImageDraw

FFMPEG = os.environ.get("FFMPEG", shutil.which("ffmpeg") or "ffmpeg")
FFPROBE = os.environ.get("FFPROBE", shutil.which("ffprobe") or "ffprobe")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("video")
    ap.add_argument("label")
    ap.add_argument("--sample", type=float, default=0.5, help="contact-sheet sample fps")
    ap.add_argument("--cols", type=int, default=5)
    ap.add_argument("--rows", type=int, default=4)
    args = ap.parse_args()

    video = Path(args.video)
    review = video.parent / "review" / args.label
    frames = review / "frames"
    sheets = review / "sheets"
    frames.mkdir(parents=True, exist_ok=True)
    sheets.mkdir(parents=True, exist_ok=True)

    subprocess.run([FFMPEG, "-y", "-v", "error", "-i", str(video),
                    "-vsync", "0", str(frames / "f_%05d.png")], check=True)
    files = sorted(frames.glob("f_*.png"))
    print("frames", len(files))

    # derive source fps from count / duration via ffprobe
    out = subprocess.run([FFPROBE, "-v", "error",
                          "-show_entries", "format=duration", "-of",
                          "default=nw=1:nk=1", str(video)],
                         capture_output=True, text=True, check=True).stdout.strip()
    dur = float(out)
    src_fps = len(files) / dur
    step = max(1, round(src_fps / args.sample))
    sampled = [(i, files[i]) for i in range(0, len(files), step)]

    per = args.cols * args.rows
    tw, th = 200, 356
    for si in range(0, len(sampled), per):
        chunk = sampled[si:si + per]
        sheet = Image.new("RGB", (args.cols * (tw + 6), args.rows * (th + 22)), (14, 14, 14))
        d = ImageDraw.Draw(sheet)
        for j, (idx, f) in enumerate(chunk):
            im = Image.open(f).convert("RGB")
            im.thumbnail((tw, th))
            x = (j % args.cols) * (tw + 6) + 3
            y = (j // args.cols) * (th + 22) + 20
            sheet.paste(im, (x, y))
            d.text((x, y - 17), f"{idx / src_fps:05.1f}s", fill=(255, 255, 255))
        p = sheets / f"sheet_{si // per:02d}.png"
        sheet.save(p)
    print("sheets", len(list(sheets.glob('*.png'))), "->", sheets)


if __name__ == "__main__":
    main()
