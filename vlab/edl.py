"""Write a selection of shots as an EDL and a CSV.

An EDL (edit decision list) is the oldest file format editors share:
plain text, one event per shot, source in/out and record in/out. Premiere,
Resolve and Avid all read it, and it will still open in ten years.

A selection can come from several films. Each event names its own source
file, so the edit suite knows which film to relink it to.
"""
from __future__ import annotations

import csv
from pathlib import Path


def tc(seconds: float, fps: float) -> str:
    """seconds -> timecode HH:MM:SS:FF"""
    f = int(round(seconds * fps))
    h, rem = divmod(f, int(round(fps * 3600)))
    m, rem = divmod(rem, int(round(fps * 60)))
    s, ff = divmod(rem, int(round(fps)))
    return f"{h:02d}:{m:02d}:{s:02d}:{ff:02d}"


def write(cat: dict, picks: list, title: str, edl_path, csv_path) -> None:
    """picks is a list of (shot, score). Writes both files."""
    # An EDL has one frame rate for the whole list; the first film's wins.
    first = cat["films"][picks[0][0]["film"]] if picks else {}
    fps = first.get("fps") or 25.0

    lines = [f"TITLE: MACHINE CUT {title.upper()}", "FCM: NON-DROP FRAME", ""]
    rec = 0.0
    for i, (s, score) in enumerate(picks, 1):
        source = Path(cat["films"][s["film"]]["source"]).name
        tags = ", ".join(t for t, _ in s.get("tags", [])[:3])
        lines += [
            f"{i:03d}  AX       V     C        "
            f"{tc(s['start'], fps)} {tc(s['end'], fps)} "
            f"{tc(rec, fps)} {tc(rec + s['duration'], fps)}",
            f"* FROM CLIP NAME: {source}",
            f"* COMMENT: {s['id']} score={score:.4f} tags={tags}",
            "",
        ]
        rec += s["duration"]
    Path(edl_path).write_text("\n".join(lines), encoding="utf-8")

    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["id", "film", "score", "start_s", "end_s", "duration_s",
                    "start_tc", "end_tc", "tags", "caption", "clip"])
        for s, score in picks:
            w.writerow([s["id"], s["film"], f"{score:.4f}", s["start"], s["end"],
                        s["duration"], tc(s["start"], fps), tc(s["end"], fps),
                        "; ".join(t for t, _ in s.get("tags", [])),
                        s.get("caption", ""), s["clip"]])
