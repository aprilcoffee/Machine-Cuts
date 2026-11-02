"""ch02-03 - A small copy of every film

    python ch02_vlab/03_make_proxies.py
    -> data/work/<film>/proxy.mp4

A proxy is a small, light copy of a film: 480 lines high, 12 frames a
second, no sound. All analysis from now on runs on the proxy, because a
file ten times smaller makes everything ten times faster. The finished
cut is always made from the original.

Films that already have a proxy are skipped, so you can run it again
after adding new footage.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from vlab import ff, footage, paths  # noqa: E402

HEIGHT = 480    # pixels
FPS = 12        # frames per second

for src in footage.require():
    dst = footage.work(src) / "proxy.mp4"
    # skip if the proxy exists and is newer than the film
    if footage.done(dst, src):
        print(f"skip  {footage.name(src)}")
        continue
    ff.proxy(src, dst, height=HEIGHT, fps=FPS)
    print("->", paths.rel(dst))
