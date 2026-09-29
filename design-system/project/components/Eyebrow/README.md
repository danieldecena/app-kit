# Eyebrow

Spaced mono capitals over a figure or a slot, saying what state it is in: IMPORTING, BLOCKED, IDLE. From Footage Library's chart plates.

- `eyebrow` style: SF Mono 11/13 semibold, uppercase, +1.2 tracking, `ink-soft`.
- `act`: the thing needs the person; the text turns `warn`. Pair it with the `act` Panel tone, so the state is in a word as well as a colour.
- One or two words. It names the state, the line under it explains it.
- Not a section heading (that is `title-2` or a Panel title) and not a status chip (that is Badge).

SwiftUI:

```swift
Text(word.uppercased())
    .font(Font.Kit.eyebrow)
    .tracking(CGFloat.Kit.trackingEyebrow)
    .foregroundStyle(act ? Color.Kit.warn : .secondary)
```
