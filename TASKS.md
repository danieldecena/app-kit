## Tasks

- [x] Slice 5: HeroCard -- 3:4 ratio, caption over the art, scrim checked against white artwork
- [x] Slice 4: Shelf + ArtworkCard -- 20/16pt gap breakpoint, square art, 37pt caption
- [x] Slice 3: SidebarList -- 32pt rows, active/inactive selection, thumbnails, SwiftUI recipe in the README

- [x] Dark CTA button fill: #FA2E48, which is exactly the dark accent, so no separate token is needed
- [ ] [you] Capture a row with the mouse held down, to settle whether a pressed state exists
- [ ] [you] Click the spike window, then it self-captures: .tint vs the ACTIVE selection. Four attempts incl. in-process NSApp.activate all report isKeyWindow=false -- macOS denies focus to a shell-launched binary, so this needs a human click
- [ ] [you] Capture the dark transport button with the window inactive, for music-primary-inactive
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
