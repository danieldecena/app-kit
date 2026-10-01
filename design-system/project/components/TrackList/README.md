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

## Inactive selection is the normal state for a monitor app

macOS greys the selection when the window is not key, and this caught the capture
out: the first "selected" shot read red because Music was still key, and a later
shot of the same state read grey because it was not. Pass `windowInactive` and
the fill becomes `music-select-inactive` with the labels back to normal ink.

## Columns are configuration

The measured playlist has seven columns and no Album; an earlier capture had one.
So the column set is passed in, and pixel-derived column positions recorded for
one capture describe *that* column set rather than contradicting another.

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
