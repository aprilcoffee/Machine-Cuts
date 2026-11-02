"""ch02-04 - One sheet per film

    python ch02_vlab/04_proxy_sheet.py
    -> data/out/sheets/<film>.jpg

The darkroom's old trick: one sheet, one roll. COLS x ROWS stills,
spread evenly over the whole proxy, glued into one image by ffmpeg's
tile filter. Still the fastest way for a human to hold a whole film in a
single glance - and the first time the film becomes a stack of stills,
which is the only thing an image model can ever look at.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from vlab import ff, footage, paths  # noqa: E402

COLS, ROWS = 6, 5

for src in footage.require():
    proxy = footage.work(src) / "proxy.mp4"
    sheet = paths.OUT / "sheets" / f"{footage.name(src)}.jpg"
    if not proxy.exists():
        print(f"no proxy for {footage.name(src)} - run 03_make_proxies.py first")
        continue
    if footage.done(sheet, proxy):
        print(f"skip  {footage.name(src)} (sheet already made)")
        continue

    every = max(ff.info(proxy)["duration"] / (COLS * ROWS), 0.1)
    sheet.parent.mkdir(parents=True, exist_ok=True)
    # fps=1/every   one still every `every` seconds
    # tile=6x5      glue 30 of them into one picture
    ff.run([ff.FFMPEG, "-y", "-i", str(proxy),
            "-vf", f"fps=1/{every:.4f},scale=320:-2,tile={COLS}x{ROWS}:margin=8:padding=6",
            "-frames:v", "1", "-q:v", "3", str(sheet)])
    print(f"  one still every {every:.1f}s ->", paths.rel(sheet))

print("\nOpen data/out/sheets/ and put the sheets side by side.")
