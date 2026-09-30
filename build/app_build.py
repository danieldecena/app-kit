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
 T('ink-faint', 'rgba(60, 60, 67, 0.30)', 'rgba(235, 235, 245, 0.30)', 'Tertiary text (tertiaryLabel, translucent): absences ("not recorded"), panel titles, the empty-slot outline. Under 3:1, so never the only copy of a reading.'),
 T('hair', '#D1D1D6', '#38383A', 'Hairline dividers (separator). Decorative only: never the only boundary of a control.'),
 T('edge', '#86868B', '#7C7C80', 'Outlines of interactive controls (3:1 or better on ground and surface).'),
 T('fill', 'rgba(118, 118, 128, 0.12)', 'rgba(118, 118, 128, 0.24)', 'The system fill: gray buttons, off filter pills, hover and pressed rows. Translucent.'),
 T('fill-hover', 'rgba(118, 118, 128, 0.20)', 'rgba(118, 118, 128, 0.32)', 'The system fill one step stronger: hover on gray buttons.'),
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
# Filled-button fill and label per colour. Purple, pink and blue are the system colour stepped 20% toward
# black so white passes 4.5:1; orange and mint stay the system colour with ink labels.
HL_FILL = {'purple': ('#8C42B2', '#9948C2', '#FFFFFF'), 'pink': ('#CC2444', '#CC2C4C', '#FFFFFF'), 'orange': ('#FF9500', '#FF9F0A', '#1D1D1F'),
           'mint': ('#00C7BE', '#63E6E2', '#1D1D1F'), 'blue': ('#0062CC', '#086ACC', '#FFFFFF')}
for k, (lt, lw, dt, dw) in HL.items():
    colors.append(T(f'hl-{k}', lt, dt, f'Highlighted text in {k}, as in Apple Notes: bold, on hl-{k}-wash (4.5:1 or better in both themes). Also the ink of a {k} tinted button.'))
    colors.append(T(f'hl-{k}-wash', lw, dw, f'The system {k} at 10% (16% dark), translucent: highlight and {k} tinted-button fill.'))
    fl, fd, on = HL_FILL[k]
    colors.append(T(f'hl-{k}-fill', fl, fd, f'Filled {k} button: 4.5:1 or better under hl-{k}-on in both themes.'))
    colors.append(T(f'hl-{k}-on', on, on, f'Label on hl-{k}-fill.'))
# Purple alone hovers from the system colour rather than its darker fill, as it did before the tint tokens.
colors.append(T('hl-purple-tint', '#AF52DE', '#BF5AF2', 'The system purple: what a purple tinted button mixes its hover wash from.'))
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
   {'name': 'figure-md', 'family': 'round', 'fontSize': '28px', 'lineHeight': '32px', 'fontWeight': 700, 'sample': '1,284', 'usage': 'Stat tile values: .system(.title, design: .rounded).bold().'},
   {'name': 'figure-sm', 'family': 'round', 'fontSize': '22px', 'lineHeight': '26px', 'fontWeight': 700, 'sample': '90 sec', 'usage': 'Values in a comparison: .system(.title2, design: .rounded).bold().'}]},
 {'name': 'Reading', 'family': 'sans', 'styles': [
   {'name': 'script', 'family': 'sans', 'fontSize': '17px', 'lineHeight': '28px', 'fontWeight': 400, 'sample': 'I build the systems behind campaigns.', 'usage': 'Long reading in SF Pro Text: .body with .lineSpacing(6).'}]},
 {'name': 'Glance', 'family': 'compact', 'styles': [
   {'name': 'glance', 'family': 'compact', 'fontSize': '15px', 'lineHeight': '18px', 'fontWeight': 600, 'sample': '1d 7h', 'usage': 'watchOS and widgets only; SF Compact is the watch face.'}]}]
text = next(g for g in tok['type']['groups'] if g['name'] == 'Text')['styles']
text.insert([s['name'] for s in text].index('caption') + 1, {'name': 'caption-2', 'fontSize': '11px', 'lineHeight': '13px', 'fontWeight': 400, 'sample': 'Mon', 'usage': 'Chart ticks and the smallest labels, never sentences: .caption2.'})
# From Footage Library's detail cards. letterSpacing in px is the SwiftUI .tracking value in points.
text.insert([s['name'] for s in text].index('caption-2') + 1, {'name': 'panel-title', 'fontSize': '11px', 'lineHeight': '13px', 'fontWeight': 600, 'letterSpacing': '0.8px', 'sample': 'CAPTURE', 'usage': 'Panel titles, uppercase in ink-faint: .caption2.weight(.semibold) + .tracking(0.8) + .foregroundStyle(.tertiary).'})
# Appended after label, so a rule that matches both by size alone still resolves to label.
next(g for g in tok['type']['groups'] if g['name'] == 'Mono')['styles'] += [
 {'name': 'eyebrow', 'fontSize': '11px', 'lineHeight': '13px', 'fontWeight': 600, 'letterSpacing': '1.2px', 'sample': 'IMPORTING', 'usage': 'Spaced capitals naming a figure or a slot: .caption2.monospaced().weight(.semibold) + .tracking(1.2), uppercased.'},
 {'name': 'fact', 'fontSize': '12px', 'lineHeight': '16px', 'fontWeight': 400, 'sample': '4.21 GB', 'usage': 'Fact values, so they line up down a panel: .system(.caption, design: .monospaced).'}]
tok['motion'] = {'note': 'State changes on controls. Under prefers-reduced-motion they drop to none.', 'tokens': [
 {'name': 'motion-fast', 'value': '150ms', 'usage': 'Hover and press feedback. SwiftUI: .easeOut(duration: 0.15).'},
 {'name': 'motion-ease', 'value': 'ease-out', 'usage': 'The curve for every control transition: quick to respond, soft to settle.'}]}
