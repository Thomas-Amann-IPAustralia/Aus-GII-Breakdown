// Compare two measures: the charts, the three correlations with their uncertainty, a plain-English reading, the
// automatic checks, and (across economies) where Australia sits. Over time, the correlation of year-on-year changes
// is always computed beside the chosen view, because shared trends are the commonest way these comparisons mislead.

import { axis, chart, chartCard, dataTable, legend, tipHtml, tokens } from "../charts.js";
import { coverage, SOURCES } from "../data.js";
import { num, term, tip } from "../glossary.js";
import * as S from "../stats.js";
import { download, el, fmt, link, n as nfmt, ordinal, pval, r2d, toCsv } from "../util.js";
import {
  alignEcon, alignTime, checkList, direction, ECON_TRANSFORMS, GROUPS, INCOME_NAMES, INCOME_ORDER, runChecks, short,
  span, STARTERS, strength, TIME_TERMS, TIME_TRANSFORMS,
} from "./common.js";
import { picker } from "./picker.js";

export function renderCompare(root, ds, p, ctx) {
  const { go, lenses } = ctx;
  const mode = ds.mode;
  const set = (patch) => go("compare", { ...p, ...patch });

  root.append(starters(mode, go));

  // ---------------------------------------------------------------------------------------- controls
  const X = p.x ? ds.byId.get(p.x) : null;
  const Y = p.y ? ds.byId.get(p.y) : null;
  const pickX = el("label.field.grow", el("span.lab", "X: the first measure"),
    picker({ ds, value: p.x, label: "the first measure", swatch: "var(--s1)", lenses, onChange: (id) => set({ x: id }) }));
  const pickY = el("label.field.grow", el("span.lab", "Y: the second measure"),
    picker({ ds, value: p.y, label: "the second measure", swatch: "var(--s2)", lenses, onChange: (id) => set({ y: id }) }));
  const swap = el("button.btn", { type: "button", title: "Swap X and Y", onclick: () => set({ x: p.y, y: p.x, tx: p.ty, ty: p.tx }) }, "⇄ Swap");
  const controls = el("div.card", el("div.controls", pickX, swap, pickY));
  root.append(controls);

  if (!X || !Y) {
    root.append(el("div.card.mt", el("div.empty", el("p", "Choose two measures above, or start from one of the questions."))));
    return;
  }

  const opts = el("div.controls.mt");
  if (mode === "time") {
    const tf = p.t || "level";
    opts.append(
      el("label.field", el("span.lab", "Compare as", tip("spurious")), seg(TIME_TRANSFORMS, tf, (v) => set({ t: v }))),
      el("label.field", el("span.lab", "Lag Y by (years)", tip("lag")), el("input", { type: "number", min: -10, max: 10, step: 1, value: p.lag || 0, onchange: (e) => set({ lag: +e.target.value || 0 }) })),
      el("label.field", el("span.lab", "From"), el("input", { type: "number", value: p.from || "", placeholder: String(Math.max(X.cov.from, Y.cov.from)), onchange: (e) => set({ from: e.target.value || undefined }) })),
      el("label.field", el("span.lab", "To"), el("input", { type: "number", value: p.to || "", placeholder: String(Math.min(X.cov.to, Y.cov.to)), onchange: (e) => set({ to: e.target.value || undefined }) })),
    );
  } else {
    opts.append(
      el("label.field", el("span.lab", "X scale", tip("log")), seg(ECON_TRANSFORMS, p.tx || "level", (v) => set({ tx: v }))),
      el("label.field", el("span.lab", "Y scale", tip("log")), seg(ECON_TRANSFORMS, p.ty || "level", (v) => set({ ty: v }))),
      el("label.field", el("span.lab", "Economies", tip("restricted_range")), el("select", { onchange: (e) => set({ g: e.target.value }) },
        GROUPS.map(([k, name]) => el("option", { value: k, selected: (p.g || "all") === k }, name)))),
      el("label.field", el("span.lab", "Colour"), el("select", { onchange: (e) => set({ col: e.target.value }) },
        el("option", { value: "", selected: !p.col }, "Australia against the rest"),
        el("option", { value: "income", selected: p.col === "income" }, "By income group"))),
    );
  }
  const control = p.c ? ds.byId.get(p.c) : null;
  opts.append(el("label.field.grow", el("span.lab", "Control for (optional)", tip("partial")),
    el("div.row", picker({ ds, value: p.c, label: "a control", lenses, placeholder: "Nothing: the plain correlation", allowNone: true, exclude: [p.x, p.y], onChange: (id) => set({ c: id || undefined }) }),
      control && mode === "economy" ? seg(ECON_TRANSFORMS, p.tc || "level", (v) => set({ tc: v })) : null)));
  controls.append(opts);
  controls.append(about([X, Y, control].filter(Boolean), lenses));

  if (mode === "time") renderTime(root, ds, p, X, Y, control, set);
  else renderEcon(root, ds, p, X, Y, control, set);
}

