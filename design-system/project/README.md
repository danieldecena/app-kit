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
- Detail cards tile in an equal grid: adaptive columns at least 250 wide, `space-5` (12) apart, every card as tall as the tallest (see Panel).
- A state outline is `stroke-outline` (1.5) inside the edge; the empty slot dashes it `stroke-dash` (6 on, 4 off) in `ink-faint`.

## Components

Button, FilterPill, SegmentedControl, Badge, Flag, StatTile, Panel, Fact, Eyebrow, Toolbar, ListRow, Highlight, BarChart. Each card below has its guidelines and a live preview. In SwiftUI prefer the system control (`.bordered`, `.borderedProminent`, `.glass`, `Picker(.segmented)`) and read colours from `AppKit.swift` in `~/developer/app-kit/swift`, which mirrors these tokens.

## Iconography

SF Symbols, regular weight, sized to the text beside them, hierarchical rendering in the tint. There is no logo; apps set their name in `title-3`.

## Focus and motion

- Focus ring: 2px solid `accent`, offset 2px (the system focus ring follows the accent).
- Motion is short and functional: 150ms ease-out for state changes, spring on sheet presentation (system default). Respect Reduce Motion.