tok['stroke'] = {'note': 'Outlines that carry a state, drawn inside the edge. Separation between surfaces stays surface against ground.', 'tokens': [
 {'name': 'stroke-outline', 'value': '1.5px', 'usage': 'State outlines: act and live panels, the empty slot, a selected filter pill, an attention tile. SwiftUI: .strokeBorder(color, lineWidth: 1.5).'},
 {'name': 'stroke-dash', 'value': '6 4', 'usage': 'The empty slot: 6 on, 4 off, in ink-faint. SwiftUI: StrokeStyle(lineWidth: 1.5, dash: [6, 4]).'}]}
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
for a in ('.dc-tile-attn { box-shadow: inset 0 0 0 1.5px var(--signal); }', '.dc-tile-attn .dc-tile-meter > span { background: var(--signal); }'):
    assert a in css, a; css = css.replace(a, a.replace('--signal', '--warn'))
css = css.replace('.dc-tile-attn .dc-tile-meter > span', '.dc-tile-attn .dc-tile-meter { background: var(--warn-wash); }\n.dc-tile-attn .dc-tile-meter > span')
for a, b in R: css = css.replace(a, b)
BTN_OLD = css[css.index('/* Button */'):css.index('/* FilterPill */')]
BTN = '''/* Button: iOS 26 capsules in the Notes highlight colours, translucent */
.dc-btn { --tint: var(--accent); --tint-ink: var(--accent-ink); --tint-wash: var(--accent-wash); --tint-fill: var(--accent-fill); --tint-on: var(--on-accent);
  min-height: var(--touch); padding: 0 20px; border-radius: var(--radius-pill); font: 600 15px/20px var(--font-sans); cursor: pointer; display: inline-flex; align-items: center; justify-content: center; gap: var(--space-4); border: 0; transition: background-color var(--motion-fast) var(--motion-ease), filter var(--motion-fast) var(--motion-ease); }
.dc-btn-tinted { background: var(--tint-wash); color: var(--tint-ink); }
.dc-btn-tinted:hover { background: color-mix(in srgb, var(--tint) 18%, transparent); }
.dc-btn-filled, .dc-btn-primary { background: var(--tint-fill); color: var(--tint-on); }
.dc-btn-filled:hover, .dc-btn-primary:hover { filter: brightness(1.08); }
.dc-btn-gray, .dc-btn-secondary { background: var(--fill); color: var(--ink); }
.dc-btn-gray:hover, .dc-btn-secondary:hover { background: var(--fill-hover); }
.dc-btn-plain { background: transparent; color: var(--tint-ink); padding: 0 var(--space-4); }
.dc-btn-plain:hover { background: var(--fill); }
.dc-btn-glass { background: var(--glass); color: var(--ink); -webkit-backdrop-filter: blur(16px) saturate(1.8); backdrop-filter: blur(16px) saturate(1.8); box-shadow: inset 0 0 0 .5px var(--glass-edge), var(--shadow-glass); }
.dc-btn-destructive { --tint: var(--bad); --tint-ink: var(--bad); --tint-wash: var(--bad-wash); background: var(--tint-wash); color: var(--tint-ink); }
.dc-tint-purple { --tint: var(--hl-purple-tint); --tint-ink: var(--hl-purple); --tint-wash: var(--hl-purple-wash); --tint-fill: var(--hl-purple-fill); --tint-on: var(--hl-purple-on); }
.dc-tint-pink { --tint: var(--hl-pink-fill); --tint-ink: var(--hl-pink); --tint-wash: var(--hl-pink-wash); --tint-fill: var(--hl-pink-fill); --tint-on: var(--hl-pink-on); }
.dc-tint-orange { --tint: var(--hl-orange-fill); --tint-ink: var(--hl-orange); --tint-wash: var(--hl-orange-wash); --tint-fill: var(--hl-orange-fill); --tint-on: var(--hl-orange-on); }
.dc-tint-mint { --tint: var(--hl-mint-fill); --tint-ink: var(--hl-mint); --tint-wash: var(--hl-mint-wash); --tint-fill: var(--hl-mint-fill); --tint-on: var(--hl-mint-on); }
.dc-tint-blue { --tint: var(--hl-blue-fill); --tint-ink: var(--hl-blue); --tint-wash: var(--hl-blue-wash); --tint-fill: var(--hl-blue-fill); --tint-on: var(--hl-blue-on); }
.dc-btn:disabled { opacity: .4; cursor: default; filter: none; }

'''
css = css.replace(BTN_OLD, BTN)
PANEL_OLD = css[css.index('/* Panel */'):css.index('/* ListRow */')]
css = css.replace(PANEL_OLD, '''/* Panel: Footage Library's detail card, and its Charts plate states */
.dc-panel { position: relative; background: var(--surface); border-radius: var(--radius-lg); padding: var(--space-6); display: flex; flex-direction: column; gap: 10px; }
.dc-panel-head { display: flex; align-items: baseline; justify-content: space-between; gap: var(--space-5); }
.dc-panel-title { font: 600 11px/13px var(--font-sans); letter-spacing: var(--tracking-panel-title); text-transform: uppercase; color: var(--ink-faint); margin: 0; }
.dc-panel-meta { font: 400 13px/18px var(--font-sans); color: var(--ink-soft); }
.dc-panel-act { box-shadow: inset 0 0 0 var(--stroke-outline) var(--warn); }
.dc-panel-live { box-shadow: inset 0 0 0 var(--stroke-outline) var(--accent); }
.dc-panel-empty { background: transparent; }
.dc-panel-dash { position: absolute; top: calc(var(--stroke-outline) / 2); left: calc(var(--stroke-outline) / 2); width: calc(100% - var(--stroke-outline)); height: calc(100% - var(--stroke-outline)); overflow: visible; pointer-events: none; }
.dc-panel-dash rect { rx: calc(var(--radius-lg) - var(--stroke-outline) / 2); fill: none; stroke: var(--ink-faint); stroke-width: var(--stroke-outline); stroke-dasharray: var(--stroke-dash); }
.dc-panel-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap: var(--space-5); }

/* Fact: label and value rows */
.dc-facts { display: grid; grid-template-columns: max-content minmax(0, 1fr); gap: var(--space-4) 18px; align-items: baseline; margin: 0; }
.dc-fact-label { font: 400 12px/16px var(--font-sans); color: var(--ink-soft); margin: 0; }
.dc-fact-value { font: 400 12px/16px var(--font-mono); color: var(--ink); margin: 0; min-width: 0; overflow-wrap: anywhere; font-variant-numeric: tabular-nums; }
.dc-fact-muted { color: var(--ink-faint); }
.dc-fact-line { display: flex; white-space: nowrap; }
.dc-fact-line > span:first-child { overflow: hidden; text-overflow: ellipsis; }
.dc-fact-line > span:last-child { flex-shrink: 0; }

/* Eyebrow */
.dc-eyebrow { font: 600 11px/13px var(--font-mono); letter-spacing: var(--tracking-eyebrow); text-transform: uppercase; color: var(--ink-soft); }
.dc-eyebrow-act { color: var(--warn); }

/* Toolbar: one row pinned above scrolling content */
.dc-toolbar { position: sticky; top: 0; z-index: 1; padding: var(--space-3) var(--space-6); background: var(--glass); -webkit-backdrop-filter: blur(16px) saturate(1.8); backdrop-filter: blur(16px) saturate(1.8); box-shadow: 0 1px 0 var(--hair); }
.dc-toolbar-row { display: flex; align-items: center; gap: var(--space-4); }
.dc-toolbar-spacer { flex: 1; }
.dc-toolbar .dc-btn { min-height: 32px; }
.dc-toolbar-icon { width: 32px; padding: 0; }
.dc-toolbar-icon[aria-disabled="true"] { opacity: .4; cursor: default; }
.dc-search { flex: 1; max-width: 360px; min-height: 32px; padding: 0 10px; display: flex; align-items: center; gap: var(--space-3); border-radius: var(--radius-pill); background: var(--fill); color: var(--ink-soft); }
.dc-search:focus-within { outline: 2px solid var(--accent); outline-offset: 2px; }
.dc-search input { flex: 1; min-width: 0; border: 0; padding: 0; background: none; outline: none; font: 400 15px/20px var(--font-sans); color: var(--ink); }
.dc-search input::placeholder { color: var(--ink-soft); }
.dc-search-clear { display: inline-flex; border: 0; padding: 0; background: none; color: var(--ink-soft); cursor: pointer; }
.dc-toolbar-notice { margin: var(--space-3) 0 0; padding: var(--space-3) var(--space-5); border-radius: var(--radius-sm); background: var(--surface); font: 400 13px/18px var(--font-sans); color: var(--ink-soft); }
.dc-toolbar-notice-bad { color: var(--bad); }

''')
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
assert css.count('inset 0 0 0 1.5px') == 2
css = css.replace('inset 0 0 0 1.5px', 'inset 0 0 0 var(--stroke-outline)')
assert 'clay' not in re.sub(r'dc-(badge|flag)-(clay|signal)', '', css), [l for l in css.split('\n') if 'clay' in l]
assert '--signal' not in css
# Every font size reaches the stylesheet as a tokens.json type style: --type-<style>, with a weight
# override where a control sets a style semibold, as SwiftUI does with .weight(.semibold).
TYPE = {s['name']: (s['fontWeight'], s['fontSize'], s['lineHeight'], s.get('family', g['family'])) for g in tok['type']['groups'] for s in g['styles']}
css = css.replace('font-family: var(--font-sans); font-size: 16px; line-height: 21px;', 'font: 400 16px/21px var(--font-sans);')
# The thumbnail placeholder was 10/12, the only size below the scale; it takes label, one step up.
css = css.replace('font: 600 10px/12px var(--font-mono);', 'font: 600 11px/14px var(--font-mono);')
def type_var(m):
    wt, size, line, fam = int(m[1]), m[2], m[3], m[4]
    hits = [n for n, (_, sz, lh, f) in TYPE.items() if (sz, f) == (size, fam) and line in (None, lh)]
    assert hits, m[0]
    exact = [n for n in hits if TYPE[n][0] == wt]
    return f'font: var(--type-{exact[0]})' if exact else f'font: var(--type-{hits[0]}); font-weight: {wt}'