// ------------------------------------------------------------------------------------------- over time

function renderTime(root, ds, p, X, Y, control, set) {
  const tf = p.t || "level";
  const lag = +p.lag || 0;
  const from = p.from ? +p.from : -Infinity, to = p.to ? +p.to : Infinity;
  const a = alignTime(X, Y, { tf, lag, from, to });
  const n = a.years.length;
  if (n < 4) {
    root.append(el("div.card.mt", el("div.empty", el("p", `These two measures share only ${n} year${n === 1 ? "" : "s"} once transformed${lag ? " and lagged" : ""} (X ${coverage(X)}; Y ${coverage(Y)}). Choose measures that overlap, or compare as levels.`))));
    return;
  }
  const r = S.pearson(a.x, a.y);
  const rho = S.spearman(a.x, a.y);
  const tau = S.kendall(a.x, a.y);
  const fit = S.linFit(a.x, a.y);
  const r1x = S.acf1(span(a.xs, a.years)), r1y = S.acf1(span(a.ys, a.years.map((t) => t + lag)));
  const nEff = S.effectiveN(n, r1x, r1y);
  const adj = S.corrTest(r.r, n, { nEff });

  // levels against changes, always
  const lev = alignTime(X, Y, { tf: "level", lag, from, to });
  const dif = alignTime(X, Y, { tf: "diff", lag, from, to });
  const rLev = lev.years.length >= 4 ? S.pearsonR(lev.x, lev.y) : NaN;
  const rDif = dif.years.length >= 4 ? S.pearsonR(dif.x, dif.y) : NaN;

  // controlling for a third series
  let part = null;
  if (control) {
    const zs = S.transform(control.series, tf);
    part = S.partial(a.x, a.y, [a.years.map((t) => (zs.has(t) ? zs.get(t) : null))]);
  }

  const extra = [];
  if (tf === "level" && Number.isFinite(rLev) && Math.abs(rLev) >= 0.5 && Number.isFinite(rDif) && Math.abs(rDif) < Math.abs(rLev) - 0.3) {
    extra.push({ level: "serious", body: [el("b", "Probably a shared trend. "), `The levels correlate at ${r2d(rLev)}, but year-on-year changes only at ${r2d(rDif)}. Both series trend, and trending series correlate whatever they measure (`, term("spurious", "spurious correlation"), "). Switch to year-on-year change."] });
  } else if (tf === "level" && Math.abs(r.r) >= 0.5 && Number.isFinite(rDif)) {
    extra.push({ level: "warn", body: [el("b", "Levels of trending series. "), `Year-on-year changes correlate at ${r2d(rDif)}: `, Math.abs(rDif) >= 0.3 ? "the association survives, which is more telling than the levels." : "check the changes before reading anything into the levels."] });
  } else if (tf === "level" && Math.abs(r.r) >= 0.5) {
    extra.push({ level: "warn", body: [el("b", "Levels of trending series. "), "Too few overlapping changes to compare (the series have long gaps). Try Detrended before reading anything into the levels."] });
  }
  if (nEff < n * 0.6) extra.push({ level: "warn", body: [el("b", `Worth about ${fmt(Math.round(nEff))} independent years, not ${n}. `), "Both series move smoothly (", term("autocorrelation", "autocorrelation"), ` ${r2d(r1x)} and ${r2d(r1y)}), so the `, term("adjusted_p", "adjusted p-value"), ` (${pval(adj.p)}) is the one to read.`] });
  if (lag) extra.push({ level: "info", body: [el("b", `Lagged by ${lag} year${Math.abs(lag) === 1 ? "" : "s"}. `), "Trying several lags and keeping the best is ", term("multiple_comparisons", "multiple testing"), "; treat the best lag as a hint about timing."] });
  if (X.labels || Y.labels) extra.push({ level: "info", body: [el("b", "Period averages or financial years. "), "Some Closing the Gap values cover several years or a financial year and are placed at one year (see Sources)."] });
  if (control && part) {
    const how = [X, Y].some((V) => V.parts_of?.includes(control.id) || control.parts_of?.includes(V.id));
    if (how) extra.push({ level: "warn", body: [el("b", "The control is built from one of the measures "), "(or the other way round): removing it removes part of the measure itself."] });
  }

  const labels = a.years.map((t) => (lag ? `${t} → ${t + lag}` : String(t)));
  const checks = runChecks({ ds, X, Y, x: a.x, y: a.y, labels, n, mode: "time", tf, extra });

  // ---------------------------------------------------------------------------------------- reading
  const tfName = TIME_TRANSFORMS.find(([k]) => k === tf)[1].toLowerCase();
  const reading = el("p.reading",
    `Over ${n} years (${a.years[0]}–${a.years[n - 1]}${lag ? `, Y ${lag > 0 ? "+" : ""}${lag}` : ""}), `,
    el("strong", short(X, 50)), " and ", el("strong", short(Y, 50)),
    tf === "level" ? " have " : ` (${tfName}) have `,
    el("strong", `a ${strength(r.r)} ${direction(r.r)} association`), ` (r = ${r2d(r.r)}, 95% interval ${r2d(r.lo)} to ${r2d(r.hi)}). `,
    tf === "level" && Number.isFinite(rDif) ? `Their year-on-year changes correlate at ${r2d(rDif)}. ` : "",
    nEff < n * 0.9 ? `Allowing for how smoothly both move, that is worth about ${fmt(Math.round(nEff))} independent years (adjusted p = ${pval(adj.p)}).` : `p = ${pval(r.p)}.`,
    part && Number.isFinite(part.r) ? ` Holding ${short(control, 40)} fixed, the partial correlation is ${r2d(part.r)}.` : "");

  // ---------------------------------------------------------------------------------------- charts
  const [zTog] = toggle(["One scale (z-scores)", "Each in its own units"], p.view === "own" ? 1 : 0, (i) => set({ view: i ? "own" : undefined }));
  const left = el("div");
  const lineCard = chartCard({
    title: tf === "level" ? "Over time" : `Over time: ${tfName}`,
    tip: tip(p.view === "own" ? "time_series" : "indexed"),
    sub: p.view === "own" ? "Each series in its own units. Two panels rather than two axes: a second axis invents a match by its choice of scale." : "Both standardised to their own mean and spread, so their shapes share one axis. Hover for the values.",
    legend: legend([["line", "var(--s1)", `X: ${short(X, 50)}`], ["line", "var(--s2)", `Y: ${short(Y, 50)}${lag ? ` (${lag > 0 ? "+" : ""}${lag} yr)` : ""}`]]),
    actions: zTog, height: p.view === "own" ? "tall" : "",
    render: (box) => (p.view === "own" ? ownUnits(box, a, X, Y, lag) : zLines(box, a, X, Y, lag, tf)),
    table: () => dataTable(a.years.map((t, i) => ({ t, x: a.x[i], y: a.y[i] })), [
      { label: "Year (X)", value: (d) => d.t }, { label: short(X, 30), n: true, value: (d) => fmt(d.x, 4) },
      { label: `${short(Y, 30)}${lag ? ` (year ${lag > 0 ? "+" : ""}${lag})` : ""}`, n: true, value: (d) => fmt(d.y, 4) }]),
  });
  const [cTog] = toggle(["Points", "Connected"], p.path === "1" ? 1 : 0, (i) => set({ path: i ? "1" : undefined }));
  const scatterCard = chartCard({
    title: "Each year as a point", tip: tip("scatter"),
    sub: `X across, Y up${tf === "level" ? "" : `, ${tfName}`}. The dashed line is the least-squares fit.`,
    actions: cTog,
    render: (box) => timeScatter(box, a, fit, labels, X, Y, p.path === "1"),
  });
  const lagCard = chartCard({
    title: "Correlation at each lag", tip: tip("lag"), height: "short",
    sub: "Positive lag: X this year against Y that many years later; the outlined bar is the lag in use (click a bar to use it). The shaded band is roughly where chance alone would put r (±1.96/√effective n).",
    render: (box) => lagChart(box, X, Y, tf, lag, from, to, nEff, set),
  });
  left.append(lineCard, scatterCard, lagCard);

  const right = el("div", statCard({ r, rho, tau, fit, n, X, Y, mode: "time", r1x, r1y, nEff, adj, part, control }),
    el("div.card", el("h3", "Reading"), reading,
      el("p.small.muted", el("span.badge", "Exploratory association"), " ", term("evidence_levels", "Why this label?"))),
    el("div.card", el("h3", "Things to check"), checkList(checks)),
    exportCard(() => toCsv(a.years.map((t, i) => ({ t, x: a.x[i], y: a.y[i] })), [
      { label: "year_x", value: (d) => d.t }, { label: `${X.id} (${tf})`, value: (d) => d.x },
      { label: `${Y.id} (${tf}${lag ? `, lag ${lag}` : ""})`, value: (d) => d.y }]), `compare-${X.id}-${Y.id}.csv`.replace(/[^\w.-]+/g, "_")));
  root.append(el("div.split.mt", left, right));
}

