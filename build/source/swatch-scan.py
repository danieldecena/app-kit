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
