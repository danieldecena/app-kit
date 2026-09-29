# Toolbar

One row pinned above the content it acts on, which scrolls under it. From Footage Library's library bar and Claude Spinner's session toolbar. A Mac pattern: on iPhone use the system toolbar and keep `touch` targets.

- Order: leading controls (a SegmentedControl), the search field, a spacer, icon tools, then the primary action last.
- Search (`searchLabel`): a capsule with a magnifying glass, 10 side padding, at least 32 tall, at most 360 wide, on the system `fill`. A clear button appears once there is a query.
- Tools: icon-only gray buttons, 32 square. The title is the tooltip and the accessible name. A tool that cannot run stays visible, dimmed, and its tooltip says why (`disabled: "No clip selected"`).
- `primary`: one filled Button, the thing the screen is for (Export, Send). At most one.
- `notice`: a line under the row that appears only after an action, saying what happened ("Exported 42 clips") or what failed (`noticeTone: "bad"`). It is announced to screen readers. Clear it on the next action.
- On the web the bar is `glass` with a `hair` bottom edge, sticky at the top.

SwiftUI, docked (Footage Library): the row is an `HStack(spacing: 10)` padded 16 by 6 over `.background(.bar)` with a `Divider()` under it. Search is `HStack(spacing: 6) { Image(systemName: "magnifyingglass").foregroundStyle(.secondary); TextField(...) }` with `.padding(.horizontal, 10)`, `.frame(minHeight: 32)`, `.background(.quaternary.opacity(0.5), in: Capsule())`, `.frame(maxWidth: 360)`. Tools are `.buttonStyle(.bordered)` with `.help(title)`; the primary is `.buttonStyle(.borderedProminent)`.

SwiftUI, native on macOS 26 and later (Claude Spinner's SessionToolbar): Liquid Glass instead of a bar. Wrap the row in `GlassEffectContainer(spacing: 8) { HStack(spacing: 8) { ... } }`, give the search field `.glassEffect(.regular, in: Capsule())` and the tools `.buttonStyle(.glass)` with `.help(reason ?? title)`, put the notice under it on a card (radius 6), and pin the whole stack with `.safeAreaInset(edge: .top, spacing: 0)` so content scrolls beneath.
