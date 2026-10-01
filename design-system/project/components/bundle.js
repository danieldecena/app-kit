/* @ds-bundle: {"format":4,"namespace":"AppKit","components":[{"name":"Button"},{"name":"FilterPill"},{"name":"SegmentedControl"},{"name":"Badge"},{"name":"Flag"},{"name":"StatTile"},{"name":"Panel"},{"name":"Fact"},{"name":"Eyebrow"},{"name":"Toolbar"},{"name":"SidebarList"},{"name":"Shelf"},{"name":"ArtworkCard"},{"name":"HeroCard"},{"name":"MiniPlayer"},{"name":"TrackList"},{"name":"ListRow"},{"name":"Highlight"},{"name":"BarChart"}]} */
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

  function ArtworkCard(p) {
    return h("button", { type: "button", className: cx("dc-artcard", p.className), onClick: p.onClick,
                         style: p.width ? { "--artcard-w": p.width + "px" } : undefined },
      h("img", { className: "dc-artcard-art", src: p.art, alt: "" }),
      h("span", { className: "dc-artcard-cap" },
        h("span", { className: "dc-artcard-title" }, p.title),
        p.subtitle ? h("span", { className: "dc-artcard-sub" }, p.subtitle) : null));
  }

  // Full-bleed artwork at 3:4 with the caption over it. `tone` is the colour
  // the adopting app derived from the artwork; nothing here reads the image,
  // because no part of this pipeline reads a colour at runtime. It only shows
  // while the artwork loads, and behind a transparent one.
  function HeroCard(p) {
    var style = {};
    if (p.width) style["--hero-w"] = p.width + "px";
    if (p.tone) style.background = p.tone;
    return h("button", { type: "button", className: cx("dc-herocard", p.className), onClick: p.onClick,
                         style: style },
      h("img", { className: "dc-herocard-art", src: p.art, alt: "" }),
      h("span", { className: "dc-herocard-scrim" }),
      p.badge ? h("span", { className: "dc-herocard-badge" }, p.badge) : null,
      h("span", { className: "dc-herocard-cap" },
        p.eyebrow ? h("span", { className: "dc-herocard-eyebrow" }, p.eyebrow) : null,
        h("span", { className: "dc-herocard-title" }, p.title)));
  }

  // Music's song table. `columns` is configuration, not a fixed set: the
  // playlist measured has seven and no Album, an earlier capture had one.
  function TrackList(p) {
    var cols = p.columns || [];
    var rows = p.rows || [];
    var grid = cols.map(function (c) { return c.width || "1fr"; }).join(" ");
    var ids = rows.map(function (row, i) { return row.id != null ? row.id : i; });
    var selectable = !!p.onSelect;
    // A role=grid wants ONE tab stop with the arrows moving inside it, not one
    // per row: a 200-track playlist is otherwise 200 tab stops. The row that
    // takes it is the selected one, falling back to the first.
    var activeIndex = Math.max(0, ids.indexOf(p.selection));
    function onKeyDown(e, i) {
      var next = null;
      if (e.key === "ArrowDown") next = Math.min(ids.length - 1, i + 1);
      else if (e.key === "ArrowUp") next = Math.max(0, i - 1);
      else if (e.key === "Home") next = 0;
      else if (e.key === "End") next = ids.length - 1;
      else if (e.key === "Enter" || e.key === " ") {
        // Enter plays, which is what Music does. Space too, since a focused row
        // has to answer the key that activates everything else.
        e.preventDefault();
        if (p.onPlay) p.onPlay(ids[i]);
        return;
      } else return;
      e.preventDefault();
      if (next === i) return;
      // Move focus WITH the selection. Moving only the selection leaves the
      // focus ring behind and a screen reader never hears the change.
      var el = e.currentTarget.parentNode.querySelectorAll(".dc-tracklist-row")[next];
      if (el) el.focus();
      if (p.onSelect) p.onSelect(ids[next]);
    }
    function cells(row, head) {
      return cols.map(function (c, i) {
        var v = head ? c.label : (c.render ? c.render(row) : row[c.key]);
        return h("span", { key: c.key || i,
                           className: head ? undefined : "dc-tracklist-cell",
                           role: head ? "columnheader" : "gridcell",
                           "data-soft": !head && c.soft ? "true" : undefined,
                           // Alignment is a column property, so the header has to
                           // take it too or a right-aligned Time column sits over
                           // left-aligned times.
                           "data-align": c.align === "end" ? "end" : undefined }, v);
      });
    }
    return h("div", { className: cx("dc-tracklist", p.className), role: "grid",
                      "aria-label": p.label || "Tracks",
                      "aria-rowcount": rows.length,
                      "data-window-inactive": p.windowInactive ? "true" : undefined },
      cols.some(function (c) { return c.label; })
        ? h("div", { className: "dc-tracklist-head", role: "row", style: { gridTemplateColumns: grid } }, cells(null, true))
        : null,
      rows.map(function (row, i) {
        var id = ids[i];
        return h("div", { key: id, className: "dc-tracklist-row", role: "row",
                          tabIndex: i === activeIndex ? 0 : -1,
                          // Only claim a selection state when selection is a
                          // thing here; otherwise every row announces itself as
                          // "not selected" in a purely presentational list.
                          "aria-selected": selectable ? (p.selection === id ? "true" : "false") : undefined,
                          style: { gridTemplateColumns: grid },
                          onKeyDown: function (e) { onKeyDown(e, i); },
                          onClick: p.onSelect ? function () { p.onSelect(id); } : undefined,
                          onDoubleClick: p.onPlay ? function () { p.onPlay(id); } : undefined },
          cells(row, false));
      }));
  }

  // The floating transport capsule. `progress` is 0..1 and is presentation
  // only -- the capsule does not own playback, it reports it.
  function MiniPlayer(p) {
    function btn(key, label, glyph, on, extra) {
      // A control with no handler is genuinely unavailable, so it is disabled.
      // But a toggle must not claim BOTH pressed and unavailable, which is what
      // `shuffle` without `onShuffle` produced: accent-red, dimmed, and out of
      // the tab order. Drop the pressed state when there is nothing to press.
      var pressable = !!on;
      var e2 = Object.assign({}, extra || {});
      if (!pressable) delete e2["aria-pressed"];
      return h("button", Object.assign({ key: key, type: "button", className: "dc-miniplayer-btn",
                                         "aria-label": label, onClick: on, disabled: !on }, e2), glyph);
    }
    var pct = Math.max(0, Math.min(1, p.progress || 0)) * 100;
    return h("div", { className: cx("dc-miniplayer", p.className), role: "group", "aria-label": "Now playing",
                      "data-floating": p.floating ? "true" : undefined,
                      style: p.width ? { "--miniplayer-w": p.width + "px" } : undefined },
      h("div", { className: "dc-miniplayer-transport" },
        btn("sh", "Shuffle", p.shuffleGlyph || "⇄", p.onShuffle, { "aria-pressed": p.shuffle ? "true" : "false" }),
        btn("pv", "Previous", p.prevGlyph || "⏮", p.onPrev),
        btn("pp", p.playing ? "Pause" : "Play", p.playing ? (p.pauseGlyph || "⏸") : (p.playGlyph || "▶"), p.onPlayPause),
        btn("nx", "Next", p.nextGlyph || "⏭", p.onNext),
        btn("rp", "Repeat", p.repeatGlyph || "↻", p.onRepeat, { "aria-pressed": p.repeat ? "true" : "false" })),
      h("div", { className: "dc-miniplayer-now" },
        h("img", { className: "dc-miniplayer-art", src: p.art, alt: "" }),
        h("span", { className: "dc-miniplayer-text" },
          h("span", { className: "dc-miniplayer-title" }, p.title, p.favorite ? p.favoriteGlyph || " ★" : null),
          p.subtitle ? h("span", { className: "dc-miniplayer-sub" }, p.subtitle) : null),
        h("span", { className: "dc-miniplayer-track", role: "progressbar", "aria-label": "Playback position",
                    "aria-valuemin": 0, "aria-valuemax": 100, "aria-valuenow": Math.round(pct) },
          h("span", { className: "dc-miniplayer-fill", style: { width: pct + "%" } }))),
      p.actions ? h("div", { className: "dc-miniplayer-actions" }, p.actions) : null);
  }

  function Shelf(p) {
    // Arrow keys scroll by one card pitch, so the shelf snaps the way Music's
    // does (measured: an ease-out settling on a card boundary).
    var track = React.useRef(null);
    function nudge(dir) {
      var el = track.current; if (!el) return;
      var first = el.firstElementChild;
      var pitch = first ? first.getBoundingClientRect().width + (p.compact ? 16 : 20) : 200;
      el.scrollBy({ left: dir * pitch, behavior: "smooth" });
    }
    return h("section", { className: cx("dc-shelf", p.className), "data-compact": p.compact ? "true" : undefined,
                          "aria-label": p.title },
      h("div", { className: "dc-shelf-head" },
        h("h2", { className: "dc-shelf-title" }, p.title),
        p.onMore ? h("button", { type: "button", className: "dc-shelf-more", "aria-label": "See all " + p.title, onClick: p.onMore },
          h("svg", { width: 12, height: 12, viewBox: "0 0 16 16", fill: "none", stroke: "currentColor", strokeWidth: 2, strokeLinecap: "round", "aria-hidden": "true" },
            h("path", { d: "M6 3l5 5-5 5" }))) : null),
      // No role=list here: the children are the caller's cards, not listitems,
      // and a list owning no listitem is announced as empty. The section's
      // aria-label already names the group.
      h("div", { className: "dc-shelf-track", ref: track, tabIndex: 0,
                 onKeyDown: function (e) {
                   if (e.key === "ArrowRight") { e.preventDefault(); nudge(1); }
                   if (e.key === "ArrowLeft") { e.preventDefault(); nudge(-1); }
                 } },
        p.children));
  }

  function SidebarList(p) {
    // sections: [{ label, action, onAction, items: [{ id, label, icon, thumb }] }]
    // Selection is controlled. Arrow keys move it, matching SegmentedControl.
    var flat = [];
    (p.sections || []).forEach(function (sec) { (sec.items || []).forEach(function (it) { flat.push(it.id); }); });
    function move(e, d) {
      var i = flat.indexOf(p.selection);
      // With nothing selected, step to an END rather than to index 0 + d: the
      // old form made ArrowDown land on item 1 and skip item 0 entirely.
      var n = i < 0 ? (d > 0 ? 0 : flat.length - 1)
                    : Math.min(flat.length - 1, Math.max(0, i + d));
      if (n === i) return;
      // Focus follows the selection. Moving only the selection leaves the ring
      // on the row you started from and a screen reader never hears the change.
      var rows = e.currentTarget.closest(".dc-sidebar").querySelectorAll(".dc-sidebar-row");
      if (rows[n]) rows[n].focus();
      if (p.onSelect) p.onSelect(flat[n]);
    }
    return h("nav", {
      className: cx("dc-sidebar", p.className),
      "data-window": p.windowInactive ? "inactive" : undefined,
      "aria-label": p.label || "Sidebar"
    },
      h("div", { className: "dc-sidebar-scroll" },
        (p.sections || []).map(function (sec, si) {
          return h("div", { key: sec.label || si },
            sec.label ? h("div", { className: "dc-sidebar-head" },
              h("span", { className: "dc-sidebar-head-label" }, sec.label),
              sec.action ? h("button", { type: "button", className: "dc-sidebar-head-action", onClick: sec.onAction }, sec.action) : null) : null,
            (sec.items || []).map(function (it) {
              var on = it.id === p.selection;
              return h("button", {
                key: it.id, type: "button", className: "dc-sidebar-row",
                "aria-current": on ? "true" : undefined,
                onClick: function () { if (p.onSelect) p.onSelect(it.id); },
                onKeyDown: function (e) {
                  if (e.key === "ArrowDown") { e.preventDefault(); move(e, 1); }
                  if (e.key === "ArrowUp") { e.preventDefault(); move(e, -1); }
                }
              },
                it.thumb
                  ? h("img", { className: "dc-sidebar-thumb", src: it.thumb, alt: "" })
                  : h("span", { className: "dc-sidebar-icon", "aria-hidden": "true" }, it.icon),
                h("span", { className: "dc-sidebar-label" }, it.label));
            }));
        })),
      p.footer ? h("div", { className: "dc-sidebar-foot" },
        h("span", { className: "dc-sidebar-avatar" }),
        h("span", { className: "dc-sidebar-label" }, p.footer)) : null);
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
    Flag: Flag, StatTile: StatTile, Panel: Panel, Fact: Fact, Eyebrow: Eyebrow, Toolbar: Toolbar, SidebarList: SidebarList, Shelf: Shelf, ArtworkCard: ArtworkCard, HeroCard: HeroCard, MiniPlayer: MiniPlayer, TrackList: TrackList, ListRow: ListRow, Highlight: Highlight, BarChart: BarChart
  });
})();
