// The GII breakdown page: Australia's Global Innovation Index 2026 from WIPO's data file (data/processed/
// gii-australia.json), from the headline down to each of the 79 indicators.

import { axis, chart, chartCard, dataTable, legend, tipHtml, tokens } from "./charts.js";
import { giiPage } from "./data.js";
import { initPopover, term, tip } from "./glossary.js";
import { el, fmt, initTheme, ordinal } from "./util.js";

const BASE = "assets/data/"; // a frozen copy of the retired build's output, until the page is rebuilt on the corpus
const root = document.getElementById("main");


async function render() {
  const g = await giiPage(BASE);
  const by = new Map(g.nodes.map((nd) => [nd.num, nd]));
  const top = by.get(""), inp = by.get("IN"), out = by.get("OUT");
  const pillars = g.nodes.filter((nd) => nd.level === "Pillar");
  const indicators = g.nodes.filter((nd) => nd.level === "Indicator" && nd.au.rank != null);

  root.append(
    el("section.hero",
      el("div",
        el("p.eyebrow", `Global Innovation Index ${g.edition}`),
        el("h1", `Australia ranks ${ordinal(top.au.rank)} of ${g.economies} economies`),
        el("p.lede", "WIPO's ", term("gii", "Global Innovation Index"), " scores economies on 79 indicators in seven ", term("pillar", "pillars"), ". Australia does much better on ",
          term("inputs_outputs", "inputs"), ` (${ordinal(inp.au.rank)}) than on outputs (${ordinal(out.au.rank)}): it has the ingredients of innovation in greater measure than its measured results. This page breaks the score down.`)),
      el("div.tiles",
        tile("GII score", top, "the simple average of inputs and outputs"),
        tile("Innovation inputs", inp, "five pillars"),
        tile("Innovation outputs", out, "two pillars"))));

  // ---------------------------------------------------------------------------------------- pillars
  root.append(el("div.grid.g2.mt2",
    chartCard({
      title: "The seven pillars", tip: tip("pillar"), height: "tall",
      sub: "Australia's score on each pillar (0-100) against the median of high-income economies and the top scorer. Hover for ranks.",
      legend: legend([["dot", "var(--s2)", "Australia"], ["dot", "var(--s-muted)", "High-income median"], ["dot", "var(--ink)", "Top economy"]]),
      render: (box) => pillarChart(box, pillars),
      table: () => dataTable(pillars, [
        { label: "Pillar", value: (d) => `${d.num} ${d.name}` }, { label: "Australia", n: true, value: (d) => fmt(d.au.score, 3) },
        { label: "Rank", n: true, value: (d) => d.au.rank }, { label: "High-income median", n: true, value: (d) => fmt(d.median_high_income, 3) },
        { label: "Top", value: (d) => `${d.best.name} (${fmt(d.best.score, 3)})` }]),
    }),
    chartCard({
      title: `All ${g.economies} economies`, tip: tip("normalised_score"), height: "tall",
      sub: "Every economy's GII score, highest first. Australia in orange. Hover a bar for the economy.",
      render: (box) => leagueChart(box, g.league),
      table: () => dataTable(g.league, [{ label: "Rank", n: true, value: (d) => d.rank }, { label: "Economy", value: (d) => d.name },
        { label: "Score", n: true, value: (d) => fmt(d.score, 3) }, { label: "Income group", value: (d) => d.income }], { rowClass: (d) => (d.iso3 === "AUS" ? "au" : null) }),
    })));

  // ---------------------------------------------------------------------------------------- strengths and weaknesses
  const sw = (flag) => indicators.filter((nd) => nd.au.sw_overall === flag).sort((a, b) => (flag === "S" ? a.au.rank - b.au.rank : b.au.rank - a.au.rank));
  const swList = (flag, title, sub) => el("div.card",
    el("h3", title, tip("strength")), el("p.card-sub", sub),
    dataTable(sw(flag), [
      { label: "Indicator", node: (d) => `${d.num.replace(/^(IN|OUT)\./, "")} ${d.name}` },
      { label: "Rank", n: true, value: (d) => ordinal(d.au.rank) },
      { label: "Value", n: true, value: (d) => (d.au.value != null ? fmt(d.au.value, 3) : "–") }]));
  root.append(el("div.grid.g2.mt2",
    swList("S", "Australia's strengths", "Indicators WIPO marks as strengths: among Australia's best ranks. Click one to see it against GDP per capita across economies."),
    swList("W", "Australia's weaknesses", "Indicators WIPO marks as weaknesses: among Australia's worst ranks. Click one to see it against GDP per capita across economies.")));

  // ---------------------------------------------------------------------------------------- the tree
  const tree = el("div.tree");
  tree.append(el("div.tree-head", el("span", "Pillar, sub-pillar, indicator"), el("span.n", "Score"), el("span.n", "Rank"), el("span.bar-col", "Score against the high-income median")));
  for (const p of pillars) tree.append(node(p, g.nodes, by));
  root.append(el("div.card.mt2",
    el("div.card-head", el("div", el("h2", "The full breakdown"),
      el("p.card-sub", "Open a pillar for its sub-pillars, and a sub-pillar for its indicators. Each indicator shows Australia's value, its data year, and WIPO's definition and source. The tick on each bar is the high-income median.")),
    el("div.row", el("button.btn.small", { type: "button", onclick: () => tree.querySelectorAll("details").forEach((d) => (d.open = true)) }, "Open all"),
      el("button.btn.small", { type: "button", onclick: () => tree.querySelectorAll("details").forEach((d) => (d.open = false)) }, "Close all"))),
    tree));

  // ---------------------------------------------------------------------------------------- the research goal and context
  root.append(el("div.mt2",
    el("div.card",
      el("h2", "Why this page exists"),
      el("p", "IP Australia's research programme asks: ", el("em", "where, how and for whom can IP Australia's interventions generate the greatest additional public value, and what evidence would justify acting on those opportunities?")),
      el("p.ink2", "Its framework separates five concepts: ", term("potential", "innovation potential"), ", ", term("activity", "innovation activity"), ", ", term("ip", "IP protection and use"), ", ",
        term("outcomes", "private and organisational outcomes"), " and ", term("public_value", "public value"), ", and treats the links between them as empirical questions."),
      el("p.ink2", "A ranking like the GII is a starting point. Its pillars are averages of very different things, and its scores are relative to other economies. Use it to find where to look, then look underneath."),
      el("p", el("a", { href: "https://github.com/Thomas-Amann-IPAustralia/Aus-GII-Breakdown/blob/main/docs/research-goal.md" }, "Read the research goal →")))));
}

