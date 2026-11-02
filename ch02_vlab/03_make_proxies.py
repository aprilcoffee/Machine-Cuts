"""ch02-03 - A small copy of every film

    python ch02_vlab/03_make_proxies.py

A proxy is a small, light copy of a film: 480 lines high, 12 frames a
second, no sound. All analysis from week 3 on (shot detection, the
image model) runs on the proxy, never on the original - deciding what a
shot shows does not need 4K, and a file ten times smaller makes the
class ten times faster.

The finished cut is always made from the ORIGINAL. Small files for
analysis, big files for output: that two-track shape is the whole
pipeline.

Run it twice. The second time, every film is skipped: footage.done()
sees that the proxy is newer than the film it was made from. Add a new
film to data/raw and only that one is made.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from vlab import ff, footage, paths  # noqa: E402

for src in footage.require():
    dst = footage.work(src) / "proxy.mp4"
    if footage.done(dst, src):
        print(f"skip  {footage.name(src)} (proxy already made)")
        continue

    print(f"\n{footage.name(src)}")
    ff.proxy(src, dst, height=480, fps=12)

    before, after = ff.info(src), ff.info(dst)
    print(f"  source {before['width']}x{before['height']} {before['size_mb']} MB"
          f"  ->  proxy {after['width']}x{after['height']} {after['size_mb']} MB")
    print("  ->", paths.rel(dst))
