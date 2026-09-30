# Panel

Groups related content on a `surface` card, one step off the `ground`: Footage Library's detail card.

- `radius-lg` (14), `space-6` (16) padding, 10 between children. No border and no shadow; the surface step is the separation.
- `title` is the `panel-title` style: 11/13 semibold, uppercase, +0.8 tracking, in `ink-faint`. It names the card ("Capture", "Storage"), it is not a headline. `meta` sits on the trailing edge in `ink-soft` 13/18 for freshness or counts. Both are optional.
- `tone` marks a slot, from Footage's Charts plates. Pair it with an Eyebrow that says the same thing in words, since an outline alone is colour only.
  - `act`: needs the person (blocked, failed). A `stroke-outline` (1.5) ring in `warn`.
  - `live`: work in progress. The same ring in `accent`.
  - `empty`: nothing yet. No fill, a `stroke-dash` (6 on, 4 off) outline in `ink-faint`.
- Content goes straight in: Fact rows in a `.dc-facts` list, `.dc-row` / `.dc-stack` for layout. Nest a `.dc-list` for rows, not another Panel.
- Equal tiles: put panels in `.dc-panel-grid`, adaptive columns at least 250 wide, `space-5` (12) apart, every card as tall as the tallest in its row. Stack single panels `space-7` apart.

SwiftUI:

```swift
VStack(alignment: .leading, spacing: 10) {
    Text(title.uppercased()).font(Font.Kit.panelTitle).tracking(CGFloat.Kit.trackingPanelTitle).foregroundStyle(.tertiary)
    content
}
.padding(16)
.frame(maxWidth: .infinity, alignment: .leading)
.background(.background.secondary, in: RoundedRectangle(cornerRadius: 14, style: .continuous))
// act / live: .overlay { RoundedRectangle(cornerRadius: 14, style: .continuous).strokeBorder(color, lineWidth: CGFloat.Kit.strokeOutline) }
// empty: no background; .strokeBorder(.tertiary, style: StrokeStyle(lineWidth: CGFloat.Kit.strokeOutline, dash: CGFloat.Kit.strokeDash))
```

The equal-tile grid (Claude Spinner's detail pane): a custom `Layout` (`TileGrid(minimum: 250, spacing: 12)`) that fits as many columns as it can, measures each card at the column width, and places every card in a row at that row's tallest height; the card itself takes `.frame(maxHeight: .infinity, alignment: .topLeading)`. `LazyVGrid` can't do it, since it leaves each cell at its own height, and equalising across the whole grid instead stretches a short card to match a chart two rows away. On the web, `.dc-panel-grid` gets the same result from CSS grid's default row stretch.
