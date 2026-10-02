# MiniPlayer

The transport capsule that floats over Music's scrolled content. It is **not** a
bar in the window chrome, which was the open question this slice closed.

## Measured

| | |
|---|---|
| size | **700 x 54pt** (AX; four pixel scans gave 698-701.5) |
| radius | **height / 2**, a full stadium -- the left-edge inset falls 17.5 to 0pt over 24pt |
| floats | **19pt** up from the window bottom |
| centred on | the **content area**, not the window |
| artwork | 34pt square |
| progress line | **2pt**, 2pt up from the inner bottom edge |

The centring is the detail worth keeping. AX puts it at `x=579 w=700` in a 1588pt
window with a 270pt sidebar: its centre lands on 929, which is the content
centre, not the window's 794. Widen the sidebar and the capsule moves.

## The progress line spans the now-playing group, not the capsule

An earlier reading from a pasted screenshot described "a hairline progress bar
along its own lower edge", implying the full 700pt. Measured against the
capsule's true edges at its widest row, the line runs **x 166.5-571.0pt** inside
a capsule that is exactly 700.0pt there: played to 546.0, then a dim unplayed
tail to 571.0.

That tail is why an earlier pass recorded the end as 555. It is only 15 units
above the capsule, so a brightness-threshold scan loses most of it and stops
early; the start, 166.5 against the artwork's 166.0, was right all along.

The line starts at the artwork's left edge, so it belongs to the now-playing
group rather than the capsule, which is why it is positioned inside
`.dc-miniplayer-now` here. **What sets its right end is still unexplained**: at
571 it matches neither the text, whose glyphs stop at 335, nor the trailing
cluster, which runs 507-680. This component's line is `flex: 1` between the
transport and the actions, which gives 167-607.8 -- the right start and 36.8pt
too much length.

## The progress line's two greys are white at an alpha, not two tokens

Measured off the same opaque capture, at @2x: the line is 4 device px, so **2pt**
and not the 1pt first recorded. On the line's centre row the played run is
`#D4D5D7` across 760 px (x 1421-2180) and the unplayed `#6E6F71` across 50 px
(x 2181-2230), every pixel in each identical -- so these are fills rather than
antialiased edges, and the step between them is hard.

Over the capsule's `#3B3B3D` those solve to white at **0.781 / 0.786 / 0.794**
per channel and **0.260 / 0.265 / 0.268**, so the line is drawn as
`on-music-glass` at 79% and 26% rather than as two new tokens. Compositing at
those alphas reproduces the measured greys to within 2/255, and it does the right
thing in light, where `on-music-glass` is black and nothing has been measured.

Before this the played fill was `ink-soft` (`#9A9A9A`) and the track was
`music-select-inactive`, a ground ink and a selection red on a glass surface --
the same borrowing called out below as the original mistake, surviving in the two
declarations that correction did not reach.

**The boundary that carries the value is not a fixed ratio.** What a sighted
reader uses is where the played run ends, not either grey against the capsule, and
both sides are an alpha over a *translucent* surface -- so the ratio moves with
whatever the capsule floats over. Over the measured opaque capsule it is 3.50:1 in
dark and 6.43:1 in light, both clear of the 3:1 a graphical object needs. Over a
translucent capsule on bright content in dark it falls to **1.90:1**, which fails
1.4.11, and that is the ordinary case, since Reduce Transparency is off by default
and the capsule floats over artwork.

No list of token pairs can catch that, because neither side is a token value. The
greys are Music's own, so they are recorded rather than corrected -- the same call
already made for `music-accent` and `music-star`. An app that must meet 1.4.11
here should raise the unplayed alpha or back the line with an opaque strip.

## Reduce Transparency is how any of this got measured

Three approaches failed before it. Over artwork the capsule is translucent and
has no stable edge; over flat white ground it is nearly white and has almost no
contrast; and a translucency-lift comparison fails because the lift changes with
whatever is behind. With Reduce Transparency on, the capsule is opaque
(`#3B3B3D` dark) and its edge is a clean step.

One trap inside that: the capsule floats over the Concerts card, so a naive
non-ground scan returns the card's 1231pt width instead. The two had to be
separated by fill colour.

