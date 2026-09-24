"""App Kit: the Decena Apps design system brought back for SwiftUI apps, on
Apple's own system neutrals and colours (the same palette as Artifact Kit).

Reads the live Decena files from <src>/project, writes the new files to
<out>/project, and a SwiftUI token file to <out>/swift/AppKit.swift.
"""
import json, os, re, sys
SRC = sys.argv[1]; OUT = sys.argv[2]
P = os.path.join(OUT, 'project'); os.makedirs(P, exist_ok=True)
def rd(rel): return open(os.path.join(SRC, 'project', rel)).read()
def w(rel, text, base=P):
    path = os.path.join(base, rel); os.makedirs(os.path.dirname(path), exist_ok=True); open(path, 'w').write(text)

# ------------------------------------------------------------------ tokens
tok = json.loads(rd('tokens.json'))
old = {t['name']: t for t in tok['color']['tokens']}
def T(name, light, dark, usage): return {'name': name, 'value': {'light': light, 'dark': dark} if dark else light, 'usage': usage}
colors = [
 T('ground', '#F2F2F7', '#000000', 'Screen background behind grouped content: systemGroupedBackground.'),
 T('surface', '#FFFFFF', '#1C1C1E', 'Panels, cards, list rows, sheets: secondarySystemGroupedBackground.'),
 T('surface-sunk', '#E5E5EA', '#2C2C2E', 'Segmented tracks, neutral badges, thumbnail placeholders: systemGray5 / tertiary grouped.'),
 T('ink', '#1D1D1F', '#F5F5F7', 'Primary text and icons (label). 13:1 or better on ground, surface and surface-sunk.'),
 T('ink-soft', '#636366', '#98989D', 'Secondary text (secondaryLabel, opaque). 4.7:1 or better on ground, surface and surface-sunk.'),
 T('hair', '#D1D1D6', '#38383A', 'Hairline dividers (separator). Decorative only: never the only boundary of a control.'),
 T('edge', '#86868B', '#7C7C80', 'Outlines of interactive controls (3:1 or better on ground and surface).'),
 T('fill', 'rgba(118, 118, 128, 0.12)', 'rgba(118, 118, 128, 0.24)', 'The system fill: gray buttons, off filter pills, hover and pressed rows. Translucent.'),
 T('accent', '#007AFF', '#0A84FF', "The app's accent: Color.accentColor, System Blue by default; follows the person's accent on the Mac. Tints, selection, rings, marks."),
 T('accent-fill', '#0062CC', '#086ACC', 'Filled (borderedProminent) buttons: the accent stepped 20% toward black so white text passes 4.5:1.'),
 T('on-accent', '#FFFFFF', '#FFFFFF', 'Text and symbols on accent-fill.'),
 T('accent-wash', 'rgba(0, 122, 255, 0.12)', 'rgba(10, 132, 255, 0.20)', 'Translucent accent tint: tinted (bordered) buttons, selected pills and rows.'),
 T('accent-ink', '#0058B9', '#5DABFF', 'Accent text on accent-wash or on any ground (4.5:1 or better): links, plain buttons.'),
 T('ok', '#207936', '#30DB5B', 'Status: done, healthy, synced (system green, text step). Always with a word or glyph.'),
 T('ok-wash', '#DCF4E1', '#1F4527', 'Fill behind ok text.'),
 T('warn', '#C73300', '#FFB340', 'Status: needs a look soon, stale, partial (system orange, text step).'),
 T('warn-wash', '#FCECD3', '#513914', 'Fill behind warn text.'),
 T('warn-ink', '#C73300', '#FFB340', 'Warn text on warn-wash (4.6:1 or better).'),
 T('bad', '#CC0014', '#FF6A63', 'Status: failed, over limit, destructive (system red, text step). Never a high value on a data scale.'),
 T('bad-wash', '#FCDDDB', '#51241F', 'Fill behind bad text.'),
]
for k in ('heat-1', 'heat-2', 'heat-3', 'heat-4', 'series-1', 'series-2', 'series-3', 'series-4', 'series-5'):
    t = dict(old[k]); t['usage'] = t['usage'].replace(' because blue is `signal`', '').replace('Never on a chart that also shows signal. ', 'Reads as the accent; avoid beside accent controls. ').replace(' Last on purpose: it sits 1.15:1 from clay, so never beside a clay control.', '').replace('Chart series 1, Apple mint. First, and the colour of a single-series chart: blue is taken by signal, so a lone blue series would read as "needs you".', 'Chart series 1, Apple mint. First, and the colour of a single-series chart.')
    colors.append(t)
