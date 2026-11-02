"""ch02-01 - Is everything installed?

    python ch02_vlab/01_check_env.py

Week 1 needed nothing but Python and ffmpeg. From now on the scripts use
packages that other people wrote (numpy, OpenCV, the image model ...),
listed in requirements.txt. Install them first (see this folder's
README), then run this. Every line should say [ok]. A [--] tells you
what is missing.

Still plain Python, like week 1 - vlab comes in the next script.
"""
import importlib
import shutil
import sys
import urllib.request

# 1. which Python is running this file?
print("Python ", sys.version.split()[0])
print("        ", sys.executable)

# a virtual environment is a private copy of Python for this project
if sys.prefix != sys.base_prefix:
    print("  [ok]  running inside a virtual environment")
else:
    print("  [--]  NOT inside a virtual environment - see the README, step 2")

if sys.version_info < (3, 10):
    print("  [--]  Python 3.10 or newer is needed")

# 2. ffmpeg is a program, not a Python package
print()
for program in ["ffmpeg", "ffprobe"]:
    where = shutil.which(program)
    if where:
        print(f"  [ok]  {program:<12} {where}")
    else:
        print(f"  [--]  {program:<12} missing - install ffmpeg (README, step 3)")

# 3. the Python packages from requirements.txt, and the week that needs them
packages = [
    ("numpy",        "week 2"),
    ("PIL",          "week 2"),
    ("cv2",          "week 3"),
    ("scenedetect",  "week 3"),
    ("torch",        "week 5"),
    ("open_clip",    "week 5"),
    ("transformers", "week 5"),
    ("requests",     "week 7"),
    ("streamlit",    "week 8"),
]
print()
for package, week in packages:
    try:
        module = importlib.import_module(package)
        version = getattr(module, "__version__", "")
        print(f"  [ok]  {package:<12} {version:<12} ({week})")
    except ImportError:
        print(f"  [--]  {package:<12} {'missing':<12} ({week})  pip install -r requirements.txt")

# 4. Ollama is a separate app that runs a language model on this machine
print()
try:
    urllib.request.urlopen("http://localhost:11434/api/tags", timeout=2)
    print("  [ok]  Ollama is running")
except Exception:
    print("  [--]  Ollama is not running (only needed in week 7)")
