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

### Driving the window width without touching Music

Music is policy-blocked for automation, so its window cannot be resized
directly. But **changing a display's resolution resizes the windows on it**, and
BetterDisplay exposes that from the command line:

```
betterdisplaycli get --name="Virtual 16:9" --resolution        # 2560x1440
betterdisplaycli set --name="Virtual 16:9" --resolution=1600x900
```

With Music parked on a virtual display this gives hands-off control of the one
variable the layout actually responds to. A descending sweep produced six
distinct window widths (2049, 2049, 1792, 1600, 1376, 1280) with no interaction
with Music at all.

Two things about the mechanism:

- **Only shrinking works.** macOS resizes a window down to fit a smaller display
  but does not grow it back, so a sweep must descend. An ascending sweep gave
  two widths out of six attempts.
- It changes a real display, so record the starting resolution and restore it.

This is what makes the gap breakpoint (16pt narrow, 20pt wide) findable: it
needs many widths, and widths were previously only available by asking a human
to drag a window.

### Finding interaction states: `state-diff.py`

```
uv run --with pillow python build/source/state-diff.py <mov>
```

Record while hovering over things; this reports every moment a **small** region
changed, with its bounding box in window points, ignoring large changes like
scrolling and navigation. It is how hover, pressed and selection states get
located without driving the app, which is blocked for Music.

On `motion-04` it found 19 localised changes, including full-width
**1210 x 74pt** and **1210 x 50pt** boxes (track-row hovers) and **40pt-wide**
columns (the favorited-star column).

#### Track-row hover, measured (dark)

| Property | Value |
|---|---|
| fill | **`#2C2C2D`** sRGB, against the `#1E1F20` ground |
| size | **1238 x 45pt** |
| horizontal inset | **40pt** each side, within the 1318pt content width |
| vertical inset | **5.5pt** top and bottom, within the 56pt row |
| corner radius | **~6pt** (left edge moves 5.5pt over the first 6pt, then flat) |

So the highlight is a **rounded inset pill, not a full-bleed row fill**. Built as
a full-width fill it would read wrong immediately. Exactly one band in the
capture matched, which is what confirms it is the hovered row and not a
separator or the playing row.

#### Track-row selected, measured (dark)

**Same shape, different fill.** The selected row is the identical pill:

**Selection has two appearances, and which one you see depends on window focus.**

| state | dark | light | when |
|---|---|---|---|
| hover | **`#2C2C2D`** | **`#F0F0F0`** | pointer over the row. Dark value measured twice independently |
| selected, window **active** | **`#CC132D`** | **`#DC1229`** | Music is the key window |
| selected, window **inactive** | **`#464646`** | **`#DCDCDD`** | any other app is frontmost |

#### Losing focus changes more than the selection

The **Play button inverts completely** when the window is not key. Light mode,
measured at the AX-reported frame (x=655 y=285 132x38pt) rather than by scanning:

| | fill | label |
|---|---|---|
| active | `#0E0E0E` | `#FFFFFF` |
| **inactive** | **`#ECECEC`** | **`#242424`** |

Black-on-white becomes light-grey-with-dark-text. It does not dim, it swaps.

**This is the single most important state for the first adopter.** Claude
Spinner is a monitor app, so an unfocused window is its normal condition, and
every value in the inactive column is what its users will actually see. A build
tested only with the window in front would render none of them.

**The sidebar icons lose their red entirely.** Sampled at the icon column
(x 20-47pt), not the label text:

| | red-ish pixels | most saturated |
|---|---|---|
| dark, active | 1562 | `#FF2156` |
| light, active | 1796 | `#FF003C` |
| light, **inactive** | **0** | `#E7E7E7` |

So an inactive window renders its accent-tinted symbols as plain grey. Combined
with the Play button inversion, **losing focus is a whole-window state change,
not a single control's dim.**

Method note: a first attempt at this sampled x 97-132pt and found no red in any
appearance, which nearly got written down as "the icons are not red in light
mode". That range is the label text. The icon column had already been located at
x=31pt in an earlier measurement and simply was not reused.

Geometry is identical across both appearances and both states: **1238pt wide,
45pt tall, x 310.0-1547.5pt**. The selected pill is the reliable one to measure
because red matches nothing else on the page; a light-mode hover scan for
`#F0F0F0` runs into the sidebar ground `#EDEDEE` and over-reports the width as
1348pt.

Note the selection fill is **not** the accent in either theme. Accent is
`#FA2E48` dark / `#FA233B` light; selection is `#CC132D` / `#DC1229`, darker and
more saturated in both. Three separate red tokens, none derivable from another.

This is standard macOS active/inactive selection, and it caught me out: the
first "selected" capture read red because Music was still key at that moment,
and a later capture of the same state read grey because it was not.

**It matters more than usual for the first adopter.** Claude Spinner is a
monitor app, so its window is unfocused most of the time. The inactive grey is
therefore the state its users will see most, and it is the one most likely to be
skipped by a build that only ever tests with the window in front.

| | hover | selected |
|---|---|---|
| fill | `#2C2C2D` | **`#CC132D`** (active) |
| width | 1238pt | 1238pt |
| x span | 310.0-1547.5pt | 310.0-1547.5pt |
| height | 45.0pt | ~45.5pt |
| corner radius | ~6pt | ~5pt |
| label | normal ink | white |

One rounded pill, two fills. That is a single component with a state, not two
layouts.

**`#CC132D` is its own value, not a derivation.** App Kit's convention is the
accent stepped 20% toward black, which from `#FA2E48` would give `#C8253A`.
The measured fill is `#CC132D` — close in lightness, different in hue and
saturation. Deriving it would be visibly wrong, so it ships as a measured token.

Note also that the accent-derived fills do **not** collapse into one value:
the light-mode CTA button is `#FA233B` (the accent itself) while the dark
selected row is `#CC132D`. Different contexts, different tokens.

**Anatomy** (structure only, corroborated by two sources):

- the track number is replaced by a play triangle
- a star appears in the leading 40pt column
- a "+" appears toward the trailing edge
- the whole row takes a fill

The two sources are `state-diff.py`'s boxes on the Mac app, which found exactly
a full-width row change plus a 40pt leading-column change, and a screenshot of
the **web player**, which shows the same four changes legibly. The web player is
barred as a value source and that screenshot is a good illustration of why: its
ground is blue-tinted, nowhere near the Mac app's neutral `#1F1F20`. It is being
used here for structure only, and no number from it may be recorded.

**But do not take colour from a recording.** Recording frames are
**Rec. ITU-R BT.709**, a third colour space after the P3 of stills and the sRGB
of tokens, and video encoding shifts values far beyond rounding:

