// What the explorer's views share: lining measures up (by year or by economy), the transforms, the starter
// questions tied to the research goal, and the automatic checks that go with every correlation.

import { construction, wholes } from "../data.js";
import { term } from "../glossary.js";
import { el, fmt, r2d, svg } from "../util.js";
import * as S from "../stats.js";

export const TIME_TRANSFORMS = [
  ["level", "Levels"],
  ["diff", "Year-on-year change"],
  ["pct", "% change"],
  ["detrend", "Detrended"],
  ["log", "Log"],
];
export const TIME_TERMS = { level: null, diff: "diff", pct: "pct", detrend: "detrend", log: "log" };
export const ECON_TRANSFORMS = [["level", "As published"], ["log", "Log scale"]];
export const GROUPS = [
  ["all", "Every economy"],
  ["gii", "GII economies"],
  ["HI", "High income"],
  ["UM", "Upper-middle income"],
  ["LM", "Lower-middle income"],
  ["LI", "Low income"],
];
export const INCOME_ORDER = ["LI", "LM", "UM", "HI"];
export const INCOME_NAMES = { LI: "Low income", LM: "Lower-middle income", UM: "Upper-middle income", HI: "High income" };

/** A short name for charts: the source's own name without our "(source)" suffix, cut to `max` characters. */
export function short(v, max = 60) {
  const s = v.name.replace(/ \((WHR|HDR|CtG|OECD How's Life|GII economy data)\)$/, "");
  return s.length > max ? `${s.slice(0, max - 1)}…` : s;
}

// ------------------------------------------------------------------------------------------- lining up

/**
 * Pairs of a time comparison: each X year with Y `lag` years later, after the transform, inside [from, to] (X's
 * years). Returns the years, the paired values, and the full transformed series (for the autocorrelations).
 */
export function alignTime(X, Y, { tf = "level", lag = 0, from = -Infinity, to = Infinity } = {}) {
  const xs = S.transform(X.series, tf), ys = S.transform(Y.series, tf);
  const years = [...xs.keys()].filter((y) => y >= from && y <= to && ys.has(y + lag)).sort((a, b) => a - b);
  const x = years.map((y) => xs.get(y)), y = years.map((t) => ys.get(t + lag));
  return { years, x, y, xs, ys };
}

/** A transformed yearly series over a span of consecutive years, with nulls for gaps (for acf1). */
export function span(series, years) {
  if (!years.length) return [];
  const out = [];
  for (let t = years[0]; t <= years[years.length - 1]; t++) out.push(series.has(t) ? series.get(t) : null);
  return out;
}

export function inGroup(e, group) {
  if (group === "all" || !group) return true;
  if (group === "gii") return e.in_gii;
  return e.income_code === group;
}

export function econValues(v, tf) {
  return v.values.map((x) => (x == null ? null : tf === "log" ? (x > 0 ? Math.log(x) : null) : x));
}

/** Pairs of an economy comparison: indices into ds.economies with both values (after transforms) in the group. */
export function alignEcon(ds, X, Y, { tx = "level", ty = "level", group = "all", Z = null, tz = "level" } = {}) {
  const xv = econValues(X, tx), yv = econValues(Y, ty), zv = Z ? econValues(Z, tz) : null;
  const idx = [];
  for (let i = 0; i < ds.economies.length; i++) {
    if (!inGroup(ds.economies[i], group)) continue;
    if (xv[i] == null || yv[i] == null || (zv && zv[i] == null)) continue;
    idx.push(i);
  }
  return { idx, x: idx.map((i) => xv[i]), y: idx.map((i) => yv[i]), z: zv ? idx.map((i) => zv[i]) : null, xv, yv, zv };
}

// ------------------------------------------------------------------------------------------- starters

/** Starter questions: each a link into the explorer, tied to the research goal's questions (docs/research-goal.md). */
export const STARTERS = [
  { m: "time", x: "wdi:GB.XPD.RSDV.GD.ZS", y: "wdi:IP.PAT.RESD", rq: "Q3", q: "Do resident patent filings track R&D spending?",
    why: "Complementary capabilities: does more research go with more patenting by Australians? Few years, so read the interval." },
  { m: "time", x: "wdi:NY.GDP.PCAP.KD", y: "whr:life-evaluation", rq: "Q1", q: "Income and life satisfaction over time",
    why: "Real GDP per person rose while life evaluations fell. A lesson in why levels mislead: compare the year-on-year changes." },
  { m: "time", x: "wdi:IP.PAT.NRES", y: "wdi:IP.PAT.RESD", rq: "Q2", q: "Foreign and Australian patent filings",
    why: "Who uses the system? Non-residents file most Australian patents. Do the two move together year to year?" },
  { m: "time", x: "wdi:BM.GSR.ROYL.CD", y: "wdi:BX.GSR.ROYL.CD", t: "pct", rq: "Q1", q: "IP payments and receipts",
    why: "Charges for the use of IP paid abroad against those received, as % change: is Australia's IP trade balance shifting?" },
  { m: "time", x: "wdi:IP.TMK.RSCT", y: "wdi:IC.BUS.NREG", t: "diff", rq: "Q3", q: "Trade mark filings and new businesses",
    why: "Do years with more new businesses also see more trade mark applications by residents? Year-on-year changes." },
  { m: "economy", x: "gii:score:IN", y: "gii:score:OUT", rq: "Q4", q: "Innovation inputs against outputs",
    why: "Australia ranks higher on inputs than outputs. Where does it sit against economies with similar inputs? (Its residual.)" },
  { m: "economy", x: "gii:score:GII", y: "whr:life-evaluation", c: "gii:economy:PPPPC", tc: "log", rq: "Q1", q: "Innovation and well-being, beyond income",
    why: "The GII and life evaluations go together across economies, but so does income with both. What is left once income is held fixed?" },
  { m: "economy", x: "gii:economy:PPPPC", tx: "log", y: "gii:value:OUT.6.1.1", ty: "log", rq: "Q1", q: "Patenting and prosperity",
    why: "Patents by origin per PPP$ GDP against GDP per capita, both on log scales. Is patenting a rich-economy activity?" },
  { m: "economy", x: "hdr:gini", y: "gii:score:GII", rq: "Q2", q: "Inequality and innovation",
    why: "Distribution: do more unequal economies innovate less, or is income doing the work? Try controlling for GDP per capita." },
  { m: "economy", x: "gii:value:IN.5.1.2", y: "hdr:gii", rq: "Q2", q: "Women in knowledge work and gender inequality",
    why: "Females employed with advanced degrees (GII) against UNDP's Gender Inequality Index (higher is more unequal)." },
];

export const MATRIX_PRESETS = {
  time: [
    { name: "IP, research and the economy", ids: ["wdi:IP.PAT.RESD", "wdi:IP.PAT.NRES", "wdi:IP.TMK.RSCT", "wdi:IP.IDS.RSCT", "wdi:GB.XPD.RSDV.GD.ZS", "wdi:IP.JRN.ARTC.SC", "wdi:BX.GSR.ROYL.CD", "wdi:NY.GDP.PCAP.KD"] },
    { name: "Well-being and prosperity", ids: ["whr:life-evaluation", "wdi:NY.GDP.PCAP.KD", "hdr:hdi", "hdr:le", "oecd:employment-rate", "oecd:housing-affordability", "wdi:SL.UEM.TOTL.ZS"] },
  ],
  economy: [
    { name: "The GII's seven pillars", ids: ["gii:score:IN.1", "gii:score:IN.2", "gii:score:IN.3", "gii:score:IN.4", "gii:score:IN.5", "gii:score:OUT.6", "gii:score:OUT.7"] },
    { name: "One measure per framework concept", ids: ["gii:score:IN.2", "gii:score:OUT.6.1", "gii:value:OUT.6.1.1", "gii:score:OUT.6.2", "whr:life-evaluation", "hdr:hdi", "gii:economy:PPPPC"] },
    { name: "Innovation and distribution", ids: ["gii:score:GII", "hdr:gini", "hdr:gii", "hdr:ineq_inc", "hdr:share_richest10", "gii:economy:PPPPC"] },
  ],
};

// ------------------------------------------------------------------------------------------- checks

const ICONS = {
  serious: '<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M8 1.5 15 14H1z" fill="currentColor" opacity=".18"/><path d="M8 6v3.5M8 11.8v.1" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>',
  warn: '<svg viewBox="0 0 16 16" aria-hidden="true"><circle cx="8" cy="8" r="7" fill="currentColor" opacity=".16"/><path d="M8 4.5v4.2M8 11.3v.1" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>',
  info: '<svg viewBox="0 0 16 16" aria-hidden="true"><circle cx="8" cy="8" r="7" fill="currentColor" opacity=".14"/><path d="M8 7.2v4.3M8 4.6v.1" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>',
  ok: '<svg viewBox="0 0 16 16" aria-hidden="true"><circle cx="8" cy="8" r="7" fill="currentColor" opacity=".15"/><path d="M4.5 8.3l2.2 2.2 4.8-5" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>',
};
const LEVEL_WORD = { serious: "Serious", warn: "Check", info: "Note", ok: "OK" };

export function checkList(items) {
  const order = { serious: 0, warn: 1, info: 2, ok: 3 };
  return el("ul.checks", items.sort((a, b) => order[a.level] - order[b.level]).map((c) =>
    el("li", el(`span.${c.level}`, { title: LEVEL_WORD[c.level] }, svg(ICONS[c.level])), el("div", el("span.sr-only", `${LEVEL_WORD[c.level]}: `), c.body))));
}

/**
 * The checks every comparison runs. `ctx`: {ds, X, Y, x, y, labels (a name per point), r, rho, n, mode, tf,
 * tx, ty, lag, extra: [...]} where `extra` holds the mode's own findings.
 */
export function runChecks(ctx) {
  const { ds, X, Y, x, y, labels, n, mode } = ctx;
  const out = [];
  const add = (level, ...body) => out.push({ level, body });
  const r = S.pearsonR(x, y);
  const rho = n >= 3 ? S.pearsonR(S.ranks(x), S.ranks(y)) : NaN;

  if (n < 8) add("serious", el("b", `Only ${n} pairs. `), "With this few points a correlation can swing anywhere from one point to the next; the ", term("ci", "confidence interval"), " shows how little is pinned down.");
  else if (n < 20) add("warn", el("b", `${n} pairs. `), "A modest number: read the interval, not just r. ", term("power", "Power"), " to detect a moderate association is low.");

  const how = construction(ds, X.id, Y.id);
  if (how === "siblings") {
    add("info", el("b", "Two parts of one index. "), "Both feed the same composite index. That does not tie them together mechanically unless they share ingredients, but the index's designers chose them to belong together (", term("part_whole", "part and whole"), ").");
  } else if (how) {
    const [part, whole] = how === "a-in-b" ? [X, Y] : how === "b-in-a" ? [Y, X] : [null, null];
    add("serious", el("b", "Built from each other. "), [`"${short(part, 50)}" is one of the ingredients of "${short(whole, 50)}", so they correlate partly by construction (`, term("part_whole", "part and whole"), ")."]);
  }

  if (Number.isFinite(r) && Number.isFinite(rho) && Math.abs(r - rho) > 0.2) {
    add("warn", el("b", "Pearson and Spearman disagree "), `(r ${r2d(r)}, ρ ${r2d(rho)}). `,
      Math.abs(rho) > Math.abs(r) ? "The order is more consistent than the straight line: the pattern may be curved, or an outlier pulls r down." : "A few extreme points may be making the straight-line correlation; the ranks show a weaker pattern.",
      " Look at the scatter.");
  }

  if (n >= 6) {
    const d = S.cooks(x, y);
    let k = 0;
    d.forEach((v, i) => { if (v > d[k]) k = i; });
    if (d[k] > Math.max(4 / n, 0.5)) {
      const keep = x.map((_, i) => i).filter((i) => i !== k);
      const r2 = S.pearsonR(keep.map((i) => x[i]), keep.map((i) => y[i]));
      if (Math.abs(r2 - r) > 0.1) add("warn", el("b", `One point carries a lot of weight: ${labels[k]}. `), "Without it r would be ", el("b", r2d(r2)), ` instead of ${r2d(r)} (`, term("cooks", "Cook's distance"), ` ${fmt(d[k], 2)}).`);
    }
  }

  for (const [V, vals, t] of [[X, x, ctx.tx ?? ctx.tf], [Y, y, ctx.ty ?? ctx.tf]]) {
    if (t !== "level" || vals.length < 8 || vals.some((v) => v <= 0)) continue;
    const sk = S.skew(vals);
    if (sk > 1.5) add("info", el("b", `"${short(V, 45)}" is strongly skewed `), "(", term("skewness", `skewness ${fmt(sk, 2)}`, sk), "): a few large values dominate. Try a log scale.");
  }

  if (Math.abs(r) > 0.97 && !how) add("info", el("b", "Nearly identical. "), "A correlation this close to ±1 usually means the two measure the same thing (perhaps from two publishers) or are linked by definition.");

  for (const V of [X, Y]) {
    if (V.kind === "rank") add("info", `"${short(V, 45)}" is a `, term("rank", "rank"), ": prefer Spearman's ρ.");
    if (V.note && /worse/.test(V.note)) add("info", `"${short(V, 45)}": `, term("bad", "higher is worse"), ". Read a positive correlation with it as a negative one with performance.");
  }

  out.push(...(ctx.extra || []));
  add("info", el("b", "Exploratory association only. "), mode === "time"
    ? ["Two Australian series moving together says nothing on its own about cause, direction or ", term("additionality"), ". See ", term("causation", "correlation is not causation"), "."]
    : ["A pattern across economies need not hold within them (the ", term("ecological_fallacy", "ecological fallacy"), "), and income and history ", term("confounder", "confound"), " most cross-country comparisons."]);
  return out;
}

/** The plain-English strength of a correlation. */
export function strength(r) {
  const a = Math.abs(r);
  if (!Number.isFinite(a)) return "no measurable";
  return a >= 0.9 ? "very strong" : a >= 0.7 ? "strong" : a >= 0.5 ? "moderate" : a >= 0.3 ? "weak" : a >= 0.1 ? "very weak" : "next to no";
}
export function direction(r) {
  return r > 0 ? "positive" : r < 0 ? "negative" : "";
}

export function wholesOf(ds, id) {
  return wholes(ds, id);
}
