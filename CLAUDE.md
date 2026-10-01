# CLAUDE.md

App Kit is the Decena Apps design system brought back for SwiftUI apps, on
Apple's own system neutrals. It ships as a published Design System artifact plus
a SwiftUI token mirror. There is no app target here and nothing to run.

## Build

Everything under `design-system/project/` and `swift/AppKit.swift` is generated.
Never hand-edit either; edit `build/app_build.py` and regenerate, or the next
build silently reverts you.

The generator takes two paths:

```
python3 build/app_build.py <src> <out>
```

It reads `<src>/project/*` and writes `<out>/project/*` plus
`<out>/swift/AppKit.swift`. Two things about that are not obvious and have
already cost a session:

- **The committed snapshot is not a valid `<src>`.** `build/source/decena-apps-2026-09-24/`
  holds `tokens.json`, `README.md` and `components/` at its top level, but the
  reader wants them under `<src>/project/`. Pointing `<src>` at the snapshot
  fails with `FileNotFoundError` on `tokens.json`. Give it a directory whose
  `project` is the snapshot:

  ```
  mkdir -p /tmp/ak/src && ln -sfn "$PWD/build/source/decena-apps-2026-09-24" /tmp/ak/src/project
  /opt/homebrew/bin/python3 build/app_build.py /tmp/ak/src /tmp/ak/out
  ```

  Verified 2026-09-30: that reproduces `swift/AppKit.swift` byte-identical and
  `design-system/project/` identical but for the one file below. The invocation
  in `README.md:19` is a description, not a runnable command.

- **`<out>` cannot be a single in-tree path.** `<out>/project` corresponds to
  `design-system/project/` while `<out>/swift` corresponds to `swift/` at the
  repo root, so no one value of `<out>` lands both where they live. Build to a
  scratch `<out>`, diff, then copy the two trees into place.

**`design-system/project/design-system.json` is not generated.** It is the
published index and carries `lastChange`. The build never writes it and nothing
should: a build that produced it would overwrite publish state.

Use `/opt/homebrew/bin/python3`. Never bare `python3`.

**`build/` is ignored globally** (`~/.gitignore_global:52`), yet `build/app_build.py`
and the whole snapshot are tracked because they were force-added. A new file
under `build/` needs `git add -f` or it stages nothing and reports no error.

## Previewing locally

The previews are not standalone pages: each is a bare `<script>` expecting
`React`, `ReactDOM` and `window.AppKit` as globals, and `bundle.css` defines only
`--type-*`, `--stroke-*` and `--tracking-*`, so colour, spacing, radius, shadow
and motion vars are missing too. Opened directly in a browser a preview renders
blank and unstyled. The artifact host supplies all of it.

`build/preview/index.html` is a local stand-in for that host. Serve the repo root
and open it:

```
/opt/homebrew/bin/python3 -m http.server 8111 --directory /Users/home/developer/app-kit
open http://localhost:8111/build/preview/index.html?c=Toolbar
```

`.claude/launch.json` defines the same server for `preview_start`. The component
list comes from the bundle's own `@ds-bundle` manifest, so it cannot drift. Type
is approximate there: `tokens.json` names font families but carries no stacks,
so the harness guesses them. Judge type on the published artifact; judge colour,
spacing, radius, state and layout in the harness.

## Publish

`README.md` holds the rule and `artifacts.json` holds the URL. Publish with the
recorded URL; omitting it mints a second artifact and the existing link goes
stale. The index (`design-system.json`) goes last, re-read right before, with
`lastChange` set. Current artifact version is 20.

## Adding a component

Two patterns exist in the generator and new work follows the first:

- **Authored (Toolbar, Fact, Eyebrow).** Written wholly in `app_build.py`: CSS
  inside the Panel-block replacement, a `function X(p)` in the bundle.js
  replacement, manifest and export entries, a `.d.ts` block, a README, a
  `preview.html` whose first line is an `@dsCard` comment, and an entry in the
  component assert. Copy Toolbar end to end.
- **Pass-through (ListRow, StatTile, …).** Inherited from the snapshot and only
  swept by the global replacements. Nothing new arrives this way.

Font declarations are rewritten into `--type-*` vars by a sweep that asserts it
matched. Write a size/leading/family triple that already exists in
`tokens.json`, or the build fails rather than emitting a raw `px` size.

## What the build does not check

The 12 assertions are structural: no raw `px` font size survives, no `clay` or
`--signal` leaks through, each README surgery matches exactly once. **No
assertion computes a contrast ratio.** Every "4.5:1" in `tokens.json` is a
hand-written usage string verified out of band in a browser. A new colour's
contrast is on the honour system until a check exists, so measure it and say
where you measured it.

## Design work

This is a design system, so judgement alone is not review. Run the skill and say
which skill produced which finding:

- `design:design-system` (extend) before adding a token or component, for naming
  and state parity with what is already here.
- `design:accessibility-review` for any colour, any text over artwork, and any
  hover or hit target.
- `design:design-critique` on a side-by-side screenshot, for hierarchy and
  spacing.
- `dataviz` before restyling any chart, meter or stat tile.
- `apple-docs` for any Apple framework symbol, before reasoning about it.

Previews are judged in headless Chromium and WebKit, light and dark. Material is
not: `glass` is a `backdrop-filter` stand-in and Chromium samples the page, not
the desktop, so vibrancy can only be judged in a real SwiftUI window.
