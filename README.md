# machine cut

Automated editing, shot analysis and semantic search for your own
footage. Eight weeks, one folder per week. Runs on a normal laptop — no
GPU, no API key, nothing leaves your drive.

Bauhaus-Universität Weimar · WS 26/27

---

## Where things go

```
machine-cut/                 open THIS folder in VS Code
│
├─ README.md
├─ requirements.txt          packages (from week 2)
├─ .vscode/                  makes the ▶ button work
├─ vlab/                     the course's toolbox (from week 2)
│
├─ ch01_python/              week 1  ┐
├─ ch02_vlab/                week 2  │ a new folder every week:
├─ …                                 │ put it here, next to the others
├─ ch08_pipeline_app/        week 8  ┘
│
└─ data/
   ├─ raw/                   ← YOUR FILMS GO HERE
   ├─ work/                  made by the scripts — leave it alone
   └─ out/                   results to look at: cuts, sheets, pages
```

- **Your films:** copy them into `data/raw/`, directly (no subfolders).
  As many as you like. Name them with letters, numbers and `_` only:
  `harbour_night.mp4`, not `Harbour (night) final.mp4`.
- **Each week's folder:** unzip it into `machine-cut/`, next to the
  other `chNN_…` folders. Never inside another week's folder.
- **`data/work`** can always be deleted; everything in it is rebuilt from
  `data/raw`. **`data/raw`** is never changed by any script.

---

## Start

1. Install **Python 3.12**, **VS Code** and **ffmpeg**
   (Mac: `brew install ffmpeg` · Windows: `winget install ffmpeg`).
2. VS Code → *File → Open Folder…* → `machine-cut`.
3. `Cmd/Ctrl+Shift+P` → **Python: Create Environment** → **Venv**.
4. Open `ch01_python/01_hello.py`, press **▶**.

Details in [`ch01_python/README.md`](ch01_python/README.md).
Never used a terminal? [`ch01_python/TERMINAL.md`](ch01_python/TERMINAL.md).

---

## The eight weeks

| week | folder | what you do |
|---|---|---|
| 1 | `ch01_python` | plain Python and ffmpeg: read your films, trim, glitch |
| 2 | `ch02_vlab` | install packages, meet the toolbox, proxies and proxy sheets |
| 3 | `ch03_shots` | cut every film into shots; see which stills the model looks at |
| 4 | `ch04_catalog` | your films as one table; tag by hand |
| 5 | `ch05_siglip` | an image model turns every shot into numbers |
| 6 | `ch06_search_edit` | search with a sentence, automatic cuts, find the right film |
| 7 | `ch07_gemma` | a local language model describes shots and writes a storyboard |
| 8 | `ch08_pipeline_app` | one command, one window, an EDL for your edit suite |

Every week's folder has its own `README.md`. Read it first.

---

## Run it as often as you like

Every script checks what is already done and skips it. Run it twice and
the second time says `skip`. Add a film to `data/raw` and only that film
is processed.

---

Python 3.11 or 3.12 · ffmpeg · ~10 GB free disk for the models.
Free to use, modify and redistribute for teaching.
