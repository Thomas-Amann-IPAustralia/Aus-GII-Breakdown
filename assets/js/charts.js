// ECharts, themed from the page's colour tokens (adapted from Moria/dashboard/assets/js/charts.js). Every tooltip is
// built here from escaped text; names from a data file never reach a chart as HTML.

import { css, el, esc } from "./util.js";

/* global echarts */
const observed = new WeakMap();
const live = new Set();

export function tokens() {
  return {
    ink: css("--ink"), ink2: css("--ink-2"), muted: css("--muted"), line: css("--line"), surface: css("--surface"),
    surface2: css("--surface-2"), grid: css("--chart-grid"), axis: css("--chart-axis"), s1: css("--s1"), s2: css("--s2"),
    sMuted: css("--s-muted"), accent: css("--accent"), ramp: [css("--ramp-1"), css("--ramp-2"), css("--ramp-3"), css("--ramp-4")],
    div: [css("--div-neg"), css("--div-neg-2"), css("--div-mid"), css("--div-pos-2"), css("--div-pos")],
    font: getComputedStyle(document.body).fontFamily,
  };
}

export function baseOption() {
  const t = tokens();
  return {
    textStyle: { fontFamily: t.font, color: t.ink2 },
    animationDuration: 450,
    animationEasing: "cubicOut",
    tooltip: {
      backgroundColor: t.surface, borderColor: t.line, borderWidth: 1, padding: [9, 11],
      textStyle: { color: t.ink, fontFamily: t.font, fontSize: 13 },
      extraCssText: "border-radius:10px;box-shadow:0 8px 24px rgba(0,0,0,.16);max-width:340px;white-space:normal;",
      confine: true,
    },
  };
}

export function axis(kind = "value", extra = {}) {
  const t = tokens();
  return {
    type: kind,
    axisLine: { show: kind !== "value" && kind !== "log", lineStyle: { color: t.axis } },
    axisTick: { show: false },
    axisLabel: { color: t.muted, fontFamily: t.font, fontSize: 12, hideOverlap: true },
    splitLine: { show: kind === "value" || kind === "log", lineStyle: { color: t.grid } },
    nameTextStyle: { color: t.muted, fontFamily: t.font, fontSize: 12 },
    scale: kind === "value",
    ...extra,
  };
}

/**
 * Render (or re-render) a chart into a node; resized with its container and redrawn when the theme changes.
 * `build` returns the option, so it is re-run against the new colour tokens.
 */
export function chart(node, build) {
  let c = echarts.getInstanceByDom(node);
  if (!c) {
    c = echarts.init(node, null, { renderer: "canvas" });
    const ro = new ResizeObserver(() => c.resize());
    ro.observe(node);
    observed.set(node, ro);
  }
  node._build = build;
  live.add(node);
  draw(node, c);
  return c;
}
function draw(node, c) {
  const option = node._build();
  const base = baseOption();
  c.setOption({ ...base, ...option, tooltip: option.tooltip === false ? { show: false } : { ...base.tooltip, ...(option.tooltip || {}) } }, true);
}
window.addEventListener("themechange", () => {
  for (const node of live) {
    const c = node.isConnected && echarts.getInstanceByDom(node);
    if (c) draw(node, c);
    else live.delete(node);
  }
});

export function disposeAll(root) {
  for (const node of root.querySelectorAll("[_echarts_instance_]")) {
    observed.get(node)?.disconnect();
    echarts.getInstanceByDom(node)?.dispose();
    live.delete(node);
  }
}

/** Tooltip HTML: a heading and rows of [colour, label, value]; every string escaped. Values lead (bold). */
export function tipHtml(head, rows = [], foot) {
  let h = head ? `<div style="font-weight:700;margin-bottom:4px">${esc(head)}</div>` : "";
  for (const [colour, label, value] of rows) {
    const key = colour ? `<span style="display:inline-block;width:14px;height:3px;border-radius:2px;background:${esc(colour)};margin-right:6px;vertical-align:middle"></span>` : "";
    h += `<div style="display:flex;justify-content:space-between;gap:14px"><span style="color:${esc(tokens().ink2)}">${key}${esc(label)}</span><strong>${esc(value)}</strong></div>`;
  }
  if (foot) h += `<div style="margin-top:6px;color:${esc(tokens().muted)};font-size:12px">${esc(foot)}</div>`;
  return h;
}

/** A card holding a chart with a Chart/Table toggle (the table is the chart's accessible twin). */
export function chartCard({ title, tip, sub, height = "", render, table, actions, legend }) {
  const box = el(`div.chart${height ? `.${height}` : ""}`, { role: "img", "aria-label": typeof title === "string" ? title : "chart" });
  const tableBox = el("div.table-wrap", { hidden: true });
  const tog = table
    ? el("div.toggle", { role: "group", "aria-label": "Show as" },
        el("button", { type: "button", "aria-pressed": "true", onclick: () => flip(false) }, "Chart"),
        el("button", { type: "button", "aria-pressed": "false", onclick: () => flip(true) }, "Table"))
    : null;
  function flip(showTable) {
    const [a, b] = tog.children;
    a.setAttribute("aria-pressed", String(!showTable));
    b.setAttribute("aria-pressed", String(showTable));
    box.hidden = showTable;
    tableBox.hidden = !showTable;
    if (showTable) tableBox.replaceChildren(table());
  }
  const card = el("div.card",
    el("div.card-head", el("div", el("h3", title, tip || null), sub ? el("p.card-sub", sub) : null), el("div.row", actions || null, tog)),
    legend || null, box, tableBox);
  requestAnimationFrame(() => render(box));
  return card;
}

/** A plain data table from rows and column specs {label, value(row), n: numeric, node(row)}. */
export function dataTable(rows, cols, { onRow, max, rowClass } = {}) {
  const t = el("table.data");
  t.append(el("thead", el("tr", cols.map((c) => el(`th${c.n ? ".n" : ""}`, c.head ?? c.label)))));
  const tb = el("tbody");
  for (const r of (max ? rows.slice(0, max) : rows)) {
    const cls = rowClass?.(r);
    const tr = el(`tr${onRow ? ".click" : ""}${cls ? `.${cls}` : ""}`, onRow ? { onclick: () => onRow(r), tabindex: 0, onkeydown: (e) => e.key === "Enter" && onRow(r) } : null);
    for (const c of cols) {
      const v = c.node ? c.node(r) : c.value(r);
      tr.append(el(`td${c.n ? ".n" : ""}`, v instanceof Node ? v : v ?? "–"));
    }
    tb.append(tr);
  }
  t.append(tb);
  return t;
}

/** A legend row mirroring the marks: line keys for lines, dots for points. Text stays in ink, never series colour. */
export function legend(items) {
  return el("div.legend", items.map(([kind, colour, label]) => {
    const k = el(`span.${kind}`);
    k.style.background = colour;
    return el("span.k", k, label);
  }));
}
