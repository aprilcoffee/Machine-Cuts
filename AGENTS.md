# AGENTS.md

Course code. The tutor adds one new week folder per week; students
`git pull` it into this folder. Existing files are never updated, so you
may edit them — but keep the structure, or the next pull breaks.

## Never
- move, rename or delete `data/raw/`, `data/work/`, `data/out/`, `vlab/`,
  the `chNN_*` folders, their scripts, or the `.gitkeep` files
- create anything at a path a later week will ship: `chNN_*` folders,
  `vlab/`, `requirements.txt` (git refuses the pull if it exists)
- write to `data/raw/` (footage, read only)
- hard-code absolute paths or rely on the working directory — build paths
  from `vlab.paths` (`PROJECT`, `RAW`, `WORK`, `OUT`), or in week-1 scripts
  from `Path(__file__).resolve().parent.parent`
- rename or remove keys in `data/work/<film>/shots.json` or change the
  shot id format `<film>/sNNNN` (adding keys is fine)
- edit `.gitignore`, commit anything from `data/` or `.venv/`, or run
  destructive git commands unless asked

## Where new things go
New scripts, modules and extensions go in `mine/` (directly in the
project root). Extra packages go in `mine/requirements.txt`.

## Style
Plain scripts for art students: no classes, no `main()`, no argparse
(use `vlab.cli`), settings in CAPITALS at the top. `ch01_python/` uses
only the standard library and ffmpeg. Expensive steps skip finished work
with `vlab.footage.done(output, *inputs)`.
