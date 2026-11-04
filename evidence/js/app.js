// The evidence atlas: one page, routed by the address's #fragment, reading evidence/data/atlas.json (built by
// analysis/atlas/build.py) and each chart's JSON on demand. All text reaches the page as text nodes; the light markup
// in the content (**bold**, [[term]], {U44}, {B6}, {M3}, `code`) is turned into elements here, never parsed as HTML.

import { download, el, initTheme } from "../../assets/js/util.js";
import { chartCard, sweep } from "./charts.js";
import { observationMarkdown } from "./markdown.js";

const $ = (s, r = document) => r.querySelector(s);
const main = $("#main");
let A = null; // the atlas
const byId = {};
const chartCache = {};

const LENS_ORDER = ["rights", "timeline", "firms", "regions", "national", "industries", "institutions", "corpus"];
const lensColour = (l) => `var(--l-${l})`;

// ------------------------------------------------------------------------------------------------ text markup

const TOKEN = /\*\*(.+?)\*\*|\[\[([^\]|]+)(?:\|([^\]]+))?\]\]|\{([UBM]\d+)\}|`([^`]+)`|(OQ\d+)/g;
/** Inline markup to nodes. */
function inline(text) {
  const out = [];
  let last = 0;
  for (const m of String(text ?? "").matchAll(TOKEN)) {
    if (m.index > last) out.push(document.createTextNode(text.slice(last, m.index)));
    if (m[1] !== undefined) out.push(el("strong", inline(m[1])));
    else if (m[2] !== undefined) out.push(termButton(m[2], m[3] || A.glossary[m[2]]?.title?.toLowerCase() || m[2]));
    else if (m[4] !== undefined) out.push(obsLink(m[4]));
    else if (m[5] !== undefined) out.push(el("code", m[5]));
    else if (m[6] !== undefined) out.push(el("a", { href: "#/next", title: "An open question, listed under What comes next" }, m[6]));
    last = m.index + m[0].length;
  }
  if (last < String(text ?? "").length) out.push(document.createTextNode(text.slice(last)));
  return out;
}
/** Paragraphs (blank-line separated) of inline markup. */
function paras(text, cls) {
  return String(text ?? "").split(/\n\s*\n/).filter(Boolean).map((p) => el(`p${cls ? `.${cls}` : ""}`, inline(p.trim())));
}
/** The notebook's own markdown, for the "for analysts" view: bullets, numbered lists, bold and code. */
function notebookMarkdown(md) {
  const box = el("div.original");
  let list = null;
  for (const raw of md.split("\n")) {
    const line = raw.replace(/^#+\s*/, "");
    const b = raw.match(/^\s*(?:-|\d+\.)\s+(.*)$/);
    if (b) {
      if (!list) { list = el(/^\s*\d/.test(raw) ? "ol" : "ul"); box.append(list); }
      list.append(el("li", inline(b[1])));
    } else if (/^\s{2,}\S/.test(raw) && list?.lastChild) {
      list.lastChild.append(" ", ...inline(raw.trim()));
    } else if (raw.trim()) {
      list = null;
      box.append(el("p", inline(line)));
    } else list = null;
  }
  return box;
}

// ------------------------------------------------------------------------------------------------ small components

function obsLink(id) {
  const o = byId[id];
  return el("a.id", { href: `#/${id}`, title: o ? o.headline : id }, id);
}
function lensChip(lens, link = true) {
  const L = A.lenses[lens] || { name: lens };
  const c = el(link ? "a.chip" : "span.chip", link ? { href: `#/lens/${lens}` } : {}, el("span.ldot"), L.name);
  c.style.setProperty("--lc", lensColour(lens));
  return c;
}
function qChip(q) {
  const Q = A.questions.find((x) => x.id === q);
  return el("a.chip.qchip", { href: `#/question/${q}`, title: Q?.title }, `Q${q} · ${Q?.short || ""}`);
}
function strengthBadge(s) {
  return el("span.strength", { title: "How strong the evidence is: see How to read an observation" }, s);
}
const STAGE_NAME = { 1: "each variable on its own", 2: "pairs of variables", 3: "many variables together" };
function stageChip(o) {
  return el(`span.chip.stagechip.s${o.stage}`, { title: `Stage ${o.stage}: ${STAGE_NAME[o.stage]}` }, `Stage ${o.stage}`);
}
function aboutLabel(o) {
  return el("span.about", o.about === "data" ? "About the data" : "About the IP system");
}
// Stage 3's outcomes (ADR 0046): always the word and its colour together, never the colour alone
const VERDICT_TONE = {
  holds: "hold", weakened: "weak", "not detected once held": "gone", reversed: "rev", "appears once held": "new",
  "not detected either way": "none", "does not replicate": "none", mixed: "mixed", refined: "ref",
};
function verdictTag(v, small = false) {
  return el(`span.vtag.vt-${VERDICT_TONE[v] || "none"}${small ? ".sm" : ""}`, { title: A.site.verdict_words?.[v] || null }, v);
}
/** The outcomes a page carries: a Stage 3 page's own (what it revisits), or what Stage 3 found for an earlier page. */
function verdictsOf(o) {
  return [...new Set([...(o.revisits || []), ...(o.later || [])].map((r) => r.verdict))];
}
function laterChip(o) {
  return o.later?.length ? el("span.chip.later", { title: "Stage 3 tested this with other factors held" }, `Tested again in ${o.later.map((x) => x.id).join(", ")}`) : null;
}
function ocard(o) {
  const a = el("a.ocard", { href: `#/${o.id}` },
    el("div.meta", el("span.id", o.id), lensChip(o.lens, false), stageChip(o), aboutLabel(o)),
    el("h3", o.headline),
    el("p", trim(plain(o.statement), 190)),
    el("div.meta", (o.questions || []).map((q) => el("span.chip.qchip", `Q${q.q}`)), o.chart ? el("span.chip", "Chart") : null,
      o.stage === 3 ? verdictsOf(o).map((v) => verdictTag(v, true)) : laterChip(o)));
  a.style.setProperty("--lc", lensColour(o.lens));
  return a;
}
/** A compact row for long lists: the id, the headline, and what Stage 3 made of it. */
function orow(o) {
  const tags = o.stage === 3 ? verdictsOf(o).map((v) => verdictTag(v, true)) : o.later?.length
    ? [el("span.chip.later", { title: `Stage 3 tested this with other factors held: ${o.later.map((x) => `${x.id}, ${x.verdict}`).join("; ")}` }, `→ ${o.later.map((x) => x.id).join(", ")}`)] : [];
  const a = el("a.orow", { href: `#/${o.id}` },
    el("span.id", o.id),
    el("span.ohead", o.headline),
    el("span.otags", ...tags, o.chart ? el("span.ochart", { title: "Has a chart" }, icon("chart")) : null));
  a.style.setProperty("--lc", lensColour(o.lens));
  return a;
}
/** A notebook section as a group that opens and closes, holding its observations as rows. */
function sectionGroup(title, items, open = true) {
  return el("details.sub", open ? { open: true } : {},
    el("summary", el("span.chev", { "aria-hidden": "true" }, "›"), el("span.stitle", title.replace(/`/g, "")), el("span.scount", String(items.length))),
    el("div.olist", items.map(orow)));
}
/** Every check Stage 3 made of an earlier observation, with the Stage 3 page that made it. */
function revisitsAll() {
  return A.observations.filter((o) => o.stage === 3).flatMap((o) => (o.revisits || []).map((r) => ({ ...r, m: o.id, lens: o.lens })));
}
/** A bar of Stage 3's checks by outcome, with the counts written out beside it. */
function verdictBar() {
  const all = revisitsAll();
  const counts = A.verdicts.map((v) => [v, all.filter((r) => r.verdict === v).length]).filter(([, c]) => c);
  const label = counts.map(([v, c]) => `${c} ${v}`).join(", ");
  return el("div.vsummary",
    el("div.vbar", { role: "img", "aria-label": `Stage 3's ${all.length} checks of earlier observations by outcome: ${label}.` },
      counts.map(([v, c]) => { const s = el(`span.vt-${VERDICT_TONE[v]}`, { title: `${v}: ${c}` }); s.style.flexGrow = String(c); return s; })),
    el("div.vlegend", counts.map(([v, c]) => el("span", verdictTag(v, true), el("strong", String(c))))));
}
/** A numbered list of findings, each with the observations behind it. */
function tenList(items) {
  return el("ol.ten", { style: { listStyle: "none", padding: 0 } }, items.map((t, i) => el("li.tenitem",
    el("span.n", String(i + 1).padStart(2, "0")),
    el("h3", t.title),
    ...paras(t.text),
    el("div.meta", t.ids.map(obsLink)))));
}
/** A name or phrase used mid-sentence: first letter lower-cased, unless it starts an acronym or a proper noun. */
function lower(s) {
  const t = String(s ?? "");
  return /^([A-Z]{2}|Australia)/.test(t) ? t : t.charAt(0).toLowerCase() + t.slice(1);
}
/** Markup removed, for short summaries. */
function plain(s) {
  return String(s ?? "").replace(/\[\[[^\]|]+\|([^\]]+)\]\]/g, "$1").replace(/\[\[([^\]]+)\]\]/g, (_, k) => A.glossary[k]?.title?.toLowerCase() || k)
    .replace(/\*\*/g, "").replace(/\{([UBM]\d+)\}/g, "$1").replace(/`/g, "");
}
function trim(s, n) {
  const t = String(s).replace(/\s+/g, " ").trim();
  return t.length > n ? `${t.slice(0, t.lastIndexOf(" ", n))}…` : t;
}
function icon(name) {
  const s = document.createElementNS("http://www.w3.org/2000/svg", "svg");
  s.setAttribute("class", "i");
  s.setAttribute("aria-hidden", "true");
  const u = document.createElementNS("http://www.w3.org/2000/svg", "use");
  u.setAttribute("href", `#i-${name}`);
  s.append(u);
  return s;
}
function note(kind, text) {
  const tags = { assume: ["Assumption", "flag"], limit: ["Limit", "alert"], next: ["Next stage", "arrow"], done: ["Done in Stage 3", "check"] };
  const [tag, ic] = tags[kind];
  return el(`div.note.${kind}`, icon(ic), el("div", el("span.tag", tag), el("p", inline(text))));
}
function setCrumbs(parts) {
  const c = $("#crumbs");
  c.replaceChildren();
  parts.forEach((p, i) => {
    if (i) c.append(el("span.sep", { "aria-hidden": "true" }, "/"));
    c.append(p.href ? el("a", { href: p.href }, p.label) : el("strong", { "aria-current": "page" }, p.label));
  });
}
function setNav(key) {
  for (const a of document.querySelectorAll(".nav a")) {
    if (a.dataset.nav === key) a.setAttribute("aria-current", "page");
    else a.removeAttribute("aria-current");
  }
}
function section(title, intro, ...kids) {
  return el("section.section", el("div.section-head", el("div", el("h2", title), intro ? el("p", inline(intro)) : null)), ...kids);
}
function editorialNote(text) {
  return el("p.editorial", icon("info"), el("span", text));
}

