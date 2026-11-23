# Week 5 · ch05 · SigLIP 2: pictures and words in one space

## What you'll do

| script | what it does |
|---|---|
| `01_hello_siglip.py` | one picture, a few words, one number each |
| `02_embed_your_tags.py` | last week's tagged shots and your words → `data/out/your_embeddings.csv` |
| `03_compare_your_tags.py` | your words next to the model's ranking → `data/out/your_tags.html` |

The whole archive comes next week (ch06).

---

## What the model does

It puts pictures and sentences into the **same space**. An image becomes
768 numbers; so does a sentence. If they are about the same thing, the
angle between them is small. "Similarity" is the cosine of that angle.

## Why SigLIP 2 and not CLIP

| | CLIP (OpenAI, 2021) | SigLIP 2 (Google, 2025) |
|---|---|---|
| training objective | compare within a batch (softmax) | each pair judged on its own (sigmoid) |
| in practice | general, serviceable | clearly better on **short, concrete** descriptions |
| vector length | 512 | 768 |
| size we use | ViT-B-32 | **ViT-B-32-SigLIP2-256** (the smallest) |
| download | ~350 MB | ~1.5 GB |
| CPU speed | 0.1–0.3 s / image | 0.1–0.3 s / image |

"Better on short concrete descriptions" is exactly what searching footage
is: you type `a hand holding a melting cone`, not an abstract.

Same code either way (both through `open_clip`), so switching back, or up
to a bigger model, is one line in `vlab/embed.py`.

> **How it learned:** billions of "image + the text next to it" pairs
> scraped from the web. So it did not learn *the world*. It learned **how
> people on the internet caption pictures.** That sentence explains every
> bias you are about to meet.

## Install

```bash
pip install torch torchvision open_clip_torch transformers
```

> `transformers` is needed by SigLIP 2's **tokenizer**,
> even though our code never calls it. Without it you get
> `ModuleNotFoundError: No module named 'transformers'`.

First run downloads ~1.5 GB into `~/.cache/huggingface`, then works offline.

## 01 · Hello

```bash
python ch05_siglip/01_hello_siglip.py
```

`test.jpg` sits next to the script, so this works on its own — no
archive, no `vlab`. Edit `TEXTS` at the top and run it again; swap
`IMAGE` for any picture you like.

```
0.0984  a destroyed house
0.0934  a red car
0.0376  a desert
0.0192  two people walking
0.0149  a city at night
0.0023  ice cream
```

Three things to say out loud:

1. **The size of the number means nothing on its own.** It is not a
   percentage of truth.
2. **Only the order means something** — and only among these words.
   Change the list, change the order.
3. **There is always a winner**, even when the right word isn't listed.

### Why are the numbers so small?

Between a word and a picture the cosine is small for **every** pair, good
or bad — roughly `0.00–0.15`. Text and pictures sit in two separate
regions of the same space (the **modality gap**). Compare a picture with
another picture and you get `0.5–0.8`. Another model may give `0.6` for
the same word and picture without being any more sure. So never compare
numbers across models, and never use a fixed number as a cut-off.

## 02 · Your tags, as numbers

```bash
python ch05_siglip/02_embed_your_tags.py
# -> data/out/your_embeddings.csv
```

Every shot you tagged in ch04 (its keyframe) and every word you used goes
through the same model. Each becomes one row of 768 numbers:

```
kind   name          0          1         ...  767
image  video/s0002   0.008347   0.053583  ...
text   red car       0.016761  -0.025884  ...
```

Open it in a spreadsheet. That is everything the model knows about your
shots and your words.

Each word is sent as `"a photo of {word}."` — the shape of the captions
the model learned from. The template lives in `vlab/embed.py`.

## 03 · Your words, as the model sees them

```bash
python ch05_siglip/03_compare_your_tags.py
# -> data/out/your_tags.html
```

For every shot you tagged: **all** the words you used anywhere, sorted by
how close they sit to that picture. The words you gave this shot are in
bold. The terminal prints where they landed:

```
video/s0002
    0.0824  red car              rank 1 of 3
    0.0553  hello                rank 2 of 3
video/s0003
    0.0326  this is              rank 3 of 3
```

A word at the top: you and the model agree. A word at the bottom is not
wrong. It is either about something the picture does not contain — the
day, the person, the reason — or not about anything you can see at all
(`this is`). Those are the words only you can use.

The model writes no tags here. **Ordering is the only thing it can do.**
It has no idea what a shot *is*; it can only say how close a picture sits
to a word.

## Which ViT, and can it be smaller?

`vlab/embed.py` names the model in one line. Ours is the smallest SigLIP 2
that exists in `open_clip`:

```python
MODEL, PRETRAINED = "ViT-B-32-SigLIP2-256", "webli"
```

Two different numbers hide in those names:

- **the patch size** (`-32`, `-16`) — how finely the picture is chopped
  before the model looks at it. At 256 px, `/32` gives 8×8 = **64**
  patches; `/16` gives 16×16 = **256** patches. Four times the pieces,
  roughly four times the work. `/32` sees composition; `/16` sees small
  things — a face across a room, text on a sign.
- **the model size** (`B`, `L`, `SO400M`, `gopt`) — how wide and deep the
  network is.

| name | what changes | note |
|---|---|---|
| `ViT-B-32-SigLIP2-256` | ours | smallest available |
| `ViT-B-16-SigLIP2-256` | 4× the patches | still 768 numbers — drop-in |
| `ViT-L-16-SigLIP2-256` | bigger network | 1024 numbers, so re-embed everything |

There is **no** smaller SigLIP 2 — no "S", no "tiny". Going below this
means leaving the family altogether (MobileCLIP, TinyCLIP), and paying for
it in quality. If you change the line, run `02_embed_your_tags.py` again.

## When it breaks

| symptom | why | fix |
|---|---|---|
| `none of your own words yet` | ch04 was skipped | tag some shots first |
| `no numbers yet` | 03 before 02 | run `02_embed_your_tags.py` |
| `No module named 'transformers'` | SigLIP 2's tokenizer needs it | `pip install transformers` |
| `Warning: ... unauthenticated requests to the HF Hub` | the model checks Hugging Face for updates | harmless, ignore it |
| download hangs | campus network blocks huggingface | download at home, copy `~/.cache/huggingface` |
| very slow first run | 1.5 GB download | once only |

## Think about

1. The model learned how people caption pictures online. Which things are
   rarely captioned — the everyday, the boring, the non-Western, the
   non-commercial? What happens to them in your archive?
2. For one of your shots the model puts your word last. Is that the model
   failing, or the word carrying something only you can see? Which of the
   two can be fixed?

## Homework

**A.** In `01_hello_siglip.py`, find the word that wins on `test.jpg`
although it is wrong. One sentence on why.

**B.** Open `your_tags.html`. Find the shot where you and the model agree
most, and the one where you disagree most. One sentence each on why —
and say which of the two tells you more about your footage.