## Glyphs

The defaults are text characters so the component renders with no asset
dependency. Pass real SF Symbols (`playGlyph`, `nextGlyph`, and the rest) in an
app that has them.

## SwiftUI

Lifted from `build/source/music-components-spike.swift`, which is compiled
against `swift/AppKit.swift` and rendered in a real window before it ships.
Edit the spike, not this block.

```swift
/// The floating transport capsule: 700x54, stadium radius, real material.
struct MiniPlayer: View {
    let art: Color
    let title: String
    let subtitle: String
    var progress: Double = 0.54
    var playing: Bool = true
    var shuffle: Bool = false
    var repeatOn: Bool = false
    var onPlayPause: () -> Void = {}
    var onPrevious: () -> Void = {}
    var onNext: () -> Void = {}
    var onShuffle: () -> Void = {}
    var onRepeat: () -> Void = {}
    var onLyrics: () -> Void = {}
    var onQueue: () -> Void = {}
    var onVolume: () -> Void = {}

    private func control(_ symbol: String, _ label: String, _ act: @escaping () -> Void) -> some View {
        Button(action: act) {
            Image(systemName: symbol).foregroundStyle(Color.Kit.onMusicGlass)
        }
        .buttonStyle(.plain)
        .accessibilityLabel(label)
    }

    /// A toggle says whether it is ON, which a plain button cannot. The accent
    /// is the only visual signal otherwise, so without this the state is
    /// colour-only and invisible to VoiceOver.
    private func toggle(_ symbol: String, _ label: String, _ on: Bool,
                        _ act: @escaping () -> Void) -> some View {
        Button(action: act) {
            Image(systemName: symbol)
                .foregroundStyle(on ? Color.Kit.musicAccent : Color.Kit.onMusicGlass)
        }
        .buttonStyle(.plain)
        .accessibilityLabel(label)
        .accessibilityValue(on ? "On" : "Off")
        .accessibilityAddTraits(on ? [.isSelected] : [])
    }

    var body: some View {
        HStack(spacing: 11) {
            toggle("shuffle", "Shuffle", shuffle, onShuffle)
            control("backward.fill", "Previous", onPrevious)
            control(playing ? "pause.fill" : "play.fill", playing ? "Pause" : "Play", onPlayPause)
            control("forward.fill", "Next", onNext)
            toggle("repeat", "Repeat", repeatOn, onRepeat)

            ZStack(alignment: .bottom) {
                Color.clear.frame(height: 54)   // the line belongs to the CAPSULE's edge
                HStack(spacing: 8) {
                    RoundedRectangle(cornerRadius: 3, style: .continuous)
                        .fill(art).frame(width: 34, height: 34)
                    VStack(alignment: .leading, spacing: 2) {
                        Text(title).font(.system(size: 15, weight: .semibold))
                            .foregroundStyle(Color.Kit.onMusicGlass)
                        Text(subtitle).font(.footnote).foregroundStyle(Color.Kit.onMusicGlass)
                    }
                    Spacer()
                }
                .frame(height: 54)
                GeometryReader { g in
                    ZStack(alignment: .leading) {
                        Capsule().fill(Color.Kit.musicInkSoft.opacity(0.35))
                        Capsule().fill(Color.Kit.musicInkSoft)
                            .frame(width: g.size.width * progress)
                    }
                }
                .frame(height: 1).padding(.bottom, 2)
                .accessibilityElement()
                .accessibilityLabel("Playback position")
                .accessibilityValue("\(Int(progress * 100)) percent")
            }

            HStack(spacing: 14) {
                control("quote.bubble", "Lyrics", onLyrics)
                control("list.bullet", "Queue", onQueue)
                control("speaker.wave.2.fill", "Volume", onVolume)
            }
        }
        .padding(.leading, 15).padding(.trailing, 20)
        .frame(width: 700, height: 54)
        .background(.regularMaterial, in: Capsule())
        .overlay(Capsule().strokeBorder(.white.opacity(0.12), lineWidth: 0.5))
        .shadow(color: .black.opacity(0.18), radius: 12, y: 4)
    }
}
```
