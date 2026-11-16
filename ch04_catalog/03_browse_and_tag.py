"""ch04-03 - Browse the archive and tag it, in a browser

    python ch04_catalog/03_browse_and_tag.py
    python ch04_catalog/03_browse_and_tag.py --port 8010

Every shot of every film on one page: click to play, type your own words
underneath. Each field saves itself into data/work/<film>/shots.json the
moment you leave it. Stop button or Ctrl+C in the terminal when done.

WHY A SERVER. A page opened as a file (file:///...) is not allowed to
write to your disk - that is the point of a browser. So this script is a
tiny web server on 127.0.0.1 (this machine only, nothing online): the
page asks, Python writes. That is all a "web app" is.

The button at the top writes data/out/human_tags.csv - your words as a
spreadsheet. Nothing else is saved: the words themselves live in
shots.json, and this page is how you look at them.
"""
import csv
import html
import json
import mimetypes
import sys
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from vlab import catalog, cli, paths  # noqa: E402

PORT = cli.flag("--port", 8004, int)
TAGS = paths.OUT / "human_tags.csv"

cat = catalog.load()
lock = threading.Lock()        # two tabs must not write at the same moment


def fresh():
    """Re-read the tables from disk.

    The page holds no state of its own. Other scripts write into the same
    shots.json - ch07 adds captions, ch03 can cut the shots again - so the
    file on disk, not what this script read at startup, is the truth. Read
    it before showing anything and before every save, or a tag typed here
    would quietly put the archive back the way it was an hour ago.
    """
    global cat
    cat = catalog.load()


def done():
    return sum(1 for s in cat["shots"] if s.get("human_tags"))

CSS = """body{font:14px/1.5 system-ui,sans-serif;margin:0;padding:28px;
background:#111;color:#eee}h1{font-size:20px;margin:0 0 4px}
h2{font-size:17px;margin:34px 0 12px;color:#7fd1c4}.meta{color:#888;margin-bottom:12px}
.bar{position:sticky;top:0;z-index:9;background:#111;padding:10px 0;
border-bottom:1px solid #2a2a2a}button{font:inherit;background:#2c2c2c;color:#eee;
border:1px solid #3a3a3a;border-radius:5px;padding:5px 12px;cursor:pointer;margin-right:8px}
#say{color:#7fd1c4;font-size:12.5px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:18px}
.card{background:#1b1b1b;border-radius:6px;overflow:hidden}
video{width:100%;display:block;aspect-ratio:16/9;object-fit:cover;background:#000}
.body{padding:10px 12px 14px}.id{font-family:monospace;color:#7fd1c4}
.t{color:#888;font-size:12px}.tags{margin:8px 0;display:flex;flex-wrap:wrap;gap:5px}
.tag{background:#2c2c2c;border-radius:99px;padding:2px 9px;font-size:11.5px}
.mine{background:#2b4a45;color:#cfeee8}.cap{color:#bbb;font-size:12.5px;font-style:italic}
input{width:100%;box-sizing:border-box;margin-top:6px;background:#121212;color:#eee;
border:1px solid #333;border-radius:4px;padding:6px 8px;font:inherit}
input:focus{outline:none;border-color:#7fd1c4}"""

JS = """const say = document.getElementById('say');
document.querySelectorAll('input').forEach(i => {
  i.onkeydown = e => { if (e.key === 'Enter') i.blur(); };
  i.onchange = async () => {
    const c = i.closest('.card');
    const r = await fetch('/tag', {method: 'POST', body: JSON.stringify({
      id: c.dataset.id, tags: c.querySelector('.tg').value,
      caption: c.querySelector('.cp').value})});
    say.textContent = await r.text();
  };
});
async function save() {
  say.textContent = 'saving ...';
  say.textContent = await (await fetch('/save', {method: 'POST'})).text();
}"""


def card(s):
    """One shot: the clip, what is known about it, and two fields of yours."""
    e = html.escape
    pills = "".join(f'<span class="tag">{e(str(t))} <b>{v:.2f}</b></span>'
                    for t, v in s.get("tags", [])[:5])
    cap = f'<div class="cap">{e(s["caption"])}</div>' if s.get("caption") else ""
    # on Windows the catalog stores data\work\...; a URL wants forward slashes
    clip, key = (s["clip"].replace("\\", "/"), s["keyframe"].replace("\\", "/"))
    return (f'<div class="card" data-id="{e(s["id"])}">'
            f'<video src="/media/{clip}" poster="/media/{key}" '
            f'controls preload="none"></video>'
            f'<div class="body"><span class="id">{e(s["id"])}</span>'
            f'<span class="t"> · {s["start"]:.2f}-{s["end"]:.2f}s</span>'
            f'<div class="tags">{pills}</div>{cap}'
            f'<input class="tg" placeholder="your tags, comma separated" '
            f'value="{e(", ".join(s.get("human_tags", [])))}">'
            f'<input class="cp" placeholder="your sentence" '
            f'value="{e(s.get("human_caption", ""))}"></div></div>')


