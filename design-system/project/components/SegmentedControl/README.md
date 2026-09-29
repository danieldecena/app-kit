# SegmentedControl

Picks exactly one of 2-5 views of the same content: Day / Week / Season.

- A `surface-sunk` track (`radius-md`, 3px inset); the chosen segment lifts to `surface` with `ink` text and `shadow-segment`, the rest sit in `ink-soft`. SwiftUI: `Picker(...).pickerStyle(.segmented)`.
- Segments are 38px tall, `space-6` side padding, 600 15/20. Keep labels to one or two words, all roughly the same length.
- `label` is required: it names the group for screen readers (`role="radiogroup"`). Pass `value` + `onChange` to control it, or `defaultValue` to let it hold its own state.
- `options` are strings, or `{ value, label }` when the label is not plain text.
- Several filters at once, or more than 5 choices: use FilterPill instead.
