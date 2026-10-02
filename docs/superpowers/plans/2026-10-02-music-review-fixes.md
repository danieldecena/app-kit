# Music Review Fixes Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Close the gaps found when the App Kit tab in Claude Spinner was compared side by side with the real Music app on 2026-10-02.

**Architecture:** The Music components' SwiftUI lives in `build/source/music-components-spike.swift`, and the generator (`build/app_build.py`) extracts it into the README recipes, typechecks it, and emits tokens to `swift/AppKit.swift` and `design-system/project/`. Every fix lands in the spike or the generator, then the tree is regenerated, then the two generated Swift files are re-copied byte-for-byte into Claude Spinner's App Kit tab.

**Tech Stack:** SwiftUI (macOS 27 SDK, `swiftc`), Python 3 generator (`/opt/homebrew/bin/python3`), pillow via `/usr/bin/python3` for pixel probes, `screencapture`.

**Spec:** The review in this session, restated as requirements below, and the measurements in `build/source/music-capture.md` (the source of truth for every value; any value a task adds must be recorded there first).

## What the review found, corrected

The review made six claims. Three survived a check against the code and the capture notes:

1. **Background-window sidebar is not dimmed.** Music greys every sidebar icon and dims every label when its window is not in front (`music-capture.md:150-161`: zero red pixels in the icon column, light, inactive). App Kit dims only the selected row, in both the Swift `SidebarList` (`glyph()` returns `musicAccent` for every unselected row) and the web CSS (`app_build.py:1292` targets only `[aria-current="true"]`). Claude Spinner is a monitor app whose window is in the background most of the time, so this is the state its users see most. Measured 2026-10-02 from an inactive dark capture: sidebar ground `#252526`, unselected labels `#929293`, unselected icons `#454546`.
2. **No large page title.** Music opens Home with a large bold "Home" above the first shelf. App Kit has nothing for it.
3. **Selections move after launch with no input.** Seen twice in the Claude Spinner tab: the TrackList went from "Solo" to "Nights", and the SidebarList from "Home" to "Songs". The spike renders both correctly when run alone, so the cause is in the hosting.

Three did not survive and get **no task**:

- "MiniPlayer is narrower than Music's": wrong. Music's capsule measures 699pt at a 980pt window; App Kit's is 700pt. It only looked wider because Music's window was smaller.
- "Shelves don't overflow": the component already scrolls (`Shelf` uses a horizontal `ScrollView` with `contentMargins`). The tab simply passes three hero cards. Fixed as demo data in Task 6, not in the component.
- "Sidebar is black, not material": a hosting artifact. Outside a split view's sidebar column, `.listStyle(.sidebar)` gets no vibrancy. The spike window, which is a real `NavigationSplitView`, renders it correctly. Not fixable from inside Claude Spinner's detail pane and not an App Kit defect.

## Global Constraints

- Never hand-edit `design-system/project/**` or `swift/AppKit.swift`; edit `build/app_build.py` or the spike, then regenerate (`CLAUDE.md`, Build).
- Build: `mkdir -p /tmp/ak/src && ln -sfn "$PWD/build/source/decena-apps-2026-09-24" /tmp/ak/src/project && /opt/homebrew/bin/python3 build/app_build.py /tmp/ak/src /tmp/ak/out`, then diff and copy `/tmp/ak/out/project/` to `design-system/project/` and `/tmp/ak/out/swift/AppKit.swift` to `swift/AppKit.swift`.
- `design-system/project/design-system.json` is never written by the build or by hand outside a publish.
- A new file under `build/` needs `git add -f` (`build/` is ignored globally).
- Python: `/opt/homebrew/bin/python3` for the generator, `/usr/bin/python3` for anything needing pillow. Never bare `python3`.
- Spike render: `swiftc build/source/music-components-spike.swift swift/AppKit.swift -o /tmp/ak/spike && /tmp/ak/spike --dark --selfshot /tmp/ak/shot.png`. The appearance flag goes **before** the path; the path is read as the last argument.
- The spike's selfshot window is never key (`isKeyWindow=false` is printed), so a plain selfshot is the **inactive** state.
- Every new colour gets a row in the contrast gate, and the gate's floor is the claim the usage string makes.
- Design review is by skill, named per finding: `design:accessibility-review` for any colour and any hover target, `design:design-critique` on a side-by-side, `design:design-system` before adding a token.
- Commit with an explicit pathspec, imperative subject, `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`. Never `--no-verify`, never amend.
- Claude Spinner's `claude spinner/AppKitTokens.swift` and `claude spinner/AppKitMusicComponents.swift` must stay byte-identical to app-kit's `swift/AppKit.swift` and spike lines 1 through the line before `// MARK: - Spike window`. `cmp` is the check.

