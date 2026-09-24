# BarChart

Compares amounts across categories or days, one bar per row, stacked when a row carries several values. Built to Apple's HIG chart guidance.

- **Say the point first.** `title` names the chart; `summary` is its main message in one sentence ("Most clips on Sep 17 still have one copy"). The summary is also the chart's accessibility label.
- **Data first, frame quiet.** Bars take `series-1` onward; grid lines are `hair`, the zero baseline is `edge`, tick labels are `caption` in `ink-soft` with tabular figures.
- **Axis on the trailing edge, from zero.** Value labels sit right of the plot so the leading edge lines up with the rest of the screen. Bars always start at zero, and ticks step through familiar sequences (1, 2, 2.5, 5 x 10^n), about three grid lines.
- **Stacks are separated.** Segments in a stack are split by a 1.5px `surface` line, and only the top segment gets the 4px rounded cap.
- **Not colour alone.** A stacked chart shows a legend of dots with names; each bar carries a text title with its value for assistive tech.
- **Emphasis when one bar is the point.** Pass `highlight` (a label or a list) and the chart turns monochrome: those bars take series `color` (mint unless told otherwise), every other bar takes `chart-base`, each bar carries its value, and the legend names both (`highlightName`, `restName`). Use it when the story is one category, not a comparison of series.
- **Series order:** mint, purple, blue, pink, orange. A single-series chart is mint, so it never reads as the blue accent.
- The consumer provides `data` (`label` plus `value` or `values`), `series` names for stacks, `title`, `summary` and `unit`; for emphasis, `highlight` and the two legend names.
- SwiftUI: use Swift Charts `BarMark` with `.foregroundStyle(by:)` mapped to the series colour sets, `.chartYAxis { AxisMarks(position: .trailing) }`, and `.accessibilityLabel` from `summary`.
