#!/usr/bin/env python3
"""Render pages of the clean Indore scan to PNG for vision reading.

Usage: python3 tools/render_source_pages.py 1 2 37-40
Writes /tmp/opencode/source_pages/<n>.png
"""
import sys
from pathlib import Path

import pymupdf

ROOT = Path(__file__).resolve().parents[1]
PDF = ROOT / "source" / "84-Vaishnav-Vaartaji-Vraj-Bhasha-Best-Quality-Indore-2005-Vaarta-Sahitya.pdf"
OUT = Path("/tmp/opencode/source_pages")


def parse(tokens: list[str]) -> list[int]:
    pages = []
    for tok in tokens:
        if "-" in tok:
            a, b = tok.split("-", 1)
            pages.extend(range(int(a), int(b) + 1))
        else:
            pages.append(int(tok))
    return pages


def main() -> None:
    if len(sys.argv) < 2:
        raise SystemExit("pass page numbers, e.g. 1 2 37-40")
    OUT.mkdir(parents=True, exist_ok=True)
    doc = pymupdf.open(PDF)
    for n in parse(sys.argv[1:]):
        if not 1 <= n <= len(doc):
            print("skip out of range", n)
            continue
        pix = doc[n - 1].get_pixmap(matrix=pymupdf.Matrix(1.8, 1.8))
        p = OUT / f"{n:03d}.png"
        pix.save(p)
        print(p)


if __name__ == "__main__":
    main()
