"""ch03-04 - Which stills will the model look at?

    python ch03_shots/04_keyframe_sheet.py
    python ch03_shots/04_keyframe_sheet.py --frames 5
    -> data/out/keyframes.html   (open it in a browser)

The model never watches a shot. It looks at a few stills from it - the
rule is in vlab/frames.py: skip 10% at each end, then spread n stills
evenly over the middle. This page shows those stills for every shot.
A moment that is not sampled cannot be found later.
"""
import sys
from pathlib import Path

from tqdm import tqdm

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from vlab import catalog, cli, frames, paths  # noqa: E402

N = cli.flag("--frames", 3, int)    # stills per shot

cat = catalog.load()
page = f"<h1>{N} stills per shot</h1>"

for film in cat["films"]:
    page += f"<h2>{film}</h2>"
    shots = [s for s in cat["shots"] if s["film"] == film]
    for shot in tqdm(shots, desc=film, unit="shot"):
        # the stills (extracted the first time, reused after) and their times
        stills = frames.frames_for(cat, shot, N)
        times = ", ".join(f"{t:.1f}s" for t in frames.times_for(shot, N))
        page += f"<p>{shot['id']} · {shot['duration']:.1f}s · sampled at {times}<br>"
        page += "".join(f'<img src="{p.resolve().as_uri()}" height="120"> ' for p in stills)
        page += "</p>"

out = paths.OUT / "keyframes.html"
out.write_text(f"<meta charset='utf-8'><body style='font-family:sans-serif'>{page}", encoding="utf-8")
print("->", paths.rel(out))
print("   open it:", out.resolve().as_uri())
