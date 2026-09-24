# Panel

Groups related content as a `surface` on the `ground`, the main way screens are divided.

- `radius-lg` (14), `space-6` padding, `space-5` inner gap; no border, no shadow.
- Title in `title-3`; optional meta (count, freshness) in `footnote` `ink-soft` on the right.
- Nest controls one radius step down (`radius-md`). Stack panels with `space-7` between them.
- SwiftUI: `.background(Color.surface, in: .rect(cornerRadius: 14))` on a `ground` screen, or an inset-grouped `List`.
