// Turn a chart spec (written by analysis/atlas/charts.py, or quoted in an observation's YAML) into an ECharts chart,
// with a legend, a choice of views where the spec has them, and a table that holds the same numbers (the chart's
// accessible twin). Text from the spec reaches the page only as text: tooltips are built from escaped strings.

import { el, esc } from "../../assets/js/util.js";

/* global echarts */
const live = new Map(); // chart node -> redraw()
const reduced = matchMedia("(prefers-reduced-motion: reduce)").matches;

function token(name) {
  return getComputedStyle(document.documentElement).getPropertyValue(name).trim();
}
function palette() {
  return [1, 2, 3, 4, 5, 6, 7].map((i) => token(`--c${i}`));
}
function colourOf(s, i) {
  if (s.colour === "muted") return token("--c-muted");
  if (s.colour === "ink") return token("--ink-2");
  if (typeof s.colour === "number") return palette()[s.colour % 7];
  return palette()[i % 7];
}

const nf = (d) => new Intl.NumberFormat("en-AU", { maximumFractionDigits: d, minimumFractionDigits: 0 });
export function fmt(v, format, digits) {
  if (v == null || Number.isNaN(v)) return "–";
  if (typeof v !== "number") return String(v);
  const d = digits ?? (format === "pct" ? 1 : Math.abs(v) < 10 && !Number.isInteger(v) ? 2 : 0);
  switch (format) {
    case "pct": return `${nf(d).format(v)}%`;
    case "money": return `$${nf(d).format(v)}`;
    case "moneym": return `$${nf(d).format(v)} m`;
    case "year": return String(Math.round(v));
    case "ratio": return nf(digits ?? 3).format(v);
    default: return nf(d).format(v);
  }
}
function axisFmt(format) {
  return (v) => {
    if (format === "pct") return `${nf(1).format(v)}%`;
    if (format === "year") return String(v);
    if (format === "money" || format === "moneym") return `$${compact(v)}${format === "moneym" ? " m" : ""}`;
    return compact(v);
  };
}
function compact(v) {
  if (typeof v !== "number") return v;
  return Math.abs(v) >= 10000 ? new Intl.NumberFormat("en-AU", { notation: "compact", maximumFractionDigits: 1 }).format(v) : nf(2).format(v);
}

/** The spec for one view: the shared keys, overridden by the view's own. */
function viewSpec(spec, k) {
  if (!spec.views) return spec;
  const v = spec.views[k] || spec.views[0];
  return { ...spec, ...v, x: { ...(spec.x || {}), ...(v.x || {}) }, y: { ...(spec.y || {}), ...(v.y || {}) } };
}

