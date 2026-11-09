"""The embedding model: SigLIP 2 (small).

ch05-01 spells this out inline - that is the lesson. From ch05-02 on,
every script imports these three functions instead of retyping them.

WHY SigLIP 2 AND NOT CLIP
    Same idea, newer training. Both put pictures and sentences into one
    shared space; both answer "how close is this image to this sentence".
    SigLIP 2 (Google, 2025) is trained with a sigmoid loss instead of
    CLIP's contrastive softmax, and it is noticeably better at short,
    concrete descriptions - which is exactly what footage search is.

    We use the smallest one, ViT-B-32-SigLIP2-256: about 377M parameters,
    a ~1.5 GB download the first time, then offline. It runs on a laptop
    CPU at roughly 0.1-0.3 s per image.

    The vectors it produces are 768 numbers long (CLIP ViT-B-32 gave 512).
    Nothing else in the course changes: the search in ch06 is still one
    matrix multiplication.

NOTE  The SigLIP 2 tokenizer comes from the transformers package, so
      `pip install transformers` is required even though we
      never call transformers ourselves.
"""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import numpy as np
import torch
from PIL import Image

MODEL, PRETRAINED = "ViT-B-32-SigLIP2-256", "webli"
# bigger and slower, if you want the accuracy:
#   MODEL, PRETRAINED = "ViT-B-16-SigLIP2-256", "webli"
#   MODEL, PRETRAINED = "ViT-L-16-SigLIP2-256", "webli"

# SigLIP was trained on lowercase captions ending in a full stop.
# Wrapping a bare word in this template makes the scores noticeably
# steadier. Pass template="{}" to switch it off and compare.
TEMPLATE = "a photo of {}."


@lru_cache(maxsize=1)
def load():
    """Load the model once per process (downloads on the first run)."""
    import open_clip
    model, _, preprocess = open_clip.create_model_and_transforms(
        MODEL, pretrained=PRETRAINED)
    model.eval()
    return model, preprocess, open_clip.get_tokenizer(MODEL)


@torch.no_grad()
def encode_images(paths: list) -> np.ndarray:
    """A stack of image paths -> (n, 768) normalised vectors."""
    model, preprocess, _ = load()
    batch = torch.stack([preprocess(Image.open(Path(p)).convert("RGB")) for p in paths])
    v = model.encode_image(batch)
    v /= v.norm(dim=-1, keepdim=True)        # normalise: dot product = cosine
    return v.cpu().numpy().astype("float32")


@torch.no_grad()
def encode_texts(texts: list, template: str = TEMPLATE) -> np.ndarray:
    """A stack of sentences -> (n, 768) normalised vectors."""
    model, _, tokenizer = load()
    prompts = [template.format(t) for t in texts]
    v = model.encode_text(tokenizer(prompts))
    v /= v.norm(dim=-1, keepdim=True)
    return v.cpu().numpy().astype("float32")
