"""Which films are there, and what has already been done to them.

Every video file directly inside data/raw/ is one film. Its name is the
file name without the extension, and everything made from it lives in
its own folder:

    data/raw/harbour.mp4
    data/work/harbour/proxy.mp4
    data/work/harbour/cuts.json
    data/work/harbour/shots/s0001.mp4 ...
    data/work/harbour/shots.json

DON'T DO THE WORK TWICE
    Every step asks one question before it starts:

        is the result already there, and newer than what it was made from?

    If yes, skip. That is the whole rule - it is what the program `make`
    has done since 1976. It means you can run any script, or the whole
    pipeline, as often as you like: finished films are skipped, new
    footage is processed, and a film you replaced in data/raw (a newer
    file) is redone from that step on.
"""
from __future__ import annotations

from pathlib import Path

from . import cli
from .paths import RAW, WORK

VIDEO_EXT = {".mp4", ".mov", ".mkv", ".m4v", ".avi", ".mpg", ".webm"}


def videos() -> list[Path]:
    """Every film in data/raw, sorted by name."""
    if not RAW.exists():
        return []
    return sorted(p for p in RAW.iterdir()
                  if p.is_file() and p.suffix.lower() in VIDEO_EXT)


def require() -> list[Path]:
    """Like videos(), but stops with a helpful sentence if there are none.

    Add --film NAME to any script to work on that one film only.
    """
    found = videos()
    only = cli.flag("--film")
    if only:
        found = [v for v in found if name(v) == only]
        if not found:
            raise SystemExit(f"No film called '{only}' in data/raw/.")
    if not found:
        raise SystemExit("No footage found.\n"
                         "  Put one or more video files into data/raw/ and run this again.")
    return found


def name(src) -> str:
    """The film's name: data/raw/harbour.mp4 -> 'harbour'."""
    return Path(src).stem


def work(src) -> Path:
    """The film's own folder in data/work (not created here)."""
    return WORK / name(src)


def done(output, *inputs) -> bool:
    """True if `output` exists and is newer than every input that exists."""
    output = Path(output)
    if not output.exists():
        return False
    t = output.stat().st_mtime
    return all(t >= Path(i).stat().st_mtime for i in inputs if Path(i).exists())


def steps(src) -> dict:
    """Which of the expensive steps are finished for this film."""
    w = work(src)
    return {
        "proxy":   done(w / "proxy.mp4", src),
        "cuts":    done(w / "cuts.json", w / "proxy.mp4"),
        "shots":   done(w / "shots.json", w / "cuts.json"),
        "vectors": done(w / "embeddings.npy", w / "cuts.json"),
    }


def pending() -> list[Path]:
    """Films that still have at least one step to do."""
    return [v for v in videos() if not all(steps(v).values())]