colors += [
 T('chart-base', '#C7C7CC', '#48484A', 'Emphasis charts: every mark that is not the point (systemGray3). Under 3:1, so those marks carry a value label or sit beside a table.'),
 T('chart-mid', '#8E8E93', '#8E8E93', 'A lone series with nothing to single out (systemGray); hover on grey marks.'),
]
HL = {'purple': ('#8944AB', 'rgba(175, 82, 222, 0.10)', '#DA8FFF', 'rgba(191, 90, 242, 0.16)'), 'pink': ('#C60E41', 'rgba(255, 45, 85, 0.10)', '#FF6482', 'rgba(255, 55, 95, 0.16)'),
      'orange': ('#C73300', 'rgba(255, 149, 0, 0.10)', '#FFB340', 'rgba(255, 159, 10, 0.16)'), 'mint': ('#0B7771', 'rgba(0, 199, 190, 0.10)', '#66D4CF', 'rgba(99, 230, 226, 0.16)'),
      'blue': ('#0040DD', 'rgba(0, 122, 255, 0.10)', '#429DFF', 'rgba(10, 132, 255, 0.16)')}
for k, (lt, lw, dt, dw) in HL.items():
    colors.append(T(f'hl-{k}', lt, dt, f'Highlighted text in {k}, as in Apple Notes: bold, on hl-{k}-wash (4.5:1 or better in both themes). Also the ink of a {k} tinted button.'))
    colors.append(T(f'hl-{k}-wash', lw, dw, f'The system {k} at 10% (16% dark), translucent: highlight and {k} tinted-button fill.'))
colors += [
 T('glass', 'rgba(255, 255, 255, 0.55)', 'rgba(44, 44, 46, 0.55)', 'Web stand-in for Liquid Glass (with a 16px blur): toolbars and controls floating over content. In SwiftUI use .glassEffect() or .buttonStyle(.glass).'),
 T('glass-edge', 'rgba(255, 255, 255, 0.70)', 'rgba(255, 255, 255, 0.14)', 'The 0.5px inner edge of glass.'),
 T('scrim', 'rgba(0, 0, 0, 0.80)', 'rgba(0, 0, 0, 0.78)', 'Toasts and hints over content, white text.'),
]
tok['name'] = 'App Kit'
tok['color']['tokens'] = colors
tok['type']['families'] = {
 'sans': '-apple-system, BlinkMacSystemFont, "SF Pro Text", "SF Pro", system-ui, sans-serif',
 'display': '-apple-system, BlinkMacSystemFont, "SF Pro Display", "SF Pro", system-ui, sans-serif',
 'round': 'ui-rounded, "SF Pro Rounded", -apple-system, BlinkMacSystemFont, system-ui, sans-serif',
 'mono': 'ui-monospace, "SF Mono", SFMono-Regular, Menlo, monospace',
 'compact': '"SF Compact Text", "SF Compact", -apple-system, system-ui, sans-serif'}
for g in tok['type']['groups']:
    for s in g['styles']:
        s['usage'] = s['usage'].replace(' SF Pro Display everywhere (Instrument Sans off Apple devices).', ' SF Pro Display.')
tok['type']['groups'] = [g for g in tok['type']['groups'] if g['name'] != 'Figures'] + [
 {'name': 'Figures', 'family': 'round', 'styles': [
   {'name': 'figure', 'family': 'round', 'fontSize': '34px', 'lineHeight': '40px', 'fontWeight': 700, 'sample': '7 of 24', 'usage': 'Health-style big number: .system(.largeTitle, design: .rounded).bold().'},
   {'name': 'figure-sm', 'family': 'round', 'fontSize': '22px', 'lineHeight': '26px', 'fontWeight': 700, 'sample': '90 sec', 'usage': 'Values in a comparison: .system(.title2, design: .rounded).bold().'}]},
 {'name': 'Reading', 'family': 'sans', 'styles': [
   {'name': 'script', 'family': 'sans', 'fontSize': '17px', 'lineHeight': '28px', 'fontWeight': 400, 'sample': 'I build the systems behind campaigns.', 'usage': 'Long reading in SF Pro Text: .body with .lineSpacing(6).'}]},
 {'name': 'Glance', 'family': 'compact', 'styles': [
   {'name': 'glance', 'family': 'compact', 'fontSize': '15px', 'lineHeight': '18px', 'fontWeight': 600, 'sample': '1d 7h', 'usage': 'watchOS and widgets only; SF Compact is the watch face.'}]}]
