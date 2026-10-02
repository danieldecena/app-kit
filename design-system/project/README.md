SwiftUI on Apple's own neutrals and system colours: capsule buttons tinted like Notes highlights, Rounded figures, glass for controls that float over content. The native half of three kits: **App Kit** (Mac, iPhone, iPad and Watch apps: WA Fish Map, Footage Library, Claude Spinner), **Artifact Kit** (web pages and artifacts, same palette) and **Terminal Kit** (the macOS Terminal look). Source: `~/developer/app-kit`.

## Principles

- **Defer to the system.** Use the system controls, colours and text styles first; these tokens describe what they already do, for places you draw yourself.
- **The accent is for acting.** `accent` (the app's accent, the person's on the Mac) marks what you can act on and what is selected. Status, charts and highlights never borrow it.
- **Translucent, not heavy.** Tints are washes (12%, 20% in dark), selection is a wash, and only one filled button per view.
- **Glass floats, content doesn't.** Liquid Glass is for toolbars, tab bars and controls over content. Lists, charts and reading text stay on opaque `surface`.
- **A scale is not a status.** `heat-1` to `heat-4` rank data. `bad` means something failed.

## Content

- Sentence case everywhere: "Import clips", not "Import Clips". Uppercase only in the mono `label` and `eyebrow` styles and in panel titles.
- Verb first on buttons ("Retry sync", "Add filter"). A control says what happens; the toast after it says what happened ("Synced 42 clips").
- Real units, always: "2,400 fish", "4.2 GB", "6 min ago". Numbers use tabular figures (`font-variant-numeric: tabular-nums`, `.monospacedDigit()` in SwiftUI).
- No emoji. Status carries a word or glyph as well as a color.

## Color

- Neutrals are Apple's: `ground` is the grouped background (#F2F2F7, black in dark), `surface` the grouped cell (white, #1C1C1E), `surface-sunk` systemGray5. `ink` and `ink-soft` pass 4.5:1 on all three in both themes.
- `ink-faint` (tertiaryLabel) is for absences and chrome: "not recorded", panel titles, the empty-slot outline. It sits under 3:1, so it never carries the only copy of a reading.
- Control borders use `edge` (3:1). `hair` is decoration only and never the sole outline of a control.
- Tinted fills pair with their own ink: `accent-ink` on `accent-wash`, `warn-ink` on `warn-wash`, `ok` on `ok-wash`, `bad` on `bad-wash`, `hl-<colour>` on `hl-<colour>-wash`.
- On `accent-fill` use `on-accent`. `accent-fill` is the accent stepped 20% toward black so white labels pass 4.5:1; `accent` itself stays the system colour for marks, rings and tints.
- Charts use `series-1` to `series-5`, which are Apple's system mint, purple, blue, pink and orange: the HIG Increased Contrast values in light, the defaults in dark. Data ramps use `heat-1` to `heat-4`. Both are marks at 3:1 or better on `surface`; put numbers in `ink`, not the series colour. Chart layout follows the BarChart card.
- When one bar, dot or segment is the point, chart in emphasis: that mark takes one series colour (`series-1` unless the screen already means something by mint) and every other mark takes `chart-base`. Label every `chart-base` mark or give the chart a table, since grey marks sit under 3:1.
- Highlighted text uses Apple Notes' five colours: `hl-purple`, `hl-pink`, `hl-orange`, `hl-mint`, `hl-blue`, each on its own `-wash`. Pick a meaning per colour and keep it (see Highlight).
- Status uses the system green, orange and red, stepped for text. Each still comes with a word or glyph.
- Dark is Apple's: a black `ground`, `surface` one step up at #1C1C1E, every system colour at its dark value.

## Type

| Role | Style | SwiftUI |
|---|---|---|
| Screen title | `large-title` 34/41 bold | `.largeTitle.bold()` |
| Detail title | `title-1` 28/34 bold | `.title.bold()` |
| Section | `title-2` 22/28 bold | `.title2.bold()` |
| Panel title | `panel-title` 11/13 semibold, +0.8, uppercase, `ink-faint` | `.caption2.weight(.semibold)` + `.tracking(0.8)` + `.foregroundStyle(.tertiary)` |
| Row title | `headline` 17/22 semibold | `.headline` |
| Reading | `body` 17/22 | `.body` |
| Web body | `callout` 16/21 | `.callout` |
| Row subtitle | `subhead` 15/20 | `.subheadline` |
| Metadata | `footnote` 13/18 | `.footnote` |
| Axis, footer | `caption` 12/16 | `.caption` |
| Tile key | `label` mono 11, 600, +0.08em, uppercase | `.caption2.monospaced().weight(.semibold)` + `.textCase(.uppercase)` + `.tracking(0.9)` |
| Tile value | `value` mono 28/32 600 | `.system(size: 28, weight: .semibold, design: .monospaced)` |
| Eyebrow | `eyebrow` mono 11/13 600, +1.2, uppercase | `.caption2.monospaced().weight(.semibold)` + `.tracking(1.2)` |
| Fact label, value | `caption` 12/16 · `fact` mono 12/16 | `.caption` · `.system(.caption, design: .monospaced)` |

