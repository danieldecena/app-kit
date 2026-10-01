#!/usr/bin/env python3
"""Track horizontal displacement of a band across a screen recording.

Screen recordings are variable frame rate, so time comes from the container's
presentation timestamps, never from frame index / fps.

usage: motion-track.py <movie> <crop_w:crop_h:crop_x:crop_y> [max_shift_px]
"""
import subprocess, sys, io, glob, os, tempfile
from PIL import Image

mov, crop = sys.argv[1], sys.argv[2]
maxshift = int(sys.argv[3]) if len(sys.argv) > 3 else 300

ts = [float(l.split(',')[0]) for l in subprocess.run(
    ['ffprobe','-v','error','-select_streams','v:0','-show_entries','frame=pts_time',
     '-of','csv=p=0',mov], capture_output=True, text=True).stdout.splitlines() if l.strip()]

d = tempfile.mkdtemp()
subprocess.run(['ffmpeg','-nostdin','-v','error','-i',mov,'-fps_mode','passthrough',
                '-vf',f'crop={crop},scale=1200:1,format=gray',f'{d}/%05d.png','-y'], check=True)
files = sorted(glob.glob(f'{d}/*.png'))
sigs = [list(Image.open(f).convert('L').getdata()) for f in files]

def best_shift(a, b, lim):
    """Shift of b relative to a, by minimising mean abs difference."""
    best, bs = None, 0
    for s in range(-lim, lim+1):
        ov = [(a[i], b[i+s]) for i in range(len(a)) if 0 <= i+s < len(b)]
        if len(ov) < len(a)//2: continue
        e = sum(abs(x-y) for x, y in ov)/len(ov)
        if best is None or e < best: best, bs = e, s
    return bs

ref = sigs[0]; cum = 0; prev = sigs[0]; out = []
for i, s in enumerate(sigs[1:], 1):
    cum += best_shift(prev, s, 40)
    prev = s
    out.append((ts[i] if i < len(ts) else ts[-1], cum))
print("time_s\tshift_units")
for t, c in out: print(f"{t:.4f}\t{c}")
