# Button

Starts an action; verb first, sentence case ("Retry sync", "Import clips").

- `primary` (clay fill, `on-clay` text): at most one per view, for the thing the screen is for.
- `secondary` (surface, `edge` border): everything else. The default.
- `plain` (clay text, no fill): low-weight inline actions like "Show all".
- `destructive` (`bad` text): Delete, Remove. Confirm in the UI before acting.
- Height is `touch` (44px), radius `radius-md`. The consumer provides the label and `onClick`.
- SwiftUI: a `ButtonStyle` with `.frame(minHeight: 44)`, `RoundedRectangle(cornerRadius: 10)`; primary is `.tint(.clay)` with `.borderedProminent`.