for t in tok['shadow']['tokens']:
    for th in ('light', 'dark'):
        t['value'][th] = t['value'][th].replace('rgba(27,26,24,', 'rgba(0,0,0,')
tok['shadow']['tokens'].append({'name': 'shadow-glass', 'value': {'light': '0 1px 3px rgba(0,0,0,0.12)', 'dark': '0 1px 3px rgba(0,0,0,0.4)'}, 'usage': 'Under glass controls, with the glass-edge ring.'})
for t in tok['radius']['tokens']:
    if t['name'] == 'radius-md': t['usage'] = 'Inputs, list rows, stat tiles, segments.'
    if t['name'] == 'radius-pill': t['usage'] = 'Buttons (capsules, as in iOS 26), filter pills, chips, toasts.'
w('tokens.json', json.dumps(tok, indent=2, ensure_ascii=False))

# ------------------------------------------------------------------ bundle.css
css = rd('components/bundle.css')
css = re.sub(r'@import url\([^)]*\);\n\n', '', css)
R = [('var(--signal)', 'var(--accent)'), ('var(--clay-wash)', 'var(--accent-wash)'), ('var(--clay-ink)', 'var(--accent-ink)'),
     ('var(--on-clay)', 'var(--on-accent)'), ('var(--signal-wash)', 'var(--accent-wash)')]
for a, b in R: css = css.replace(a, b)
BTN_OLD = css[css.index('/* Button */'):css.index('/* FilterPill */')]
BTN = '''/* Button: iOS 26 capsules in the Notes highlight colours, translucent */
.dc-btn { --tint: var(--accent); --tint-ink: var(--accent-ink); --tint-wash: var(--accent-wash); --tint-fill: var(--accent-fill); --tint-on: var(--on-accent);
  min-height: var(--touch); padding: 0 20px; border-radius: var(--radius-pill); font: 600 15px/20px var(--font-sans); cursor: pointer; display: inline-flex; align-items: center; justify-content: center; gap: var(--space-4); border: 0; transition: background-color 150ms ease-out, filter 150ms ease-out; }
.dc-btn-tinted { background: var(--tint-wash); color: var(--tint-ink); }
.dc-btn-tinted:hover { background: color-mix(in srgb, var(--tint) 18%, transparent); }
.dc-btn-filled, .dc-btn-primary { background: var(--tint-fill); color: var(--tint-on); }
.dc-btn-filled:hover, .dc-btn-primary:hover { filter: brightness(1.08); }
.dc-btn-gray, .dc-btn-secondary { background: var(--fill); color: var(--ink); }
.dc-btn-gray:hover, .dc-btn-secondary:hover { background: rgba(118, 118, 128, .2); }
.dc-btn-plain { background: transparent; color: var(--tint-ink); padding: 0 var(--space-4); }
.dc-btn-plain:hover { background: var(--fill); }
.dc-btn-glass { background: var(--glass); color: var(--ink); -webkit-backdrop-filter: blur(16px) saturate(1.8); backdrop-filter: blur(16px) saturate(1.8); box-shadow: inset 0 0 0 .5px var(--glass-edge), var(--shadow-glass); }
.dc-btn-destructive { --tint: #FF3B30; --tint-ink: var(--bad); --tint-wash: var(--bad-wash); background: var(--tint-wash); color: var(--tint-ink); }
.dc-tint-purple { --tint: #AF52DE; --tint-ink: var(--hl-purple); --tint-wash: var(--hl-purple-wash); --tint-fill: #8C42B2; --tint-on: #FFFFFF; }
.dc-tint-pink { --tint: #FF2D55; --tint-ink: var(--hl-pink); --tint-wash: var(--hl-pink-wash); --tint-fill: #CC2444; --tint-on: #FFFFFF; }
.dc-tint-orange { --tint: #FF9500; --tint-ink: var(--hl-orange); --tint-wash: var(--hl-orange-wash); --tint-fill: #FF9500; --tint-on: #1D1D1F; }
.dc-tint-mint { --tint: #00C7BE; --tint-ink: var(--hl-mint); --tint-wash: var(--hl-mint-wash); --tint-fill: #00C7BE; --tint-on: #1D1D1F; }
.dc-tint-blue { --tint: #007AFF; --tint-ink: var(--hl-blue); --tint-wash: var(--hl-blue-wash); --tint-fill: #0062CC; --tint-on: #FFFFFF; }
.dc-btn:disabled { opacity: .4; cursor: default; filter: none; }

'''
css = css.replace(BTN_OLD, BTN)
css = css.replace('.dc-pill { min-height: 40px; padding: 0 var(--space-5); border-radius: var(--radius-pill); font: 600 13px/18px var(--font-sans); border: 1px solid var(--edge); background: var(--surface); color: var(--ink);',
                  '.dc-pill { min-height: 40px; padding: 0 var(--space-5); border-radius: var(--radius-pill); font: 600 13px/18px var(--font-sans); border: 0; background: var(--fill); color: var(--ink);')