css = re.sub(r'font: (\d+) (\d+px)(?:/(\d+px))? var\(--font-(\w+)\)', type_var, css)
assert not re.search(r'font(-size)?:[^;}]*\d+px', css), re.findall(r'font(?:-size)?:[^;}]*\d+px', css)
# Tracking and stroke vars ride along in case the host page only maps the families it knows.
css = (':root {\n' + ''.join(f'  --type-{n}: {wt} {sz}/{lh} var(--font-{f});\n' for n, (wt, sz, lh, f) in TYPE.items())
       + ''.join(f"  --tracking-{s['name']}: {s['letterSpacing']};\n" for g in tok['type']['groups'] for s in g['styles'] if 'letterSpacing' in s)
       + ''.join(f"  --{t['name']}: {t['value']};\n" for t in tok['stroke']['tokens']) + '}\n' + css)
w('components/bundle.css', css)

# ------------------------------------------------------------------ bundle.js
js = rd('components/bundle.js')
js = js.replace('"namespace":"Decena"', '"namespace":"AppKit"')
js = js.replace('var variant = p.variant || "secondary";\n    return h("button", Object.assign({ type: "button" }, omit(p, ["variant", "className", "children"]), {\n      className: cx("dc-btn", "dc-btn-" + variant, p.className)',
                'var variant = p.variant || "tinted";\n    return h("button", Object.assign({ type: "button" }, omit(p, ["variant", "tint", "className", "children"]), {\n      className: cx("dc-btn", "dc-btn-" + variant, p.tint && p.tint !== "accent" && "dc-tint-" + p.tint, p.className)')
