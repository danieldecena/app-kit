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

## Scrolling

Music's shelf snaps to a card boundary: a measured scroll landed 878.9px against
a 219.5px pitch, four cards, within 0.1%, after an ease-out of about 0.73s. The
CSS uses `scroll-snap-type: x mandatory` and arrow keys scroll by exactly one
card pitch.