function option(s) {
  const ink2 = token("--ink-2"), muted = token("--muted"), grid = token("--chart-grid"), axis = token("--chart-axis");
  const surface = token("--surface"), ink = token("--ink"), line = token("--line-strong");
  const font = getComputedStyle(document.body).fontFamily;
  const horizontal = !!s.horizontal;
  const xs = s.x || {}, ys = s.y || {};
  const cat = (xs.type || "category") === "category";
  const valueAxis = (a, isX) => ({
    type: a.type === "log" ? "log" : "value",
    name: a.name || "",
    nameLocation: isX ? "middle" : "end",
    nameGap: isX ? 30 : 14,
    nameTextStyle: isX ? { color: muted, fontFamily: font, fontSize: 12 } : { color: muted, fontFamily: font, fontSize: 12, align: "left", padding: [0, 0, 0, -6] },
    min: a.min, max: a.max,
    axisLine: { show: false }, axisTick: { show: false },
    axisLabel: { color: muted, fontFamily: font, fontSize: 11.5, formatter: axisFmt(a.format), hideOverlap: true },
    splitLine: { lineStyle: { color: grid } },
  });
  const catAxis = (a) => ({
    type: "category", data: a.values, name: a.name || "", nameLocation: "middle", nameGap: 30,
    nameTextStyle: { color: muted, fontFamily: font, fontSize: 12 },
    axisLine: { lineStyle: { color: axis } }, axisTick: { show: false },
    axisLabel: { color: muted, fontFamily: font, fontSize: 11.5, hideOverlap: !(horizontal || s.type === "range"), interval: horizontal || s.type === "range" ? 0 : "auto", width: horizontal || s.type === "range" ? 200 : undefined, overflow: horizontal || s.type === "range" ? "break" : undefined, lineHeight: 13 },
    inverse: horizontal,
  });
  // A titled log x-axis makes ECharts draw a stray "0" beside the title, so its title is a caption below the chart
  let xAxis = cat ? catAxis(xs) : valueAxis(xs.type === "log" ? { ...xs, name: "" } : xs, true);
  let yAxis = valueAxis(ys, false);
  if (s.type === "range") {
    xAxis = valueAxis({ ...ys, min: ys.min, max: ys.max }, true);
    yAxis = { ...catAxis(xs), inverse: true };
  } else if (horizontal) [xAxis, yAxis] = [valueAxis(ys, true), catAxis(xs)];
  if (horizontal || s.type === "range") { xAxis.nameGap = 30; }

  const few = (n) => n <= 24;
  const series = [];
  (s.series || []).forEach((d, i) => {
    const c = colourOf(d, i);
    if (s.type === "range") {
      series.push({ type: "bar", stack: "r", data: d.data.map((p) => (p ? p[0] : null)), itemStyle: { color: "transparent" }, silent: true, name: "_base", tooltip: { show: false }, barMaxWidth: 16 });
      const span = (ys.max ?? 2030) - (ys.min ?? 1900);
      series.push({ type: "bar", stack: "r", name: d.name, data: d.data.map((p) => (p ? Math.max(p[1] - p[0], span / 120) : null)), itemStyle: { color: c, borderRadius: 4 }, barMaxWidth: 16, _starts: d.data });
      return;
    }
    if ((s.type === "scatter" && d.kind !== "line") || d.kind === "scatter") {
      series.push({
        type: "scatter", name: d.name, data: d.data, symbolSize: d.size || 7,
        itemStyle: { color: c, opacity: d.opacity ?? 0.8, borderColor: surface, borderWidth: 1 }, emphasis: { scale: 1.6 },
        label: d.labels ? { show: true, position: "right", color: ink2, fontFamily: font, fontSize: 11.5, formatter: (p) => p.data[2] ?? "" } : { show: false },
      });
      return;
    }
    if (s.type === "bar" || d.kind === "bar") {
      const n = (d.data || []).length;
      series.push({
        type: "bar", name: d.name, data: d.data, stack: s.stack ? "s" : undefined, barMaxWidth: 24, barGap: "12%",
        itemStyle: { color: c, borderRadius: s.stack ? 0 : horizontal ? [0, 4, 4, 0] : [4, 4, 0, 0], borderColor: s.stack ? surface : undefined, borderWidth: s.stack ? 1 : 0 },
        label: (s.series.length === 1 && few(n) && s.labels !== false) ? { show: true, position: horizontal ? "right" : "top", color: ink2, fontFamily: font, fontSize: 11.5, formatter: (p) => fmt(p.value, ys.format, ys.digits) } : { show: false },
      });
      return;
    }
    const n = (d.data || []).length;
    series.push({
      type: "line", name: d.name, data: d.data, step: d.step ? "end" : false, connectNulls: false,
      symbol: few(n) && !d.line && d.kind !== "line" ? "circle" : "none", symbolSize: 7, showSymbol: few(n) && !d.line && d.kind !== "line",
      lineStyle: { width: d.width || 2, color: c, type: d.line || "solid", cap: "round", join: "round" },
      itemStyle: { color: c, borderColor: surface, borderWidth: 2 },
      areaStyle: d.area ? { color: c, opacity: 0.1 } : undefined,
      emphasis: { focus: "series" },
      z: d.colour === "muted" ? 1 : 3,
    });
  });

  // reference lines and shaded bands, on the first real series
  const m = s.marks || {};
  const host = series.find((x) => x.name !== "_base");
  if (host) {
    const lab = (t) => ({ show: !!t, formatter: t || "", color: ink2, fontFamily: font, fontSize: 11, position: "insideEndTop" });
    const lines = [
      ...(m.x || []).map((p) => ({ [horizontal ? "yAxis" : "xAxis"]: p.at, label: lab(p.label) })),
      ...(m.y || []).map((p) => ({ [horizontal ? "xAxis" : "yAxis"]: p.at, label: { ...lab(p.label), position: "insideEndTop" } })),
    ];
    if (lines.length) host.markLine = { silent: true, symbol: "none", lineStyle: { color: ink2, type: "dashed", width: 1 }, data: lines, animation: false };
    if (m.bands?.length) host.markArea = { silent: true, itemStyle: { color: token("--surface-3"), opacity: 0.7 }, label: { color: muted, fontFamily: font, fontSize: 11, position: "insideTop" }, data: m.bands.map((b) => [{ [horizontal ? "yAxis" : "xAxis"]: b.from, name: b.label || "" }, { [horizontal ? "yAxis" : "xAxis"]: b.to }]) };
  }

  const tipRow = (colour, name, value) => `<div style="display:flex;justify-content:space-between;gap:16px"><span>${colour ? `<span style="display:inline-block;width:10px;height:10px;border-radius:3px;background:${esc(colour)};margin-right:6px"></span>` : ""}${esc(name)}</span><strong>${esc(value)}</strong></div>`;
  const tooltip = {
    backgroundColor: surface, borderColor: line, borderWidth: 1, padding: [9, 12], confine: true,
    textStyle: { color: ink, fontFamily: font, fontSize: 13 },
    extraCssText: "border-radius:10px;box-shadow:0 8px 24px rgba(0,0,0,.16);max-width:340px;white-space:normal;",
  };
  if (s.type === "scatter") {
    Object.assign(tooltip, {
      trigger: "item",
      formatter: (p) => {
        const [x, y, label] = p.data;
        return `<div style="font-weight:700;margin-bottom:4px">${esc(label ?? p.seriesName)}</div>${tipRow(null, xs.name || "x", fmt(x, xs.format, xs.digits))}${tipRow(null, ys.name || "y", fmt(y, ys.format, ys.digits))}`;
      },
    });
  } else if (s.type === "range") {
    Object.assign(tooltip, {
      trigger: "item",
      formatter: (p) => {
        const st = series[p.seriesIndex]._starts?.[p.dataIndex];
        return st ? `<div style="font-weight:700;margin-bottom:4px">${esc(p.name)}</div>${tipRow(p.color, p.seriesName, `${fmt(st[0], ys.format)} to ${fmt(st[1], ys.format)}`)}` : "";
      },
    });
  } else {
    Object.assign(tooltip, {
      trigger: "axis",
      axisPointer: { type: s.type === "bar" ? "shadow" : "line", lineStyle: { color: axis }, shadowStyle: { color: "rgba(128,128,128,.08)" } },
      formatter: (ps) => {
        const list = (Array.isArray(ps) ? ps : [ps]).filter((p) => p.seriesName !== "_base" && p.value != null && !(Array.isArray(p.value) && p.value[1] == null));
        if (!list.length) return "";
        const head = cat ? list[0].name : fmt(Array.isArray(list[0].value) ? list[0].value[0] : list[0].axisValue, xs.format, xs.digits);
        const headTxt = s.tipHead ? s.tipHead.replace("{x}", head) : head;
        return `<div style="font-weight:700;margin-bottom:4px">${esc(headTxt)}</div>` + list.map((p) => tipRow(p.color, p.seriesName, fmt(Array.isArray(p.value) ? p.value[1] : p.value, ys.format, ys.digits))).join("");
      },
    });
  }
  return {
    animation: !reduced, animationDuration: 450,
    textStyle: { fontFamily: font, color: ink2 },
    grid: { left: 10, right: horizontal || s.type === "range" ? 46 : 22, top: ys.name && !horizontal && s.type !== "range" ? 40 : 26, bottom: (xs.name && xs.type !== "log") || horizontal ? 34 : 8, containLabel: true },
    legend: { show: false, data: (s.series || []).map((d) => d.name) },
    tooltip, xAxis, yAxis, series,
  };
}