css = css.replace('.dc-pill[aria-pressed="true"] { background: var(--clay); border-color: var(--clay); color: var(--on-accent); }',
                  '.dc-pill[aria-pressed="true"] { background: var(--accent-wash); color: var(--accent-ink); box-shadow: inset 0 0 0 1.5px var(--accent); }')
css = css.replace('.dc-badge-clay { background: var(--accent-wash); color: var(--accent-ink); }\n.dc-badge-signal { background: var(--accent-wash); color: var(--accent); }',
                  '.dc-badge-accent, .dc-badge-clay, .dc-badge-signal { background: var(--accent-wash); color: var(--accent-ink); }')
css = css.replace('.dc-flag-signal { background: var(--accent-wash); color: var(--accent); box-shadow: inset 0 0 0 1px var(--accent); }',
                  '.dc-flag-accent, .dc-flag-signal { background: var(--accent-wash); color: var(--accent-ink); box-shadow: inset 0 0 0 1px var(--accent); }')
css = css.replace('.dc-tile-value { font: 600 28px/32px var(--font-mono);', '.dc-tile-value { font: 700 28px/32px var(--font-round);')
css = css.replace('.dc-tile-meter > span { display: block; height: 100%; border-radius: 3px; background: var(--ink); }', '.dc-tile-meter > span { display: block; height: 100%; border-radius: 3px; background: var(--accent); }')
css = css.replace('.dc-tile-meter { height: 6px; border-radius: 3px; background: var(--surface-sunk);', '.dc-tile-meter { height: 6px; border-radius: 3px; background: var(--accent-wash);')
assert 'clay' not in re.sub(r'dc-(badge|flag)-(clay|signal)', '', css), [l for l in css.split('\n') if 'clay' in l]
assert '--signal' not in css
w('components/bundle.css', css)

# ------------------------------------------------------------------ bundle.js
js = rd('components/bundle.js')
js = js.replace('"namespace":"Decena"', '"namespace":"AppKit"')
js = js.replace('var variant = p.variant || "secondary";\n    return h("button", Object.assign({ type: "button" }, omit(p, ["variant", "className", "children"]), {\n      className: cx("dc-btn", "dc-btn-" + variant, p.className)',
                'var variant = p.variant || "tinted";\n    return h("button", Object.assign({ type: "button" }, omit(p, ["variant", "tint", "className", "children"]), {\n      className: cx("dc-btn", "dc-btn-" + variant, p.tint && p.tint !== "accent" && "dc-tint-" + p.tint, p.className)')
js = js.replace('var FLAG_GLYPH = { warn: "!", bad: "x", signal: "->" };', 'var FLAG_GLYPH = { warn: "!", bad: "x", accent: "->", signal: "->" };')
js = js.replace('window.Decena = Object.assign(window.Decena || {}, {', 'window.AppKit = window.Decena = Object.assign(window.AppKit || {}, {')
assert 'dc-tint-' in js and 'window.AppKit' in js
w('components/bundle.js', js)

# ------------------------------------------------------------------ index.d.ts
dts = rd('components/index.d.ts')
dts = dts.replace('/** Action button. `primary` (clay) at most once per view. */\nexport function Button(props: ButtonHTMLAttributes<HTMLButtonElement> & {\n  variant?: "primary" | "secondary" | "plain" | "destructive";',
                  '/** Action button, an iOS 26 capsule. `tinted` (translucent) is the default; `filled` at most once per view. */\nexport function Button(props: ButtonHTMLAttributes<HTMLButtonElement> & {\n  variant?: "tinted" | "filled" | "gray" | "plain" | "glass" | "destructive" | "primary" | "secondary";\n  /** The Notes highlight colours; accent by default. */\n  tint?: "accent" | "purple" | "pink" | "orange" | "mint" | "blue";')
