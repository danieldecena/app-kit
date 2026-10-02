# Button

Starts an action; verb first, sentence case ("Retry sync", "Import clips"). Capsules, as in iOS 26, in the Notes highlight colours.

- `tinted` (the default): a translucent wash of the tint (`accent-wash`, 12% / 20%) with `accent-ink` text. SwiftUI: `.buttonStyle(.bordered)` with `.tint(...)`.
- `filled`: at most one per view, the thing the screen is for. `accent-fill` with `on-accent`. SwiftUI: `.buttonStyle(.borderedProminent)`.
- `gray`: the system `fill` in `ink`, for Cancel and neutral actions. SwiftUI: `.bordered` with `.tint(.gray)`.
- `plain`: text in the tint, no fill, for inline actions like "Show all". SwiftUI: `.borderless`.
- `glass`: controls floating over content (maps, photos, video). SwiftUI: `.buttonStyle(.glass)` on iOS 26 and macOS 26.
- `destructive`: Delete, Remove, in system red; never `filled` by default. SwiftUI: `Button(role: .destructive)`.
- `tint`: `accent` (default), `purple`, `pink`, `orange`, `mint`, `blue`. Every label passes 4.5:1 on its fill.
- `music`: Music's transport button, for the Music variant only. Maximum contrast against the ground, so it INVERTS with appearance -- `#0E0E0E` with a white label in light, `#F3F3F3` with a black one in dark. Never the accent: App Kit's own `filled` convention would paint Play red, which reads as not-Music immediately. Add `data-window-inactive="true"` when the window is not key and the pill inverts again, to measured `#ECECEC` / `#2F2F30` with a `music-ink` label, rather than dimming.
- Height is `touch` (44px), `radius-pill`. The consumer provides the label and `onClick`.
