# TrackList

Music's song table: the playlist and album view.

## The highlight is a pill, not a row fill

This is the whole component, and getting it wrong reads as not-Music instantly.

| | |
|---|---|
| row height | **56pt** (AX and pixels agree) |
| pill | **1238 x 45pt**, x 310.0-1547.5 |
| inset | **40pt** each side of the 1318pt content width |
| vertical | **5.5pt** above and below, inside the 56pt row |
| radius | **~6pt** |

Hover and selection are the *same* pill with different fills, which is one
component with a state rather than two layouts. The pill is a pseudo-element here
so the inset does not move the cells.

## Three reds, none derived from another

| | light | dark |
|---|---|---|
| accent | `#FA233B` | `#FA2E48` |
| selection | `#DC1229` | `#CC132D` |

App Kit's convention is the accent stepped 20% toward black, which from `#FA2E48`
would give `#C8253A`. Music uses `#CC132D`. So `music-select` is a measured value
and not a derivation, and the same goes the other way.

## Header

`caption-2` uppercase. Music's own headers read "Song / Artist / Album" in
sentence case and the capture records a 32pt header row that this component does
not set. Both are departures, not readings.

## Inactive selection is the normal state for a monitor app

macOS greys the selection when the window is not key, and this caught the capture
out: the first "selected" shot read red because Music was still key, and a later
shot of the same state read grey because it was not. Pass `windowInactive` and
the fill becomes `music-select-inactive` with the labels back to normal ink.
Music's inactive label colour was not measured; normal ink is the macOS default
and clears 4.5:1 on that fill, which `music-ink-soft` does not (3.31:1), so
secondary cells step to `music-ink-soft-on-fill` under any fill.

## Keyboard

A `grid` takes **one** tab stop, not one per row -- a 200-track playlist would
otherwise be 200 of them. The selected row holds it, falling back to the first.

| key | |
|---|---|
| Up / Down | move focus **and** the selection together |
| Home / End | first and last row |
| Enter, Space | play, which is what Music does |

Focus moves with the selection rather than trailing it, or the ring stays on the
row you left and a screen reader never hears the change. Double-click also plays,
for the pointer.

## Columns are configuration

The measured playlist has seven columns and no Album; an earlier capture had one.
So the column set is passed in, and pixel-derived column positions recorded for
one capture describe *that* column set rather than contradicting another.

### Two measured columns this component cannot place

The star sits at x=270 and the "..." menu runs to 1588, while the pill spans
310.0-1547.5. So in Music both live **outside** the pill, in the 40pt gutters.
The grid here starts after that 40px padding, so a star or menu column passed in
`columns` renders inside the pill instead. Shipped that way deliberately rather
than silently dropping them: the frames below are the record of what Music does,
and matching it needs a gutter slot this component does not have yet.

Measured column frames for the seven-column playlist, window-relative:

| Column | x | width |
|---|---|---|
| favorited star | 270.0 | 40.0 |
| artwork | 310.0 | 57.0 |
| Song | 367.0 | 593.5 |
| Artist | 960.5 | 468.5 |
| cloud / download | 1429.0 | 16.0 |
| Time | 1445.0 | 58.0 |
| "..." menu | 1503.0 | 85.0 |

## SwiftUI

Lifted from `build/source/music-components-spike.swift`, which is compiled
against `swift/AppKit.swift` and rendered in a real window before it ships.
Edit the spike, not this block.

```swift
struct Track: Identifiable {
    let id: Int
    let starred: Bool
    let art: Color
    let song: String
    let artist: String
    let time: String
}

/// Music's song table. The highlight is a rounded inset PILL, not a row fill.
struct TrackList: View {
    let rows: [Track]
    @Binding var selection: Int?
    var windowInactive: Bool = false
    var onPlay: (Int) -> Void = { _ in }
    @FocusState private var focused: Bool

    private func fill(_ id: Int) -> Color {
        guard id == selection else { return .clear }
        return windowInactive ? Color.Kit.musicSelectInactive : Color.Kit.musicSelect
    }
    private func ink(_ id: Int, soft: Bool) -> Color {
        if id == selection && !windowInactive { return Color.Kit.onMusicSelect }
        if id == selection && windowInactive { return soft ? Color.Kit.musicInkSoftOnFill : Color.Kit.musicInk }
        return soft ? Color.Kit.musicInkSoft : Color.Kit.musicInk
    }

    var body: some View {
        VStack(spacing: 0) {
            ForEach(rows) { r in
                HStack(spacing: 12) {
                    Text(r.starred ? "\u{2605}" : " ")
                        .foregroundStyle(Color.Kit.musicStar).frame(width: 16)
                    RoundedRectangle(cornerRadius: 4, style: .continuous)
                        .fill(r.art).frame(width: 40, height: 40)
                    Text(r.song).foregroundStyle(ink(r.id, soft: false))
                    Spacer()
                    Text(r.artist).foregroundStyle(ink(r.id, soft: true))
                        .frame(width: 160, alignment: .leading)
                    Text(r.time).foregroundStyle(ink(r.id, soft: true))
                        .monospacedDigit().frame(width: 48, alignment: .trailing)
                }
                .font(.subheadline)
                .padding(.horizontal, 12)
                // 45pt pill inside a 56pt row: 5.5pt above and below.
                .frame(height: 45)
                .background(RoundedRectangle(cornerRadius: 6, style: .continuous).fill(fill(r.id)))
                .padding(.horizontal, 40)   // the measured inset
                .frame(height: 56)
                .contentShape(Rectangle())
                .onTapGesture { selection = r.id }
                .accessibilityElement(children: .combine)
                .accessibilityAddTraits(r.id == selection ? [.isSelected] : [])
            }
        }
        // One focus target for the whole table, with the arrows moving inside
        // it -- a row-per-tab-stop would be 200 stops on a real playlist. This
        // mirrors the keyboard model the web component documents.
        .focusable()
        .focused($focused)
        .onMoveCommand { direction in
            guard let current = selection ?? rows.first?.id,
                  let i = rows.firstIndex(where: { $0.id == current }) else { return }
            switch direction {
            case .up:   selection = rows[max(0, i - 1)].id
            case .down: selection = rows[min(rows.count - 1, i + 1)].id
            default:    break
            }
        }
        // Return plays, which is what Music does.
        .onKeyPress(.return) {
            if let s = selection { onPlay(s); return .handled }
            return .ignored
        }
        .accessibilityLabel("Tracks")
    }
}
```
