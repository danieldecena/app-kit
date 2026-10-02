# Close the Music Provenance Gaps Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Turn the "no instrument recorded" and "not observed" rows of the Music provenance table into witnessed measurements, or into recorded contradictions, using captures already on disk.

**Architecture:** One small scan tool reads a capture, converts it to sRGB, and reports whether the window was key (traffic-light colour) before any colour from that capture is trusted. Three measurement tasks use it on existing captures. A final task writes the results into `MUSIC_PROVENANCE`, the token values and the log, rebuilds, and stops before publishing.

**Tech Stack:** Python 3 with Pillow (`/usr/bin/python3`, the only interpreter here with PIL), `sips`, the captures in `build/source/music-reference/` (gitignored: album art), `build/app_build.py`.

**Spec:** the provenance table in `design-system/project/README.md` ("Where each colour came from", published as artifact v55/v56) and the 2026-10-02 `STATUS.md` decision that created it. This plan closes the rows that entry listed as weak.

## Global Constraints

- Never hand-edit `design-system/project/**` or `swift/AppKit.swift`. Edit `build/app_build.py`, build to a scratch `<out>`, diff, copy. Build: `/opt/homebrew/bin/python3 build/app_build.py <src> <out>` with `<src>/project` a symlink to `build/source/decena-apps-2026-09-24`; put `<src>` and `<out>` in the session scratchpad, not `/tmp`.
- Files under `build/` need `git add -f`.
- Use `/usr/bin/python3` for anything that imports PIL; `/opt/homebrew/bin/python3` for the build. Never bare `python3`.
- Captures are P3 or a display profile. Every read goes through `sips -m "/System/Library/ColorSync/Profiles/sRGB Profile.icc"` first; the scan tool does this.
- A colour from a capture counts only if the capture's window state is witnessed (traffic lights). A "not key" claim from a shot with no lights is "unclear", never "not key".
- A check needs a known-good and a known-bad input before it is trusted.
- Commit with an explicit pathspec, message ending `Co-Authored-By: Claude <noreply@anthropic.com>`. Never `--no-verify`.
- No emoji and no em dashes in generated docs.
- Do not publish to the artifact in this plan. Say what changed and ask.

## What planning already observed

These are the reasons the tasks exist. Each number was read from a capture with the tool in Task 1 while writing this plan; the tasks re-observe them and record them properly.

- `album-selected-inactive-dark.png` is named inactive but its traffic lights are saturated (key window). Its grey pill `#464646` is therefore a key-window, unfocused-list reading, not an app-inactive one. `music-select-inactive` dark has no valid evidence yet.
- `row-selected-inactive-light-vd.png` has grey lights (not key) and a selected row of exactly `#DCDCDC` (370 of 370 samples). The token says `#DCDCDD`.
- Dark Play label reads `#000000` in two key-window captures; the token `on-music-primary` dark says `#0E0E0E`.
- The selected-row label is `#FFFFFF` in key-window captures of both appearances.
- The light MiniPlayer capsule reads about `#F0F0F0`, not the `#FFFFFF` the `on-music-glass` usage text claims. Its pause glyph is `#000000`.
- The selected row is not one shape. Light (key and inactive): full-bleed, x 208-963, 55pt tall, on a playlist page. Dark playlist page: inset pill x 249-922, 55pt tall. Dark album page at 1588pt: pill 1238 x 45pt. The spike's `TrackList` and the README say "pill, 40pt in, 45pt tall, never full-bleed".

## File Structure

- Create: `build/source/swatch-scan.py` (the tool; one file, four functions plus a selftest).
- Modify: `build/source/music-capture.md` (append one dated section with the audit tables).
- Modify: `build/app_build.py` (`MUSIC_PROVENANCE` rows, up to three token values, one usage string).
- Modify (copy from build): `design-system/project/README.md`, `design-system/project/tokens.json`, `swift/AppKit.swift`, and any generated component file the build diff shows.
- Modify: `STATUS.md` (one decision log entry), `TASKS.md` (titles only).

---

### Task 1: The scan tool, with controls

**Files:**
- Create: `build/source/swatch-scan.py`

