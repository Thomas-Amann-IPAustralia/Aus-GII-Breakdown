// The chat's evidence: every page of the atlas split into passages (ADR 0054).
//
//   node analysis/atlas/passages.mjs            # writes evidence/data/passages.jsonl and passages.meta.json
//   node analysis/atlas/passages.mjs --check    # exits 1 if the committed files are not what it would write
//
// Observation pages come from their Markdown copies (evidence/js/markdown.js, the "Copy as Markdown" button), so a
// passage says exactly what its page says; the other pages (glossary, lenses, questions, sources, and the site's own
// pages) are flattened from atlas.json with the same markup handling. Each passage is one JSON line with sorted keys
// and no timestamps, so the file changes only when the pages do. The Econ service ingests this file at a named
// commit and serves it to the atlas chat (`econ atlas-ingest`).
import { createHash } from "node:crypto";
import { existsSync, readFileSync, writeFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

export const VERSION = "atlas-passages-v1";
export const CAP = 260; // words a passage
// and at most this many tokens by `toks`, an estimate of Econ's reference tokenizer (BAAI/bge-small-en-v1.5, a
// BERT word-piece vocabulary) that undercounted by at most 12 on the 4 November passages, so the real count stays
// under the 384 Econ's chunks keep to (its ingest checks with the tokenizer itself)
export const TOKEN_CAP = 360;
export const TABLE_ROWS = 120; // a longer table keeps its first rows and says how many follow
export const BASE = "https://thomas-amann-ipaustralia.github.io/Aus-GII-Breakdown/evidence/";

const root = resolve(dirname(fileURLToPath(import.meta.url)), "../..");
const { observationMarkdown, markup } = await import(pathToFileURL(`${root}/evidence/js/markdown.js`).href);
const STAGE_NAME = { 1: "each variable on its own", 2: "pairs of variables", 3: "many variables together" };

// ---------------------------------------------------------------------------------------------------- plain text

/** Markdown links and images as plain text: `[B6](https://…#/B6)` reads `B6`; images and code marks go. */
export function plain(text) {
  return String(text ?? "")
    .replace(/!\[[^\]]*\]\([^)]*\)/g, "")
    .replace(/\[([^\]]*)\]\((?:[^()]|\([^)]*\))*\)/g, "$1")
    .replace(/`/g, "");
}

const words = (s) => (s.match(/\S+/g) || []).length;
/** Tokens, estimated: a short word is one, a long one two or three, an acronym about one per 1.5 letters, digits
 * one per two, and each punctuation mark one (numbers, codes and tables cost far more than prose). */
export function toks(s) {
  let n = 2;
  for (const [g] of String(s).matchAll(/[A-Za-z]+|\d+|[^\sA-Za-z\d]/g)) {
    if (/[A-Za-z]/.test(g[0])) n += g.length >= 2 && g === g.toUpperCase() ? Math.ceil(g.length / 1.5) : 1 + (g.length >= 7) + (g.length >= 10);
    else if (/\d/.test(g[0])) n += Math.ceil(g.length / 2);
    else n += 1;
  }
  return n;
}
const fits = (t) => words(t) <= CAP && toks(t) <= TOKEN_CAP;
const isTable = (line) => /^\s*\|/.test(line);
const isItem = (line) => /^\s*(?:[-*] |\d+\. )/.test(line);
const HASH = /\b[0-9a-f]{16,}\b/;

/** Join hard-wrapped lines (the notebooks wrap at 120 characters): a line that starts no block joins the one before. */
function unwrap(lines) {
  const out = [];
  for (const raw of lines) {
    const line = raw.replace(/\s+$/, "");
    const prev = out.length ? out[out.length - 1] : "";
    const starts = !line.trim() || isTable(line) || isItem(line) || /^#/.test(line) || /^\*\*\d+\. /.test(line);
    if (!starts && prev.trim() && !isTable(prev)) out[out.length - 1] = `${prev} ${line.trim()}`;
    else out.push(line);
  }
  return out;
}

/** A block of text as units that may be packed into passages but never split: list items (with their nested
 * items), table rows (with the table's header kept apart), and sentences of an over-long paragraph. */
function units(text) {
  const lines = unwrap(text.split("\n"));
  const blocks = [];
  let cur = [];
  for (const l of lines) {
    if (!l.trim()) { if (cur.length) blocks.push(cur); cur = []; } else cur.push(l);
  }
  if (cur.length) blocks.push(cur);
  const out = [];
  for (const b of blocks) {
    if (isTable(b[0])) {
      const head = b.slice(0, 2).join("\n");
      let rows = b.slice(2);
      const more = rows.length - TABLE_ROWS;
      if (more > 0) rows = rows.slice(0, TABLE_ROWS);
      rows.forEach((r, i) => out.push({ text: r, table: head, first: i === 0 }));
      if (more > 0) out.push({ text: `(${more} more rows follow on the page.)`, gap: true });
      continue;
    }
    // a list: one unit per top-level item; nested lines stay with their item
    const items = [];
    for (const l of b) {
      if (items.length && /^\s+/.test(l)) items[items.length - 1].push(l);
      else items.push([l]);
    }
    items.forEach((it, i) => {
      const t = it.join("\n");
      if (fits(t)) out.push({ text: t, gap: i === 0 });
      else sentences(t).forEach((s, k) => out.push({ text: s, gap: i === 0 && k === 0 }));
    });
  }
  return out;
}

function sentences(t) {
  const parts = t.split(/(?<=[.!?:;])\s+(?=[A-Z(*"'“‘\-0-9])/);
  // a sentence longer than the cap is split at its commas rather than left whole
  return parts.flatMap((p) => (fits(p) ? [p] : p.split(/(?<=[,;])\s+/)));
}

/** Pack units into passages of at most CAP words and TOKEN_CAP tokens; a table's header row is repeated in each
 * passage it spans. */
function pack(text) {
  const us = units(text);
  const out = [];
  let cur = [], n = 0, t = 0, table = null;
  const flush = () => { if (cur.length) out.push(cur.join("\n").replace(/\n{3,}/g, "\n\n").trim()); cur = []; n = 0; t = 0; table = null; };
  for (const u of us) {
    const head = u.table && u.table !== table ? u.table : null;
    const need = words(u.text) + (head ? words(head) : 0);
    const needT = toks(u.text) + (head ? toks(head) : 0);
    if (n && (n + need > CAP || t + needT > TOKEN_CAP)) flush();
    const headNow = u.table && u.table !== table ? u.table : null;
    if (headNow) { if (cur.length) cur.push(""); cur.push(headNow); table = u.table; n += words(headNow); t += toks(headNow); }
    else if (!u.table) { if (cur.length && (u.gap || table)) cur.push(""); table = null; }
    cur.push(u.text);
    n += words(u.text);
    t += toks(u.text);
  }
  flush();
  return out.filter((p) => p && words(p) > 0);
}

// ---------------------------------------------------------------------------------------------------- observations

/** The sections of an observation's Markdown copy: `{path: [h2, h3?], body}`, in order. */
function sectionsOf(mdText) {
  const out = [];
  let h2 = null, h3 = null, body = [];
  const push = () => { if (h2 !== null) out.push({ path: h3 ? [h2, h3] : [h2], body: body.join("\n") }); body = []; };
  for (const line of mdText.split("\n")) {
    const m2 = /^## (.*)$/.exec(line), m3 = /^### (.*)$/.exec(line);
    if (m2) { push(); h2 = m2[1].trim(); h3 = null; }
    else if (m3 && h2 !== null) { push(); h3 = m3[1].trim(); }
    else if (/^---$/.test(line)) { push(); h2 = null; }
    else if (h2 !== null) body.push(line);
  }
  push();
  return out;
}

const DROP = [/^Explainers$/, /^Related observations$/];

function observationPassages(o, A, chart) {
  const md = observationMarkdown(o, { atlas: A, chart, base: BASE });
  const secs = sectionsOf(md);
  const srcs = o.sources.map((s) => A.sources[s]).filter(Boolean);
  const out = [];
  // a short preamble before a section's first sub-section (the chart's subtitle; "From the publisher's file ...")
  // goes with that first sub-section rather than standing alone
  for (let i = 0; i < secs.length; i++) {
    const s = secs[i];
    if (DROP.some((r) => r.test(s.path[0]))) continue;
    let body = s.body;
    const next = secs[i + 1];
    if (s.path.length === 1 && next && next.path.length === 2 && next.path[0] === s.path[0] && words(plain(body)) < 60) {
      next.body = `${body.trim()}\n\n${next.body}`;
      continue;
    }
    if (s.path[1]?.startsWith("Step 1 of 4")) {
      // one line per source: its name, publisher and licence (the page has its dates, tables and fingerprints)
      body = [s.body.split("\n").find((l) => l.trim() && !isItem(l)) || "",
        ...srcs.map((x) => `- ${x.title} (${x.derived ? `built by this project, ${x.publisher.replace(/^(built|compiled) here /, "")}` : `published by ${x.publisher}`}${x.licence ? `; licence: ${x.licence}` : ""})`)].join("\n");
    }
    if (s.path[1]?.startsWith("Step 2 of 4")) {
      // the tables without their sizes and fingerprints
      body = body.replace(/ \(the fingerprint is [^)]*\)/, "").split("\n").map((l) => {
        if (!isTable(l)) return l;
        const cells = l.split(/(?<!\\)\|/).slice(1, -1);
        return `|${cells.slice(0, 3).join("|")}|`;
      }).join("\n");
    }
    if (s.path[0] === "For analysts: the notebook's own words") body = body.replace(/^> ?/gm, "");
    body = plain(body).split("\n").filter((l) => !HASH.test(l)).join("\n");
    for (const text of pack(body)) out.push({ section: s.path.map(plain), text });
  }
  const L = A.lenses[o.lens] || { name: o.lens };
  return out.map((p, k) => ({
    passage_id: `atlas-${o.id}:${String(k).padStart(4, "0")}`,
    doc_id: `atlas-${o.id}`,
    kind: "observation",
    observation: o.id,
    stage: String(o.stage),
    lens: o.lens,
    lens_name: L.name,
    strength: o.strength,
    chapter: plain(o.section || o.chapter || ""),
    title: `${o.id}: ${plain(markup(A)(o.headline))}`,
    section: p.section,
    url: `${BASE}#/${o.id}`,
    related: (o.related || []).filter((r) => A.observations.some((x) => x.id === r)),
    text: p.text,
  }));
}

