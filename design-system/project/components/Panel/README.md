# Panel

Groups related content on a `surface` card over the `ground`.

- `radius-lg`, `space-6` padding, `space-5` between children. Separate panels with `space-7`, not shadows or borders.
- `title` is the `title-3` style (20/25 semibold); `meta` sits on the trailing edge in `ink-soft` 13/18 for freshness or counts ("Updated 6 min ago"). Both are optional.
- Content goes straight in; use `.dc-row` / `.dc-stack` inside for layout. Nest a `.dc-list` for rows, not another Panel.