| | from the recording | from a still capture |
|---|---|---|
| content ground, dark | `#0D0D0D` | `#1F1F20` |

So the division of labour is: **recordings give geometry, timing, and the fact
that a state exists; stills give its colour.** A hover's fill must be sampled
from a still capture taken while the pointer rests on the element.

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

### Measured motion: page navigation is NOT animated

From `motion-04.mov` (Home -> playlist detail -> back -> Home -> another
detail), by per-frame difference against the VFR timestamps.

Navigating to a detail page produces a **single-frame** change with a difference
peak of 48-60 against a median of 0.07. One frame. There is no push, no
cross-fade, no slide.

What happens instead, measured as the fraction of the content area holding the
flat ground colour:

```
 t=2.45s   0.12   content present
 t=2.60s   1.00   CONTENT AREA COMPLETELY BLANK
 t=2.90s   0.60   content back, still sparse
 t=4.00s   0.36   artwork still filling in
```

So the sequence is: **clear the content area to flat ground instantly, hold a
blank state for roughly 0.15-0.4s, then populate, with artwork continuing to
load progressively for seconds afterwards.** The sidebar and the MiniPlayer
never blank; only the content region does.

Consequence for the variant: do not build an animated page transition. Build an
empty state for the content region and an async artwork placeholder. An
animated push would be *more* work and *less* faithful.

### Measured motion: the shelf DOES snap to a card

Tool: `build/source/motion-track.py`, which tracks a band's horizontal
displacement frame by frame via 1-D cross-correlation and reports position
against the container's real timestamps.

```
swift-free:  uv run --with pillow python motion-track.py <mov> <w:h:x:y>
```

From `motion-02-dark-shelf-hscroll.mov`, tracking the Stations shelf:

```
 t=5.58s      0.0pt
 t=5.79s    306.3pt    1808 pt/s
 t=6.00s    699.1pt    1886 pt/s   <- peak
 t=6.21s    853.6pt     742 pt/s
 t=6.42s    878.9pt     121 pt/s
 motion ends t=6.308s
```

**Final displacement 878.9pt against a 219.5pt card pitch = 4.00 cards**, landing
within 0.9pt (0.1%). The velocity profile rises then decays smoothly to zero:
a clean ease-out over roughly **0.73s**, with no overshoot and no spring return.

So `music-motion-shelf` is an ease-out of ~0.73s that settles on a card
boundary. Caveat worth keeping: this is **one** scroll event. Landing within
0.1% of an exact multiple is strong evidence of snapping rather than chance, but
a second event would turn it from strong evidence into a confirmed rule, and
would also show whether 4 cards is fixed or just how far that flick went.

Also visible: a small -81pt excursion at 4.95s that returns to -70.6pt and
holds, before the main movement. That looks like a drag that was released below
the snap threshold, which would be worth confirming as the rubber-band
behaviour.

Identified: the 9.942-10.575s event in `motion-04` is a **fast vertical scroll**,
not a UI animation. Frames across it are identical until the last, then far down
the page.

### Measured motion: the appearance switch IS animated

From `motion-03-dark.mov`, tracking sidebar luminance (chrome, so it flips hard;
an earlier attempt sampled card artwork, which stays colourful in both
appearances and barely moved).

```
 8.528s   flat, light      233
 8.545s     5.3% complete
 8.645s    45.1%
 8.720s    72.2%
 8.853s    93.5%
 8.995s   100%, dark        37
```

**0.47s, ease-out**: half the distance in the first 0.14s, the remaining half
over 0.33s.

A first pass reported 3.92s. That was the start detector firing on a 3-unit
luminance drift at 5.0s caused by artwork loading, not by the switch. The
transition only begins once the value leaves its flat 228.8 plateau.

### Motion summary across all four recordings

| Event | Animated? | Duration | Curve |
|---|---|---|---|
| page navigation | **no** | single frame, then a blank content area for ~0.15-0.4s | n/a |
| shelf horizontal scroll | yes | ~0.73s | ease-out, snaps to a card boundary |
| appearance switch | yes | **~0.47s** | ease-out |
| vertical page scroll | yes | varies with the flick | inertial |

So Music animates **state** changes (appearance, scroll position) and does not
animate **navigation**. That is the opposite of the usual instinct, which is to
animate the page transition and let everything else snap.

## Measured

All sRGB unless marked. Values taken before the P3 discovery have been redone.

| Role | Dark | Light | Instrument |
|---|---|---|---|
| **accent, content** | **`#FA2E48`** | **`#FA233B`** | stroke interiors of the "Tame Impala" title, found by scanning the whole image for strongly-red pixels rather than guessing coordinates. 707 px dark, ~445 px light |
| **accent, sidebar icon** | **`#FF275C`** | **`#FF0029`** | same scan, 626 px in both. Differs from the content accent because the sidebar is a vibrancy material; treat as one token through material, not two tokens, until proven otherwise |
| **transport button fill** (Play) | **`#F3F3F3`** | **`#0E0E0E`** | widest dark/light run in the header band. Light: 124pt wide at y=294pt, 2484 px of `#0E0E0E`. **It inverts with appearance**: maximum contrast against the ground |
| **CTA button fill** (Set Location) | **`#FA2E48`** | **`#FA233B`** | filled bar, 32pt tall in both themes, white label. **Exactly the content accent in each theme**, so the CTA fill is not a separate token: it IS `music-accent` |
| surface (detail panel) | not yet | `#FFFFFF` | vertical sweep, y=60-540pt on the album page |
| ground | `#1F1F20` | `#FFFFFF` | row-wise sweep where every sample agrees. Light confirmed on Home; `#F8F8F8` is a section background on album pages, not the ground |
| sidebar ground | `#262629` | `#EDEDEE` | same sweep. **Wallpaper-dependent in dark**, see below |
| **ink** (track titles) | `#DDDDDD` | **`#272727`** | darkest-common glyph interior, found by searching the content area rather than sampling a guessed coordinate. 4547 px light |
| **ink-soft** (duration, "…") | `#9A9A9A` | **`#808080`** | same method, 2449 px light |

**Music runs lower contrast than App Kit in both directions.** App Kit is
`ink #F5F5F7 / #1D1D1F` and `ink-soft #98989D / #636366`. Music is a dimmer
white on dark, a lighter black on light, and a notably lighter secondary grey.
The variant therefore softens text rather than inheriting App Kit's inks, which
is the opposite of what a design system usually wants and needs stating
explicitly or it will be "corrected" back.

**Light mode has two grounds**, which maps onto App Kit's existing `surface` /
`ground` split: `#FFFFFF` for the detail panel, `#F8F8F8` for the content below
it. App Kit light is `ground #F2F2F7` / `surface #FFFFFF`, so the surface matches
and the ground needs lightening.