function legendNode(s, chartObj) {
  if (!s.series || s.series.length < 2) return null;
  return el("div.legend", { role: "group", "aria-label": "Series (select to hide or show)" }, s.series.map((d, i) => {
    const k = el(`span.${s.type === "line" ? "line" : "sq"}${d.line ? ".dashed" : ""}`);
    k.style.background = colourOf(d, i);
    const b = el("button.k", { type: "button", "aria-pressed": "true", style: { border: 0, background: "none", padding: "2px 0" } }, k, d.name);
    b.addEventListener("click", () => {
      const on = b.getAttribute("aria-pressed") === "true";
      b.setAttribute("aria-pressed", String(!on));
      b.style.opacity = on ? 0.45 : 1;
      chartObj()?.dispatchAction({ type: "legendToggleSelect", name: d.name });
    });
    return b;
  }));
}

function tableNode(s) {
  const xs = s.x || {}, ys = s.y || {};
  const t = el("table.data");
  const series = (s.series || []).filter((d) => d.colour !== "muted" || s.type === "scatter");
  let head, rows;
  if (s.type === "range") {
    head = [xs.name || "", ...series.flatMap((d) => [`${d.name}: from`, "to"])];
    rows = (xs.values || []).map((v, i) => [v, ...series.flatMap((d) => (d.data[i] ? [fmt(d.data[i][0], ys.format), fmt(d.data[i][1], ys.format)] : ["–", "–"]))]);
  } else if (s.type === "scatter") {
    head = ["", xs.name || "x", ys.name || "y"];
    rows = series.filter((d) => d.kind !== "line").flatMap((d) => d.data.map((p) => [p[2] ?? d.name, fmt(p[0], xs.format, xs.digits), fmt(p[1], ys.format, ys.digits)]));
  } else if ((xs.type || "category") === "category") {
    head = [xs.name || "", ...series.map((d) => d.name)];
    rows = (xs.values || []).map((v, i) => [v, ...series.map((d) => fmt(d.data[i], ys.format, ys.digits))]);
  } else {
    const pts = s.table_points;
    const xsAll = [...new Set(series.flatMap((d) => d.data.map((p) => p[0])))].sort((a, b) => a - b).filter((x) => !pts || pts.includes(x));
    head = [xs.name || "x", ...series.map((d) => d.name)];
    rows = xsAll.map((x) => [fmt(x, xs.format, xs.digits), ...series.map((d) => fmt(d.data.find((p) => p[0] === x)?.[1], ys.format, ys.digits))]);
  }
  t.append(el("thead", el("tr", head.map((h, i) => el(`th${i ? ".n" : ""}`, { scope: "col" }, h)))));
  t.append(el("tbody", rows.map((r) => el("tr", r.map((c, i) => (i ? el("td.n", c) : el("th", { scope: "row" }, c)))))));
  return t;
}

