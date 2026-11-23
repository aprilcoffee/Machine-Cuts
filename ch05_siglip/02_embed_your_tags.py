"""ch05-02 - Your tags, as numbers

    python ch05_siglip/02_embed_your_tags.py
    -> data/out/your_embeddings.csv

Every shot you tagged last week (its keyframe) and every word you used go
through the same model as in 01. Each becomes 768 numbers - one row of
the CSV:

    kind   name          0          1        ...  767
    image  video/s0002   0.012345  -0.045678 ...
    text   red car       ...

Open it in a spreadsheet: this is everything the model knows about your
shots and your words. 03 measures how close the rows are to each other.

Each word goes in exactly as you typed it in ch04 - nothing is added
around it.
"""
import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from vlab import catalog, embed, paths  # noqa: E402

CSV = paths.OUT / "your_embeddings.csv"

cat = catalog.load()
tagged = [s for s in cat["shots"] if s.get("human_tags")]
if not tagged:
    raise SystemExit("[!] none of your own words yet.\n"
                     "    Run ch04_catalog/03_browse_and_tag.py and tag some shots.")
words = sorted({w for s in tagged for w in s["human_tags"]})

print(f"{len(tagged)} shots you tagged · {len(words)} different words")
print(f"loading {embed.MODEL} ...")
images = embed.encode_images([paths.PROJECT / s["keyframe"] for s in tagged])
texts = embed.encode_texts(words, template="{}")   # exactly as typed

paths.ensure_dirs()
with open(CSV, "w", newline="", encoding="utf-8-sig") as f:
    out = csv.writer(f)
    out.writerow(["kind", "name"] + list(range(images.shape[1])))
    for s, v in zip(tagged, images):
        out.writerow(["image", s["id"]] + [f"{x:.6f}" for x in v])
    for w, v in zip(words, texts):
        out.writerow(["text", w] + [f"{x:.6f}" for x in v])

print(f"{len(tagged)} pictures + {len(words)} words, {images.shape[1]} numbers each")
print("->", paths.rel(CSV))
