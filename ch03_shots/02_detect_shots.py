"""ch03-02 - Find the cuts in every film

    python ch03_shots/02_detect_shots.py
    -> data/work/<film>/cuts.json

Last week one frame became a histogram. Compare those numbers frame
after frame: inside a shot they barely change, at a cut they jump.
PySceneDetect does exactly that, and also handles fades, flashes and
very short shots. The result is a list of cut times for each film.

Films whose cuts are already found are skipped.
"""
import json
import sys
from pathlib import Path

from scenedetect import ContentDetector, detect

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from vlab import ff, footage, paths  # noqa: E402

THRESHOLD = 27.0    # how big a jump counts as a cut; lower = more cuts
MIN_LEN_FRAMES = 12 # a shot must be at least this many frames long


def secs(tc):
    """A PySceneDetect timecode in seconds (older versions spell it differently)."""
    try:
        return float(tc.seconds)
    except AttributeError:
        return float(tc.get_seconds())


for src in footage.require():
    proxy = footage.work(src) / "proxy.mp4"
    out = footage.work(src) / "cuts.json"
    if not proxy.exists():
        print(f"no proxy for {footage.name(src)} - run ch02_vlab/03_make_proxies.py first")
        continue
    if footage.done(out, proxy):
        print(f"skip  {footage.name(src)}")
        continue

    print(footage.name(src))
    scenes = detect(str(proxy), ContentDetector(threshold=THRESHOLD, min_scene_len=MIN_LEN_FRAMES),
                    show_progress=True)     # a progress bar while it reads the film
    if scenes:
        # every shot is (start, end); keep the first start and all the ends
        bounds = [secs(scenes[0][0])] + [secs(end) for _, end in scenes]
    else:
        bounds = [0.0, ff.info(proxy)["duration"]]   # no cut: one long take

    out.write_text(json.dumps({"bounds": bounds}, indent=2))
    print(f"{footage.name(src)}: {len(bounds) - 1} shots ->", paths.rel(out))
