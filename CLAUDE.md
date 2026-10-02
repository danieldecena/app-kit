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

Two things that cost a session each when measuring in the harness:

- **The browser caches `bundle.js`.** A rebuild does not reach the page, so the
  "fixed" code under test is the old code and the result reads as a pass. Add a
  `?v=<epoch>` to the script src, and have the page assert *which* build it
  loaded before measuring anything.
- **The harness re-renders, detaching node references.** A `track` captured
  before an `await` can be a detached node by the time you read it, which reports
  `clientWidth: 0` and silently makes every scroll a no-op. Re-query inside each
  step, or measure on an isolated static page instead.
- **Smooth scrolling cannot be measured there at all** when the browser pane is
  hidden: `document.hidden` is true, and Chromium does not run scroll animations
  on a hidden document even though `requestAnimationFrame` keeps ticking. Every
  instant scroll form still works, so the asymmetry is the tell.
- **Switching `data-theme` and reading `getComputedStyle` in the same call gives
  you the previous theme's `background-color`.** `color` updates immediately and
  the custom properties on `:root` resolve correctly, so a probe that reads both
  comes back internally inconsistent -- a near-white fill under a white label --
  and looks exactly like a broken component. A forced reflow does not fix it.
  Set the theme in one tool call and read in the next, so a frame elapses, or
  reload the page per appearance. This cost a real false alarm on the `music`
  Button variant, which was correct the whole time.

Use `/usr/bin/python3` for anything needing pillow. `uv run --with pillow`
re-resolves against pypi and fails with no network; the system python has it.

## Publish

`README.md` holds the rule and `artifacts.json` holds the URL. Publish with the
recorded URL; omitting it mints a second artifact and the existing link goes
stale. The index (`design-system.json`) goes last, re-read right before, with
`lastChange` set. Which publish the repo last made is recorded there too, in
`lastChange.note` -- read that rather than a version number written here,
which goes stale on the next publish and did (it said 34 at v38).

**`index.d.ts` needs an explicit `contentType`.** `.ts` is not a served extension,
and the refusal publishes *nothing at all* rather than skipping that one file:
pass `{"from": "...", "contentType": "text/plain"}`.

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

## What the build checks

Most assertions are structural: no raw `px` font size survives, no `clay` or
`--signal` leaks through, each README surgery matches exactly once. Three are
not, and they are the ones to know about.

- **Contrast is computed, not promised.** `_check_contrast` walks 25 (fg, bg,
  floor) pairs at floors from 3.0 to 13.0 and raises, so a colour that misses
  its claim fails the build. It raises rather than asserts, which keeps it alive
  under `python -O`. This section used to say no assertion computed a ratio and
  that new colours were on the honour system; that stopped being true on
  2026-10-01 and the stale sentence was worth more than the gate for a while.
- **Orientation.** Contrast is blind to a light/dark swap, since inverting both
  sides leaves every ratio unchanged. A separate check asserts which side of
  mid-grey each token belongs on. It caught all eleven Music tokens written
  dark-first from a notes table.
- **The SwiftUI recipes typecheck.** See below.

A new colour still needs its contrast measured and the measurement recorded --
the gate proves the claim you made, not that you picked the right value.

## The SwiftUI recipes are generated

The `## SwiftUI` block in Shelf, HeroCard, TrackList, MiniPlayer and SidebarList
is **extracted at build time** from `build/source/music-components-spike.swift`,
by `// MARK: - <Name>` section. Edit the spike, never the README block, exactly
as with every other generated file here.

The build typechecks that spike against the Swift it just generated
(`swiftc -typecheck`, not `-parse` -- a parse accepts `var w: CGFloat = "nope"`),
so a recipe that stops compiling fails the build instead of shipping. Two limits
are deliberate and stated in the code: it runs *after* the tree is written,
because it needs the generated Swift, and its message says not to install that
build; and without `swiftc` it prints NOT CHECKED rather than passing quietly.

Render it with `swiftc build/source/music-components-spike.swift swift/AppKit.swift -o <bin>`
then `<bin> --selfshot <out.png>`, adding `--light` for the light appearance.

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