One family: SF, in the cuts the system gives you. `design: .default` for UI, `.rounded` (SF Pro Rounded) for Health-style figures (`figure`), `.monospaced` (SF Mono) for codes and timers, SF Pro Text with extra leading for long reading (`script`); SF Compact is the watch face and only appears on watchOS and widgets. Nothing lighter than Regular.

Web pages and artifacts use **Artifact Kit**, the same palette for the browser; see the Web section.

## Space and shape

- Hit targets are at least `touch` (44px). Pills are 40px tall with the rest of the 44 as gap.
- Page gutters: `space-6` (16) on phone, `space-7` (20) on iPad and desktop. Panels pad `space-6`; gaps between stacked panels `space-7`, between tiles in a panel grid `space-5`; sections `space-8`.
- Radii: buttons and pills are capsules (`radius-pill`, as in iOS 26); `radius-sm` (6) thumbnails and badges, `radius-md` (10) inputs and rows, `radius-lg` (14) panels and sheets, `radius-pill` for pills and toasts. Nest one step down: a `radius-md` row inside a `radius-lg` panel.
- Detail cards tile in an equal grid: adaptive columns at least 250 wide, `space-5` (12) apart, every card as tall as the tallest in its row (see Panel).
- A state outline is `stroke-outline` (1.5) inside the edge; the empty slot dashes it `stroke-dash` (6 on, 4 off) in `ink-faint`.

## Components

Button, FilterPill, SegmentedControl, Badge, Flag, StatTile, Panel, Fact, Eyebrow, Toolbar, SidebarList, Shelf, ArtworkCard, HeroCard, TrackList, MiniPlayer, ListRow, Highlight, BarChart. Each card below has its guidelines and a live preview. In SwiftUI prefer the system control (`.bordered`, `.borderedProminent`, `.glass`, `Picker(.segmented)`) and read colours from `AppKit.swift` in `~/developer/app-kit/swift`, which mirrors these tokens.

## Iconography

SF Symbols, regular weight, sized to the text beside them, hierarchical rendering in the tint. There is no logo; apps set their name in `title-3`.

## Focus and motion

- Focus ring: 2px solid `accent`, offset 2px (the system focus ring follows the accent).
- Motion is short and functional: 150ms ease-out for state changes, spring on sheet presentation (system default). Respect Reduce Motion.

## The Music variant

A second palette and six components that make an app read as Music for macOS
rather than as a generic Mac app. Opt in per screen: the `music-*` tokens sit
beside the core ones and nothing here replaces `accent`, `ink` or `ground`.

**Every value was measured from the native Mac app**, sampled from
`screencapture` PNGs converted to sRGB and from Accessibility Inspector frames.
The web player is not a source for anything the Mac app also has. An early
scrape of music.apple.com gave `#D60017` for the accent; the Mac app measures
`#FA233B`, which is how far off that route was.

### Three reds, none derived from another

| Token | Light | Dark | Use |
|---|---|---|---|
| `music-accent` | `#FA233B` | `#FA2E48` | sidebar glyphs, text actions, the active queue icon, promotional CTA fills |
| `music-accent-ink` | `#EA0623` | `#FA3851` | the same red as *text*, stepped to pass 4.5:1 |
| `music-select` | `#DC1229` | `#CC132D` | the selected track row pill |

App Kit's convention is the accent stepped 20% toward black, which from
`#FA2E48` gives `#C8253A`. Music uses `#CC132D`. So none of these is reachable
from another and all three are in `tokens.json` as measured values.

The sidebar's selection is none of the three: it is not red at all. It is a
translucent grey, `music-sidebar-select` and `music-sidebar-select-inactive`
(white at 13.4% and 6.3% in dark, black at 9.3% and 4.5% in light), an alpha
because it composites over whatever the vibrancy puts behind it.

