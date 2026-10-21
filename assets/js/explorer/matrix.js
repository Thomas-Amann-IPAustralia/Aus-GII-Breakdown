// The correlation matrix: every pair in a chosen set at once, the set's multicollinearity (VIF, condition number),
// and a descriptive regression of one measure on the others.

import { axis, chart, chartCard, dataTable, tipHtml, tokens } from "../charts.js";
import { construction } from "../data.js";
import { num, term, tip } from "../glossary.js";
import * as S from "../stats.js";
import { el, fmt, pval, r2d } from "../util.js";
import { checkList, econValues, GROUPS, inGroup, MATRIX_PRESETS, short, TIME_TRANSFORMS } from "./common.js";
import { seg } from "./compare.js";
import { picker } from "./picker.js";

const MAX_VARS = 14;

export function renderMatrix(root, ds, p, { go, lenses }) {
  const mode = ds.mode;
  const ids = (p.v || "").split(",").filter((id) => ds.byId.has(id));
  const set = (patch) => go("matrix", { ...p, ...patch });
  const setIds = (list) => set({ v: list.join(",") || undefined, out: undefined });
  const method = p.meth || "pearson";
  const listwise = p.miss === "listwise";
  const tf = p.t || "level";
  const group = p.g || "all";

  const chips = el("div.row", ids.map((id, i) => el("span.chip.x", {
    role: "button", tabindex: 0, title: "Remove", onclick: () => setIds(ids.filter((x) => x !== id)),
    onkeydown: (e) => e.key === "Enter" && setIds(ids.filter((x) => x !== id)),
  }, `${i + 1}. ${short(ds.byId.get(id), 48)}`)));
  const add = ids.length < MAX_VARS
    ? picker({ ds, label: "a measure to add", lenses, placeholder: `Add a measure (${ids.length} of ${MAX_VARS})…`, exclude: ids, onChange: (id) => id && setIds([...ids, id]) })
    : el("p.small.muted", `${MAX_VARS} measures is the limit: remove one to add another.`);
  const presets = el("div.row", el("span.small.muted", "Presets:"),
    MATRIX_PRESETS[mode].map((pr) => el("button.btn.small", { type: "button", onclick: () => setIds(pr.ids.filter((id) => ds.byId.has(id))) }, pr.name)),
    ids.length ? el("button.btn.small", { type: "button", onclick: () => setIds([]) }, "Clear") : null);
  const opts = el("div.controls.mt",
    el("label.field", el("span.lab", "Correlation", tip("spearman")), seg([["pearson", "Pearson's r"], ["spearman", "Spearman's ρ"]], method, (v) => set({ meth: v }))),
    el("label.field", el("span.lab", "Missing values", tip("pairwise")), seg([["pairwise", "Pairwise"], ["listwise", "Complete cases"]], listwise ? "listwise" : "pairwise", (v) => set({ miss: v === "listwise" ? v : undefined }))),
    mode === "time"
      ? el("label.field", el("span.lab", "Compare as", tip("spurious")), seg(TIME_TRANSFORMS, tf, (v) => set({ t: v })))
      : el("label.field", el("span.lab", "Economies"), el("select", { onchange: (e) => set({ g: e.target.value }) }, GROUPS.map(([k, nm]) => el("option", { value: k, selected: group === k }, nm)))),
    mode === "economy" ? el("label.check", el("input", { type: "checkbox", checked: p.log === "1", onchange: (e) => set({ log: e.target.checked ? "1" : undefined }) }), "Log scale for skewed positive measures", tip("log")) : null);
  root.append(el("div.card", el("h3", "Measures in the matrix"), el("div.stack", chips, add, presets), opts));

  if (ids.length < 2) {
    root.append(el("div.card.mt", el("div.empty", el("p", "Add at least two measures, or start from a preset."))));
    return;
  }

  // the columns: one array per measure, aligned on years or economies
  const vars = ids.map((id) => ds.byId.get(id));
  let rowsLabel, cols;
  if (mode === "time") {
    const series = vars.map((v) => S.transform(v.series, tf));
    const lo = Math.min(...series.map((s) => Math.min(...s.keys()))), hi = Math.max(...series.map((s) => Math.max(...s.keys())));
    rowsLabel = [];
    for (let y = lo; y <= hi; y++) rowsLabel.push(String(y));
    cols = series.map((s) => rowsLabel.map((y) => (s.has(+y) ? s.get(+y) : null)));
  } else {
    const keep = ds.economies.map((e, i) => i).filter((i) => inGroup(ds.economies[i], group));
    rowsLabel = keep.map((i) => ds.economies[i].name);
    cols = vars.map((v) => {
      const skewed = p.log === "1" && v.values.every((x) => x == null || x > 0) && S.skew(v.values.filter((x) => x != null)) > 1.5;
      v._logged = skewed;
      const vals = econValues(v, skewed ? "log" : "level");
      return keep.map((i) => vals[i]);
    });
  }
  const M = S.corrMatrix(cols, { method, listwise });
  const k = ids.length;
  const label = (i) => `${i + 1}. ${short(vars[i], 34)}`;

  const heat = chartCard({
    title: `${method === "spearman" ? "Spearman's ρ" : "Pearson's r"} for every pair`, tip: tip("correlation"),
    sub: `Blue: move together; red: move oppositely; grey: no straight-line pattern. ${listwise ? "Complete cases only." : "Each cell uses its own overlap: hover for n."} Click a cell to compare the pair.`,
    height: k > 5 ? "tall" : "",
    render: (box) => {
      const c = chart(box, () => {
        const t = tokens();
        const data = [];
        for (let a = 0; a < k; a++) for (let b = 0; b < k; b++) {
          const rv = Number.isFinite(M.R[a][b]) ? +M.R[a][b].toFixed(3) : null;
          data.push({ value: [b, k - 1 - a, rv, a, b], label: { color: rv == null ? t.ink : textOn(t.div, rv) } });
        }
        return {
          grid: { left: 230, right: 20, top: 10, bottom: 90 },
          xAxis: axis("category", { data: vars.map((_, i) => String(i + 1)), axisLabel: { color: t.muted }, splitLine: { show: false } }),
          yAxis: axis("category", { data: vars.map((_, i) => label(i)).reverse(), axisLabel: { color: t.ink2, width: 220, overflow: "truncate" }, splitLine: { show: false } }),
          visualMap: { min: -1, max: 1, calculable: false, orient: "horizontal", left: "center", bottom: 8, itemWidth: 12, itemHeight: 220, text: ["+1", "−1"], textStyle: { color: t.muted }, inRange: { color: t.div }, dimension: 2 },
          tooltip: {
            trigger: "item", formatter: (q) => {
              const [, , rv, a, b] = q.data.value;
              const how = construction(ds, ids[a], ids[b]);
              return tipHtml(`${short(vars[a], 40)} × ${short(vars[b], 40)}`, [[null, method === "spearman" ? "ρ" : "r", rv == null ? "–" : r2d(rv)], [null, "n", String(M.N[a][b])], [null, "p", a === b ? "–" : pval(M.P[a][b])]],
                a === b ? "The diagonal: each measure with itself." : how ? "Built from each other: a mechanical link." : "Click to compare");
            },
          },
          series: [{
            type: "heatmap", data, label: { show: k <= 12, formatter: (q) => (q.data.value[2] == null ? "" : r2d(q.data.value[2])), fontSize: 11 },
            itemStyle: { borderColor: t.surface, borderWidth: 2, borderRadius: 3 }, emphasis: { itemStyle: { borderColor: t.ink, borderWidth: 2 } },
          }],
        };
      });
      c.off("click").on("click", (q) => {
        const [, , , a, b] = q.data.value;
        if (a !== b) go("compare", { m: mode, x: ids[b], y: ids[a], t: mode === "time" && tf !== "level" ? tf : undefined, g: group !== "all" ? group : undefined });
      });
    },
    table: () => dataTable(vars.map((v, a) => ({ v, a })), [{ label: "Measure", value: (d) => label(d.a) }, ...vars.map((_, b) => ({ label: String(b + 1), n: true, value: (d) => (Number.isFinite(M.R[d.a][b]) ? r2d(M.R[d.a][b]) : "–") }))]),
  });

  // multicollinearity on complete cases
  const col = S.collinearity(cols);
  const colChecks = [];
  if (col.tooFew) colChecks.push({ level: "serious", body: [el("b", `Only ${col.n} ${mode === "time" ? "years" : "economies"} have every measure. `), "Too few to assess the set; remove a measure with short coverage."] });
  else {
    const worst = Math.max(...col.vif);
    if (worst >= 10) colChecks.push({ level: "serious", body: [el("b", "Severe multicollinearity. "), "At least one measure is almost entirely predicted by the others (", term("vif", "VIF"), " ≥ 10). A regression on this set cannot separate their contributions."] });
    else if (worst >= 5) colChecks.push({ level: "warn", body: [el("b", "Notable multicollinearity. "), "Some measures overlap heavily (VIF 5 to 10); coefficients for them will be unstable."] });
    else colChecks.push({ level: "ok", body: [el("b", "Little multicollinearity. "), "Every VIF is under 5."] });
    if (col.n < 5 * k) colChecks.push({ level: "warn", body: [el("b", `Only ${col.n} complete ${mode === "time" ? "years" : "economies"} for ${k} measures. `), "With so few, the VIFs themselves are unstable; treat them as rough."] });
    let siblings = 0;
    for (let a = 0; a < k; a++) for (let b = a + 1; b < k; b++) {
      const how = construction(ds, ids[a], ids[b]);
      if (how === "siblings") siblings++;
      else if (how) colChecks.push({ level: "warn", body: [el("b", `${a + 1} and ${b + 1}: one is built from the other `), "(", term("part_whole", "part and whole"), "), which forces them to correlate."] });
    }
    if (siblings) colChecks.push({ level: "info", body: [`${siblings} pair${siblings === 1 ? " feeds" : "s feed"} the same composite index. Not a mechanical link, but chosen by the index's designers to belong together (`, term("part_whole", "part and whole"), ")."] });
  }
  const vifCard = el("div.card",
    el("h3", "Multicollinearity", tip("multicollinearity")),
    el("p.small.muted", `Over the ${col.n} ${mode === "time" ? "years" : "economies"} with every measure. `, mode === "time" ? "Over time most series share trends, so expect high VIFs in levels." : ""),
    col.tooFew ? null : el("dl.statgrid", el("dt", "Condition number", tip("condition_number")), el("dd", num("condition_number", col.condition, fmt(col.condition, 3)))),
    col.tooFew ? null : dataTable(vars.map((v, i) => ({ v, i, vif: col.vif[i] })), [
      { label: "Measure", value: (d) => label(d.i) },
      { head: el("span", "VIF", tip("vif")), label: "VIF", n: true, node: (d) => num("vif", d.vif, Number.isFinite(d.vif) ? fmt(d.vif, 3) : "∞") },
      { label: "R² on the others", n: true, value: (d) => (Number.isFinite(d.vif) ? fmt(1 - 1 / d.vif, 2) : "1") },
    ]),
    el("div.mt", checkList(colChecks)));

  root.append(el("div.split.mt", el("div", heat), el("div", vifCard)));
  root.append(modelCard(ds, vars, ids, cols, p, set, col, mode));
  if (mode === "economy" && vars.some((v) => v._logged)) root.append(el("p.small.muted.mt", "On a log scale here: ", vars.filter((v) => v._logged).map((v) => short(v, 40)).join("; "), "."));
}