dts = dts.replace('tone?: "neutral" | "hollow" | "clay" | "signal" | "ok" | "warn" | "bad";', 'tone?: "neutral" | "hollow" | "accent" | "ok" | "warn" | "bad";')
dts = dts.replace('export function Flag(props: { tone?: "warn" | "bad" | "signal"; children: ReactNode }): JSX.Element;', 'export function Flag(props: { tone?: "warn" | "bad" | "accent"; children: ReactNode }): JSX.Element;')
w('components/index.d.ts', dts)

# ------------------------------------------------------------------ component docs + previews
def ns(s): return s.replace('window.Decena', 'window.AppKit')
docs = {}
docs['Button/README.md'] = '''# Button

Starts an action; verb first, sentence case ("Retry sync", "Import clips"). Capsules, as in iOS 26, in the Notes highlight colours.

- `tinted` (the default): a translucent wash of the tint (`accent-wash`, 12% / 20%) with `accent-ink` text. SwiftUI: `.buttonStyle(.bordered)` with `.tint(...)`.
- `filled`: at most one per view, the thing the screen is for. `accent-fill` with `on-accent`. SwiftUI: `.buttonStyle(.borderedProminent)`.
- `gray`: the system `fill` in `ink`, for Cancel and neutral actions. SwiftUI: `.bordered` with `.tint(.gray)`.
- `plain`: text in the tint, no fill, for inline actions like "Show all". SwiftUI: `.borderless`.
- `glass`: controls floating over content (maps, photos, video). SwiftUI: `.buttonStyle(.glass)` on iOS 26 and macOS 26.
- `destructive`: Delete, Remove, in system red; never `filled` by default. SwiftUI: `Button(role: .destructive)`.
- `tint`: `accent` (default), `purple`, `pink`, `orange`, `mint`, `blue`. Every label passes 4.5:1 on its fill.
- Height is `touch` (44px), `radius-pill`. The consumer provides the label and `onClick`.
'''
docs['Button/preview.html'] = '''<!-- @dsCard group="Actions" height=190 subtitle="Tinted in six colours, filled, gray, plain, glass, destructive" -->
<!doctype html>
<html>
<head><meta charset="utf-8"><title>Button</title></head>
<body>
<div id="root"></div>
<script>
  var D = window.AppKit, h = React.createElement;
  ReactDOM.createRoot(document.getElementById('root')).render(h('div',{className:'dc-stack'},
    h('div',{className:'dc-row'},h(D.Button,null,'Preview'),h(D.Button,{tint:'purple'},'Tag'),h(D.Button,{tint:'pink'},'Favorite'),h(D.Button,{tint:'orange'},'Flag'),h(D.Button,{tint:'mint'},'Share'),h(D.Button,{tint:'blue'},'Info')),
    h('div',{className:'dc-row'},h(D.Button,{variant:'filled'},'Import 42 clips'),h(D.Button,{variant:'gray'},'Cancel'),h(D.Button,{variant:'plain'},'Show all'),h(D.Button,{variant:'destructive'},'Delete'),
      h('span',{style:{display:'inline-flex',padding:10,borderRadius:22,background:'linear-gradient(120deg,#5AC8FA,#AF52DE 60%,#FF2D55)'}},h(D.Button,{variant:'glass'},'Play')))));
</script>
</body>
</html>
'''
docs['FilterPill/README.md'] = rd('components/FilterPill/README.md').replace('- Off: `surface` with an `edge` border. On: `clay` fill, `on-clay` text. From Footage Library.', '- Off: the system `fill` (translucent gray), `ink` text. On: `accent-wash` with `accent-ink` text and a 1.5px `accent` ring, translucent like the Mac. From Footage Library.')
docs['Badge/README.md'] = rd('components/Badge/README.md').replace('`clay`, `signal`, `ok`, `warn`, `bad`', '`accent`, `ok`, `warn`, `bad`')
docs['Badge/preview.html'] = ns(rd('components/Badge/preview.html')).replace("h(D.Badge,{tone:'clay'},'Selected'),h(D.Badge,{tone:'signal'},'Needs you'),", "h(D.Badge,{tone:'accent'},'Selected'),").replace('Neutral, hollow, clay, signal, ok, warn, bad', 'Neutral, hollow, accent, ok, warn, bad')
docs['Flag/README.md'] = rd('components/Flag/README.md').replace('`signal`: something needs the person.', '`accent`: something needs the person.')
docs['Flag/preview.html'] = ns(rd('components/Flag/preview.html')).replace("{tone:'signal'}", "{tone:'accent'}").replace('Warn, bad, signal', 'Warn, bad, accent')
docs['StatTile/README.md'] = rd('components/StatTile/README.md').replace('value in `value` (mono 28, tabular figures)', 'value in `figure` (SF Pro Rounded 28 bold, tabular figures, as in Health)').replace('`attention` draws a 1.5px `signal` ring and turns the meter `signal`', '`attention` draws a 1.5px `accent` ring').replace("From Charts Tab's instrument panel and Footage Review Board.", 'The meter is `accent` on `accent-wash`.')
docs['ListRow/README.md'] = rd('components/ListRow/README.md').replace('Selected rows take `clay-wash`.', 'Selected rows take `accent-wash`, translucent.')
docs['BarChart/README.md'] = rd('components/BarChart/README.md').replace('A single-series chart is mint, because blue is `signal`. Orange comes last since it sits close to clay.', 'A single-series chart is mint, so it never reads as the blue accent.')
for comp in ('FilterPill', 'SegmentedControl', 'StatTile', 'Panel', 'ListRow', 'Highlight', 'BarChart'):
    docs[f'{comp}/preview.html'] = ns(rd(f'components/{comp}/preview.html'))
