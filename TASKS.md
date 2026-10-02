## Tasks

- [x] Render the spike and run accessibility-review on the 55pt pill
- [x] Measure Music's inactive sidebar ink in both appearances -- edf3df3
- [x] Add inactive sidebar ink and glyph tokens -- dda4658
- [x] SidebarList/TrackList read appearsActive, dim whole sidebar -- 1a53795
- [x] Web SidebarList dims every row when inactive -- dda4658
- [x] Large page title in the spike window -- (this commit)
- [ ] Spinner tab: re-copy, title, overflowing shelves
- [ ] Find what moves the tab's selections after launch
- [ ] Publish the Music review fixes and record
- [ ] Shelf draws the chevron only when it has a See All

## Completed

### 2026-10-02 — cleared from Active
- [x] Publish provenance and token corrections to the artifact -- v58
- [x] TrackList pill height follows the row, 55pt on artwork rows -- 0fcbf9a
- [x] Build design runbook artifact for the measure-to-publish process -- fe8bdbe
- [x] Draw the TrackList focus ring on the pill, not under it -- a92945a
- [x] Publish the TrackList pill and focus ring to the artifact -- v61
- [x] Add the design runbook binding to the terminal-kit register -- terminal-kit 4aaa164
- [x] Check the TrackList focus ring in WebKit -- passes, WebKit 26.6
- [x] Fix TrackList preview: inactive list shows no selection -- 3453e65
- [x] Publish the TrackList preview fix and WebKit note -- v63

- [x] Build swatch-scan tool with key-state witness and controls -- 89b8e3d
- [x] Witness window state of every capture behind a provenance row -- d3233a0
- [x] Sample inactive fill, labels, Play label, capsule from witnessed captures -- 38cf667
- [x] Measure selected-row shape by appearance and page type -- a8e1d32
- [x] Write results into MUSIC_PROVENANCE and tokens, rebuild, stop before publish -- fd89c70
- [x] Capture dark selected row with the window not key -- 0c654fb
- [x] SwiftUI recipes for the five Music components, compiled and AX-checked
- [x] Shelf arrow-key pitch: not a bug, mandatory snap corrects it
- [x] MiniPlayer line ends 36.8pt long: Music's 36pt hit frames set 572
- [x] Sidebar selection: neutral in every state, red was the track row's
- [x] SidebarList takes its own two neutral selection tokens, CSS and SwiftUI
- [x] Row mid-press: no visual of its own (dark); selection fires on mouse-up
- [x] Contextual toolbar: decided not a component, per-page content
- [x] Window chrome: decided, belongs to the adopting app
- [x] Measure Music's shelf and song-row trailing edges, fix spike if they differ -- 4a1c9a8
- [x] MiniPlayer README: record colour-only toggle and pointer-sized frames -- 3a73285

### 2026-10-01 — cleared from Active

- [x] Slice 6 spike gate: MiniPlayer judged against a real material, passes
- [x] Close eight bug-hunt findings: caption clipping, TrackList keyboard, grid roles, sidebar focus, toggle contradiction, shelf list role, unasserted css anchors, unfailable gate check
- [x] Slice 7: document and publish -- design system artifact at v28
- [x] TrackList -- taken into this plan rather than deferred; pill highlight, configurable columns
- [x] Slice 6: MiniPlayer -- 700x54 stadium capsule, progress line scoped to the now-playing group
- [x] Slice 5: HeroCard -- 3:4 ratio, caption over the art, scrim checked against white artwork
- [x] Slice 4: Shelf + ArtworkCard -- 20/16pt gap breakpoint, square art, 37pt caption
- [x] Slice 3: SidebarList -- 32pt rows, active/inactive selection, thumbnails, SwiftUI recipe in the README
- [x] Dark CTA button fill: #FA2E48, which is exactly the dark accent, so no separate token is needed
- [x] .tint does NOT reach the sidebar selection: a key, active window fills #434346, a neutral grey. Answered without a human click; the "macOS denies focus" note is retracted as too strong
- [x] Verify the Home AX dump was complete -- depth 9 reports no truncation; card size turned out to track the resizable sidebar width
- [x] Slice 2: 11 music-* tokens added, gate extended to 29 pairs plus an orientation check
- [x] Slice 2: WCAG contrast assertion in app_build.py -- 24 pairs, proved by mutation, survives python -O
- [x] Slice 2: SwiftUI spike -- ground-window, select and hover render exactly; sidebar is the stock material within 2 units
- [x] Confirm the app_build.py invocation reproduces the tree byte-for-byte
- [x] Write a CLAUDE.md for app-kit (build, publish, component pattern, design skills)
- [x] Slice 1: capture harness, AX dump, motion tracker, state finder
- [x] Slice 1: measure colour, geometry and motion in both appearances
- [x] Write READMEs for SegmentedControl, Panel, Highlight -- 0357bf2
- [x] Tokenize tint palette and gray hover -- b567bc5
- [x] Emit type styles and motion tokens -- cf065a5
- [x] Add arrow-key navigation to SegmentedControl -- 854ddcb
- [x] Port Footage detail-card patterns: Fact, Eyebrow, Toolbar, Panel -- 68565a7
- [x] Sync Panel grid and docs to per-row tiles -- de84451
- [x] Publish Footage patterns to the App Kit artifact -- v19
- [x] StatTile attention ring moves to warn -- v20
