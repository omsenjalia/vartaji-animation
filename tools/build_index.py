#!/usr/bin/env python3
"""Extract the PDF to page-anchored text and build the varta / prasang index.

The OCR'd PDF mixes Devanagari with Gujarati glyphs. Nothing here cleans the
prose: it only builds navigation. Prose cleaning happens per-reel in
`reels/<id>/source.md` against canonical sources.
"""
import json
import re
from pathlib import Path

import pymupdf

ROOT = Path(__file__).resolve().parents[1]
PDF = ROOT / "source" / "84 vaishnav.pdf"
TEXT = ROOT / "source_text" / "all.txt"
IDX = ROOT / "research" / "index"

CANONICAL = """Damodardas Harsani|Krishnadas Meghan|Damodardas Sambhalware|The Londi (girl)|Padmanabhdas|Tulsa|Parvati|Raghunathdas|Rajo Kshatrani|Sheth Purshottamdas|Rukmini|Gopaldas|Ramdas Saraswat|Gadadhardas|Benidas & Madhavdas|Harivansh Pathak|Govinddas Bhalla|Amma Kshatrani|Gajjan Dhaavan|Narayandas Brahmachari|A Kshatrani|Jaydas Suri|Deva Kapur Kshatri|Dinkar Sheth|Dinkaddas Mukunddas|Prabhudas Jalota|Prabhudas Bhaat|Purshottamdas (husband & wife)|Tripurdas Kayasth|Puranmal Jeval Kshatri|Jadvendradas Kumhar|Gusaindas Saraswat|Madhav Bhatt Kashmiri|Gopaldas of Banswada|Padma Raval Sanchora|Purshottam Joshi Sanchora|Jagannath Joshi|Narhari Joshi|Rana Vyas Sanchora|Ramdas Sanchora|Govind Dube Sanchora|Raja Dube & Madhav Dube|Uttamsholkdas|Ishwar Dube Sanchora|Vasudevdas Chhakada|Baba Venu, Krishnadas Gheri & Jadav Khavas|Jagatanand Brahmin|Ananddas Vishvambhardas|A Brahmini of Adel|A Kshatrani of Prayag|Goraja & Samarai|Krishnadasi|Bula Mishra|Ramdas Mevada|Ramdas Chauhan|Ramanand Pandit|Vishnudas Chhipa|Jivandas Kshatri|Bhagvandas Saraswat|Bhagvandas Sanchora|Achyutdas Sanadya|Narayandas Kayasth|Narayandas Lohana Diwan|A Kshatrani of Singhnand|Virbai (Damodardas' mother)|Husband & wife from Singhnand|A carpenter of Adel|A Kshatri|Laghu Purshottamdas Kshatri|Kaviraj Bhaat|Gopaldas of Punjab|Janardhandas Chopra|Gadu Swami Sanadya|Kanhaiyalal Kshatri|Narhar Gaudiya|Narhar Sanyasi|Saddu Pande, Bhavani & Naro|Gopaldas Jatadhari|Krishnadas (husband & wife)|Santdas Chopra|Sundardas Madhavdas|Mavji Patel|Gopaldas Kshatri of Naroda|Badarayandas""".split("|")

START_RE = re.compile(r"^(अब|और|अन)\s+श्रीआचार्यजी")
PRASANG_RE = re.compile(r"वार्ता\s*प्रस(ङ|ं)ग|वार्ताप्रस(ङ|ं)ग|वातप्रिसद|प्रस(ङ|ं)ग")


def clean(s: str) -> str:
    return " ".join(s.split())


def main() -> None:
    IDX.mkdir(parents=True, exist_ok=True)
    TEXT.parent.mkdir(parents=True, exist_ok=True)
    doc = pymupdf.open(PDF)

    pages = []
    for i, page in enumerate(doc):
        t = page.get_text()
        pages.append(t)

    TEXT.write_text(
        "\n".join(f"=== PAGE {i+1} ===\n{t}" for i, t in enumerate(pages)),
        encoding="utf-8",
    )

    # Section starts: a 'अब/और/अन श्रीआचार्यजी...' line that actually announces
    # a वार्ता. Continuation lines (e.g. p7) don't mention वार्ता and are skipped.
    starts = []
    for i, t in enumerate(pages):
        if i + 1 < 3:
            continue
        lines = t.split("\n")
        for j, line in enumerate(lines):
            s = clean(line)
            window = " ".join(lines[j:j + 8])
            if (len(s) > 12 and START_RE.match(s)
                    and ("सेवक" in window or "सेवकनी" in window)
                    and "वार्ता" in window):
                starts.append({"page": i + 1, "heading": window[:360]})
                break

    sections = []
    for n, st in enumerate(starts):
        end = starts[n + 1]["page"] - 1 if n + 1 < len(starts) else len(pages)
        heading = st["heading"]
        # Devanagari name: text after 'सेवक/सेवकनी' up to the 'वार्ता' clause.
        m = re.search(r"सेवक(?:नी)?[,]?\s*(.{3,150})", heading)
        name_hi = clean(m.group(1)) if m else heading[:80]
        name_hi = re.split(r"\s+(?:तिनकी|तिनकौ|जिनकी|वार्ता)", name_hi)[0]
        name_hi = re.sub(r"^(सो\s+)?श्रीआचार्यजी\s*(महाप्रभुनके|महाप्रमुखके|महाप्रभुके|के)?\s*", "", name_hi)
        name_hi = name_hi.strip(" ,.;।") or heading[:60]
        # Canonical names are kept as a separate cross-reference list, NOT zipped
        # by index: this PDF omits the Londi section and adds Jagannath's mother,
        # so index-based matching would silently mis-name most Vaishnavs.
        sections.append({
            "id": f"v{n+1:02d}",
            "n": n + 1,
            "name_hi": name_hi,
            "name_en": None,
            "start_page": st["page"],
            "end_page": end,
            "heading": heading,
            "prasang_markers": sum(
                len(PRASANG_RE.findall(pages[p - 1]))
                for p in range(st["page"], end + 1)
            ),
        })

    (IDX / "canonical_names.json").write_text(
        json.dumps({"names": CANONICAL}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (IDX / "vaishnavs.json").write_text(
        json.dumps({
            "source": PDF.name,
            "pages": len(pages),
            "intro_pages": [1, 2],
            "note": "Sections and page ranges are OCR-derived. This edition omits the Londi varta and includes Jagannath Joshi's mother, so sections are NOT zipped 1:1 with the canonical 84-name list. Verify against the printed book before scripting.",
            "vaishnavs": sections,
        }, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    prasangs = []
    for sec in sections:
        # One prasang per section is a placeholder. Real prasang boundaries are
        # decided during the treatment stage by reading the section, not by
        # trusting OCR markers (the printed markers number only ~30 total).
        prasangs.append({
            "id": f"{sec['id']}-p1",
            "vaishnav_id": sec["id"],
            "part": 1,
            "title": sec["name_hi"] or sec["id"],
            "pages": [sec["start_page"], sec["end_page"]],
            "archetype": None,
            "status": "indexed",
        })
    (IDX / "prasangs.json").write_text(
        json.dumps({"prasangs": prasangs}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(f"pages={len(pages)} sections={len(sections)} prasangs={len(prasangs)}")
    for s in sections[:6]:
        print(f"  {s['id']} p{s['start_page']}-{s['end_page']} {s['name_en']} ({s['name_hi'][:40]})")
    print("  ...")
    for s in sections[-4:]:
        print(f"  {s['id']} p{s['start_page']}-{s['end_page']} {s['name_en']} ({s['name_hi'][:40]})")


if __name__ == "__main__":
    main()