Resolved by a light Home capture: **light ground is `#FFFFFF`**. The `#F8F8F8`
measured on the album page is a *section* background under "More By" and
"Featured On", not the global ground, and the `#FDFDFD` from the pre-P3 motion
frame is superseded. So the album page has three bands: `#FFFFFF` detail panel,
`#F8F8F8` related-content section, `#FFFFFF` elsewhere.

### The hero gutter: RETRACTED, there was never a mystery

An earlier version of this section claimed the gutter between hero cards
measures `#EEEEEE` in **dark** as well as light, concluded it therefore does not
invert, and reasoned from that it could not be the ground showing through.

**All of it was wrong, from one mislabelled file.** The capture used as the
"dark" source, then named `window-home-wide-unfocused-dark.png`, is a **light
mode** capture. It was renamed from `probe-minimized.png` and labelled by
assumption rather than by looking. Sampling its sidebar gives `#F2F2F2` and the
area above the shelf `#FFFFFF`.

So both gutter measurements were light-mode measurements, and `#EEEEEE` against
a near-white ground is entirely ordinary. **The gutter has never been measured
in dark mode at all.** The simple reading, that the gap is the ground showing
between cards, is unrefuted and is what AX supports: cards are 257.5pt wide at
277.5pt pitch with no element between them.

The one thing that survives is the width. **20pt**, from the line profile and
independently from AX (277.5 - 257.5). That was never in doubt.

Every other capture's name was audited against its actual mean luminance after
this was found; only this one was wrong.

Lesson worth keeping: a filename is not an observation. This one asserted an
appearance that was never checked, and then a finding was built on top of it and
committed.

For reference, Apple's dark system colours in sRGB are `systemRed #FF453A` and
`systemPink #FF375F`. The measured content accent sits between them and matches
neither, so do not substitute a system colour for it.

The content ground is **flat**, not graded and not tinted by the top artwork.
That closes the open question in the plan.

## Slice 2 spike: the tokens against a real SwiftUI window

`build/source/music-spike.swift`, compiled with `swiftc` and run as a plain
binary (not `swift file.swift`, which JITs and cannot resolve SwiftUI symbols).
Standalone on purpose: Spinner carries no App Kit Swift tokens, and coupling two
repos for a throwaway is worse than hardcoding eleven measured values.

**The tokens render correctly.** Sampled from a capture of the spike window,
sRGB, against the Music measurements:

| | spike | Music | |
|---|---|---|---|
| `ground-window` | `#1F1F20` | `#1F1F20` | exact |
| `music-select` | `#CC132D` | `#CC132D` | exact |
| `music-hover` | `#2C2C2D` | `#2C2C2D` | exact |
| sidebar | `#262627` | `#262629` | within 2 units |

### The sidebar needs no token

Stock `List { }.listStyle(.sidebar)` in a `NavigationSplitView`, with **no
background set**, lands within 2 units of Music's measured sidebar. So Music's
sidebar is the standard SwiftUI material and nothing else. The variant should
set no background there; doing so would defeat the vibrancy that makes it match.

This is the thing a CSS preview could not have told us, and it is why this slice
exists.

### Two SwiftUI behaviours the preview would have hidden

1. **Sidebar selection uses the system accent, not your colour.** The spike's
   selected row renders system blue despite every label being tinted
   `music-accent`. `List(selection:)` with `.listStyle(.sidebar)` draws its own
   selection. Matching Music's red needs an explicit override, which slice 3
   must budget for.
2. **`.foregroundStyle` on a `Label` tints the symbol AND the text.** Music
   tints only the symbol and leaves the label in normal ink. Fixed in the spike
   by building the Label from explicit `Text`/`Image` closures and tinting only
   the `Image`; that renders correctly and matches Music.

### A third thing the spike gives for free

**The inactive selection is automatic.** With the spike window not key, its
sidebar selection renders grey rather than any accent, exactly as Music does.
That behaviour needs no code: SwiftUI already does it. Given Spinner is a
monitor app whose window is usually unfocused, this is the state its users will
mostly see, and it is free.

Still open: whether `.tint(_:)` on the List reaches the **active** selection
fill. The spike applies it, but the window was never key during capture, so only
the inactive grey was observed. Settling it needs the spike window frontmost.

## Contrast audit

A WCAG relative-luminance function was written for slice 2's build assertion and
first run against **App Kit's existing claims**, which are hand-written usage
strings nothing verifies. All 14 checkable pairs pass, several comfortably
(`ink on ground` claims 13:1 and measures 15.08 light / 19.29 dark). The honour
system held.

The function is proved rather than assumed, because one that passes everything on
its first run is indistinguishable from one that cannot fail:

| case | computed | expected |
|---|---|---|
| white on black | 21.00 | 21.00, the maximum |
| a colour on itself | 1.00 | 1.00, the minimum |
| white on the HeroCard yellow `#F4B63F` | 1.81 | 1.81, matching the plan's independent figure |
| `#777777` on white | 4.48 | fails the 4.5 gate |
| `#767676` on white | 4.54 | passes the 4.5 gate |

### It immediately found a real conflict

**The measured Music accent fails WCAG AA on its own ground.**
`#FA2E48` on `#1F1F20` is **4.35:1**, short of 4.5 for normal text.

So fidelity and accessibility genuinely disagree here, and the variant cannot
have both from one token. The resolution is the split App Kit already uses for
`accent` / `accent-ink`:

| Token | Dark | Light | Use |
|---|---|---|---|
| `music-accent` | `#FA2E48` | `#FA233B` | icons, symbols, CTA fills. Matches Music exactly |
| `music-accent-ink` | **`#FA3851`** (4.51:1) | **`#EA0623`** (4.62:1) | accent **text**, where 4.5 must hold |

Both ink values keep the measured hue (H=352) and saturation and move lightness
only as far as the gate requires: `L 0.58 -> 0.60` on dark, `0.58 -> 0.47` on
light. The difference is small enough not to read as a different red, which is
the point.

### A second failure: secondary text in light mode

`music-ink-soft` measured `#808080`, which on the light ground `#FFFFFF` is
**3.95:1**. Secondary text is exactly where small type lives, so this matters
more than the accent case.

| | measured | compliant | ratio |
|---|---|---|---|
| `music-ink-soft` dark | `#9A9A9A` | unchanged | 5.85 |
| `music-ink-soft` light | `#808080` (3.95) | **`#767676`** | 4.54 |

`#767676` is the first grey that clears 4.5 on white, and is the same boundary
value used as a test case for the contrast function itself.

### The two deliberate departures, together

Music's own palette fails WCAG AA in two places. The variant keeps the measured
value wherever it is not text, and ships a corrected value where it is:

