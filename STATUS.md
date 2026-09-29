# STATUS

## Confirmed working

- `build/app_build.py` regenerates `design-system/project/` and `swift/AppKit.swift` from the source snapshot; the build asserts no raw `px` font sizes survive outside the `--type-*` vars.
- The App Kit design system artifact (URL in `artifacts.json`) serves the tint tokens, `--type-*` style vars and the `motion` group; observed resolving in a live preview frame on 2026-09-29 (`--motion-fast` 150ms, button transition 0.15s ease-out, stat tile 700 28px/32px Rounded).
- SegmentedControl keyboard: one tab stop on the chosen segment, arrows move and choose with wrap, Home/End jump (headless Chrome, 2026-09-29).

## Known broken

- Nothing known broken.

## Next Up

- No open items; see `TASKS.md`.

## Decision log

### 2026-09-29
- Decided: type styles ship as `--type-<name>` shorthand vars prepended to `bundle.css`, and component rules reference them, adding a `font-weight` override where a component needs a heavier cut than the style. Keeps one source of truth for size/leading while letting buttons and pills stay semibold.
- Decided: added `caption-2` (11/13) for chart ticks and `figure-md` (28/32 Rounded) for stat tiles rather than leaving those as raw sizes; the ListRow thumbnail moved from 10/12 to the `label` style (11/14), the only intended visual change.
- Decided: motion is a `motion` token group (`motion-fast` 150ms, `motion-ease` ease-out). The Design System page accepts that family natively; reduced motion still drops button transitions to none.
- Decided: publish to the artifact sends only changed `project/` files and the index last, with only `lastChange` edited (version 14, 2026-09-29).
