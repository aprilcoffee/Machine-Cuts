# The terminal, in one page

The terminal is a window where you type commands instead of clicking.
In VS Code: *Terminal → New Terminal*. It opens in the project folder.

- **Mac:** the terminal runs *zsh*
- **Windows:** the terminal runs *PowerShell*

Almost everything below is the same on both.

## Where am I, what is here

| what | Mac | Windows (PowerShell) |
|---|---|---|
| where am I? | `pwd` | `pwd` |
| what is in this folder? | `ls` | `ls` |
| go into a folder | `cd data/raw` | `cd data\raw` |
| go up one folder | `cd ..` | `cd ..` |
| go to my home folder | `cd ~` | `cd ~` |
| make a folder | `mkdir data/out/test` | `mkdir data\out\test` |
| clear the screen | `clear` | `cls` |

On Windows, `/` works too: `cd data/raw` is fine in PowerShell.

## Running things

| what | Mac | Windows |
|---|---|---|
| run a Python script | `python ch01_python/01_hello.py` | `python ch01_python\01_hello.py` |
| which Python is this? | `which python` | `Get-Command python` |
| switch on the project's Python | `source .venv/bin/activate` | `.venv\Scripts\Activate.ps1` |
| is ffmpeg there? | `ffmpeg -version` | `ffmpeg -version` |
| what is in this video? | `ffprobe data/raw/film.mp4` | `ffprobe data\raw\film.mp4` |

When the project's Python is on, the line starts with `(.venv)`. VS Code
usually switches it on for you.

## ffmpeg, the shape of every command

```
ffmpeg  -i INPUT   [what to do]   OUTPUT
```

```bash
ffmpeg -i data/raw/film.mp4 data/out/film.mov                    # change the format
ffmpeg -ss 60 -i data/raw/film.mp4 -t 5 data/out/piece.mp4       # 5 s from 1:00
ffmpeg -i data/raw/film.mp4 -vf scale=-2:480 data/out/small.mp4  # smaller
ffmpeg -i data/raw/film.mp4 -an data/out/silent.mp4              # no sound
```

## Keys that save you

| key | what it does |
|---|---|
| `Tab` | completes a file or folder name — type `data/r` then Tab |
| `↑` | the previous command again |
| `Ctrl + C` | stop whatever is running (on Mac too: Ctrl, not Cmd) |

## When it says no

| message | meaning |
|---|---|
| `command not found` / `is not recognized` | that program is not installed, or the terminal was opened before you installed it: close it, open a new one |
| `No such file or directory` / `Cannot find path` | wrong folder or a typo: `pwd`, then `ls` |
| Windows: `running scripts is disabled on this system` (when activating `.venv`) | run once: `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`, answer `Y` |
| a file name with spaces fails | put it in quotes: `"data/raw/my film.mp4"` — or better, rename it |