// ---------------------------------------------------------------------------------------------------- other pages

const LABELS = {
  title: null, name: null, signal: null, gap: null, claim: null, label: null,
  text: "", short: "", intro: "", lead: "", what: "", now: "Now", why: "Why", source: "Possible source", cost: "Cost",
  when: "When", strength: "Strength", next: "Next", asks: "Asks", how: "How", example: "Example", adds: "Adds",
  done: "Done when", status: "Status", evidence: "Evidence", follows: "What follows", note: "Note", adds_here: "Adds",
  sub: "Sub-questions", reach: "What the data can reach", affects: "Affects", category: null, value: null,
  figures: "Figures published", agree: "Years that agree", years: "Years", gap_pct: "Largest gap (%)",
  gap_pts: "Largest gap (points)", ids: "Observations", questions: "Questions",
};
const SKIP = new Set(["href", "chart", "charts", "src", "kind", "record", "adr", "adr_later", "as_at", "eyebrow", "n"]);

/** A sentence's closing stop, if it has none. */
const stop = (t) => (/[.!?:;)"'”’]$|\*\*$/.test(t.trim()) ? t.trim() : `${t.trim()}.`);

/** One list item or record as one line of text. */
function record(x, md) {
  if (typeof x === "string" || typeof x === "number") return md(String(x));
  if (!x || typeof x !== "object") return "";
  const head = ["id", "title", "name", "signal", "gap", "claim", "label"].filter((k) => typeof x[k] === "string" || typeof x[k] === "number");
  const lead = head.map((k) => md(String(x[k]))).join(": ");
  const rest = [];
  for (const [k, v] of Object.entries(x)) {
    if (head.includes(k) || SKIP.has(k) || v == null || typeof v === "boolean" || k === "category") continue;
    const lab = LABELS[k] === undefined ? k.replace(/_/g, " ").replace(/^./, (c) => c.toUpperCase()) : LABELS[k];
    let val;
    if (Array.isArray(v)) val = k === "questions" ? v.map((q) => `Q${q}`).join(", ") : v.every((i) => typeof i !== "object") ? v.map((i) => md(String(i))).join(k === "ids" || k === "affects" ? ", " : "; ") : v.map((i) => record(i, md)).join("; ");
    else if (typeof v === "object") val = record(v, md);
    else val = md(String(v));
    if (!val) continue;
    rest.push(stop(lab ? `${lab}: ${val}` : val));
  }
  return [lead ? `**${stop(lead)}**` : null, ...rest].filter(Boolean).join(" ");
}

/** A page's content object as sections: `X_title` names the section of `X`, and `X_intro` leads it. */
function flatten(obj, md, headings = {}, skip = []) {
  const keys = Object.keys(obj).filter((k) => !SKIP.has(k) && !skip.includes(k));
  const done = new Set();
  const secs = [];
  const lead = [];
  for (const k of keys) {
    if (done.has(k)) continue;
    const stem = k.replace(/_(title|intro)$/, "");
    if (stem !== k && obj[stem] === undefined) {
      // an intro or title with no list of its own: part of the page's lead, or a section of its own
      if (k.endsWith("_title")) { done.add(k); continue; }
      done.add(k);
      secs.push({ path: [headings[stem] || obj[`${stem}_title`] || cap(stem)], body: md(obj[k]) });
      continue;
    }
    if (stem !== k) continue; // handled with its stem
    done.add(k);
    const v = obj[k];
    const head = obj[`${k}_title`] || headings[k] || cap(k);
    const intro = obj[`${k}_intro`] ? md(obj[`${k}_intro`]) : null;
    done.add(`${k}_title`); done.add(`${k}_intro`);
    if (typeof v === "string" || typeof v === "number") {
      if (["title", "intro", "lead", "banner", "page_title"].includes(k)) lead.push(md(String(v)));
      else secs.push({ path: [head], body: md(String(v)) });
    } else if (Array.isArray(v)) {
      secs.push({ path: [head], body: [intro, v.map((x) => `- ${record(x, md)}`).join("\n")].filter(Boolean).join("\n\n") });
    } else if (v && typeof v === "object") {
      const vals = Object.values(v);
      if (vals.every((x) => typeof x === "string")) {
        secs.push({ path: [head], body: [intro, Object.entries(v).map(([a, b]) => `- **${a}**: ${md(b)}`).join("\n")].filter(Boolean).join("\n\n") });
      } else {
        for (const s of flatten(v, md, headings)) secs.push({ path: [head, ...s.path.filter((p) => p !== "About this page")], body: s.body });
      }
    }
  }
  if (lead.length) secs.unshift({ path: ["About this page"], body: lead.join("\n\n") });
  return secs.filter((s) => s.body && s.body.trim());
}
const cap = (k) => k.replace(/_/g, " ").replace(/^./, (c) => c.toUpperCase());

function docPassages(doc, secs) {
  const out = [];
  for (const s of secs) for (const text of pack(plain(s.body))) out.push({ section: s.path.map(plain), text });
  return out.map((p, k) => ({
    passage_id: `${doc.doc_id}:${String(k).padStart(4, "0")}`,
    doc_id: doc.doc_id,
    kind: doc.kind,
    observation: null,
    stage: null,
    lens: doc.lens || null,
    lens_name: doc.lens_name || null,
    strength: null,
    chapter: null,
    title: doc.title,
    section: p.section,
    url: `${BASE}#/${doc.route}`,
    related: doc.related || [],
    text: p.text,
  }));
}

const idsIn = (x) => [...new Set([...JSON.stringify(x).matchAll(/\{([UBM]\d+)\}/g)].map((m) => m[1]))];

function otherPassages(A) {
  const md = markup(A);
  const known = new Set(A.observations.map((o) => o.id));
  const rel = (x) => idsIn(x).filter((i) => known.has(i)).sort(byIdOrder);
  const out = [];
  // the glossary: one document per term
  for (const [term, g] of Object.entries(A.glossary)) {
    const body = `**${md(g.title)}.** ${md(g.short)}${g.more ? `\n\n${md(g.more)}` : ""}`;
    out.push(...docPassages({ doc_id: `atlas-glossary-${term}`, kind: "glossary", title: `Glossary: ${plain(md(g.title))}`, route: `glossary/${term}`, related: rel(g) },
      [{ path: ["Glossary", plain(md(g.title))], body }]));
  }
  // the lenses
  for (const [id, L] of Object.entries(A.lenses)) {
    const secs = [{ path: [L.name], body: [md(L.description), `Unit: ${md(L.unit)}.${L.rows ? ` Rows: ${md(L.rows)}.` : ""}`].filter(Boolean).join("\n\n") }];
    if (L.facts?.length) secs.push({ path: [L.name, "Key figures"], body: L.facts.map((f) => `- ${record(f, md)}`).join("\n") });
    if (L.repairs?.length) secs.push({ path: [L.name, "Repairs made before any observation"], body: L.repairs.map((r, i) => `${i + 1}. ${md(r.what)} Why: ${md(r.why)}`).join("\n") });
    if (L.limits?.length) secs.push({ path: [L.name, "Limits"], body: L.limits.map((x) => `- ${md(x)}`).join("\n") });
    const srcs = (L.sources || []).map((s) => A.sources[s]?.title).filter(Boolean);
    if (srcs.length) secs.push({ path: [L.name, "Sources"], body: srcs.map((t) => `- ${md(t)}`).join("\n") });
    if (L.questions?.length) secs.push({ path: [L.name, "Questions it bears on"], body: L.questions.map((q) => `- Q${q}. ${md(A.questions.find((x) => x.id === q)?.title)}`).join("\n") });
    out.push(...docPassages({ doc_id: `atlas-lens-${id}`, kind: "lens", title: `Lens: ${L.name}`, route: `lens/${id}`, lens: id, lens_name: L.name, related: rel(L) }, secs));
  }
  // the five research questions
  for (const q of A.questions) {
    const secs = [{ path: [`Q${q.id}. ${md(q.title)}`], body: md(q.text) }];
    if (q.sub?.length) secs.push({ path: [`Q${q.id}. ${md(q.title)}`, "Sub-questions"], body: q.sub.map((x) => `- ${md(x)}`).join("\n") });
    if (q.reach?.length) secs.push({ path: [`Q${q.id}. ${md(q.title)}`, "What the data can reach"], body: q.reach.map((x) => `- ${md(x)}`).join("\n") });
    out.push(...docPassages({ doc_id: `atlas-question-${q.id}`, kind: "question", title: `Research question ${q.id}: ${plain(md(q.title))}`, route: `question/${q.id}`, related: rel(q) }, secs));
  }
  // the sources, one document each (they share the data page)
  for (const [id, s] of Object.entries(A.sources)) {
    const body = [`**${md(s.title)}.** ${s.derived ? `Built by this project, ${s.publisher.replace(/^(built|compiled) here /, "")}.` : `Published by ${s.publisher}.`}`,
      s.licence ? `Licence: ${md(s.licence)}.` : null, s.coverage ? `Coverage: ${md(s.coverage)}.` : null,
      s.tier != null ? `Tier ${s.tier}${(s.questions || []).length ? `; questions ${s.questions.join(", ")}` : ""}.` : null].filter(Boolean).join(" ");
    out.push(...docPassages({ doc_id: `atlas-source-${id}`, kind: "source", title: `Source: ${plain(md(s.title))}`, route: "data", related: rel(s) },
      [{ path: ["Data sources", plain(md(s.title))], body }]));
  }
  // the site's own pages
  const S = A.site;
  const n = A.observations.length;
  const overview = { hero: S.hero, stats: S.stats.map((x) => ({ ...x, value: String(x.value).replace("{n}", n) })), banner: S.banner,
    journey_intro: S.journey_intro, stages: S.stages, featured: S.featured, stage2: S.stage2, ten_title: S.ten_title, ten_intro: S.ten_intro, ten: S.ten, reading: S.reading };
  const pages = [
    { route: "", doc_id: "atlas-page-overview", title: "Overview: what Australia's IP data show so far", content: overview,
      headings: { hero: "Overview", stats: "In numbers", stages: "The three stages", featured: "Start with one observation", stage2: "What Stage 2 found", reading: "How to read an observation", banner: "Overview" } },
    { route: "stage3", doc_id: "atlas-page-stage3", title: "What Stage 3 found", content: { ...S.stage3, verdict_words: S.verdict_words },
      headings: { items: "What Stage 3 found", how: "How Stage 3 works", example: "An example", verdict_words: "What each outcome means", verdicts: "Outcomes", board: "Every observation Stage 3 revisited", structure: "What Stage 3 found about structure" } },
    { route: "limits", doc_id: "atlas-page-limits", title: "Limits and assumptions", content: S.limits,
      headings: { cannot: "What the three stages cannot tell you", assumptions: "Assumptions", weak: "Where the datasets link weakly", corrections: "Corrections" } },
    { route: "next", doc_id: "atlas-page-next", title: "What comes next", content: S.next,
      headings: { stages: "The stages", signals: "Early signals that warrant further investigation", recorded: "Recorded, not carried", data_gaps: "Data gaps", puzzles: "Puzzles", owner: "Open questions for the research owner", ipa: "Open questions for IP Australia", after: "After Stage 3" } },
  ];
  if (A.audit) {
    pages.push({ route: "audit", doc_id: "atlas-page-audit", title: "Checked against IP Australia", content: A.audit,
      headings: { in_brief: "In brief", since: "Since the first review", method: "Method", verdict_words: "What each verdict means", measures: "Measures compared year by year", conclusions: "IP Australia's conclusions and what the evidence adds", changes: "What the review changed", questions: "Questions raised", limits: "Limits of the check", findings: "Findings", verdicts: "Verdicts, observation by observation", untestable: "Not testable", counts: "Verdicts counted", later: "The later check (4 November 2026)", stats: "In numbers" } });
  }
  for (const p of pages) {
    const secs = flatten(p.content, md, p.headings);
    out.push(...docPassages({ doc_id: p.doc_id, kind: "page", title: p.title, route: p.route, related: rel(p.content) }, secs));
  }
  return out;
}

function byIdOrder(a, b) {
  const k = (x) => ["U", "B", "M"].indexOf(x[0]) * 1000 + Number(x.slice(1));
  return k(a) - k(b);
}

// ---------------------------------------------------------------------------------------------------- output

const sorted = (o) => Array.isArray(o) ? o.map(sorted) : o && typeof o === "object"
  ? Object.fromEntries(Object.keys(o).sort().map((k) => [k, sorted(o[k])])) : o;
const sha = (b) => createHash("sha256").update(b).digest("hex");

export function build() {
  const atlasBytes = readFileSync(`${root}/evidence/data/atlas.json`);
  const A = JSON.parse(atlasBytes.toString("utf8"));
  const passages = [];
  for (const o of A.observations) {
    const p = `${root}/evidence/data/charts/${o.chart}.json`;
    const chart = o.chart && existsSync(p) ? JSON.parse(readFileSync(p, "utf8")) : null;
    passages.push(...observationPassages(o, A, chart));
  }
  passages.push(...otherPassages(A));
  const jsonl = passages.map((p) => JSON.stringify(sorted(p))).join("\n") + "\n";
  const kinds = {};
  for (const p of passages) kinds[p.kind] = (kinds[p.kind] || 0) + 1;
  const meta = sorted({
    version: VERSION,
    built: A.built,
    atlas_sha256: sha(atlasBytes),
    passages_sha256: sha(Buffer.from(jsonl, "utf8")),
    passages: passages.length,
    documents: new Set(passages.map((p) => p.doc_id)).size,
    kinds: sorted(kinds),
    words: passages.reduce((n, p) => n + words(p.text), 0),
    word_cap: CAP,
    token_cap: TOKEN_CAP,
    table_rows: TABLE_ROWS,
    base: BASE,
  });
  return { jsonl, meta: `${JSON.stringify(meta, null, 2)}\n`, passages };
}

if (import.meta.url === pathToFileURL(process.argv[1]).href) {
  const { jsonl, meta } = build();
  const out = `${root}/evidence/data/passages.jsonl`, metaOut = `${root}/evidence/data/passages.meta.json`;
  if (process.argv.includes("--check")) {
    const same = existsSync(out) && existsSync(metaOut) && readFileSync(out, "utf8") === jsonl && readFileSync(metaOut, "utf8") === meta;
    if (!same) { console.error("passages.jsonl is out of date: run `node analysis/atlas/passages.mjs` and commit"); process.exit(1); }
    console.log("passages: current");
  } else {
    writeFileSync(out, jsonl);
    writeFileSync(metaOut, meta);
    console.log(meta.trim());
  }
}
