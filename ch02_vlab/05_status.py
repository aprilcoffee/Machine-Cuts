"""ch02-05 - What has been done to which film?

    python ch02_vlab/05_status.py

One line per film, one column per expensive step. Run it whenever you
are unsure where you are - after adding footage, after a crash, at the
start of a session. "yes" means the result exists and is newer than what
it was made from (footage.done in vlab/footage.py).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from vlab import footage  # noqa: E402

# which script makes which column, and the week it arrives in
MADE_BY = {
    "proxy":   "ch02_vlab/03_make_proxies.py      (week 2)",
    "cuts":    "ch03_shots/02_detect_shots.py     (week 3)",
    "shots":   "ch03_shots/03_split_shots.py      (week 3)",
    "vectors": "ch05_siglip/02_embed_shots.py     (week 5)",
}

films = footage.require()
print(f"{'film':<32}" + "".join(f"{c:>9}" for c in MADE_BY))
for src in films:
    steps = footage.steps(src)
    print(f"{footage.name(src):<32}"
          + "".join(f"{'yes' if steps[c] else '-':>9}" for c in MADE_BY))

todo = footage.pending()
print(f"\n{len(films) - len(todo)} of {len(films)} films are fully processed.")
for src in todo:
    steps = footage.steps(src)
    missing = next(c for c in MADE_BY if not steps[c])
    print(f"  {footage.name(src):<30} next: {MADE_BY[missing]}")
