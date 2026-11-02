"""ch02-04 - One contact sheet per film

    python ch02_vlab/04_proxy_sheet.py
    -> data/out/sheets/<film>.jpg

The darkroom's contact sheet: 30 stills spread evenly over the whole
film, glued into one picture. The fastest way to see a whole film at
once - made from the proxy, so it is quick.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from vlab import ff, footage, paths  # noqa: E402

COLS, ROWS = 6, 5    # 6 x 5 = 30 stills

for src in footage.require():
    proxy = footage.work(src) / "proxy.mp4"
    sheet = paths.OUT / "sheets" / f"{footage.name(src)}.jpg"
    if not proxy.exists():
        print(f"no proxy for {footage.name(src)} - run 03_make_proxies.py first")
        continue
    if footage.done(sheet, proxy):
        print(f"skip  {footage.name(src)}")
        continue

    every = max(ff.info(proxy)["duration"] / (COLS * ROWS), 0.1)   # seconds between stills
    sheet.parent.mkdir(parents=True, exist_ok=True)
    # fps=1/every: one still every `every` seconds · tile: glue them into a grid
    ff.run([ff.FFMPEG, "-y", "-i", str(proxy),
            "-vf", f"fps=1/{every:.4f},scale=320:-2,tile={COLS}x{ROWS}:margin=8:padding=6",
            "-frames:v", "1", "-q:v", "3", str(sheet)])
    print("->", paths.rel(sheet))
