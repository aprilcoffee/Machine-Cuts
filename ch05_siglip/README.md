# Week 5 · ch05 · SigLIP 2: pictures and words in one space

The model turns a picture into 768 numbers and a text into 768 numbers.
The closer they point, the higher the score (cosine similarity).

| script | what it does |
|---|---|
| `01_hello_siglip.py` | `test.jpg` against the words in `TEXTS` |
| `02_embed_your_tags.py` | your tagged shots and your words from ch04 → `data/out/your_embeddings.csv` |
| `03_compare_your_tags.py` | every word you used, sorted per shot → `data/out/your_tags.html` |
| `04_live_camera.py` | your webcam against the words in `TEXTS` · `q` quits |

Words go in exactly as you type them; nothing is added around them.
The whole archive comes next week (ch06).

## Install

```bash
pip install -r requirements.txt
```

This installs the libraries only. The model itself (about 1.5 GB) is
downloaded the first time you run `01_hello_siglip.py`, into
`~/.cache/huggingface`; after that it works offline.

## Reading the numbers

- **Only the order means something.** A word and a picture score about
  `0.00–0.15` whether they match or not; two pictures score `0.5–0.8`.
  Text and pictures sit in two separate regions of the space.
- **There is always a winner**, even when the right word isn't listed.
- **Never compare numbers across models**, and never use a fixed number
  as a cut-off.

## The model

`ViT-B-32-SigLIP2-256`, the smallest SigLIP 2, set in one line in
`vlab/embed.py`. It learned from billions of pictures and the text next
to them on the web — so it learned how people online caption pictures,
not the world.

## When it breaks

| symptom | fix |
|---|---|
| `none of your own words yet` | tag some shots in ch04 first |
| `no numbers yet` | run 02 before 03 |
| `No module named 'transformers'` | `pip install transformers` |
| `Warning: ... unauthenticated requests to the HF Hub` | harmless, ignore it |
| download hangs | campus network: download at home |
| `no camera 0` | close Zoom / Photo Booth, allow the camera, or set `CAMERA = 1` |
| umlauts or Chinese show as `?` in 04 | the camera window only draws plain letters |
| macOS: camera stays black | System Settings › Privacy & Security › Camera: allow your terminal / VS Code |

## Homework

Open `your_tags.html`. Find the shot where you and the model agree most,
and the one where you disagree most. One sentence each on why.