// glossary popover
const pop = $("#popover");
let popFor = null;
function termButton(key, shown) {
  const b = el("button.term", { type: "button", "aria-expanded": "false", "data-term": key }, shown);
  b.addEventListener("click", (e) => { e.stopPropagation(); popFor === b ? hidePop() : showPop(b, key); });
  b.addEventListener("mouseenter", () => showPop(b, key));
  b.addEventListener("mouseleave", () => setTimeout(() => { if (!pop.matches(":hover") && popFor === b) hidePop(); }, 180));
  return b;
}
function showPop(b, key) {
  const g = A.glossary[key];
  if (!g) return;
  popFor?.setAttribute("aria-expanded", "false");
  popFor = b;
  b.setAttribute("aria-expanded", "true");
  pop.replaceChildren(el("h3", g.title), ...paras(g.short), el("p", el("a", { href: `#/glossary/${key}` }, "More in the glossary")));
  pop.hidden = false;
  const r = b.getBoundingClientRect(), w = Math.min(360, innerWidth - 24);
  pop.style.left = `${Math.max(12, Math.min(r.left, innerWidth - w - 12))}px`;
  const below = r.bottom + 8, h = pop.offsetHeight;
  pop.style.top = `${below + h > innerHeight - 8 ? Math.max(8, r.top - h - 8) : below}px`;
}
function hidePop() {
  popFor?.setAttribute("aria-expanded", "false");
  popFor = null;
  pop.hidden = true;
}
pop.addEventListener("mouseleave", hidePop);
document.addEventListener("click", (e) => { if (!pop.contains(e.target)) hidePop(); });
document.addEventListener("keydown", (e) => { if (e.key === "Escape") { const b = popFor; hidePop(); b?.focus(); } });
addEventListener("scroll", hidePop, { passive: true });

// charts: fetched once, drawn into a placeholder
function chartSlot(id, opts = {}) {
  const slot = el("div.chart-slot");
  const o = byId[id];
  const origin = o?.chart_origin || "query";
  const go = (spec) => slot.replaceChildren(chartCard(spec, { origin, ...opts }));
  if (chartCache[id]) go(chartCache[id]);
  else {
    fetch(`data/charts/${id}.json`).then((r) => (r.ok ? r.json() : Promise.reject(r.status))).then((spec) => {
      chartCache[id] = spec;
      go(spec);
    }).catch(() => slot.replaceChildren(el("p.muted.small", "The chart could not be loaded.")));
  }
  return slot;
}

// the Markdown copy of an observation page (markdown.js), with the chart's numbers as a table
async function chartSpec(id) {
  if (!chartCache[id]) {
    const r = await fetch(`data/charts/${id}.json`);
    if (!r.ok) throw new Error(String(r.status));
    chartCache[id] = await r.json();
  }
  return chartCache[id];
}
async function markdownOf(o) {
  const chart = o.chart ? await chartSpec(o.chart).catch(() => null) : null;
  return observationMarkdown(o, { atlas: A, chart, base: location.href.split("#")[0] });
}
function say(text) {
  const live = $("#live");
  if (live) { live.textContent = ""; requestAnimationFrame(() => { live.textContent = text; }); }
}
async function copyText(text) {
  try { await navigator.clipboard.writeText(text); return true; } catch { /* no clipboard: the older way */ }
  const t = el("textarea", { style: { position: "fixed", opacity: "0" } }, text);
  document.body.append(t);
  t.select();
  let ok = false;
  try { ok = document.execCommand("copy"); } catch { ok = false; }
  t.remove();
  return ok;
}
function markdownTools(o) {
  const label = (b, text) => { b.lastChild.textContent = text; };
  const copy = el("button.btn.small", { type: "button", title: "Copy this page as Markdown: the observation, its chart's numbers as a table, the evidence trail, sources, limits and explainers" }, icon("copy"), el("span", "Copy as Markdown"));
  const save = el("button.btn.small", { type: "button", title: `Download this page as ${o.id}.md` }, icon("source"), el("span", "Download .md"));
  copy.addEventListener("click", async () => {
    const ok = await copyText(await markdownOf(o));
    label(copy, ok ? "Copied" : "Could not copy");
    say(ok ? `Observation ${o.id} copied as Markdown.` : "The browser did not allow copying; use Download .md instead.");
    setTimeout(() => label(copy, "Copy as Markdown"), 2000);
  });
  save.addEventListener("click", async () => {
    download(`${o.id}.md`, await markdownOf(o), "text/markdown;charset=utf-8");
    say(`Observation ${o.id} downloaded as ${o.id}.md.`);
  });
  return el("div.md-tools", { role: "group", "aria-label": "Take this page as Markdown" }, copy, save);
}

// ------------------------------------------------------------------------------------------------ pages

/** Replace the page's content, skipping empty slots (a native replaceChildren would print "null"). */
function show(...nodes) {
  main.replaceChildren(...nodes.flat(Infinity).filter((n) => n != null && n !== false && n !== ""));
}

function home() {
  setCrumbs([{ label: "Overview" }]);
  setNav("home");
  const S = A.site;
  const n = A.observations.length;
  const metrics = el("div.metrics", S.stats.map((s) => el("div", el("strong", s.value.replace("{n}", n)), el("span", s.label))));
  const hero = el("div.hero",
    el("div",
      el("div.eyebrow", S.hero.eyebrow),
      el("h1", S.hero.title),
      ...paras(S.hero.lead, "lead"),
      el("div.row", { style: { marginTop: "18px" } },
        el("a.btn.primary", { href: "#/stage3" }, "What Stage 3 found", icon("arrow")),
        el("a.btn", { href: "#/observations" }, "Browse all observations"),
        el("a.btn", { href: "#/limits" }, "What the analysis cannot tell you yet"))),
    metrics);

  const banner = el("div.banner", icon("info"), el("div", ...paras(S.banner)));

  const journey = el("div.journey", S.stages.map((s) => el(`a.stage${s.status === "Complete" ? ".done" : s.now ? ".now" : ""}`, { href: s.href || "#/next" },
    el("div.dot", s.n), el("h3", s.name), el("span.status", s.status), el("p", s.short))));

  const f = byId[S.featured.id];
  const feature = el("div.feature",
    el("div.feature-copy",
      el("div.meta", obsLink(f.id), lensChip(f.lens), stageChip(f), strengthBadge(f.strength)),
      el("h2", S.featured.title || f.headline),
      ...paras(S.featured.text),
      el("div.row", el("a.btn.primary", { href: `#/${f.id}` }, "Follow this observation back to its data", icon("arrow")))),
    el("div.feature-viz", chartSlot(f.chart, { compact: true })));

  const found3 = S.stage3 ? el("div",
    verdictBar(),
    tenList(S.stage3.items),
    el("div.row", { style: { marginTop: "16px" } }, el("a.btn.primary", { href: "#/stage3" }, "Every signal Stage 3 tested, and what is left of it", icon("arrow")),
      el("a.btn", { href: "#/next" }, "The early signals and data gaps"))) : null;

  const lensTiles = el("div.lens-tiles", LENS_ORDER.filter((l) => A.lenses[l]).map((l) => {
    const L = A.lenses[l];
    const mine = A.observations.filter((o) => o.lens === l);
    const per = [1, 2, 3].map((k) => mine.filter((o) => o.stage === k).length).map((c, k) => (c ? `${c} in Stage ${k + 1}` : "")).filter(Boolean).join(", ");
    const t = el("a.ltile", { href: `#/lens/${l}` }, el("h3", L.name), el("p", L.unit), el("small", `${mine.length} observation${mine.length === 1 ? "" : "s"}${per ? ` (${per})` : ""}`));
    t.style.setProperty("--lc", lensColour(l));
    return t;
  }));

  const qTiles = el("div.grid.g3", A.questions.map((q) => {
    const count = A.observations.filter((o) => o.questions.some((x) => x.q === q.id)).length;
    const t = el("a.ltile", { href: `#/question/${q.id}` },
      el("small", `Question ${q.id}`), el("h3", q.title), el("small", `${count} observations bear on it`));
    t.style.setProperty("--lc", "var(--teal)");
    return t;
  }));

  const anatomy = el("div.anatomy", S.reading.parts.map((p) => el(`div.a-${p.kind}`, el("strong", p.title), ...paras(p.text))));
  const scale = el("div.grid.g4", S.reading.strengths.map((s) => el(`div.card.flat`, { style: s.now ? { borderColor: "var(--obs-line)", background: "var(--obs)" } : {} },
    el("h3", s.name, ...(s.stages || []).map((k) => el("span.chip", { style: { marginLeft: "8px" } }, `Stage ${k}`))), ...paras(s.text))));

  show(hero, banner,
    section("Where this sits in the research", S.journey_intro, journey),
    found3 ? section(S.stage3.title, S.stage3.intro, found3) : null,
    section("Start with one observation", S.featured.intro, feature),
    S.stage2 ? section(S.stage2.title, S.stage2.intro, tenList(S.stage2.items)) : null,
    section(S.ten_title || "Ten things most worth knowing", S.ten_intro, tenList(S.ten)),
    section("Explore by lens", "A lens is the unit being described: an IP right, a firm, a place, a country, a month, an industry or a research institution.", lensTiles),
    section("Explore by research question", "The five questions the research will answer after Stage 3. Every observation says which of them it moves closer to, and how.", qTiles),
    section("How to read an observation", S.reading.intro, anatomy, el("h3", { style: { margin: "22px 0 10px" } }, "How strong is the evidence?"), ...paras(S.reading.strength_intro, "muted"), scale));
}

