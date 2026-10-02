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
selection frame. The hover reuses `music-hover`, measured on track rows.

**The selection is neutral, not red.** An earlier version reused `music-select`
on the reasoning that macOS draws one selection colour per window, and that
inference was wrong: `music-select` is the *track row's* red, and the sidebar
never draws it. Observed in Music, key window, in both appearances, with the
click driven by the agent and the pointer parked off the row: the fill is a
translucent grey, `music-sidebar-select` (white at 13.4% in dark, black at 9.3%
in light), and `music-sidebar-select-inactive` (6.3% and 4.5%) when another app
is frontmost. Pressing and focus change nothing, and the glyph keeps its accent
tint on the selected row. The label goes to pure `on-music-glass` at weight 600.
The alphas are alphas because the same fill lands on different greys over
different backdrops, and the 6.3% reproduced across two (`#101010` to
`#1F1F1F`, `#252525` to `#333333`). The build composites each over the backdrop
it was measured on and fails if the result or the label ratio drifts.

A red sidebar reading, `#FA2E48` in dark with the list focused, was recorded
earlier from a capture that no longer exists. It could not be reproduced here by
clicking, by holding the mouse down, or by moving keyboard focus, so it is not
used.

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

- A *focused* SwiftUI sidebar draws the **system accent** on the selected row,
  and `.tint()` on the `List` does not change it. Measured: with the list focused
  the row fills `#007AFF` while `.tint` was set to `#CC132D`. Music never draws
  an accent there, so matching it needs an explicit row background, which the
  recipe supplies.
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
`music-sidebar-select-inactive`. macOS does this itself natively. It is not an edge
case: a monitor app is unfocused most of the time, so this is the state most
users see most often.

## Keyboard

Arrow keys move the selection, matching SegmentedControl.

## SwiftUI

Lifted from `build/source/music-components-spike.swift`, which is compiled
against `swift/AppKit.swift` and rendered in a real window before it ships.
Edit the spike, not this block.

```swift
/// A Mac source list with Music's NEUTRAL selection: a translucent grey, not the
/// red. A focused `.listStyle(.sidebar)` draws the system accent instead
/// (measured: #007AFF, and `.tint()` does not override it), which Music never
/// does, so the rows draw their own background and the List supplies only the
/// vibrancy. The List is given NO `selection:` binding for the same reason: its
/// native highlight would draw under ours and the two stack (measured: dark
/// `#555456` against Music's `#434346`). The cost is that the List no longer
/// handles arrow keys, so a real app should add `.onMoveCommand` if it needs them.
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
        return windowInactive ? Color.Kit.musicSidebarSelectInactive : Color.Kit.musicSidebarSelect
    }
    private func ink(_ id: String) -> Color {
        id == selection && !windowInactive ? Color.Kit.onMusicGlass : Color.Kit.musicInk
    }
    /// Music tints the SYMBOL and leaves the label in normal ink, which is why
    /// the row is built from Text and Image rather than a Label: a
    /// .foregroundStyle on a Label would tint both.
    private func glyph(_ id: String) -> Color {
        if id == selection && windowInactive { return Color.Kit.musicInkSoftOnFill }
        return Color.Kit.musicAccent
    }

    var body: some View {
        List {
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
                        .contentShape(Rectangle())
                        .onTapGesture { selection = r.id }
                        .accessibilityAddTraits(r.id == selection ? .isSelected : [])
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