function modelCard(ds, vars, ids, cols, p, set, col, mode) {
  const out = ids.includes(p.out) ? ids.indexOf(p.out) : 0;
  const preds = vars.map((_, i) => i).filter((i) => i !== out);
  const card = el("div.card.mt",
    el("div.card-head", el("div", el("h3", "A descriptive regression", tip("regression")),
      el("p.card-sub", "One measure on all the others at once, on the complete cases. Each coefficient is that measure's association with the outcome holding the others fixed: descriptive, not an effect.")),
    el("label.field", el("span.lab", "Outcome"), el("select", { onchange: (e) => set({ out: e.target.value }) }, vars.map((v, i) => el("option", { value: ids[i], selected: i === out }, `${i + 1}. ${short(v, 50)}`))))));
  const keep = [];
  for (let i = 0; i < cols[0].length; i++) if (cols.every((c) => c[i] != null && Number.isFinite(c[i]))) keep.push(i);
  const nObs = keep.length;
  if (nObs < preds.length + 3) {
    card.append(el("p.notice", `Only ${nObs} complete ${mode === "time" ? "years" : "economies"} for ${preds.length} predictors: too few to fit. Remove measures with short coverage.`));
    return card;
  }
  let fit;
  try {
    fit = S.ols(keep.map((i) => cols[out][i]), preds.map((j) => keep.map((i) => cols[j][i])));
  } catch {
    card.append(el("p.notice", "The predictors are perfectly collinear (one is an exact combination of others), so the model cannot be fitted. Remove one of them."));
    return card;
  }
  const rows = preds.map((j, c) => ({ j, c: fit.coef[c + 1], vif: S.collinearity(preds.map((q) => keep.map((i) => cols[q][i]))).vif[c] }));
  const warn = [];
  if (nObs / preds.length < 10) warn.push({ level: "warn", body: [el("b", `${nObs} observations for ${preds.length} predictors. `), "Fewer than 10 per predictor: the model will fit noise (", term("overfitting", "overfitting"), ")."] });
  if (rows.some((r) => r.vif >= 5)) warn.push({ level: "warn", body: [el("b", "Collinear predictors. "), "Where VIF ≥ 5 a coefficient's size and even its sign are unreliable (", term("multicollinearity"), ")."] });
  for (const j of preds) if (["a-in-b", "b-in-a"].includes(construction(ds, ids[out], ids[j]))) warn.push({ level: "serious", body: [el("b", `${j + 1} and the outcome: one is built from the other. `), "Its coefficient partly reflects the index's arithmetic."] });
  if (mode === "time") warn.push({ level: "info", body: ["Over time, residuals are usually autocorrelated, so these p-values are too small (", term("autocorrelation"), "). Year-on-year changes help."] });
  warn.push({ level: "info", body: [el("b", "Descriptive only. "), "A coefficient is a conditional association in this sample, not what would happen if the predictor changed (", term("causal_inference", "causal inference"), ")."] });

  card.append(
    el("dl.statgrid", el("dt", "Observations"), el("dd", String(nObs)), el("dt", "R²", tip("r2")), el("dd", num("r2", fit.r2, fmt(fit.r2, 2))),
      el("dt", "Adjusted R²", tip("adj_r2")), el("dd", fmt(fit.adjR2, 2))),
    el("div.grid.g2.mt",
      el("div", dataTable(rows, [
        { label: "Predictor", value: (d) => `${d.j + 1}. ${short(vars[d.j], 40)}` },
        { head: el("span", "β (std)", tip("std_coef")), label: "β", n: true, value: (d) => fmt(d.c.std, 2) },
        { label: "95% CI", n: true, value: (d) => `${fmt(d.c.stdLo, 2)} to ${fmt(d.c.stdHi, 2)}` },
        { head: el("span", "p", tip("p_value")), label: "p", n: true, node: (d) => num("p_value", d.c.p, pval(d.c.p)) },
        { head: el("span", "VIF", tip("vif")), label: "VIF", n: true, node: (d) => num("vif", d.vif, fmt(d.vif, 3)) },
      ])),
      el("div", (() => {
        const box = el("div.chart.short");
        requestAnimationFrame(() => chart(box, () => {
          const t = tokens();
          const cats = rows.map((d) => `${d.j + 1}`);
          return {
            grid: { left: 40, right: 20, top: 10, bottom: 30 },
            xAxis: axis("value", { name: "standardised coefficient (SDs of outcome per SD)", nameLocation: "middle", nameGap: 22 }),
            yAxis: axis("category", { data: cats, inverse: true, axisLabel: { color: t.ink2 } }),
            tooltip: { trigger: "item", formatter: (q) => { const d = rows[q.dataIndex]; return tipHtml(short(vars[d.j], 50), [[t.s1, "β", fmt(d.c.std, 2)], [null, "95% CI", `${fmt(d.c.stdLo, 2)} to ${fmt(d.c.stdHi, 2)}`], [null, "p", pval(d.c.p)]]); } },
            series: [
              { type: "custom", renderItem: (params, api) => {
                const lo = api.coord([api.value(0), api.value(2)]), hi = api.coord([api.value(1), api.value(2)]);
                return { type: "line", shape: { x1: lo[0], y1: lo[1], x2: hi[0], y2: hi[1] }, style: { stroke: t.s1, lineWidth: 2 } };
              }, data: rows.map((d, i) => [d.c.stdLo, d.c.stdHi, i]), encode: { x: [0, 1], y: 2 }, silent: true },
              { type: "scatter", data: rows.map((d, i) => [d.c.std, i]), symbolSize: 10, itemStyle: { color: t.s1, borderColor: t.surface, borderWidth: 1.5 },
                markLine: { silent: true, symbol: "none", lineStyle: { color: t.axis, type: "solid" }, data: [{ xAxis: 0 }], label: { show: false } } },
            ],
          };
        }));
        return box;
      })())),
    el("div.mt", checkList(warn)));
  return card;
}

/** Black or white text, whichever reads on the diverging scale's colour at r (the visual map's five stops). */
function textOn(stops, r) {
  const rgb = (h) => [1, 3, 5].map((i) => parseInt(h.slice(i, i + 2), 16));
  const pos = ((r + 1) / 2) * (stops.length - 1);
  const i = Math.min(stops.length - 2, Math.floor(pos)), f = pos - i;
  const [a, b] = [rgb(stops[i]), rgb(stops[i + 1])];
  const lin = (c) => { const v = c / 255; return v <= 0.04045 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4; };
  const [R, G, B] = a.map((c, j) => lin(c + (b[j] - c) * f));
  return 0.2126 * R + 0.7152 * G + 0.0722 * B > 0.22 ? "#0b0b0b" : "#ffffff";
}