function tile(label, nd, sub) {
  return el("div.tile", el("div.lab", label), el("div.val", fmt(nd.au.score, 3)),
    el("div.sub", el("strong", `${ordinal(nd.au.rank)}`), ` of ${nd.n_scored} · ${sub}`));
}

function node(nd, nodes, by) {
  const kids = nodes.filter((k) => k.num.startsWith(`${nd.num}.`) && k.num.split(".").length === nd.num.split(".").length + 1);
  const isLeaf = nd.level === "Indicator";
  const pct = nd.au.score != null ? Math.max(0, Math.min(100, nd.au.score)) : null;
  const bar = el("span.scorebar.bar-col", pct != null ? el("span.s", { style: { width: `${pct}%` } }) : null,
    nd.median_high_income != null ? el("span.m", { style: { left: `${nd.median_high_income}%` }, title: `High-income median ${fmt(nd.median_high_income, 3)}` }) : null);
  const flags = [
    nd.au.sw_overall ? el(`span.sw.${nd.au.sw_overall}`, { "data-term": "strength", tabindex: 0 }, nd.au.sw_overall === "S" ? "Strength" : "Weakness") : null,
    nd.au.outdated ? el("span.flagtxt", { "data-term": "outdated", tabindex: 0 }, "outdated") : null,
    nd.au.dmc ? el("span.flagtxt", { "data-term": "dmc", tabindex: 0 }, "low coverage") : null,
  ];
  const summary = el("summary",
    el("span.nm", el("span", `${nd.num.replace(/^(IN|OUT)\./, "")} ${nd.name}`), ...flags),
    el("span.n.num", nd.au.score != null ? fmt(nd.au.score, 3) : "n/a"),
    el("span.n.num", nd.au.rank != null ? ordinal(nd.au.rank) : "–"),
    bar);
  const d = el(`details.lvl-${nd.level}${isLeaf ? ".leaf" : ""}`, summary);
  const desc = el("div.desc");
  if (isLeaf) {
    desc.append(
      el("p", nd.description || ""),
      el("p",
        nd.au.value != null && nd.profile === "Value" ? [el("strong", "Australia's value: "), `${fmt(nd.au.value, 4)}`, nd.au.year ? ` (data year ${nd.au.year})` : "", ". "] : nd.au.score == null ? "No value for Australia. " : "",
        `${nd.n_scored} economies scored; the top is ${nd.best?.name} (${fmt(nd.best?.score, 3)}).`,
        nd.bad ? [" ", el("span.flagtxt", { "data-term": "bad", tabindex: 0 }, "higher is worse")] : "",
        nd.half_weight ? " Half weight in its sub-pillar." : ""),
      el("p.small.muted", nd.type ? `${nd.type === "Data" ? "Hard data" : nd.type === "Index" ? "A composite indicator" : "A survey question"}. ` : "", nd.source ? `Source: ${nd.source}.` : ""));
  } else {
    desc.append(el("p", nd.description || ""),
      el("p.small.row", el("span.muted", `High-income median ${fmt(nd.median_high_income, 3)} · top ${nd.best?.name} ${fmt(nd.best?.score, 3)}`)));
  }
  d.append(desc);
  if (kids.length) d.append(el("div.kids", kids.map((k) => node(k, nodes, by))));
  return d;
}

