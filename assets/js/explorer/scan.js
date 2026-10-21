// Find correlates: one target against every other measure, with the multiple-testing arithmetic in plain view. Over
// time, the correlation of year-on-year changes sits beside the levels' so shared trends stand out.

import { axis, chart, chartCard, dataTable, tipHtml, tokens } from "../charts.js";
import { construction, SOURCES } from "../data.js";
import { num, term, tip } from "../glossary.js";
import * as S from "../stats.js";
import { download, el, fmt, n as nfmt, pval, r2d, toCsv } from "../util.js";
import { alignEcon, alignTime, checkList, ECON_TRANSFORMS, GROUPS, short, TIME_TRANSFORMS } from "./common.js";
import { seg } from "./compare.js";
import { picker } from "./picker.js";

export function renderScan(root, ds, p, { go, lenses }) {
  const mode = ds.mode;
  const set = (patch) => go("scan", { ...p, ...patch });
  const T = p.x ? ds.byId.get(p.x) : null;
  const tf = p.t || "level";
  const minN = +p.min || (mode === "time" ? 12 : 40);
  const method = p.meth || "pearson";
  const group = p.g || "all";
  const lens = p.lens || "";
  const source = p.src || "";
  const keepBuilt = p.built === "1";
  const control = p.c ? ds.byId.get(p.c) : null;

  const opts = el("div.controls.mt",
    mode === "time"
      ? el("label.field", el("span.lab", "Compare as", tip("spurious")), seg(TIME_TRANSFORMS, tf, (v) => set({ t: v })))
      : el("label.field", el("span.lab", "Target scale", tip("log")), seg(ECON_TRANSFORMS, p.tx || "level", (v) => set({ tx: v }))),
    el("label.field", el("span.lab", "Correlation"), seg([["pearson", "Pearson's r"], ["spearman", "Spearman's ρ"]], method, (v) => set({ meth: v }))),
    el("label.field", el("span.lab", "At least n", tip("n")), el("input", { type: "number", min: 5, max: 200, value: minN, onchange: (e) => set({ min: e.target.value }) })),
    el("label.field", el("span.lab", "Lens", tip("lens")), el("select", { onchange: (e) => set({ lens: e.target.value || undefined }) },
      el("option", { value: "" }, "Every lens"), Object.entries(lenses).map(([k, l]) => el("option", { value: k, selected: lens === k }, l.name)))),
    el("label.field", el("span.lab", "Source"), el("select", { onchange: (e) => set({ src: e.target.value || undefined }) },
      el("option", { value: "" }, "Every source"), [...new Set(ds.vars.map((v) => v.source))].sort().map((s) => el("option", { value: s, selected: source === s }, SOURCES[s] || s)))),
    mode === "economy" ? el("label.field", el("span.lab", "Economies"), el("select", { onchange: (e) => set({ g: e.target.value }) }, GROUPS.map(([k, nm]) => el("option", { value: k, selected: group === k }, nm)))) : null,
    el("label.check", el("input", { type: "checkbox", checked: keepBuilt, onchange: (e) => set({ built: e.target.checked ? "1" : undefined }) }), "Include measures built from or into the target", tip("part_whole")));
  if (mode === "economy") {
    opts.append(el("label.field.grow", el("span.lab", "Control for (optional)", tip("partial")),
      picker({ ds, value: p.c, label: "a control", lenses, placeholder: "Nothing", allowNone: true, exclude: [p.x], onChange: (id) => set({ c: id || undefined }) })));
  }
  root.append(el("div.card",
    el("label.field", el("span.lab", "Target: what should the others be compared with?"),
      picker({ ds, value: p.x, label: "the target", swatch: "var(--s1)", lenses, onChange: (id) => set({ x: id }) })),
    opts));

  if (!T) {
    root.append(el("div.card.mt", el("div.empty", el("p", "Choose a target. Every other measure with enough overlap is correlated with it, and the results are corrected for the number of tests."))));
    return;
  }

  // ---------------------------------------------------------------------------------------- the scan
  const results = [];
  let skippedBuilt = 0;
  for (const V of ds.vars) {
    if (V.id === T.id || (lens && V.lens !== lens) || (source && V.source !== source) || (control && V.id === control.id)) continue;
    if (!keepBuilt && construction(ds, T.id, V.id)) { skippedBuilt++; continue; }
    let x, y, nn, rDiff = null;
    if (mode === "time") {
      const a = alignTime(T, V, { tf });
      if (a.years.length < minN) continue;
      x = a.x; y = a.y; nn = a.years.length;
      if (tf === "level") {
        const d = alignTime(T, V, { tf: "diff" });
        rDiff = d.years.length >= 6 ? S.pearsonR(d.x, d.y) : null;
      }
    } else {
      const a = alignEcon(ds, T, V, { tx: p.tx || "level", ty: "level", group, Z: control, tz: "log" });
      if (a.idx.length < minN) continue;
      nn = a.idx.length;
      if (control) {
        const pr = S.partial(a.x, a.y, [a.z]);
        results.push({ V, n: nn, r: pr.r, p: pr.p, rDiff: null });
        continue;
      }
      x = a.x; y = a.y;
    }
    const t = method === "spearman" ? S.spearman(x, y) : S.pearson(x, y);
    if (!Number.isFinite(t.r)) continue;
    results.push({ V, n: nn, r: t.r, p: t.p, rDiff, lo: t.lo, hi: t.hi });
  }
  const q = S.bh(results.map((d) => d.p));
  results.forEach((d, i) => { d.q = q[i]; });
  const m = results.length;
  const p05 = results.filter((d) => d.p < 0.05).length;
  const q05 = results.filter((d) => d.q < 0.05).length;
  const sortBy = p.sort || "abs";
  results.sort(sortBy === "q" ? (a, b) => a.q - b.q || Math.abs(b.r) - Math.abs(a.r) : (a, b) => Math.abs(b.r) - Math.abs(a.r));

  const shown = +p.more ? results.length : Math.min(100, results.length);
  const summary = el("div.card.mt",
    el("h3", `${nfmt(m)} measures tested against “${short(T, 70)}”`),
    el("div.grid.g4.mt",
      stat("Tests", nfmt(m), "measures with enough overlap"),
      stat(el("span", "p < 0.05", tip("p_value")), nfmt(p05), `${fmt((p05 / Math.max(m, 1)) * 100, 2)}% of the tests`),
      stat(el("span", "Expected by chance", tip("multiple_comparisons")), nfmt(Math.round(0.05 * m)), "if nothing at all were related"),
      stat(el("span", "q < 0.05", tip("fdr")), nfmt(q05), "after Benjamini-Hochberg")),
    el("div.mt", checkList([
      { level: "warn", body: [el("b", "A search, not a test. "), "Ranking many correlations and reading off the top is the classic way to find patterns that aren't there (", term("multiple_comparisons", "multiple comparisons"), "). A lead found here needs checking on its own, ideally on new data."] },
      ...(mode === "time" && tf === "level" ? [{ level: "serious", body: [el("b", "Levels of trending series. "), "Most of these series trend, so the top of the list in levels is mostly ", term("spurious", "shared trends"), ". Compare the 'r of changes' column, or switch to year-on-year change."] }] : []),
      ...(skippedBuilt ? [{ level: "info", body: [`${skippedBuilt} measure${skippedBuilt === 1 ? " was" : "s were"} left out as built from or into the target (`, term("part_whole", "part and whole"), ")."] }] : []),
      { level: "info", body: ["Many of these measures move together (shared trends, sources, components), so the tests are not independent and the correction is approximate (", term("fdr", "false discovery rate"), ")."] },
    ])));
  root.append(summary);

  const hist = chartCard({
    title: "How the correlations are spread", tip: tip("correlation"), height: "xshort",
    sub: "Every test's correlation, in bins of 0.1. With no real associations most would sit near 0.",
    render: (box) => {
      const bins = Array.from({ length: 20 }, (_, i) => ({ lo: -1 + i * 0.1, n: 0, sig: 0 }));
      for (const d of results) {
        const b = bins[Math.min(19, Math.floor((d.r + 1) / 0.1))];
        b.n++;
        if (d.q < 0.05) b.sig++;
      }
      chart(box, () => {
        const t = tokens();
        return {
          grid: { left: 44, right: 12, top: 10, bottom: 26 },
          xAxis: axis("category", { data: bins.map((b) => r2d(b.lo + 0.05)), axisLabel: { color: t.muted, interval: 3 } }),
          yAxis: axis("value", { minInterval: 1 }),
          tooltip: { trigger: "axis", axisPointer: { type: "shadow" }, formatter: (ps) => { const b = bins[ps[0].dataIndex]; return tipHtml(`r from ${r2d(b.lo)} to ${r2d(b.lo + 0.1)}`, [[t.s1, "measures", String(b.n)], [null, "of them q < 0.05", String(b.sig)]]); } },
          series: [{ type: "bar", data: bins.map((b) => b.n), barCategoryGap: "8%", itemStyle: { color: t.s1, borderRadius: [4, 4, 0, 0] } }],
        };
      });
    },
  });

  const cols = [
    { label: "#", n: true, value: (d) => results.indexOf(d) + 1 },
    { label: "Measure", node: (d) => el("div", el("div", d.V.name), el("div.small.muted", SOURCES[d.V.source] || d.V.source, " · ", lenses[d.V.lens]?.short ?? d.V.lens, " · ", d.V.topic)) },
    { head: el("span", "n", tip("n")), label: "n", n: true, value: (d) => d.n },
    { head: el("span", control ? "partial r" : method === "spearman" ? "ρ" : "r", tip(control ? "partial" : method)), label: "r", n: true, node: (d) => rcell(d.r) },
    ...(mode === "time" && tf === "level" ? [{ head: el("span", "r of changes", tip("diff")), label: "r of changes", n: true, node: (d) => (d.rDiff == null ? "–" : rcell(d.rDiff)) }] : []),
    { head: el("span", "p", tip("p_value")), label: "p", n: true, node: (d) => num("p_value", d.p, pval(d.p)) },
    { head: el("span", "q", tip("q_value")), label: "q", n: true, node: (d) => num("q_value", d.q, pval(d.q)) },
  ];
  const table = el("div.card.mt",
    el("div.card-head", el("div", el("h3", "The measures, strongest first"), el("p.card-sub", "Click a row to compare it with the target.")),
      el("div.row",
        seg([["abs", "Sort by |r|"], ["q", "Sort by q"]], sortBy, (v) => set({ sort: v === "abs" ? undefined : v })),
        el("button.btn.small", { type: "button", onclick: () => download(`correlates-${T.id}.csv`.replace(/[^\w.-]+/g, "_"), toCsv(results, [
          { label: "id", value: (d) => d.V.id }, { label: "name", value: (d) => d.V.name }, { label: "source", value: (d) => d.V.source },
          { label: "lens", value: (d) => d.V.lens }, { label: "n", value: (d) => d.n }, { label: "r", value: (d) => d.r },
          { label: "r_of_changes", value: (d) => d.rDiff }, { label: "p", value: (d) => d.p }, { label: "q_bh", value: (d) => d.q }])) }, "Download all (CSV)"))),
    el("div.table-wrap", dataTable(results.slice(0, shown), cols, {
      onRow: (d) => go("compare", { m: mode, x: T.id, y: d.V.id, t: mode === "time" && tf !== "level" ? tf : undefined, tx: p.tx, g: group !== "all" ? group : undefined, c: p.c, tc: p.c ? "log" : undefined }),
    })),
    shown < results.length ? el("button.btn.mt", { type: "button", onclick: () => set({ more: "1" }) }, `Show all ${nfmt(results.length)}`) : null);
  root.append(hist, table);
  if (control) root.append(el("p.small.muted.mt", `Partial correlations holding ${short(control, 60)} fixed (log scale).`));
}

function stat(label, value, sub) {
  return el("div.tile", el("div.lab", label), el("div.val", value), el("div.sub", sub));
}

function rcell(r) {
  const bar = el("span.rbar", el("i", { style: { left: r >= 0 ? "50%" : `${50 + r * 50}%`, width: `${Math.abs(r) * 50}%`, background: r >= 0 ? "var(--div-pos)" : "var(--div-neg)" } }));
  return el("span.bar-cell", bar, num("pearson", r, r2d(r)));
}
