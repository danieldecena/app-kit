# Highlight

Marks the few words in running text worth remembering: a figure, a name, a date. The five colours are Apple Notes' highlight set: purple, pink, orange, mint, blue.

- Bold `hl-<colour>` ink on `hl-<colour>-wash`, 4px radius, tabular figures. Every pair clears 4.6:1 in both themes.
- Colour is a category you choose and keep: for example mint for money, blue for dates, purple for names. Say what each colour means once, near the top of the page.
- A handful per screen. If most of a sentence is highlighted, nothing is.
- Never for status (use Badge or Flag) and never on a control.
- SwiftUI: `Text(AttributedString)` with `.backgroundColor` and `.foregroundColor` from the matching colour sets, or `.background(Color.hlMintWash, in: .rect(cornerRadius: 4))` on a `Text`.
