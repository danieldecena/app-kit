#!/usr/bin/env python3
"""Sample a sidebar region of a 2x window capture.

Prints the ground (sampled just right of the region, mid-height), the most
common colours that differ from it by more than 20 in channel sum, and how
many red pixels the region holds. Coordinates are in points; the capture is
assumed to be @2x, which `screencapture -l` produces on a Retina display.
"""
import sys
from collections import Counter
from PIL import Image

path, x0, x1, y0, y1 = sys.argv[1], *map(float, sys.argv[2:6])
im = Image.open(path).convert("RGB")
s = 2
ground = im.getpixel((int(x1 * s) + 4, int((y0 + y1) / 2 * s)))
ink, red = Counter(), 0
for y in range(int(y0 * s), int(y1 * s)):
    for x in range(int(x0 * s), int(x1 * s)):
        p = im.getpixel((x, y))
        if p[0] > 180 and p[1] < 90 and p[2] < 110:
            red += 1
        if abs(sum(p) - sum(ground)) > 20:
            ink[p] += 1
print("ground  #%02X%02X%02X" % ground)
for p, n in ink.most_common(3):
    print("ink     #%02X%02X%02X  x%d" % (*p, n))
print("red     %d" % red)
