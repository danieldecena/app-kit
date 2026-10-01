# Music capture notes

Reference measurements for App Kit's Apple Music variant
(`_project-knowledge/plans/app-kit-music.md`, slice 1).

Source files live in `music-reference/` and are gitignored, because they contain
album art. `build/` is covered by `~/.gitignore_global:52`, so no `.gitignore`
edit is needed here; the plan's Touches line is wrong about that.

Every value below carries its instrument. A value with no instrument is not a
measurement and must not reach `tokens.json`.

## Method

Capture with `music-shot.sh <app> <name>`, which wraps:

```
screencapture -o -x -l <window-id>
```

Four traps, all hit for real on 2026-09-30:

1. **The window id needs `.optionAll`.** macOS drops a fully covered window from
   the on-screen list, so a helper using `.optionOnScreenOnly` returns a stray
   124x144 panel and `screencapture` grabs that at exit 0.
2. **A fullscreen window cannot be captured.** It sits on its own Space and the
   capture returns a uniform rectangle of the correct size. The first attempt
   produced 3600x2260 containing exactly **one** distinct colour. Keep Music
   windowed. Minimised is fine: the backing store is still readable, and it was
   observed updating (the now-playing track changed between shots).
3. **Size is not content.** The geometry check passed on that blank capture.
   `music-shot.sh` now also counts distinct colours and refuses below 50. Proved
   both ways: it blocks the blank capture and passes a real one at 1233 colours.
4. **Colour comes from the PNG, not from Digital Color Meter**, which samples the
   live screen. `uv run --with pillow`; neither python here has PIL.

Sampling rule learned the hard way: **sweep, do not average a box.** A region
mean is worthless where cards, the MiniPlayer or tinted glass intrude. Take a
scanline and look for rows where every sample agrees.

### Colour space: the one that would have poisoned every token

**`screencapture` writes Display P3, not sRGB.** Reading those bytes as RGB
yields P3 values. `tokens.json` ships CSS hex, which is sRGB by definition, so a
P3 number written there renders visibly wrong. Convert before sampling:

```
sips -m /System/Library/ColorSync/Profiles/sRGB\ Profile.icc <in>.png --out <out>.png
```

The error is invisible on neutrals and large on saturated colour:

| | as captured (P3) | true sRGB |
|---|---|---|
| accent, content text | `#E6444F` | **`#FA2E48`** |
| accent, sidebar icon | `#FF4561` | **`#FF275C`** |
| a mid grey | `#242526` | `#242526` (unchanged) |

So every grey measured before this was found still stands, and every red taken
before it was wrong. Pixel counts are identical either side of the conversion
(707 and 626), which is what confirms it is a straight remap rather than
resampling.

### Motion

Screen recordings are **variable frame rate**. `ffprobe` reports
`r_frame_rate=120/1` while recording 813 frames across 15.39s, about 53fps
actual. The plan's stated method, frames divided by frame rate, is therefore
wrong here. Use the per-frame presentation timestamps:

```
ffprobe -v error -select_streams v:0 -show_entries frame=pts_time -of csv=p=0 <file>
```

Gaps in those timestamps mark exactly when the screen changed, so animations
fall out as bursts of sub-40ms deltas without looking at a single pixel.

Note when extracting frames: `ffmpeg` re-times to constant frame rate by
default and duplicated 542 source frames into 1148 strips. Pass
`-fps_mode passthrough` to keep the real frames.

## Measured

| Role | Dark | Light | Instrument |
|---|---|---|---|
| content ground | `#1F1F20` | `#FDFDFD` | scanline sweep, every sample in a row agreeing. Dark: `window-home-narrow-unfocused-dark.png`. Light: `motion-f0200-light.png` |
| sidebar ground | `#262629` | `#E6E6E8` | same sweep. **Wallpaper-dependent in dark**, see below |
| primary button fill | `#F3F3F3` | not yet | solid fill, maximised playlist capture |
| track title ink | `#DDDDDD` | not yet | solid glyph interior |
| column header ink | `#9A9A9A` | not yet | solid glyph interior |
| **accent, content** | **`#FA2E48`** | not yet | sRGB-converted, 707 stroke-interior pixels of the "Tame Impala" title, `album-detail-unfocused-dark.png`. Found by scanning the whole image for strongly-red pixels rather than guessing coordinates |
| **accent, sidebar icon** | **`#FF275C`** | not yet | same scan, 626 pixels. Differs from the content accent because the sidebar is a vibrancy material; treat as one token rendered through material, not two tokens, until proven otherwise |

For reference, Apple's dark system colours in sRGB are `systemRed #FF453A` and
`systemPink #FF375F`. The measured content accent sits between them and matches
neither, so do not substitute a system colour for it.

The content ground is **flat**, not graded and not tinted by the top artwork.
That closes the open question in the plan.

## Not measured, and why

- ~~The accent.~~ **Measured, see the table above.** Taken from large-title stroke
  interiors rather than a favorited star, because the favorited star turned out
  to be **gold, not accent red** (`album-detail-unfocused-dark.png`, track row 1).
  The web player's `#D60017` is superseded and must not be used.
- **The light-mode accent.** Not yet captured; needs one light-mode shot of a
  page with accent text, such as any album detail page.
- **Whether the sidebar can be hidden at all.** Music appears to have no
  hide-sidebar command, unlike most Mac apps. If `View` offers none, drop that
  row from the shot list rather than chasing it; a variant does not need a state
  the app cannot enter.
- **Sidebar vibrancy.** `#262629` is a reading of *this wallpaper*. The sidebar
  is a material, so no fixed hex is correct. This is why slices 3 and 6 are
  judged in the Swift spike rather than a CSS preview.
- **The hero-card gutter.** The gap between hero cards reads `#EEEEEE` in the
  dark capture, near-white, running the full 478pt height of the hero row
  between two 189.5pt artwork rows. In light mode the same gutter is the page
  ground. A near-white gutter in dark mode is unexplained; do not model it until
  someone looks at it directly.
- **Everything requiring interaction.** Music is blocked by policy for computer
  use, so hover, pressed, selected-while-focused, menus open, sidebar hidden,
  narrow window and the focus ring all need a human hand on the app.
- **All frames in points.** Accessibility Inspector only
  (`/Applications/Xcode.app/Contents/Applications/Accessibility Inspector.app`).

Also unrecorded by the plan's shot list and worth adding: **focused versus
unfocused**. Every still so far is Music unfocused, since Claude was frontmost.
Selection fills and chrome differ between the two.

## Source files

| File | What |
|---|---|
| `window-home-wide-unfocused-dark.png` | 1592x1016pt. Home, queue closed, all shelves. Best general reference |
| `window-home-narrow-unfocused-dark.png` | 980x928pt. Home narrow, queue panel open |
| `motion-f0200-light.png` | Light mode still, frame from `motion-01` |
| `motion-01-light-scroll.mov` | 15.39s, light. Vertical page scrolling. Symlink into `~/Documents` |
| `motion-02-dark-shelf-hscroll.mov` | 9.56s, dark. Horizontal scroll of the Stations shelf. Answers "does it snap to a card?" once analysed |
| `motion-03-dark.mov` | 14.05s, dark. Not yet analysed |

A filename trap: macOS writes **U+202F**, a narrow no-break space, before "PM"
in screen-recording names. A pasted path with an ordinary space fails to open
while `ls` on the directory shows the file. Glob for it rather than typing it.
