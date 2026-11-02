# Week 2 · ch02 · The toolbox: packages, `vlab`, proxies

## What you'll do

Last week was plain Python. This week the project gets two new things:

1. **packages** other people wrote (`requirements.txt`) — the image
   model, shot detection, the interface. Installed once, used for the
   rest of the term.
2. **`vlab/`**, the course's own small toolbox. Not new magic: the same
   ffprobe and ffmpeg calls you wrote by hand last week, moved into one
   drawer so every script stays one screen long.

Then the first real step on all of your footage: a proxy and a proxy
sheet per film.

| script | what it does |
|---|---|
| `01_check_env.py` | is every package installed? (plain Python, like week 1) |
| `02_meet_vlab.py` | last week's `03_read_footage.py` in 15 lines |
| `03_make_proxies.py` | a small copy of every film → `data/work/<film>/proxy.mp4` |
| `04_proxy_sheet.py` | one contact sheet per film → `data/out/sheets/<film>.jpg` |
| `05_status.py` | which film has which step done |

## New files in the project this week

Copy them next to `ch01_python/`:

```
machine-cut/
├─ requirements.txt     the list of packages
├─ vlab/                the toolbox
├─ ch01_python/
├─ ch02_vlab/           this week
└─ data/
```

---

## 1. Install the packages

In the VS Code terminal, with `(.venv)` at the start of the prompt:

```bash
pip install -r requirements.txt
```

(No `(.venv)`? Close the terminal with the bin icon and open a new one:
*Terminal → New Terminal*. Or do it all by clicking: `Cmd+Shift+P` →
**Python: Create Environment** → **Venv** → **Delete and Recreate** →
tick **requirements.txt**.)

It downloads about 1–2 GB (PyTorch is most of it) and takes 5–15
minutes. Do it on a good network — before class if you can. Then:

```bash
python ch02_vlab/01_check_env.py
```

Every line should say `[ok]`. Ollama (week 7) may still say `[--]`.

---

## 2. What `vlab` is

**Not a library. A drawer for the chores every script would otherwise
retype.** Open `ch01_python/03_read_footage.py` and
`ch02_vlab/02_meet_vlab.py` side by side: same result, 60 lines vs 15.
The 45 lines did not disappear — they are in `vlab/ff.py`, function
`info()`. Go and find them.

Every script from now on starts with the same lines:

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))   # the project folder
from vlab import ff, footage, paths
```

The third line tells Python "also look for code in the project folder",
so `from vlab import …` finds the `vlab/` folder. Nothing to install.

### The drawers you use this week

```python
footage.videos()          # every film in data/raw, as a list of paths
footage.name(src)         # data/raw/harbour.mp4 -> "harbour"
footage.work(src)         # data/work/harbour/ - that film's own folder
footage.done(out, src)    # True if `out` exists and is newer than `src`

ff.info(src)              # ffprobe -> {"duration", "fps", "width", ...}
ff.proxy(src, dst)        # the small copy
ff.run([...])             # any ffmpeg command; prints it before running
```

`ff.run` prints every command with a `$` in front. Read them: a lot of
"automation" is typing on your behalf. The rest of `vlab` (catalog,
frames, embed, search, llm, edl) arrives in use over the next weeks;
`vlab/README.md` lists all of it.

---

## 3. Many films, and never the same work twice

Every film in `data/raw` gets its own folder in `data/work`:

```
data/raw/harbour.mp4            data/work/harbour/proxy.mp4
data/raw/kitchen.mov      ->    data/work/kitchen/proxy.mp4
data/raw/tram_0412.mp4          data/work/tram_0412/proxy.mp4
```

Before any step, a script asks one question:

> is the result already there, and newer than what it was made from?

```python
if footage.done(proxy, src):
    print("skip")
    continue
```

Last week's `if target.exists()` — plus one check: if you replace a film
in `data/raw` with a new version, its file is newer than the old proxy,
so that film is redone and the others are left alone. This is the rule
the program `make` has used since 1976.

Try it:

```bash
python ch02_vlab/03_make_proxies.py    # makes every proxy
python ch02_vlab/03_make_proxies.py    # skip, skip, skip
# copy one more film into data/raw
python ch02_vlab/03_make_proxies.py    # only the new one
python ch02_vlab/05_status.py
```

---

## 4. Proxies and proxy sheets

A **proxy** is 480 lines high, 12 frames a second, no sound. All analysis
from next week on runs on it, never on the original: deciding what a shot
shows does not need 4K. The finished cut is always made from the
original. Small files for looking, big files for output.

A **proxy sheet** is last week's `06_contact_sheet.py`, made from the
proxy instead of the original — much faster, because the proxy is small.
Put all the sheets of your films side by side — that is the first time
your footage is a set of stills, which is the only thing an image model
will ever see.

---

## When it breaks

| symptom | why | fix |
|---|---|---|
| `ModuleNotFoundError: No module named 'vlab'` | `vlab/` not in the project folder | copy it next to `ch02_vlab/` |
| `ModuleNotFoundError` for numpy, cv2 … | packages not installed in this `.venv` | step 1 again; check `(.venv)` |
| `pip` fails on torch | Python too new | make the `.venv` with Python 3.12 |
| a film is never skipped | its file keeps getting a new date (synced folder) | keep `data/` outside iCloud/Dropbox |

## Think about

1. A proxy throws away most of the picture. What exactly could the
   machine miss later because of it?
2. Look at the proxy sheets side by side. Which film would you recognise
   from its sheet alone? Why?

## Homework

All your films with proxies and sheets. Hand in the sheets and the output
of `05_status.py`.
