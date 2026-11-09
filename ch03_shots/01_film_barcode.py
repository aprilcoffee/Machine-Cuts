"""ch03-01 - The whole film as one strip of colour

    python ch03_shots/01_film_barcode.py
    -> data/out/barcodes/<film>.jpg

Every frame is squashed into ONE colour: the average of all its pixels.
Those colours are laid side by side, first frame on the left, last on
the right, and stretched into a picture. A "film barcode".

You can read the editing in it: a long shot is a wide calm band, fast
cutting is a flicker of thin lines, a cut is where the colour jumps.
That jump is what the next script, 02_detect_shots.py, looks for.
"""
import sys
from pathlib import Path

import cv2
import numpy as np
from tqdm import tqdm

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from vlab import footage, paths  # noqa: E402

EVERY = 6       # use every 6th frame: the proxy has 12 a second, so 2 colours a second
WIDTH = 1600    # pixels; each column blends the frames that fall into it
HEIGHT = 400

for src in footage.require():
    proxy = footage.work(src) / "proxy.mp4"
    out = paths.OUT / "barcodes" / f"{footage.name(src)}.jpg"
    if not proxy.exists():
        print(f"no proxy for {footage.name(src)} - run ch02_vlab/03_make_proxies.py first")
        continue
    if footage.done(out, proxy):
        print(f"skip  {footage.name(src)}")
        continue

    # 1. one average colour per sampled frame
    colours = []
    video = cv2.VideoCapture(str(proxy))
    total = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    for i in tqdm(range(total), desc=footage.name(src), unit="frame"):
        if not video.grab():                        # step to the next frame
            break
        if i % EVERY == 0:                          # only every EVERY-th one is looked at
            ok, frame = video.retrieve()
            colours.append(frame.mean(axis=(0, 1)))  # mean over height and width -> (blue, green, red)

    # 2. a picture 1 pixel high, one pixel per colour ...
    strip = np.array([colours], dtype=np.uint8)

    # 3. ... stretched to WIDTH x HEIGHT (neighbouring frames blend together)
    barcode = cv2.resize(strip, (WIDTH, HEIGHT), interpolation=cv2.INTER_AREA)

    out.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(out), barcode)
    print(f"{footage.name(src)}: {len(colours)} colours ->", paths.rel(out))
