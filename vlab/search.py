"""Searching the archive with a sentence.

This is the one line the whole course turns on:

    scores = shot_vectors @ query_vector

It lives here rather than in a chapter script so that every chapter can
use it without importing another chapter. Chapter scripts read top to
bottom and never import each other.

Each film keeps its own vectors (data/work/<film>/embeddings.npy).
vectors() stacks them into one matrix, so a search always runs across
every film in the archive at once.
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
        raise SystemExit("no vectors yet - run ch05_siglip/02_embed_shots.py first")
    E = np.concatenate(blocks)
    # rows of shots that have been cut again since are left out
    known = {s["id"] for s in cat["shots"]}
    keep = [i for i, shot_id in enumerate(ids) if shot_id in known]
    return [ids[i] for i in keep], E[keep]


def _check(E, dim: int) -> None:
    if E.shape[1] != dim:
        raise SystemExit(
            f"the stored vectors are {E.shape[1]}-dimensional but this model "
            f"makes {dim}-dimensional ones.\n"
            f"They were embedded with a different model. Re-run:\n"
            f"    python ch05_siglip/02_embed_shots.py --redo")


def rank(cat: dict, query: str) -> list:
    """Return [(shot, score), ...] for one sentence, best first."""
    ids, E = vectors(cat)
    by_id = {s["id"]: s for s in cat["shots"]}
    q = embed.encode_texts([query])[0]
    _check(E, q.shape[0])
    scores = E @ q                       # <- the entire point
    order = np.argsort(-scores)
    return [(by_id[ids[i]], float(scores[i])) for i in order]


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
    S = E @ Q.T                          # (shots, lines)

    used, out = set(), []
    for j, line in enumerate(lines):
        order = np.argsort(-S[:, j])
        pick = next((i for i in order if reuse or ids[i] not in used), order[0])
        used.add(ids[pick])
        out.append((line, by_id[ids[pick]], float(S[pick, j])))
    return out
