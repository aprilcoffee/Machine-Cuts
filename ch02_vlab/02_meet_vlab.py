"""ch02-02 - Last week's 03_read_footage.py, with vlab

    python ch02_vlab/02_meet_vlab.py

Reads resolution, frame rate and length of every film in data/raw -
the same thing last week's script did in about 60 lines. Those lines did
not disappear: they now live in vlab/ff.py, function info(). From here
on every script uses vlab, so it can stay one screen long.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))   # lets this script find vlab/
from vlab import ff, footage  # noqa: E402

# footage.require(): every film in data/raw
# ff.info(): ask ffprobe about one file, get a dictionary back
for src in footage.require():
    meta = ff.info(src)
    print(f"{footage.name(src):<30} {meta['width']}x{meta['height']}  "
          f"{meta['fps']:>6} fps  {meta['duration'] / 60:5.1f} min")