function zLines(box, a, X, Y, lag, tf) {
  const zx = S.zscores(a.x), zy = S.zscores(a.y);
  chart(box, () => {
    const t = tokens();
    return {
      grid: { left: 44, right: 16, top: 14, bottom: 30 },
      xAxis: axis("value", { min: a.years[0], max: a.years[a.years.length - 1], axisLabel: { color: t.muted, formatter: (v) => String(v) }, minInterval: 1 }),
      yAxis: axis("value", { name: "SDs from mean", nameLocation: "middle", nameGap: 30 }),
      tooltip: {
        trigger: "axis", axisPointer: { type: "line", lineStyle: { color: t.axis } },
        formatter: (ps) => {
          const i = a.years.indexOf(ps[0].value[0]);
          return tipHtml(lag ? `${a.years[i]} (Y: ${a.years[i] + lag})` : String(a.years[i]), [
            [t.s1, short(X, 34), fmt(a.x[i], 4)], [t.s2, short(Y, 34), fmt(a.y[i], 4)]],
          tf === "level" ? `z: ${fmt(zx[i], 2)} and ${fmt(zy[i], 2)}` : `As compared (${tf}); z: ${fmt(zx[i], 2)} and ${fmt(zy[i], 2)}`);
        },
      },
      series: [
        { type: "line", name: "X", data: a.years.map((y, i) => [y, zx[i]]), symbol: "circle", symbolSize: 5, showSymbol: a.years.length < 30, lineStyle: { width: 2, color: t.s1 }, itemStyle: { color: t.s1 }, connectNulls: false },
        { type: "line", name: "Y", data: a.years.map((y, i) => [y, zy[i]]), symbol: "circle", symbolSize: 5, showSymbol: a.years.length < 30, lineStyle: { width: 2, color: t.s2 }, itemStyle: { color: t.s2 } },
      ],
    };
  });
}

