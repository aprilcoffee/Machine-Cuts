"""ch02-02 - The same job, with the drawer

    python ch02_vlab/02_meet_vlab.py

Last week, ch01_python/03_read_footage.py took about 60 lines to read
the numbers out of every film. Here is the same thing with vlab, the
course's small toolbox:

    footage.videos()   every film in data/raw            (vlab/footage.py)
    ff.info(path)      ffprobe, turned into a dictionary (vlab/ff.py)

Nothing new happens. The 60 lines still run - they just live in vlab/
now, so that from here on every script can stay one screen long.
Open vlab/ff.py and find the function info(): you will recognise it.
"""
import sys
from pathlib import Path

# these two lines let a script in a chapter folder find vlab/
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from vlab import ff, footage  # noqa: E402

for src in footage.require():
    meta = ff.info(src)
    print(f"{footage.name(src):<30} {meta['width']}x{meta['height']}  "
          f"{meta['fps']:>6} fps  {meta['duration'] / 60:5.1f} min  "
          f"sound: {meta['acodec'] or 'none'}")

print("\nwhere things will go, per film:")
for src in footage.videos():
    print(f"  {src.name:<30} -> {footage.work(src)}")

print("\nOne thing vlab does that you did by hand: it prints every ffmpeg")
print("command before it runs it. Watch for lines starting with $ next.")