SEG_OLD = js[js.index('  function SegmentedControl(p) {'):js.index('  function Badge(p) {')]
SEG = '''  function SegmentedControl(p) {
    var st = React.useState(p.value != null ? p.value : p.defaultValue);
    var value = p.value != null ? p.value : st[0];
    function pick(v) { if (p.value == null) st[1](v); if (p.onChange) p.onChange(v); }
    var vals = (p.options || []).map(function (o) { return typeof o === "string" ? o : o.value; });
    var stop = Math.max(vals.indexOf(value), 0);
    // Radio group keys: one tab stop, on the chosen segment; arrows move and choose, wrapping; Home and End jump.
    function onKey(e, i) {
      var n = vals.length, j = { ArrowRight: i + 1, ArrowDown: i + 1, ArrowLeft: i - 1, ArrowUp: i - 1, Home: 0, End: n - 1 }[e.key];
      if (j == null) return;
      e.preventDefault();
      j = (j + n) % n;
      e.currentTarget.parentNode.children[j].focus();
      pick(vals[j]);
    }
    return h("div", { className: "dc-seg", role: "radiogroup", "aria-label": p.label },
      (p.options || []).map(function (o, i) {
        var v = vals[i];
        var label = typeof o === "string" ? o : o.label;
        return h("button", {
          key: v, type: "button", role: "radio", className: "dc-seg-opt",
          "aria-checked": v === value ? "true" : "false", tabIndex: i === stop ? 0 : -1,
          onClick: function () { pick(v); }, onKeyDown: function (e) { onKey(e, i); }
        }, label);
      }));
  }

'''
js = js.replace(SEG_OLD, SEG)
js = js.replace('var FLAG_GLYPH = { warn: "!", bad: "x", signal: "->" };', 'var FLAG_GLYPH = { warn: "!", bad: "x", accent: "->", signal: "->" };')
js = js.replace('window.Decena = Object.assign(window.Decena || {}, {', 'window.AppKit = window.Decena = Object.assign(window.AppKit || {}, {')
PANEL_OLD = js[js.index('  function Panel(p) {'):js.index('  function ListRow(p) {')]
js = js.replace(PANEL_OLD, '''  function Panel(p) {
    var tone = p.tone && p.tone !== "plain" ? p.tone : null;
    return h("section", { className: cx("dc-panel", tone && "dc-panel-" + tone, p.className) },
      tone === "empty" ? h("svg", { className: "dc-panel-dash", "aria-hidden": "true" }, h("rect", { width: "100%", height: "100%", rx: 13.25 })) : null,
      p.title || p.meta ? h("header", { className: "dc-panel-head" },
        p.title ? h("h3", { className: "dc-panel-title" }, p.title) : null,
        p.meta ? h("span", { className: "dc-panel-meta" }, p.meta) : null) : null,
      p.children);
  }

  // One <dt>/<dd> pair; place inside <dl class="dc-facts">. oneLine truncates in the middle, keeping the tail.
  function Fact(p) {
    var none = p.value == null || p.value === "";
    var text = none ? "not recorded" : String(p.value);
    var tail = p.oneLine && !none ? Math.min(12, Math.floor(text.length / 2)) : 0;
    return h(React.Fragment, null,
      h("dt", { className: "dc-fact-label" }, p.label),
      h("dd", { className: cx("dc-fact-value", (none || p.muted) && "dc-fact-muted", p.oneLine && "dc-fact-line"), title: p.oneLine ? text : undefined },
        tail ? [h("span", { key: "head" }, text.slice(0, -tail)), h("span", { key: "tail" }, text.slice(-tail))] : text));
  }

  function Eyebrow(p) {
    return h("span", { className: cx("dc-eyebrow", p.act && "dc-eyebrow-act", p.className) }, p.children);
  }

  function Toolbar(p) {
    var st = React.useState("");
    var query = p.query != null ? p.query : st[0];
    function setQuery(v) { if (p.query == null) st[1](v); if (p.onQueryChange) p.onQueryChange(v); }
    var icon = { width: 14, height: 14, viewBox: "0 0 16 16", fill: "none", stroke: "currentColor", strokeWidth: 1.5, strokeLinecap: "round", "aria-hidden": "true" };
    return h("div", { className: cx("dc-toolbar", p.className) },
      h("div", { className: "dc-toolbar-row" },
        p.children,
        p.searchLabel ? h("label", { className: "dc-search" },
          h("svg", icon, h("circle", { cx: 7, cy: 7, r: 4.75 }), h("path", { d: "M10.5 10.5 14 14" })),
          h("input", { type: "text", value: query, placeholder: p.searchLabel, "aria-label": p.searchLabel, onChange: function (e) { setQuery(e.target.value); } }),
          query ? h("button", { type: "button", className: "dc-search-clear", "aria-label": "Clear search", onClick: function () { setQuery(""); } },
            h("svg", icon, h("path", { d: "M4.5 4.5l7 7M11.5 4.5l-7 7" }))) : null) : null,
        h("span", { className: "dc-toolbar-spacer" }),
        (p.tools || []).map(function (t) {
          // aria-disabled, not disabled, so the reason still shows as the tooltip.
          return h("button", {
            key: t.title, type: "button", className: "dc-btn dc-btn-gray dc-toolbar-icon", title: t.disabled || t.title, "aria-label": t.title,
            "aria-disabled": t.disabled ? "true" : undefined, onClick: t.disabled ? undefined : t.onClick
          }, t.icon);
        }),
        p.primary || null),
      h("div", { role: "status" },
        p.notice ? h("p", { className: cx("dc-toolbar-notice", p.noticeTone === "bad" && "dc-toolbar-notice-bad") }, p.notice) : null));
  }

''')
js = js.replace('{"name":"Panel"},', '{"name":"Panel"},{"name":"Fact"},{"name":"Eyebrow"},{"name":"Toolbar"},')
js = js.replace('Panel: Panel, ListRow: ListRow,', 'Panel: Panel, Fact: Fact, Eyebrow: Eyebrow, Toolbar: Toolbar, ListRow: ListRow,')
assert 'dc-tint-' in js and 'window.AppKit' in js and 'onKeyDown' in js and 'Toolbar: Toolbar' in js and '{"name":"Toolbar"}' in js
w('components/bundle.js', js)

