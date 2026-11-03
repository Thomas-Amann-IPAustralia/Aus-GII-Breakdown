// The numbers behind a chart, without the page: how a value is written (fmt), one view of a spec (viewSpec), and the
// chart's table as header and rows (chartTable). charts.js draws the table from these, and markdown.js writes the same
// table into an observation's Markdown copy, so the two never disagree. Nothing here touches the document.

const nf = (d) => new Intl.NumberFormat("en-AU", { maximumFractionDigits: d, minimumFractionDigits: 0 });
export function fmt(v, format, digits) {
  if (v == null || Number.isNaN(v)) return "–";
  if (typeof v !== "number") return String(v);
  const d = digits ?? (format === "pct" ? 1 : Math.abs(v) < 10 && !Number.isInteger(v) ? 2 : 0);
  switch (format) {
    case "pct": return `${nf(d).format(v)}%`;
    case "share": return `${nf(digits ?? 1).format(v * 100)}%`; // a proportion (0 to 1) shown as a percentage
    case "money": return `$${nf(d).format(v)}`;
    case "moneym": return `$${nf(d).format(v)} m`;
    case "year": return String(Math.round(v));
    case "ratio": return nf(digits ?? 3).format(v);
    case "signed": return `${v > 0 ? "+" : ""}${nf(digits ?? 1).format(v)}`; // a difference, with its sign
    case "points": return `${v > 0 ? "+" : ""}${nf(digits ?? 1).format(v)} pts`; // percentage points
    default: return nf(d).format(v);
  }
}

/** An effect chart's value: the estimate and, where there is one, its interval. */
export function effectText(p, ys = {}) {
  if (!p || p[0] == null) return "–";
  const f = (v) => fmt(v, ys.format, ys.digits);
  return p[1] != null && p[2] != null ? `${f(p[0])} (${f(p[1])} to ${f(p[2])})` : f(p[0]);
}

/** The spec for one view: the shared keys, overridden by the view's own. */
export function viewSpec(spec, k) {
  if (!spec.views) return spec;
  const v = spec.views[k] || spec.views[0];
  return { ...spec, ...v, x: { ...(spec.x || {}), ...(v.x || {}) }, y: { ...(spec.y || {}), ...(v.y || {}) } };
}

/** A chart's table: `head` (the column names) and `rows` (text, the first cell naming the row). */
export function chartTable(s) {
  const xs = s.x || {}, ys = s.y || {};
  const series = (s.series || []).filter((d) => d.colour !== "muted" || s.type === "scatter");
  let head, rows;
  if (s.type === "effect") {
    head = [xs.name || "", ...(s.series || []).map((d) => d.name)];
    rows = (xs.values || []).map((v, i) => [v, ...(s.series || []).map((d) => effectText(d.data?.[i], ys))]);
  } else if (s.type === "range") {
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
  return { head, rows };
}