**Interfaces:**
- Produces: CLI `swatch-scan.py <png> [--scale N] (--lights | --hist Y:X0:X1 | --glyph X0:Y0:X1:Y1 | --extent X:Y)` and `swatch-scan.py --selftest`. Coordinates are image pixels; `--scale` is pixels per point and defaults to 2 above 1800px wide. Output lines: `window: key|not key|unclear (...)`, `hist [(hex, count) x3] <samples>`, `glyph <hex> <count> <background hex>`, `fill <hex>  x L-R (Wpt)  y T-B (Hpt)`.

- [ ] **Step 1: Write the tool**

Create `build/source/swatch-scan.py` with exactly this content:

```python
#!/usr/bin/python3
"""Sample a Music capture, and say whether the window was key when it was shot.

usage: swatch-scan.py <png> [--scale N] (--lights | --hist Y:X0:X1 | --glyph X0:Y0:X1:Y1 | --extent X:Y)
       swatch-scan.py --selftest

All coordinates are image pixels. --scale is pixels per point (2 for a Retina
window shot, 1 for the *-vd.png shots); it defaults to 2 above 1800px wide.
The PNG is converted to sRGB first (sips), because a capture carries the
display's profile and a saturated colour read raw is the wrong number.
"""

import colorsys
import os
import subprocess
import sys
import tempfile
from collections import Counter

from PIL import Image, ImageDraw

SRGB = "/System/Library/ColorSync/Profiles/sRGB Profile.icc"


def to_srgb(path):
    out = os.path.join(tempfile.mkdtemp(), "srgb.png")
    r = subprocess.run(
        ["sips", "-m", SRGB, path, "--out", out], capture_output=True, text=True
    )
    if r.returncode != 0 or not os.path.exists(out):
        raise SystemExit(f"sips failed on {path}: {r.stderr.strip()}")
    return Image.open(out).convert("RGB")


def hexs(p):
    return "#%02X%02X%02X" % tuple(p[:3])


def _sv(p):
    _, s, v = colorsys.rgb_to_hsv(*(c / 255 for c in p))
    return s * v


def key_state(im, scale):
    """The traffic lights are coloured when the window is key and grey when not.
    A blank or fullscreen shot has no lights at all, so absence of colour alone
    must not read as "not key": it needs three disc-sized marks to be there."""
    box = (int(10 * scale), int(10 * scale), int(85 * scale), int(40 * scale))
    crop = im.crop(box)
    px = list(crop.getdata())
    modal = Counter(px).most_common(1)[0][0]
    marks = sum(1 for p in px if max(abs(a - b) for a, b in zip(p, modal)) > 12)
    sat = max(_sv(p) for p in px)
    if marks < 100 * scale * scale:
        return "unclear (no traffic lights in the box)", sat
    if sat > 0.5:
        return "key", sat
    if sat < 0.1:
        return "not key", sat
    return "unclear (in between)", sat


def hist(im, y, x0, x1, n=3):
    c = Counter(im.getpixel((x, y)) for x in range(x0, x1))
    return [(hexs(k), v) for k, v in c.most_common(n)], x1 - x0


def glyph(im, box):
    """Solid interior of a glyph: the most common colour among the pixels farthest
    from the box's background (its modal colour). Antialiased edges are rarer
    than the interior, so they lose the count."""
    px = list(im.crop(box).getdata())
    bg = Counter(px).most_common(1)[0][0]
    dist = lambda p: max(abs(a - b) for a, b in zip(p, bg))
    far = max(dist(p) for p in px)
    solid = Counter(p for p in px if dist(p) >= 0.9 * far)
    k, v = solid.most_common(1)[0]
    return hexs(k), v, hexs(bg)


def extent(im, x, y, tol=3):
    """Walk out from a seed pixel while the colour stays within tol of the seed."""
    seed = im.getpixel((x, y))
    near = lambda p: max(abs(a - b) for a, b in zip(p, seed)) <= tol
    W, H = im.size
    l = x
    while l > 0 and near(im.getpixel((l - 1, y))):
        l -= 1
    r = x
    while r < W - 1 and near(im.getpixel((r + 1, y))):
        r += 1
    t = y
    while t > 0 and near(im.getpixel((x, t - 1))):
        t -= 1
    b = y
    while b < H - 1 and near(im.getpixel((x, b + 1))):
        b += 1
    return hexs(seed), (l, r + 1), (t, b + 1)


def selftest():
    def shot(lights, row):
        im = Image.new("RGB", (400, 200), (237, 237, 238))
        d = ImageDraw.Draw(im)
        for i, c in enumerate(lights):
            cx = 26 + 22 * i
            d.ellipse((cx - 6, 26 - 6, cx + 6, 26 + 6), fill=c)
        d.rectangle((100, 100, 300, 140), fill=row)
        return im

    ok = shot([(255, 95, 87), (254, 188, 46), (40, 200, 64)], (220, 220, 220))
    off = shot([(207, 207, 207)] * 3, (220, 220, 220))
    blank = Image.new("RGB", (400, 200), (255, 255, 255))
    results = [
        ("known-good key", key_state(ok, 1)[0] == "key"),
        ("known-good not key", key_state(off, 1)[0] == "not key"),
        ("blank shot is not 'not key'", key_state(blank, 1)[0].startswith("unclear")),
        ("hist finds the fill", hist(ok, 120, 110, 290)[0][0][0] == "#DCDCDC"),
        ("extent walks the fill", extent(ok, 200, 120)[1] == (100, 301)),
    ]
    mixed = Image.new("RGB", (400, 200), (255, 255, 255))
    ImageDraw.Draw(mixed).rectangle((0, 0, 99, 199), fill=(10, 10, 10))
    results.append(
        ("mixed row is not one fill", hist(mixed, 50, 0, 200)[0][0][1] <= 100)
    )
    for name, passed in results:
        print(("ok   " if passed else "FAIL ") + name)
    return all(p for _, p in results)


def span(s):
    return [int(v) for v in s.split(":")]


if __name__ == "__main__":
    a = sys.argv[1:]
    if a == ["--selftest"]:
        sys.exit(0 if selftest() else 1)
    path = a[0]
    scale = float(a[a.index("--scale") + 1]) if "--scale" in a else None
    im = to_srgb(path)
    if scale is None:
        scale = 2 if im.size[0] > 1800 else 1
    print(f"{os.path.basename(path)} {im.size[0]}x{im.size[1]} scale {scale:g}")
    if "--lights" in a:
        state, sat = key_state(im, scale)
        print(f"window: {state} (max saturation {sat:.2f})")
    if "--hist" in a:
        y, x0, x1 = span(a[a.index("--hist") + 1])
        print("hist", *hist(im, y, x0, x1))
    if "--glyph" in a:
        print("glyph", *glyph(im, tuple(span(a[a.index("--glyph") + 1]))))
    if "--extent" in a:
        x, y = span(a[a.index("--extent") + 1])
        c, (l, r), (t, b) = extent(im, x, y)
        print(
            f"fill {c}  x {l}-{r} ({(r - l) / scale:g}pt)  y {t}-{b} ({(b - t) / scale:g}pt)"
        )
```