`music-accent` fails 4.5:1 on its own ground (`#FA2E48` on `#1F1F20` is 4.35),
which is why `music-accent-ink` exists. Fidelity and accessibility genuinely
disagree there and one token cannot carry both.

### The accent is a fill for exactly one kind of button

| Kind | Example | Fill | Label |
|---|---|---|---|
| transport / primary | Play on an album | neutral, inverting: `#0E0E0E` light, `#F3F3F3` dark | the opposite neutral |
| CTA / promotional | "Set Location" in a Concerts card | the accent | white |

The thing you press to *play* is neutral; the thing that *sells* you something
is red. Backwards gives a red Play button, which reads as not-Music at a glance.

### Inactive is the normal state

macOS greys a selection when the window is not key, and a monitor app spends
most of its life there. `TrackList` takes `windowInactive`, which swaps
`music-select` for `music-select-inactive` and returns labels to normal ink.
`SidebarList` takes it too and swaps `music-sidebar-select` for
`music-sidebar-select-inactive`. Sidebar glyphs keep their accent in the web
component; the SwiftUI recipe steps a selected row's glyph to
`music-ink-soft-on-fill` once the window is inactive.

Music's own secondary ink on a filled row was never measured, and the measured
`music-ink-soft` reaches only 3.31:1 on the inactive fill and 3.99:1 on hover in
light. So secondary cells step to `music-ink-soft-on-fill` whenever a fill is
under them. That is a decision rather than a measurement, and it is the same
split App Kit already makes between `accent` and `accent-ink`.

### Sizes are not the spec; ratios and gaps are

Three readings of the same window disagreed on card size and agreed on
everything else, because cards track the width left over by a user-resizable
sidebar. So:

- `Shelf` owns the **gap**: 20px, or 16px when `compact`. That is a breakpoint,
  measured at ~1300px and 772px of content; where it switches is unknown.
- `ArtworkCard` is a square artwork plus a **37px** caption that does not scale.
- `HeroCard` is **3:4** and derives its height.
- `TrackList` rows are **56px** and the highlight is a pill inset **40px** each
  side, 45px tall, ~6px radius -- never a full-bleed row fill.
- `MiniPlayer` is **700x54** with a stadium radius, floating 19px up and centred
  on the *content area*, not the window. Its layout is set by hit frames, not
  glyphs (28pt transport, Play 36, 36pt actions), so the now-playing group runs
  166-572 whatever glyphs are passed.

Nothing here ships a fixed card size, because a component shipping 188x225 is
correct only at the one sidebar position it was measured at.

### What is ours and not Music's

`HeroCard` carries a bottom scrim. Music's heroes are commissioned artwork that
happens to carry white text -- the one measured puts white on `#F4B63F`, which
is 1.81:1. An adopting app has whatever artwork it has, so the card backs its
own text: 10.0:1 at the title and 6.5:1 at the eyebrow over a pure white image,
the worst case.

### Not here, on purpose

- **A contextual toolbar.** Music's toolbar content is per page (the share and
  edit buttons, the search field), so there is no one component to ship.
- **Window chrome.** Traffic lights, the sidebar toggle and the title area belong
  to the adopting app's window, not to this kit.

### SwiftUI

Every component here carries a SwiftUI recipe, and those recipes are
**extracted from a spike at build time** rather than written into the docs. The
spike compiles against `swift/AppKit.swift` itself and is rendered in a real
window before anything ships, so a recipe that stopped compiling fails the
build instead of reaching a reader. On a machine without `swiftc` the build
says NOT CHECKED rather than passing quietly.

Three things the spike settled that a browser could not:

- **`.tint()` does not reach a sidebar selection.** With the list focused the
  row fills `#007AFF`, the system accent, against a tint set to `#CC132D`. Music's
  own sidebar selection is neutral, not red, so the recipe draws its own neutral
  row background and binds no `selection:` on the `List`, because the native
  highlight would draw underneath it. The cost is the List's arrow keys.
- **A key window is not a focused list.** The same row fills `#434346` when the
  window is key but focus is elsewhere, which is neither the accent nor the
  tint. Establish which state you are in before reading a colour off a screen.
- **`.listStyle(.sidebar)` gives the real vibrancy for free**, within 2 units of
  Music's own sidebar, and setting any background defeats it. CSS `glass` is a
  `backdrop-filter` that samples the page; the real thing samples the desktop
  behind the window.

The full measurement record, including what was measured, how, and what was
retracted, is `build/source/music-capture.md` in the repo.
