"""ch04-01 - The shape of your archive

    python ch04_catalog/02_inspect_catalog.py

Before any AI: for every film, how many shots, how long they are, and a
small histogram of shot lengths - how fast or slow each film cuts.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from vlab import catalog  # noqa: E402

cat = catalog.load()
print(f"\n{catalog.summary(cat)}\n")

EDGES = [0, 1, 2, 3, 5, 8, 13, 999]   # shot-length boxes, in seconds

for film in cat["films"]:
    durs = [s["duration"] for s in cat["shots"] if s["film"] == film]
    print(f"== {film}")
    print(f"   {len(durs)} shots · total {sum(durs):.1f}s · "
          f"mean {sum(durs) / len(durs):.2f}s · "
          f"shortest {min(durs):.2f}s · longest {max(durs):.2f}s")
    for lo, hi in zip(EDGES, EDGES[1:]):
        k = sum(1 for d in durs if lo <= d < hi)
        label = f"{lo}-{hi}s" if hi < 999 else f"{lo}s+"
        print(f"   {label:>7} |{'#' * k}")
    print()
