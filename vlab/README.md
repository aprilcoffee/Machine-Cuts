# `vlab/` — the shared drawer

**`vlab` is not a library. It is a drawer for the things every script
would otherwise retype.** It arrives in week 2; week 1 does everything by
hand, so you have seen what is inside before you use it.

> **Why it exists.** Without it, half of `ch06_search_edit/02_auto_edit.py`
> would be ffmpeg string handling, and the actual lesson — select, order,
> join — would be buried under it.
>
> **It is not a black box.** Each file is a few dozen lines of ordinary
> Python. When something breaks, open it.

---

## How a script reaches it

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))   # the project folder
from vlab import catalog, footage, paths
```

No installation step. The scripts run top to bottom: no `main()`, no
classes. Settings in capitals near the top, the work below. Nothing
imports a chapter script; anything two weeks share lives here.

## The modules

| module | what it holds | first used |
|---|---|---|
| `paths.py` | where `data/raw`, `data/work`, `data/out` are | week 2 |
| `footage.py` | **which films there are, and what is already done** | week 2 |
| `ff.py` | a thin ffmpeg wrapper: probe, trim, proxy, stills, conform, concat, label | week 2 |
| `catalog.py` | read and write the per-film tables, as one archive | week 3 |
| `frames.py` | **which stills represent a shot** — the most consequential rule here | week 3 |
| `embed.py` | load SigLIP 2; turn images and sentences into vectors | week 5 |
| `search.py` | rank shots, rank films, cast a storyboard | week 6 |
| `llm.py` | talk to a local Ollama (Gemma), text and vision | week 7 |
| `edl.py` | write a selection as an EDL and a CSV | week 8 |
| `cli.py` | the smallest possible argument parsing | everywhere |

### `footage.py` — many films, no double work

```python
footage.videos()        # every film in data/raw
footage.require()       # the same, or a helpful stop if there are none
footage.name(src)       # data/raw/harbour.mp4 -> "harbour"
footage.work(src)       # data/work/harbour/
footage.done(out, src)  # out exists and is newer than src -> skip
footage.steps(src)      # {"proxy": True, "cuts": True, "shots": False, ...}
footage.pending()       # films with a step still to do
```

`done()` is the rule `make` has used since 1976. Every expensive step in
the course asks it before starting, which is why every script — and the
whole pipeline — can be run again at any time and only does new work.

### `ff.py`

```python
ff.info(path)                       # duration, fps, size, codecs
ff.trim(src, dst, start, end)       # cut, re-encoded so the cut lands exactly
ff.proxy(src, dst, height, fps)     # the small copy that analysis runs on
ff.frame_at(src, dst, t)            # one still at time t
ff.concat([clips], dst)             # join clips, even from different films
ff.burn_text(src, dst, "label")     # a line of text in the picture
ff.run([...])                       # any ffmpeg command, printed first
```

`concat()` conforms every clip first — same size (black bars where the
shape differs), same frame rate, a silent track where there is no sound
— because clips from different films cannot be glued together otherwise.
`run()` prints ffmpeg's own error lines before raising, so a failure
explains itself. `burn_text()` draws the label with Pillow and lays it on
with ffmpeg's `overlay`, because many ffmpeg builds have no `drawtext`.

### `catalog.py`

```python
cat = catalog.load()      # every film's shots.json, merged:
                          #   {"films": {name: info}, "shots": [...]}
catalog.save(cat)         # written back, one file per film
catalog.summary(cat)      # "3 films · 212 shots · 212 tagged · 0 captioned"
```

A shot's id is `film/s0007`. Scripts add keys to shots and save; nothing
else.

### `frames.py` — read this one

```python
frames.times_for(shot, n)        # the timecodes that will be sampled
frames.frames_for(cat, shot, n)  # those stills, extracted once, then reused
```

Skip 10% at each end of the shot, then spread `n` stills across the
middle. A moment that is never sampled does not exist downstream.

### `embed.py` and `search.py`

```python
embed.encode_images([paths])           # -> (n, 768) normalised vectors
embed.encode_texts(["a dark room"])    # -> (n, 768)

search.vectors(cat)                    # all films' vectors, stacked
search.rank(cat, "a dark room")        # [(shot, score), ...] best first
search.by_film(cat, "a dark room", 3)  # [(film, score, best 3 shots), ...]
search.cast(cat, lines)                # one shot per storyboard line
```

### `llm.py`, `edl.py`, `cli.py`

```python
llm.require("gemma3:4b")
llm.generate(prompt, images=[...], stream=True)

edl.write(cat, picks, title, edl_path, csv_path)

cli.positionals()            # the real arguments
cli.flag("--top", 8, int)    # --top 5 -> 5
cli.has("--burn")            # True if present
```

---

## Who calls what

```
week 1  (nothing - plain Python)
week 2  paths · footage · ff
week 3  paths · footage · ff · catalog · frames · cli
week 4  paths · catalog · cli
week 5  paths · footage · catalog · frames · embed · search · cli
week 6  paths · catalog · search · ff · cli
week 7  paths · catalog · llm · cli
week 8  paths · footage · catalog · search · edl · ff · cli
```

## The lines you might want to change

```python
vlab/embed.py    MODEL, PRETRAINED = "ViT-B-32-SigLIP2-256", "webli"
vlab/llm.py      TEXT_MODEL = "gemma3:4b"
vlab/frames.py   EDGE = 0.10        # how much of each shot end to skip
vlab/footage.py  VIDEO_EXT = {...}  # which files in data/raw count as films
```
