"""ch05-04 - The model, live

    python ch05_siglip/04_live_camera.py

Your webcam and the words in TEXTS. Every few frames the picture goes
through the same SigLIP 2 as in 02 and 03 (vlab/embed.py), and the words are sorted by how close
they sit to it, on top of the image. Point the camera at things.
Press q to quit.

The words are encoded once, at the start, exactly as you type them -
no "a photo of ..." around them. Edit TEXTS and run again.
Write them in plain English letters - cv2.putText cannot draw umlauts,
accents or Chinese (they come out as ?).

macOS: the first time, allow your terminal (or VS Code) to use the
camera in System Settings > Privacy & Security > Camera, then run again.
"""
import sys
from pathlib import Path

import cv2
import torch
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from vlab import embed  # noqa: E402

TEXTS = [
    "a face",
    "a hand",
    "a cup",
    "a phone",
    "a book",
    "an empty room",
]
CAMERA = 0      # try 1 if you have more than one camera
EVERY = 5       # ask the model every 5th frame - lower is livelier, but slower

print(f"loading {embed.MODEL} ...")
model, preprocess, _ = embed.load()
texts = embed.encode_texts(TEXTS, template="{}")  # once, exactly as you typed them

cam = cv2.VideoCapture(CAMERA)
if not cam.isOpened():
    raise SystemExit(f"no camera {CAMERA} - try CAMERA = 1, or check the camera permission")

ranked, n = [], 0
while True:
    ok, frame = cam.read()
    if not ok:
        break
    if n % EVERY == 0:
        picture = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        with torch.no_grad():
            image = model.encode_image(preprocess(picture).unsqueeze(0))
        image = (image / image.norm(dim=-1, keepdim=True))[0].numpy()
        ranked = sorted(zip((texts @ image).tolist(), TEXTS), reverse=True)
    n += 1

    for i, (score, text) in enumerate(ranked):
        line, at = f"{score:.4f}  {text}", (20, 40 + i * 34)
        colour = (0, 255, 255) if i == 0 else (255, 255, 255)      # the winner in yellow
        cv2.putText(frame, line, at, cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 4, cv2.LINE_AA)
        cv2.putText(frame, line, at, cv2.FONT_HERSHEY_SIMPLEX, 0.8, colour, 2, cv2.LINE_AA)

    cv2.imshow("SigLIP 2 - q to quit", frame)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cam.release()
cv2.destroyAllWindows()