---

### Task 1: Measure the inactive sidebar in both appearances

Dark is measured once, from a scratch capture. Light is unmeasured. Both need a controlled capture recorded in the notes before any token exists.

**Files:**
- Modify: `build/source/music-capture.md` (append a section)
- Create: `build/tools/sidebar_probe.py` (force-add)

**Interfaces:**
- Produces: four measured hexes recorded in `music-capture.md` under the heading `## Inactive sidebar ink -- 2026-10-02`, named `label-dark`, `glyph-dark`, `label-light`, `glyph-light`. Task 2 copies them.
- Produces: `build/tools/sidebar_probe.py <png> <x0_pt> <x1_pt> <y0_pt> <y1_pt>`, which prints the sidebar ground, the most common non-ground colour in the region, and a count of red pixels (`r > 180 and g < 90 and b < 110`). Tasks 1 and 3 use it.

- [ ] **Step 1: Write the probe**

```python
#!/usr/bin/env python3
"""Sample a sidebar region of a 2x window capture.

Prints the ground (sampled at the region's right edge, mid-height), the most
common colour that differs from it by more than 20 in channel sum, and how
many red pixels the region holds. Coordinates are in points; the capture is
assumed to be @2x, which `screencapture -l` produces on a Retina display.
"""
import sys
from collections import Counter
from PIL import Image

path, x0, x1, y0, y1 = sys.argv[1], *map(float, sys.argv[2:6])
im = Image.open(path).convert("RGB")
s = 2
ground = im.getpixel((int(x1 * s) + 4, int((y0 + y1) / 2 * s)))
ink, red = Counter(), 0
for y in range(int(y0 * s), int(y1 * s)):
    for x in range(int(x0 * s), int(x1 * s)):
        p = im.getpixel((x, y))
        if p[0] > 180 and p[1] < 90 and p[2] < 110:
            red += 1
        if abs(sum(p) - sum(ground)) > 20:
            ink[p] += 1
print("ground  #%02X%02X%02X" % ground)
for p, n in ink.most_common(3):
    print("ink     #%02X%02X%02X  x%d" % (*p, n))
print("red     %d" % red)
```

- [ ] **Step 2: Prove the probe fires and stays quiet**

Run the current spike selfshot (inactive, icons still red, so a known positive) and probe the icon column:

```bash
swiftc build/source/music-components-spike.swift swift/AppKit.swift -o /tmp/ak/spike
/tmp/ak/spike --dark --selfshot /tmp/ak/before-dark.png
/usr/bin/python3 build/tools/sidebar_probe.py /tmp/ak/before-dark.png 20 47 50 320
```

Expected: `red` well above 0 (the unselected icons are `musicAccent`). Then probe a region of the content ground with no red, x 600-700pt, y 50-80pt. Expected: `red 0`. Both outcomes are required before the probe is trusted.

- [ ] **Step 3: Capture Music, dark, inactive**

