# Button

Starts an action; verb first, sentence case ("Retry sync", "Import clips"). Capsules, as in iOS 26, in the Notes highlight colours.

- `tinted` (the default): a translucent wash of the tint (`accent-wash`, 12% / 20%) with `accent-ink` text. SwiftUI: `.buttonStyle(.bordered)` with `.tint(...)`.
- `filled`: at most one per view, the thing the screen is for. `accent-fill` with `on-accent`. SwiftUI: `.buttonStyle(.borderedProminent)`.
- `gray`: the system `fill` in `ink`, for Cancel and neutral actions. SwiftUI: `.bordered` with `.tint(.gray)`.
- `plain`: text in the tint, no fill, for inline actions like "Show all". SwiftUI: `.borderless`.
- `glass`: controls floating over content (maps, photos, video). SwiftUI: `.buttonStyle(.glass)` on iOS 26 and macOS 26.
- `destructive`: Delete, Remove, in system red; never `filled` by default. SwiftUI: `Button(role: .destructive)`.
- `tint`: `accent` (default), `purple`, `pink`, `orange`, `mint`, `blue`. Every label passes 4.5:1 on its fill.
- Height is `touch` (44px), `radius-pill`. The consumer provides the label and `onClick`.