for rel, text in docs.items():
    assert 'clay' not in text.lower() or rel.endswith('.html') is False and 'clay' not in text, (rel, [l for l in text.split('\n') if 'clay' in l.lower()])
    w('components/' + rel, text)

# ------------------------------------------------------------------ Cover
w('components/Cover/preview.html', '''<!-- @dsCard height=320 -->
<!doctype html>
<html>
<head><meta charset="utf-8"><title>Cover</title>
<style>
  html, body { margin: 0; padding: 0; background: var(--ground); }
  .cv { position: relative; width: 960px; height: 320px; overflow: hidden; background: var(--ground); font-family: var(--font-sans); }
  .txt { position: absolute; left: 40px; bottom: 36px; width: 440px; display: flex; flex-direction: column; gap: 14px; }
  .name { margin: 0; font-family: var(--font-display); font-weight: 700; font-size: 104px; line-height: .95; letter-spacing: -2px; color: var(--ink); }
  .tag { margin: 0; font-size: 15px; line-height: 21px; color: var(--ink-soft); }
  .win { position: absolute; left: 500px; top: 28px; width: 430px; height: 264px; border-radius: 22px; background: linear-gradient(135deg, #5AC8FA, #AF52DE 55%, #FF2D55); overflow: hidden; }
  .card { position: absolute; left: 18px; top: 18px; width: 250px; padding: 12px 14px; border-radius: 16px; background: var(--surface); }
  .cat { font: 600 15px/20px var(--font-sans); color: var(--hl-mint); }
  .fig { font: 700 34px/40px var(--font-round); color: var(--ink); } .fig small { font: 600 15px var(--font-round); color: var(--ink-soft); margin-left: 4px; }
  .bar { position: absolute; left: 18px; bottom: 18px; display: flex; gap: 8px; padding: 8px; border-radius: 999px; background: var(--glass); -webkit-backdrop-filter: blur(16px) saturate(1.8); backdrop-filter: blur(16px) saturate(1.8); box-shadow: inset 0 0 0 .5px var(--glass-edge); }
  .b { height: 36px; padding: 0 16px; border-radius: 999px; display: inline-flex; align-items: center; font: 600 14px var(--font-sans); }
</style>
</head>
<body>
<div class="cv">
  <div class="win" aria-hidden="true">
    <div class="card"><div class="cat">Mindful minutes</div><div class="fig">34<small>min</small></div></div>
    <div class="bar"><span class="b" style="background: var(--accent-fill); color: #FFFFFF">Start</span><span class="b" style="background: var(--fill); color: var(--ink)">Later</span><span class="b" style="background: var(--hl-mint-wash); color: var(--hl-mint)">Share</span></div>
  </div>
  <div class="txt">
    <h1 class="name">App Kit</h1>
    <p class="tag">SwiftUI on Apple's own neutrals and system colours: capsule buttons tinted like Notes highlights, Rounded figures, glass over content.</p>
  </div>
</div>
</body>
</html>
''')