| Role | Measured (Music) | Shipped | Why |
|---|---|---|---|
| accent on icons, symbols, CTA fills | `#FA2E48` / `#FA233B` | same | not text, fidelity wins |
| accent as **text** | 4.35 dark, 3.91 light | `#FA3851` / `#EA0623` | 4.51 / 4.62 |
| secondary **text** | `#808080` light, 3.95 | `#767676` light | 4.54 |

Both corrections move lightness only as far as the gate requires and keep hue
and saturation, so neither reads as a different colour.

Music itself does neither, so these are the only two places the variant
deliberately departs from the reference. Both must be stated in the README or
someone will "restore" the measured values and reintroduce the failures.

## Geometry

**Use `ax-dump.swift`. It reads exact frames in points straight from the app.**

```
swift build/source/ax-dump.swift Music [maxDepth]
```

This supersedes pixel measurement for geometry, and it means Accessibility
Inspector is not needed either. Getting there took three wrong turns worth
recording, because the obvious routes all fail on Music specifically:

- `System Events` reports Music as having **0 windows**. Finder and Safari
  report 1, so the permission is fine and the failure is Music-specific.
- The raw AX API agrees: `AXWindows` returns success with an **empty** array for
  Music and one window for Safari.
- But `AXMainWindow` works. **Enter through `AXMainWindow`, not `AXWindows`.**

Music's own AppleScript dictionary also answers (`bounds of front window` gives
`106, 59, 1694, 1066`), but only for the window, not its contents.

### Window chrome and containers (AX, exact)

| Element | Frame, window-relative |
|---|---|
| window | 1588 x 1007pt |
| toolbar | y=0, h=**52pt**, full width |
| sidebar scroll area | x=0, y=52, w=269.5 **(user-resizable, not a spec)** |
| content scroll area | x=270, y=52, w=1318 **(follows the sidebar)** |
| MiniPlayer group | x=579, y=934, **w=700, h=54** |
| profile button | x=18, y=961, 123 x 28 |
| Go Back / Share / More / Sort | 40x52, 36x52, 36x52, 42x52 |
| search field | x=1359, y=7, 221.5 x 38 |

### SidebarList (AX, exact)

| | |
|---|---|
| row height | **32.0pt** (rows at y=52, 84, 116, 148 …) |
| section header row | **19.0pt** |
| row width | 270.0pt |

Cross-check: pixel measurement gave 32.2pt for the row, so that method was sound.

**The sidebar width is user-resizable and is not a design value at all.** Pixels
gave 200pt and AX gives 269.5pt; I first wrote that down as the pixel method
being wrong about a colour boundary. That conclusion was overconfident. The two
readings come from different moments of a draggable control, so they need not
agree and neither is "the" width. `AXSplitter` confirms it: `AXOrientation =
AXVerticalOrientation`, `AXValue = 269.5`.

AX does **not** expose the real limits. `AXMinValue 0 / AXMaxValue 1586.5` is
just the window range, not AppKit's enforced minimum, which lives in a delegate
and would need dragging to find. Dragging is control, which is blocked for Music.

A second splitter (`AXValue = 1317.5`) sits between the content area and the
queue panel, so **the queue panel is resizable too**. Neither width belongs in
`tokens.json`; both belong in the component as a default plus a min.

The MiniPlayer is the reverse check: AX says 700 x 54pt, pixel measurement said
700 x ~52pt. Agreement there is what validates the pixel numbers below.

### TrackList (AX, exact)

Row height **56.0pt**, width 1318pt, confirming the 56.0pt measured from pixels.

Columns, window-relative x (the content area begins at x=270):

| Column | x | width |
|---|---|---|
| favorited star | 270.0 | 40.0 |
| artwork | 310.0 | 57.0 |
| Song | 367.0 | 593.5 |
| Artist | 960.5 | 468.5 |
| cloud / download | 1429.0 | 16.0 |
| Time | 1445.0 | 58.0 |
| "…" menu | 1503.0 | 85.0 |

**The column set is not fixed.** This playlist has seven columns and no Album;
an earlier capture had one. So TrackList takes its columns as configuration, and
the pixel-derived column positions recorded earlier describe a *different*
column set, not a contradiction.

### Detail page button row (AX, exact)

| Element | Frame |
|---|---|
| Shuffle | x=611, y=285, **38 x 38pt** |
| Play | x=655, y=285, **132 x 38pt** |
| "+" | x=793, y=285, **38 x 38pt** |
| gap between them | **6pt** on each side of Play |
| artist link | x=611, y=134, 502 x 33pt |
| column header row | 32pt tall (Song x=318 w=454.5, Artist x=772.5 w=292.5, Album x=1065 w=364.5) |

All three buttons share a 38pt height and sit on one baseline; the two circular
ones are exactly square. Play is the only one with a width of its own.

### Cards are drag sources

Dragging a hero card does not pan the shelf, it begins a drag of the **music
item** itself. Worth knowing before building the shelf: the card needs to be a
drag source, and any press-and-move gesture intended for scrolling will fight
it. This surfaced while trying to zoom into a card edge, which turned out to be
impossible by dragging for exactly this reason.

### Detail page header (AX, exact)

| Element | Frame |
|---|---|
| title | x=611, y=87, 502 x 33 |
| "Updated N days ago" | x=611, y=155, 119.5 x 17 |
| description | x=611, y=206, 502 x 54 |
| header group | x=310, y=52, 1238 x 270 |

### Measured off captures by edge detection

Still the right tool for anything AX does not expose as its own element, such as
the gap *between* cards. Source: `playlist-tracklist-unfocused-light.png`.

### TrackList

| Dimension | Measured | How |
|---|---|---|
| row pitch | **56.0pt** | five consecutive separator hairlines, all exactly 56.0pt apart |
| artwork thumbnail | **40 x 40pt** | ink run x 247.0-286.5pt, ink column y 680.0-719.5pt |
| thumbnail padding | 8pt top and bottom | (56 - 40) / 2 |
| favorited star | ~11pt wide, x 221.5-232.0pt | ink run |
| title text starts | x ~309pt | first glyph ink after the thumbnail |
| columns | Artist ~737pt, Album ~1050pt, Time right-aligned ~1465pt | header and cell ink runs |

The header area above the rows is not on the 56pt grid: the gaps there measure
68.5, 16.2, 15.5 and 67.8pt, so the description block has its own spacing.

### Shelf and cards (AX, exact)

Home, window 1588x1007pt, content area 1318pt wide.

Shelves tile with **no vertical gap** between them, each group's height
including its header:

| Shelf | y | height |
|---|---|---|
| Top Picks for You (hero) | 98 | **400pt** |
| Recently Played / Pop / Stations (artwork) | 498 / 780 / 1760 | **282pt** |
| The Sampled Series (carries a subtitle) | 1062 | 298pt |
| Playlists Made for You (hero) | 1360 | **400pt** |

The scrollable row inside each: hero `x=304 y=145 w=2476 h=343`, artwork
`x=304 y=545 w=2476 h=225`. The 2476pt width is the horizontal scroll extent
against a 1318pt viewport.

| Card | Size (at one sidebar width) | Pitch | Gap |
|---|---|---|---|
| **HeroCard** | 257.5 x 343pt | 277.5pt | **20pt** |
| **ArtworkCard** | 188 x 225pt | 208pt | **20pt** |

These sizes are a snapshot at one sidebar width, not constants. See below.

**The gap is constant; the card size is not, and the mechanism is now known.**

Three measurements of the *same* 1588pt window disagree on card size and agree
on the gap:

| Run | content left edge | ArtworkCard | pitch | gap |
|---|---|---|---|---|
| AX, sidebar wide | 304pt | 188 x 225 | 208.0 | 20 |
| AX, sidebar narrow | **242pt** | **198.5 x 235.3** | 218.3 | ~20 |
| pixel scan | - | ~200 x 200 | 219.5 | 20 |

The left edge moves because **the sidebar is user-resizable**. A narrower
sidebar gives a wider content area, and the cards grow to fill it while the gap
stays at 20pt. Both AX runs fit about 6.17 columns, so the column count holds
and the card width absorbs the difference.

HeroCard behaves identically: 257.5 x 343pt at the wide sidebar, 271.0 x 362.5pt
at the narrow one, pitch 277.5 then 291.0, gap 20pt throughout.

**Correction: the gap is not constant either.** A third run, with Music on a
virtual display at a 980pt window, gives a **16pt** gap in both shelves. So
"the 20pt gap holds across every measurement" was true only of the two wide
runs, and is wrong.

| Run | content width | hero gap | artwork gap | hero w/h | artwork caption |
|---|---|---|---|---|---|
| 1588pt window, sidebar 270 | 1318 | 20.0 | 20.0 | 0.751 | 37.0 |
| 1588pt window, sidebar 242 | 1346 | 20.0 | 19.8 | 0.748 | 36.8 |
| **980pt window, sidebar 208** | **772** | **16.0** | **16.0** | 0.748 | 37.0 |

The gap looks like a breakpoint rather than a scale: 20pt at ~1300pt of content,
16pt at 772. Where it switches is unknown, and three points cannot locate it.

### HeroCard caption geometry (pixel, light)

Source `window-home-unfocused-light.png`, converted to sRGB, card 1 isolated by
scanning for the near-white gutters at a mid-card row: gutters at x 1015-1052,
1602-1639 and 2188-2223 @2x give a 587px pitch and a 550px card, so 275.5 x
367.0pt and a ratio of 0.751, agreeing with the AX figure.

Text bands inside that card, offsets from the card's own edges:

| | |
|---|---|
| left inset, both lines | **18.5pt** |
| title band | y 335.0-344.5pt, so **22.5pt** up from the card bottom, cap height ~10pt |
| eyebrow band | y 320.0-327.5pt, **7.5pt** above the title, cap height ~8pt |
| badge | top-right, Apple Music wordmark |

The title was found at a >240 white threshold; the eyebrow needed a lower one,
which is itself the observation that **the eyebrow is translucent white and the
title is not**. Both sample over orange artwork, so neither is a colour source:
the alpha is inferred from the threshold that finds them, not measured.

**The scrim is not Music's.** Music has none here; the artwork is commissioned
to carry the text. White on the measured `#F4B63F` is 1.81:1.

### What IS invariant, which is the useful part

Three widths spanning 772 to 1346pt agree on two things, and they are a better
component spec than any pixel size:

- **HeroCard is 3:4.** Width over height is 0.751, 0.748, 0.748.
- **ArtworkCard is a square artwork plus a caption block of constant height.**
  Card height minus card width is 37.0, 36.8, 37.0pt at every width. The
  artwork is square and the caption does not scale.

So `ArtworkCard` takes a width and derives `width + 37pt`; `HeroCard` takes a
width and derives `width / 0.75`. Neither needs a hard-coded size, and that is
what makes the component correct at any sidebar position rather than only at
mine.

Consequence for the component: **do not ship a fixed card size.** Ship the 20pt
gap and let the card size derive, which is also what the earlier finding implied
when the two shelves shared a gap and a left edge but not a card shape.

### Earlier pixel measurements of the same thing

Superseded by the AX figures above, kept because the method is still right for
anything AX does not expose as an element. Source:
`window-home-unfocused-light.png`. Content bands were located by a vertical
non-white fraction sweep first, then measured horizontally. Card runs fragment on
artwork detail, so **widths were derived from gap positions**, which are exact.

| Dimension | Measured | How |
|---|---|---|
| **shelf gap** | **20.0pt** | repeats exactly: 5 times in the hero row, 7 in the artwork row, and confirmed by a 1px line profile with hard edges on both sides |
| **ArtworkCard** | **200 x 200pt, square** | pitch 219.5-220.0pt across 5 consecutive gaps, minus the 20pt gap. Height confirmed independently by the band sweep, y 570-770pt |
| **HeroCard** | **273 x 395pt** | pitch 293.0pt across 3 consecutive gaps, minus the gap. Height from the band sweep, y 145-540pt, caption included inside the card |
| content left edge | x = 310pt | first card's left edge in both rows |
| artwork caption block | y 780-800pt | title and subtitle under each card, outside the card |

The two shelves share one gap value and one left edge but differ in card shape,
so a Shelf component should take the card as a slot rather than owning its size.

### SidebarList

| Dimension | Measured | How |
|---|---|---|
| **row pitch** | **32.2pt** | median of 19 of 23 consecutive label-row pitches, clustered 30.5-33.2 |
| **sidebar width** | **200pt** | ground `#EDEDEE` runs x 0-200pt, then white content |
| section break | ~63pt, about 2x the row pitch | the two outliers among those pitches, at Library-to-Store and Store-to-Playlists |

So a section header occupies roughly one extra row slot rather than a bespoke
margin, which is worth copying.

### Buttons: the accent IS a fill, for one kind of button

An earlier note here claimed Music never fills a button with its accent. **That
was wrong**, generalised from the Play button alone. Both kinds exist:

| Kind | Example | Fill | Label |
|---|---|---|---|
| transport / primary | Play on an album or playlist | neutral, inverts with appearance (`#0E0E0E` light, `#F3F3F3` dark) | opposite neutral |
| CTA / promotional | "Set Location" in the Concerts card | **the accent, `#FA233B` light** | white |

