"""The smallest possible argument parsing.

Deliberately not argparse. Not because argparse is bad, but because in a
teaching script ten readable lines beat a framework you have to look up.
For a real tool, use argparse or typer instead.
"""
import sys

# Flags that are followed by a value; skipped when collecting positionals.
VALUED = {"--top", "--seconds", "--order", "--shots", "--limit", "--style",
          "--frames", "--min", "--film", "--per-film", "--films"}


def flag(name, default=None, cast=str):
    """--top 5  ->  flag("--top", 8, int) == 5"""
    if name in sys.argv:
        return cast(sys.argv[sys.argv.index(name) + 1])
    return default


def has(name) -> bool:
    """--burn  ->  has("--burn") == True"""
    return name in sys.argv


def positionals() -> list:
    """The real positional arguments (flags and their values removed)."""
    out, skip = [], False
    for a in sys.argv[1:]:
        if skip:
            skip = False
            continue
        if a.startswith("--"):
            skip = a in VALUED
            continue
        out.append(a)
    return out
