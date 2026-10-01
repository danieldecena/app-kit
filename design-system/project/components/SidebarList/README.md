# SidebarList

A Mac source list, as in Music for macOS: sections with small grey headers and an
optional trailing action, rows carrying either a tinted glyph or a playlist
thumbnail, and a rounded selection fill.

## Geometry

Measured from the Music app, not designed.

| | |
|---|---|
| row height | 32pt |
| section header | 19pt |
| selection | rounded fill inset within the row |

The sidebar's **width is not a token**. It is a user-resizable split, so ship a
default and a minimum and let the person drag it. Card and shelf sizes elsewhere
in the variant derive from the width this leaves, so hard-coding it is wrong
twice over.

## The material is not CSS

The real sidebar is a vibrant material that samples the **desktop behind the
window**. `glass` here is a `backdrop-filter` stand-in that samples the page, and
it cannot reproduce that; this preview approximates, it does not match.

In SwiftUI you get the real thing for free:

```swift
NavigationSplitView {
    List(selection: $selection) { ... }
        .listStyle(.sidebar)          // real vibrancy; set NO background
} detail: { ... }
```

Measured against Music: stock `.listStyle(.sidebar)` with no background set lands
within 2 units of Music's own sidebar. **Setting a background defeats it.**

Two SwiftUI behaviours worth knowing before you build this natively:

- Sidebar selection draws the **system accent**, not your colour. Matching
  Music's red needs an explicit override.
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