- [ ] **Step 2: Run the controls**

Run: `/usr/bin/python3 build/source/swatch-scan.py --selftest`
Expected: six lines starting `ok   `, exit 0. The cases are a coloured-lights shot (key), a grey-lights shot (not key), a blank shot (must read `unclear`, not `not key`), a fill, a walked extent, and a half-dark row (must not read as one fill).

- [ ] **Step 3: Prove the witness on real captures**

Run, from `build/source/music-reference`:

```bash
for f in album-selected-inactive-dark.png row-selected-inactive-light-vd.png album-transport-inactive-dark.png row-selected-key-dark-vd.png row-selected-key-light-vd.png; do
  /usr/bin/python3 ../swatch-scan.py $f --lights | tail -1
done
```

Expected, in order: `key`, `not key`, `not key`, `key`, `key`. The first is the finding: a file named inactive that was shot with the window key.

- [ ] **Step 4: Commit**

```bash
git add -f build/source/swatch-scan.py
git commit -m "Add swatch-scan: sample a Music capture and witness its key state" -- build/source/swatch-scan.py
```

---

### Task 2: Witness every capture a provenance row leans on

**Files:**
- Modify: `build/source/music-capture.md` (append a section)

**Interfaces:**
- Consumes: `swatch-scan.py --lights` from Task 1.
- Produces: a table, in the log, of capture name, appearance, window state, and which provenance rows it may support. Task 4 reads it.

- [ ] **Step 1: Scan the inactive-named and Play-label captures**

Run, from `build/source/music-reference`:

```bash
for f in album-selected-inactive-dark.png album-selected-row-dark.png album-transport-inactive-dark.png home-inactive-dark-sidebar.png home-miniplayer-inactive-dark.png album-light-inactive.png album-light-inactive-sidebar.png album-inactive-light.png row-selected-inactive-light-vd.png row-selected-key-dark-vd.png row-selected-key-light-vd.png; do
  /usr/bin/python3 ../swatch-scan.py $f --lights | tr '\n' ' '; echo
done
```

Expected: one `window:` verdict per file. Any `unclear` is recorded as unclear and the file is not used as evidence for a state.

- [ ] **Step 2: Find out whether any dark capture shows a selected track row with the window not key**

For every file Step 1 reports `not key` and that is dark, view it (Read the PNG) and note whether a selected track row is visible. Planning only confirmed `album-transport-inactive-dark.png` as not-key, and its name says it shows the transport, not a selected track row; the other dark inactive-named files were not scanned. If one does show a selected row, scan it with `--hist Y:X0:X1` across a text-free band of the row and record the fill.

- [ ] **Step 3: Append the audit to the log**

Append to `build/source/music-capture.md` a section `### Window state of the captures behind the provenance table (2026-10-02)` containing the table from Step 1 (file, appearance, `key` / `not key` / `unclear`, max saturation), the sentence "state witnessed by traffic-light saturation after sRGB conversion, `build/source/swatch-scan.py --lights`", and the Step 2 result. State plainly that `album-selected-inactive-dark.png` is a key-window shot, so `#464646` is the fill of a selected row in a key window whose list is not focused, and that no dark app-inactive selected-row capture exists.

- [ ] **Step 4: Commit**

```bash
git add -f build/source/music-capture.md
git commit -m "Log which captures behind the provenance table were key or not key" -- build/source/music-capture.md
```

---

### Task 3: Sample the labels, the light fill and the capsule

**Files:**
- Modify: `build/source/music-capture.md` (append to the Task 2 section)

**Interfaces:**
- Consumes: `swatch-scan.py` from Task 1; the window-state table from Task 2.
- Produces: the numbers Task 5 writes into `MUSIC_PROVENANCE` and the tokens.

All coordinates below are 1x (`*-vd.png`, 980x779) unless a file is 3176x2014, where `--scale 2` is the default. Run from `build/source/music-reference`. Only a capture the Task 2 table marks `key` may support a key-window claim; only one marked `not key` may support an inactive claim.

- [ ] **Step 1: Selected-row fill, light, inactive**

```bash
/usr/bin/python3 ../swatch-scan.py row-selected-inactive-light-vd.png --lights --hist 480:330:700
```

Expected: `window: not key`, and `hist [('#DCDCDC', 370), ...] 370`. All 370 samples one colour. This settles `music-select-inactive` light as measured `#DCDCDC`, one unit under the token's `#DCDCDD`.

- [ ] **Step 2: Selected-row label, both appearances, key window**

```bash
/usr/bin/python3 ../swatch-scan.py row-selected-key-dark-vd.png --lights --glyph 305:516:360:531
/usr/bin/python3 ../swatch-scan.py row-selected-key-light-vd.png --lights --glyph 305:597:410:613
```

Expected: both `window: key`; dark `glyph #FFFFFF 63 #CC132C`, light `glyph #FFFFFF 93 #DC1229`. The background field is the row fill, which confirms the box sits on the selected row. This measures `on-music-select` in both appearances.

- [ ] **Step 3: Play-button label, dark, two captures**

```bash
/usr/bin/python3 ../swatch-scan.py row-selected-key-dark-vd.png --lights --glyph 630:295:690:313
/usr/bin/python3 ../swatch-scan.py album-selected-inactive-dark.png --lights --glyph 1400:585:1520:635
```

Expected: both `window: key`; the first `glyph #000000 111 #F3F3F3`, the second `glyph #000000 654 #F3F3F3`. The background `#F3F3F3` is `music-primary` dark, which confirms the box is on the Play button. Two captures agree on `#000000`; the token `on-music-primary` dark is `#0E0E0E`.

- [ ] **Step 4: MiniPlayer capsule and pause glyph, light, inactive**

```bash
/usr/bin/python3 ../swatch-scan.py row-selected-inactive-light-vd.png --hist 712:260:930
/usr/bin/python3 ../swatch-scan.py row-selected-inactive-light-vd.png --glyph 316:722:338:746
```

