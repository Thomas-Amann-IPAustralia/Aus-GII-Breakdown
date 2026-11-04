// An observation's page as one Markdown document, for the "Copy as Markdown" and "Download .md" buttons: everything
// the page says, in the page's order, so the copy stands on its own. The statement, points and key figures; the
// chart's numbers as a table (every view, always: a copy cannot carry the chart, so it carries the table instead);
// the four steps of the evidence trail with each source's publisher, licence, date copied, tables and fingerprints;
// the assumptions, limits and next step; the explainers for every term used; and the notebook's own words.
// Nothing here touches the document, so the tests can run it under Node (tests/test_atlas.py).

import { chartTable, viewSpec } from "./tables.js";

const STAGE_NAME = { 1: "each variable on its own", 2: "pairs of variables", 3: "many variables together" };
const INTRO = {
  1: "Stage 1 answers none of the five questions. This is how the observation prepares the ground for them.",
  2: "Stage 2 answers none of the five questions either: it finds which measures go together. This is how the association prepares the ground for them.",
  3: "Stage 3 answers none of the five questions either: it tests which of Stage 2's signals survive with their other factors held together. This is how the result prepares the ground for them.",
};
export const TOKEN = /\[\[([^\]|]+)(?:\|([^\]]+))?\]\]|\{([UBM]\d+)\}/g;

const plural = (n, word) => `${n} ${word}${n === 1 ? "" : "s"}`;
const lower = (s) => String(s ?? "").replace(/^[A-Z](?![A-Z])/, (c) => c.toLowerCase());
const nfmt = new Intl.NumberFormat("en-AU");
function bytes(b) {
  return b >= 1e9 ? `${(b / 1e9).toFixed(1)} GB` : b >= 1e6 ? `${(b / 1e6).toFixed(1)} MB` : `${Math.max(1, Math.round(b / 1e3))} kB`;
}
function longDate(iso) {
  const d = new Date(`${iso}T00:00:00Z`);
  return Number.isNaN(d.getTime()) ? String(iso) : d.toLocaleDateString("en-AU", { day: "numeric", month: "long", year: "numeric", timeZone: "UTC" });
}

/**
 * The Markdown for observation `o`.
 * - `atlas`: the whole of atlas.json (glossary, lenses, questions, sources, observations);
 * - `chart`: the chart's spec when the observation has one (fetched by the page from data/charts/<id>.json);
 * - `base`: the page's address without its #fragment, so that links to other observations and images resolve.
 */
/**
 * The site's light markup as Markdown: `[[term|label]]` reads as its words (the term is added to `terms`, so a copy
 * can explain it), and `{U44}` becomes a link to that observation's page. Shared with the chat's passages
 * (analysis/atlas/passages.mjs), so they read exactly as the pages do.
 */
export function markup(A, { base = "", terms = new Set(), byId = null } = {}) {
  const ids = byId || Object.fromEntries(A.observations.map((x) => [x.id, x]));
  return (text) => String(text ?? "").replace(TOKEN, (_, term, label, id) => {
    if (id) return ids[id] ? `[${id}](${base}#/${id})` : id;
    terms.add(term);
    return label || lower(A.glossary[term]?.title) || term;
  });
}

