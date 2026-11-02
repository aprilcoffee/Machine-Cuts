"""vlab - the workshop's tiny toolbox.

This is not meant to be a good library. It is a thin layer of glue that
holds ffmpeg, OpenCV, SigLIP and Ollama together, so that every teaching
script fits on one screen.
"""

from .paths import PROJECT, RAW, WORK, OUT, ensure_dirs, rel  # noqa: F401
