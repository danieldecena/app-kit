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

So **no card dimension in this file is a constant**. The only transferable
numbers are the 20pt gap and the aspect ratios (ArtworkCard about 1:1.19,
HeroCard about 1:1.34). A component that hard-codes 188x225 will be wrong for
every user whose sidebar is not where mine was.

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

## Not measured, and why

- ~~The accent.~~ **Measured, see the table above.** Taken from large-title stroke
  interiors rather than a favorited star, because the favorited star turned out
  to be **gold, not accent red** (`album-detail-unfocused-dark.png`, track row 1).
  The web player's `#D60017` is superseded and must not be used.
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
