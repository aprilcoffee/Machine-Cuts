"""A thin wrapper around a local Ollama server.

Ollama is a small service running on your own machine at :11434. It is
not a Python package - you talk to it over HTTP like any other API. The
difference is that this API is *here*: it works offline, and your footage
never leaves the drive. For a class working with other people's faces and
private material, that is not a technical detail.
"""
from __future__ import annotations

import base64
import json
from pathlib import Path

import requests

HOST = "http://localhost:11434"
TEXT_MODEL = "gemma3:4b"     # ollama pull gemma3:4b
VISION_MODEL = "gemma3:4b"   # the same model can see images (the 1b one cannot)


def is_up() -> bool:
    try:
        requests.get(f"{HOST}/api/tags", timeout=2)
        return True
    except Exception:
        return False


def models() -> list[str]:
    r = requests.get(f"{HOST}/api/tags", timeout=5)
    return [m["name"] for m in r.json().get("models", [])]


def require(model: str) -> None:
    """Fail with a sentence a human can act on, not a ConnectionError."""
    if not is_up():
        raise SystemExit(
            "Ollama is not running.\n"
            "  1. install it from https://ollama.com\n"
            "  2. start it:   ollama serve\n"
            f"  3. get the model:   ollama pull {model}"
        )
    have = models()
    if model not in have and model.split(":")[0] not in [m.split(":")[0] for m in have]:
        raise SystemExit(f"{model} has not been pulled yet:  ollama pull {model}")


def generate(prompt: str, model: str = TEXT_MODEL, images: list | None = None,
             system: str | None = None, temperature: float = 0.8,
             stream: bool = False) -> str:
    """Send a prompt, get text back. Pass image paths to use vision mode."""
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": stream,
        "options": {"temperature": temperature},
    }
    if system:
        payload["system"] = system
    if images:
        payload["images"] = [
            base64.b64encode(Path(p).read_bytes()).decode() for p in images
        ]

    if not stream:
        r = requests.post(f"{HOST}/api/generate", json=payload, timeout=600)
        r.raise_for_status()
        return r.json().get("response", "").strip()

    # Streaming: one JSON object per line. Printing as it arrives feels
    # better in a classroom than waiting on a blank terminal.
    out = []
    with requests.post(f"{HOST}/api/generate", json=payload,
                       stream=True, timeout=600) as r:
        r.raise_for_status()
        for line in r.iter_lines():
            if not line:
                continue
            chunk = json.loads(line)
            piece = chunk.get("response", "")
            print(piece, end="", flush=True)
            out.append(piece)
            if chunk.get("done"):
                break
    print()
    return "".join(out).strip()
