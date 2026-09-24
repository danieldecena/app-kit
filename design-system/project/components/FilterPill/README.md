# FilterPill

Toggles one filter on a list; several can be on at once.

- Off: the system `fill` (translucent gray), `ink` text. On: `accent-wash` with `accent-ink` text and a 1.5px `accent` ring, translucent like the Mac. From Footage Library.
- 40px tall, `radius-pill`, `space-5` side padding, `space-3` gap between pills; wrap, never scroll a row of fewer than 8.
- Add `count` when the number helps pick (clips per camera). The consumer provides label, `selected` and `onClick`.
- For exactly one of 2-5 views, use SegmentedControl instead.
