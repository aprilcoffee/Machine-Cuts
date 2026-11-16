# Week 4 · ch04 · The archive: your films as one table

## What you'll do

Before any AI: get clear about the archive itself. What the files already
say, what the material looks like, and — who decides the words.

- `01_read_metadata.py` — everything each file says about itself
- `02_inspect_catalog.py` — shot-length distribution, the breathing of a film
- `03_browse_and_tag.py` — every shot on one page in your browser; type
  your own words straight into it

```bash
python ch04_catalog/01_read_metadata.py
python ch04_catalog/02_inspect_catalog.py
python ch04_catalog/03_browse_and_tag.py
```

---

## What a file says before anyone looks at it

```bash
python ch04_catalog/01_read_metadata.py
# -> data/out/metadata.json
```

A film arrives carrying numbers about itself that nobody wrote on
purpose: codec, pixel format, colour primaries and transfer, the frame
rate as a fraction, the time base, the handler, the vendor id, the moment
the recording started. The camera and the encoder wrote them.

This is the part of a film that is **completely addressable before any
interpretation**. Every field can be sorted, counted and compared across
the whole folder, and not one of them is about the subject — they
describe the apparatus. Two files whose colour primaries differ look
identical to you and are plainly different to the machine.

Look at the two frame rates the script points out when they disagree:

```
note: r_frame_rate 30000/1001 is what the container claims,
      avg_frame_rate 27296000/910777 is what the frames actually add up to.
```

Neither is wrong. One is a declaration, the other is a measurement.

Nothing is selected: every field ffprobe returns is printed, and the same
answer is kept whole in `metadata.json`. If `exiftool` is installed
(`brew install exiftool`) it runs too, and there are a few hundred more.

## Shot length is the breathing of a film

```bash
python ch04_catalog/02_inspect_catalog.py
```

- lots of 1–2s shots → urgent, dense
- lots of 8s+ shots → observation, waiting, felt time

One histogram per film: compare how your films breathe. This distribution
decides the tone of whatever week 6 cuts automatically — if your material
is all long takes, cutting a fast montage from it is a fight against the
footage itself.

It is also worth knowing before next week. A twenty-second take holds
more than one thing, and no single description of it will be true.

## Why tag by hand at all

Next week the model does not label anything. It **ranks**: you give it a
sentence, it puts every shot in order. So the words have to come from
somewhere, and this week they come from you.

That forces the real question: **which words?**
A clip of the sea can be tagged "sea", "blue", "waiting", "summer 2019",
or "the day I couldn't sleep". Those are five different archives, and
five different sets of things you will be able to find later.

Tagging does not describe footage. It decides **what the footage can
later be searched as**. Next week this gets very concrete: every word you
type here becomes a question put to the model, and you get to see where
it thinks that word lives in your own material.

## The tagging page

```bash
python ch04_catalog/03_browse_and_tag.py
```

It opens `http://127.0.0.1:8004/`. One section per film, one card per
shot, click to play. Under each shot are two fields: your tags (commas
between them) and one sentence. **Every field saves itself** the moment
you click away, into `data/work/<film>/shots.json`.

Stop button in VS Code, or Ctrl+C in the terminal, when you are done.

Tag in pairs: have two groups tag the same footage independently, then
compare. The words they disagree on are the best material in this session.

**This page is the antidote.** The danger of automation is not wrong
labels. It is that you stop looking at the material at all.

### Why it is a server and not just a file

A page opened as a file (`file:///…`) is not allowed to write anything to
your disk — that is the point of a browser. So the script is a very small
web server running on your own machine: the page asks it to save, and the
script, which is ordinary Python, does the writing.

It listens on `127.0.0.1`, which means *this machine only*. Nothing is
online, nothing leaves the drive. Open the script and read it — the whole
server is about forty lines.

### The one file it writes

The button at the top writes `data/out/human_tags.csv` — your words as a
spreadsheet, one row per shot.

Nothing else is saved, because nothing else needs to be: the words
themselves live in `data/work/<film>/shots.json`, and this page is how
you look at them. Start the script again whenever you want it back. It
re-reads the tables on every refresh, so after Gemma has written captions
(week 7) they appear under the shots without restarting anything.

## When it breaks

- **"Address already in use"** → the page is still running in another
  terminal, or use `--port 8010`
- **the browser does not open by itself** → copy the address the terminal
  prints into it
- **CSV shows garbled characters** → open it with Numbers or Google
  Sheets, or import as UTF-8
- **your words vanish** → they are in `data/work/<film>/shots.json`;
  deleting `data/work/` deletes them too

## Think about

1. Open `metadata.json` and count the fields you had never looked at.
   Which of them could you sort your whole folder by — and would that
   sorting tell you anything you could not already see?
2. Of the words you used, how many are visible in the frame, and how many
   only you know? A machine can only ever do the first kind.
3. If the footage is of other people, who gets to decide which words they
   are filed under?
4. You tagged shots. Next week the same words get used as questions, and
   a word you put on four shots may send the model to four others. Which
   of your words do you already expect to fail?

## Homework

Tag at least thirty shots, and keep a note of the words you used more
than once. Those are your vocabulary — next week they go straight to the
model, one at a time, and come back with its own answer next to yours.