# ------------------------------------------------------------------ index.d.ts
dts = rd('components/index.d.ts')
dts = dts.replace('/** Action button. `primary` (clay) at most once per view. */\nexport function Button(props: ButtonHTMLAttributes<HTMLButtonElement> & {\n  variant?: "primary" | "secondary" | "plain" | "destructive";',
                  '/** Action button, an iOS 26 capsule. `tinted` (translucent) is the default; `filled` at most once per view. */\nexport function Button(props: ButtonHTMLAttributes<HTMLButtonElement> & {\n  variant?: "tinted" | "filled" | "gray" | "plain" | "glass" | "destructive" | "primary" | "secondary";\n  /** The Notes highlight colours; accent by default. */\n  tint?: "accent" | "purple" | "pink" | "orange" | "mint" | "blue";')
dts = dts.replace('tone?: "neutral" | "hollow" | "clay" | "signal" | "ok" | "warn" | "bad";', 'tone?: "neutral" | "hollow" | "accent" | "ok" | "warn" | "bad";')
PANEL_DTS = 'export function Panel(props: { title?: ReactNode; meta?: ReactNode; children: ReactNode }): JSX.Element;'
assert PANEL_DTS in dts
dts = dts.replace(PANEL_DTS, '''/** Detail card: uppercase caption title, surface one step off the ground. `tone` marks a slot: `act` needs the person, `live` is working, `empty` has nothing yet. */
export function Panel(props: { title?: ReactNode; meta?: ReactNode; tone?: "plain" | "act" | "live" | "empty"; children?: ReactNode }): JSX.Element;
/** One label and value row, inside `<dl className="dc-facts">`. A null or empty value reads "not recorded" in ink-faint. */
export function Fact(props: { label: ReactNode; value?: string | number | null; muted?: boolean; oneLine?: boolean }): JSX.Element;
/** Spaced mono capitals naming a figure or a slot; `act` when it needs the person. */
export function Eyebrow(props: { act?: boolean; children: ReactNode }): JSX.Element;
export interface ToolbarTool {
  /** The tooltip and accessible name. */
  title: string;
  icon: ReactNode;
  onClick?: () => void;
  /** Why the tool is unavailable; replaces the tooltip. */
  disabled?: string;
}
/** One row pinned above scrolling content: search, icon tools, one filled primary action, and a notice after an action. */
export function Toolbar(props: {
  searchLabel?: string;
  query?: string;
  onQueryChange?: (query: string) => void;
  tools?: ToolbarTool[];
  /** One filled Button. */
  primary?: ReactNode;
  notice?: ReactNode;
  noticeTone?: "neutral" | "bad";
  /** Leading controls, such as a SegmentedControl. */
  children?: ReactNode;
}): JSX.Element;''')
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
docs['StatTile/README.md'] = rd('components/StatTile/README.md').replace('value in `value` (mono 28, tabular figures)', 'value in `figure` (SF Pro Rounded 28 bold, tabular figures, as in Health)').replace('`attention` draws a 1.5px `signal` ring and turns the meter `signal`', '`attention` draws a 1.5px `warn` ring and turns the meter `warn`, like a Panel `act` tone').replace("From Charts Tab's instrument panel and Footage Review Board.", 'The meter is `accent` on `accent-wash`.')
docs['ListRow/README.md'] = rd('components/ListRow/README.md').replace('Selected rows take `clay-wash`.', 'Selected rows take `accent-wash`, translucent.')
docs['BarChart/README.md'] = rd('components/BarChart/README.md').replace('A single-series chart is mint, because blue is `signal`. Orange comes last since it sits close to clay.', 'A single-series chart is mint, so it never reads as the blue accent.')
docs['SegmentedControl/README.md'] = '''# SegmentedControl

Picks exactly one of 2-5 views of the same content: Day / Week / Season.

- A `surface-sunk` track (`radius-md`, 3px inset); the chosen segment lifts to `surface` with `ink` text and `shadow-segment`, the rest sit in `ink-soft`. SwiftUI: `Picker(...).pickerStyle(.segmented)`.
- Segments are 38px tall, `space-6` side padding, 600 15/20. Keep labels to one or two words, all roughly the same length.
- `label` is required: it names the group for screen readers (`role="radiogroup"`). Pass `value` + `onChange` to control it, or `defaultValue` to let it hold its own state.
- `options` are strings, or `{ value, label }` when the label is not plain text.
- Keyboard, as a radio group: Tab lands on the chosen segment only; the arrow keys move and choose (wrapping), Home and End jump to the ends.
- Several filters at once, or more than 5 choices: use FilterPill instead.
'''
docs['Panel/README.md'] = r'''# Panel

Groups related content on a `surface` card, one step off the `ground`: Footage Library's detail card.

- `radius-lg` (14), `space-6` (16) padding, 10 between children. No border and no shadow; the surface step is the separation.
- `title` is the `panel-title` style: 11/13 semibold, uppercase, +0.8 tracking, in `ink-faint`. It names the card ("Capture", "Storage"), it is not a headline. `meta` sits on the trailing edge in `ink-soft` 13/18 for freshness or counts. Both are optional.
- `tone` marks a slot, from Footage's Charts plates. Pair it with an Eyebrow that says the same thing in words, since an outline alone is colour only.
  - `act`: needs the person (blocked, failed). A `stroke-outline` (1.5) ring in `warn`.
  - `live`: work in progress. The same ring in `accent`.
  - `empty`: nothing yet. No fill, a `stroke-dash` (6 on, 4 off) outline in `ink-faint`.
- Content goes straight in: Fact rows in a `.dc-facts` list, `.dc-row` / `.dc-stack` for layout. Nest a `.dc-list` for rows, not another Panel.
- Equal tiles: put panels in `.dc-panel-grid`, adaptive columns at least 250 wide, `space-5` (12) apart, every card as tall as the tallest in its row. Stack single panels `space-7` apart.

SwiftUI:

```swift
VStack(alignment: .leading, spacing: 10) {
    Text(title.uppercased()).font(Font.Kit.panelTitle).tracking(CGFloat.Kit.trackingPanelTitle).foregroundStyle(.tertiary)
    content
}
.padding(16)
.frame(maxWidth: .infinity, alignment: .leading)
.background(.background.secondary, in: RoundedRectangle(cornerRadius: 14, style: .continuous))
// act / live: .overlay { RoundedRectangle(cornerRadius: 14, style: .continuous).strokeBorder(color, lineWidth: CGFloat.Kit.strokeOutline) }
// empty: no background; .strokeBorder(.tertiary, style: StrokeStyle(lineWidth: CGFloat.Kit.strokeOutline, dash: CGFloat.Kit.strokeDash))
```

The equal-tile grid (Claude Spinner's detail pane): a custom `Layout` (`TileGrid(minimum: 250, spacing: 12)`) that fits as many columns as it can, measures each card at the column width, and places every card in a row at that row's tallest height; the card itself takes `.frame(maxHeight: .infinity, alignment: .topLeading)`. `LazyVGrid` can't do it, since it leaves each cell at its own height, and equalising across the whole grid instead stretches a short card to match a chart two rows away. On the web, `.dc-panel-grid` gets the same result from CSS grid's default row stretch.
'''
docs['Panel/preview.html'] = r'''<!-- @dsCard group="Layout" height=420 subtitle="Detail card, act, live and empty, in an equal-tile grid" -->
<!doctype html>
<html>
<head><meta charset="utf-8"><title>Panel</title></head>
<body>
<div id="root"></div>
<script>
  var D = window.AppKit, h = React.createElement;
  function facts(rows) { return h('dl',{className:'dc-facts'},rows.map(function (r) { return h(D.Fact,{key:r[0],label:r[0],value:r[1]}); })); }
  ReactDOM.createRoot(document.getElementById('root')).render(h('div',{className:'dc-panel-grid'},
    h(D.Panel,{title:'Capture',meta:'Sep 12'},facts([['Camera','FX3'],['Lens','24-70mm f/2.8'],['Frame rate','23.976 fps'],['Shutter',null]])),
    h(D.Panel,{title:'Storage'},facts([['Size','4.21 GB'],['Copies','2']])),
    h(D.Panel,{title:'Import',tone:'act'},h(D.Eyebrow,{act:true},'Blocked'),h('p',{style:{margin:0,color:'var(--ink-soft)'}},'Card is read-only. Unlock it and try again.')),
    h(D.Panel,{title:'Import',tone:'live'},h(D.Eyebrow,null,'Importing'),h('p',{style:{margin:0,color:'var(--ink-soft)'}},'18 of 42 clips')),
    h(D.Panel,{title:'Import',tone:'empty'},h(D.Eyebrow,null,'Idle'),h('p',{style:{margin:0,color:'var(--ink-soft)'}},'Insert a card to import.'))));
</script>
</body>
</html>
'''
docs['Fact/README.md'] = r'''# Fact

One label and its value, in the two-column grid of Footage Library's detail cards.

- Label in `caption` (12/16), `ink-soft`, proportional. Value in `fact` (SF Mono 12/16), `ink`, tabular figures, so values line up down a panel.
- Put the rows in `<dl class="dc-facts">`: labels size to the longest, 18 between the columns, `space-4` (8) between rows.
- A missing value reads "not recorded" in `ink-faint`: say it is absent rather than hiding the row, so the card keeps its shape. `muted` sets any other value in `ink-faint` (a placeholder, an inherited default).
- `oneLine` keeps a long value (a path, a hash, a device ID) to one line and truncates in the middle, since the tail is what tells two apart. The full value is the tooltip.
- Values are data, not prose: no sentences, no trailing punctuation. Real units ("4.21 GB", "23.976 fps").

SwiftUI:

```swift
Grid(alignment: .leading, horizontalSpacing: 18, verticalSpacing: 8) {
    GridRow {
        Text(label).font(.caption).foregroundStyle(.secondary)
        Text(value).font(Font.Kit.factValue).foregroundStyle(muted ? .tertiary : .primary)
            .lineLimit(oneLine ? 1 : nil).truncationMode(.middle)
            .textSelection(.enabled)
    }
}
```

With `oneLine`, add `.help(value)` and a Copy item in `.contextMenu`, since the middle of the value is hidden.
'''
docs['Fact/preview.html'] = r'''<!-- @dsCard group="Data" height=170 subtitle="Values, not recorded, and a middle-truncated path" -->
<!doctype html>
<html>
<head><meta charset="utf-8"><title>Fact</title></head>
<body>
<div id="root"></div>
<script>
  var D = window.AppKit, h = React.createElement;
  ReactDOM.createRoot(document.getElementById('root')).render(h('dl',{className:'dc-facts',style:{maxWidth:340}},
    h(D.Fact,{label:'Camera',value:'Sony FX3'}),
    h(D.Fact,{label:'Duration',value:'00:04:12:08'}),
    h(D.Fact,{label:'Location',value:null}),
    h(D.Fact,{label:'Codec',value:'Default (XAVC S-I)',muted:true}),
    h(D.Fact,{label:'File',value:'/Volumes/A001/PRIVATE/M4ROOT/CLIP/C0042_2026-09-12_dawn.MP4',oneLine:true})));
</script>
</body>
</html>
'''
docs['Eyebrow/README.md'] = r'''# Eyebrow

Spaced mono capitals over a figure or a slot, saying what state it is in: IMPORTING, BLOCKED, IDLE. From Footage Library's chart plates.

- `eyebrow` style: SF Mono 11/13 semibold, uppercase, +1.2 tracking, `ink-soft`.
- `act`: the thing needs the person; the text turns `warn`. Pair it with the `act` Panel tone, so the state is in a word as well as a colour.
- One or two words. It names the state, the line under it explains it.
- Not a section heading (that is `title-2` or a Panel title) and not a status chip (that is Badge).

SwiftUI:

```swift
Text(word.uppercased())
    .font(Font.Kit.eyebrow)
    .tracking(CGFloat.Kit.trackingEyebrow)
    .foregroundStyle(act ? Color.Kit.warn : .secondary)
```
'''
docs['Eyebrow/preview.html'] = r'''<!-- @dsCard group="Status" height=80 subtitle="Plain and act" -->
<!doctype html>
<html>
<head><meta charset="utf-8"><title>Eyebrow</title></head>
<body>
<div id="root"></div>
<script>
  var D = window.AppKit, h = React.createElement;
  ReactDOM.createRoot(document.getElementById('root')).render(h('div',{className:'dc-row',style:{gap:24}},
    h(D.Eyebrow,null,'Importing'),h(D.Eyebrow,null,'Idle'),h(D.Eyebrow,{act:true},'Blocked')));
</script>
</body>
</html>
'''
docs['Toolbar/README.md'] = r'''# Toolbar

One row pinned above the content it acts on, which scrolls under it. From Footage Library's library bar and Claude Spinner's session toolbar. A Mac pattern: on iPhone use the system toolbar and keep `touch` targets.

- Order: leading controls (a SegmentedControl), the search field, a spacer, icon tools, then the primary action last.
- Search (`searchLabel`): a capsule with a magnifying glass, 10 side padding, at least 32 tall, at most 360 wide, on the system `fill`. A clear button appears once there is a query.
- Tools: icon-only gray buttons, 32 square. The title is the tooltip and the accessible name. A tool that cannot run stays visible, dimmed, and its tooltip says why (`disabled: "No clip selected"`).
- `primary`: one filled Button, the thing the screen is for (Export, Send). At most one.
- `notice`: a line under the row that appears only after an action, saying what happened ("Exported 42 clips") or what failed (`noticeTone: "bad"`). It is announced to screen readers. Clear it on the next action.
- On the web the bar is `glass` with a `hair` bottom edge, sticky at the top.

SwiftUI, docked (Footage Library): the row is an `HStack(spacing: 10)` padded 16 by 6 over `.background(.bar)` with a `Divider()` under it. Search is `HStack(spacing: 6) { Image(systemName: "magnifyingglass").foregroundStyle(.secondary); TextField(...) }` with `.padding(.horizontal, 10)`, `.frame(minHeight: 32)`, `.background(.quaternary.opacity(0.5), in: Capsule())`, `.frame(maxWidth: 360)`. Tools are `.buttonStyle(.bordered)` with `.help(title)`; the primary is `.buttonStyle(.borderedProminent)`.

SwiftUI, native on macOS 26 and later (Claude Spinner's SessionToolbar): Liquid Glass instead of a bar. Wrap the row in `GlassEffectContainer(spacing: 8) { HStack(spacing: 8) { ... } }`, give the search field `.glassEffect(.regular, in: Capsule())` and the tools `.buttonStyle(.glass)` with `.help(reason ?? title)`, put the notice under it on a card (radius 6), and pin the whole stack with `.safeAreaInset(edge: .top, spacing: 0)` so content scrolls beneath.
'''
docs['Toolbar/preview.html'] = r'''<!-- @dsCard group="Navigation" height=300 subtitle="Search, tools, one primary action; a notice after Export" -->
<!doctype html>
<html>
<head><meta charset="utf-8"><title>Toolbar</title></head>
<body>
<div id="root"></div>
<script>
  var D = window.AppKit, h = React.createElement;
  var s = { width: 16, height: 16, viewBox: '0 0 16 16', fill: 'none', stroke: 'currentColor', strokeWidth: 1.5, strokeLinecap: 'round', strokeLinejoin: 'round', 'aria-hidden': 'true' };
  var tools = [
    { title: 'Import', icon: h('svg', s, h('path', { d: 'M8 2.5v8M4.5 7 8 10.5 11.5 7M3 13.5h10' })) },
    { title: 'Reveal in Finder', icon: h('svg', s, h('path', { d: 'M2.5 4.5h4l1.5 1.5h5.5v6.5h-11z' })), disabled: 'No clip selected' }];
  function Demo(props) {
    var n = React.useState(props.notice || null);
    var rows = ['C0042 dawn, north shore', 'C0043 dawn, launch', 'C0044 midday, dock', 'C0045 dusk, point', 'C0046 dusk, point'];
    return h('div', { style: { height: 132, overflow: 'auto', borderRadius: 14, background: 'var(--ground)' } },
      h(D.Toolbar, { searchLabel: 'Search clips', tools: tools, notice: n[0],
        primary: h(D.Button, { variant: 'filled', onClick: function () { n[1]('Exported 42 clips'); } }, 'Export') },
        h(D.SegmentedControl, { label: 'View', options: ['Grid', 'List'], defaultValue: 'Grid' })),
      h('div', { style: { padding: '8px 16px' } }, rows.map(function (r) { return h('div', { key: r, style: { padding: '6px 0', color: 'var(--ink-soft)' } }, r); })));
  }
  ReactDOM.createRoot(document.getElementById('root')).render(h('div', { className: 'dc-stack' }, h(Demo), h(Demo, { notice: 'Exported 42 clips' })));
</script>
</body>
</html>
'''
docs['Highlight/README.md'] = '''# Highlight

Marks the few words in running text that carry the point, like Apple Notes' highlighter.

- `color`: `purple` (default), `pink`, `orange`, `mint`, `blue`. Each is `hl-<color>` text on its `hl-<color>-wash`, semibold, tabular figures, `4px` radius; wraps cleanly across lines.
- Give each colour one meaning per document (for example numbers in pink, dates in blue) and keep it; colour alone must not carry the meaning.
- A word or short phrase, a few per paragraph at most. Renders as `<mark>`.
'''
for comp in ('FilterPill', 'SegmentedControl', 'StatTile', 'ListRow', 'Highlight', 'BarChart'):
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
def edit(s, a, b):
    assert s.count(a) == 1, a
    return s.replace(a, b)
