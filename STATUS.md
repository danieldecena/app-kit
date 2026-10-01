# STATUS

## Confirmed working

- `build/app_build.py` regenerates `design-system/project/` and `swift/AppKit.swift` from the source snapshot; the build asserts no raw `px` font sizes survive outside the `--type-*` vars.
- The App Kit design system artifact (URL in `artifacts.json`) serves the tint tokens, `--type-*` style vars and the `motion` group; observed resolving in a live preview frame on 2026-09-29 (`--motion-fast` 150ms, button transition 0.15s ease-out, stat tile 700 28px/32px Rounded).
- SegmentedControl keyboard: one tab stop on the chosen segment, arrows move and choose with wrap, Home/End jump (headless Chrome, 2026-09-29).
- The Music variant: eleven `music-*` tokens plus SidebarList, Shelf, ArtworkCard, HeroCard, TrackList and MiniPlayer. Published as artifact version 26 (2026-10-01). Every geometry claim verified from the live DOM in the preview harness in both appearances, and the MiniPlayer additionally against a real `.regularMaterial` in the SwiftUI spike.
- The build's contrast gate computes WCAG 2.x ratios over 33 token pairs and fails the build below the claimed figure. Proved to fire by mutation, with the mutation asserted applied each time.
- An orientation check catches a `T(name, light, dark)` triple written dark-first, which a contrast gate cannot: ratios survive a consistent swap. It caught a real inversion of all eleven Music tokens.

## Known broken

- Nothing known broken.

## Next Up

- Two capture tasks need Daniel's hands, because driving Music is policy-blocked for the agent: a row with the mouse held down (does a pressed state exist?), and the dark transport button with the window inactive (for `music-primary-inactive`).
- Contextual toolbar and window chrome are deliberately deferred, not dropped. Music's are per-page, so both need their own capture pass before either is a component.

## Decision log

### 2026-10-01
- Decided: the native Mac app is the only value source for the Music variant. An early Firecrawl scrape of music.apple.com gave `#D60017` for the accent against a measured `#FA233B`, so the web player is superseded by measurement rather than by argument.
- Decided: ship ratios and gaps, never card sizes. Three readings of the same window disagreed on card size and agreed on the gap and the ratios, because cards track the width left by a user-resizable sidebar. `ArtworkCard` is width + 37, `HeroCard` is 3:4, `Shelf` owns the 20/16 gap breakpoint.
- Decided: `music-ink-soft-on-fill` (`#5F5F5F` / `#B4B4B4`) rather than moving the measured `music-ink-soft`. The measured value is 3.31:1 on `music-select-inactive` and 3.99:1 on `music-hover` in light, and fidelity is the point of the measured token, so the variant takes the same split App Kit already makes between `accent` and `accent-ink`.
- Decided: `HeroCard` carries a bottom scrim that Music does not have. Music's heroes are commissioned to carry white text; the one measured is white on `#F4B63F`, 1.81:1. An adopting app has whatever artwork it has. Stops computed against a pure white image: 10.0:1 at the title, 6.5:1 at the eyebrow.
- Decided: TrackList joins this plan rather than going to `music-discovery-web` or being deferred. The measurements already existed and it carries more Music character than anything else outstanding.
- Answered: `.tint` does not reach a SwiftUI sidebar selection. On a key, active window with `.tint(Color.musicSelect)` the selected row fills `#434346`, a neutral grey. A SwiftUI `SidebarList` needs a custom row background.
- Retracted: "macOS denies focus to a shell-launched binary", written after four consecutive `isKeyWindow=false` self-captures. Five later attempts returned true four times. Focus there is unreliable, not denied, and the question had been parked on Daniel for nothing. A count of a flaky operation is not a mechanism (`cerebrum.md`).
- Caught late: the TrackList hover rule tied the selected-row rule on specificity and won by order, so a hovered selected row painted the stepped grey onto the red fill at 1.27:1. The gate is not at fault; both pairs pass on their own and the failure lives only in the cascade between them. Fixed and verified by driving a real hover rather than re-reading the cascade.
- Retracted: "the progress bar runs along the MiniPlayer's lower edge", which came from a pasted screenshot. Measured, the line runs x 165-555 inside the 700pt capsule: it belongs to the now-playing group, not the capsule.

### 2026-09-29
- Decided: StatTile `attention` moves from an `accent` ring to `warn`, ring and meter (track `warn-wash`), so "needs the person" reads as one colour with the Panel `act` tone. Computed ring `#C73300` in a headless Chrome render; published as artifact version 20, the three files read back byte-identical.
- Decided: Panel tiles equalise per row, not across the grid. `.dc-panel-grid` drops `grid-auto-rows: 1fr` (CSS grid's default row stretch does the rest) and the Panel README describes Spinner's `TileGrid` Layout. Grid-wide equal heights stretched a short card to a chart two rows away (Spinner a39aa82). Published as artifact version 19, the four files read back byte-identical.
- Decided: type styles ship as `--type-<name>` shorthand vars prepended to `bundle.css`, and component rules reference them, adding a `font-weight` override where a component needs a heavier cut than the style. Keeps one source of truth for size/leading while letting buttons and pills stay semibold.
- Decided: added `caption-2` (11/13) for chart ticks and `figure-md` (28/32 Rounded) for stat tiles rather than leaving those as raw sizes; the ListRow thumbnail moved from 10/12 to the `label` style (11/14), the only intended visual change.
- Decided: motion is a `motion` token group (`motion-fast` 150ms, `motion-ease` ease-out). The Design System page accepts that family natively; reduced motion still drops button transitions to none.
- Decided: publish to the artifact sends only changed `project/` files and the index last, with only `lastChange` edited (version 14, 2026-09-29).
- Decided: brought Footage Library's detail-card patterns into App Kit (Fact, Eyebrow, Toolbar; Panel restyled as the detail card) without its clay accent, blue signal or filter chips. Footage has no separate attention colour in App Kit, so the Charts plate `act` state maps to `warn` and `live` to `accent`; plate states became Panel `tone`s rather than a second card component.
- Decided: new tokens are `ink-faint` (tertiaryLabel, iOS values rgba(60,60,67,.30) / rgba(235,235,245,.30), not observed on a device), a `stroke` group (`stroke-outline` 1.5px, `stroke-dash` 6 4) and `panel-title` / `eyebrow` / `fact` type styles with px tracking. Tracking and stroke vars are also emitted in the `bundle.css` `:root` block, since host support for an unknown `stroke` family is unverified; Swift gets `CGFloat.Kit`.
- Decided: the equal-tile grid is Claude Spinner's (adaptive 250, gap 12, tallest-card preference), not Footage's details grid (adaptive 300, gap 16, top-aligned), per the brief. Previews verified in headless Chromium and WebKit, light and dark (2026-09-29); not yet published.
