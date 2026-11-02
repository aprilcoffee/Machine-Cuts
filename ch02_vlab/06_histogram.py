"""ch02-06 - One frame as a histogram

    python ch02_vlab/06_histogram.py
    -> data/out/histograms/<film>.jpg

Takes one frame of a film and draws its brightness histogram under it.
A histogram counts how many pixels are dark, a bit less dark, ...
bright, in 32 boxes. It forgets WHERE things are and keeps only HOW
MUCH: the whole picture becomes 32 numbers.

Change SECONDS to a frame from another shot and compare the two.
"""
import sys
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from vlab import footage, paths  # noqa: E402

FILM = 0        # 0 = the first film in data/raw, 1 = the second ...
SECONDS = 10    # which moment of the film

film = footage.require()[FILM]

# 1. read one frame from the proxy
video = cv2.VideoCapture(str(footage.work(film) / "proxy.mp4"))
video.set(cv2.CAP_PROP_POS_MSEC, SECONDS * 1000)
ok, frame = video.read()
if not ok:
    raise SystemExit(f"no frame at {SECONDS}s - film too short, or no proxy yet (03_make_proxies.py)")

# 2. count the pixels per brightness: 32 boxes from black (0) to white (255)
gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
counts = cv2.calcHist([gray], [0], None, [32], [0, 256]).flatten()
print(counts.astype(int))

# 3. draw the 32 counts as bars under the frame
frame = cv2.resize(frame, (640, int(frame.shape[0] * 640 / frame.shape[1])))
chart = np.full((220, 640, 3), 255, dtype=np.uint8)
for i, count in enumerate(counts):
    top = 190 - int(count / counts.max() * 180)
    cv2.rectangle(chart, (i * 20 + 1, top), (i * 20 + 18, 190), (i * 8,) * 3, -1)   # each bar in its own grey
    cv2.rectangle(chart, (i * 20 + 1, top), (i * 20 + 18, 190), (0, 0, 0), 1)
cv2.putText(chart, "dark", (4, 210), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 0), 1)
cv2.putText(chart, "bright", (582, 210), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 0), 1)

out = paths.OUT / "histograms" / f"{footage.name(film)}.jpg"
out.parent.mkdir(parents=True, exist_ok=True)
cv2.imwrite(str(out), np.vstack([frame, chart]))
print("->", paths.rel(out))
