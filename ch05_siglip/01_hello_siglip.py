"""ch05-01 - Hello, SigLIP 2

    python ch05_siglip/01_hello_siglip.py

One picture, a few words. The model turns the picture into 768 numbers
and each text into 768 numbers, then measures how close they point: the
cosine similarity. Higher = closer.

Edit TEXTS and run again. Swap IMAGE for any picture you like.
The first run downloads the model (about 1.5 GB), then it works offline.
"""
from pathlib import Path

import open_clip
import torch
from PIL import Image

IMAGE = Path(__file__).parent / "test.jpg"
TEXTS = [
    "a red car",
    "a destroyed house",
    "two people walking",
    "a desert",
    "ice cream",
    "a city at night",
]

MODEL = "ViT-B-32-SigLIP2-256"
model, _, preprocess = open_clip.create_model_and_transforms(MODEL, pretrained="webli")
tokenizer = open_clip.get_tokenizer(MODEL)
model.eval()

with torch.no_grad():
    image = model.encode_image(preprocess(Image.open(IMAGE).convert("RGB")).unsqueeze(0))
    texts = model.encode_text(tokenizer(TEXTS))

image /= image.norm(dim=-1, keepdim=True)      # length 1, so a dot product is the cosine
texts /= texts.norm(dim=-1, keepdim=True)
scores = (image @ texts.T)[0]

for score, text in sorted(zip(scores.tolist(), TEXTS), reverse=True):
    print(f"{score:.4f}  {text}")
