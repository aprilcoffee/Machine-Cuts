"""ch03-03 - Cut every film into shots

    python ch03_shots/03_split_shots.py
    -> data/work/<film>/shots/s0001.mp4 ...
    -> data/work/<film>/keyframes/s0001.jpg ...
    -> data/work/<film>/shots.json

For every film:
  1. cut each shot out of the ORIGINAL file (not the proxy)
  2. save one thumbnail from the middle of each shot
  3. write shots.json - one row per shot. From here on, that table is the film.

If you run 02 again with another threshold, the old shots (and any tags
they had) are thrown away and the film is cut again.
"""
import json
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from vlab import catalog, ff, footage, paths  # noqa: E402

MIN_SHOT = 0.5   # seconds; shorter shots are dropped (usually false cuts)

for src in footage.require():
    film = footage.name(src)
    work = footage.work(src)
    cutfile = work / "cuts.json"
    if not cutfile.exists():
        print(f"no cuts for {film} - run 02_detect_shots.py first")
        continue
    if footage.done(work / "shots.json", cutfile):
        print(f"skip  {film}")
        continue

    # start clean: old shots belong to old cuts
    for folder in ["shots", "keyframes", "stills"]:
        shutil.rmtree(work / folder, ignore_errors=True)

    bounds = json.loads(cutfile.read_text())["bounds"]
    meta = ff.info(src)
    print(f"\n{film}: {len(bounds) - 1} shots")

    shots, n = [], 0
    for a, b in zip(bounds, bounds[1:]):      # each pair of cuts = one shot
        if b - a < MIN_SHOT:
            continue
        n += 1
        clip = work / "shots" / f"s{n:04d}.mp4"
        key = work / "keyframes" / f"s{n:04d}.jpg"
        print(f"  [{n:>3}/{len(bounds) - 1}] {a:7.2f} -> {b:7.2f}  ({b - a:.2f}s)")
        ff.trim(src, clip, a, b, reencode=True, quiet=n > 1)   # print only the first ffmpeg command
        ff.frame_at(src, key, t=(a + b) / 2, quiet=True)        # the middle of the shot
        shots.append({
            "id": catalog.shot_id(film, n),
            "film": film,
            "start": round(a, 3), "end": round(b, 3), "duration": round(b - a, 3),
            "clip": paths.rel(clip),
            "keyframe": paths.rel(key),
            "tags": [], "caption": "",
        })

    info = {"film": film, "source": paths.rel(src), "fps": meta["fps"], "duration": meta["duration"]}
    path = catalog.write_film(info, shots)
    print(f"  {len(shots)} shots ->", paths.rel(path))
