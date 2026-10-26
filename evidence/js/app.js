// The evidence atlas: one page, routed by the address's #fragment, reading evidence/data/atlas.json (built by
// analysis/atlas/build.py) and each chart's JSON on demand. All text reaches the page as text nodes; the light markup
// in the content (**bold**, [[term]], {U44}, `code`) is turned into elements here, never parsed as HTML.

import { el, initTheme } from "../../assets/js/util.js";
import { chartCard, sweep } from "./charts.js";

const $ = (s, r = document) => r.querySelector(s);
const main = $("#main");
let A = null; // the atlas
const byId = {};
const chartCache = {};

const LENS_ORDER = ["rights", "timeline", "firms", "regions", "national", "industries", "institutions", "corpus"];
const lensColour = (l) => `var(--l-${l})`;

// ------------------------------------------------------------------------------------------------ text markup

const TOKEN = /\*\*(.+?)\*\*|\[\[([^\]|]+)(?:\|([^\]]+))?\]\]|\{(U\d+)\}|`([^`]+)`|(OQ\d+)/g;
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
function aboutLabel(o) {
  return el("span.about", o.about === "data" ? "About the data" : "About the IP system");
}
function ocard(o) {
  const a = el("a.ocard", { href: `#/${o.id}` },
    el("div.meta", el("span.id", o.id), lensChip(o.lens, false), aboutLabel(o)),
    el("h3", o.headline),
    el("p", trim(plain(o.statement), 190)),
    el("div.meta", (o.questions || []).map((q) => el("span.chip.qchip", `Q${q.q}`)), o.chart ? el("span.chip", "Chart") : null));
  a.style.setProperty("--lc", lensColour(o.lens));
  return a;
}
/** Markup removed, for short summaries. */
function plain(s) {
  return String(s ?? "").replace(/\[\[[^\]|]+\|([^\]]+)\]\]/g, "$1").replace(/\[\[([^\]]+)\]\]/g, (_, k) => A.glossary[k]?.title?.toLowerCase() || k)
    .replace(/\*\*/g, "").replace(/\{(U\d+)\}/g, "$1").replace(/`/g, "");
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
  const tags = { assume: ["Assumption", "flag"], limit: ["Limit", "alert"], next: ["Next stage", "arrow"] };
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
        el("a.btn.primary", { href: "#/observations" }, "Browse all observations", icon("arrow")),
        el("a.btn", { href: "#/limits" }, "What Stage 1 cannot tell you"))),
    metrics);

  const banner = el("div.banner", icon("info"), el("div", ...paras(S.banner)));

  const journey = el("div.journey", S.stages.map((s) => el(`a.stage${s.status === "Complete" ? ".done" : ""}`, { href: s.href || "#/next" },
    el("div.dot", s.n), el("h3", s.name), el("span.status", s.status), el("p", s.short))));

  const f = byId[S.featured.id];
  const feature = el("div.feature",
    el("div.feature-copy",
      el("div.meta", obsLink(f.id), lensChip(f.lens), strengthBadge(f.strength)),
      el("h2", S.featured.title || f.headline),
      ...paras(S.featured.text),
      el("div.row", el("a.btn.primary", { href: `#/${f.id}` }, "Follow this observation back to its data", icon("arrow")))),
    el("div.feature-viz", chartSlot(f.chart, { compact: true })));

  const ten = el("ol.ten", { style: { listStyle: "none", padding: 0 } }, S.ten.map((t, i) => el("li.tenitem",
    el("span.n", String(i + 1).padStart(2, "0")),
    el("h3", t.title),
    ...paras(t.text),
    el("div.meta", t.ids.map(obsLink)))));

  const lensTiles = el("div.lens-tiles", LENS_ORDER.filter((l) => A.lenses[l]).map((l) => {
    const L = A.lenses[l];
    const count = A.observations.filter((o) => o.lens === l).length;
    const t = el("a.ltile", { href: `#/lens/${l}` }, el("h3", L.name), el("p", L.unit), el("small", `${count} observation${count === 1 ? "" : "s"} · ${L.rows || ""}`));
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
    el("h3", s.name, s.now ? el("span.chip", { style: { marginLeft: "8px" } }, "Stage 1") : null), ...paras(s.text))));

  show(hero, banner,
    section("Where this sits in the research", S.journey_intro, journey),
    section("Start with one observation", S.featured.intro, feature),
    section("Ten things most worth knowing", S.ten_intro, ten),
    section("Explore by lens", "A lens is the unit being described: an IP right, a firm, a place, a country, a month, an industry or a research institution.", lensTiles),
    section("Explore by research question", "The five questions the research will answer after Stage 3. Every observation says which of them it moves closer to, and how.", qTiles),
    section("How to read an observation", S.reading.intro, anatomy, el("h3", { style: { margin: "22px 0 10px" } }, "How strong is the evidence?"), ...paras(S.reading.strength_intro, "muted"), scale));
}

