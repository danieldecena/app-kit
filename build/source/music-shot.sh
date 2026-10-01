#!/bin/zsh
# Shoot a named window of an app at @2x, verified by size, not by exit code.
# Usage: music-shot.sh <app-name> <output-name>   e.g. music-shot.sh Music window-home-default-dark
set -u
APP="$1"; NAME="$2"
DIR="${0:A:h}/music-reference"
HELPER="${0:A:h}/.winid.swift"

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

read -r ID W H < <(swift "$HELPER" "$APP") || { print -u2 "no layer-0 window for $APP"; exit 2 }
OUT="$DIR/$NAME.png"
rm -f "$OUT"
screencapture -o -x -l "$ID" "$OUT" || { print -u2 "screencapture failed"; exit 3 }

# Verify the EFFECT: the file must be exactly 2x the window's point size.
# A wrong-window grab exits 0 just like a right one.
PW=$(sips -g pixelWidth  "$OUT" | awk '/pixelWidth/{print $2}')
PH=$(sips -g pixelHeight "$OUT" | awk '/pixelHeight/{print $2}')
if [[ "$PW" -ne $((W*2)) || "$PH" -ne $((H*2)) ]]; then
  print -u2 "MISMATCH $NAME: got ${PW}x${PH}, window is ${W}x${H} points (expected $((W*2))x$((H*2)))"
  exit 4
fi

# Verify the CONTENT, not just the geometry. A fullscreen window sits on its own
# Space and screencapture returns a uniform rectangle of the right size at exit 0.
DISTINCT=$(uv run --quiet --with pillow python -c "
from PIL import Image
from collections import Counter
im=Image.open('$OUT').convert('RGB'); W,H=im.size
print(len(Counter(im.getpixel((x,y)) for x in range(0,W,37) for y in range(0,H,37))))
")
if [[ "$DISTINCT" -lt 50 ]]; then
  print -u2 "BLANK $NAME: only $DISTINCT distinct colours. The window is probably"
  print -u2 "  fullscreen (own Space) or never rendered. Take it out of fullscreen."
  rm -f "$OUT"
  exit 5
fi

print "$NAME  ${PW}x${PH}  ${DISTINCT} colours  (window ${W}x${H}pt, id $ID)"
