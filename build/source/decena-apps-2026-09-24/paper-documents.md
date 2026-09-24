# Paper documents

The Paper profile is for long-read web pages people study or keep open: prep sheets, briefs, study guides, call sheets. Apps, dashboards and anything tappable-first stay on the panel and radius rules in the main guide.

## Surfaces and lines

- Set the page on `surface`. The header band and the sidebar sit on `ground`, separated from the page by one `hair` line.
- Hairlines, not panels. Split rows, lists, tables and key/value pairs with 1px `hair`. No panels, cards, shadows or blur on a Paper page.
- Corners are square: controls, rows, tags and bars use radius 0. Only dots are round.

## One accent

- `clay` marks where you are and what to do: the active tab's 2px underline, the sidebar's active row (a 2px inset bar on the leading edge), the primary button, and the 3px rule of the page's one callout.
- A pressed secondary control fills `ink` with `surface` text. Quiz verdicts fill `ok` or `bad` only once chosen.
- Links inherit the text colour with an `edge` underline, offset 2.5px, that turns `ink` on hover. Never blue: blue is `signal`.

## Type

One family: SF. The web stack is `-apple-system, BlinkMacSystemFont, "SF Pro Display"` for headlines and the `sans` family for everything else.

| Role | Style |
|---|---|
| Page headline | SF Pro Display 40/45, 700, -0.022em (30px below 640px) |
| Countdown figure | SF Pro Display 19, 700 |
| Section title | 13/17, 600, uppercase, +0.08em, `ink` |
| Subsection | `headline` |
| Script to read aloud | 15/27, `ink`, 64ch |
| Body | 14/22, `ink-soft`; bold runs in `ink` |
| Micro-label | 11.5, 600, uppercase, +0.07em, `ink-soft` |
| Figures in prose | `mono` 600 at .93em in `ink`, no wash |

When a page asks the reader to memorise a handful of words, use Highlight instead of mono figures, with one meaning per colour for the whole page.

## Controls and tags

- Controls are 32px tall on desktop with a pointer and `touch` (44px) below 860px.
- Secondary controls: transparent with a 1px `hair` outline that darkens to `edge` on hover.
- Segmented settings (speed, voice) use `mono` 11.5 labels; the chosen segment fills `ink`.
- Status tags are uppercase micro-labels on a 1px outline: solid `edge` for done, dashed for to do. Never a filled pill.

## Charts

Chart in emphasis: every mark `chart-base`, the one that makes the point in a series colour, values in `ink`, and a Show table toggle on every chart. See BarChart.

## Layout

- A 272px sidebar beside a 760px reading column; from 1100px the column widens to 1140px and lists go two across.
- At 860px and below the sidebar hides and the header's uppercase tabs become the navigation.
- At 640px and below: one column, `space-6` gutters.

## From Paper System tokens

| Paper | Decena |
|---|---|
| `--bk-bg` | `surface` |
| `--bk-wash` | `ground` |
| `--bk-ink` | `ink` |
| `--bk-soft` | `ink-soft` |
| `--bk-grey` | `edge` (markers and underlines only) |
| `--bk-hair`, `--bk-line` | `hair` |
| `--bk-clay` | `clay` |
| `--bk-ok` | `ok` |
| `--bk-warn` | `warn` (the old amber read too close to clay) |
| `--bk-bad` | `bad` |
| `--bk-fill` | `surface-sunk` |
| `--chart-hl` | `series-1` to `series-5` |
| `--chart-base` | `chart-base` |