Expected: the hist's top colours are about `#F1F1F1`, `#F0F0F0`, `#EAEAEA` (the capsule is translucent over the rows behind it, so it is a range, not one value); the glyph reads `#000000` as the modal colour with the capsule as the far colour (`#EDEDED` seen in planning). Record the range, not a single hex. The `on-music-glass` usage text says the light capsule is `#FFFFFF`; this contradicts it.

- [ ] **Step 5: Append the results and commit**

Append a table under the Task 2 section: rows for Steps 1-4 with the command, the window state, and the observed values. Add one line for each prediction in "What planning already observed" that held or did not.

```bash
git add -f build/source/music-capture.md
git commit -m "Log label, light-fill and capsule samples behind the provenance rows" -- build/source/music-capture.md
```

---

### Task 4: Measure the selected row's shape in both appearances

**Files:**
- Modify: `build/source/music-capture.md` (append)

**Interfaces:**
- Consumes: `swatch-scan.py --extent`.
- Produces: a geometry table. Task 5 states the discrepancy in `STATUS.md`; changing `TrackList` is out of scope here and is a follow-up for the user.

Seeds are chosen above the 40px artwork thumbnail so the walk is not stopped by it: 4px below the row's top edge.

- [ ] **Step 1: Measure the four selected rows**

```bash
/usr/bin/python3 ../swatch-scan.py row-selected-key-light-vd.png --extent 650:589
/usr/bin/python3 ../swatch-scan.py row-selected-inactive-light-vd.png --extent 650:456
/usr/bin/python3 ../swatch-scan.py row-selected-key-dark-vd.png --extent 650:508
/usr/bin/python3 ../swatch-scan.py album-selected-inactive-dark.png --extent 1500:975
```

Expected: light key `fill #DC1229 x 208-963 (755pt) y 585-640 (55pt)`; light inactive `fill #DCDCDC x 208-963 (755pt) y 452-507 (55pt)`; dark key playlist `fill #CC132C x 249-922 (673pt) y 504-559 (55pt)`; dark album `fill #464546 x 620-3096 (1238pt) y 960-1050 (45pt)`. The dark playlist left edge is 249 not 248 because the walk is 4px under a 6pt corner radius; say so rather than correcting it.

- [ ] **Step 2: Establish the page type for each capture**

View each of the four PNGs. The first three are a playlist page ("Jump rope", rows with artwork, 56pt pitch); the fourth is an album page ("Charm", track-number rows, about 45-46pt pitch). Record this beside each row, because the 45pt figure in the log and README came from an album page and the 55pt figures are playlist rows.

- [ ] **Step 3: Control**

Run the same `--extent` on the dark playlist capture with the seed on a non-selected row's background (for example `650:480`). Expected: the walk returns the ground colour and an extent far larger than a row, which shows the tool distinguishes a fill from the ground.

- [ ] **Step 4: Append and commit**

Append a section `### Selected-row shape by appearance and page (2026-10-02)` with the table and the page type, and one sentence of verdict: which of "inset pill", "full-bleed", "45pt" and "55pt" each capture supports. Do not edit `TrackList`.

```bash
git add -f build/source/music-capture.md
git commit -m "Measure the selected row's shape by appearance and page type" -- build/source/music-capture.md
```

---

### Task 5: Write the results into the provenance table and tokens

**Files:**
- Modify: `build/app_build.py` (`MUSIC_PROVENANCE`; `T("music-select-inactive", ...)`; `T("on-music-primary", ...)`; the `on-music-glass` usage string)
- Modify (copy from build): files the build diff shows
- Modify: `STATUS.md`, `TASKS.md`

**Interfaces:**
- Consumes: the numbers from Tasks 3 and 4.
- Produces: a rebuilt tree whose provenance rows match the evidence. The class codes are `M` measured, `N` no instrument recorded, `D` derived, `U` not observed.

- [ ] **Step 1: Update the rows**

In `MUSIC_PROVENANCE` in `build/app_build.py`, change only what Tasks 3 and 4 observed. Planning predicts these; apply a change only if the task output matches, and otherwise keep the old row and write why in its evidence:

- `music-select-inactive`: light `N` -> `M`, evidence naming `row-selected-inactive-light-vd.png` (window not key, 370 of 370 samples). Dark stays `N`; its evidence becomes "`album-selected-inactive-dark.png` was shot with the window key, so `#464646` is the fill of a selected row in a key window with an unfocused list; no app-inactive dark capture exists".
- `on-music-select`: `("U", "N", ...)` -> `("M", "M", ...)`, evidence naming `row-selected-key-light-vd.png` and `row-selected-key-dark-vd.png` (window key, label `#FFFFFF` in both).
- `on-music-primary`: dark `N` -> `M` for the sampled value, evidence naming both captures.
- `on-music-glass`: light `N` -> `M` for the pause glyph `#000000`, evidence stating the capsule fill is a translucent range of about `#EAEAEA` to `#F1F1F1`, not `#FFFFFF`.

- [ ] **Step 2: Update the three token values only where measurement differs**

- `music-select-inactive` light: `#DCDCDD` -> `#DCDCDC`.
- `on-music-primary` dark: `#0E0E0E` -> `#000000`, only because two captures agree.
- `on-music-glass` usage string: replace "Light is MEASURED #000000 on a #FFFFFF capsule" with the measured range from Task 3 Step 4. Leave the values.

The contrast gate recomputes every ratio and fails the build if a floor is missed. If it fails, the measured value wins and the claim that referenced the old ratio is corrected.

- [ ] **Step 3: Build, diff, run the controls**

```bash
S=<session scratchpad>; mkdir -p $S/ak/src && ln -sfn "$PWD/build/source/decena-apps-2026-09-24" $S/ak/src/project
rm -rf $S/ak/out && /opt/homebrew/bin/python3 build/app_build.py $S/ak/src $S/ak/out
diff -rq $S/ak/out/project design-system/project; diff -q $S/ak/out/swift/AppKit.swift swift/AppKit.swift
```

Expected: the build passes; the diff names `README.md`, `tokens.json`, `swift/AppKit.swift` and any component README that quotes a changed value, and nothing else except `design-system.json` (not generated). Then mutate once to prove the provenance check still fires: delete the `on-music-select` row from a scratch copy of `build/app_build.py`, run it, expect `no provenance row for on-music-select` and a non-zero exit, and assert the mutation applied before trusting that result.

- [ ] **Step 4: Copy, log, commit**

Copy the two trees into place (`design-system/project/` from `$S/ak/out/project` except `design-system.json`; `swift/AppKit.swift`). Append one `STATUS.md` decision entry under `### 2026-10-02` stating: which rows became measured, which stay `N` and why, the two token values changed, the corrected capsule claim, and the geometry finding (light selection is full-bleed on a playlist page; dark playlist pill is 55pt, dark album pill is 45pt; `TrackList` and the README say 45pt inset pill, so this needs a decision from the user). Add one `TASKS.md` line, titles only: `- [ ] Decide TrackList selected-row shape: light full-bleed, 55pt on playlists`.

```bash
git add -f build/app_build.py
git commit -m "Close provenance gaps from witnessed captures; correct two token values" -- build/app_build.py design-system/project swift/AppKit.swift STATUS.md TASKS.md
```

- [ ] **Step 5: Stop and report**

Report the rows that changed, the token values that moved and by how much, the geometry finding, and that the artifact still carries the old table. Do not publish; ask.

---

## Self-review

- **Spec coverage:** the four "no instrument recorded" rows and the one "not observed" row each map to a task: `music-select-inactive` (Tasks 2, 3.1, 5), `on-music-primary` dark (3.3, 5), `on-music-select` (3.2, 5), `on-music-glass` light (3.4, 5). The dark `music-select-inactive` value cannot be closed from existing captures and the plan says so instead of guessing; it needs a new capture with the system in Dark and the window not key, which is the user's switch.
- **Placeholders:** none; every command and expected value was run against the real captures while writing this plan. The one `<session scratchpad>` is the harness-provided directory, named in the system prompt.
- **Consistency:** the tool's flag names (`--lights`, `--hist`, `--glyph`, `--extent`) and the class codes (`M`, `N`, `D`, `U`) are the same in every task.
- **Known limit:** the scan tool reads one pixel row or one box, not a rendered state machine. A capture whose lights are covered by another window reads `unclear`, not `not key`, which is deliberate.
