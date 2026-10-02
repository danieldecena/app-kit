# Spike Critique Follow-ups Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Settle the three findings a design critique of the SwiftUI spike render raised, by measuring Music first and changing only what Music contradicts.

**Architecture:** One measurement task decides whether the playlist row's trailing edge needs a change. One docs task records two accessibility notes in the MiniPlayer README. The third finding is closed as already documented. Every shipped file here is generated, so changes go in `build/app_build.py` or the spike, then through a scratch build.

**Tech Stack:** Python generator (`build/app_build.py`), SwiftUI spike (`build/source/music-components-spike.swift`), AX dump (`build/source/ax-dump.swift`), Music.app on the BetterDisplay virtual display.

**Spec:** the 2026-10-02 `/design:design-critique` of `spike2.png` (spike render, dark, after the MiniPlayer fix). It lived only in chat, so its three recommendations are restated here in "Findings and verdicts".

## Global Constraints

- Never hand-edit `design-system/project/**` or `swift/AppKit.swift`. Edit `build/app_build.py` or the spike, build to a scratch `<out>`, diff, copy.
- Build: `/opt/homebrew/bin/python3 build/app_build.py <src> <out>` with `<src>/project` a symlink to `build/source/decena-apps-2026-09-24`. Use `/opt/homebrew/bin/python3`, never bare `python3`.
- Files under `build/` need `git add -f`.
- Capture and drive Music off-screen: park it on the virtual display with `build/source/music-park.swift`, drive with `build/source/music-drive.swift`, and restore the user's cursor and frontmost app after each action. Never leave a window on the main screen.
- A check needs a known-bad and a known-good input before it is trusted, and a mutation must be asserted applied.
- No emoji and no em dashes in replies or generated docs.
- Publish only changed `project/` files, the index last with `lastChange` set, then read back by hash. Use the URL in `artifacts.json`.

## Findings and verdicts

