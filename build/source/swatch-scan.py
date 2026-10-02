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
    """Detect Music's traffic lights at fixed template positions. Traffic lights are
    at x = 26, 48.5, 71 pt (y = 26 pt), about 12pt across. Each disc is present when
    its mean colour differs from its adjacent gaps by >= 5 on some channel. Returns
    'key' (all discs present, all > 0.5 saturation*value), 'not key' (all present,
    all < 0.1), or 'unclear'. A capture from another app will read unclear."""
    # Convert template positions from points to pixels
    disc_x_pt = [26, 48.5, 71]
    disc_y_pt = 26
    disc_radius_pt = 3.5
    gap_x_pt = [14, 37, 60, 83]
    gap_y_pt = 26
    gap_radius_pt = 2

    scale_f = float(scale)
    disc_x = [int(x * scale_f) for x in disc_x_pt]
    disc_y = int(disc_y_pt * scale_f)
    disc_r = int(disc_radius_pt * scale_f)
    gap_x = [int(x * scale_f) for x in gap_x_pt]
    gap_y = int(gap_y_pt * scale_f)
    gap_r = int(gap_radius_pt * scale_f)

    # Sample pixels within a circle
    def sample_disc(cx, cy, r):
        px = []
        for x in range(max(0, cx - r), min(im.size[0], cx + r + 1)):
            for y in range(max(0, cy - r), min(im.size[1], cy + r + 1)):
                dx, dy = x - cx, y - cy
                if dx * dx + dy * dy <= r * r:
                    px.append(im.getpixel((x, y)))
        return px

    # Compute mean colour of pixels
    def mean_colour(px):
        if not px:
            return (0, 0, 0)
        r = sum(p[0] for p in px) // len(px)
        g = sum(p[1] for p in px) // len(px)
        b = sum(p[2] for p in px) // len(px)
        return (r, g, b)

    # Check if two colours differ by at least 5 on some channel
    def colour_diff(c1, c2, threshold=5):
        return any(abs(a - b) >= threshold for a, b in zip(c1, c2))

    # Sample each disc and its adjacent gaps
    disc_values = []
    for i, cx in enumerate(disc_x):
        disc_px = sample_disc(cx, disc_y, disc_r)
        if not disc_px:
            return "unclear (no traffic lights at the expected positions)", 0.0

        disc_mean = mean_colour(disc_px)

        # Adjacent gaps (0-1 for disc 0, 1-2 for disc 1, 2-3 for disc 2)
        gap_left_px = sample_disc(gap_x[i], gap_y, gap_r)
        gap_right_px = sample_disc(gap_x[i + 1], gap_y, gap_r)

        if not gap_left_px or not gap_right_px:
            return "unclear (no traffic lights at the expected positions)", 0.0

        gap_pooled = gap_left_px + gap_right_px
        gap_mean = mean_colour(gap_pooled)

        # Check if disc is present
        if not colour_diff(disc_mean, gap_mean):
            return "unclear (no traffic lights at the expected positions)", 0.0

        # Compute saturation*value for disc
        sv = max(_sv(p) for p in disc_px)
        disc_values.append(sv)

    # All three discs present; determine key state from saturation values
    max_sv = max(disc_values)
    if all(sv > 0.5 for sv in disc_values):
        return "key", max_sv
    if all(sv < 0.1 for sv in disc_values):
        return "not key", max_sv
    return "unclear (in between)", max_sv


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

    # Test cases for key_state that FAIL on original code (must read unclear on new)
    saturated_rect = Image.new("RGB", (400, 200), (237, 237, 238))
    ImageDraw.Draw(saturated_rect).rectangle((15, 15, 80, 35), fill=(255, 0, 0))
    results.append(
        (
            "saturated rectangle reads unclear",
            key_state(saturated_rect, 1)[0].startswith("unclear"),
        )
    )

    grey_rect = Image.new("RGB", (400, 200), (237, 237, 238))
    ImageDraw.Draw(grey_rect).rectangle((15, 15, 80, 35), fill=(150, 150, 150))
    results.append(
        (
            "grey rectangle reads unclear",
            key_state(grey_rect, 1)[0].startswith("unclear"),
        )
    )

    grey_lines = Image.new("RGB", (400, 200), (237, 237, 238))
    d_lines = ImageDraw.Draw(grey_lines)
    for x in [20, 40, 60]:
        d_lines.rectangle((x, 12, x + 1, 38), fill=(150, 150, 150))
    results.append(
        (
            "three grey lines read unclear",
            key_state(grey_lines, 1)[0].startswith("unclear"),
        )
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