# ------------------------------------------------------------------ README + web section
readme = rd('README.md')
readme = readme[readme.index('Warm paper'):] if readme.startswith('> **Archived') else readme
body = readme[readme.index('## Content'):]
body = body.replace('''- `ink` on `surface` for body text; `ink-soft` for secondary lines. Both pass on `ground`, `surface` and `surface-sunk` in both themes.''', '''- Neutrals are Apple's: `ground` is the grouped background (#F2F2F7, black in dark), `surface` the grouped cell (white, #1C1C1E), `surface-sunk` systemGray5. `ink` and `ink-soft` pass 4.5:1 on all three in both themes.''')
body = re.sub(r'- Tinted fills pair with their own ink:.*\n', '- Tinted fills pair with their own ink: `accent-ink` on `accent-wash`, `warn-ink` on `warn-wash`, `ok` on `ok-wash`, `bad` on `bad-wash`, `hl-<colour>` on `hl-<colour>-wash`.\n', body)
body = re.sub(r'- On a `clay` fill.*\n', '- On `accent-fill` use `on-accent`. `accent-fill` is the accent stepped 20% toward black so white labels pass 4.5:1; `accent` itself stays the system colour for marks, rings and tints.\n', body)
body = body.replace('(`series-1` unless the page already means something by mint)', '(`series-1` unless the screen already means something by mint)')
body = re.sub(r'- `warn` is olive.*\n', '- Status uses the system green, orange and red, stepped for text. Each still comes with a word or glyph.\n', body)
body = re.sub(r'- Dark is designed, not inverted:.*\n', "- Dark is Apple's: a black `ground`, `surface` one step up at #1C1C1E, every system colour at its dark value.\n", body)
body = body.replace('One family: SF. `display` (SF Pro Display, `.largeTitle` weight on Apple) is for one hero figure or page headline per screen, at most. It never sets UI chrome. Off Apple devices every role falls back to Instrument Sans and JetBrains Mono.',
  'One family: SF, in the cuts the system gives you. `design: .default` for UI, `.rounded` (SF Pro Rounded) for Health-style figures (`figure`), `.monospaced` (SF Mono) for codes and timers, SF Pro Text with extra leading for long reading (`script`); SF Compact is the watch face and only appears on watchOS and widgets. Nothing lighter than Regular.')
body = body.replace('Long-read web pages (prep sheets, briefs, study guides) use the Paper profile: see the Paper documents section.', 'Web pages and artifacts use **Artifact Kit**, the same palette for the browser; see the Web section.')
body = body.replace('- Radii: `radius-sm` (6) thumbnails and badges, `radius-md` (10) controls and rows,', '- Radii: buttons and pills are capsules (`radius-pill`, as in iOS 26); `radius-sm` (6) thumbnails and badges, `radius-md` (10) inputs and rows,')
body = body.replace('- Focus ring: 2px solid `signal`, offset 2px, on every interactive element (3:1 or better on every surface).', '- Focus ring: 2px solid `accent`, offset 2px (the system focus ring follows the accent).')
body = body.replace('Button, FilterPill, SegmentedControl, Badge, Flag, StatTile, Panel, ListRow, Highlight, BarChart. Each card below has its guidelines and a live preview. In SwiftUI, build each as a `View` or `ButtonStyle` reading these tokens from an asset catalog color set per color token.',
  'Button, FilterPill, SegmentedControl, Badge, Flag, StatTile, Panel, ListRow, Highlight, BarChart. Each card below has its guidelines and a live preview. In SwiftUI prefer the system control (`.bordered`, `.borderedProminent`, `.glass`, `Picker(.segmented)`) and read colours from `AppKit.swift` in `~/developer/app-kit/swift`, which mirrors these tokens.')
body = body.replace("SF Symbols on Apple, regular weight, sized to the text beside them. On the web, no icon font is shipped: use plain glyphs (`->`, `+`, `x`) in the mono face, or inline SVGs drawn at 1.5px stroke in `currentColor`. There is no logo; apps set their name in `title-3` sans.",
  "SF Symbols, regular weight, sized to the text beside them, hierarchical rendering in the tint. There is no logo; apps set their name in `title-3`.")
