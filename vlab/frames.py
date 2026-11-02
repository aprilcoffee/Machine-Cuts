"""WHERE THE KEYFRAMES COME FROM.

This is the one question that decides what the whole archive can see, so
the rule lives in exactly one small file and every script calls it.

A model cannot watch a shot. It can only look at stills. So for every
shot we have to pick a few moments and say: these stand for those four
seconds. That choice is ours, not the model's.

The rule used here, in `times_for()`:

    shot:   |----------------------------------------|
            start                                  end
    skip the first 10% and the last 10% (fades, motion blur,
    the tail of the previous shot bleeding in)
            |....|===========================|....|
                 ^           ^           ^
                 evenly spaced samples inside that middle 80%

    n = 1  ->  one still, exactly in the middle
    n = 3  ->  10%, 50%, 90% of the usable span
    n = 5  ->  10%, 30%, 50%, 70%, 90%

Why not simply the middle frame? Because things move. A shot that pans
from an empty street to a face is "a face" for only its last second, and
a single middle frame makes that face unsearchable forever.

Why not every frame? Because 25 frames a second times an hour is 90,000
images - the model could do it, you could never look at the result, and
nearly all of those frames are the same picture.

Three frames per shot is this course's compromise, not a law. Changing
`n` changes what your archive is able to find. Run
ch03_shots/04_keyframe_sheet.py to SEE the frames a given n picks.
"""
from __future__ import annotations

from pathlib import Path

from . import ff
from .paths import PROJECT, WORK

EDGE = 0.10        # fraction skipped at each end of a shot


def times_for(shot: dict, n: int = 3) -> list[float]:
    """The timecodes (in seconds, in the source file) we will sample."""
    a, b = float(shot["start"]), float(shot["end"])
    span = b - a
    if n <= 1:
        return [a + span / 2]
    usable = 1.0 - 2 * EDGE
    return [a + span * (EDGE + usable * k / (n - 1)) for k in range(n)]


def frames_for(cat: dict, shot: dict, n: int = 3) -> list[Path]:
    """Return n still images for a shot, extracting them if needed.

    n == 1 reuses the keyframe ch03 already made; larger n writes extra
    stills into data/work/<film>/stills/ once and reuses them after.
    """
    if n <= 1:
        return [PROJECT / shot["keyframe"]]
    source = PROJECT / cat["films"][shot["film"]]["source"]
    short = shot["id"].split("/")[-1]                 # "s0007"
    out = []
    for k, t in enumerate(times_for(shot, n)):
        p = WORK / shot["film"] / "stills" / f"{short}_{n}_{k}.jpg"
        if not p.exists():
            ff.frame_at(source, p, t, quiet=True)
        out.append(p)
    return out
