"""The catalog - the spine of the whole course.

Each film keeps its own table in data/work/<film>/shots.json. load() puts
all of them together into one table, so every later script sees the whole
archive at once:

    {
      "films": {
        "harbour": {"film": "harbour", "source": "data/raw/harbour.mp4",
                    "fps": 25.0, "duration": 312.4},
        ...
      },
      "shots": [
        {
          "id": "harbour/s0007", "film": "harbour",
          "start": 12.4, "end": 16.8, "duration": 4.4,
          "clip":     "data/work/harbour/shots/s0007.mp4",
          "keyframe": "data/work/harbour/keyframes/s0007.jpg",
          "tags":     [["water", 0.11], ["a boat", 0.09]],
          "caption":  "a grey harbour wall, a rope moving in the wind"
        },
        ...
      ]
    }

Every script from ch03 on does the same thing: load, add a field to some
shots, save. save() splits the table back into one file per film.
"""
from __future__ import annotations

import json
from pathlib import Path

from .paths import WORK


def film_file(film: str) -> Path:
    return WORK / film / "shots.json"


def write_film(info: dict, shots: list) -> Path:
    """Write one film's table. info has film, source, fps, duration."""
    path = film_file(info["film"])
    path.parent.mkdir(parents=True, exist_ok=True)
    data = {**info, "shots": shots}
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def load(must_exist: bool = True) -> dict:
    """Every film's table, merged into one."""
    cat = {"films": {}, "shots": []}
    for path in sorted(WORK.glob("*/shots.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        shots = data.pop("shots")
        cat["films"][data["film"]] = data
        cat["shots"] += shots
    if must_exist and not cat["shots"]:
        raise SystemExit("[!] no shots yet.\n"
                         "    Run ch03_shots/02_detect_shots.py and 03_split_shots.py first.")
    return cat


def save(cat: dict) -> None:
    """Write the merged table back, one file per film."""
    for film, info in cat["films"].items():
        write_film(info, [s for s in cat["shots"] if s["film"] == film])


def shot_id(film: str, i: int) -> str:
    return f"{film}/s{i:04d}"


def summary(cat: dict) -> str:
    n = len(cat["shots"])
    tagged = sum(1 for s in cat["shots"] if s.get("tags"))
    capt = sum(1 for s in cat["shots"] if s.get("caption"))
    return f"{len(cat['films'])} films · {n} shots · {tagged} tagged · {capt} captioned"