function ownUnits(box, a, X, Y, lag) {
  box.style.display = "grid";
  box.style.gridTemplateRows = "1fr 1fr";
  const top = el("div"), bottom = el("div");
  box.append(top, bottom);
  const one = (node, V, vals, colour, label, lastAxis) => chart(node, () => {
    const t = tokens();
    return {
      grid: { left: 60, right: 16, top: 22, bottom: lastAxis ? 26 : 8 },
      title: { text: label, left: 60, top: 0, textStyle: { fontSize: 12, fontWeight: 600, color: t.ink2 } },
      xAxis: axis("value", { min: a.years[0], max: a.years[a.years.length - 1], axisLabel: { show: lastAxis, color: t.muted, formatter: (v) => String(v) }, minInterval: 1 }),
      yAxis: axis("value", { axisLabel: { color: t.muted, formatter: (v) => fmt(v, 3) } }),
      tooltip: { trigger: "axis", formatter: (ps) => tipHtml(String(ps[0].value[0]), [[t[colour], short(V, 40), fmt(ps[0].value[1], 4)]], V.unit || "") },
      series: [{ type: "line", data: a.years.map((y, i) => [y, vals[i]]), showSymbol: a.years.length < 30, symbolSize: 5, lineStyle: { width: 2, color: t[colour] }, itemStyle: { color: t[colour] } }],
    };
  });
  requestAnimationFrame(() => {
    one(top, X, a.x, "s1", `X: ${short(X, 60)}`, false);
    one(bottom, Y, a.y, "s2", `Y: ${short(Y, 60)}${lag ? ` (year ${lag > 0 ? "+" : ""}${lag})` : ""}`, true);
  });
}

function timeScatter(box, a, fit, labels, X, Y, connected) {
  const xmin = Math.min(...a.x), xmax = Math.max(...a.x);
  chart(box, () => {
    const t = tokens();
    const pts = a.x.map((x, i) => ({ value: [x, a.y[i]], name: labels[i], label: { show: i === 0 || i === a.x.length - 1, formatter: labels[i], position: "top", color: t.ink2, fontSize: 11 } }));
    return {
      grid: { left: 64, right: 24, top: 40, bottom: 44 },
      xAxis: axis("value", { name: short(X, 70), nameLocation: "middle", nameGap: 28, axisLabel: { color: t.muted, formatter: (v) => fmt(v, 3) } }),
      yAxis: axis("value", { name: short(Y, 60), nameLocation: "end", nameTextStyle: { align: "left", color: tokens().muted }, axisLabel: { color: t.muted, formatter: (v) => fmt(v, 3) } }),
      tooltip: { trigger: "item", formatter: (q) => (q.seriesType === "scatter" ? tipHtml(q.name, [[t.s1, short(X, 34), fmt(q.value[0], 4)], [t.s2, short(Y, 34), fmt(q.value[1], 4)]]) : "") },
      series: [
        { type: "line", data: [[xmin, fit.intercept + fit.slope * xmin], [xmax, fit.intercept + fit.slope * xmax]], showSymbol: false, silent: true, lineStyle: { type: "dashed", width: 1.5, color: t.ink2 }, z: 1 },
        connected ? { type: "line", data: a.x.map((x, i) => [x, a.y[i]]), showSymbol: false, silent: true, lineStyle: { width: 1, color: t.sMuted }, z: 2 } : null,
        { type: "scatter", data: pts, symbolSize: 10, itemStyle: { color: t.s1, borderColor: t.surface, borderWidth: 1.5 }, emphasis: { scale: 1.4 }, z: 3 },
      ].filter(Boolean),
    };
  });
}