function observationsPage(params) {
  setCrumbs([{ label: "Overview", href: "#/" }, { label: "Observations" }]);
  setNav("observations");
  const st = { lens: params.get("lens") || "all", q: params.get("q") || "all", about: params.get("about") || "all", s: params.get("s") || "" };
  const results = el("div");
  const count = el("p.result-count", { "aria-live": "polite" });

  const lensBar = el("div.chipbar", { role: "group", "aria-label": "Lens" });
  const opts = [["all", "All lenses"], ...LENS_ORDER.filter((l) => A.lenses[l]).map((l) => [l, A.lenses[l].name])];
  for (const [k, name] of opts) {
    const b = el("button", { type: "button", "aria-pressed": String(st.lens === k) }, k === "all" ? null : el("span.ldot"), name);
    if (k !== "all") b.style.setProperty("--lc", lensColour(k));
    b.addEventListener("click", () => { st.lens = k; [...lensBar.children].forEach((c) => c.setAttribute("aria-pressed", String(c === b))); update(); });
    lensBar.append(b);
  }
  const qSel = el("select", { "aria-label": "Research question" }, el("option", { value: "all" }, "Any research question"),
    A.questions.map((q) => el("option", { value: String(q.id) }, `Q${q.id}: ${q.short}`)));
  qSel.value = st.q;
  qSel.addEventListener("change", () => { st.q = qSel.value; update(); });
  const about = el("div.seg", { role: "group", "aria-label": "What the observation is about" });
  for (const [k, name] of [["all", "All"], ["system", "About the IP system"], ["data", "About the data"]]) {
    const b = el("button", { type: "button", "aria-pressed": String(st.about === k) }, name);
    b.addEventListener("click", () => { st.about = k; [...about.children].forEach((c) => c.setAttribute("aria-pressed", String(c === b))); update(); });
    about.append(b);
  }
  const search = el("input", { type: "search", placeholder: "Search the observations", "aria-label": "Search the observations", value: st.s });
  search.addEventListener("input", () => { st.s = search.value; update(); });

  function update() {
    const words = st.s.toLowerCase().split(/\s+/).filter(Boolean);
    const list = A.observations.filter((o) =>
      (st.lens === "all" || o.lens === st.lens) &&
      (st.q === "all" || o.questions.some((x) => String(x.q) === st.q)) &&
      (st.about === "all" || o.about === st.about) &&
      words.every((w) => `${o.id} ${o.headline} ${o.statement} ${(o.points || []).join(" ")}`.toLowerCase().includes(w)));
    count.textContent = `${list.length} of ${A.observations.length} observations`;
    const groups = LENS_ORDER.map((l) => [l, list.filter((o) => o.lens === l)]).filter(([, g]) => g.length);
    results.replaceChildren(...groups.flatMap(([l, g]) => [
      el("div.group-head", lensChip(l), el("h2", A.lenses[l]?.unit || ""), el("span.muted.small", `${g.length}`)),
      el("div.cards", g.map(ocard)),
    ]), list.length ? "" : el("p.muted", "No observation matches. Try fewer words, or another lens."));
    const p = new URLSearchParams();
    if (st.lens !== "all") p.set("lens", st.lens);
    if (st.q !== "all") p.set("q", st.q);
    if (st.about !== "all") p.set("about", st.about);
    if (st.s) p.set("s", st.s);
    history.replaceState(null, "", `#/observations${p.toString() ? `?${p}` : ""}`);
  }
  show(
    el("div.eyebrow", "Stage 1 · every observation"),
    el("h1", "Observations"),
    ...paras(A.site.observations_intro, "lead"),
    el("div.filters", lensBar, el("div.filter-row", qSel, about, search), count),
    results);
  update();
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

function observationPage(id) {
  const o = byId[id];
  const L = A.lenses[o.lens] || { name: o.lens };
  const i = A.observations.indexOf(o);
  setCrumbs([{ label: "Observations", href: "#/observations" }, { label: L.name, href: `#/lens/${o.lens}` }, { label: o.id }]);
  setNav("observations");
  document.title = `${o.id}: ${o.headline} · Evidence atlas`;

  const head = el("header.obs-head",
    el("div.meta", el("span.id", o.id), lensChip(o.lens), el("span", o.section.replace(/`/g, "")), strengthBadge(o.strength), aboutLabel(o)),
    el("h1", o.headline));
  const box = el("section.obs-box", { "aria-label": `Observation ${o.id}` },
    el("div.obs-label", icon("eye"), `Observation ${o.id} · ${o.strength}`),
    el("p.statement", inline(o.statement)),
    o.points?.length ? el("ul", o.points.map((p) => el("li", inline(p)))) : null);
  const figures = o.figures?.length ? el("div.figures", o.figures.map((f) => el("div.figure", el("strong", f.value), el("span", inline(f.label))))) : null;
  const chart = o.chart ? chartSlot(o.chart) : null;

  const why = el("section.block",
    el("h2", icon("compass"), "How this moves the research forward"),
    el("p.block-intro", "Stage 1 answers none of the five questions. This is how the observation prepares the ground for them."),
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
      el("p.small.muted", inline(`The lens table this observation reads, ${L.name.toLowerCase()} (${L.unit.toLowerCase()}), is not stored: it is rebuilt from these tables in minutes by the project's build code, so it always matches them.`))]);
  const prep = [...(o.prep || []).map((p) => el("div.prepitem", el("p", inline(p.what)), el("p.why", el("strong", "Why"), ...inline(p.why))))];
  const lensRepairs = (L.repairs || []).map((p) => el("div.prepitem", el("p", inline(p.what)), el("p.why", el("strong", "Why"), ...inline(p.why))));
  const step3 = trailStep(3, "tool", "How it was prepared",
    `${(o.prep || []).length} step${(o.prep || []).length === 1 ? "" : "s"} for this observation, on the ${L.name.toLowerCase()} lens (${L.unit.toLowerCase()})`,
    [el("h4", "For this observation"), el("div.prep", prep),
      lensRepairs.length ? el("details.more", el("summary", icon("tool"), `Repairs made to the ${L.name.toLowerCase()} lens before any observation (${lensRepairs.length})`), el("div", el("div.prep", lensRepairs))) : null]);
  const step4 = trailStep(4, "route", "From the data to the observation",
    `${o.steps.length} reasoning steps. The steps are not findings; only the last box is.`,
    [el("ol.steps", o.steps.map((s) => el("li", el("span.slabel", "Step"), el("span", inline(s)))),
      el("li.result", el("div.resultbox", el("span.slabel", `Which gives observation ${o.id}`), el("span", inline(o.statement)))))], true);
  const trail = el("section.block", el("h2", icon("route"), "Follow the evidence"),
    el("p.block-intro", "From the publisher's file to this observation, in four steps. Open any step for the detail."),
    el("div.trail", step1, step2, step3, step4));

  const honesty = el("section.block", el("h2", icon("alert"), "Assumptions and limits"),
    el("div.notes", o.assumptions.map((a) => note("assume", a)), o.limits.map((a) => note("limit", a))));
  const next = el("section.block", el("h2", icon("arrow"), "What happens next"), el("div.notes", note("next", o.next)));

  const nbCharts = o.notebook_charts || [];
  const analysts = el("section.block",
    el("details.more",
      el("summary", icon("book"), "For analysts: the notebook's own words and charts"),
      el("div",
        el("p.small.muted", inline(`Quoted from section ${o.section.replace(/`/g, "")} of the Stage 1 notebook. Reading it is optional: everything above says the same in plain English.`)),
        notebookMarkdown(o.original),
        ...nbCharts.map((c) => el("figure.nbimg", el("img", { src: c.src, alt: `A chart from the notebook, above observation ${o.id}`, loading: "lazy", decoding: "async" }), el("figcaption", "The chart as drawn in the notebook."))),
        el("p.small", el("a", { href: A.notebook, rel: "noopener noreferrer", target: "_blank" }, "Open the notebook on GitHub"), " · the code that builds every lens is in analysis/eda/build.py."))));

  const related = (o.related || []).filter((r) => byId[r]);
  const rel = related.length ? el("section.block", el("h2", "Related observations"), el("div.cards", related.map((r) => ocard(byId[r])))) : null;

  const prev = A.observations[i - 1], nxt = A.observations[i + 1];
  const pager = el("nav.pager", { "aria-label": "Previous and next observations" },
    prev ? el("a", { href: `#/${prev.id}` }, el("small", `← ${prev.id}`), prev.headline) : el("span"),
    nxt ? el("a.next", { href: `#/${nxt.id}` }, el("small", `${nxt.id} →`), nxt.headline) : null);

  const terms = [...new Set([...(o.terms || []), ...[...JSON.stringify(o).matchAll(/\[\[([^\]|]+)/g)].map((m) => m[1])])].filter((t) => A.glossary[t]);
  const rail = el("aside.rail", { "aria-label": "Explainers and facts about this observation" },
    el("section",
      el("div.glance",
        el("h2", "At a glance"),
        el("dl",
          el("dt", "Lens"), el("dd", lensChip(o.lens)),
          el("dt", "Unit"), el("dd", L.unit),
          el("dt", "About"), el("dd", o.about === "data" ? "The data themselves" : "The IP system"),
          el("dt", "Stage"), el("dd", "1 of 3 (each variable on its own)")),
        el("h2", { style: { marginTop: "14px" } }, "Strength of evidence"),
        el("div.scale", ["descriptive", "observational", "causal", "projected"].map((s) => el(`span${s === o.strength ? ".on" : ""}`, s === o.strength ? `${s} (this observation)` : s))),
        el("p.small.muted", { style: { marginTop: "8px" } }, "Descriptive: what the data show, not why. Stronger kinds need Stages 2 and 3."))),
    terms.length ? el("section", el("h2", "Explainers"), ...terms.map((t) => el("div.explainer", el("h3", icon("info"), A.glossary[t].title), ...paras(A.glossary[t].short)))) : null);

  show(el("div.obs-page",
    el("article.obs-main", head, box, figures, chart, why, trail, honesty, next, analysts, rel, pager),
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
  const sections = [...new Set(obs.map((o) => o.section))];
  const srcs = (L.sources || []).map((s) => A.sources[s]).filter(Boolean);
  const head = el("header",
    el("div.eyebrow", lensChip(l, false), "Lens"),
    el("h1", L.name), el("p.lead", L.unit),
    el("div.figures", (L.facts || []).map((f) => el("div.figure", el("strong", f.value), el("span", f.label)))));
  show(head,
    el("div.prose", ...paras(L.description)),
    L.questions?.length ? el("div.row", { style: { margin: "10px 0 0" } }, el("span.muted.small", "Mainly informs"), ...L.questions.map(qChip)) : "",
    section("Built from", "Each source as its publisher released it; open a source for its tables.", el("div.srclist", srcs.map((s) => sourceCard(s)))),
    L.repairs?.length ? section("Repairs made before any observation", "Problems found while profiling, fixed in the lens and recorded in a decision record. Each says why.",
      el("div.prep", L.repairs.map((p) => el("div.prepitem", el("p", inline(p.what)), el("p.why", el("strong", "Why"), ...inline(p.why), p.adr ? el("span.muted", ` (ADR ${p.adr})`) : null))))) : "",
    L.limits?.length ? section("Limits of this lens", null, el("div.notes", L.limits.map((x) => note("limit", x)))) : "",
    section(`Its ${obs.length} observations`, null, ...sections.flatMap((s) => [el("h3", { style: { margin: "18px 0 10px" } }, s.replace(/`/g, "")), el("div.cards", obs.filter((o) => o.section === s).map(ocard))])));
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
  const items = bearing.map((o) => el("div.qitem", obsLink(o.id), el("div", el("h3", el("a", { href: `#/${o.id}` }, o.headline)), el("p", inline(o.questions.find((x) => x.q === q.id).how)))));
  const leads = A.site.next.leads.filter((l) => l.questions.includes(q.id));
  show(
    el("div.eyebrow", `Question ${q.id} of 5`), el("h1", q.title), ...paras(q.text, "lead"),
    q.sub?.length ? section("What the research goal asks under it", null, el("ul.prose", q.sub.map((s) => el("li", s)))) : "",
    section("What Stage 1 found that bears on it", "Descriptive observations only: groundwork, not answers.", el("div.qlist", items), editorialNote("These links are the analyst's guide to where each observation may help. They are not findings.")),
    section("What Stage 2 will test for it", "Pairs of variables to relate, each needing its size, its uncertainty and a second sample before it counts.",
      el("div.qlist", leads.map((l) => el("div.qitem", el("span.qn", "Lead"), el("div", el("h3", inline(l.lead)), el("p", "From ", ...l.ids.flatMap((x, i) => [i ? ", " : "", obsLink(x)]))))))),
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
    section("What Stage 1 cannot tell you", null, el("div.notes", Lm.cannot.map((x) => el("div.note.limit", icon("alert"), el("div", el("span.tag", x.title), ...paras(x.text)))))),
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
  const leads = el("div.tablewrap", el("table.data", el("thead", el("tr", el("th", "What Stage 2 will relate"), el("th", "From"), el("th", "Questions"))),
    el("tbody", N.leads.map((l) => el("tr", el("td", inline(l.lead)), el("td", l.ids.flatMap((x, i) => [i ? " " : "", obsLink(x)])), el("td", l.questions.map(qChip)))))));
  show(el("div.eyebrow", "The road ahead"), el("h1", "What comes next"), ...paras(N.intro, "lead"),
    section("Three stages, then the questions", null, stages),
    section("What Stage 2 will test", N.leads_intro, leads),
    section("Puzzles kept in view", N.puzzles_intro, el("div.notes", N.puzzles.map((p) => el("div.note.next", icon("flag"), el("div", el("span.tag", "Unexplained"), el("p", inline(p))))))),
    section("Questions waiting on someone else", N.open_intro, el("div.grid.g2",
      el("div.card.flat", el("h3", "For the research owner"), el("ul", N.owner.map((x) => el("li", inline(x))))),
      el("div.card.flat", el("h3", "For IP Australia"), el("ul", N.ipa.map((x) => el("li", inline(x))))))),
    section("Data worth adding", N.gaps_intro, el("ul.prose", N.gaps.map((x) => el("li", inline(x))))),
    section("After Stage 3", null, el("ol.prose", N.after.map((x) => el("li", inline(x))))));
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
  const raw = location.hash.replace(/^#\/?/, "");
  const [path, query] = raw.split("?");
  const params = new URLSearchParams(query || "");
  const parts = path.split("/").filter(Boolean);
  document.title = "Evidence atlas";
  if (!parts.length) home();
  else if (/^U\d+$/.test(parts[0]) && byId[parts[0]]) observationPage(parts[0]);
  else if (parts[0] === "observations") observationsPage(params);
  else if (parts[0] === "lenses") lensesPage();
  else if (parts[0] === "lens" && A.lenses[parts[1]]) lensPage(parts[1]);
  else if (parts[0] === "questions") questionsPage();
  else if (parts[0] === "question" && A.questions.some((q) => String(q.id) === parts[1])) questionPage(parts[1]);
  else if (parts[0] === "data") dataPage();
  else if (parts[0] === "limits") limitsPage();
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

// the search box in the top bar: an id goes straight to its page; words go to the filtered list
$("#jump").addEventListener("keydown", (e) => {
  if (e.key !== "Enter") return;
  const v = e.target.value.trim();
  e.target.value = "";
  if (/^u\d+$/i.test(v) && byId[v.toUpperCase()]) location.hash = `#/${v.toUpperCase()}`;
  else location.hash = `#/observations?s=${encodeURIComponent(v)}`;
});

initTheme($("#theme"));
fetch("data/atlas.json").then((r) => r.json()).then((atlas) => {
  A = atlas;
  for (const o of A.observations) byId[o.id] = o;
  $("#nav-count").textContent = String(A.observations.length);
  $("#foot-asat").textContent = `as at ${longDate(A.built)}`;
  addEventListener("hashchange", route);
  route();
}).catch(() => { show(el("p", "The evidence could not be loaded. If you opened this file from disk, serve the folder over http instead.")); });