// Stage 3 on one page: how a signal is tested, what the outcomes mean, and every check with the page that made it
function stage3Page() {
  setCrumbs([{ label: "Overview", href: "#/" }, { label: "What Stage 3 found" }]);
  setNav("stage3");
  document.title = "What Stage 3 found · Evidence atlas";
  const T = A.site.stage3;
  const all = revisitsAll();
  const st = { v: "all" };
  const board = el("div");
  const bar = el("div.chipbar", { role: "group", "aria-label": "Show the checks with this outcome" });
  const opts = [["all", "Every outcome"], ...A.verdicts.filter((v) => all.some((r) => r.verdict === v)).map((v) => [v, v])];
  for (const [k, name] of opts) {
    const b = el("button", { type: "button", "aria-pressed": String(st.v === k) },
      k === "all" ? name : verdictTag(k, true), el("span.muted.small", String(k === "all" ? all.length : all.filter((r) => r.verdict === k).length)));
    b.addEventListener("click", () => { st.v = k; [...bar.children].forEach((c) => c.setAttribute("aria-pressed", String(c === b))); draw(); });
    bar.append(b);
  }
  function draw() {
    const rows = all.filter((r) => st.v === "all" || r.verdict === st.v);
    board.replaceChildren(...LENS_ORDER.map((l) => [l, rows.filter((r) => r.lens === l)]).filter(([, g]) => g.length).flatMap(([l, g]) => [
      el("div.group-head", lensChip(l), el("h3", A.lenses[l]?.unit || ""), el("span.muted.small", `${g.length} check${g.length === 1 ? "" : "s"}`)),
      el("div.vboard", g.map((r) => el("div.vrow",
        el("div.vfrom", el("span.vstage", `Stage ${byId[r.id]?.stage ?? 2} found`), el("div", obsLink(r.id), " ", el("strong", r.signal || "")), el("p.small", trim(byId[r.id]?.headline || "", 150))),
        el("div.varrow", { "aria-hidden": "true" }, icon("arrow")),
        el("div.vto", el("span.vstage", "Held together in Stage 3"), el("div", verdictTag(r.verdict)), el("p", inline(r.what)),
          el("a.small.vread", { href: `#/${r.m}` }, `${r.m}: ${trim(byId[r.m].headline, 96)}`))))),
    ]), rows.length ? "" : el("p.muted", "No check has this outcome."));
  }
  draw();
  const words = el("div.tablewrap", el("table.data", el("thead", el("tr", el("th", "Outcome"), el("th", "What it means"), el("th.n", "Checks"))),
    el("tbody", A.verdicts.filter((v) => A.site.verdict_words?.[v]).map((v) => el("tr", el("td", verdictTag(v)), el("td", inline(A.site.verdict_words[v])), el("td.n", String(all.filter((r) => r.verdict === v).length)))))));
  const ex = byId[T.example.id];
  show(el("div.eyebrow", "Stage 3 · many variables together"), el("h1", T.page_title), ...paras(T.lead, "lead"),
    el("div.banner", { style: { margin: "18px 0" } }, icon("info"), el("div", ...paras(T.banner))),
    section("How Stage 3 tests a signal", T.how_intro, journeyDiagram(T.how),
      el("div.dsteps", { style: { marginTop: "18px" } }, T.how.map((s, i) => el("div.dstep", el("div.dn", String(i + 1)), el("div", el("h3", s.title), ...paras(s.text)))))),
    section(T.example.title, T.example.intro,
      el("div.feature",
        el("div.feature-copy", el("div.meta", obsLink(ex.id), lensChip(ex.lens), stageChip(ex)), el("h2", ex.headline), ...paras(T.example.text),
          el("div.row", el("a.btn.primary", { href: `#/${ex.id}` }, `Open ${ex.id}`, icon("arrow")))),
        el("div.feature-viz", chartSlot(ex.chart, { compact: true })))),
    section("What the outcomes mean", T.verdicts_intro, words),
    section("Every signal Stage 3 tested, and what is left of it", T.board_intro, verdictBar(), el("div", { style: { margin: "14px 0 4px" } }, bar), board),
    section(T.structure_title, T.structure_intro, tenList(T.structure)),
    section("What Stage 3 hands on", T.next_intro, el("div.row", el("a.btn.primary", { href: "#/next" }, "The early signals and data gaps", icon("arrow")),
      el("a.btn", { href: "#/observations?stage=3" }, "All Stage 3 observations"))));
}