function lagChart(box, X, Y, tf, lag, from, to, nEff, set) {
  const L = 6;
  const rows = [];
  for (let k = -L; k <= L; k++) {
    const al = alignTime(X, Y, { tf, lag: k, from, to });
    rows.push({ k, n: al.years.length, r: al.years.length >= 4 ? S.pearsonR(al.x, al.y) : null });
  }
  const band = 1.96 / Math.sqrt(Math.max(nEff, 3));
  chart(box, () => {
    const t = tokens();
    return {
      grid: { left: 44, right: 16, top: 12, bottom: 30 },
      xAxis: axis("category", { data: rows.map((d) => (d.k > 0 ? `+${d.k}` : String(d.k))), axisLabel: { color: t.muted } }),
      yAxis: axis("value", { min: -1, max: 1, interval: 0.5 }),
      tooltip: { trigger: "item", formatter: (q) => { const d = rows[q.dataIndex]; return tipHtml(`Lag ${d.k > 0 ? "+" : ""}${d.k}`, [[t.s1, "r", d.r == null ? "too few years" : r2d(d.r)], [null, "pairs", String(d.n)]], d.k === lag ? "The lag shown above" : "Click to use this lag"); } },
      series: [{
        type: "bar", barWidth: "55%",
        data: rows.map((d) => ({ value: d.r, itemStyle: { color: t.s1, borderColor: d.k === lag ? t.ink : t.s1, borderWidth: d.k === lag ? 2 : 0, borderRadius: d.r >= 0 ? [4, 4, 0, 0] : [0, 0, 4, 4] } })),
        markArea: { silent: true, itemStyle: { color: t.sMuted, opacity: 0.25 }, data: [[{ yAxis: -band }, { yAxis: band }]] },
      }],
    };
  }).off("click").on("click", (q) => set({ lag: rows[q.dataIndex].k || undefined }));
}

// ------------------------------------------------------------------------------------------- across economies

