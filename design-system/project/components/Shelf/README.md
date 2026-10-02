# Shelf

A horizontally scrolling row of cards with a title and an optional "see all"
chevron, as on Music's Home.

## The shelf owns the gap; the card owns its shape

This is the one structural decision, and it comes from measurement rather than
taste. Three readings of the *same* window disagreed on card size and agreed on
the gap and the ratios, because the card tracks the width left over by a
user-resizable sidebar.

| | |
|---|---|
| gap | **20px**, or 16px with `compact` |
| ArtworkCard | square artwork + a **37px** caption block |
| HeroCard | 3:4 |

So **do not hard-code a card size**. A component shipping 188x225 is correct only
for the one sidebar position it was measured at.

The 20/16 split is a breakpoint, not a scale: 20px was measured at ~1300px of
content and 16px at 772px. Where it switches is not known, so `compact` is a
caller decision.

## The caption has to fit 37px, not be clipped to it

37 is a measured total, so the type inside it is constrained by it. Two
`footnote` lines are 18 + 18 = 36 and leave 1px for the gap under the artwork,
so the subtitle takes `caption-2`: 6 + 18 + 13 is exactly 37.

The first attempt used `footnote` for both and let flex compress each line from
18 to 14, cutting the descenders off the subtitle. It looked right only because
the preview's subtitle was all-caps. Music's own caption type was never
measured, so this split is ours.

## States

| State | What it does |
|---|---|
| `compact` | `data-compact="true"` on the shelf; the gap goes 20px to 16px |
| head hover | hovering the title row brings the see-all chevron from `ink-soft` to `ink` |
| track focus | the scroll track is a tab stop, so the arrow keys work without a trackpad; the ring is `music-accent`, 2px at 2px offset, like every other focusable thing here |
| head focus | the see-all button takes the same ring. Both relied on the browser's own 1px blue until 2026-10-01 -- a ring was always visible, it just was not this system's |

The cards are the caller's, so the shelf has no selected or disabled state of
its own.

## Scrolling

Music's shelf snaps to a card boundary: a measured scroll landed 878.9px against
a 219.5px pitch, four cards, within 0.1%, after an ease-out of about 0.73s. The
CSS uses `scroll-snap-type: x mandatory` and arrow keys scroll by exactly one
card pitch.

## SwiftUI

Lifted from `build/source/music-components-spike.swift`, which is compiled
against `swift/AppKit.swift` and rendered in a real window before it ships.
Edit the spike, not this block.

```swift
/// A horizontally scrolling row. The shelf owns the GAP; the card owns its size.
struct Shelf<Content: View>: View {
    let title: String
    var compact: Bool = false
    /// Leading inset of the shelf's header and first card: 34pt from the content
    /// edge, 6pt outside the 40pt line TrackList's pill starts on. Measured in
    /// Music at 980 and 1588pt (music-capture.md, 2026-10-02).
    var inset: CGFloat = 34
    var onMore: () -> Void = {}
    @ViewBuilder var content: Content

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack(spacing: 6) {
                Text(title).font(.title3.bold()).foregroundStyle(Color.Kit.musicInk)
                Button(action: onMore) {
                    Image(systemName: "chevron.right")
                        .font(.system(size: 12, weight: .semibold))
                        .foregroundStyle(Color.Kit.musicInkSoft)
                }
                .buttonStyle(.plain)
                .accessibilityLabel("See all \(title)")
            }
            .padding(.leading, inset)
            ScrollView(.horizontal, showsIndicators: false) {
                // 20pt wide, 16pt once the window narrows. A breakpoint, not a scale.
                HStack(alignment: .top, spacing: compact ? 16 : 20) { content }
                    .scrollTargetLayout()
            }
            .scrollTargetBehavior(.viewAligned)       // the snap Music has
            // The cards rest 34pt in, 6pt outside TrackList's pill, but scroll
            // all the way under the edge -- which contentMargins gives and a
            // plain .padding does not.
            .contentMargins(.horizontal, inset, for: .scrollContent)
        }
    }
}

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