function pillarChart(box, pillars) {
  const cats = pillars.map((p) => `${p.num.replace(/^(IN|OUT)\./, "")}. ${p.name}`);
  chart(box, () => {
    const t = tokens();
    const ser = (name, vals, colour, size, symbol = "circle") => ({ type: "scatter", name, data: vals.map((v, i) => [v, i]), symbol, symbolSize: size, itemStyle: { color: colour, borderColor: t.surface, borderWidth: 1.5 }, z: size });
    return {
      grid: { left: 210, right: 24, top: 10, bottom: 40 },
      xAxis: axis("value", { min: 0, max: 100, name: "score, 0-100", nameLocation: "middle", nameGap: 24 }),
      yAxis: axis("category", { data: cats, inverse: true, axisLabel: { color: t.ink2, width: 200, overflow: "truncate" }, splitLine: { show: true, lineStyle: { color: t.grid } } }),
      tooltip: {
        trigger: "axis", axisPointer: { type: "shadow" },
        formatter: (ps) => {
          const p = pillars[ps[0].dataIndex];
          return tipHtml(`${p.num} ${p.name}`, [[t.s2, "Australia", `${fmt(p.au.score, 3)} (${ordinal(p.au.rank)})`], [t.sMuted, "High-income median", fmt(p.median_high_income, 3)], [t.ink, `Top: ${p.best.name}`, fmt(p.best.score, 3)]]);
        },
      },
      series: [
        { type: "custom", silent: true, renderItem: (params, api) => {
          const a = api.coord([api.value(0), api.value(2)]), b = api.coord([api.value(1), api.value(2)]);
          return { type: "line", shape: { x1: a[0], y1: a[1], x2: b[0], y2: b[1] }, style: { stroke: t.axis, lineWidth: 2 } };
        }, data: pillars.map((p, i) => [Math.min(p.au.score, p.median_high_income), p.best.score, i]), encode: { x: [0, 1], y: 2 } },
        ser("High-income median", pillars.map((p) => p.median_high_income), t.sMuted, 11, "diamond"),
        ser("Top economy", pillars.map((p) => p.best.score), t.ink, 9),
        ser("Australia", pillars.map((p) => p.au.score), t.s2, 14),
      ],
    };
  });
}

function leagueChart(box, league) {
  chart(box, () => {
    const t = tokens();
    return {
      grid: { left: 40, right: 12, top: 10, bottom: 30 },
      xAxis: axis("category", { data: league.map((d) => d.name), axisLabel: { show: false } }),
      yAxis: axis("value", { min: 0, name: "GII score", nameLocation: "middle", nameGap: 28 }),
      tooltip: { trigger: "axis", axisPointer: { type: "shadow" }, formatter: (ps) => { const d = league[ps[0].dataIndex]; return tipHtml(d.name, [[d.iso3 === "AUS" ? t.s2 : t.sMuted, "GII score", fmt(d.score, 3)], [null, "Rank", ordinal(d.rank)]], d.income); } },
      series: [{
        type: "bar", barCategoryGap: "12%",
        data: league.map((d) => ({ value: d.score, itemStyle: { color: d.iso3 === "AUS" ? t.s2 : t.sMuted, borderRadius: [2, 2, 0, 0] } })),
        markPoint: { symbol: "pin", symbolSize: 0, data: [{ coord: [league.findIndex((d) => d.iso3 === "AUS"), league.find((d) => d.iso3 === "AUS").score], value: "Australia" }],
          label: { show: true, formatter: "Australia", position: "top", color: t.ink, fontWeight: 700, distance: 6 } },
      }],
    };
  });
}

initTheme(document.getElementById("theme"));
initPopover(null);
render().catch((e) => {
  root.append(el("div.notice", `Could not load the data (${e.message}). If you opened this file from disk, serve the folder instead: python3 -m http.server, then open http://localhost:8000/.`));
  throw e;
});
