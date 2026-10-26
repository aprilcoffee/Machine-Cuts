"""ch01-04 - Cut a piece out of every film

    python ch01_python/04_trim.py

Takes LENGTH seconds from the middle of each film in data/raw and saves
them to data/out/ch01/. The cutting is done by ffmpeg; Python only builds
the command and runs it. You could type the same command yourself:

    ffmpeg -ss 60 -i data/raw/your_film.mp4 -t 5 data/out/ch01/your_film_trim.mp4

Run this script twice. The second time it skips every film, because the
piece is already there. Every script in this course works like that:
it never does the same work twice.
"""
import json
import subprocess
from pathlib import Path

LENGTH = 5          # seconds

PROJECT = Path(__file__).resolve().parent.parent
RAW = PROJECT / "data" / "raw"
OUT = PROJECT / "data" / "out" / "ch01"
VIDEO_TYPES = [".mp4", ".mov", ".mkv", ".m4v", ".avi"]

OUT.mkdir(parents=True, exist_ok=True)


def duration_of(path):
    """Ask ffprobe how long a file is, in seconds."""
    command = ["ffprobe", "-v", "error", "-print_format", "json",
               "-show_format", str(path)]
    result = subprocess.run(command, capture_output=True, text=True)
    return float(json.loads(result.stdout)["format"]["duration"])


for path in sorted(RAW.iterdir()):
    if path.suffix.lower() not in VIDEO_TYPES:
        continue

    target = OUT / f"{path.stem}_trim.mp4"
    if target.exists():
        print(f"skip  {target.name} (already there)")
        continue

    start = duration_of(path) / 2          # the middle of the film
    command = [
        "ffmpeg", "-y",
        "-ss", str(start),                 # jump to the start ...
        "-i", str(path),                   # ... of this file
        "-t", str(LENGTH),                 # take LENGTH seconds
        "-c:v", "libx264", "-c:a", "aac",  # re-encode, so the cut is exact
        str(target),
    ]
    print("$", " ".join(command))
    subprocess.run(command, capture_output=True)
    print(f"made  {target.name}  ({LENGTH}s from {start:.1f}s)\n")

print("\nOpen data/out/ch01/ and play the pieces.")
print("Then delete one of them and run this script again: only that one is made.")