function observationsPage(params) {
  setCrumbs([{ label: "Overview", href: "#/" }, { label: "Observations" }]);
  setNav("observations");
  const pref = (k, d) => { try { return localStorage.getItem(`atlas.${k}`) || d; } catch { return d; } };
  const keep = (k, v) => { try { localStorage.setItem(`atlas.${k}`, v); } catch { /* storage unavailable: the choice lasts this visit */ } };
  const st = {
    lens: params.get("lens") || "all", q: params.get("q") || "all", about: params.get("about") || "all", stage: params.get("stage") || "all",
    v: params.get("v") || "all", s: params.get("s") || "", view: params.get("view") || pref("view", "list"), group: params.get("group") || pref("group", "lens"),
  };
  const results = el("div.results");
  const count = el("p.result-count", { "aria-live": "polite" });
  const outline = el("nav.outline", { "aria-label": "Jump to a group" });

  const pressGroup = (box, b) => [...box.children].forEach((c) => c.setAttribute("aria-pressed", String(c === b)));
  const lensBar = el("div.chipbar", { role: "group", "aria-label": "Lens" });
  for (const [k, name] of [["all", "All lenses"], ...LENS_ORDER.filter((l) => A.lenses[l]).map((l) => [l, A.lenses[l].name])]) {
    const b = el("button", { type: "button", "aria-pressed": String(st.lens === k) }, k === "all" ? null : el("span.ldot"), name);
    if (k !== "all") b.style.setProperty("--lc", lensColour(k));
    b.addEventListener("click", () => { st.lens = k; pressGroup(lensBar, b); update(); });
    lensBar.append(b);
  }
  const segOf = (label, pairs, key, titles = {}) => {
    const box = el("div.seg", { role: "group", "aria-label": label });
    for (const [k, name] of pairs) {
      const b = el("button", { type: "button", "aria-pressed": String(st[key] === k), title: titles[k] || null }, name);
      b.addEventListener("click", () => { st[key] = k; pressGroup(box, b); if (key === "view" || key === "group") keep(key, k); update(); });
      box.append(b);
    }
    return box;
  };
  const stageSeg = segOf("Stage", [["all", "All stages"], ["1", "Stage 1"], ["2", "Stage 2"], ["3", "Stage 3"]], "stage",
    { 1: `Stage 1: ${STAGE_NAME[1]}`, 2: `Stage 2: ${STAGE_NAME[2]}`, 3: `Stage 3: ${STAGE_NAME[3]}` });
  const about = segOf("What the observation is about", [["all", "All"], ["system", "About the IP system"], ["data", "About the data"]], "about");
  const viewSeg = segOf("Show as", [["list", "List"], ["cards", "Cards"]], "view");
  const groupSeg = segOf("Group by", [["lens", "By lens"], ["stage", "By stage"]], "group");
  const qSel = el("select", { "aria-label": "Research question" }, el("option", { value: "all" }, "Any research question"),
    A.questions.map((q) => el("option", { value: String(q.id) }, `Q${q.id}: ${q.short}`)));
  qSel.value = st.q;
  qSel.addEventListener("change", () => { st.q = qSel.value; update(); });
  const used = new Set(A.observations.flatMap(verdictsOf));
  const vSel = el("select", { "aria-label": "What Stage 3 found" }, el("option", { value: "all" }, "Any Stage 3 outcome"),
    el("option", { value: "later" }, "Tested again in Stage 3"),
    A.verdicts.filter((v) => used.has(v)).map((v) => el("option", { value: v }, `Stage 3: ${v}`)));
  vSel.value = st.v;
  vSel.addEventListener("change", () => { st.v = vSel.value; update(); });
  const search = el("input", { type: "search", placeholder: "Search the observations", "aria-label": "Search the observations", value: st.s });
  search.addEventListener("input", () => { st.s = search.value; update(); });
  const openAll = (open) => results.querySelectorAll("details").forEach((d) => { d.open = open; });

  function groups(list) {
    if (st.group === "stage") {
      return [1, 2, 3].map((k) => ({ key: `s${k}`, title: `Stage ${k}: ${STAGE_NAME[k]}`, chip: el("span.chip.stagechip", `Stage ${k}`), items: list.filter((o) => o.stage === k) }))
        .filter((g) => g.items.length)
        .map((g) => ({ ...g, subs: LENS_ORDER.map((l) => [A.lenses[l]?.name || l, g.items.filter((o) => o.lens === l)]).filter(([, x]) => x.length) }));
    }
    return LENS_ORDER.map((l) => ({ key: l, title: A.lenses[l]?.unit || "", chip: lensChip(l), items: list.filter((o) => o.lens === l) }))
      .filter((g) => g.items.length)
      .map((g) => ({ ...g, subs: [...new Set(g.items.map((o) => `${o.stage}|${o.section}`))].map((k) => {
        const [s, sec] = [k.slice(0, 1), k.slice(2)];
        return [`Stage ${s} · ${sec}`, g.items.filter((o) => String(o.stage) === s && o.section === sec)];
      }) }));
  }
  function update() {
    const words = st.s.toLowerCase().split(/\s+/).filter(Boolean);
    const list = A.observations.filter((o) =>
      (st.lens === "all" || o.lens === st.lens) &&
      (st.q === "all" || o.questions.some((x) => String(x.q) === st.q)) &&
      (st.about === "all" || o.about === st.about) &&
      (st.stage === "all" || String(o.stage) === st.stage) &&
      (st.v === "all" || (st.v === "later" ? o.later?.length : verdictsOf(o).includes(st.v))) &&
      words.every((w) => haystack(o).includes(w)));
    count.textContent = `${list.length} of ${A.observations.length} observations`;
    const gs = groups(list);
    const few = list.length <= 60;
    outline.replaceChildren(...gs.map((g) => el("button", { type: "button", onclick: () => { const d = document.getElementById(`grp-${g.key}`); if (d) { d.open = true; d.scrollIntoView({ block: "start" }); } } },
      g.chip.cloneNode(true), el("span.count", String(g.items.length)))));
    outline.hidden = gs.length < 2;
    results.replaceChildren(...gs.map((g) => el("details.ogroup", { id: `grp-${g.key}`, open: true },
      el("summary", el("span.chev", { "aria-hidden": "true" }, "›"), g.chip, el("h2", g.title), el("span.muted.small", `${g.items.length}`)),
      st.view === "cards"
        ? g.subs.map(([t, items]) => [el("h3.subhead", t.replace(/`/g, "")), el("div.cards", items.map(ocard))])
        : g.subs.map(([t, items]) => sectionGroup(t, items, few || g.subs.length <= 6)))),
    list.length ? "" : el("p.muted", "No observation matches. Try fewer words, or another lens."));
    const p = new URLSearchParams();
    for (const k of ["lens", "q", "about", "stage", "v"]) if (st[k] !== "all") p.set(k, st[k]);
    if (st.s) p.set("s", st.s);
    if (st.view !== "list") p.set("view", st.view);
    if (st.group !== "lens") p.set("group", st.group);
    history.replaceState(null, "", `#/observations${p.toString() ? `?${p}` : ""}`);
  }
  show(
    el("div.eyebrow", "Stages 1, 2 and 3 · every observation"),
    el("h1", "Observations"),
    ...paras(A.site.observations_intro, "lead"),
    el("div.filters",
      lensBar,
      el("div.filter-row", search, qSel, vSel),
      el("div.filter-row", stageSeg, about),
      el("div.filter-row.tools", count, el("span.spacer"), el("span.muted.small", "Group"), groupSeg, el("span.muted.small", "Show"), viewSeg,
        el("button.linkbtn", { type: "button", onclick: () => openAll(true) }, "Open all"), el("button.linkbtn", { type: "button", onclick: () => openAll(false) }, "Close all"))),
    outline,
    results);
  update();
}
const hayCache = new Map();
/** The text an observation is searched by. */
function haystack(o) {
  if (!hayCache.has(o.id)) hayCache.set(o.id, `${o.id} ${o.headline} ${plain(o.statement)} ${(o.points || []).map(plain).join(" ")} ${o.section} ${(o.revisits || []).map((r) => `${r.id} ${r.signal || ""}`).join(" ")}`.toLowerCase());
  return hayCache.get(o.id);
}

function trailStep(n, iconName, title, summary, body, open = false) {
  return el("div.tstep",
    el("div.ticon", icon(iconName)),
    el("details", open ? { open: true } : {},
      el("summary", el("span.tnum", `Step ${n} of 4`), el("h3", title), el("span.tsum", summary), el("span.chev", { "aria-hidden": "true" }, "›")),
      el("div.tbody", body)));
}
const nfmt = new Intl.NumberFormat("en-AU");
function bytes(b) {
  return b >= 1e9 ? `${(b / 1e9).toFixed(1)} GB` : b >= 1e6 ? `${(b / 1e6).toFixed(1)} MB` : `${Math.max(1, Math.round(b / 1e3))} kB`;
}
function sourceCard(s, compact = false) {
  return el("div.src",
    el("h5", s.url ? el("a", { href: s.url, rel: "noopener noreferrer", target: "_blank" }, s.title) : s.title),
    el("p", s.derived ? `Built by this project, ${s.publisher.replace(/^(built|compiled) here /, "")}.` : `Published by ${s.publisher}.`, s.coverage ? ` ${s.coverage}.` : ""),
    compact ? null : el("div.meta", s.licence ? el("span.tag-pill", `Licence: ${s.licence}`) : null, s.fetched ? el("span.tag-pill", `Copied ${longDate(s.fetched)}`) : null, el("span.tag-pill", `${s.tables.length} table${s.tables.length === 1 ? "" : "s"}`)));
}
function longDate(iso) {
  const d = new Date(`${iso}T00:00:00`);
  return d.toLocaleDateString("en-AU", { day: "numeric", month: "long", year: "numeric" });
}
function tablesTable(sources) {
  const rows = sources.flatMap((s) => s.tables.map((t) => [s, t]));
  const t = el("table.data", el("thead", el("tr", el("th", "Table"), el("th.n", "Rows"), el("th", "Kept in"), el("th.n", "Size"), el("th", "Fingerprint"))),
    el("tbody", rows.map(([s, t]) => el("tr",
      el("td", `${s.id}/${t.table}`, t.describe ? el("div.muted.small", t.describe) : null),
      el("td.n", t.rows != null ? nfmt.format(t.rows) : "–"),
      el("td", el(`span.tag-pill.where-${t.where}`, t.where === "repo" ? "The repository" : "Cloud storage (R2)")),
      el("td.n", bytes(t.bytes)),
      el("td", el("span.fingerprint", { title: "The first 12 characters of the file's SHA-256 fingerprint, recorded in data/manifest.json" }, t.sha256))))));
  return el("div.tablewrap", t);
}

/** For a Stage 3 page: what Stage 2 found, what was held together, and what is left, as three linked steps. */
function chainBlock(o) {
  const seen = new Set();
  const from = (o.revisits || []).filter((r) => byId[r.id] && !seen.has(r.id) && seen.add(r.id));
  return el("section.chain", { "aria-label": "How this observation follows from the earlier stages" },
    el("div.clink",
      el("span.ctag", el("b", "1"), from.some((r) => byId[r.id].stage === 1) && !from.some((r) => byId[r.id].stage === 2) ? "Stage 1 found" : "Stage 2 found"),
      from.length
        ? el("ul", from.map((r) => el("li", obsLink(r.id), " ", el("span", r.signal ? r.signal : trim(byId[r.id].headline, 110)))))
        : el("p", "A question of structure: which measures repeat each other, and whether there are distinct groups.")),
    el("div.carrow", { "aria-hidden": "true" }, icon("arrow")),
    el("div.clink",
      el("span.ctag", el("b", "2"), "Stage 3 held together"),
      o.held?.length ? el("div.held", o.held.map((h) => el("span.chip", inline(h)))) : el("p", "Nothing held: a description of how the measures relate.")),
    el("div.carrow", { "aria-hidden": "true" }, icon("arrow")),
    el("div.clink.cres",
      el("span.ctag", el("b", "3"), "What is left"),
      (o.revisits || []).length
        ? el("ul.vlist", o.revisits.map((r) => el("li", verdictTag(r.verdict, true), " ", el("span", r.signal || r.id))))
        : el("p", "See the observation below.")));
}

function observationPage(id) {
  const o = byId[id];
  const L = A.lenses[o.lens] || { name: o.lens };
  const i = A.observations.indexOf(o);
  setCrumbs([{ label: "Observations", href: "#/observations" }, { label: L.name, href: `#/lens/${o.lens}` }, { label: o.id }]);
  setNav("observations");
  document.title = `${o.id}: ${o.headline} · Evidence atlas`;

  const head = el("header.obs-head",
    el("div.meta", el("span.id", o.id), lensChip(o.lens), stageChip(o), el("span", o.section.replace(/`/g, "")), strengthBadge(o.strength), aboutLabel(o)),
    el("h1", o.headline),
    markdownTools(o));
  const chain = o.stage === 3 ? chainBlock(o) : null;
  const box = el("section.obs-box", { "aria-label": `Observation ${o.id}` },
    el("div.obs-label", icon("eye"), `Observation ${o.id} · ${o.strength}`),
    el("p.statement", inline(o.statement)),
    o.points?.length ? el("ul", o.points.map((p) => el("li", inline(p)))) : null);
  const update = o.later?.length ? el("section.s3update", { "aria-label": "What Stage 3 found" },
    el("div.s3label", icon("route"), o.later.length === 1 ? "Stage 3 tested this with other factors held together" : `Stage 3 tested this ${o.later.length} ways, with other factors held together`),
    o.later.map((x) => el("div.s3item",
      el("div", verdictTag(x.verdict)),
      el("div", el("p", inline(x.what)), el("a.vread", { href: `#/${x.id}` }, `Read ${x.id}: ${trim(byId[x.id].headline, 110)}`))))) : null;
  const figures = o.figures?.length ? el("div.figures", o.figures.map((f) => el("div.figure", el("strong", f.value), el("span", inline(f.label))))) : null;
  const chart = o.chart ? chartSlot(o.chart) : null;
  const verdicts = o.verdicts?.length ? el("section.block",
    el("h2", icon("check"), "Signal by signal"),
    el("p.block-intro", "Each comparison as Stage 2 measured it (raw), then with its other factors held together, and the outcome."),
    el("div.tablewrap", el("table.data.vtable",
      el("thead", el("tr", el("th", { scope: "col" }, "What was compared"), el("th", { scope: "col" }, "Raw, then held together"), el("th", { scope: "col" }, "Outcome"))),
      el("tbody", o.verdicts.map((v) => el("tr", el("td", inline(v.signal)), el("td", inline(v.detail || "")), el("td", verdictTag(v.verdict)))))))) : null;

  const intro = {
    1: "Stage 1 answers none of the five questions. This is how the observation prepares the ground for them.",
    2: "Stage 2 answers none of the five questions either: it finds which measures go together. This is how the association prepares the ground for them.",
    3: "Stage 3 answers none of the five questions either: it tests which of Stage 2's signals survive with their other factors held together. This is how the result prepares the ground for them.",
  };
  const why = el("section.block",
    el("h2", icon("compass"), "How this moves the research forward"),
    el("p.block-intro", intro[o.stage]),
    el("div.qlist", o.questions.map((q) => {
      const Q = A.questions.find((x) => x.id === q.q);
      return el("div.qitem", el("a.qn", { href: `#/question/${q.q}` }, `Q${q.q}`), el("div", el("h3", Q.title), el("p", inline(q.how))));
    })),
    editorialNote("Linking an observation to a question is the analyst's guide to where it may help. It is not a finding."));

  // the four steps of the trail
  const srcs = o.sources.map((s) => A.sources[s]).filter(Boolean);
  const publishers = [...new Set(srcs.filter((s) => !s.derived).map((s) => s.publisher))];
  const pubText = publishers.length <= 3 ? publishers.join(", ").replace(/, ([^,]*)$/, " and $1") : `${publishers.slice(0, 2).join(", ")} and ${publishers.length - 2} more publishers`;
  const step1 = trailStep(1, "source", "Where the data came from",
    `${srcs.length} source${srcs.length === 1 ? "" : "s"}, published by ${pubText}`,
    [el("p", "Every number here starts in data that a public body published. The project downloads each one as published; nothing is typed in by hand."),
      el("div.srclist", srcs.map((s) => sourceCard(s)))]);
  const tables = srcs.reduce((n, s) => n + s.tables.length, 0);
  const inR2 = srcs.flatMap((s) => s.tables).filter((t) => t.where === "r2").length;
  const step2 = trailStep(2, "box", "How it is kept",
    `${tables} tidy table${tables === 1 ? "" : "s"} from these sources, ${inR2} of them large enough to live in cloud storage`,
    [...paras(A.site.storage_text),
      el("details.more", el("summary", icon("table"), "The tables behind these sources"), el("div", tablesTable(srcs))),
      el("p.small.muted", inline(`The lens table this observation reads, ${lower(L.name)} (${lower(L.unit)}), is not stored: it is rebuilt from these tables in minutes by the project's build code, so it always matches them.`))]);
  const prep = [...(o.prep || []).map((p) => el("div.prepitem", el("p", inline(p.what)), el("p.why", el("strong", "Why"), ...inline(p.why))))];
  const lensRepairs = (L.repairs || []).map((p) => el("div.prepitem", el("p", inline(p.what)), el("p.why", el("strong", "Why"), ...inline(p.why))));
  const step3 = trailStep(3, "tool", "How it was prepared",
    `${(o.prep || []).length} step${(o.prep || []).length === 1 ? "" : "s"} for this observation, on the ${lower(L.name)} lens (${lower(L.unit)})`,
    [el("h4", "For this observation"), el("div.prep", prep),
      lensRepairs.length ? el("details.more", el("summary", icon("tool"), `Repairs made to the ${lower(L.name)} lens before any observation (${lensRepairs.length})`), el("div", el("div.prep", lensRepairs))) : null]);
  const step4 = trailStep(4, "route", "From the data to the observation",
    `${o.steps.length} reasoning steps. The steps are not findings; only the last box is.`,
    [el("ol.steps", o.steps.map((s) => el("li", el("span.slabel", "Step"), el("span", inline(s)))),
      el("li.result", el("div.resultbox", el("span.slabel", `Which gives observation ${o.id}`), el("span", inline(o.statement)))))], true);
  const trail = el("section.block", el("h2", icon("route"), "Follow the evidence"),
    el("p.block-intro", "From the publisher's file to this observation, in four steps. Open any step for the detail."),
    el("div.trail", step1, step2, step3, step4));

  const honesty = el("section.block", el("h2", icon("alert"), "Assumptions and limits"),
    el("div.notes", o.assumptions.map((a) => note("assume", a)), o.limits.map((a) => note("limit", a))));
  const done = o.later?.length ? note("done", `Stage 3 has since tested this with other factors held: ${o.later.map((x) => `{${x.id}}, ${x.verdict}`).join("; ")}. The box under the observation says what was left.`) : null;
  const next = el("section.block", el("h2", icon("arrow"), "What happens next"), el("div.notes", note("next", o.next), done));

  const nbCharts = o.notebook_charts || [];
  const analysts = el("section.block",
    el("details.more",
      el("summary", icon("book"), "For analysts: the notebook's own words and charts"),
      el("div",
        el("p.small.muted", inline(`Quoted from section ${o.section.replace(/`/g, "")} of the Stage ${o.stage} notebook. Reading it is optional: everything above says the same in plain English.`)),
        notebookMarkdown(o.original),
        ...nbCharts.map((c) => el("figure.nbimg", el("img", { src: c.src, alt: `A chart from the notebook, above observation ${o.id}`, loading: "lazy", decoding: "async" }), el("figcaption", "The chart as drawn in the notebook."))),
        el("p.small", el("a", { href: A.notebooks?.[o.stage] || A.notebook, rel: "noopener noreferrer", target: "_blank" }, "Open the notebook on GitHub"), " · the code that builds every lens is in analysis/eda/build.py."))));

  const related = (o.related || []).filter((r) => byId[r]);
  const rel = related.length ? el("section.block", el("h2", "Related observations"), el("div.olist.boxed", related.map((r) => orow(byId[r])))) : null;

  const prev = A.observations[i - 1], nxt = A.observations[i + 1];
  const pager = el("nav.pager", { "aria-label": "Previous and next observations" },
    prev ? el("a", { href: `#/${prev.id}`, rel: "prev" }, el("small", `← ${prev.id}`), prev.headline) : el("span"),
    nxt ? el("a.next", { href: `#/${nxt.id}`, rel: "next" }, el("small", `${nxt.id} →`), nxt.headline) : null);
  const keys = el("p.keys", "Keys: ", el("kbd", "←"), " and ", el("kbd", "→"), " move between observations; ", el("kbd", "/"), " searches.");

  const sibs = A.observations.filter((x) => x.stage === o.stage && x.section === o.section && x.lens === o.lens);
  const terms = [...new Set([...(o.terms || []), ...[...JSON.stringify(o).matchAll(/\[\[([^\]|]+)/g)].map((m) => m[1])])].filter((t) => A.glossary[t]);
  const rail = el("aside.rail", { "aria-label": "Explainers and facts about this observation" },
    el("section",
      el("div.glance",
        el("h2", "At a glance"),
        el("dl",
          el("dt", "Lens"), el("dd", lensChip(o.lens)),
          el("dt", "Unit"), el("dd", L.unit),
          el("dt", "About"), el("dd", o.about === "data" ? "The data themselves" : "The IP system"),
          el("dt", "Stage"), el("dd", `${o.stage} of 3 (${STAGE_NAME[o.stage]})`)),
        el("h2", { style: { marginTop: "14px" } }, "Strength of evidence"),
        el("div.scale", ["descriptive", "observational", "causal", "projected"].map((s) => el(`span${s === o.strength ? ".on" : ""}`, s === o.strength ? `${s} (this observation)` : s))),
        el("p.small.muted", { style: { marginTop: "8px" } }, o.strength === "descriptive" ? "Descriptive: what the data show, not why." : "Observational: measures go together; other explanations remain, and it is not a cause.", " Causal claims need designs that come after Stage 3."))),
    sibs.length > 1 ? el("section.sibs",
      el("h2", "In this section"),
      el("p.small.muted", `Stage ${o.stage} · ${o.section.replace(/`/g, "")}`),
      el("ol", sibs.map((x) => el("li", x.id === o.id
        ? el("span.here", { "aria-current": "page" }, el("span.id", x.id), el("span", trim(x.headline, 80)))
        : el("a", { href: `#/${x.id}` }, el("span.id", x.id), el("span", trim(x.headline, 80))))))) : null,
    terms.length ? el("section", el("h2", "Explainers"), ...terms.map((t) => el("div.explainer", el("h3", icon("info"), A.glossary[t].title), ...paras(A.glossary[t].short)))) : null);

  show(el("div.obs-page",
    el("article.obs-main", head, chain, box, update, figures, chart, verdicts, why, trail, honesty, next, analysts, rel, pager, keys),
    rail));
}

function lensesPage() {
  setCrumbs([{ label: "Overview", href: "#/" }, { label: "Lenses" }]);
  setNav("lenses");
  const S = A.site.lenses_page;
  show(
    el("div.eyebrow", "Units of analysis"), el("h1", "Lenses"), ...paras(S.intro, "lead"),
    el("div.card.flat", { style: { margin: "18px 0" } }, el("h3", "Why lenses?"), ...paras(S.why)),
    el("div.lens-tiles", LENS_ORDER.filter((l) => A.lenses[l]).map((l) => {
      const L = A.lenses[l];
      const count = A.observations.filter((o) => o.lens === l).length;
      const t = el("a.ltile", { href: `#/lens/${l}` }, el("h3", L.name), el("p", L.unit), el("p", trim(plain(L.description), 150)), el("small", `${L.rows || ""} · ${count} observations`));
      t.style.setProperty("--lc", lensColour(l));
      return t;
    })));
}

function lensPage(l) {
  const L = A.lenses[l];
  setCrumbs([{ label: "Lenses", href: "#/lenses" }, { label: L.name }]);
  setNav("lenses");
  const obs = A.observations.filter((o) => o.lens === l);
  const stages = [1, 2, 3].filter((k) => obs.some((o) => o.stage === k));
  const srcs = (L.sources || []).map((s) => A.sources[s]).filter(Boolean);
  const head = el("header",
    el("div.eyebrow", lensChip(l, false), "Lens"),
    el("h1", L.name), el("p.lead", L.unit),
    el("div.figures", (L.facts || []).map((f) => el("div.figure", el("strong", f.value), el("span", f.label)))));
  const outline = el("nav.outline", { "aria-label": "Jump to a stage" }, stages.map((k) => el("button", { type: "button", onclick: () => document.getElementById(`st-${k}`)?.scrollIntoView({ block: "start" }) },
    el("span.chip.stagechip", `Stage ${k}`), STAGE_NAME[k], el("span.count", String(obs.filter((o) => o.stage === k).length)))));
  show(head,
    el("div.prose", ...paras(L.description)),
    L.questions?.length ? el("div.row", { style: { margin: "10px 0 0" } }, el("span.muted.small", "Mainly informs"), ...L.questions.map(qChip)) : "",
    section(`Its ${obs.length} observations`, "In the order the analysis made them: each measure on its own (Stage 1), then pairs (Stage 2), then several at once (Stage 3). Each notebook section opens and closes.",
      outline,
      ...stages.flatMap((k) => {
        const mine = obs.filter((o) => o.stage === k);
        const secs = [...new Set(mine.map((o) => o.section))];
        return [el("h2.stage-h", { id: `st-${k}` }, `Stage ${k}: ${STAGE_NAME[k]}`, el("span.muted.small", ` · ${mine.length} observation${mine.length === 1 ? "" : "s"}`)),
          ...secs.map((s) => sectionGroup(s, mine.filter((o) => o.section === s), secs.length <= 8))];
      })),
    section("Built from", "Each source as its publisher released it. Where the data come from lists every table, where it is kept and its fingerprint.", el("div.srclist", srcs.map((s) => sourceCard(s)))),
    L.repairs?.length ? section("Repairs made before any observation", "Problems found while profiling, fixed in the lens and recorded in a decision record. Each says why.",
      el("div.prep", L.repairs.map((p) => el("div.prepitem", el("p", inline(p.what)), el("p.why", el("strong", "Why"), ...inline(p.why), p.adr ? el("span.muted", ` (ADR ${p.adr})`) : null))))) : "",
    L.limits?.length ? section("Limits of this lens", null, el("div.notes", L.limits.map((x) => note("limit", x)))) : "");
}

function questionsPage() {
  setCrumbs([{ label: "Overview", href: "#/" }, { label: "Research questions" }]);
  setNav("questions");
  const S = A.site.questions_page;
  show(el("div.eyebrow", "The purpose"), el("h1", "Research questions"), ...paras(S.intro, "lead"),
    el("div.banner", { style: { margin: "18px 0" } }, icon("info"), el("div", ...paras(S.caution))),
    el("div.grid", A.questions.map((q) => {
      const count = A.observations.filter((o) => o.questions.some((x) => x.q === q.id)).length;
      return el("a.card", { href: `#/question/${q.id}`, style: { textDecoration: "none", color: "inherit", display: "block" } },
        el("div.meta", el("span.chip.qchip", `Question ${q.id}`), el("span", `${count} observations bear on it`)),
        el("h2", { style: { marginTop: "8px" } }, q.title), ...paras(q.text, "muted"));
    })));
}

function questionPage(id) {
  const q = A.questions.find((x) => x.id === Number(id));
  setCrumbs([{ label: "Research questions", href: "#/questions" }, { label: `Question ${q.id}` }]);
  setNav("questions");
  const bearing = A.observations.filter((o) => o.questions.some((x) => x.q === q.id));
  const items = (n) => bearing.filter((o) => o.stage === n).map((o) => el("div.qitem", obsLink(o.id), el("div",
    el("h3", el("a", { href: `#/${o.id}` }, o.headline)),
    o.stage === 3 ? el("div.meta", { style: { margin: "2px 0 4px" } }, verdictsOf(o).map((v) => verdictTag(v, true))) : null,
    el("p", inline(o.questions.find((x) => x.q === q.id).how)))));
  const signals = (A.site.next.signals || []).filter((l) => l.questions.includes(q.id));
  const count = (n) => bearing.filter((o) => o.stage === n).length;
  show(
    el("div.eyebrow", `Question ${q.id} of 5`), el("h1", q.title), ...paras(q.text, "lead"),
    q.sub?.length ? section("What the research goal asks under it", null, el("ul.prose", q.sub.map((s) => el("li", s)))) : "",
    signals.length ? section("Early signals that bear on it", "From Stage 3's table of early signals: associations that survived their third factors held together, drafted for the research owner's review. Not answers.",
      el("div.qlist", signals.map((l) => el("div.qitem", el("span.qn", `#${A.site.next.signals.indexOf(l) + 1}`), el("div", el("h3", inline(l.signal)), el("p.small", el("strong", "Strength: "), ...inline(l.strength)), el("p.small", "From ", ...l.ids.flatMap((x, i) => [i ? ", " : "", obsLink(x)])), el("p.small", el("strong", "Suggested next step: "), ...inline(l.next))))))) : "",
    count(3) ? section(`What Stage 3 found that bears on it (${count(3)})`, "Stage 2's signals tested with their other factors held together, and the structure among places, countries, industries and institutions.", el("div.qlist", items(3)), editorialNote("These links are the analyst's guide to where each observation may help. They are not findings.")) : "",
    section(`What Stage 2 found that bears on it (${count(2)})`, "Pairs of measures that go together, held in a second period or sample: associations, not answers.", el("div.qlist", items(2))),
    section(`What Stage 1 found that bears on it (${count(1)})`, "Descriptive observations: groundwork, not answers.", el("div.qlist", items(1))),
    q.reach?.length ? section("What is out of reach for now", null, el("div.notes", q.reach.map((x) => note("limit", x)))) : "");
}

function dataPage() {
  setCrumbs([{ label: "Overview", href: "#/" }, { label: "Where the data come from" }]);
  setNav("data");
  const D = A.site.data_page;
  const all = Object.values(A.sources);
  const lensOf = {};
  for (const [l, L] of Object.entries(A.lenses)) for (const s of L.sources || []) (lensOf[s] ||= []).push(l);
  const filter = el("input", { type: "search", placeholder: "Filter the sources", "aria-label": "Filter the sources" });
  const list = el("div.srclist");
  const draw = () => {
    const w = filter.value.toLowerCase();
    list.replaceChildren(...all.filter((s) => `${s.id} ${s.title} ${s.publisher}`.toLowerCase().includes(w)).map((s) => {
      const rows = s.tables.reduce((n, t) => n + (t.rows || 0), 0);
      return el("details.more", { id: `src-${s.id}` },
        el("summary", el("span", { style: { flex: 1 } }, s.title, el("span.muted.small", ` · ${s.publisher}`)), el("span.tag-pill", `${s.tables.length} tables`)),
        el("div", sourceCard(s), el("div.row", { style: { margin: "8px 0" } }, el("span.muted.small", "Lenses:"), ...(lensOf[s.id] || []).map((l) => lensChip(l)), lensOf[s.id] ? "" : el("span.muted.small", "outside the lenses for now")),
          el("p.small.muted", `${nfmt.format(rows)} rows in all.`), tablesTable([s])));
    }));
  };
  filter.addEventListener("input", draw);
  draw();
  show(el("div.eyebrow", "Provenance"), el("h1", "Where the data come from"), ...paras(D.intro, "lead"),
    section("The journey of every number", null, journeyDiagram(D.journey), el("div.dsteps", { style: { marginTop: "18px" } }, D.journey.map((s, i) => el("div.dstep", el("div.dn", String(i + 1)), el("div", el("h3", s.title), ...paras(s.text)))))),
    section(`The ${all.length} sources`, D.sources_intro, el("div.filter-row", { style: { marginBottom: "12px" } }, filter), list));
}
function journeyDiagram(steps) {
  const NS = "http://www.w3.org/2000/svg";
  const w = 1100, h = 120, n = steps.length, gap = 22, bw = (w - gap * (n - 1)) / n;
  const svg = document.createElementNS(NS, "svg");
  svg.setAttribute("viewBox", `0 0 ${w} ${h}`);
  svg.setAttribute("class", "journey-svg");
  svg.setAttribute("role", "img");
  svg.setAttribute("aria-label", `The journey of a number: ${steps.map((s) => s.title).join(", then ")}.`);
  const mk = (tag, attrs, text) => { const e = document.createElementNS(NS, tag); for (const [k, v] of Object.entries(attrs)) e.setAttribute(k, v); if (text) e.textContent = text; return e; };
  const defs = mk("defs", {});
  const marker = mk("marker", { id: "arrowhead", viewBox: "0 0 10 10", refX: 9, refY: 5, markerWidth: 7, markerHeight: 7, orient: "auto-start-reverse" });
  marker.append(mk("path", { d: "M0 0 10 5 0 10z" }));
  defs.append(marker);
  svg.append(defs);
  steps.forEach((s, i) => {
    const x = i * (bw + gap);
    const g = mk("g", { class: `node${i === n - 1 ? " hi" : ""}` });
    g.append(mk("rect", { x, y: 14, width: bw, height: 92, rx: 12 }));
    g.append(mk("text", { x: x + 12, y: 44 }, s.short || s.title));
    const words = (s.sub || "").split(" ");
    let line = "", yy = 66;
    for (const wd of words) {
      if ((line + wd).length > Math.floor(bw / 7)) { g.append(mk("text", { x: x + 12, y: yy, class: "sub" }, line.trim())); line = ""; yy += 16; }
      line += `${wd} `;
    }
    if (line.trim()) g.append(mk("text", { x: x + 12, y: yy, class: "sub" }, line.trim()));
    svg.append(g);
    if (i < n - 1) svg.append(mk("path", { class: "arrow", d: `M${x + bw + 2} 60 h${gap - 6}` }));
  });
  return el("div.card.flat", { style: { padding: "12px", overflowX: "auto" } }, svg);
}

function limitsPage() {
  setCrumbs([{ label: "Overview", href: "#/" }, { label: "Limits and assumptions" }]);
  setNav("limits");
  const Lm = A.site.limits;
  show(el("div.eyebrow", "Honesty"), el("h1", "Limits and assumptions"), ...paras(Lm.intro, "lead"),
    section(Lm.cannot_title, null, el("div.notes", Lm.cannot.map((x) => el("div.note.limit", icon("alert"), el("div", el("span.tag", x.title), ...paras(x.text)))))),
    section("Assumptions made across the work", "Each observation also lists its own. These hold everywhere.", el("div.notes", Lm.assumptions.map((x) => note("assume", x)))),
    section("Where the data are weakest", Lm.weak_intro, el("div.notes", Lm.weak.map((x) => el("div.note.limit", icon("link"), el("div", el("span.tag", x.title), ...paras(x.text)))))),
    section("Corrections made along the way", Lm.corrections_intro, el("div.tablewrap", el("table.data", el("thead", el("tr", el("th", "When"), el("th", "What was wrong"), el("th", "Now"))),
      el("tbody", Lm.corrections.map((c) => el("tr", el("td", c.when), el("td", inline(c.what)), el("td", inline(c.now)))))))));
}

function nextPage() {
  setCrumbs([{ label: "Overview", href: "#/" }, { label: "What comes next" }]);
  setNav("next");
  const N = A.site.next;
  const stages = el("div.grid.g3", N.stages.map((s) => el("div.card", { style: s.now ? { borderColor: "var(--obs-line)" } : {} },
    el("div.meta", el("span.chip", s.when)), el("h2", { style: { marginTop: "8px" } }, s.name), el("p", el("strong", "Asks: "), inline(s.asks)),
    ...paras(s.how, "small"), el("p.small", el("strong", "For example: "), inline(s.example)), el("p.small", el("strong", "What it adds: "), inline(s.adds)), el("p.small.muted", el("strong", "Finished when: "), inline(s.done)))));
  const signals = el("div.tablewrap", el("table.data.signals", el("thead", el("tr", el("th.n", "#"), el("th", "Signal"), el("th", "Evidence"), el("th", "Strength"), el("th", "Questions"), el("th", "Suggested next step"))),
    el("tbody", N.signals.map((x, i) => el("tr", el("td.n", String(i + 1)), el("td", inline(x.signal)), el("td", x.ids.flatMap((y, j) => [j ? " " : "", obsLink(y)])), el("td", inline(x.strength)), el("td", x.questions.map(qChip)), el("td", inline(x.next)))))));
  const gaps = el("div.tablewrap", el("table.data", el("thead", el("tr", el("th", "Gap"), el("th", "Why it matters"), el("th", "Possible source"), el("th", "Cost"))),
    el("tbody", N.data_gaps.map((g) => el("tr", el("td", el("strong", inline(g.gap))), el("td", inline(g.why)), el("td", inline(g.source)), el("td", inline(g.cost)))))));
  show(el("div.eyebrow", "The road ahead"), el("h1", "What comes next"), ...paras(N.intro, "lead"),
    section("Three stages, then the questions", null, stages),
    section(N.signals_title, N.signals_intro, signals, N.recorded ? el("div.notes", { style: { marginTop: "12px" } }, el("div.note.limit", icon("flag"), el("div", el("span.tag", "Recorded, not carried"), el("p", inline(N.recorded))))) : null),
    section("Gaps in the data", N.gaps_intro, gaps),
    section("Puzzles kept in view", N.puzzles_intro, el("div.notes", N.puzzles.map((p) => el("div.note.next", icon("flag"), el("div", el("span.tag", "Unexplained"), el("p", inline(p))))))),
    section("Questions waiting on someone else", N.open_intro, el("div.grid.g2",
      el("div.card.flat", el("h3", "For the research owner"), el("ul", N.owner.map((x) => el("li", inline(x))))),
      el("div.card.flat", el("h3", "For IP Australia"), el("ul", N.ipa.map((x) => el("li", inline(x))))))),
    section("After Stage 3", null, el("ol.prose", N.after.map((x) => el("li", inline(x))))));
}

// the review against IP Australia's published evidence (ADR 0024, 0025): a page of its own, read from atlas.audit;
// the observation pages are left as they are
const VERDICT_CLASS = { corroborated: "ok", consistent: "near", qualified: "near", disputed: "warn", contradicted: "bad", "not testable": "none" };
function verdictPill(label, category) {
  return el(`span.verdict.v-${VERDICT_CLASS[category] || "none"}`, label);
}
function auditPage() {
  setCrumbs([{ label: "Overview", href: "#/" }, { label: "Checked against IP Australia" }]);
  setNav("audit");
  document.title = "Checked against IP Australia · Evidence atlas";
  const R = A.audit;
  const figures = el("div.figures", R.stats.map((s) => el("div.figure", el("strong", s.value), el("span", s.label))));
  const brief = el("ul.prose", R.in_brief.map((p) => el("li", inline(p))));
  const method = el("div.dsteps", R.method.map((s, i) => el("div.dstep", el("div.dn", String(i + 1)), el("div", el("h3", s.title), ...paras(s.text)))));
  const words = el("div.tablewrap", el("table.data", el("thead", el("tr", el("th", "Verdict"), el("th", "What it means"))),
    el("tbody", Object.entries(R.verdict_words).map(([k, t]) => el("tr", el("td", verdictPill(k.charAt(0).toUpperCase() + k.slice(1), k)), el("td", inline(t)))))));
  const gap = (m) => (m.gap_pct != null ? `${fmtNum(m.gap_pct)}%` : m.gap_pts != null ? `${fmtNum(m.gap_pts)} points` : "–");
  const measures = el("div.tablewrap", el("table.data",
    el("thead", el("tr", el("th", "What was compared"), el("th", "Years"), el("th.n", "Figures"), el("th.n", "Agree"), el("th.n", "Largest gap"))),
    el("tbody", R.measures.map((m) => el("tr", el("td", m.label), el("td", m.years), el("td.n", String(m.figures)), el("td.n", String(m.agree)), el("td.n", gap(m)))))));

  const order = ["corroborated", "consistent", "qualified", "disputed", "contradicted"];
  const byCat = order.map((c) => [c, R.verdicts.filter((v) => v.category === c)]).filter(([, vs]) => vs.length);
  const tested = byCat.flatMap(([c, vs]) => [
    el("h3", { style: { margin: "22px 0 10px" } }, verdictPill(c.charAt(0).toUpperCase() + c.slice(1), c), el("span.muted.small", { style: { marginLeft: "8px" } }, `${vs.length} observation${vs.length === 1 ? "" : "s"}`)),
    el("div.qlist", vs.map((v) => el("div.qitem", obsLink(v.id),
      el("div",
        el("h3", el("a", { href: `#/${v.id}` }, byId[v.id]?.headline || v.id)),
        el("p", verdictPill(v.label, v.category)),
        ...paras(v.note),
        el("details.more", el("summary", icon("book"), "The record's evidence"),
          el("div", el("p.small", inline(v.evidence)), el("p.small", el("strong", "What follows: "), ...inline(v.follows)))))))),
  ]);
  const untested = el("div.grid.g2", R.untestable.map((g) => el("div.card.flat",
    el("div.meta", verdictPill("Not testable", "not testable"), el("span.muted.small", `${g.ids.length}`)),
    el("h3", { style: { marginTop: "8px" } }, g.why), el("div.meta", g.ids.map(obsLink)))));

  const findings = el("div.grid", R.findings.map((d) => el("div.card",
    el("div.meta", el("span.chip", d.id), ...(d.affects.length ? d.affects.map(obsLink) : [el("span.muted.small", "No observation affected")])),
    el("h3", { style: { marginTop: "8px" } }, d.title), ...paras(d.text),
    el("p", el("strong", "What it means: "), ...inline(d.means)),
    d.now ? el("div.note.next", icon("info"), el("div", el("span.tag", `Since then · ${d.status}`), ...paras(d.now))) : null,
    d.chart ? chartSlot(d.chart, { origin: "audit" }) : null)));
  const open = (x) => ["Still open", "Not covered"].includes(x.status);
  const since = R.since ? el("div.notes", R.since.map((x) => el(`div.note.${open(x) ? "limit" : "done"}`,
    icon(open(x) ? "alert" : "info"), el("div", el("span.tag", x.status), el("h3", { style: { margin: "2px 0 6px" } }, x.title), ...paras(x.text))))) : null;

  const conclusions = el("div.tablewrap", el("table.data",
    el("thead", el("tr", el("th", ""), el("th", "IP Australia concludes"), el("th", "How strongly it says so"), el("th", "What Stage 1 adds"))),
    el("tbody", R.conclusions.map((c) => el("tr", el("td", c.id), el("td", inline(c.claim)), el("td", inline(c.strength)), el("td", inline(c.adds)))))));
  const questions = el("div.qlist", R.questions.map((q) => el("div.qitem", el("span.qn", q.id), el("div", el("p", inline(q.text))))));

  show(el("div.eyebrow", R.eyebrow), el("h1", R.title), ...paras(R.lead, "lead"),
    el("div.banner", { style: { margin: "18px 0" } }, icon("info"), el("div", ...paras(R.banner))),
    figures,
    section("In brief", null, brief),
    since ? section("Since the review", R.since_intro, since) : null,
    section("How the check was done", null, method, el("h3", { style: { margin: "22px 0 10px" } }, "The verdicts"), words),
    section("How close the figures are", R.closeness_intro, chartSlot("audit-closeness", { origin: "audit" }),
      el("h3", { style: { margin: "22px 0 10px" } }, "By kind of figure"), ...paras(R.measures_intro, "muted"), measures),
    section("Four things that do not agree", null, findings),
    section("Every observation, and how it stands", "Each verdict is read from the review's record; open one to see IP Australia's evidence as the record gives it.",
      chartSlot("audit-verdicts", { origin: "audit" }), ...tested,
      el("h3", { style: { margin: "26px 0 10px" } }, `Not testable from IP Australia's publications (${R.untestable.reduce((n, g) => n + g.ids.length, 0)})`),
      ...paras(R.untestable_intro, "muted"), untested),
    section("What IP Australia concludes, and what Stage 1 adds", R.conclusions_intro, conclusions),
    section("What changes, and what does not", R.changes_intro, el("ul.prose", R.changes.map((x) => el("li", inline(x))))),
    section("Questions put to IP Australia", R.questions_intro, questions),
    section("Limits of this check", null, el("div.notes", R.limits.map((x) => el("div.note.limit", icon("alert"), el("div", el("span.tag", x.title), ...paras(x.text)))))),
    el("p.small.muted", { style: { marginTop: "26px" } }, "The full record: ",
      el("a", { href: R.record, rel: "noopener noreferrer", target: "_blank" }, "the audit"), " and ",
      el("a", { href: R.adr, rel: "noopener noreferrer", target: "_blank" }, "the decision record (ADR 0024)"), `, as at ${longDate(R.as_at)}.`));
}
function fmtNum(v) {
  return new Intl.NumberFormat("en-AU", { maximumFractionDigits: 2 }).format(v);
}

function glossaryPage(focus) {
  setCrumbs([{ label: "Overview", href: "#/" }, { label: "Glossary" }]);
  setNav("glossary");
  const groups = A.site.glossary_groups;
  const filter = el("input", { type: "search", placeholder: "Find a term", "aria-label": "Find a term" });
  const box = el("div");
  const draw = () => {
    const w = filter.value.toLowerCase();
    box.replaceChildren(...Object.entries(groups).flatMap(([g, name]) => {
      const items = Object.entries(A.glossary).filter(([, t]) => t.group === g && `${t.title} ${t.short}`.toLowerCase().includes(w)).sort((a, b) => a[1].title.localeCompare(b[1].title));
      return items.length ? [el("h2", { style: { margin: "26px 0 10px" } }, name), el("div.gloss", items.map(([k, t]) => el("div.gitem", { id: `g-${k}` }, el("h3", t.title), ...paras(t.short), t.more ? paras(t.more, "muted") : null)))] : [];
    }));
  };
  filter.addEventListener("input", draw);
  show(el("div.eyebrow", "Plain English"), el("h1", "Glossary"), ...paras(A.site.glossary_intro, "lead"), el("div.filter-row", filter), box);
  draw();
  if (focus) requestAnimationFrame(() => document.getElementById(`g-${focus}`)?.scrollIntoView({ block: "center" }));
}

// ------------------------------------------------------------------------------------------------ routing

function route() {
  hidePop();
  closeMenu();
  closeJump();
  const raw = location.hash.replace(/^#\/?/, "");
  const [path, query] = raw.split("?");
  const params = new URLSearchParams(query || "");
  const parts = path.split("/").filter(Boolean);
  document.title = "Evidence atlas";
  if (!parts.length) home();
  else if (/^[UBM]\d+$/.test(parts[0]) && byId[parts[0]]) observationPage(parts[0]);
  else if (parts[0] === "observations") observationsPage(params);
  else if (parts[0] === "stage3") stage3Page();
  else if (parts[0] === "lenses") lensesPage();
  else if (parts[0] === "lens" && A.lenses[parts[1]]) lensPage(parts[1]);
  else if (parts[0] === "questions") questionsPage();
  else if (parts[0] === "question" && A.questions.some((q) => String(q.id) === parts[1])) questionPage(parts[1]);
  else if (parts[0] === "data") dataPage();
  else if (parts[0] === "limits") limitsPage();
  else if (parts[0] === "audit" && A.audit) auditPage();
  else if (parts[0] === "next") nextPage();
  else if (parts[0] === "glossary") glossaryPage(parts[1]);
  else {
    setCrumbs([{ label: "Not found" }]);
    show(el("h1", "Not found"), el("p", "There is no page here. ", el("a", { href: "#/" }, "Go to the overview.")));
  }
  sweep();
  const keep = /^\/?observations/.test(path) && params.toString();
  if (!keep) scrollTo(0, 0);
  main.focus({ preventScroll: true });
}

// the menu, on small screens
const side = $("#side"), menu = $("#menu");
function closeMenu() { side.classList.remove("open"); menu.setAttribute("aria-expanded", "false"); }
menu.addEventListener("click", () => { const open = !side.classList.contains("open"); side.classList.toggle("open", open); menu.setAttribute("aria-expanded", String(open)); });

// the search box in the top bar: suggestions as you type (an id, or words in a headline); Enter opens the one chosen,
// or the filtered list of observations
const jump = $("#jump");
const jumpList = el("ul.jump-list", { id: "jump-list", role: "listbox", "aria-label": "Matching observations", hidden: true });
jump.closest(".jump").append(jumpList);
jump.setAttribute("role", "combobox");
jump.setAttribute("aria-autocomplete", "list");
jump.setAttribute("aria-controls", "jump-list");
jump.setAttribute("aria-expanded", "false");
let hits = [], pick = -1;
function matches(v) {
  const q = v.trim().toLowerCase();
  if (!q) return [];
  const id = q.toUpperCase();
  const exact = byId[id] ? [byId[id]] : [];
  const prefix = /^[UBM]\d*$/.test(id) ? A.observations.filter((o) => o.id !== id && o.id.startsWith(id)) : [];
  const words = q.split(/\s+/);
  const rest = A.observations.filter((o) => !exact.includes(o) && !prefix.includes(o) && words.every((w) => haystack(o).includes(w)));
  // headline matches first, the latest stage first among equals; then matches anywhere in the text
  const inHead = (o) => words.every((w) => o.headline.toLowerCase().includes(w));
  const rank = (o) => (inHead(o) ? 0 : 10) + (3 - o.stage);
  return [...exact, ...prefix, ...rest.sort((x, y) => rank(x) - rank(y))].slice(0, 8);
}
function closeJump() {
  jumpList.hidden = true;
  jump.setAttribute("aria-expanded", "false");
  jump.removeAttribute("aria-activedescendant");
  pick = -1;
}
function drawJump() {
  hits = matches(jump.value);
  pick = Math.min(pick, hits.length - 1);
  if (!jump.value.trim()) { closeJump(); return; }
  jumpList.replaceChildren(...hits.map((o, k) => {
    const li = el("li", { id: `jump-${k}`, role: "option", "aria-selected": String(k === pick) },
      el("span.id", o.id), el("span.jh", trim(o.headline, 92)), el("span.js", `Stage ${o.stage} · ${A.lenses[o.lens]?.name || o.lens}`));
    li.addEventListener("mousedown", (e) => { e.preventDefault(); go(o); });
    return li;
  }), (() => {
    const all = el("li.all", { role: "option", id: "jump-all", "aria-selected": String(pick === hits.length) }, hits.length ? `See every match for "${jump.value.trim()}"` : `No headline matches "${jump.value.trim()}". Search the full text`);
    all.addEventListener("mousedown", (e) => { e.preventDefault(); goList(); });
    return all;
  })());
  jumpList.hidden = false;
  jump.setAttribute("aria-expanded", "true");
  if (pick >= 0) jump.setAttribute("aria-activedescendant", pick < hits.length ? `jump-${pick}` : "jump-all");
  else jump.removeAttribute("aria-activedescendant");
}
function go(o) { jump.value = ""; closeJump(); jump.blur(); location.hash = `#/${o.id}`; }
function goList() { const v = jump.value.trim(); jump.value = ""; closeJump(); jump.blur(); location.hash = `#/observations?s=${encodeURIComponent(v)}`; }
jump.addEventListener("input", () => { pick = -1; drawJump(); });
jump.addEventListener("focus", () => { if (jump.value.trim()) drawJump(); });
jump.addEventListener("blur", () => setTimeout(closeJump, 120));
jump.addEventListener("keydown", (e) => {
  if (e.key === "ArrowDown" || e.key === "ArrowUp") {
    e.preventDefault();
    if (jumpList.hidden) drawJump();
    const n = hits.length + 1;
    const down = e.key === "ArrowDown";
    pick = pick < 0 ? (down ? 0 : n - 1) : (pick + (down ? 1 : n - 1)) % n;
    drawJump();
  } else if (e.key === "Enter") {
    e.preventDefault();
    if (!jump.value.trim()) return;
    if (pick >= 0 && pick < hits.length) go(hits[pick]);
    else if (pick < 0 && byId[jump.value.trim().toUpperCase()]) go(byId[jump.value.trim().toUpperCase()]);
    else goList();
  } else if (e.key === "Escape") {
    if (!jumpList.hidden) { e.stopPropagation(); closeJump(); } else jump.blur();
  }
});

// keys: "/" searches; on an observation, the arrow keys (or j and k) move to the next or previous one
document.addEventListener("keydown", (e) => {
  if (!A || e.defaultPrevented || e.metaKey || e.ctrlKey || e.altKey) return;
  if (e.target.closest?.("input, textarea, select, [contenteditable], .chart-card, .tablewrap")) return;
  if (e.key === "/") { e.preventDefault(); jump.focus(); return; }
  const cur = byId[location.hash.replace(/^#\/?/, "").split(/[/?]/)[0]];
  if (!cur) return;
  const i = A.observations.indexOf(cur);
  const to = e.key === "ArrowRight" || e.key === "j" ? A.observations[i + 1] : e.key === "ArrowLeft" || e.key === "k" ? A.observations[i - 1] : null;
  if (to) { e.preventDefault(); location.hash = `#/${to.id}`; }
});

initTheme($("#theme"));
fetch("data/atlas.json").then((r) => r.json()).then((atlas) => {
  A = atlas;
  for (const o of A.observations) byId[o.id] = o;
  $("#nav-count").textContent = String(A.observations.length);
  $("#foot-asat").textContent = `as at ${longDate(A.built)}`;
  addEventListener("hashchange", route);
  route();
}).catch((e) => { console.error(e?.stack || e); show(el("p", "The evidence could not be loaded. If you opened this file from disk, serve the folder over http instead.")); });
