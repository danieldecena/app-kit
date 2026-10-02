# ArtworkCard

A square artwork with a two-line caption under it, as on Music's shelves and its
Albums grid. Exported separately from [Shelf](../Shelf/README.md) because the
grid is a real use: the card does not need a scrolling row around it.

## The caption is 37px and does not scale

Card height minus card width measured 37.0, 36.8 and 37.0pt across three window
widths. The artwork is square, so that difference is the caption, and it is the
one number three readings agreed on. Everything else about the card tracks the
width the sidebar leaves over.

So the card takes a `width` and derives nothing else. **Do not ship a card
size.** A component fixed at 188x225 is correct only at the one sidebar position
it was measured at, and the shelf owns the gap between cards rather than the card
owning its own margin.

| | |
|---|---|
| artwork | square, `radius-md` |
| caption | **37px** total, constant |
| title | `footnote` on `ink`, one line, ellipsised |
| subtitle | `caption-2` on `ink-soft`, one line, ellipsised |

## Why the subtitle is a size smaller than the title

37 is a measured total, so the type has to fit inside it rather than be clipped
to it. Two `footnote` lines are 18 + 18 = 36 and leave 1px for the gap under the
artwork; dropping the subtitle to `caption-2` makes it 6 + 18 + 13, which is
exactly 37.

The first attempt used `footnote` for both and let flex compress each line from
18 to 14, cutting the descenders off the subtitle. It read as correct only
because that preview's subtitle was in caps, which have no descenders. There is
no gap between the artwork and the caption for the same reason: a gap on top of
a 37px caption makes the difference 45 and breaks the measured invariant.

Music's own caption type was never measured, so this split is ours rather than
Apple's.

## States

| State | What it does |
|---|---|
| focus | a 2px `music-accent` ring, offset 2px, around the **artwork** rather than the whole card |
| press | not implemented -- Music's pressed state is unmeasured, and inventing one is the only place this component would stop tracing to a capture |

The card is a `<button>`, so it is a tab stop and takes `onClick`. Hover is
deliberately absent: the one hover captured was a TrackList row, not a card.

## Artwork and alt text

`art` is any image URL. The artwork renders `object-fit: cover` over
`surface-sunk`, so a non-square or still-loading image shows the sunk fill rather
than a stretched one. The `<img>` carries an empty `alt` on purpose: the title
beside it is the accessible name, and repeating it would make a screen reader say
the album twice.

Use [HeroCard](../HeroCard/README.md) instead when the caption belongs *over* the
art at 3:4.

## SwiftUI

Lifted from `build/source/music-components-spike.swift`, which is compiled
against `swift/AppKit.swift` and rendered in a real window before it ships.
Edit the spike, not this block.

```swift
/// Square artwork over a caption block of CONSTANT height. Card height minus
/// card width measured 37pt at every width, so the caption does not scale.
struct ArtworkCard: View {
    let art: Color
    let title: String
    let subtitle: String
    var width: CGFloat = 188
    var action: () -> Void = {}

    var body: some View {
        Button(action: action) { card }
            .buttonStyle(.plain)
            // One label for the pair: VoiceOver should say "Episode 740,
            // Soulection playgroup", not read two separate static texts.
            .accessibilityElement(children: .ignore)
            .accessibilityLabel("\(title), \(subtitle)")
            .accessibilityAddTraits(.isButton)
    }

    private var card: some View {
        VStack(alignment: .leading, spacing: 0) {
            RoundedRectangle(cornerRadius: 6, style: .continuous)
                .fill(art)
                .frame(width: width, height: width)   // square
            VStack(alignment: .leading, spacing: 0) {
                Text(title).font(.footnote).foregroundStyle(Color.Kit.musicInk)
                    .lineLimit(1)
                Text(subtitle).font(.caption2).foregroundStyle(Color.Kit.musicInkSoft)
                    .lineLimit(1)
            }
            .padding(.top, 6)
            .frame(height: 37, alignment: .top)       // constant, not derived
        }
        .frame(width: width)
    }
}
```
