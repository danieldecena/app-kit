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
| progress line | 1pt, 2pt up from the inner bottom edge |

The centring is the detail worth keeping. AX puts it at `x=579 w=700` in a 1588pt
window with a 270pt sidebar: its centre lands on 929, which is the content
centre, not the window's 794. Widen the sidebar and the capsule moves.

## The progress line spans the now-playing group, not the capsule

An earlier reading from a pasted screenshot described "a hairline progress bar
along its own lower edge", implying the full 700pt. Measured, the line runs
x 165-555pt: it starts at the artwork's left edge and ends with the text group.
So the line belongs to the now-playing group, which is why it is positioned
inside `.dc-miniplayer-now` here rather than on the capsule.

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
