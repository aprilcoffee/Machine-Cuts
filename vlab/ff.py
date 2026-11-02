"""A thin wrapper around ffmpeg / ffprobe.

Why not moviepy or another wrapper? Because ffmpeg is the actual ground
floor of video work. If you can read the command, you can take it to any
machine, any pipeline, any decade. Wrappers change; ffmpeg does not.
"""
from __future__ import annotations

import json
import shutil
import subprocess
from functools import lru_cache
from pathlib import Path

FFMPEG = shutil.which("ffmpeg") or "ffmpeg"
FFPROBE = shutil.which("ffprobe") or "ffprobe"

VERBOSE = True  # set False to stop printing every command

# where the little label PNGs are cached
WORK_LABELS = Path(__file__).resolve().parent.parent / "data" / "work" / "_labels"


def run(args: list[str], quiet: bool = False) -> subprocess.CompletedProcess:
    """Run one command. args is a list, so no quoting worries.

    On failure this raises, but it prints the last lines of ffmpeg's own
    error message first. ffmpeg always explains itself; the problem is
    that Python usually swallows it.
    """
    if VERBOSE and not quiet:
        print("  $", " ".join(str(a) for a in args))
    r = subprocess.run([str(a) for a in args],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if r.returncode != 0:
        tail = r.stderr.decode("utf-8", "replace").strip().splitlines()[-6:]
        print("\n  ffmpeg said:")
        for line in tail:
            print("   ", line)
        raise subprocess.CalledProcessError(r.returncode, args,
                                            output=r.stdout, stderr=r.stderr)
    return r


def have_ffmpeg() -> bool:
    return shutil.which("ffmpeg") is not None and shutil.which("ffprobe") is not None


def probe(path) -> dict:
    """Ask ffprobe what this file is. Returns the raw dict."""
    out = run(
        [FFPROBE, "-v", "error", "-print_format", "json",
         "-show_format", "-show_streams", str(path)],
        quiet=True,
    ).stdout
    return json.loads(out)


def info(path) -> dict:
    """The handful of fields a human actually wants."""
    data = probe(path)
    v = next((s for s in data["streams"] if s["codec_type"] == "video"), None)
    a = next((s for s in data["streams"] if s["codec_type"] == "audio"), None)
    fps = 0.0
    if v and v.get("r_frame_rate", "0/0") != "0/0":
        num, den = v["r_frame_rate"].split("/")
        fps = float(num) / float(den or 1)
    return {
        "path": str(path),
        "duration": float(data["format"].get("duration", 0.0)),
        "size_mb": round(int(data["format"].get("size", 0)) / 1e6, 2),
        "width": int(v["width"]) if v else 0,
        "height": int(v["height"]) if v else 0,
        "fps": round(fps, 3),
        "vcodec": v["codec_name"] if v else None,
        "acodec": a["codec_name"] if a else None,
    }


# --- cutting --------------------------------------------------------------

def trim(src, dst, start: float, end: float, reencode: bool = True,
         quiet: bool = False) -> Path:
    """Cut out [start, end).

    reencode=True   slower, but the cut lands exactly where you asked.
                    This is what automated editing needs.
    reencode=False  uses -c copy: fast, but cuts snap to keyframes and drift.
    """
    dst = Path(dst)
    dst.parent.mkdir(parents=True, exist_ok=True)
    dur = max(0.04, float(end) - float(start))
    if reencode:
        args = [FFMPEG, "-y", "-ss", f"{start:.3f}", "-i", str(src),
                "-t", f"{dur:.3f}",
                "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
                "-pix_fmt", "yuv420p", "-c:a", "aac", "-movflags", "+faststart",
                str(dst)]
    else:
        args = [FFMPEG, "-y", "-ss", f"{start:.3f}", "-i", str(src),
                "-t", f"{dur:.3f}", "-c", "copy", str(dst)]
    run(args, quiet=quiet)
    return dst


def frame_at(src, dst, t: float, width: int = 640, quiet: bool = False) -> Path:
    """Grab a single still at time t (a keyframe / thumbnail)."""
    dst = Path(dst)
    dst.parent.mkdir(parents=True, exist_ok=True)
    run([FFMPEG, "-y", "-ss", f"{t:.3f}", "-i", str(src),
         "-frames:v", "1", "-vf", f"scale={width}:-2", "-q:v", "3", str(dst)],
        quiet=quiet)
    return dst


def proxy(src, dst, height: int = 480, fps: int = 12) -> Path:
    """Make a small proxy: analysis runs fast and the disk survives."""
    dst = Path(dst)
    dst.parent.mkdir(parents=True, exist_ok=True)
    run([FFMPEG, "-y", "-i", str(src),
         "-vf", f"scale=-2:{height},fps={fps}",
         "-c:v", "libx264", "-preset", "veryfast", "-crf", "28",
         "-an", str(dst)])
    return dst


def conform(src, dst, width: int, height: int, fps: float = 25) -> Path:
    """Re-encode a clip to one fixed size, frame rate and sound format.

    Clips from different films differ in all three (and some have no
    sound at all). They can only be joined once they all look the same,
    so every clip is fitted into width x height (black bars where the
    shape differs) and given a silent stereo track if it has none.
    """
    dst = Path(dst)
    dst.parent.mkdir(parents=True, exist_ok=True)
    picture = (f"scale={width}:{height}:force_original_aspect_ratio=decrease,"
               f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2,setsar=1,fps={fps}")
    args = [FFMPEG, "-y", "-i", str(src),
            "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo",
            "-vf", picture, "-map", "0:v:0"]
    args += ["-map", "0:a:0"] if info(src)["acodec"] else ["-map", "1:a:0"]
    args += ["-shortest",
             "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p",
             "-c:a", "aac", "-ar", "48000", "-ac", "2", str(dst)]
    run(args, quiet=True)
    return dst


def concat(clips: list, dst, width: int | None = None, height: int | None = None,
           fps: float = 25) -> Path:
    """Join clips - from one film or from many - into one file.

    Every clip is conformed first (see conform), to the size of the first
    clip unless you pass width and height. Then the concat demuxer glues
    the identical-looking pieces together without re-encoding again.
    """
    dst = Path(dst)
    dst.parent.mkdir(parents=True, exist_ok=True)
    if width is None or height is None:
        first = info(clips[0])
        width, height = first["width"] // 2 * 2, first["height"] // 2 * 2

    tmp = dst.parent / f"_{dst.stem}_parts"
    tmp.mkdir(parents=True, exist_ok=True)
    parts = []
    for i, c in enumerate(clips):
        print(f"  conforming {i + 1}/{len(clips)}  {Path(c).name}")
        parts.append(conform(c, tmp / f"p{i:04d}.mp4", width, height, fps))

    listfile = tmp / "list.txt"
    with open(listfile, "w", encoding="utf-8") as f:
        for p in parts:
            f.write(f"file '{p.resolve().as_posix()}'\n")
    run([FFMPEG, "-y", "-f", "concat", "-safe", "0", "-i", str(listfile),
         "-c", "copy", "-movflags", "+faststart", str(dst)])
    shutil.rmtree(tmp)
    return dst


# --- putting a label into the picture ------------------------------------
# ffmpeg's drawtext filter needs the binary to be built with libfreetype AND
# a font file to point at. Plenty of builds have neither - Homebrew's ffmpeg
# often reports "No such filter: 'drawtext'". So we never use drawtext:
# Pillow draws the label into a small transparent PNG and ffmpeg's `overlay`
# filter (a core filter, always present) puts it on the picture.
FONTS = [
    "/System/Library/Fonts/Supplemental/Arial.ttf",          # macOS
    "/System/Library/Fonts/Supplemental/Helvetica.ttc",
    "/System/Library/Fonts/Helvetica.ttc",
    "/Library/Fonts/Arial.ttf",
    "C:/Windows/Fonts/arial.ttf",                            # Windows
    "C:/Windows/Fonts/segoeui.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",       # Linux
    "/usr/share/fonts/TTF/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
]


@lru_cache(maxsize=1)
def find_font() -> str | None:
    """A font file on this machine, or None (Pillow then uses its own)."""
    for f in FONTS:
        if Path(f).exists():
            return f
    return None


def label_image(text: str, size: int = 28) -> Path:
    """Draw one line of text as a small PNG with a translucent background."""
    from PIL import Image, ImageDraw, ImageFont
    font_path = find_font()
    try:
        font = ImageFont.truetype(font_path, size) if font_path else ImageFont.load_default()
    except Exception:
        font = ImageFont.load_default()

    pad = max(6, size // 3)
    probe = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    box = probe.textbbox((0, 0), text, font=font)
    w, h = box[2] - box[0] + pad * 2, box[3] - box[1] + pad * 2
    # even dimensions keep h264 happy when the overlay touches an edge
    w += w % 2
    h += h % 2

    img = Image.new("RGBA", (w, h), (0, 0, 0, 128))
    ImageDraw.Draw(img).text((pad - box[0], pad - box[1]), text,
                             fill=(255, 255, 255, 255), font=font)

    out = WORK_LABELS / (f"{abs(hash((text, size)))}.png")
    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out)
    return out


def burn_text(src, dst, text: str, size: int = 28, corner: str = "bl") -> Path:
    """Put one line of text on the picture. corner: tl, tr, bl, br.

    Uses Pillow + overlay, so it works on any ffmpeg build.
    """
    dst = Path(dst)
    dst.parent.mkdir(parents=True, exist_ok=True)
    png = label_image(str(text), size)
    m = 24
    pos = {"tl": f"{m}:{m}", "tr": f"W-w-{m}:{m}",
           "bl": f"{m}:H-h-{m}", "br": f"W-w-{m}:H-h-{m}"}.get(corner, f"{m}:H-h-{m}")
    run([FFMPEG, "-y", "-i", str(src), "-i", str(png),
         "-filter_complex", f"overlay={pos}",
         "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
         "-pix_fmt", "yuv420p", "-c:a", "copy", str(dst)])
    return dst
