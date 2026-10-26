"""ch01-06 - One sheet per film

    python ch01_python/06_contact_sheet.py

The darkroom's old trick: one sheet, one roll. COLS x ROWS stills,
spread evenly over the whole film, glued into one picture by ffmpeg.
The fastest way to hold a whole film in a single glance.

Two ffmpeg filters do all the work:

    fps=1/10     keep one frame every 10 seconds
    tile=6x5     glue 30 of them into one picture, 6 across, 5 down

In the terminal it would be:

    ffmpeg -i data/raw/your_film.mp4 -vf "fps=1/10,scale=320:-2,tile=6x5" -frames:v 1 sheet.jpg

The sheets go to data/out/ch01/. Like 04_trim.py, a sheet that already
exists is skipped.
"""
import json
import subprocess
from pathlib import Path

COLS = 6            # stills across
ROWS = 5            # stills down
WIDTH = 320         # width of one still, in pixels

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

    target = OUT / f"{path.stem}_sheet.jpg"
    if target.exists():
        print(f"skip  {target.name} (already there)")
        continue

    # spread COLS x ROWS stills evenly over the whole film
    every = duration_of(path) / (COLS * ROWS)
    command = [
        "ffmpeg", "-y", "-i", str(path),
        "-vf", f"fps=1/{every:.3f},scale={WIDTH}:-2,tile={COLS}x{ROWS}:margin=8:padding=4",
        "-frames:v", "1",                  # the whole sheet is one picture
        str(target),
    ]
    print("$", " ".join(command))
    print("  (ffmpeg reads the whole film - a long film takes a moment)")
    subprocess.run(command, capture_output=True)
    print(f"made  {target.name}  (one still every {every:.1f}s)\n")

print("\nOpen data/out/ch01/ and put the sheets side by side.")
print("Change COLS and ROWS at the top, delete a sheet, run it again.")
