#!/bin/zsh
# Shoot a named window of an app at @2x, verified by size AND content, not by
# exit code. Usage: music-shot.sh <app-name> <output-name> [delay-seconds]
#   e.g. music-shot.sh Music window-home-default-dark
#        music-shot.sh Music row-pressed-dark 5
#
# The delay exists for states a human has to HOLD -- a pressed row, an open
# context menu, a drag in flight. Without it the only way to catch one is to
# guess the timing, and a mistimed shot is indistinguishable from "there is no
# pressed state", which is the wrong conclusion to draw from a missed capture.
set -u

if [[ $# -lt 2 || $# -gt 3 ]]; then
  print -u2 "usage: ${0:t} <app-name> <output-name> [delay-seconds]"
  exit 64
fi
APP="$1"; NAME="$2"; DELAY="${3:-0}"
if [[ ! "$DELAY" == <-> ]]; then
  print -u2 "delay must be a whole number of seconds: $DELAY"
  exit 64
fi
if [[ "$NAME" != ${~NAME//[^A-Za-z0-9._-]/} ]]; then
  # The name is interpolated into a Python literal below; keep it boring.
  print -u2 "output name must be [A-Za-z0-9._-] only: $NAME"
  exit 64
fi
DIR="${0:A:h}/music-reference"
HELPER="${0:A:h}/.winid.swift"
mkdir -p "$DIR"

cat > "$HELPER" <<'EOF'
import CoreGraphics
import Foundation
let target = CommandLine.arguments[1]
// .optionAll, NOT .optionOnScreenOnly: macOS drops a fully covered window from
// the on-screen list, and the helper then returns some stray panel instead.
guard let list = CGWindowListCopyWindowInfo(.optionAll, kCGNullWindowID) as? [[String: Any]] else { exit(1) }
var best: (Int, Int, Int)? = nil
for w in list {
    guard let o = w[kCGWindowOwnerName as String] as? String, o == target else { continue }
    guard (w[kCGWindowLayer as String] as? Int) == 0 else { continue }
    let n = w[kCGWindowNumber as String] as? Int ?? -1
    let b = w[kCGWindowBounds as String] as? [String: CGFloat] ?? [:]
    let wd = Int(b["Width"] ?? 0), ht = Int(b["Height"] ?? 0)
    if best == nil || wd*ht > best!.1*best!.2 { best = (n, wd, ht) }
}
if let b = best { print("\(b.0) \(b.1) \(b.2)") } else { exit(2) }
EOF

# Capture swift's own exit status. Piping into `read` would report the status of
# `read`, so a compile error would be announced as "no window for <app>".
WINLINE=$(swift "$HELPER" "$APP")
SWIFT_RC=$?
if (( SWIFT_RC == 2 )); then
  print -u2 "no layer-0 window for $APP (is it running?)"
  exit 2
elif (( SWIFT_RC != 0 )); then
  print -u2 "window-id helper failed with status $SWIFT_RC -- this is a tooling fault, not a missing window"
  exit 70
fi
read -r ID W H <<< "$WINLINE"

OUT="$DIR/$NAME.png"
rm -f "$OUT"

if (( DELAY > 0 )); then
  print "window $ID found (${W}x${H}pt). Hold the state now --"
  for (( i = DELAY; i > 0; i-- )); do
    print -n "  $i "
    sleep 1
  done
  print "shooting"
fi
screencapture -o -x -l "$ID" "$OUT" || { print -u2 "screencapture failed"; exit 3 }
[[ -s "$OUT" ]] || { print -u2 "screencapture wrote nothing"; exit 3 }

# Verify the EFFECT, not the exit code: the file must be exactly 2x the window's
# point size. A wrong-window grab exits 0 just like a right one.
PW=$(sips -g pixelWidth  "$OUT" | awk '/pixelWidth/{print $2}')
PH=$(sips -g pixelHeight "$OUT" | awk '/pixelHeight/{print $2}')
if [[ -z "$PW" || -z "$PH" ]]; then
  print -u2 "could not read the PNG's dimensions; the capture is kept at $OUT"
  exit 70
fi
if (( PW != W*2 || PH != H*2 )); then
  print -u2 "MISMATCH $NAME: got ${PW}x${PH}, window is ${W}x${H} points (expected $((W*2))x$((H*2)))"
  exit 4
fi

# Verify the CONTENT. A fullscreen window sits on its own Space and
# screencapture returns a uniform rectangle of the right size at exit 0.
DISTINCT=$(/usr/bin/python3 - "$OUT" <<'PY'
import sys
from collections import Counter
from PIL import Image
im = Image.open(sys.argv[1]).convert("RGB")
W, H = im.size
print(len(Counter(im.getpixel((x, y)) for x in range(0, W, 37) for y in range(0, H, 37))))
PY
)
CHECK_RC=$?
# An empty or non-numeric result means the CHECKER broke, which is a different
# thing from a blank window. Never delete the capture on a tooling fault: the
# whole point of this script is that the capture is the evidence.
if (( CHECK_RC != 0 )) || [[ ! "$DISTINCT" == <-> ]]; then
  print -u2 "colour check did not run (status $CHECK_RC, output: ${DISTINCT:-empty})."
  print -u2 "  This is a tooling fault, NOT a verdict on the image."
  print -u2 "  The capture is kept at $OUT -- inspect it before re-shooting."
  exit 70
fi
if (( DISTINCT < 50 )); then
  print -u2 "BLANK $NAME: only $DISTINCT distinct colours. The window is probably"
  print -u2 "  fullscreen (own Space) or never rendered. Take it out of fullscreen."
  mv "$OUT" "$OUT.blank"
  print -u2 "  Kept as $OUT.blank rather than deleted."
  exit 5
fi

print "$NAME  ${PW}x${PH}  ${DISTINCT} colours  (window ${W}x${H}pt, id $ID)"