So the variant needs `music-accent-fill` after all, and the real rule is about
*which* button: the thing you press to play is neutral, the thing that sells you
something is accent. Getting that backwards gives you a red Play button, which
is the original failure this was guarding against.

### MiniPlayer

| Dimension | Measured | How |
|---|---|---|
| **width** | **700pt** | four scans across two appearances: 698, 700.0, 701.0, 701.5pt |
| **height** | **~52pt** | 51.0pt by fill-colour match (excludes the antialiased edge), 54.0pt by band edge (includes it) |
| **corner radius** | **height / 2, a full stadium** | left-edge inset falls 17.5 -> 0pt over 24pt against a 51pt height |
| fill, Reduce Transparency **on**, dark | `#3B3B3D` | 701pt run, cleanly separated from the `#1C1C1E` Concerts card beneath it |

### Correction: the progress line spans the now-playing group, not the capsule

Recorded earlier from a pasted screenshot as "a hairline progress bar along its
own lower edge", which implies the full 700pt. Measured from
`home-reduced-transparency-dark.png`, the line runs **x 165-555pt** inside the
capsule: it begins at the artwork's left edge and ends with the text group, and
sits 1pt tall, 2pt above the inner bottom edge.

So it belongs to the now-playing group, not to the capsule. A pasted screenshot
is good for layout and role and this is exactly where it was not good enough.

### MiniPlayer contents (pixel, Reduce Transparency dark)

Column-occupancy scan of the capsule interior, offsets from the capsule's own
left edge:

| Element | x |
|---|---|
| shuffle | 15.5-28.5 |
| previous | 39.5-60.0 |
| play / pause | 74.5-89.5 |
| next | 104.0-124.5 |
| repeat | 136.0-148.0 |
| artwork | **165.0-199.0, 34pt square** |
| title / subtitle | from 207.5 |
| trailing icon cluster | 506-680 |

Left inset 15.5pt, right inset 20pt.

**Reduce Transparency is the tool that made this measurable**, and it beats every
other approach tried. Three failed first:

1. Over album artwork the capsule is translucent, so it has no stable edge.
2. Over flat **white** ground it is nearly white, so there is almost no contrast.
   Scrolling it onto flat ground made it *harder*, not easier.
3. A translucency-lift comparison fails too, because the lift changes with
   whatever is behind it.

With Reduce Transparency on, the capsule is opaque and its edge is a clean step.
Turning it on is also what the plan's capture rules already ask for, to record
each glass surface twice; it turns out to be the only practical way to measure
any glass element's geometry at all.

One trap inside that: the capsule floats over the Concerts card, so a naive
non-ground scan returns the **card's** 1231pt width. The two had to be separated
by fill colour, `#3B3B3D` capsule against `#1C1C1E` card.

### Superseded, kept so it is not re-derived

The capsule is translucent and floats over album artwork, so it has no stable
edge: a threshold finds nothing (it is not pale, it is mid-grey over dark art)
and a translucency-lift comparison finds nothing either, because the lift
changes with whatever is behind it.

**It becomes measurable in one shot:** scroll the page so the capsule sits over
flat ground rather than artwork, then capture. Its edges are then a simple step
against a known colour. Until then its width, height and corner radius are
unknown, and the ~690 x 60pt suggested by eye on a crop is an estimate, not a
measurement, and must not be used.

## Slice 6's spike gate, 2026-10-01

`music-spike.swift` now carries the MiniPlayer capsule, which is what the plan
asks for: the CSS preview answers geometry and nothing else, because `glass`
there is a `backdrop-filter` sampling the page while a real capsule samples what
is behind it in a window. Captured at `spike-miniplayer-key-dark.png`.

**It passes.** 700 x 54 at a stadium radius over `.regularMaterial`, 19pt up,
centred on the content column, reads as Music's capsule against scrolled
content. Transport left, now-playing centre, actions right, and the progress
hairline on the capsule's own bottom edge below the text.

One spike-only bug on the way, worth the note because it is the same mistake the
CSS avoids by accident: letting the text set the stack height put the line
*through* the subtitle. The line belongs to the capsule's bottom edge, so the
group has to be the full 54 tall with the text centred inside it.

## `.tint` does NOT reach the sidebar selection -- ANSWERED

Open since slice 2 and tagged for a human, because four earlier self-capture
attempts all reported `isKeyWindow=false`.

Measured on a **key, active** window (`isKeyWindow=true isActive=true`), with
`.tint(Color.musicSelect)` on the `List`: the selected "Home" row fills
**`#434346`**, sampled identically at two x positions. That is a neutral grey. It
is not `music-select` `#CC132D` and not a red of any kind.

So `.tint` is not the lever for a sidebar selection fill, and a SwiftUI
`SidebarList` cannot get Music's red selection from `.listStyle(.sidebar)` plus a
tint. It needs a custom row background, which is what the CSS component already
does.

### Retraction: "macOS denies focus to a shell-launched binary"

Written down after four failed attempts. **Too strong.** Five attempts today
returned `isKeyWindow=true` four times and `false` once. Focus for a
shell-launched binary is *unreliable*, not denied, and the earlier run simply
hit the unlucky side of it four times.

The capture tool was right to report the focus state alongside every shot --
that is the only reason this could be distinguished at all. The wrong move was
reading four failures as a rule.

## MiniPlayer ink is WHITE, not music-ink -- 2026-10-01

Capture `home-miniplayer-inactive-dark.png`, Home, dark, window **inactive**,
a track playing.

| Element | Reads | Note |
|---|---|---|
| play/pause, previous, next | **`#FFFFFF`** | 817 and 516 solid px, not antialiasing |
| queue icon | `#FFFFFF` | |
| shuffle, OFF | ~`#7E7E80` | an off toggle is dimmed, not hidden |
| repeat, OFF | ~`#6B6E6F` | |

**Two things follow, and the first is a defect in what shipped.**

`music-ink` dark is `#DDDDDD`, and both the CSS and SwiftUI MiniPlayer use it
for the transport glyphs and the title. Music uses pure white. That is not a
rounding difference: the capsule is a glass surface, not the window ground, and
a token named for ink *on the ground* was the wrong one to reach for. The
component needs its own on-glass value rather than borrowing `music-ink`.

**The glyphs do NOT dim when the window goes inactive.** Worth recording because
the opposite is true elsewhere in this app -- the album Play button inverts and
the sidebar loses its red entirely -- so "inactive dims everything" would have
been a reasonable and wrong generalisation.

### Re-measured with Reduce Transparency, same session

`home-miniplayer-reduced-dark.png`. The capsule is opaque here, so these are
readings rather than upper bounds.

