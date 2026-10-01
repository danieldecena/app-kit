#!/usr/bin/env python3
"""Find localised UI state changes (hover, pressed, selection) in a recording.

Record while hovering over things; this finds each moment a SMALL region
changed, which is what a hover highlight looks like, and reports where and when
so the before/after can be cropped.

Large-area changes (scrolling, navigation) are ignored on purpose.

usage: state-diff.py <movie> [max_change_fraction] [min_box_pt]
"""

import subprocess, sys, glob, tempfile
from PIL import Image, ImageChops

mov = sys.argv[1]
maxfrac = float(sys.argv[2]) if len(sys.argv) > 2 else 0.06  # ignore big changes
minbox = int(sys.argv[3]) if len(sys.argv) > 3 else 10  # ignore tiny noise

probe = subprocess.run(
    [
        "ffprobe",
        "-v",
        "error",
        "-select_streams",
        "v:0",
        "-show_entries",
        "frame=pts_time",
        "-of",
        "csv=p=0",
        mov,
    ],
    capture_output=True,
    text=True,
)
if probe.returncode != 0:
    raise SystemExit(f"ffprobe failed on {mov}: {probe.stderr.strip() or 'no stderr'}")
ts = [float(l.split(",")[0]) for l in probe.stdout.splitlines() if l.strip()]
# An empty timestamp list would otherwise produce "0 state changes", which reads
# as a finding about the video rather than a failure to read it.
if not ts:
    raise SystemExit(
        f"ffprobe returned no timestamps for {mov}; nothing can be said about it"
    )

d = tempfile.mkdtemp()
# /4 keeps it fast; boxes are reported back in window points. A scaled-image
# coordinate is 4 source pixels, and the source is @2x, so points = scaled * 2.
subprocess.run(
    [
        "ffmpeg",
        "-nostdin",
        "-v",
        "error",
        "-i",
        mov,
        "-fps_mode",
        "passthrough",
        "-vf",
        "scale=iw/4:ih/4,format=gray",
        f"{d}/%05d.png",
        "-y",
    ],
    check=True,
)
fs = sorted(glob.glob(f"{d}/*.png"))
if not fs:
    raise SystemExit(f"ffmpeg extracted no frames from {mov}")
# Padding a short timestamp list would give every extra frame the same time,
# which collapses distinct events into one. Fail rather than mis-time them.
if len(fs) != len(ts):
    raise SystemExit(
        f"frame/timestamp mismatch: {len(fs)} frames against {len(ts)} timestamps. "
        f"The stream was re-timed; event times would be wrong."
    )
W, H = Image.open(fs[0]).size
prev = Image.open(fs[0])
events = []
for i, f in enumerate(fs[1:], 1):
    cur = Image.open(f)
    diff = ImageChops.difference(cur, prev).point(lambda v: 255 if v > 24 else 0)
    bbox = diff.getbbox()
    prev = cur
    if not bbox:
        continue
    x0, y0, x1, y1 = bbox
    frac = ((x1 - x0) * (y1 - y0)) / (W * H)
    if frac > maxfrac:
        continue
    if (x1 - x0) < minbox or (y1 - y0) < minbox:
        continue
    t = ts[i]  # lengths are asserted equal above, so no padding is possible
    events.append((t, x0 * 2, y0 * 2, (x1 - x0) * 2, (y1 - y0) * 2, frac))

# collapse bursts into one event each
out = []
for e in events:
    if out and e[0] - out[-1][-1][0] < 0.20:
        out[-1].append(e)
    else:
        out.append([e])
print(f"{len(out)} localised state changes (boxes in window points)\n")
print("  t(s)     x     y     w     h   area%")
for grp in out:
    t, x, y, w, h, f = max(grp, key=lambda e: e[3] * e[4])
    print(f"{t:7.3f} {x:5} {y:5} {w:5} {h:5} {f * 100:6.2f}")
