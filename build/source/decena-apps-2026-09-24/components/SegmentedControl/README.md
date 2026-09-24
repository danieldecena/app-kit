# SegmentedControl

Switches between 2 to 5 views of the same content ("Day", "Week", "Season").

- Track is `surface-sunk` with 3px inset and `radius-md`; the active segment is `surface` with `shadow-segment`, the only shadow on a resting screen.
- Labels `subhead` at 600; inactive in `ink-soft`, active in `ink`.
- The consumer provides `options`, `label` (for assistive tech) and either `value` + `onChange` or `defaultValue`.
- SwiftUI: use the native `Picker(...).pickerStyle(.segmented)`; it already matches.
