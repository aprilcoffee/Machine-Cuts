"""Folder conventions.

    data/raw            source footage, never modified - as many films as you like
    data/work/<film>/   intermediates for one film: proxy, cuts, shots, stills, vectors
    data/out            deliverables: cuts, pages, sheets, scripts, EDLs
"""
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
RAW = PROJECT / "data" / "raw"
WORK = PROJECT / "data" / "work"
OUT = PROJECT / "data" / "out"


def ensure_dirs(*extra: Path) -> None:
    """Create the standard folders (plus any extra ones)."""
    for d in (RAW, WORK, OUT, *extra):
        Path(d).mkdir(parents=True, exist_ok=True)


def rel(p) -> str:
    """Short, project-relative path - easier to read in a terminal."""
    p = Path(p)
    try:
        return str(p.resolve().relative_to(PROJECT))
    except ValueError:
        return str(p)
