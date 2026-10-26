"""ch01-05 - Break it on purpose

    python ch01_python/05_glitch.py

A video file is nothing but a long row of numbers (bytes, 0-255).
The picture only exists because a decoder reads those numbers in exactly
the expected way. Change a few of them and the decoder carries on anyway,
smearing the wrong colours and movements across the following frames.

Three steps, for every piece 04_trim.py made:
  1. ffmpeg writes the bare picture stream, without the mp4 wrapping
  2. Python changes BYTES random numbers in the middle of it
  3. ffmpeg decodes the damaged stream back into a playable mp4

Change BYTES and SEED at the top and run it again (delete the old
glitch files first, or set REDO = True).
"""
import random
import subprocess
from pathlib import Path

BYTES = 40          # how many numbers to change: try 5, 40, 400
SEED = 1            # same seed = same glitch; change it for a different one
REDO = False        # True: make the glitch again even if it exists

FOLDER = Path(__file__).resolve().parent.parent / "data" / "out" / "ch01"

pieces = sorted(FOLDER.glob("*_trim.mp4"))
if not pieces:
    raise SystemExit("no pieces yet - run 04_trim.py first")

for piece in pieces:
    target = FOLDER / piece.name.replace("_trim.mp4", "_glitch.mp4")
    if target.exists() and not REDO:
        print(f"skip  {target.name} (already there)")
        continue

    # 1. the bare h264 stream. -g 250: only one full picture every 250
    #    frames, so a mistake keeps spreading until the next one
    raw = FOLDER / "temp.h264"
    subprocess.run(["ffmpeg", "-y", "-i", str(piece), "-an",
                    "-c:v", "libx264", "-g", "250", "-bf", "0",
                    "-f", "h264", str(raw)], capture_output=True)

    # 2. read every byte, change some, write them back
    data = bytearray(raw.read_bytes())
    random.seed(SEED)
    for _ in range(BYTES):
        # leave the first 5% alone: that is where the format is described
        position = random.randint(len(data) // 20, len(data) - 1)
        data[position] = random.randint(0, 255)
    raw.write_bytes(data)
    print(f"changed {BYTES} of {len(data)} bytes in {piece.name}")

    # 3. decode the damaged stream into a normal file again
    subprocess.run(["ffmpeg", "-y", "-i", str(raw),
                    "-c:v", "libx264", "-pix_fmt", "yuv420p", str(target)],
                   capture_output=True)
    raw.unlink()
    print(f"made  {target.name}\n")

print("Play the _glitch files next to the _trim files.")
