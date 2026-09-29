# STATUS

## Confirmed working

- `build/app_build.py` regenerates `design-system/project/` and `swift/AppKit.swift` from the source snapshot; the build asserts no raw `px` font sizes survive outside the `--type-*` vars.
- The App Kit design system artifact (URL in `artifacts.json`) serves the tint tokens, `--type-*` style vars and the `motion` group; observed resolving in a live preview frame on 2026-09-29 (`--motion-fast` 150ms, button transition 0.15s ease-out, stat tile 700 28px/32px Rounded).
- SegmentedControl keyboard: one tab stop on the chosen segment, arrows move and choose with wrap, Home/End jump (headless Chrome, 2026-09-29).

## Known broken

- Nothing known broken.

## Next Up

- Publish the Footage patterns (Fact, Eyebrow, Toolbar, Panel tones) to the artifact in `artifacts.json`, index last.
- Decide whether StatTile `attention` keeps its `accent` ring or moves to `warn` like the Panel `act` tone.

## Decision log

### 2026-09-29
- Decided: type styles ship as `--type-<name>` shorthand vars prepended to `bundle.css`, and component rules reference them, adding a `font-weight` override where a component needs a heavier cut than the style. Keeps one source of truth for size/leading while letting buttons and pills stay semibold.
- Decided: added `caption-2` (11/13) for chart ticks and `figure-md` (28/32 Rounded) for stat tiles rather than leaving those as raw sizes; the ListRow thumbnail moved from 10/12 to the `label` style (11/14), the only intended visual change.
- Decided: motion is a `motion` token group (`motion-fast` 150ms, `motion-ease` ease-out). The Design System page accepts that family natively; reduced motion still drops button transitions to none.
- Decided: publish to the artifact sends only changed `project/` files and the index last, with only `lastChange` edited (version 14, 2026-09-29).
- Decided: brought Footage Library's detail-card patterns into App Kit (Fact, Eyebrow, Toolbar; Panel restyled as the detail card) without its clay accent, blue signal or filter chips. Footage has no separate attention colour in App Kit, so the Charts plate `act` state maps to `warn` and `live` to `accent`; plate states became Panel `tone`s rather than a second card component.
- Decided: new tokens are `ink-faint` (tertiaryLabel, iOS values rgba(60,60,67,.30) / rgba(235,235,245,.30), not observed on a device), a `stroke` group (`stroke-outline` 1.5px, `stroke-dash` 6 4) and `panel-title` / `eyebrow` / `fact` type styles with px tracking. Tracking and stroke vars are also emitted in the `bundle.css` `:root` block, since host support for an unknown `stroke` family is unverified; Swift gets `CGFloat.Kit`.
- Decided: the equal-tile grid is Claude Spinner's (adaptive 250, gap 12, tallest-card preference), not Footage's details grid (adaptive 300, gap 16, top-aligned), per the brief. Previews verified in headless Chromium and WebKit, light and dark (2026-09-29); not yet published.