function renderEcon(root, ds, p, X, Y, control, set) {
  const tx = p.tx || "level", ty = p.ty || "level", group = p.g || "all", tc = p.tc || "level";
  const a = alignEcon(ds, X, Y, { tx, ty, group, Z: control, tz: tc });
  const n = a.idx.length;
  if (n < 5) {
    root.append(el("div.card.mt", el("div.empty", el("p", `Only ${n} economies have both measures${group !== "all" ? " in this group" : ""}${control ? " and the control" : ""}. Choose other measures or a wider group.`))));
    return;
  }
  const r = S.pearson(a.x, a.y), rho = S.spearman(a.x, a.y), tau = S.kendall(a.x, a.y), fit = S.linFit(a.x, a.y);
  const part = control ? S.partial(a.x, a.y, [a.z]) : null;
  const econ = a.idx.map((i) => ds.economies[i]);
  const auAt = a.idx.indexOf(ds.au);

  const extra = [];
  const years = [X, Y].filter((V) => V.years).map((V) => {
    const ys = a.idx.map((i) => V.years[i]).filter((y) => y != null);
    return [V, Math.min(...ys), Math.max(...ys)];
  }).filter(([, lo, hi]) => hi > lo);
  for (const [V, lo, hi] of years) extra.push({ level: "info", body: [el("b", "Mixed data years. "), `"${short(V, 45)}" uses each economy's latest value, from ${lo} to ${hi} (`, term("data_year", "data year"), "). Hover a point for its year."] });
  if (X.year && Y.year && X.year !== Y.year && !/edition/.test(X.year + Y.year)) extra.push({ level: "info", body: [el("b", "Different reference years: "), `X is ${X.year}, Y is ${Y.year}.`] });
  if (group !== "all") extra.push({ level: "info", body: [el("b", "A subgroup only. "), "Narrowing the economies narrows the range, which usually weakens a correlation (", term("restricted_range", "restricted range"), ")."] });
  const both = ds.economies.length;
  if (n < 0.6 * Math.min(X.cov.n, Y.cov.n)) extra.push({ level: "info", body: [el("b", `${n} of ${both} economies have both. `), "Missing data are rarely random: smaller and poorer economies are missing more often (", term("missing", "missing data"), ")."] });
  if (!control && Math.abs(r.r) >= 0.4) extra.push({ level: "warn", body: [el("b", "Income may be doing the work. "), "Richer economies score higher on most measures. Try controlling for GDP per capita (log scale) to see what is left (", term("confounder", "confounder"), ")."] });
  if (control && part) {
    if ([X, Y].some((V) => V.parts_of?.includes(control.id) || control.parts_of?.includes(V.id))) extra.push({ level: "warn", body: [el("b", "The control is built from one of the measures "), "(or the other way round): removing it removes part of the measure itself."] });
  }
  if (p.col === "income") extra.push({ level: "info", body: ["Coloured by income group: if the groups' own patterns differ from the overall one, see ", term("simpsons", "Simpson's paradox"), "."] });

  const labels = econ.map((e) => e.name);
  const checks = runChecks({ ds, X, Y, x: a.x, y: a.y, labels, n, mode: "economy", tx, ty, extra });

  // Australia's place
  let auNode = null;
  if (auAt >= 0) {
    const resid = fit.resid[auAt], sdRes = Math.sqrt(fit.s2);
    const pctX = (a.x.filter((v) => v < a.x[auAt]).length / (n - 1)) * 100;
    const pctY = (a.y.filter((v) => v < a.y[auAt]).length / (n - 1)) * 100;
    const rankRes = fit.resid.filter((v) => v > resid).length + 1;
    const yUnit = ty === "log" ? "log points" : Y.unit || "units";
    auNode = el("div.card", el("h3", "Where Australia sits"),
      el("dl.statgrid",
        el("dt", "On X", tip("percentile")), el("dd", num("percentile", pctX, `${ordinal(Math.round(pctX))} percentile`)),
        el("dt", "On Y", tip("percentile")), el("dd", num("percentile", pctY, `${ordinal(Math.round(pctY))} percentile`)),
        el("dt", "Against the line", tip("residual")), el("dd", `${resid >= 0 ? "+" : "−"}${fmt(Math.abs(resid), 3)} `, el("span.sub", `${yUnit}; ${fmt(Math.abs(resid / sdRes), 2)} SD ${resid >= 0 ? "above" : "below"}`)),
        el("dt", "Residual rank"), el("dd", `${ordinal(rankRes)} of ${n}`, el("span.sub", "1st = furthest above the line"))),
      el("p.small.ink2.mt", resid >= 0
        ? `Australia's Y is higher than economies with similar X would suggest. ${ty === "log" ? `About ${fmt((Math.exp(resid) - 1) * 100, 2)}% higher.` : ""}`
        : `Australia's Y is lower than economies with similar X would suggest. ${ty === "log" ? `About ${fmt((1 - Math.exp(resid)) * 100, 2)}% lower.` : ""} A gap worth a closer look, not yet an opportunity: the line is an average over very different economies.`),
      control ? el("p.small.muted", "Measured against the plain line of Y on X; the added-variable plot shows Australia once the control is removed.") : null);
  } else {
    auNode = el("div.card", el("h3", "Where Australia sits"), el("p.muted", "Australia is not in this comparison (a value is missing, or the group excludes it)."));
  }

  const reading = el("p.reading",
    `Across ${n} economies, `, el("strong", short(X, 50)), " and ", el("strong", short(Y, 50)), " have ",
    el("strong", `a ${strength(r.r)} ${direction(r.r)} association`), ` (r = ${r2d(r.r)}, 95% interval ${r2d(r.lo)} to ${r2d(r.hi)}; ρ = ${r2d(rho.r)}). `,
    part && Number.isFinite(part.r) ? `Holding ${short(control, 40)} fixed, it is ${strength(part.r)} (partial r = ${r2d(part.r)}, p = ${pval(part.p)}). ` : "",
    auAt >= 0 ? `Australia sits ${fit.resid[auAt] >= 0 ? "above" : "below"} the line.` : "");

  const view = p.res === "1" && part?.rx ? "res" : "raw";
  const [rTog] = control ? toggle(["Values", `After removing ${short(control, 24)}`], view === "res" ? 1 : 0, (i) => set({ res: i ? "1" : undefined })) : [null];
  const scatter = chartCard({
    title: view === "res" ? "After removing the control (an added-variable plot)" : "Each economy as a point",
    tip: tip(view === "res" ? "partial" : "scatter"),
    sub: view === "res" ? `What is left of X and of Y once ${short(control, 50)} has been regressed out of each. The slope of this cloud is the partial association.` : "Australia in orange, labelled. Hover a point for the economy, its values and data years. The dashed line is the least-squares fit.",
    legend: p.col === "income"
      ? legend([...INCOME_ORDER.map((k, i) => ["dot", `var(--ramp-${i + 1})`, INCOME_NAMES[k]]), ["dot", "var(--s-muted)", "Not in the GII"], ["dot", "var(--s2)", "Australia"]])
      : legend([["dot", "var(--s-muted)", "Other economies"], ["dot", "var(--s2)", "Australia"]]),
    actions: rTog, height: "tall",
    render: (box) => econScatter(box, ds, a, econ, fit, X, Y, { tx, ty, colour: p.col, view, part, auAt }),
    table: () => dataTable(econ.map((e, i) => ({ e, x: a.x[i], y: a.y[i], res: fit.resid[i] })).sort((m, q) => q.res - m.res), [
      { label: "Economy", value: (d) => d.e.name }, { label: `X${tx === "log" ? " (log)" : ""}`, n: true, value: (d) => fmt(d.x, 4) },
      { label: `Y${ty === "log" ? " (log)" : ""}`, n: true, value: (d) => fmt(d.y, 4) }, { label: "Residual", n: true, value: (d) => fmt(d.res, 3) }],
    { rowClass: (d) => (d.e.iso3 === "AUS" ? "au" : null) }),
  });

  const right = el("div", statCard({ r, rho, tau, fit, n, X, Y, mode: "economy", part, control }), auNode,
    el("div.card", el("h3", "Reading"), reading, el("p.small.muted", el("span.badge", "Exploratory association"), " ", term("evidence_levels", "Why this label?"))),
    el("div.card", el("h3", "Things to check"), checkList(checks)),
    exportCard(() => toCsv(econ.map((e, i) => ({ e, x: a.x[i], y: a.y[i], z: a.z?.[i] })), [
      { label: "iso3", value: (d) => d.e.iso3 }, { label: "economy", value: (d) => d.e.name }, { label: "income_group", value: (d) => d.e.income },
      { label: `${X.id}${tx === "log" ? " (log)" : ""}`, value: (d) => d.x }, { label: `${Y.id}${ty === "log" ? " (log)" : ""}`, value: (d) => d.y },
      ...(control ? [{ label: `${control.id}${tc === "log" ? " (log)" : ""}`, value: (d) => d.z }] : [])]), `compare-${X.id}-${Y.id}.csv`.replace(/[^\w.-]+/g, "_")));
  root.append(el("div.split.mt", el("div", scatter), right));
}

