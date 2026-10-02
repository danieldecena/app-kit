# HeroCard

The large card at the top of Music's Home: artwork filling the whole card, with
an eyebrow and a title set over it at the bottom-left, and a slot top-right where
Music puts its own wordmark.

## 3:4 is the spec, the size is not

Width over height measured 0.751, 0.748 and 0.748 across three window widths,
while the card itself went from 257.5x343pt to 271.0x362.5pt as the sidebar
moved. So `HeroCard` takes a `width` and derives the height; see
[Shelf](../Shelf/README.md) for the same decision on the row around it.

Caption geometry, measured from the same capture: 18.5pt in from the left edge,
title sitting 22.5pt up from the bottom, eyebrow 7.5pt above the title. The CSS
rounds to 18px and lets the line boxes set the rest, so the title sits a little
lower than Music's; the badge inset (14px) and the eyebrow's 82% alpha are the
component's own and were not measured.

## The scrim is ours, not Music's

Music's heroes are commissioned artwork that happens to carry white text. The one
measured here puts white on `#F4B63F`, which is **1.81:1** -- nowhere near the
4.5:1 this design system asserts everywhere else. Music gets away with it because
Apple controls the image.

An adopting app does not, so the card carries its own bottom gradient and the
white text sits on that rather than on the artwork. The cost is a card that is
slightly darker at the bottom than Music's; the alternative is text whose
legibility depends on an image nobody checked.

The stops were picked against the worst artwork there is, a pure white image,
and checked rather than eyeballed:

| | scrim alpha at that band | contrast over white artwork |
|---|---|---|
| title | 0.74 | **10.0:1** |
| eyebrow (itself 82% white) | 0.71 | **6.5:1** |

A gentler first attempt, `0.72` ramping to `0.38` by 22%, measured **3.16:1** at
the eyebrow and was replaced.

The `badge` slot has **no** scrim behind it, because Music's wordmark sits on
open artwork. Anything placed there has to be legible unaided.

## `tone` does not read the artwork

Nothing in this pipeline reads a colour at runtime. `tone` is a colour the app
derived itself; the card only shows it while the artwork loads and behind a
transparent one.

## SwiftUI

Lifted from `build/source/music-components-spike.swift`, which is compiled
against `swift/AppKit.swift` and rendered in a real window before it ships.
Edit the spike, not this block.

```swift
/// Full-bleed artwork at 3:4 with the caption INSIDE the card. The ratio is the
/// spec; the size is not.
struct HeroCard: View {
    let art: LinearGradient
    let eyebrow: String
    let title: String
    var width: CGFloat = 258

    var body: some View {
        ZStack(alignment: .bottomLeading) {
            art
            // The scrim is ours, not Music's: Music's heroes are commissioned to
            // carry white text, an adopting app's artwork is not.
            LinearGradient(stops: [
                .init(color: .black.opacity(0.78), location: 0.00),
                .init(color: .black.opacity(0.70), location: 0.16),
                .init(color: .black.opacity(0.30), location: 0.34),
                .init(color: .black.opacity(0.00), location: 0.56),
            ], startPoint: .bottom, endPoint: .top)
            VStack(alignment: .leading, spacing: 2) {
                Text(eyebrow).font(.caption2).foregroundStyle(.white.opacity(0.82))
                Text(title).font(.system(size: 15, weight: .semibold)).foregroundStyle(.white)
                    .lineLimit(1)
            }
            .padding(18)
        }
        .frame(width: width, height: width / 0.75)    // 3:4
        .clipShape(RoundedRectangle(cornerRadius: 14, style: .continuous))
    }
}
```
