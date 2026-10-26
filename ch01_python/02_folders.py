"""ch01-02 - Where things live

    python ch01_python/02_folders.py

The whole course uses three folders, and keeps to them strictly:

    data/raw    your footage. Put your films here. Nothing ever writes here.
    data/work   things the scripts make on the way. Can always be deleted.
    data/out    things you look at: cuts, pictures, pages.

This script makes the folders if they are missing and lists your footage.
"""
from pathlib import Path

# Path(__file__) is this file. .parent is the folder it is in.
# Two .parent steps up is the project folder, wherever you put it.
PROJECT = Path(__file__).resolve().parent.parent
RAW = PROJECT / "data" / "raw"
WORK = PROJECT / "data" / "work"
OUT = PROJECT / "data" / "out"

for folder in [RAW, WORK, OUT]:
    folder.mkdir(parents=True, exist_ok=True)     # make it, fine if it exists
    print("folder:", folder)

VIDEO_TYPES = [".mp4", ".mov", ".mkv", ".m4v", ".avi"]

print("\nfootage in data/raw:")
films = []
for path in sorted(RAW.iterdir()):
    if path.suffix.lower() in VIDEO_TYPES:
        films.append(path)
        size_mb = path.stat().st_size / 1_000_000
        print(f"  {path.name:<40} {size_mb:8.1f} MB")

        # spaces and accents in file names cause trouble on the command line
        if " " in path.name or not path.name.isascii():
            print("      ^ rename this: letters, numbers and _ only")

if not films:
    print("  (nothing yet - copy one or more video files into", RAW, ")")
else:
    print(f"\n{len(films)} films. Every script from now on works on all of them.")