def page():
    out = []
    for film, info in cat["films"].items():
        shots = [s for s in cat["shots"] if s["film"] == film]
        out.append(f"<h2>{html.escape(film)}</h2><div class='meta'>{len(shots)} shots · "
                   f"{info['duration'] / 60:.1f} min</div><div class='grid'>"
                   f"{''.join(card(s) for s in shots)}</div>")
    bar = (f"<div class='bar'>"
           f"<button onclick=\"save()\">save human_tags.csv</button>"
           f"<span id='say'>{done()} of {len(cat['shots'])} shots have your words"
           f"</span></div>")
    # the script goes last: it looks for the inputs, so they must exist already
    return (f"<!doctype html><meta charset='utf-8'><title>the archive</title>"
            f"<style>{CSS}</style><h1>the archive</h1>"
            f"<div class='meta'>{catalog.summary(cat)}</div>"
            f"{bar}{''.join(out)}<script>{JS}</script>")


def save_csv():
    """Your words as a spreadsheet."""
    fresh()
    paths.ensure_dirs()
    with open(TAGS, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["id", "film", "start", "end", "your_tags", "your_caption"])
        for s in cat["shots"]:
            w.writerow([s["id"], s["film"], s["start"], s["end"],
                        ", ".join(s.get("human_tags", [])),
                        s.get("human_caption", "")])
    return TAGS


class Handler(BaseHTTPRequestHandler):
    """The page, the video files, and "save this". Nothing else."""

    def reply(self, text, ctype="text/plain"):
        raw = text.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", f"{ctype}; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self):
        if not self.path.startswith("/media/"):
            fresh()
            return self.reply(page(), "text/html")
        # data/work only - a server on your own machine still should not
        # hand out your whole disk
        asked = unquote(self.path[7:]).replace("\\", "/")
        f = (paths.PROJECT / asked).resolve()
        if not (f.is_file() and f.is_relative_to(paths.WORK.resolve())):
            return self.send_error(404)
        # Range: without it Safari refuses to play video at all
        size = f.stat().st_size
        rng = self.headers.get("Range", "")
        part = rng.startswith("bytes=")
        a, _, b = rng[6:].partition("-") if part else ("", "", "")
        start, end = (int(a) if a else 0), (min(int(b), size - 1) if b else size - 1)
        self.send_response(206 if part else 200)
        if part:
            self.send_header("Content-Range", f"bytes {start}-{end}/{size}")
        self.send_header("Content-Type", mimetypes.guess_type(f.name)[0] or "video/mp4")
        self.send_header("Accept-Ranges", "bytes")
        self.send_header("Content-Length", str(end - start + 1))
        self.end_headers()
        with open(f, "rb") as fh:
            fh.seek(start)
            self.wfile.write(fh.read(end - start + 1))

    def do_POST(self):
        body = (json.loads(self.rfile.read(int(self.headers["Content-Length"])))
                if not self.path.startswith("/save") else None)
        with lock:
            if body is None:
                print("  saved", paths.rel(save_csv()))
                return self.reply("saved " + paths.rel(TAGS))

            fresh()                                  # read, change, write back
            shot = next(s for s in cat["shots"] if s["id"] == body["id"])
            words = body["tags"].replace("，", ",")   # CJK keyboards type this one
            shot["human_tags"] = [w.strip() for w in words.split(",") if w.strip()]
            shot["human_caption"] = body["caption"].strip()
            film = shot["film"]
            catalog.write_film(cat["films"][film],
                               [s for s in cat["shots"] if s["film"] == film])
            print(f"  {shot['id']}  {', '.join(shot['human_tags']) or '(cleared)'}")
            self.reply(f"{done()} of {len(cat['shots'])} shots have your words")

    def log_message(self, *a):
        pass                                   # the browser asks for a lot

    def handle_one_request(self):
        try:
            super().handle_one_request()
        except (BrokenPipeError, ConnectionResetError):
            pass                               # the browser stopped a video


url = f"http://127.0.0.1:{PORT}/"
print(f"\n{catalog.summary(cat)}")
print(f"{done()} of {len(cat['shots'])} shots have your words\n")
print(f"  {url}\n  every field saves itself · Ctrl+C here when you are done\n")
webbrowser.open(url)
try:
    ThreadingHTTPServer(("127.0.0.1", PORT), Handler).serve_forever()
except KeyboardInterrupt:
    print("\nstopped.", catalog.summary(cat))