/**
 * A chart card: title, view choices, chart/table switch, the chart, its legend, source and notes.
 * `origin` says how the numbers were made ("query": redrawn from the lens; "quoted": the observation's own numbers).
 */
export function chartCard(spec, { origin = "query", compact = false } = {}) {
  let k = 0;
  let instance = null;
  const card = el("figure.chart-card", { style: { margin: compact ? "0" : undefined } });
  const box = el(`div.chart${spec.height ? `.${spec.height}` : ""}`, { role: "img" });
  const tableBox = el("div.chart-table", { hidden: true });
  const legendBox = el("div");
  const xCaption = el("p.x-caption");
  const head = el("div.chart-head");
  const title = el("div");
  const tools = el("div.chart-tools");
  const views = spec.views ? el("div.chart-views", { role: "group", "aria-label": "Choose a view" }) : null;
  const foot = el("figcaption.chart-foot");
  let showTable = false;

  const tog = el("div.seg", { role: "group", "aria-label": "Show as" },
    el("button", { type: "button", "aria-pressed": "true", onclick: () => flip(false) }, "Chart"),
    el("button", { type: "button", "aria-pressed": "false", onclick: () => flip(true) }, "Table"));
  tools.append(tog);
  head.append(title, tools);

  function current() { return viewSpec(spec, k); }
  function draw() {
    const s = current();
    title.replaceChildren(...[el("h3", s.title || spec.title || ""), s.subtitle ? el("p", s.subtitle) : null].filter(Boolean));
    box.setAttribute("aria-label", `${s.title || spec.title || "Chart"}. ${s.subtitle || ""} The same numbers are in the table view.`);
    if (s.horizontal || s.type === "range") {
      const rows = (s.x?.values || []).length * (s.stack || s.type === "range" ? 1 : Math.max(1, (s.series || []).length * 0.6));
      box.style.height = `${Math.max(240, Math.round(rows * 26 + 80))}px`;
    }
    if (!showTable && typeof echarts !== "undefined") {
      instance = echarts.getInstanceByDom(box) || echarts.init(box, null, { renderer: "canvas" });
      instance.setOption(option(s), true);
    }
    xCaption.textContent = s.x?.type === "log" && s.x?.name ? s.x.name : "";
    xCaption.hidden = !xCaption.textContent || showTable;
    const lg = legendNode(s, () => instance);
    legendBox.replaceChildren(...(lg ? [lg] : []));
    tableBox.replaceChildren(tableNode(s));
    const how = origin === "quoted"
      ? "Drawn from the numbers quoted in the observation itself."
      : origin === "audit" && s.origin === "record"
        ? "Counted from the review's record, which gives each observation one verdict."
        : origin === "audit"
        ? "Drawn from the review's benchmark, which recounts IP Australia's published figures from Stage 1's data (analysis/audit)."
        : "Redrawn from the lens table with the notebook's own query, and checked against every number the observation quotes.";
    foot.replaceChildren(...[
      s.source ? el("span", `Source: ${s.source}`) : null,
      s.note ? el("span", s.note) : null,
      el("span", how),
    ].filter(Boolean));
  }
  function flip(t) {
    showTable = t;
    tog.children[0].setAttribute("aria-pressed", String(!t));
    tog.children[1].setAttribute("aria-pressed", String(t));
    box.hidden = t;
    legendBox.hidden = t;
    tableBox.hidden = !t;
    if (!t) requestAnimationFrame(() => { draw(); instance?.resize(); });
  }
  if (views && spec.select) {
    const sel = el("select", { "aria-label": "Choose a view" }, spec.views.map((v, i) => el("option", { value: String(i) }, v.label)));
    sel.addEventListener("change", () => { k = Number(sel.value); draw(); });
    views.append(el("label.view-select", el("span", "Show "), sel));
  } else if (views) {
    spec.views.forEach((v, i) => {
      const b = el("button", { type: "button", "aria-pressed": String(i === 0) }, v.label);
      b.addEventListener("click", () => {
        k = i;
        [...views.children].forEach((c, j) => c.setAttribute("aria-pressed", String(j === i)));
        draw();
      });
      views.append(b);
    });
  }
  card.append(...[head, views, box, xCaption, legendBox, tableBox, foot].filter(Boolean));
  requestAnimationFrame(() => {
    draw();
    const ro = new ResizeObserver(() => instance?.resize());
    ro.observe(box);
  });
  live.set(box, draw);
  return card;
}

window.addEventListener("themechange", () => {
  for (const [node, redraw] of live) {
    if (node.isConnected) redraw();
    else live.delete(node);
  }
});

/** Free every chart that is no longer on the page. */
export function sweep() {
  for (const node of live.keys()) {
    if (!node.isConnected) {
      if (typeof echarts !== "undefined") echarts.getInstanceByDom(node)?.dispose();
      live.delete(node);
    }
  }
}
