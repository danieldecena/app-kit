# ListRow

A selectable row in a list: optional thumbnail, title, subtitle and a trailing value.

- 58px minimum, `radius-md`, rows divided by `hair`. Selected rows take `accent-wash`, translucent.
- Thumbnail 56x36 at `radius-sm` on `surface-sunk`. Title `headline`, subtitle `subhead` `ink-soft`, trailing in mono `ink-soft` with tabular figures.
- Put rows in a `.dc-list` container with `role="listbox"`. The consumer provides the content and selection handling. From Footage Library's clip row.