function econScatter(box, ds, a, econ, fit, X, Y, { tx, ty, colour, view, part, auAt }) {
  const res = view === "res";
  const xs = res ? part.rx : a.x, ys = res ? part.ry : a.y;
  // with log scales, plot the published values on log axes; the fit is drawn back from log space
  const back = (v, t) => (t === "log" && !res ? Math.exp(v) : v);
  const f = res ? S.linFit(xs, ys) : fit;
  const lo = Math.min(...xs), hi = Math.max(...xs);
  const line = Array.from({ length: 41 }, (_, i) => lo + ((hi - lo) * i) / 40).map((v) => [back(v, tx), back(f.intercept + f.slope * v, ty)]);
  const yr = (V, i) => (V.years ? V.years[a.idx[i]] : V.year);
  chart(box, () => {
    const t = tokens();
    const col = (e) => (colour === "income" ? (e.income_code ? t.ramp[INCOME_ORDER.indexOf(e.income_code)] : t.sMuted) : t.sMuted);
    const pts = econ.map((e, i) => ({ value: [back(xs[i], tx), back(ys[i], ty)], name: e.name, i, itemStyle: { color: col(e) } }));
    const au = auAt >= 0 ? [{ ...pts[auAt], itemStyle: { color: t.s2 } }] : [];
    return {
      grid: { left: 70, right: 30, top: 40, bottom: 50 },
      xAxis: axis(tx === "log" && !res ? "log" : "value", { name: res ? `X after removing the control` : `${short(X, 70)}${tx === "log" ? " (log scale)" : ""}`, nameLocation: "middle", nameGap: 32, axisLabel: { color: t.muted, formatter: (v) => fmt(v, 3) } }),
      yAxis: axis(ty === "log" && !res ? "log" : "value", { name: res ? "Y after removing the control" : `${short(Y, 40)}${ty === "log" ? " (log)" : ""}`, nameLocation: "end", nameTextStyle: { align: "left", color: t.muted }, axisLabel: { color: t.muted, formatter: (v) => fmt(v, 3) } }),
      tooltip: {
        trigger: "item",
        formatter: (q) => {
          if (q.seriesType !== "scatter") return "";
          const i = q.data.i, e = econ[i];
          return tipHtml(e.name, [[t.s1, short(X, 30), fmt(X.values[a.idx[i]], 4)], [t.s2, short(Y, 30), fmt(Y.values[a.idx[i]], 4)],
            [null, "Residual", fmt(f.resid[i], 3)]], [e.income, yr(X, i) && `X ${yr(X, i)}`, yr(Y, i) && `Y ${yr(Y, i)}`].filter(Boolean).join(" · "));
        },
      },
      series: [
        { type: "line", data: line, showSymbol: false, silent: true, lineStyle: { type: "dashed", width: 1.5, color: t.ink2 }, z: 1 },
        { type: "scatter", data: pts, symbolSize: 9, itemStyle: { borderColor: t.surface, borderWidth: 1.5 }, emphasis: { scale: 1.5 }, z: 2 },
        { type: "scatter", data: au, symbolSize: 15, itemStyle: { borderColor: t.surface, borderWidth: 2 }, label: { show: true, formatter: "Australia", position: "right", color: t.ink, fontWeight: 700 }, z: 3 },
      ],
    };
  });
}

// ------------------------------------------------------------------------------------------- pieces