| Element | Measured |
|---|---|
| play/pause, previous, next, queue | **`#FFFFFF`** |
| title | **`#FFFFFF`** (1175 px) |
| **artist** | **`#FFFFFF`** (999 px) -- *not* a softer grey |
| shuffle OFF | `#4F4F4F` |
| repeat OFF | `#4E4F50` |
| capsule fill | ~~`#151515`~~ -- WITHDRAWN, this capture was translucent; the fill is **`#3A3A3D`**, see RESOLVED below |
| width | **701.0pt**, independently confirming the recorded 700 |

So `on-music-glass` is `#FFFFFF` dark, and the artist line shares it. The
component had the title on `ink` and the artist on `ink-soft`, both CORE tokens
on a Music surface, which is the root error: a ground ink on a glass surface.
Light is not measured and inherits `music-ink`'s light value, so the departure
is dark-only.

**Music's own OFF toggle fails 3:1.** `#4F4F4F` on the capsule is **1.38:1**, under
the bar for a graphical object. Recorded, not copied -- the same fidelity-
versus-accessibility split already made for `music-accent` / `music-accent-ink`.

### RESOLVED: only one of the two was actually opaque

Both captures were measured the same way and both looked constant, so the
disagreement read as a contradiction in the method. It was not.

| Capture | fill | backing | bleed-through |
|---|---|---|---|
| `home-reduced-transparency-dark` | **`#3A3A3D`** | `#1C1C1E` | none, crisp edge |
| `home-miniplayer-translucent-dark` | `#151516` | `#1E1E20` | **page text visible through it** |

The backings are two units apart, so a translucent capsule could not read
`#3A3A3D` over one and `#151516` over the other. Looking at the crops settles
it: the second shows "Apple Music Hip-Hop" and "Travis Scott" **through** the
capsule's lower band. It was never opaque.

**`#3A3A3D` is the capsule fill.** `#151515` is withdrawn, and the file that
produced it is renamed `home-miniplayer-translucent-dark.png` so the name says
what it is.

#### The trap: the setting was on and the effect was not

`defaults read com.apple.universalaccess reduceTransparency` returned `1` when
that capture was taken, and it was still translucent -- Music had not
re-rendered the material. Reading the setting is not observing the effect.

**Test the effect, not the switch.** An opaque capsule has no content visible
through it and holds one fill across backings that differ. A single row sampled
over uniform dark content looks constant either way, which is exactly how this
one passed.

#### Figures corrected

Measured against `#151515` and restated against `#3A3A3D`:

| | against `#151515` | against **`#3A3A3D`** |
|---|---|---|
| white ink | 18.26:1 | **11.34:1** |
| OFF toggle `#4F4F4F` | 2.23:1 | **1.38:1** |

`on-music-glass` is unaffected as a value -- white is still the measured ink and
still clears every bar. The OFF toggle misses 3:1 either way, by more than
recorded.

## Transport button, window INACTIVE -- 2026-10-01

`album-transport-inactive-dark.png`, an album page, dark, `Music active=false`
asserted before the shutter rather than assumed from the filename.

| | Active (recorded earlier) | Inactive (measured here) |
|---|---|---|
| pill fill | `#F3F3F3` | **`#2F2F30`** |
| label | `#0E0E0E` | **`#DFDFDF`** |

**It inverts; it does not dim.** Light pill with a dark label becomes a dark
pill with a light one. Shipped as `music-primary-inactive`, with the label left
on `music-ink` -- `#DFDFDF` against `music-ink`'s `#DDDDDD` is two units, a
near-match not worth a second token.

**The inactive button is 1.23:1 against the page.** Its own boundary is very
nearly invisible. The window being inactive does not disable it -- clicking
activates the window and plays -- so this is an enabled control with no
perceivable edge, which is Music's behaviour and is recorded rather than
enforced. The pill-vs-ground pair is deliberately NOT in the contrast gate; the
label-on-pill pair is, at 4.5.

### Two captures mislabelled in one session

Both were named before anything verified them, and both were wrong.

- One was named `album-transport-inactive-dark` while `Music active=true`. The
  helper now reports activity, so this was caught at the shutter.
- The other was named the same and turned out to be **Home, in light mode,
  active** -- wrong on all three counts. Renamed `home-light-active.png`, which
  is a state the set did not otherwise have.

This is the same failure the hero-gutter retraction records. The rule earned
there held again: **a filename is not an observation.**

## The light pass -- all three settled, 2026-10-01

`album-light-inactive.png`: the Favorite Songs playlist, light, window
inactive, stars in every row. One capture closed all three derivations, and
**every derived value was wrong.**

| Token | Was derived | **Measured** | |
|---|---|---|---|
| `music-star` light | `#B8860B` | **`#FFCC00`** | system yellow, not a dark gold |
| `music-primary-inactive` light | `#DCDCDD` | **`#ECECEC`** | |
| `on-music-glass` light | `#272727` | **`#000000`** | |

Each derivation was reasoned and each was off. The star is the worst: it was
stepped to `#B8860B` *specifically* to clear 3:1, and Music uses a value at
**1.51:1**. Deriving a light value from a dark measurement plus a contrast
floor produced a colour Apple would not recognise.

**`on-music-glass` is pure black and pure white.** `#000000` on a `#FFFFFF`
capsule in light, `#FFFFFF` on `#3A3A3D` in dark. Symmetric, and in neither
appearance is it the ground ink -- which is the whole reason the token exists.

### The star now fails the gate, deliberately

`#FFCC00` on white is 1.51:1, under the 3:1 a graphical object needs. The pair
moved from `CONTRAST_PAIRS` into `CONTRAST_UNCHECKED` with its reason, which is
the same call already made for `music-accent`: the variant records Music's own
mark rather than correcting it. An app that must meet 1.4.11 here should darken
it. Music does not.

## Not measured, and why

- ~~The accent.~~ **Measured, see the table above.** Taken from large-title stroke
  interiors rather than a favorited star, because the favorited star turned out
  to be **gold, not accent red** (`album-detail-unfocused-dark.png`, track row 1).
  The web player's `#D60017` is superseded and must not be used.
- ~~The star's gold.~~ **Measured 2026-10-01, dark only.** The same capture, star
  glyph at (450, 729) in the full-res image: the solid interior reads
  **`#FFD700`**, with `#FFD500` through `#FFD702` across the antialiased body.
  That is literal gold, and 11.74:1 on `ground-window` dark.
  **Light is still unmeasured.** The three light album captures do not contain
  the star at a locatable position, and the dark value cannot simply carry over:
  `#FFD700` is **1.40:1** on white, far under the 3:1 a graphical object needs.
  So `music-star` light is `#B8860B`, the first gold that clears 3:1 (3.25:1),
  and it is a derivation, not a reading. Re-measure it from a light album page
  with a favorited track when one is captured.
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

