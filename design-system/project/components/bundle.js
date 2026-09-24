/* @ds-bundle: {"format":4,"namespace":"AppKit","components":[{"name":"Button"},{"name":"FilterPill"},{"name":"SegmentedControl"},{"name":"Badge"},{"name":"Flag"},{"name":"StatTile"},{"name":"Panel"},{"name":"ListRow"},{"name":"Highlight"},{"name":"BarChart"}]} */
(function () {
  var React = window.React;
  var h = React.createElement;
  function cx() { return Array.prototype.filter.call(arguments, Boolean).join(" "); }
  function omit(props, keys) {
    var out = {};
    for (var k in props) if (keys.indexOf(k) < 0) out[k] = props[k];
    return out;
  }

  function Button(p) {
    var variant = p.variant || "tinted";
    return h("button", Object.assign({ type: "button" }, omit(p, ["variant", "tint", "className", "children"]), {
      className: cx("dc-btn", "dc-btn-" + variant, p.tint && p.tint !== "accent" && "dc-tint-" + p.tint, p.className)
    }), p.children);
  }

  function FilterPill(p) {
    return h("button", Object.assign({ type: "button" }, omit(p, ["selected", "count", "className", "children"]), {
      className: cx("dc-pill", p.className),
      "aria-pressed": p.selected ? "true" : "false"
    }), p.children, p.count != null ? h("span", { className: "dc-pill-count" }, p.count) : null);
  }

  function SegmentedControl(p) {
    var st = React.useState(p.value != null ? p.value : p.defaultValue);
    var value = p.value != null ? p.value : st[0];
    function pick(v) { if (p.value == null) st[1](v); if (p.onChange) p.onChange(v); }
    return h("div", { className: "dc-seg", role: "radiogroup", "aria-label": p.label },
      (p.options || []).map(function (o) {
        var v = typeof o === "string" ? o : o.value;
        var label = typeof o === "string" ? o : o.label;
        return h("button", {
          key: v, type: "button", role: "radio", className: "dc-seg-opt",
          "aria-checked": v === value ? "true" : "false",
          onClick: function () { pick(v); }
        }, label);
      }));
  }

  function Badge(p) {
    return h("span", { className: cx("dc-badge", "dc-badge-" + (p.tone || "neutral"), p.className) }, p.children);
  }

  var FLAG_GLYPH = { warn: "!", bad: "x", accent: "->", signal: "->" };
  function Flag(p) {
    var tone = p.tone || "warn";
    return h("span", { className: cx("dc-flag", "dc-flag-" + tone, p.className), role: "status" },
      h("span", { className: "dc-flag-glyph", "aria-hidden": "true" }, FLAG_GLYPH[tone]), p.children);
  }

  function StatTile(p) {
    var pct = p.meter != null ? Math.max(0, Math.min(1, p.meter)) * 100 : null;
    return h("div", { className: cx("dc-tile", p.attention && "dc-tile-attn", p.className) },
      h("span", { className: "dc-tile-key" }, p.label),
      h("span", null,
        h("span", { className: "dc-tile-value" }, p.value),
        p.unit ? h("span", { className: "dc-tile-unit" }, p.unit) : null),
      pct != null ? h("div", { className: "dc-tile-meter", role: "meter", "aria-valuenow": Math.round(pct), "aria-valuemin": 0, "aria-valuemax": 100, "aria-label": p.label },
        h("span", { style: { width: pct + "%" } })) : null);
  }

  function Panel(p) {
    return h("section", { className: cx("dc-panel", p.className) },
      p.title || p.meta ? h("header", { className: "dc-panel-head" },
        p.title ? h("h3", { className: "dc-panel-title" }, p.title) : null,
        p.meta ? h("span", { className: "dc-panel-meta" }, p.meta) : null) : null,
      p.children);
  }

  function ListRow(p) {
    return h("button", Object.assign({ type: "button", role: "option" }, omit(p, ["title", "subtitle", "trailing", "thumb", "selected", "className"]), {
      className: cx("dc-listrow", p.className),
      "aria-selected": p.selected ? "true" : "false"
    }),
      p.thumb !== undefined ? h("span", { className: "dc-listrow-thumb", "aria-hidden": "true" }, p.thumb) : null,
      h("span", { className: "dc-listrow-text" },
        h("span", { className: "dc-listrow-title" }, p.title),
        p.subtitle ? h("span", { className: "dc-listrow-sub" }, p.subtitle) : null),
      p.trailing ? h("span", { className: "dc-listrow-trail" }, p.trailing) : null);
  }

  var HL = ["purple", "pink", "orange", "mint", "blue"];
  function Highlight(p) {
    var c = HL.indexOf(p.color) >= 0 ? p.color : "purple";
    return h("mark", { className: cx("dc-hl", "dc-hl-" + c, p.className) }, p.children);
  }

  // Ticks people already know (HIG: prefer familiar sequences): 1, 2, 2.5, 5 x 10^n.
  function niceStep(max, count) {
    var raw = max / count, mag = Math.pow(10, Math.floor(Math.log10(raw || 1)));
    var steps = [1, 2, 2.5, 5, 10];
    for (var i = 0; i < steps.length; i++) if (steps[i] * mag >= raw) return steps[i] * mag;
    return 10 * mag;
  }
  function fmt(n) { return n >= 1000 ? (n / 1000).toFixed(n % 1000 ? 1 : 0) + "k" : String(n); }

  function BarChart(p) {
    var data = p.data || [], series = p.series || [{ name: p.unit || "Value" }];
    // Emphasis: name the bar(s) that make the point; the rest go chart-base.
    var hi = p.highlight == null ? null : [].concat(p.highlight);
    var slot = Math.max(1, Math.min(5, p.color || 1));
    var W = 560, H = 200, top = 8, bottom = 24, axisW = 36, gap = 0.36;
    var plotW = W - axisW, plotH = H - top - bottom;
    var totals = data.map(function (d) { return (d.values || [d.value]).reduce(function (a, b) { return a + (b || 0); }, 0); });
    var max = Math.max.apply(null, totals.concat([1]));
    var step = niceStep(max, 3), yMax = Math.ceil(max / step) * step;
    var y = function (v) { return top + plotH - (v / yMax) * plotH; };
    var band = plotW / Math.max(data.length, 1), bw = band * (1 - gap);
    var ticks = []; for (var v = 0; v <= yMax + 1e-9; v += step) ticks.push(v);
    var bars = [];
    data.forEach(function (d, i) {
      var vals = d.values || [d.value], acc = 0, x = i * band + (band - bw) / 2;
      vals.forEach(function (val, k) {
        if (!val) return;
        var y0 = y(acc), y1 = y(acc + val); acc += val;
        var last = k === vals.length - 1 || !vals.slice(k + 1).some(Boolean);
        var r = last ? Math.min(4, bw / 2, y0 - y1) : 0;
        var hgt = y0 - y1, dPath = "M" + x + "," + y0 + "V" + (y1 + r) + (r ? "Q" + x + "," + y1 + " " + (x + r) + "," + y1 : "") +
          "H" + (x + bw - r) + (r ? "Q" + (x + bw) + "," + y1 + " " + (x + bw) + "," + (y1 + r) : "") + "V" + y0 + "Z";
        var cls = hi ? (hi.indexOf(d.label) >= 0 ? "dc-chart-s" + slot : "dc-chart-muted") : "dc-chart-s" + (k % 5 + 1);
        bars.push(h("path", { key: i + "-" + k, d: dPath, className: "dc-chart-bar " + cls },
          h("title", null, d.label + ", " + (series[k] ? series[k].name + " " : "") + val + (p.unit ? " " + p.unit : ""))));
        if (!last && hgt > 0) bars.push(h("line", { key: i + "-" + k + "s", x1: x, x2: x + bw, y1: y1, y2: y1, className: "dc-chart-sep" }));
        if (hi && last) bars.push(h("text", { key: i + "-v", x: x + bw / 2, y: y(acc) - 6, textAnchor: "middle", className: "dc-chart-val" }, fmt(acc)));
      });
    });
    return h("figure", { className: cx("dc-chart", p.className) },
      p.title ? h("figcaption", { className: "dc-chart-head" },
        h("span", { className: "dc-chart-title" }, p.title),
        p.summary ? h("span", { className: "dc-chart-summary" }, p.summary) : null) : null,
      h("svg", { viewBox: "0 0 " + W + " " + H, role: "img", "aria-label": p.summary || p.title || "Bar chart", className: "dc-chart-svg" },
        ticks.map(function (t) {
          return h("g", { key: "t" + t },
            h("line", { x1: 0, x2: plotW, y1: y(t), y2: y(t), className: t === 0 ? "dc-chart-base" : "dc-chart-grid" }),
            h("text", { x: plotW + 8, y: y(t) + 4, className: "dc-chart-tick" }, fmt(t)));
        }),
        bars,
        data.map(function (d, i) {
          return h("text", { key: "x" + i, x: i * band + band / 2, y: H - 6, textAnchor: "middle", className: "dc-chart-tick" }, d.label);
        })),
      hi ? h("div", { className: "dc-chart-legend" },
        h("span", { className: "dc-chart-key" }, h("i", { className: "dc-chart-dot dc-chart-s" + slot, "aria-hidden": "true" }), p.highlightName || "Highlighted"),
        h("span", { className: "dc-chart-key" }, h("i", { className: "dc-chart-dot dc-chart-muted", "aria-hidden": "true" }), p.restName || "Everything else"))
      : series.length > 1 ? h("div", { className: "dc-chart-legend" }, series.map(function (s, k) {
        return h("span", { key: s.name, className: "dc-chart-key" }, h("i", { className: "dc-chart-dot dc-chart-s" + (k % 5 + 1), "aria-hidden": "true" }), s.name);
      })) : null);
  }

  window.AppKit = window.Decena = Object.assign(window.AppKit || {}, {
    Button: Button, FilterPill: FilterPill, SegmentedControl: SegmentedControl, Badge: Badge,
    Flag: Flag, StatTile: StatTile, Panel: Panel, ListRow: ListRow, Highlight: Highlight, BarChart: BarChart
  });
})();