function statCard({ r, rho, tau, fit, n, X, Y, mode, r1x, r1y, nEff, adj, part, control }) {
  const meter = el("div.meter");
  if (Number.isFinite(r.lo)) {
    const pos = (v) => `${((v + 1) / 2) * 100}%`;
    meter.append(el("span.ci", { style: { left: pos(r.lo), width: `${((r.hi - r.lo) / 2) * 100}%` } }), el("span.pt", { style: { left: pos(r.r) } }));
  }
  const rows = [
    ["n", `${nfmt(n)} ${mode === "time" ? "years" : "economies"}`, n],
    ["pearson", [num("pearson", r.r, r2d(r.r)), el("span.sub", "95% CI ", r2d(r.lo), " to ", r2d(r.hi))]],
    ["p_value", [num("p_value", r.p, pval(r.p)), el("span.sub", "for r")]],
    ["spearman", [num("spearman", rho.r, r2d(rho.r)), el("span.sub", `p ${pval(rho.p)}`)]],
    ["kendall", [num("kendall", tau.tau, r2d(tau.tau)), el("span.sub", `p ${pval(tau.p)}`)]],
    ["r2", num("r2", r.r * r.r, fmt(r.r * r.r, 2))],
    ["slope", [fmt(fit.slope, 3), el("span.sub", `Y per unit of X, ± ${fmt(1.96 * fit.seSlope, 2)}`)]],
  ];
  if (mode === "time") {
    rows.push(["autocorrelation", [num("autocorrelation", r1x, r2d(r1x)), " / ", num("autocorrelation", r1y, r2d(r1y)), el("span.sub", "X / Y")]]);
    rows.push(["effective_n", num("effective_n", nEff, fmt(nEff, 2))]);
    rows.push(["adjusted_p", num("adjusted_p", adj.p, pval(adj.p))]);
  }
  if (part) {
    rows.push(["partial", Number.isFinite(part.r) ? [num("partial", part.r, r2d(part.r)), el("span.sub", `p ${pval(part.p)}, n ${part.idx.length}`)] : "too few pairs"]);
  }
  const names = { n: "Pairs", pearson: "Pearson's r", p_value: "p-value", spearman: "Spearman's ρ", kendall: "Kendall's τ", r2: "R²", slope: "Slope", autocorrelation: "Lag-1 autocorrelation", effective_n: "Effective n", adjusted_p: "Adjusted p", partial: `Partial r${control ? `, holding ${short(control, 22)}` : ""}` };
  return el("div.card",
    el("div.card-head", el("h3", "The numbers", tip("correlation"))),
    el("div.big-r", el("span.val", r2d(r.r)), el("span.ink2", `Pearson's r: ${strength(r.r)} ${direction(r.r)}`)),
    meter, el("div.meter-scale", el("span", "−1"), el("span", "0"), el("span", "+1")),
    el("p.small.muted", "The bar is r; the box around it the 95% interval."),
    el("dl.statgrid.mt", rows.map(([k, v]) => [el("dt", names[k], tip(k)), el("dd", v)])));
}

function about(vars, lenses) {
  const d = el("details.mt", el("summary.small", "About these measures: definitions, units and sources"));
  for (const v of vars) {
    d.append(el("div.mt", el("strong", v.name), " ", el("span.chip", SOURCES[v.source] || v.source), " ",
      el("span.chip.lens", { "data-term": v.lens, tabindex: 0 }, lenses?.[v.lens]?.short ?? v.lens),
      el("p.small.ink2", [v.unit ? `Unit: ${v.unit}. ` : "", `Coverage: ${coverage(v)}. `, v.description || "", v.note ? ` ${v.note}` : ""])));
  }
  return d;
}

function exportCard(csv, name) {
  return el("div.card.row",
    el("button.btn", { type: "button", onclick: () => download(name, csv()) }, "Download the pairs (CSV)"),
    el("button.btn", { type: "button", onclick: (e) => { navigator.clipboard?.writeText(location.href); e.target.textContent = "Link copied"; } }, "Copy a link to this view"));
}

export function seg(options, value, onPick) {
  return el("div.seg", { role: "group" }, options.map(([k, name]) => el("button", {
    type: "button", "aria-pressed": String(k === value), onclick: () => k !== value && onPick(k),
    "data-term": TIME_TERMS[k] || (k === "log" ? "log" : null) || undefined,
  }, name)));
}

function toggle(names, active, onPick) {
  const t = el("div.toggle", { role: "group" }, names.map((nm, i) => el("button", { type: "button", "aria-pressed": String(i === active), onclick: () => i !== active && onPick(i) }, nm)));
  return [t];
}

function starters(mode, go) {
  const list = STARTERS.filter((s) => s.m === mode);
  const d = el("details.card.flat", { open: !location.hash.includes("x=") },
    el("summary", el("strong", "Starter questions"), el("span.muted.small", "  Comparisons that speak to the research goal's questions. Each opens with its settings.")),
    el("div.starters.mt", list.map((s) => el("button.starter", {
      type: "button",
      onclick: () => go("compare", { m: s.m, x: s.x, y: s.y, t: s.t, tx: s.tx, ty: s.ty, c: s.c, tc: s.tc }),
    }, el("span.q", s.q), el("span.why", s.why), el("span.chip.lens.rq", `Research question ${s.rq.slice(1)}`)))),
    el("p.small.muted.mt", "The research questions are in ", link("the research goal", "https://github.com/Thomas-Amann-IPAustralia/Aus-GII-Breakdown/blob/main/docs/research-goal.md"), ": Q1 public value, Q2 who benefits, Q3 what determines value, Q4 opportunities, Q5 outcomes of interventions."));
  return d;
}
