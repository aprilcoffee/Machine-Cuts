# Week 3 · ch03 · Shot detection: letting the machine find the cuts

## What you'll do

Chop every film into individual shots automatically. This is the move
that turns "a few long videos" into "hundreds of short, taggable assets".

| script | what it does |
|---|---|
| `01_film_barcode.py` | the whole film as one strip of colour → `data/out/barcodes/<film>.jpg` |
| `02_detect_shots.py` | the real tool, PySceneDetect, every film → `data/work/<film>/cuts.json` |
| `03_split_shots.py` | cut shots + thumbnails → `data/work/<film>/shots/`, `shots.json` |
| `04_keyframe_sheet.py` | **see which stills the model will actually look at** |

Needs the proxies from week 2 (`ch02_vlab/03_make_proxies.py`).

## Every film as one strip of colour

```bash
python ch03_shots/01_film_barcode.py
```

Every frame becomes one colour, the average of all its pixels. Lay those
colours side by side, first frame left, last frame right: a "film
barcode". You can read the editing in it — a long shot is a wide calm
band, fast cutting is a flicker of thin lines, a cut is where the colour
suddenly changes. Put the barcodes of your films next to each other.

`WIDTH` and `HEIGHT` at the top set the size of the picture. A long film
has more frames than `WIDTH` has pixels, so neighbouring frames blend.

## The principle

Last week `ch02_vlab/06_histogram.py` turned one frame into a histogram:
32 numbers for how dark or bright it is. Do that for every frame and
compare each one with the frame before. Inside a shot the numbers barely
change. At a cut they suddenly jump. **The machine does not see shots. It
finds jumps in a list of numbers.**

`02_detect_shots.py` does exactly this with a ready-made tool,
PySceneDetect, for every film. It also handles the cases a plain
comparison gets wrong: fades, cuts to black, a flash of light inside one
shot, shots that are too short to be real.

```bash
python ch03_shots/02_detect_shots.py      # every film -> cuts.json
```

## The threshold is a creative decision

`THRESHOLD` at the top of `02` is how big a jump has to be to count as a
cut. Try a low and a high value:

- low → over-cutting; one handheld pan becomes five shots
- high → a whole dialogue scene survives as one shot

There is no correct threshold, only "how fine do you want your material".
After changing it, delete a film's `cuts.json` to cut that film again.

## From here on, every film is a table

`03_split_shots.py`, for every film:

1. cuts each shot from the **original**, not the proxy → `data/work/<film>/shots/`
2. grabs one thumbnail from the middle of each → `data/work/<film>/keyframes/`
3. writes `data/work/<film>/shots.json`

Open one `shots.json`. Each shot has an id like `harbour/s0007`: the film
and the shot number. From now on the scripts read all the films' tables
as **one** archive, and each week adds a column:

| week | column added |
|---|---|
| 4 | `human_tags` (yours) |
| 5 | `tags` (the model's) + `embeddings.npy` per film |
| 7 | `caption` (Gemma's) |
| 8 | export to EDL / CSV |

### Running it again

Like week 2: a film whose `shots.json` is newer than its `cuts.json` is
skipped. If you re-detect a film's cuts, its old shots are thrown away
and cut again — and so are any tags those shots had, because they
belonged to shots that no longer exist. Add a new film and only the new
film is detected and cut.

---

## Keyframes: do not skip this section

The question every student asks later is "how does it know which frame to
look at?" The answer: **it doesn't. You decided.**

The keyframe saved by `03_split_shots.py` is a **thumbnail** — taken from
the middle of the shot so you can recognise it.

**The model does not look at that.** From week 5 on, the scripts sample
several stills per shot using the rule in `vlab/frames.py`:

```
shot:   |----------------------------------------|
      start                                    end
      skip 10% at each end (fades, motion blur, the tail of
      the previous shot bleeding in)
        |....|===========================|....|
             ↑            ↑            ↑
             n stills spread evenly over the middle 80%
```

Make it visible:

```bash
python ch03_shots/04_keyframe_sheet.py --frames 3
# -> data/out/keyframes.html
```

One section per film, one row of stills per shot, with the seconds they
came from. **Project this page and stop for three minutes.**

- why not every frame? one hour at 25 fps is 90,000 stills
- why not just the middle? things move; a pan from an empty street to a
  face is "a face" only in its last second
- what happens to the three? each becomes a vector, then they are
  **averaged** — which declares that a shot has exactly one meaning

As a class, find a shot whose stills all miss the point. That shot is now
unsearchable, however well you phrase the query later. Two fixes: cut
shorter shots, or raise `--frames`.

## When it breaks

- **no proxy for …** → run `ch02_vlab/03_make_proxies.py` first
- **a film comes out as one shot** → a single take; or the threshold is too high
- **hundreds of shots** → threshold too low, or flicker/handheld footage
- **black thumbnails** → the middle of the shot is a fade; check
  `keyframes.html` to see whether the sampled stills are black too
- **slow** → cutting is done from the original at full size; a long 4K
  film takes a while, but only once

## Think about

1. Is a "shot" a technical unit or an aesthetic one? Where does the
   machine's version differ from yours?
2. If a camera pans from indoors to outdoors in one take, the light
   changes completely and the machine calls it two shots. Is it wrong?

## Homework

Run week 3 on all your films. Pick the film where the machine's cuts are
furthest from yours and write a paragraph on why.
