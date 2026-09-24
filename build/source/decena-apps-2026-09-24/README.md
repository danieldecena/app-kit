> **Archived on 24 Sep 2026.** Paper System 2 (macOS theme) on the Paper System design canvas replaces this system. It is kept for reference only and gets no more updates. New work takes its tokens and chart components from that canvas.

Warm paper, one clay accent, Apple-native bones. Built for SwiftUI apps first (WA Fish Map, Footage Library, Claude Spinner) with the same tokens as CSS for web pages and artifacts.

## Principles

- **One accent, and only for acting.** `clay` marks what you can tap: the primary button, the selected pill, the active tab, a link. Status, charts and attention never borrow it.
- **Busy is clay, waiting-on-you is signal.** `signal` (blue) means the app needs the person: an approval, a failed sync to retry, the focus ring. Keep the hues apart so the two states never read alike at a glance.
- **Surfaces, not shadows.** Separate a `surface` panel from the `ground` behind it, divide rows with `hair`. Shadows exist only for the active segment (`shadow-segment`) and things floating over content (`shadow-float`).
- **Defer to the platform.** On Apple, set text with the system roles below (they map 1:1 to Dynamic Type) and let SF Pro do the work. The web stack falls back to Instrument Sans off Apple devices.
- **A scale is not a status.** `heat-1` to `heat-4` rank data (bite rating, urgency, density). `bad` means something failed. A prime fishing day is `heat-4`, never `bad`.

## Content

- Sentence case everywhere: "Import clips", not "Import Clips". Uppercase only in the mono `label` style.
- Verb first on buttons ("Retry sync", "Add filter"). A control says what happens; the toast after it says what happened ("Synced 42 clips").
- Real units, always: "2,400 fish", "4.2 GB", "6 min ago". Numbers use tabular figures (`font-variant-numeric: tabular-nums`, `.monospacedDigit()` in SwiftUI).
- No emoji. Status carries a word or glyph as well as a color.

## Color

- `ink` on `surface` for body text; `ink-soft` for secondary lines. Both pass on `ground`, `surface` and `surface-sunk` in both themes.
- Control borders use `edge` (3:1). `hair` is decoration only and never the sole outline of a control.
- Tinted fills pair with their own ink: `clay-ink` on `clay-wash`, `warn-ink` on `warn-wash`, `signal` on `signal-wash`, `ok` on `ok-wash`, `bad` on `bad-wash`.
- On a `clay` fill, use `on-clay` (white in light, near-black in dark, where clay lightens).
- Charts use `series-1` to `series-5`, which are Apple's system mint, purple, blue, pink and orange: the HIG Increased Contrast values in light, the defaults in dark. Data ramps use `heat-1` to `heat-4`. Both are marks at 3:1 or better on `surface`; put numbers in `ink`, not the series colour. Chart layout follows the BarChart card.
- When one bar, dot or segment is the point, chart in emphasis: that mark takes one series colour (`series-1` unless the page already means something by mint) and every other mark takes `chart-base`. Label every `chart-base` mark or give the chart a table, since grey marks sit under 3:1.
- Highlighted text uses Apple Notes' five colours: `hl-purple`, `hl-pink`, `hl-orange`, `hl-mint`, `hl-blue`, each on its own `-wash`. Pick a meaning per colour and keep it (see Highlight).
- `warn` is olive and `bad` a true red so each stays at least 1.28:1 from clay in lightness in both themes; a warning must never be mistaken for the accent.
- Dark is designed, not inverted: `ground` goes to a warm near-black (#121110), panels lift one step to `surface`, and clay, signal and the status colors lighten for contrast.

## Type

| Role | Style | SwiftUI |
|---|---|---|
| Screen title | `large-title` 34/41 bold | `.largeTitle.bold()` |
| Detail title | `title-1` 28/34 bold | `.title.bold()` |
| Section | `title-2` 22/28 bold | `.title2.bold()` |
| Panel title | `title-3` 20/25 semibold | `.title3.weight(.semibold)` |
| Row title | `headline` 17/22 semibold | `.headline` |
| Reading | `body` 17/22 | `.body` |
| Web body | `callout` 16/21 | `.callout` |
| Row subtitle | `subhead` 15/20 | `.subheadline` |
| Metadata | `footnote` 13/18 | `.footnote` |
| Axis, footer | `caption` 12/16 | `.caption` |
| Tile key | `label` mono 11, 600, +0.08em, uppercase | `.caption2.monospaced().weight(.semibold)` + `.textCase(.uppercase)` + `.tracking(0.9)` |
| Tile value | `value` mono 28/32 600 | `.system(size: 28, weight: .semibold, design: .monospaced)` |

One family: SF. `display` (SF Pro Display, `.largeTitle` weight on Apple) is for one hero figure or page headline per screen, at most. It never sets UI chrome. Off Apple devices every role falls back to Instrument Sans and JetBrains Mono.

Long-read web pages (prep sheets, briefs, study guides) use the Paper profile: see the Paper documents section.

## Space and shape

- Hit targets are at least `touch` (44px). Pills are 40px tall with the rest of the 44 as gap.
- Page gutters: `space-6` (16) on phone, `space-7` (20) on iPad and desktop. Panels pad `space-6`; gaps between panels `space-7`; sections `space-8`.
- Radii: `radius-sm` (6) thumbnails and badges, `radius-md` (10) controls and rows, `radius-lg` (14) panels and sheets, `radius-pill` for pills and toasts. Nest one step down: a `radius-md` row inside a `radius-lg` panel.

## Components

Button, FilterPill, SegmentedControl, Badge, Flag, StatTile, Panel, ListRow, Highlight, BarChart. Each card below has its guidelines and a live preview. In SwiftUI, build each as a `View` or `ButtonStyle` reading these tokens from an asset catalog color set per color token.

## Iconography

SF Symbols on Apple, regular weight, sized to the text beside them. On the web, no icon font is shipped: use plain glyphs (`->`, `+`, `x`) in the mono face, or inline SVGs drawn at 1.5px stroke in `currentColor`. There is no logo; apps set their name in `title-3` sans.

## Focus and motion

- Focus ring: 2px solid `signal`, offset 2px, on every interactive element (3:1 or better on every surface).
- Motion is short and functional: 150ms ease-out for state changes, spring on sheet presentation (system default). Respect Reduce Motion.
