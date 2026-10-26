# Week 1 · ch01 · Plain Python, plain ffmpeg

## What you'll do

No AI and no libraries this week. Only Python itself and one program,
ffmpeg. By the end of the session you can:

- open the project in VS Code and run a script with one click
- organise footage into the three folders the course uses
- read the numbers inside a video file
- cut a piece out of every film, from Python and from the terminal
- break a video on purpose

| script | what it does |
|---|---|
| `01_hello.py` | your first script: print, variables, a loop |
| `02_folders.py` | makes `data/raw`, `data/work`, `data/out`; lists your footage |
| `03_read_footage.py` | asks ffprobe about every film, saves a table |
| `04_trim.py` | cuts 5 seconds from the middle of every film |
| `05_glitch.py` | damages the bytes of those pieces: a glitch video |

Every script runs without typing anything: open it, press ▶.

---

## Setup (once)

### 1. Install three things

| | macOS | Windows |
|---|---|---|
| **Python 3.12** | [python.org/downloads](https://www.python.org/downloads/) | same — tick **"Add python.exe to PATH"** |
| **VS Code** | [code.visualstudio.com](https://code.visualstudio.com) | same |
| **ffmpeg** | `brew install ffmpeg` (needs [Homebrew](https://brew.sh)) | `winget install ffmpeg` |

Use Python 3.11 or 3.12. Brand-new versions are often not supported yet
by the image-model packages we install in week 2.

### 2. Open the project in VS Code

*File → Open Folder…* → choose the `machine-cut` folder (the one that
holds `ch01_python`). Not the `ch01_python` folder itself.

VS Code asks to install the **Python** extension — say yes.

### 3. Make the project's own Python (a virtual environment)

`Cmd+Shift+P` (Windows: `Ctrl+Shift+P`) → **Python: Create Environment**
→ **Venv** → pick Python 3.12.

A `.venv` folder appears. That is a private copy of Python for this
project, so nothing you install here touches the rest of your computer.
This week we install nothing into it; next week we fill it.

Check the bottom-right corner of VS Code: it should say something like
`3.12.x ('.venv')`. If not, click it and choose the `.venv` one.

### 4. Press Run

Open `ch01_python/01_hello.py` and press **▶** (top right, "Run Python
File"). A terminal opens at the bottom and prints the result.

That terminal is a real terminal. You can type in it too — never used
one? [`TERMINAL.md`](TERMINAL.md) is a one-page guide for Mac and Windows.

```bash
python ch01_python/01_hello.py
ffmpeg -version
```

If `ffmpeg -version` prints "command not found", ffmpeg is not installed
or VS Code was opened before you installed it — quit VS Code completely
and open it again.

---

## Folders: where things live

```
machine-cut/
├─ ch01_python/      this week's scripts (a new folder every week)
└─ data/
   ├─ raw/           YOUR FOOTAGE. As many films as you like. Never written to.
   ├─ work/          what the scripts make on the way. Can always be deleted.
   └─ out/           what you look at: pieces, sheets, cuts, pages
```

Run `02_folders.py`, then copy your films into `data/raw/`.

- name files with letters, numbers and `_` only: `harbour_night.mp4`,
  not `Harbour (night) final.mp4`
- every file in `data/raw` is one film; from now on every script works
  on **all** of them

---

## Reading a video file

A video is not "a video". It is a **container** (mp4, mov) holding
**streams** (picture, sound), each in a **codec** (h264, aac), plus
numbers about it: size, frame rate, length.

Ask first in the terminal:

```bash
ffprobe data/raw/your_film.mp4
```

Then run `03_read_footage.py`. It runs the same program from Python for
every film and saves `data/out/footage.csv` — open it in a spreadsheet.
Two Python tools carry the whole script:

```python
subprocess.run([...])    # run a terminal program from Python
json.loads(text)         # turn its answer into a dictionary
```

Rule one of the course: **probe every film before you touch it.**

---

## ffmpeg directly in the terminal

Python only ever builds ffmpeg commands. Try them yourself first; replace
`in.mp4` with one of your films.

```bash
# cut 5 seconds, starting at 1 minute
ffmpeg -ss 60 -i data/raw/in.mp4 -t 5 data/out/piece.mp4

# the same, but fast: no re-encoding (the cut snaps to the nearest keyframe)
ffmpeg -ss 60 -i data/raw/in.mp4 -t 5 -c copy data/out/piece_copy.mp4

# smaller: 480 lines high, no sound
ffmpeg -i data/raw/in.mp4 -vf scale=-2:480 -an data/out/small.mp4

# one still every 2 seconds
mkdir -p data/out/stills
ffmpeg -i data/raw/in.mp4 -vf fps=1/2 data/out/stills/f%04d.jpg
```

Glitches with ffmpeg's own filters — no damage, just maths on pixels:

```bash
# split the colour channels apart
ffmpeg -i data/out/piece.mp4 -vf "rgbashift=rh=-12:bh=12" data/out/rgb.mp4

# every frame minus the previous one: only movement stays visible
ffmpeg -i data/out/piece.mp4 -vf "tblend=all_mode=difference" data/out/diff.mp4

# noise, then posterise to 4 levels per colour channel
ffmpeg -i data/out/piece.mp4 -vf "noise=alls=60:allf=t,lutrgb=r='bitand(val,192)':g='bitand(val,192)':b='bitand(val,192)'" data/out/noise.mp4

# ghosting: every frame is the average of the last 25
ffmpeg -i data/out/piece.mp4 -vf "tmix=frames=25" data/out/smear.mp4
```

Compare the durations of `piece.mp4` and `piece_copy.mp4` with
`ffprobe`. They differ — that is why the scripts always re-encode.

---

## Cutting from Python, and never twice

`04_trim.py` cuts 5 seconds from the middle of every film into
`data/out/ch01/`. Run it **twice**. The second time it says `skip` for
every film, because the piece already exists:

```python
if target.exists():
    print("skip")
    continue
```

Three lines, and the most important habit of the course. From next week
on, every step works like this: run it as often as you like, add new
footage whenever you like — finished work is never done again, only new
work is.

## Breaking it on purpose

`05_glitch.py` treats the pieces as what they really are: a long row of
bytes. It changes `BYTES` of them at random, and the decoder carries on
anyway, smearing wrong colours and movement across the following frames
until the next full picture.

Change `BYTES` (5, 40, 400) and `SEED` at the top, set `REDO = True`,
press ▶ again.

---

## When it breaks

| symptom | why | fix |
|---|---|---|
| ▶ does nothing / wrong Python | VS Code uses another interpreter | click the version bottom-right, choose `.venv` |
| `ffmpeg: command not found` | not installed / VS Code opened before | install, then quit and reopen VS Code |
| `FileNotFoundError: ffprobe` | same thing, from Python | same fix |
| `no footage in data/raw` | films in the wrong folder | `data/raw/`, directly — not in a subfolder |
| weird path errors | spaces or accents in file names | rename: letters, numbers, `_` |

## Think about

1. A 10-minute 4K film at 60 fps: how many frames? If a model looked at
   every one at 0.2 s per image, how long would it take?
2. The glitch changed 40 bytes out of millions. Why does so little
   damage spread so far — and why does it stop?

## Homework

Bring 3–10 minutes of your own footage, as **several files** (different
days, places, cameras). Put them in `data/raw/`, hand in
`data/out/footage.csv` and one glitch you like.