export function observationMarkdown(o, { atlas: A, chart = null, base = "" }) {
  const byId = Object.fromEntries(A.observations.map((x) => [x.id, x]));
  const L = A.lenses[o.lens] || { name: o.lens, unit: "" };
  const page = (id) => `${base}#/${id}`;
  const terms = new Set(o.terms || []);
  const md = markup(A, { base, terms, byId });
  const cell = (text) => md(text).replace(/\s*\n\s*/g, " ").replace(/\|/g, "\\|");
  /** A Markdown table; `right` names the columns of numbers (all but the first, unless given). */
  const table = (head, rows, right = head.map((_, i) => i > 0)) => [
    `| ${head.map(cell).join(" | ")} |`,
    `| ${head.map((_, i) => (right[i] ? "---:" : "---")).join(" | ")} |`,
    ...rows.map((r) => `| ${r.map(cell).join(" | ")} |`),
  ].join("\n");
  const abs = (src) => { try { return new URL(src, base || undefined).href; } catch { return src; } };
  const section = o.section.replace(/`/g, "");
  const out = [];
  const add = (...parts) => out.push(...parts.filter((p) => p != null && p !== ""));

  // the head
  add(`# ${o.id}: ${md(o.headline)}`,
    [`- **Lens:** ${L.name}${L.unit ? ` (${L.unit})` : ""}`,
      `- **Stage:** ${o.stage} of 3 (${STAGE_NAME[o.stage]}), section ${section}`,
      `- **Strength of evidence:** ${o.strength}. ${o.strength === "descriptive" ? "Descriptive: what the data show, not why." : "Observational: measures go together; other explanations remain, and it is not a cause."} Causal claims need designs that come after Stage 3.`,
      `- **About:** ${o.about === "data" ? "the data themselves" : "the IP system"}`,
      base ? `- **Page:** ${page(o.id)}` : null,
      `- **Atlas built:** ${A.built}`].filter(Boolean).join("\n"));

  // Stage 3: what it follows from
  if (o.stage === 3) {
    const seen = new Set();
    const from = (o.revisits || []).filter((r) => byId[r.id] && !seen.has(r.id) && seen.add(r.id));
    const earlier = from.some((r) => byId[r.id].stage === 1) && !from.some((r) => byId[r.id].stage === 2) ? "Stage 1 found" : "Stage 2 found";
    add("## How this follows from the earlier stages",
      `**1. ${earlier}**`,
      from.length
        ? from.map((r) => `- [${r.id}](${page(r.id)}): ${md(r.signal || byId[r.id].headline)}`).join("\n")
        : "A question of structure: which measures repeat each other, and whether there are distinct groups.",
      "**2. Stage 3 held together**",
      o.held?.length ? o.held.map((h) => `- ${md(h)}`).join("\n") : "Nothing held: a description of how the measures relate.",
      "**3. What is left**",
      (o.revisits || []).length
        ? o.revisits.map((r) => `- **${r.verdict}** (${r.id}${r.signal ? `, ${md(r.signal)}` : ""}): ${md(r.what)}`).join("\n")
        : "See the observation below.");
  }

  // the observation
  add(`## Observation ${o.id} (${o.strength})`, md(o.statement), o.points?.length ? o.points.map((p) => `- ${md(p)}`).join("\n") : null);
  if (o.later?.length) {
    add("## What Stage 3 found",
      o.later.length === 1 ? "Stage 3 tested this with other factors held together." : `Stage 3 tested this ${o.later.length} ways, with other factors held together.`,
      o.later.map((x) => `- **${x.verdict}**: ${md(x.what)} See [${x.id}](${page(x.id)}): ${md(byId[x.id]?.headline)}`).join("\n"));
  }
  if (o.figures?.length) add("## Key figures", table(["Figure", "What it is"], o.figures.map((f) => [f.value, f.label]), [false, false]));

  // the chart, carried as its table
  if (chart) {
    const views = chart.views?.length ? chart.views.map((_, k) => viewSpec(chart, k)) : [chart];
    add(`## Chart: ${md(chart.title || "")}`.trimEnd(), chart.subtitle ? `_${md(chart.subtitle)}_` : null,
      "The chart's numbers, as a table (the table view of the chart on the page).");
    views.forEach((s, k) => {
      const { head, rows } = chartTable(s);
      if (chart.views?.length) add(`### View ${k + 1} of ${views.length}: ${md(s.label || s.title || "")}`, s.subtitle && s.subtitle !== chart.subtitle ? `_${md(s.subtitle)}_` : null);
      add(table(head, rows));
      const notes = [];
      if (s.type === "effect") notes.push(`Each value is the estimate with its 95% interval in brackets; the line of ${s.ref_label || "no difference"} is at ${s.ref ?? (s.y?.type === "log" ? 1 : 0)}.`);
      if (s.y?.name && s.type !== "effect") notes.push(`Values: ${md(s.y.name)}.`);
      if (s.x?.name && s.type === "effect") notes.push(`Values: ${md(s.x.name)}.`);
      if (s.note && s.note !== chart.note) notes.push(md(s.note));
      if (notes.length) add(notes.join(" "));
    });
    add([chart.source ? `Source: ${md(chart.source).replace(/\.$/, "")}.` : null, chart.note ? md(chart.note) : null,
      o.chart_origin === "quoted" ? "Drawn from the numbers quoted in the observation itself." : "Redrawn from the lens table with the notebook's own query, and checked against every number the observation quotes."]
      .filter(Boolean).join(" "));
  } else if (o.chart) {
    add("## Chart", "The chart's numbers could not be loaded for this copy; they are in the table view of the chart on the page.");
  }
  if (o.verdicts?.length) {
    add("## Signal by signal", "Each comparison as Stage 2 measured it (raw), then with its other factors held together, and the outcome.",
      table(["What was compared", "Raw, then held together", "Outcome"], o.verdicts.map((v) => [v.signal, v.detail || "", v.verdict]), [false, false, false]));
  }

  // the questions
  add("## How this moves the research forward", INTRO[o.stage],
    o.questions.map((q) => {
      const Q = A.questions.find((x) => x.id === q.q);
      return `- **Q${q.q}. ${md(Q?.title)}** ${md(q.how)}`;
    }).join("\n"),
    "_Linking an observation to a question is the analyst's guide to where it may help. It is not a finding._");

  // the trail
  const srcs = o.sources.map((s) => A.sources[s]).filter(Boolean);
  const publishers = [...new Set(srcs.filter((s) => !s.derived).map((s) => s.publisher))];
  add("## Follow the evidence", "From the publisher's file to this observation, in four steps.");
  add(`### Step 1 of 4: Where the data came from (${plural(srcs.length, "source")}${publishers.length ? `, published by ${publishers.join(", ").replace(/, ([^,]*)$/, " and $1")}` : ""})`,
    "Every number here starts in data that a public body published. The project downloads each one as published; nothing is typed in by hand.",
    srcs.map((s) => [
      `- **${s.url ? `[${s.title}](${s.url})` : s.title}** (\`${s.id}\`)`,
      `  - ${s.derived ? `Built by this project, ${s.publisher.replace(/^(built|compiled) here /, "")}.` : `Published by ${s.publisher}.`}${s.coverage ? ` ${s.coverage}.` : ""}`,
      s.licence ? `  - Licence: ${s.licence}` : null,
      s.fetched ? `  - Copied ${longDate(s.fetched)}` : null,
      `  - ${plural(s.tables.length, "processed table")}`,
    ].filter(Boolean).join("\n")).join("\n"));
  const tablesN = srcs.reduce((n, s) => n + s.tables.length, 0);
  const inR2 = srcs.flatMap((s) => s.tables).filter((t) => t.where === "r2").length;
  add(`### Step 2 of 4: How it is kept (${plural(tablesN, "tidy table")} from these sources, ${inR2} of them large enough to live in cloud storage)`,
    md(A.site.storage_text),
    tablesN ? "The tables behind these sources (the fingerprint is the first 12 characters of the file's SHA-256, recorded in `data/manifest.json`):" : null,
    tablesN ? table(["Table", "Rows", "Kept in", "Size", "Fingerprint"], srcs.flatMap((s) => s.tables.map((t) => [
      `\`${s.id}/${t.table}\`${t.describe ? `: ${t.describe}` : ""}`,
      t.rows != null ? nfmt.format(t.rows) : "–",
      t.where === "repo" ? "The repository" : "Cloud storage (R2)",
      bytes(t.bytes),
      `\`${t.sha256}\``])), [false, true, false, true, false]) : null,
    md(`The lens table this observation reads, ${lower(L.name)} (${lower(L.unit)}), is not stored: it is rebuilt from these tables in minutes by the project's build code, so it always matches them.`));
  const prep = o.prep || [];
  add(`### Step 3 of 4: How it was prepared (${plural(prep.length, "step")} for this observation, on the ${lower(L.name)} lens)`,
    "**For this observation**",
    prep.length ? prep.map((p, i) => `${i + 1}. ${md(p.what)}\n   - _Why:_ ${md(p.why)}`).join("\n") : "No preparation of its own.",
    (L.repairs || []).length ? `**Repairs made to the ${lower(L.name)} lens before any observation**` : null,
    (L.repairs || []).length ? L.repairs.map((p, i) => `${i + 1}. ${md(p.what)}\n   - _Why:_ ${md(p.why)}`).join("\n") : null);
  add(`### Step 4 of 4: From the data to the observation (${plural(o.steps.length, "reasoning step")})`,
    "The steps are not findings; only the last is.",
    o.steps.map((s, i) => `${i + 1}. ${md(s)}`).join("\n"),
    `**Which gives observation ${o.id}:** ${md(o.statement)}`);

  // honesty and next
  add("## Assumptions and limits",
    [...o.assumptions.map((a) => `- **Assumption:** ${md(a)}`), ...o.limits.map((a) => `- **Limit:** ${md(a)}`)].join("\n"));
  add("## What happens next", md(o.next),
    o.later?.length ? md(`Stage 3 has since tested this with other factors held: ${o.later.map((x) => `{${x.id}}, ${x.verdict}`).join("; ")}.`) : null);

  // related, then the notebook (before the explainers, so every term the copy uses is collected first)
  const related = (o.related || []).filter((r) => byId[r]);
  if (related.length) add("## Related observations", related.map((r) => `- [${r}](${page(r)}): ${md(byId[r].headline)}`).join("\n"));
  const nb = A.notebooks?.[o.stage] || A.notebook;
  add("## For analysts: the notebook's own words",
    `Quoted from section ${section} of the Stage ${o.stage} notebook${nb ? ` ([open it on GitHub](${nb}))` : ""}. Everything above says the same in plain English. The code that builds every lens is in \`analysis/eda/build.py\`.`,
    String(o.original || "").trim().split("\n").map((l) => `> ${l.replace(/^#+\s*/, "")}`.trimEnd()).join("\n"),
    (o.notebook_charts || []).map((c, i) => `![Chart ${i + 1} from the notebook, above observation ${o.id} (cell ${c.cell})](${abs(c.src)})`).join("\n\n"));

  // the explainers: every term the page and this copy use
  for (const m of JSON.stringify(o).matchAll(/\[\[([^\]|]+)/g)) terms.add(m[1]);
  const known = [...terms].filter((t) => A.glossary[t]);
  if (known.length) {
    add("## Explainers", known.map((t) => {
      const g = A.glossary[t];
      return `**${g.title}.** ${md(g.short)}${g.more ? `\n\n${md(g.more)}` : ""}`;
    }).join("\n\n"));
  }
  add("---", `_From the evidence atlas (an exploratory research view for IP Australia's IPAVentures programme, not an official publication), built ${A.built}. Every number is quoted from the analysis notebooks${A.repo ? `: ${A.repo}` : ""}._`);
  return `${out.join("\n\n")}\n`;
}
