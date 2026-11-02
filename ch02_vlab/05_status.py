"""ch02-05 - What has been done to which film?

    python ch02_vlab/05_status.py

One line per film, one column per step. "yes" means that step is done
and up to date. Run it whenever you are unsure where you are.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from vlab import footage  # noqa: E402

# the steps a film goes through over the semester
STEPS = ["proxy", "cuts", "shots", "vectors"]

print(f"{'film':<32}" + "".join(f"{step:>9}" for step in STEPS))
for src in footage.require():
    done = footage.steps(src)
    print(f"{footage.name(src):<32}" + "".join(f"{'yes' if done[s] else '-':>9}" for s in STEPS))
