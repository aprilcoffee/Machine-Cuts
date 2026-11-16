"""Searching the archive with a sentence.

This is the one line the whole course turns on:

    scores = shot_vectors @ query_vector

It lives here rather than in a chapter script so that every chapter can
use it without importing another chapter. Chapter scripts read top to
bottom and never import each other.

Each film keeps its own vectors (data/work/<film>/embeddings.npy).
vectors() stacks them into one matrix, so a search always runs across
every film in the archive at once.

ONE ROW PER STILL, NOT PER SHOT
A shot is represented by several stills (ch05-02), and each one keeps its
own row. A shot's score is then the score of its BEST still - per_shot()
below. That is the question people actually ask of footage: is this thing
in there anywhere? Averaging the stills into one vector would ask a
different and weaker question - is the shot mostly about this - and for a
twenty-second take the average lands between its contents, near nothing.

The mean still has one job: a map needs one point per shot. shots() makes
it, at the moment it is needed, from the same rows.
"""
from __future__ import annotations

import json

import numpy as np

from . import embed
from .paths import WORK


def vectors(cat: dict):
    """All shot vectors of all films: (ids, matrix), rows in the same order."""
    ids, blocks = [], []
    for film in cat["films"]:
        npy = WORK / film / "embeddings.npy"
        meta = WORK / film / "embeddings.json"
        if not npy.exists() or not meta.exists():
            continue
        ids += json.loads(meta.read_text())["ids"]
        blocks.append(np.load(npy))
    if not blocks:
        raise SystemExit("no vectors yet - run ch05_siglip/03_embed_shots.py first")
    E = np.concatenate(blocks)
    # rows of shots that have been cut again since are left out
    known = {s["id"] for s in cat["shots"]}
    keep = [i for i, shot_id in enumerate(ids) if shot_id in known]
    return [ids[i] for i in keep], E[keep]


def per_shot(ids: list, scores) -> dict:
    """Row scores -> one score per shot: its best still."""
    best = {}
    for shot_id, score in zip(ids, scores):
        if score > best.get(shot_id, -2.0):
            best[shot_id] = float(score)
    return best


def shots(cat: dict):
    """One vector per shot - the mean of its stills. For maps, not search."""
    ids, E = vectors(cat)
    rows = {}
    for shot_id, v in zip(ids, E):
        rows.setdefault(shot_id, []).append(v)
    out = [shot_id for shot_id in rows]
    M = np.stack([np.mean(rows[i], axis=0) for i in out])
    M /= np.linalg.norm(M, axis=1, keepdims=True)
    return out, M.astype("float32")


def _check(E, dim: int) -> None:
    if E.shape[1] != dim:
        raise SystemExit(
            f"the stored vectors are {E.shape[1]}-dimensional but this model "
            f"makes {dim}-dimensional ones.\n"
            f"They were embedded with a different model. Re-run:\n"
            f"    python ch05_siglip/03_embed_shots.py --redo")


def rank(cat: dict, query: str) -> list:
    """Return [(shot, score), ...] for one sentence, best first."""
    ids, E = vectors(cat)
    by_id = {s["id"]: s for s in cat["shots"]}
    q = embed.encode_texts([query])[0]
    _check(E, q.shape[0])
    best = per_shot(ids, E @ q)          # <- the entire point
    return [(by_id[i], sc) for i, sc in
            sorted(best.items(), key=lambda kv: -kv[1])]


def by_film(cat: dict, query: str, per_film: int = 3) -> list:
    """Which film answers the sentence best?

    A film's score is the mean of its best `per_film` shot scores - one
    lucky shot is not enough to make a whole film "about" something.

    Returns [(film, film_score, [(shot, score), ...]), ...], best film first,
    each with its best `per_film` shots.
    """
    best = {}
    for shot, score in rank(cat, query):
        picks = best.setdefault(shot["film"], [])
        if len(picks) < per_film:
            picks.append((shot, score))
    films = [(film, sum(sc for _, sc in picks) / len(picks), picks)
             for film, picks in best.items()]
    return sorted(films, key=lambda f: -f[1])


def cast(cat: dict, lines: list, reuse: bool = False) -> list:
    """One shot per storyboard line. Returns [(line, shot, score), ...].

    With reuse=False a shot can only be cast once - used shots are
    crossed off, the way a casting director crosses off a face.
    """
    ids, E = vectors(cat)
    by_id = {s["id"]: s for s in cat["shots"]}
    Q = embed.encode_texts(lines)        # (lines, dim)
    _check(E, Q.shape[1])
    S = E @ Q.T                          # (stills, lines)

    used, out = set(), []
    for j, line in enumerate(lines):
        best = per_shot(ids, S[:, j])
        order = sorted(best, key=lambda i: -best[i])
        pick = next((i for i in order if reuse or i not in used), order[0])
        used.add(pick)
        out.append((line, by_id[pick], best[pick]))
    return out
