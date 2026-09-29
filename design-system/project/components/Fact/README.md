# Fact

One label and its value, in the two-column grid of Footage Library's detail cards.

- Label in `caption` (12/16), `ink-soft`, proportional. Value in `fact` (SF Mono 12/16), `ink`, tabular figures, so values line up down a panel.
- Put the rows in `<dl class="dc-facts">`: labels size to the longest, 18 between the columns, `space-4` (8) between rows.
- A missing value reads "not recorded" in `ink-faint`: say it is absent rather than hiding the row, so the card keeps its shape. `muted` sets any other value in `ink-faint` (a placeholder, an inherited default).
- `oneLine` keeps a long value (a path, a hash, a device ID) to one line and truncates in the middle, since the tail is what tells two apart. The full value is the tooltip.
- Values are data, not prose: no sentences, no trailing punctuation. Real units ("4.21 GB", "23.976 fps").

SwiftUI:

```swift
Grid(alignment: .leading, horizontalSpacing: 18, verticalSpacing: 8) {
    GridRow {
        Text(label).font(.caption).foregroundStyle(.secondary)
        Text(value).font(Font.Kit.factValue).foregroundStyle(muted ? .tertiary : .primary)
            .lineLimit(oneLine ? 1 : nil).truncationMode(.middle)
            .textSelection(.enabled)
    }
}
```

With `oneLine`, add `.help(value)` and a Copy item in `.contextMenu`, since the middle of the value is hidden.
