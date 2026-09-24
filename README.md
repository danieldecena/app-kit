# App Kit

SwiftUI on Apple's own neutrals and system colours: capsule buttons tinted
like Notes highlights, SF Pro Rounded figures, and glass for controls that
float over content. It started as the Decena Apps design system (WA Fish Map,
Footage Library, Claude Spinner) and was renamed App Kit on 24 Sep 2026.

| Kit | For | Where |
|---|---|---|
| **App Kit** | SwiftUI apps on Mac, iPhone, iPad and Watch | this repo |
| **Artifact Kit** | web pages and claude.ai artifacts, same palette | `~/developer/artifact-kit` |
| **Terminal Kit** | the macOS Terminal look | `~/developer/terminal-kit` |

## What is here

```
swift/AppKit.swift        Color.Kit.* and Font.Kit.*: drop into an app target
design-system/project/    the published design system (tokens, README, components)
build/app_build.py        regenerates both from the Decena snapshot in build/source/
artifacts.json            which artifact this publishes to
```

## Use in an app

Prefer the system first: `Color.accentColor`, `.primary`, `.secondary`,
`.buttonStyle(.bordered)` with `.tint(...)` for tinted buttons,
`.borderedProminent` for the one filled action, `.glass` for controls over
content, `Picker(...).pickerStyle(.segmented)`. Reach for `Color.Kit.surface`,
`Color.Kit.hlMint` and friends only where you draw your own surfaces.

## Publish

Publish `design-system/project/` to the URL in `artifacts.json`, the index
(`design-system.json`) last, re-read right before, with `lastChange` set.
