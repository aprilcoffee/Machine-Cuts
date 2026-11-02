"""ch02-01 - Is everything installed?

    python ch02_vlab/01_check_env.py

From this week on the scripts use packages other people wrote
(requirements.txt). This checks three things: are you inside a virtual
environment, is ffmpeg there, and can Python import every package.
Only problems are printed - "all good" means you are ready.
"""
import importlib
import shutil
import sys

# the import names of the packages in requirements.txt
PACKAGES = ["numpy", "PIL", "cv2", "scenedetect", "torch", "open_clip",
            "transformers", "requests", "streamlit"]

print("Python", sys.version.split()[0], "-", sys.executable)
problems = 0

# a virtual environment is a private copy of Python for this project
if sys.prefix == sys.base_prefix:
    print("[--] not running inside a virtual environment")
    problems += 1

# ffmpeg is a program, not a Python package
for program in ["ffmpeg", "ffprobe"]:
    if not shutil.which(program):
        print(f"[--] {program} missing - install ffmpeg")
        problems += 1

# try to import each package; collect the ones that fail
missing = []
for package in PACKAGES:
    try:
        importlib.import_module(package)
    except ImportError:
        missing.append(package)
if missing:
    print("[--] missing:", ", ".join(missing))
    # sys.executable is the Python running this file - install into exactly that one
    print("     install them into THIS Python - copy this line into the terminal:")
    print(f"     {sys.executable} -m pip install -r requirements.txt")
    problems += 1

print("\nall good" if problems == 0 else f"\n{problems} problem(s)")
