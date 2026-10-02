## Tasks



- [x] SwiftUI recipes for the five Music components, compiled and AX-checked

- [x] Shelf arrow-key pitch: not a bug, mandatory snap corrects it
- [x] MiniPlayer line ends 36.8pt long: Music's 36pt hit frames set 572
- [x] Sidebar selection: neutral in every state, red was the track row's
- [x] SidebarList takes its own two neutral selection tokens, CSS and SwiftUI
- [x] Row mid-press: no visual of its own (dark); selection fires on mouse-up
- [ ] [you] Contextual toolbar: needs its own capture pass
- [ ] [you] Window chrome: deferred to the adopting app

## Completed

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