1. **Sidebar section header looks misaligned (critique #1): withdrawn.** Music's AX dump (`scratchpad/ax.txt`, "Playlists" header `x=15`, row labels `x=54`) shows the header flush left at 15pt with labels at 54pt. The spike renders the header at about 14pt. It already matches. Record the decision, change nothing.
2. **Selected playlist row runs past the shelves' right edge (critique #2): real in the spike, unknown in Music.** Measured in `spike2.png`: pill 300.0 to 1123.0pt, hero cards 300.0 to 1114.0pt, episode cards 300.0 to 1112.0pt. The pill's right edge is the scroll content width minus 40; the shelves end 9pt short of it. Whether Music has the same mismatch is unmeasured, so Task 1 measures before changing anything.
3. **Opaque backing for the unplayed progress track (critique #3): already documented.** The MiniPlayer README states the 1.90:1 case and the remedy ("raise the unplayed alpha or back the line with an opaque strip"), and records the greys as Music's own. No change.

Extra accessibility notes from the critique that the README does not carry yet (Task 2): the shuffle and repeat on-state is colour only, and the transport frames are 28pt (Play 36), adequate for a pointer and short of 44pt for touch.

## File structure

- `build/source/music-capture.md`: Task 1 appends the measurement and the verdict.
- `build/source/music-components-spike.swift`: Task 1 changes it only if Music contradicts the spike.
- `build/app_build.py`: Task 2 adds the README notes (MiniPlayer README text lives here).
- `design-system/project/components/MiniPlayer/README.md`: generated, copied from the scratch build.
- `STATUS.md`: decision log entry covering all three verdicts.

### Task 1: Measure Music's row and shelf trailing edges

**Files:**
- Modify: `build/source/music-capture.md` (append a section)
- Modify (only if Music contradicts the spike): `build/source/music-components-spike.swift` (the `Shelf` or `TrackList` trailing padding)

**Interfaces:**
- Consumes: Music.app running; `build/source/ax-dump.swift` (`swift ax-dump.swift Music <maxDepth>`); `music-park.swift` (`vdmove`-style `<x> <y>` to place the main window).
- Produces: a recorded pair of numbers, the right edge of a Home shelf card and of a song row's highlight in the same window, from the same dump.

- [ ] **Step 1: Bring Music to a page that has both a shelf and a song table, off-screen**

Run (records the front app, un-minimizes, parks on the virtual display at its current origin, restores focus):

```bash
PRIOR=$(osascript -e 'tell application "System Events" to get name of first process whose frontmost is true')
osascript -e 'tell application "Music" to reopen'
sleep 1
swiftc build/source/music-park.swift -o "$TMPDIR/park" && "$TMPDIR/park" 1905 1237
osascript -e "tell application \"System Events\" to set frontmost of process \"$PRIOR\" to true"
```

Expected: `now at 1905.0 ...` printed, and the frontmost app is back to what it was.

- [ ] **Step 2: Dump the tree and pull the two edges**

```bash
swiftc build/source/ax-dump.swift -o "$TMPDIR/axd" && "$TMPDIR/axd" Music 14 > "$TMPDIR/ax-home.txt"
grep -n "AXScrollArea\|AXGroup .*w=[0-9]\{3\}" "$TMPDIR/ax-home.txt" | head -40
```

Read the dump for (a) a Home shelf card's `x + w` and (b) a song row's `x + w`, in the same window and the same scroll area. If the window is on a page without both, scroll with `music-drive.swift` (a click that does not change selection) and dump again. Do not use frames that clip against the window edge.

Expected: two right-edge numbers in window-relative points. If either is missing from the dump, write "unknown" and stop; do not infer.

- [ ] **Step 3: Control the measurement**

Known-good: confirm the dump also reports the song table's leading inset as 40pt from the content edge (the figure already recorded in `music-capture.md`). If that number is wrong, the dump is reading the wrong elements and the trailing numbers cannot be trusted.

- [ ] **Step 4: Decide**

- If Music's shelf and row right edges are equal (within 1pt): the spike is wrong. Edit the spike so the playlist block's trailing inset matches the shelf's, build, render with `<bin> --selfshot out.png`, and re-measure the pill's right edge against the card edge with the same pixel scan used for `spike2.png` (target: within 1pt).
- If they differ by about 9pt as in the spike: record "matches Music" and change nothing.
- If unknown: change nothing and say why.

- [ ] **Step 5: Record and commit**

Append a dated section to `build/source/music-capture.md` with the two numbers, the control, and the verdict. Then:

```bash
git add -f build/source/music-capture.md build/source/music-components-spike.swift
git commit -m "Spike: playlist row trailing edge against Music's shelf edge" -- build/source/music-capture.md build/source/music-components-spike.swift
```

Expected: if the spike changed, the build's `swiftc -typecheck` of the recipes passes and the regenerated READMEs differ only in the recipe blocks you touched.

### Task 2: Record the two MiniPlayer accessibility notes

**Files:**
- Modify: `build/app_build.py` (the MiniPlayer README text, near the "## Glyphs" section)
- Modify (copy from build): `design-system/project/components/MiniPlayer/README.md`
- Modify: `STATUS.md` (one decision log entry for all three verdicts)

**Interfaces:**
- Consumes: the existing README paragraph order, ending "## Glyphs" then "## SwiftUI".
- Produces: a new "## Known borrowings" section stating the colour-only toggle state and the 28pt pointer-sized frames.

- [ ] **Step 1: Add the section**

Insert before `## Glyphs` in the MiniPlayer README source in `build/app_build.py`:

```
## Known borrowings

Two things are Music's, recorded rather than corrected, the same call made for
`music-accent` and `music-star`:

- **A toggle's on-state is colour only.** Shuffle and Repeat go accent-red when
  on and stay white when off, with no second cue, which falls short of 1.4.1 for
  a colour-blind sighted user. The component exposes the state to assistive
  technology (`aria-pressed`; `accessibilityValue` in the SwiftUI recipe). An app
  that must meet 1.4.1 visually should add a dot or underline under an on toggle.
- **The hit frames are pointer-sized.** Transport buttons are 28pt (Play 36) and
  the trailing actions 36pt, as in Music. That is adequate for a pointer and
  short of 44pt for touch; an iPadOS adopter should enlarge the frames and accept
  that the group's 166-572 span then changes.
```

Keep the existing text style: no em dashes, `--` where the file already uses it.

- [ ] **Step 2: Build to scratch and confirm only the README changed**

```bash
A=$TMPDIR/ak-b5 && mkdir -p $A/src && ln -sfn "$PWD/build/source/decena-apps-2026-09-24" $A/src/project
/opt/homebrew/bin/python3 build/app_build.py $A/src $A/out
diff -rq $A/out/project design-system/project
diff -q $A/out/swift/AppKit.swift swift/AppKit.swift
```

Expected: the only differing file is `components/MiniPlayer/README.md` (plus the unrelated "Only in design-system/project: design-system.json" line), and the Swift file is identical.

- [ ] **Step 3: Copy, log, commit**

```bash
cp $A/out/project/components/MiniPlayer/README.md design-system/project/components/MiniPlayer/README.md
```

Add to `STATUS.md` under `### 2026-10-02`:

```
- Decided: the design critique of the spike render raised three items. The sidebar header alignment was withdrawn (Music's AX has the header at 15pt and labels at 54pt, the spike matches). The playlist row's trailing edge was settled by Task 1's measurement. The opaque progress backing was already documented in the MiniPlayer README. Two accessibility notes (colour-only toggle state, pointer-sized frames) went into a "Known borrowings" section.
```

```bash
git add -f build/app_build.py
git add STATUS.md design-system/project/components/MiniPlayer/README.md
git commit -m "MiniPlayer README: record the colour-only toggle and pointer-sized frames" -- build/app_build.py STATUS.md design-system/project/components/MiniPlayer/README.md
```

- [ ] **Step 4: Publish (optional, batched)**

A README-only change does not need its own artifact version. Publish it with the next change that touches `project/`, or immediately if the user asks, following the Global Constraints publish rule.

## Self-review

- **Spec coverage:** critique #1 is withdrawn with evidence, #2 is Task 1, #3 is closed as documented, and the two extra accessibility notes are Task 2. No critique item lacks a verdict.
- **Placeholders:** none; Task 1's outcome depends on a measurement, so it states each branch and its action instead of a guess.
- **Consistency:** the file names, the `music-park.swift` and `ax-dump.swift` usage, and the README section name "Known borrowings" are the same in every task.
