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
        ["sips", "-m", SRGB, path, "--out", out],
        capture_output=True,
        text=True,
        check=False,
    )
    if r.returncode != 0 or not os.path.exists(out):
        raise SystemExit(f"sips failed on {path}: {r.stderr.strip()}")
    return Image.open(out).convert("RGB")


def hexs(p):
    return f"#{p[0]:02X}{p[1]:02X}{p[2]:02X}"


def _sv(p):
    _, s, v = colorsys.rgb_to_hsv(*(c / 255 for c in p))
    return s * v


def key_state(im, scale):
    """Detect traffic lights by finding three x-separated clusters of marks.
    Traffic lights are coloured when the window is key and grey when not. A mark is
    a pixel that differs from the box's modal colour by more than 12 on any channel.
    Groups consecutive mark-containing columns into runs. Filters to the three largest
    runs that are at least 1*scale columns wide (noise threshold). Returns 'key' if
    exactly three runs exist and max saturation > 0.5, 'not key' if < 0.1, else
    'unclear'. If not exactly three significant runs, returns unclear."""
    box = (int(10 * scale), int(10 * scale), int(85 * scale), int(40 * scale))
    crop = im.crop(box)
    W, H = crop.size
    px = list(crop.getdata())
    modal = Counter(px).most_common(1)[0][0]

    # Mark pixels that differ from modal colour
    mark = lambda p: max(abs(a - b) for a, b in zip(p, modal)) > 12

    # Count marks per column
    col_marks = []
    for x in range(W):
        count = sum(1 for y in range(H) if mark(px[y * W + x]))
        col_marks.append(count)

    # Find columns with at least 3*scale marks
    mark_cols = [x for x in range(W) if col_marks[x] >= 3 * scale]

    if not mark_cols:
        return "unclear (no traffic lights in the box)", max(_sv(p) for p in px)

    # Group consecutive mark columns into runs
    runs = []
    run_start = mark_cols[0]
    run_end = mark_cols[0]
    for x in mark_cols[1:]:
        if x == run_end + 1:
            run_end = x
        else:
            runs.append((run_start, run_end))
            run_start = x
            run_end = x
    runs.append((run_start, run_end))

    # Filter to three largest runs that are at least 1*scale wide (noise threshold)
    run_widths = [(r, r[1] - r[0] + 1) for r in runs]
    min_noise_width = int(1 * scale)
    significant_runs = [r for r, w in run_widths if w >= min_noise_width]

    # If we have more than 3 significant runs, take the 3 largest
    if len(significant_runs) > 3:
        significant_runs = sorted(
            significant_runs, key=lambda r: r[1] - r[0], reverse=True
        )[:3]
        significant_runs.sort()  # Sort back by position

    sat = max(_sv(p) for p in px)
    if len(significant_runs) != 3:
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
    than the interior, so they lose the count. Returns (None, 0, bg_hex) if the
    box is uniform (all one colour)."""
    px = list(im.crop(box).getdata())
    bg = Counter(px).most_common(1)[0][0]
    dist = lambda p: max(abs(a - b) for a, b in zip(p, bg))
    far = max(dist(p) for p in px)
    if far == 0:
        return None, 0, hexs(bg)
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

    # Test cases for key_state with wide rectangles (should be unclear)
    wide_saturated = Image.new("RGB", (400, 200), (237, 237, 238))
    ImageDraw.Draw(wide_saturated).rectangle((10, 10, 85, 40), fill=(255, 0, 0))
    results.append(
        (
            "wide saturated box is unclear",
            key_state(wide_saturated, 1)[0].startswith("unclear"),
        )
    )

    wide_grey = Image.new("RGB", (400, 200), (237, 237, 238))
    ImageDraw.Draw(wide_grey).rectangle((10, 10, 85, 40), fill=(150, 150, 150))
    results.append(
        ("wide grey box is unclear", key_state(wide_grey, 1)[0].startswith("unclear"))
    )

    # Test cases for glyph
    glyph_test = Image.new("RGB", (100, 100), (240, 240, 240))
    ImageDraw.Draw(glyph_test).ellipse((40, 40, 60, 60), fill=(50, 50, 50))
    g = glyph(glyph_test, (30, 30, 70, 70))
    results.append(("glyph finds dark shape", g[0] == "#323232" and g[2] == "#F0F0F0"))

    uniform = Image.new("RGB", (100, 100), (180, 180, 180))
    g_uniform = glyph(uniform, (10, 10, 90, 90))
    results.append(
        ("uniform box returns None", g_uniform[0] is None and g_uniform[1] == 0)
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
        g = glyph(im, tuple(span(a[a.index("--glyph") + 1])))
        if g[0] is None:
            print(f"glyph none (box is one colour) {g[2]}")
        else:
            print("glyph", *g)
    if "--extent" in a:
        x, y = span(a[a.index("--extent") + 1])
        c, (l, r), (t, b) = extent(im, x, y)
        print(
            f"fill {c}  x {l}-{r} ({(r - l) / scale:g}pt)  y {t}-{b} ({(b - t) / scale:g}pt)"
        )
