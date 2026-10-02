# SidebarList

A Mac source list, as in Music for macOS: sections with small grey headers and an
optional trailing action, rows carrying either a tinted glyph or a playlist
thumbnail, and a rounded selection fill.

## Geometry

| | | |
|---|---|---|
| row height | **32pt** | measured, AX and pixels agree |
| section header | **19pt** | measured, AX |
| selection | a rounded fill inset within the row | **shape measured, size not** |

Only the first two numbers are measured. The sidebar's selection fill, its
radius, its hover, the 16px glyph and thumbnail, the 600 weight on the selected
row, the 50px footer and the 24px avatar are all the component's own: the
capture records the sidebar's row rhythm and its inactive behaviour, not a
selection frame. The fills reuse `music-select` and `music-hover`, which were
measured on **track rows**, on the reasoning that macOS draws one selection
colour per window rather than one per list. That is a reasonable inference and
it is not an observation.

The sidebar's **width is not a token**. It is a user-resizable split, so ship a
default and a minimum and let the person drag it. Card and shelf sizes elsewhere
in the variant derive from the width this leaves, so hard-coding it is wrong
twice over.

## The material is not CSS

The real sidebar is a vibrant material that samples the **desktop behind the
window**. `glass` here is a `backdrop-filter` stand-in that samples the page, and
it cannot reproduce that; this preview approximates, it does not match.

In SwiftUI you get the real thing for free from `.listStyle(.sidebar)`, as long
as you set **no** background on the `List`: measured against Music, the stock
material lands within 2 units of Music's own sidebar, and setting a background
defeats it. The recipe below does exactly that, and puts the selection fill on
the rows instead.

Two SwiftUI behaviours worth knowing before you build this natively:

- Sidebar selection draws the **system accent**, not your colour, and `.tint()`
  on the `List` does not change it. Measured: with the list focused the selected
  row fills `#007AFF`, the system accent, while `.tint(Color.Kit.musicSelect)`
  was set to `#CC132D`. Matching Music's red needs an explicit row background.
- **A key window is not a focused list**, and the difference is visible. The same
  row fills `#434346` when the window is key but focus is elsewhere -- a neutral
  grey that is neither the accent nor the tint. An earlier reading of this spike
  took that grey as evidence about `.tint`; it is evidence about focus. Check
  which of the two you are looking at before concluding anything about colour.
- `.foregroundStyle` on a `Label` tints the symbol **and** the text. Music tints
  only the symbol. Build the Label from explicit `Text`/`Image` closures and
  tint the `Image`.

## Inactive windows

Pass `windowInactive` when the window is not key, and the selection switches to
`music-select-inactive`. macOS does this itself natively. It is not an edge
case: a monitor app is unfocused most of the time, so this is the state most
users see most often.

## Keyboard

Arrow keys move the selection, matching SegmentedControl.

## SwiftUI

Lifted from `build/source/music-components-spike.swift`, which is compiled
against `swift/AppKit.swift` and rendered in a real window before it ships.
Edit the spike, not this block.

```swift
/// A Mac source list with Music's RED selection, which is the part
/// `.listStyle(.sidebar)` will not give you: sidebar selection draws the system
/// accent and `.tint()` does not override it (measured: #007AFF against a tint
/// of #CC132D). So the rows draw their own background and the List supplies
/// only the vibrancy.
struct SidebarRow: Identifiable {
    let id: String
    let label: String
    let symbol: String
}

struct SidebarList: View {
    let sections: [(String?, [SidebarRow])]
    @Binding var selection: String?
    var windowInactive: Bool = false

    private func fill(_ id: String) -> Color {
        guard id == selection else { return .clear }
        return windowInactive ? Color.Kit.musicSelectInactive : Color.Kit.musicSelect
    }
    private func ink(_ id: String) -> Color {
        id == selection && !windowInactive ? Color.Kit.onMusicSelect : Color.Kit.musicInk
    }
    /// Music tints the SYMBOL and leaves the label in normal ink, which is why
    /// the row is built from Text and Image rather than a Label: a
    /// .foregroundStyle on a Label would tint both.
    private func glyph(_ id: String) -> Color {
        if id == selection { return windowInactive ? Color.Kit.musicInkSoftOnFill : Color.Kit.onMusicSelect }
        return Color.Kit.musicAccent
    }

    var body: some View {
        List(selection: $selection) {
            ForEach(sections.indices, id: \.self) { i in
                let (header, rows) = sections[i]
                Section {
                    ForEach(rows) { r in
                        HStack(spacing: 8) {
                            Image(systemName: r.symbol)
                                .foregroundStyle(glyph(r.id)).frame(width: 16)
                            Text(r.label).foregroundStyle(ink(r.id))
                            Spacer(minLength: 0)
                        }
                        .frame(height: 32)                       // measured
                        .padding(.horizontal, 8)
                        .background(RoundedRectangle(cornerRadius: 6, style: .continuous).fill(fill(r.id)))
                        .listRowInsets(EdgeInsets())
                        .listRowBackground(Color.clear)          // let the row's own fill show
                        .tag(r.id)
                    }
                } header: {
                    if let header { Text(header).foregroundStyle(Color.Kit.musicInkSoft) }
                }
            }
        }
        .listStyle(.sidebar)        // the vibrancy; set NO background
        .scrollContentBackground(.hidden)
    }
}
```