## 2026-10-01: the progress line, and five components wearing the wrong ink

Both found by reading the components against the tokens rather than against a new
capture. No capture was taken for either; the progress line was measured off a
file already on disk.

### The progress line: 2pt, and two greys

Instrument: `home-reduced-transparency-dark.png`, the opaque-capsule capture,
converted to sRGB with `sips -m` before sampling (the greys move by less than a
unit under the conversion, checked both ways rather than assumed).

| | Measured | Instrument |
|---|---|---|
| height | **2pt** (4 device px at @2x, rows 1963-1966) | hard step above and below; row 1960 and row 1967 are both plain capsule |
| played | **`#D4D5D7`** | 760 px, x 1421-2180, every pixel identical |
| unplayed | **`#6E6F71`** | 50 px, x 2181-2230, every pixel identical |
| span | x 1421-2230 device = **405pt**, played **380pt** of it | the step between the two runs |
| capsule there | `#3B3B3D` | matches the value the MiniPlayer README already recorded |

Over that capsule the two greys are white at 0.781/0.786/0.794 and
0.260/0.265/0.268 per channel, so they ship as `on-music-glass` at 79% and 26%.
At those alphas the composite is within 2/255 of both measurements, and it
inverts correctly in light, where nothing was measured.

The span disagrees with the README's earlier x 165-555pt (390pt) by about 15pt.
Not reconciled: different capture, and the colours do not depend on it.

**Read the colours off the centre row, not the edge rows.** y=1963 and y=1966 give
`#D5D5D7` / `#D5D5D8`, a unit off, because the line's own top and bottom rows are
partially covered. Only y=1964 and y=1965 give the value exactly. The first pass
through this reported "740 of 740" and "44 of 44" identical, which were the widths
of the sample windows used rather than the runs -- a count of what was looked at,
read back as a measurement of the thing. The runs are 760 and 50.

Superseded: played was `ink-soft` (`#9A9A9A`), the track was
`music-select-inactive`, and the height was 1pt.

### Five components inherited the core ink

`music-ink`'s own usage string says **"do not inherit ink here."** Four of the six
Music components did anyway, in eight declarations:

| Component | Was | Now |
|---|---|---|
| `Shelf` title, see-all, see-all hover | `ink` / `ink-soft` / `ink` | `music-ink` / `music-ink-soft` / `music-ink` |
| `ArtworkCard` title, subtitle | `ink` / `ink-soft` | `music-ink` / `music-ink-soft` |
| `SidebarList` section label, row label | `ink-soft` / `ink` | `music-ink-soft` / `music-ink` |
| `MiniPlayer` progress fill | `ink-soft` | `on-music-glass` at 79% |

The visible one is dark: core `ink` is `#F5F5F7` and `music-ink` is `#DDDDDD`, so
a shelf caption was 24 units brighter than the track list beside it on the same
ground. Verified after the change in headless Chromium: `#272727` / `#767676` in
light and `#DDDDDD` / `#9A9A9A` in dark, read off the computed style with the
loaded rule checked to be the new one rather than a cached sheet.

### Still wearing a core token, deliberately not changed

- `.dc-sidebar-avatar` fills with `accent-wash`, a **blue** wash, in a Music
  sidebar. There is no `music-accent-wash`, and inventing one needs a measurement
  of what Music actually puts there.
- The four artwork placeholders (`artcard`, `herocard`, `tracklist`, `miniplayer`)
  use `surface-sunk`. It shows only while an image loads and was never measured.

Both are recorded rather than guessed at.

### The star and the Play button: tokens measured, then never painted

Also found by reading tokens against usage rather than by a capture. Four
`music-*` tokens had no CSS rule referencing them at all:

| Token | Why nothing painted it |
|---|---|
| `music-star` | the MiniPlayer put the glyph inside its title span, where it inherited `on-music-glass`, so the favorited star rendered **white** instead of gold |
| `music-primary`, `on-music-primary`, `music-primary-inactive` | no component drew Music's transport button; an adopting app had to wire the Play pill by hand |

The SwiftUI mirror used both (`Color.Kit.musicStar` in the TrackList recipe,
`musicPrimary` in the spike), so the two renderings of one design system
disagreed and nothing noticed. The contrast gate already carried both pairs --
`on-music-primary` on `music-primary` and `music-ink` on
`music-primary-inactive` -- so it had been proving claims about colours no
component rendered.

Now: `Button` takes `variant="music"`, and `data-window-inactive="true"` inverts
it rather than dimming. Verified in headless Chromium, each appearance read in
its own call (see the `CLAUDE.md` trap about reading a theme switch too soon):

| | fill | label |
|---|---|---|
| light, key | `#0E0E0E` | `#FFFFFF` |
| light, not key | `#ECECEC` | `#272727` |
| dark, key | `#F3F3F3` | `#0E0E0E` |
| dark, not key | `#2F2F30` | `#DDDDDD` |

All four are the measured token values, and the four ratios are 19.30, 12.65,
17.40 and 9.85:1. The star reads `#FFCC00` in light against a `#000000` title,
and carries `role="img"` with `aria-label="Favorited"` so a screen reader says
"Favorited" rather than "black star".

### The shelf group was 17pt too tall, and the gap was counted twice

Compared the Shelf preview against the AX record above rather than against a new
capture. Card geometry was already exact; the group height was not.

| | Music (AX, plain artwork shelf) | preview, before | after |
|---|---|---|---|
| group height incl. header | **282pt** | 299.2 | **283.2** |
| header | implied 57 | 58.2 | 58.2 |
| track | 225 | 229 | 225 |
| card | 188 x 225 | 188 x 225 | 188 x 225 |
| gap / pitch | 20 / 208 | 20 / 208 | 20 / 208 |

The excess was 12px of `gap` on `.dc-shelf` plus 4px of `padding-bottom` on the
track, with the last 1.2 down to type metrics. The header was never the problem:
at 58.2 against Music's implied 57 it already carried 16.6px of whitespace under
the title, so the flex gap was counting the same space a second time. Removing it
leaves exactly that 16.6px between title and cards.

The track's `padding-bottom` was vestigial -- `scrollbar-width: none` and the
`::-webkit-scrollbar` rule already hide the bar.

Checked that nothing the padding might have been protecting broke, at a 900px
viewport where the track actually overflows: it still scrolls, `scrollLeft = 208`
lands on 208 so the pitch is intact, `scroll-snap-type` is still `x mandatory`,
no card is clipped, and `offsetHeight == clientHeight` so no scrollbar appeared.