intro = '''SwiftUI on Apple's own neutrals and system colours: capsule buttons tinted like Notes highlights, Rounded figures, glass for controls that float over content. The native half of three kits: **App Kit** (Mac, iPhone, iPad and Watch apps: WA Fish Map, Footage Library, Claude Spinner), **Artifact Kit** (web pages and artifacts, same palette) and **Terminal Kit** (the macOS Terminal look). Source: `~/developer/app-kit`.

## Principles

- **Defer to the system.** Use the system controls, colours and text styles first; these tokens describe what they already do, for places you draw yourself.
- **The accent is for acting.** `accent` (the app's accent, the person's on the Mac) marks what you can act on and what is selected. Status, charts and highlights never borrow it.
- **Translucent, not heavy.** Tints are washes (12%, 20% in dark), selection is a wash, and only one filled button per view.
- **Glass floats, content doesn't.** Liquid Glass is for toolbars, tab bars and controls over content. Lists, charts and reading text stay on opaque `surface`.
- **A scale is not a status.** `heat-1` to `heat-4` rank data. `bad` means something failed.

'''
w('README.md', intro + body)
w('paper-documents.md', '''# Web

Web pages and artifacts use **Artifact Kit**, built on the same neutrals, system colours and SF roles as App Kit, with Mac-sized controls (13px, 28px buttons) and the chart components (including the Health-style summary, highlight and range charts). Source: `~/developer/artifact-kit`.

| App Kit (SwiftUI) | Artifact Kit (CSS) |
|---|---|
| `ground` | `--bk-bg` |
| `surface` | `--bk-surface` |
| `surface-sunk` | `--bk-sunk` |
| `ink` · `ink-soft` | `--bk-ink` · `--bk-soft` |
| `hair` · `edge` | `--bk-hair` · `--bk-edge` |
| `accent` · `accent-ink` | `--os` · `--bk-accent` |
| `accent-fill` | `--os-fill` |
| `ok` `warn` `bad` | `--bk-ok` `--bk-warn` `--bk-bad` |
| `hl-*` | `--hl-*` |
| `chart-base` · `chart-mid` | `--chart-base` · `--chart-mid` |
| Button `tinted` / `filled` / `gray` / `plain` / `glass` | `.btn` / `.btn--filled` / `.btn--gray` / `.btn--plain` / `.btn--glass` |
''')

# ------------------------------------------------------------------ SwiftUI mirror
def rgba(v):
    v = v.strip()
    if v.startswith('#'):
        r, g, b = (int(v[i:i + 2], 16) / 255 for i in (1, 3, 5)); return r, g, b, 1.0
    n = [float(x) for x in re.findall(r'[\d.]+', v)]; return n[0] / 255, n[1] / 255, n[2] / 255, n[3]
def camel(s): return re.sub(r'-([a-z0-9])', lambda m: m.group(1).upper(), s)
lines = ['// App Kit colours for SwiftUI. Generated from tokens.json by app_build.py; do not edit.',
         '// Prefer system colours where one exists (Color.accentColor, .primary, .secondary);',
         '// these cover the rest and match Artifact Kit on the web.', 'import SwiftUI', '',
         '#if canImport(UIKit)', 'import UIKit',
         'private func dyn(_ l: (Double, Double, Double, Double), _ d: (Double, Double, Double, Double)) -> Color {',
         '    Color(UIColor { $0.userInterfaceStyle == .dark ? UIColor(red: d.0, green: d.1, blue: d.2, alpha: d.3) : UIColor(red: l.0, green: l.1, blue: l.2, alpha: l.3) })', '}',
         '#else', 'import AppKit',
         'private func dyn(_ l: (Double, Double, Double, Double), _ d: (Double, Double, Double, Double)) -> Color {',
         '    Color(NSColor(name: nil) { $0.bestMatch(from: [.darkAqua, .aqua]) == .darkAqua ? NSColor(red: d.0, green: d.1, blue: d.2, alpha: d.3) : NSColor(red: l.0, green: l.1, blue: l.2, alpha: l.3) })', '}',
         '#endif', '', 'public extension Color {', '    enum Kit {']
for t in colors:
    v = t['value']; l = v['light'] if isinstance(v, dict) else v; d = v.get('dark', l) if isinstance(v, dict) else v
    f = lambda c: '(%.3f, %.3f, %.3f, %.2f)' % rgba(c)
    lines.append(f"        /// {t['usage'][:110]}")
    lines.append(f"        public static let {camel(t['name'])} = dyn({f(l)}, {f(d)})")
lines += ['    }', '}', '', 'public extension Font {', '    enum Kit {',
          '        /// Health-style figure: SF Pro Rounded, bold.',
          '        public static let figure = Font.system(.largeTitle, design: .rounded).bold()',
          '        public static let figureSmall = Font.system(.title2, design: .rounded).bold()',
          '        /// Long reading: SF Pro Text body; add .lineSpacing(6).', '        public static let script = Font.body',
          '        /// Mono uppercase key above a value.', '        public static let label = Font.caption2.monospaced().weight(.semibold)',
          '    }', '}', '']
w('swift/AppKit.swift', '\n'.join(lines), OUT)
print('App Kit written to', OUT)