Open Music on Home, put another app in front, and capture by window id using the recipe in `music-capture.md` (`CGWindowListCopyWindowInfo(.optionAll)`, largest layer-0 window for Music's pid, then `screencapture -o -x -l <id> /tmp/ak/music-inactive-dark.png`). Confirm the file is 2x the window's point size before reading it.

```bash
/usr/bin/python3 build/tools/sidebar_probe.py /tmp/ak/music-inactive-dark.png 20 47 120 400
/usr/bin/python3 build/tools/sidebar_probe.py /tmp/ak/music-inactive-dark.png 55 140 120 400
```

Expected: first line `ground #252526`, icon ink about `#454546`, `red 0`; label ink about `#929293`. If either differs from the scratch reading by more than 4 in any channel, the new capture wins and the difference is noted.

- [ ] **Step 4: Capture Music, light, inactive**

Force Music alone into light without touching the system appearance, relaunch it, capture, then revert:

```bash
defaults write com.apple.Music NSRequiresAquaSystemAppearance -bool yes
osascript -e 'quit app "Music"'; sleep 2; open -a Music; sleep 4
# put another app in front, capture to /tmp/ak/music-inactive-light.png, probe as in Step 3
defaults delete com.apple.Music NSRequiresAquaSystemAppearance
osascript -e 'quit app "Music"'; sleep 2; open -a Music
```

Verify the revert: `defaults read com.apple.Music NSRequiresAquaSystemAppearance` must print an error saying the key does not exist.

- [ ] **Step 5: Record the four values**

Append to `build/source/music-capture.md`:

```markdown
## Inactive sidebar ink -- 2026-10-02

Music dims the WHOLE sidebar when its window is not key, not only the selected
row: every icon loses its red and every label steps down. App Kit dimmed only
the selected row until this measurement.

| | dark | light | how |
|---|---|---|---|
| sidebar ground | `#252526` | <measured> | probe, right edge of the icon column |
| label (unselected) | `label-dark` | `label-light` | most common non-ground colour, x 55-140pt |
| glyph (unselected) | `glyph-dark` | `glyph-light` | most common non-ground colour, x 20-47pt, red = 0 |

Captures: `music-inactive-dark.png`, `music-inactive-light.png`, Home, Music
not key. Probe: `build/tools/sidebar_probe.py`, proven on the spike's own
red icons (fires) and on the content ground (quiet) first.
```

Replace each name and `<measured>` with the hex read in Steps 3 and 4.

- [ ] **Step 6: Commit**

```bash
git add -f build/tools/sidebar_probe.py
git commit -m "Measure Music's inactive sidebar ink in both appearances

Music dims every sidebar icon and label when its window is not key; App
Kit dims only the selected row. Values recorded before any token exists.

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" -- build/tools/sidebar_probe.py build/source/music-capture.md
```

---

### Task 2: Add the two inactive sidebar tokens

**Files:**
- Modify: `build/app_build.py` (token list near the `music-ink-soft-on-fill` `T(...)` at ~line 397; the orientation list near line 374 and 781; the contrast pairs near line 643)
- Regenerated: `swift/AppKit.swift`, `design-system/project/**`

**Interfaces:**
- Consumes: the four hexes from Task 1, Step 5.
- Produces: tokens `music-sidebar-ink-inactive` and `music-sidebar-glyph-inactive`, emitted to Swift as `Color.Kit.musicSidebarInkInactive` and `Color.Kit.musicSidebarGlyphInactive`, and to CSS as `--music-sidebar-ink-inactive` and `--music-sidebar-glyph-inactive`.

- [ ] **Step 1: Run `design:design-system` (extend)**

Ask it whether the two names fit App Kit's naming next to `music-sidebar-select-inactive` and `music-ink-soft-on-fill`. Apply any rename across this whole plan before writing code.

- [ ] **Step 2: Add the tokens, after `music-ink-soft-on-fill`**

`T(name, light, dark, usage)`, the same shape as its neighbours:

```python
    T(
        "music-sidebar-ink-inactive",
        "<label-light>",
        "<label-dark>",
        "Unselected sidebar labels while the window is not key. Music steps every label down, not only the selected row's (music-capture.md, Inactive sidebar ink, 2026-10-02). macOS calls this the inactive appearance; read it from the environment, never from a parameter.",
    ),
    T(
        "music-sidebar-glyph-inactive",
        "<glyph-light>",
        "<glyph-dark>",
        "Unselected sidebar symbols while the window is not key. Music drops the accent from every icon, measured as zero red pixels in the icon column. Decorative: the label beside it carries the meaning, so it is gated as a glyph, not as text.",
    ),
```

Substitute the four recorded hexes for the `<...>` names.

- [ ] **Step 3: Add the gates**

Add both names to the orientation list wherever `music-ink-soft-on-fill` appears in it. Add to the contrast pairs:

```python
        # Inactive sidebar. The label is text and keeps the text floor; the
        # glyph is decorative beside it and is held at what Music measures,
        # which is the claim its usage string makes.
        ("music-sidebar-ink-inactive", "ground-window", 4.5),
```

For the glyph, compute its ratio against the measured sidebar ground in both appearances first. If either is under 3.0, do not invent a floor: run `design:accessibility-review` on the inactive capture, record its verdict in `music-capture.md`, and add a pair at the lower measured ratio rounded down to one decimal, with a comment naming that review.

- [ ] **Step 4: Build and confirm the gate passes and can fail**

```bash
/opt/homebrew/bin/python3 build/app_build.py /tmp/ak/src /tmp/ak/out
```

Expected: success with no contrast error. Then temporarily change `music-sidebar-ink-inactive`'s dark value to the sidebar ground `#252526`, rebuild, and confirm the build **fails** naming that token. Revert, rebuild, confirm it passes again.

- [ ] **Step 5: Copy and verify**

```bash
diff -r /tmp/ak/out/project design-system/project | grep -v design-system.json | head
cp /tmp/ak/out/swift/AppKit.swift swift/AppKit.swift
rsync -a --exclude design-system.json /tmp/ak/out/project/ design-system/project/
grep -n "musicSidebarInkInactive\|musicSidebarGlyphInactive" swift/AppKit.swift
```

Expected: the grep prints both declarations.

- [ ] **Step 6: Commit**

```bash
git commit -m "Add inactive sidebar ink and glyph tokens

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" -- build/app_build.py swift/AppKit.swift design-system/project build/source/music-capture.md
```

---

### Task 3: SidebarList and TrackList read window focus from the environment

Both take `var windowInactive: Bool = false`, which no adopter passes (Claude Spinner's tab does not), so both always render as active. SwiftUI already knows: `@Environment(\.appearsActive)`, available on macOS from 10.15 (back-deployed).

**Files:**
- Modify: `build/source/music-components-spike.swift` (`TrackList` ~line 157, `SidebarList` ~lines 241-256, the spike's `main` ~line 464)
- Regenerated: the SidebarList and TrackList READMEs (their `## SwiftUI` blocks are extracted from the spike)

**Interfaces:**
- Consumes: `Color.Kit.musicSidebarInkInactive`, `Color.Kit.musicSidebarGlyphInactive` (Task 2).
- Produces: `SidebarList(sections:selection:)` and `TrackList(rows:selection:...)` with **no** `windowInactive` parameter. Inactive state is read from `appearsActive`. Callers that passed `windowInactive:` break at compile time, which the build's typecheck surfaces.
- Produces: spike flag `--force-active`, which wraps the root view in `.environment(\.appearsActive, true)`.

- [ ] **Step 1: Record the failing observation**

```bash
/tmp/ak/spike --dark --selfshot /tmp/ak/before-dark.png
/usr/bin/python3 build/tools/sidebar_probe.py /tmp/ak/before-dark.png 20 47 50 320
```

Expected now: `red` > 0 in an inactive window. This is the bug.

- [ ] **Step 2: Add `--force-active` to the spike**

Replace line 464:

```swift
        let root = SpikeView()
        win.contentView = CommandLine.arguments.contains("--force-active")
            ? NSHostingView(rootView: AnyView(root.environment(\.appearsActive, true)))
            : NSHostingView(rootView: AnyView(root))
```

- [ ] **Step 3: Change SidebarList**

Replace `var windowInactive: Bool = false` with:

```swift
    /// Not a parameter: no adopter remembered to pass it, so every one rendered
    /// as active forever. macOS knows whether the window is key.
    @Environment(\.appearsActive) private var appearsActive
    private var windowInactive: Bool { !appearsActive }
```

Replace `ink` and `glyph`:

```swift
    private func ink(_ id: String) -> Color {
        if id == selection { return windowInactive ? Color.Kit.musicInk : Color.Kit.onMusicGlass }
        return windowInactive ? Color.Kit.musicSidebarInkInactive : Color.Kit.musicInk
    }
    /// Music tints the SYMBOL and leaves the label in normal ink, which is why
    /// the row is built from Text and Image rather than a Label. In an inactive
    /// window every symbol loses the accent, not only the selected one
    /// (music-capture.md, Inactive sidebar ink).
    private func glyph(_ id: String) -> Color {
        if id == selection && windowInactive { return Color.Kit.musicInkSoftOnFill }
        return windowInactive ? Color.Kit.musicSidebarGlyphInactive : Color.Kit.musicAccent
    }
```

- [ ] **Step 4: Change TrackList the same way**

Replace its `var windowInactive: Bool = false` with the same two lines as Step 3. Its colour functions stay as they are; they already branch on `windowInactive`.

- [ ] **Step 5: Run the spike and verify both states**

```bash
swiftc build/source/music-components-spike.swift swift/AppKit.swift -o /tmp/ak/spike
/tmp/ak/spike --dark --selfshot /tmp/ak/after-dark.png
/tmp/ak/spike --dark --force-active --selfshot /tmp/ak/after-dark-active.png
/tmp/ak/spike --light --selfshot /tmp/ak/after-light.png
for f in after-dark after-dark-active after-light; do echo $f; /usr/bin/python3 build/tools/sidebar_probe.py /tmp/ak/$f.png 20 47 50 320; done
```

Expected: `after-dark` and `after-light` print `red 0` and a glyph ink within 4 per channel of the Task 1 values. `after-dark-active` prints `red` > 0. If the active shot also reads 0, the change killed the accent outright and is wrong, whatever the inactive shot says.

- [ ] **Step 6: Rebuild the tree**

Run the Global Constraints build, copy as in Task 2 Step 5, and confirm the extracted recipe changed:

```bash
grep -n "appearsActive" design-system/project/components/SidebarList/README.md design-system/project/components/TrackList/README.md
```

Expected: both files match. The build's spike typecheck must pass; it prints NOT CHECKED if `swiftc` is missing, which is not a pass.

- [ ] **Step 7: Commit**

```bash
git commit -m "Dim the whole sidebar when the window is not key

SidebarList and TrackList read appearsActive instead of a parameter
nobody passed. Probe: red icon pixels 0 inactive, >0 with --force-active.

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" -- build/source/music-components-spike.swift swift/AppKit.swift design-system/project
```

---

### Task 4: The web SidebarList dims every row too

**Files:**
- Modify: `build/app_build.py:1288-1292` (the inactive selection CSS)

**Interfaces:**
- Consumes: `--music-sidebar-ink-inactive`, `--music-sidebar-glyph-inactive` (Task 2). The `data-window="inactive"` attribute the preview already sets.

- [ ] **Step 1: Add the rules before the selected-row rules**

Insert above line 1291, so the more specific selected-row rules that follow still win:

```css
.dc-sidebar[data-window="inactive"] .dc-sidebar-row { color: var(--music-sidebar-ink-inactive); }
.dc-sidebar[data-window="inactive"] .dc-sidebar-row .dc-sidebar-icon { color: var(--music-sidebar-glyph-inactive); }
```

- [ ] **Step 2: Build, copy, and check the composed state in the harness**

Serve and open `build/preview/index.html?c=SidebarList&v=<epoch>` (Global Constraints build first; `CLAUDE.md`, Previewing locally). In the inactive preview, read `getComputedStyle` on an unselected row's icon and label, and on the selected row's icon, in a **separate** tool call from any theme switch. Expected: unselected icon = `--music-sidebar-glyph-inactive`, unselected label = `--music-sidebar-ink-inactive`, selected icon = `--music-ink-soft-on-fill`. The last one is the check that the new rules did not override the selected row, which is the specificity collision `silent-failure.md` rule 13 records for TrackList.

- [ ] **Step 3: Sweep the gallery**

Run the one-pass gallery sweep from `CLAUDE.md` (all 20 components: file exists, `@dsCard` first line, `#root` has children, plus the 404 and empty-root controls).

- [ ] **Step 4: Commit**

```bash
git commit -m "Dim every web sidebar row when the window is inactive

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" -- build/app_build.py design-system/project
```

---

### Task 5: Large page title in the spike window

The review found Music's Home opens with a large bold title; App Kit has none. This adds it to the spike's own window only. A component waits for a second adopter (YAGNI), but the measured value goes into the notes so that component starts from data.

**Files:**
- Modify: `build/source/music-capture.md` (append)
- Modify: `build/source/music-components-spike.swift` (`SpikeView`, inside the content `VStack` before the first `Shelf`)

**Interfaces:**
- Produces: the measured title size, weight, leading inset and top offset recorded under `## Page title -- 2026-10-02`. Task 6 reuses the exact `Text` line.

- [ ] **Step 1: Measure**

From `music-inactive-dark.png` (Task 1), find the "Home" title's bounding box: scan rows from y 40pt to 150pt in x 300-600pt for pixels within 20 of `#FFFFFF`. Record top, bottom (cap height = bottom of "H" minus top), and left edge in points. Compare the cap height against SF Pro's cap height ratio (0.705 of the point size) to get the point size, then try `.largeTitle` (26pt on macOS) and a fixed `.system(size:weight: .bold)`. Record whichever renders a cap height within 0.5pt of Music's.

- [ ] **Step 2: Record**

```markdown
## Page title -- 2026-10-02

| | measured | how |
|---|---|---|
| cap height | <pt> | bounding box of "H", near-white pixels |
| point size | <pt> | cap height / 0.705 |
| weight | bold | stroke width matches the shelf heading's bold |
| left edge | <pt> | first ink column; compare to Shelf's 34pt inset |
| top | <pt> | from the content area's top edge |
```

- [ ] **Step 3: Add it to SpikeView**

Before the first `Shelf` in the content `VStack`, with the size and inset from Step 2:

```swift
                    Text("Home")
                        .font(.system(size: <size>, weight: .bold))
                        .foregroundStyle(Color.Kit.musicInk)
                        .padding(.leading, <inset>)
                        .accessibilityAddTraits(.isHeader)
```

- [ ] **Step 4: Side-by-side and critique**

Render `--dark --selfshot`, crop both it and `music-inactive-dark.png` to the content area's top 200pt, and run `design:design-critique` on the pair. Record its verdict under the Step 2 table. The title's left edge must be within 1pt of Music's.

- [ ] **Step 5: Rebuild, copy, commit**

```bash
git commit -m "Give the spike window Music's large page title

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" -- build/source/music-components-spike.swift build/source/music-capture.md swift/AppKit.swift design-system/project
```

---

### Task 6: Claude Spinner tab: re-copy, title, overflowing shelves

**Files (in `~/developer/claude-spinner`, on a branch `appkit-review-fixes`):**
- Replace: `claude spinner/AppKitTokens.swift`, `claude spinner/AppKitMusicComponents.swift`
- Modify: `claude spinner/AppKitShowcase.swift`

**Interfaces:**
- Consumes: the regenerated `swift/AppKit.swift` and spike (Tasks 2, 3, 5). The new `SidebarList`/`TrackList` signatures have no `windowInactive`; the showcase never passed it, so it compiles unchanged.

- [ ] **Step 1: Re-copy and prove identity**

```bash
cd ~/developer/claude-spinner && git switch -c appkit-review-fixes origin/main
cp ~/developer/app-kit/swift/AppKit.swift "claude spinner/AppKitTokens.swift"
end=$(grep -n "^// MARK: - Spike window" ~/developer/app-kit/build/source/music-components-spike.swift | cut -d: -f1)
head -n $((end - 1)) ~/developer/app-kit/build/source/music-components-spike.swift > "claude spinner/AppKitMusicComponents.swift"
cmp ~/developer/app-kit/swift/AppKit.swift "claude spinner/AppKitTokens.swift" && echo TOKENS-IDENTICAL
```

Then update the provenance line in `AppKitShowcase.swift`'s header comment to the app-kit commit the copy came from (`git -C ~/developer/app-kit rev-parse --short HEAD`), and change "lines 1-386" to `lines 1-$((end - 1))`.

- [ ] **Step 2: Add the title and enough cards to overflow**

In `AppKitShowcase.body`, before the first `Shelf`, add the exact `Text("Home")` block from Task 5 Step 3. Add two more `HeroCard`s to "Top Picks for You" and three more `ArtworkCard`s to "Recently Played":

```swift
                            HeroCard(art: grad(Color(red: 0.93, green: 0.30, blue: 0.47), Color(red: 0.85, green: 0.18, blue: 0.25)),
                                     eyebrow: "New Release", title: "Blonde")
                            HeroCard(art: grad(Color(red: 0.98, green: 0.62, blue: 0.20), Color(red: 0.88, green: 0.36, blue: 0.10)),
                                     eyebrow: "Station", title: "Chill Mix")
```

```swift
                            ArtworkCard(art: Color(red: 0.25, green: 0.36, blue: 0.62), title: "Episode 746", subtitle: "Soulection playgroup")
                            ArtworkCard(art: Color(red: 0.62, green: 0.55, blue: 0.24), title: "Episode 747", subtitle: "Soulection playgroup")
                            ArtworkCard(art: Color(red: 0.44, green: 0.26, blue: 0.40), title: "Episode 748", subtitle: "Soulection playgroup")
```

- [ ] **Step 3: Build and test**

Follow the `ios-build` skill: pin `-derivedDataPath`, read xcodebuild's own exit code, require `** BUILD SUCCEEDED **`, grep `warning:` unanchored. Run the unit tests only after `killall "claude spinner"` and after confirming no other session is running them (`pgrep -fl xcodebuild`). Expected: all tests pass, including `testTheAppKitTagResolvesToNoSession`.

- [ ] **Step 4: Observe it**

Install with `./run.sh`, select the App Kit row by AX, capture the window (`screencapture -o -x -l <largest window id>`). Check three things in the capture: the large "Home" title is present; a fourth hero card is cut off at the right edge; and, with Claude Spinner in the background, `sidebar_probe.py` on the App Kit sidebar's icon column reads `red 0`.

- [ ] **Step 5: Commit**

```bash
git commit -m "Refresh the App Kit tab: inactive sidebar, page title, overflowing shelves

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" -- "claude spinner/AppKitTokens.swift" "claude spinner/AppKitMusicComponents.swift" "claude spinner/AppKitShowcase.swift"
```

---

### Task 7: Find what moves the tab's selections after launch

Root cause first (`superpowers:systematic-debugging`). No fix is written in this plan, because the cause is unknown: TrackList went Solo -> Nights (one Up arrow from Solo), and SidebarList went Home -> Songs (three Downs, or a click at Songs' position).

**Files:**
- Modify (temporary, on `appkit-review-fixes`): `claude spinner/AppKitShowcase.swift`

- [ ] **Step 1: Log every selection change with its stack**

Add to the showcase's outer `HStack`:

```swift
        .onChange(of: selection) { old, new in
            os_log("appkit-showcase: track %{public}@ -> %{public}@ %{public}@",
                   String(describing: old), String(describing: new),
                   Thread.callStackSymbols.prefix(12).joined(separator: " | "))
        }
        .onChange(of: navSelection) { old, new in
            os_log("appkit-showcase: nav %{public}@ -> %{public}@ %{public}@",
                   String(describing: old), String(describing: new),
                   Thread.callStackSymbols.prefix(12).joined(separator: " | "))
        }
```

with `import os` at the top of the file.

- [ ] **Step 2: Reproduce under the three candidate triggers, one at a time**

Relaunch the app between each, select the App Kit row, wait 10 seconds, then read `log show --last 1m --predicate 'process == "claude spinner"' | grep appkit-showcase`:

1. App Kit row selected by AX (`AXSelected`), nothing else touched.
2. App Kit row selected by a real mouse click.
3. App Kit row selected by keyboard (arrow keys in Claude Spinner's own sidebar, then focus moves).

A run with no log line is a control, not a pass: run case 1 again with a deliberate click on "Albums" afterward and confirm a `nav` line appears, so the logging is proven live.

- [ ] **Step 3: Write the finding**

Record in `claude-spinner/STATUS.md`'s decision log which trigger moves which selection, with the stack frames that did it. If the cause is a key event reaching TrackList's `onKeyPress` or a List's arrow handling through Claude Spinner's own sidebar focus, the fix belongs in the showcase (focus scoping), not in App Kit. Write that fix as its own follow-up task in `TASKS.md`.

- [ ] **Step 4: Remove the logging, commit the finding**

```bash
git checkout -- "claude spinner/AppKitShowcase.swift"
git commit -m "Record what moves the App Kit tab's selections after launch

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" -- STATUS.md TASKS.md
```

---

### Task 8: Publish and record

**Files:**
- Modify: `design-system/project/design-system.json` (`lastChange`, at publish time only)
- Modify: `STATUS.md`

- [ ] **Step 1: Publish with the recorded URL**

Follow `README.md`'s publish rule: the URL comes from `artifacts.json`, never a bare publish. `index.d.ts` needs `{"from": "...", "contentType": "text/plain"}`. The index goes last, re-read right before, with `lastChange.note` naming this plan.

- [ ] **Step 2: Read back**

Read the published artifact and confirm the SidebarList README carries `appearsActive` and the CSS carries `--music-sidebar-glyph-inactive`.

- [ ] **Step 3: Record and commit**

Add a decision-log entry to `STATUS.md` naming the three surviving review findings, the three dropped ones and why, and the publish version.

```bash
git commit -m "Record the Music review fixes publish

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" -- design-system/project/design-system.json STATUS.md
```

Open the `appkit-review-fixes` PR in claude-spinner only if asked.