body = edit(body, 'Uppercase only in the mono `label` style.', 'Uppercase only in the mono `label` and `eyebrow` styles and in panel titles.')
body = edit(body, 'pass 4.5:1 on all three in both themes.\n', 'pass 4.5:1 on all three in both themes.\n- `ink-faint` (tertiaryLabel) is for absences and chrome: "not recorded", panel titles, the empty-slot outline. It sits under 3:1, so it never carries the only copy of a reading.\n')
body = edit(body, '| Panel title | `title-3` 20/25 semibold | `.title3.weight(.semibold)` |', '| Panel title | `panel-title` 11/13 semibold, +0.8, uppercase, `ink-faint` | `.caption2.weight(.semibold)` + `.tracking(0.8)` + `.foregroundStyle(.tertiary)` |')
body = edit(body, '| Tile value | `value` mono 28/32 600 | `.system(size: 28, weight: .semibold, design: .monospaced)` |\n',
  '| Tile value | `value` mono 28/32 600 | `.system(size: 28, weight: .semibold, design: .monospaced)` |\n| Eyebrow | `eyebrow` mono 11/13 600, +1.2, uppercase | `.caption2.monospaced().weight(.semibold)` + `.tracking(1.2)` |\n| Fact label, value | `caption` 12/16 · `fact` mono 12/16 | `.caption` · `.system(.caption, design: .monospaced)` |\n')
