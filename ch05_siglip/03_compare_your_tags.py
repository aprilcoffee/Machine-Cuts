"""ch05-03 - Your words, as the model sees them

    python ch05_siglip/03_compare_your_tags.py
    -> data/out/your_tags.html

Reads the numbers from 02. For every shot you tagged, it measures how
close EVERY word you used sits to that picture - not only the words you
gave this shot - and sorts them. The page shows the keyframe with that
list; your words for the shot are highlighted.

The number is the cosine similarity (distance = 1 - cosine). Between a
word and a picture it is small for every pair, roughly 0.00-0.15: text
and pictures sit in two separate regions of the same space. So read the
order, not the size. Is your word near the top for this shot?
"""
import csv
import html
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from vlab import catalog, paths  # noqa: E402

CSV = paths.OUT / "your_embeddings.csv"
PAGE = paths.OUT / "your_tags.html"

if not CSV.exists():
    raise SystemExit("no numbers yet - run ch05_siglip/02_embed_your_tags.py first")
with open(CSV, encoding="utf-8-sig") as f:
    rows = list(csv.reader(f))[1:]
images = {r[1]: np.array(r[2:], float) for r in rows if r[0] == "image"}
texts = {r[1]: np.array(r[2:], float) for r in rows if r[0] == "text"}

shots = {s["id"]: s for s in catalog.load()["shots"]}

CSS = """body{font:14px/1.5 system-ui,sans-serif;background:#111;color:#eee;padding:28px}
h1{font-size:20px;margin:0 0 4px}.meta{color:#888;font-size:12.5px;margin-bottom:20px}
.shot{display:flex;gap:20px;margin-bottom:28px}
img{width:320px;aspect-ratio:16/9;object-fit:cover;border-radius:4px;background:#000}
.id{font-family:monospace;color:#7fd1c4;margin-bottom:6px}
.w{font-family:monospace;font-size:12.5px;color:#888}.w.mine{color:#fff;font-weight:bold}"""

cards = []
for sid, v in images.items():
    if sid not in shots:
        continue                                # the shot is gone since 02
    mine = shots[sid]["human_tags"]
    ranked = sorted(((float(v @ t), w) for w, t in texts.items()), reverse=True)

    print(sid)
    for r, (c, w) in enumerate(ranked, 1):
        if w in mine:
            print(f"    {c:.4f}  {w:20} rank {r} of {len(ranked)}")

    lines = "".join(f'<div class="w{" mine" if w in mine else ""}">{c:.4f}  {html.escape(w)}</div>'
                    for c, w in ranked)
    img = (paths.PROJECT / shots[sid]["keyframe"]).resolve().as_uri()
    cards.append(f'<div class="shot"><img src="{img}"><div>'
                 f'<div class="id">{html.escape(sid)}</div>{lines}</div></div>')

paths.ensure_dirs()
PAGE.write_text(
    f"<!doctype html><meta charset='utf-8'><title>your tags</title><style>{CSS}</style>"
    f"<h1>your words, as the model sees them</h1>"
    f"<div class='meta'>{len(images)} shots · {len(texts)} words · "
    f"cosine similarity, highest first · bold = the words you gave this shot</div>"
    f"{''.join(cards)}", encoding="utf-8")
print("->", paths.rel(PAGE))
