"""ch01-03 - What is this file, actually?

    python ch01_python/03_read_footage.py

A video file is not "a video". It is a container (mp4, mov) holding
streams (picture, sound), each in its own codec (h264, aac), plus
numbers about it. The program ffprobe reads those numbers out.

You can run it yourself in the terminal first:

    ffprobe data/raw/your_film.mp4

This script runs the same program from Python, for every film, and
turns its answer into a table. Two new things:

  subprocess.run([...])   runs a terminal program from Python
  json.loads(text)        turns ffprobe's text answer into a dictionary
"""
import csv
import json
import subprocess
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
RAW = PROJECT / "data" / "raw"
OUT = PROJECT / "data" / "out"
VIDEO_TYPES = [".mp4", ".mov", ".mkv", ".m4v", ".avi"]


def probe(path):
    """Ask ffprobe about one file. Returns a dictionary."""
    command = ["ffprobe", "-v", "error", "-print_format", "json",
               "-show_format", "-show_streams", str(path)]
    result = subprocess.run(command, capture_output=True, text=True)
    return json.loads(result.stdout)


rows = []
for path in sorted(RAW.iterdir()):
    if path.suffix.lower() not in VIDEO_TYPES:
        continue

    data = probe(path)

    # the first time: look at everything ffprobe says (uncomment the next line)
    # print(json.dumps(data, indent=2))

    duration = float(data["format"]["duration"])
    video, audio = None, None
    for stream in data["streams"]:
        if stream["codec_type"] == "video" and video is None:
            video = stream
        if stream["codec_type"] == "audio" and audio is None:
            audio = stream
    if video is None:
        print(f"\n{path.name}: no picture in this file, skipped")
        continue

    # the frame rate comes as a fraction, e.g. "30000/1001" = 29.97
    top, bottom = video["r_frame_rate"].split("/")
    fps = float(top) / float(bottom)

    row = {
        "film": path.stem,
        "minutes": round(duration / 60, 2),
        "width": video["width"],
        "height": video["height"],
        "fps": round(fps, 3),
        "frames": int(duration * fps),
        "video codec": video["codec_name"],
        "sound": audio["codec_name"] if audio else "none",
    }
    rows.append(row)

    print(f"\n{path.name}")
    for key, value in row.items():
        print(f"  {key:>12} : {value}")

if not rows:
    raise SystemExit("no footage in data/raw - run 02_folders.py first")

# save the table: a .csv file opens in any spreadsheet program
OUT.mkdir(parents=True, exist_ok=True)
table = OUT / "footage.csv"
with open(table, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    writer.writeheader()
    writer.writerows(rows)

total = sum(r["frames"] for r in rows)
print(f"\n{len(rows)} films, {total} frames altogether")
print("table ->", table)