body = edit(body, 'gaps between panels `space-7`;', 'gaps between stacked panels `space-7`, between tiles in a panel grid `space-5`;')
body = edit(body, 'Nest one step down: a `radius-md` row inside a `radius-lg` panel.\n',
  'Nest one step down: a `radius-md` row inside a `radius-lg` panel.\n- Detail cards tile in an equal grid: adaptive columns at least 250 wide, `space-5` (12) apart, every card as tall as the tallest in its row (see Panel).\n- A state outline is `stroke-outline` (1.5) inside the edge; the empty slot dashes it `stroke-dash` (6 on, 4 off) in `ink-faint`.\n')
body = edit(body, 'StatTile, Panel, ListRow, Highlight, BarChart. Each card below', 'StatTile, Panel, Fact, Eyebrow, Toolbar, ListRow, Highlight, BarChart. Each card below')
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
          '        /// Panel title: uppercased, .tracking(CGFloat.Kit.trackingPanelTitle), .foregroundStyle(.tertiary).',
          '        public static let panelTitle = Font.caption2.weight(.semibold)',
          '        /// Eyebrow: uppercased, .tracking(CGFloat.Kit.trackingEyebrow).',
          '        public static let eyebrow = Font.caption2.monospaced().weight(.semibold)',
          '        /// Fact value, beside a .caption label in .secondary.',
          '        public static let factValue = Font.system(.caption, design: .monospaced)',
          '    }', '}', '', 'public extension CGFloat {', '    enum Kit {']
for t in tok['stroke']['tokens']:
    n = [x.rstrip('px') for x in t['value'].split()]
    lines += [f"        /// {t['usage'][:110]}",
              f"        public static let {camel(t['name'])}: {'CGFloat' if len(n) == 1 else '[CGFloat]'} = {n[0] if len(n) == 1 else '[' + ', '.join(n) + ']'}"]
for g in tok['type']['groups']:
    for st in g['styles']:
        if st.get('letterSpacing', '').endswith('px'):
            lines.append(f"        public static let {camel('tracking-' + st['name'])}: CGFloat = {st['letterSpacing'][:-2]}")
lines += ['    }', '}', '']
w('swift/AppKit.swift', '\n'.join(lines), OUT)
print('App Kit written to', OUT)
