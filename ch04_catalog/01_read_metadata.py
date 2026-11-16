"""ch04-01 - Everything the file says about itself

    python ch04_catalog/01_read_metadata.py
    -> data/out/metadata.json

Before anybody looks at a picture: a film already carries a great many
numbers about itself, written by the camera and the encoder, not by you.
Nothing is selected here - every field ffprobe returns is printed, and
the same answer is kept whole in data/out/metadata.json.

    the container      format, duration, bit rate, brands, creation time
    every stream       codec, pixel format, colour primaries and transfer,
                       both frame rates, time base, disposition, side data
    chapters, programs usually empty, occasionally not
    the file itself    size and timestamps, from the file system
    exiftool           if it is installed, everything it knows as well

Why this is the first thing in the week about the archive: these fields
are the only part of a film that is fully addressable before any
interpretation. Every one of them can be sorted, compared and counted
across your whole folder - and they describe the apparatus, not the
subject. A difference in colour primaries between two files is invisible
to you and obvious to the machine.
"""
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from vlab import ff, footage, paths  # noqa: E402

OUT = paths.OUT / "metadata.json"


def dump(data, indent="    "):
    """Print every field, whatever shape it is in."""
    for k, v in data.items():
        if isinstance(v, dict):
            for k2, v2 in v.items():
                print(f"{indent}{k}.{k2:<{max(2, 22 - len(k))}} {v2}")
        elif isinstance(v, list):
            for item in v:
                print(f"{indent}{k:22} {item}")
        elif v not in (None, ""):
            print(f"{indent}{k:22} {v}")


everything = {}
for src in footage.require():
    name = footage.name(src)
    print(f"\n{'=' * 66}\n  {name}   ({src.name})\n{'=' * 66}")

    data = json.loads(ff.run(
        [ff.FFPROBE, "-v", "error", "-print_format", "json", "-show_format",
         "-show_streams", "-show_chapters", "-show_programs", str(src)],
        quiet=True).stdout or "{}")

    stat = src.stat()
    record = {"file": {
        "path": paths.rel(src),
        "bytes": stat.st_size,
        "modified": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(stat.st_mtime)),
        "created": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(
            getattr(stat, "st_birthtime", stat.st_ctime))),
    }, "ffprobe": data}

    print("  on disk")
    dump(record["file"])
    print("\n  container")
    dump(data.get("format", {}))
    for s in data.get("streams", []):
        print(f"\n  stream {s.get('index')} · {s.get('codec_type', 'data')}")
        dump(s)
    for ch in data.get("chapters", []):
        print(f"\n  chapter {ch.get('id')}")
        dump(ch)

    v = next((s for s in data.get("streams", []) if s.get("codec_type") == "video"), None)
    if v and v.get("r_frame_rate") != v.get("avg_frame_rate"):
        print(f"\n    note: r_frame_rate {v['r_frame_rate']} is what the container "
              f"claims,\n          avg_frame_rate {v['avg_frame_rate']} is what the "
              f"frames actually add up to.")

    if shutil.which("exiftool"):
        try:
            raw = subprocess.run(["exiftool", "-j", "-G", str(src)],
                                 capture_output=True, text=True, timeout=60).stdout
            record["exiftool"] = json.loads(raw)[0]
            print("\n  exiftool")
            dump(record["exiftool"])
        except Exception as e:
            print(f"\n  exiftool failed: {e}")

    everything[name] = record


def count(x):
    """How many values are in there."""
    if isinstance(x, dict):
        return sum(count(v) for v in x.values())
    if isinstance(x, list):
        return sum(count(v) for v in x)
    return 1


paths.ensure_dirs()
OUT.write_text(json.dumps(everything, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"\n{len(everything)} films · {count(everything)} values ->", paths.rel(OUT))
print("Count how many of them you had never looked at.")
if not shutil.which("exiftool"):
    print("(exiftool is not installed - with it there would be a few hundred more)")
