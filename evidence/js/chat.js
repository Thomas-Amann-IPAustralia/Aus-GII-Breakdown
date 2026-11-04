// "Ask the atlas" (#/ask, ADR 0054): a chat whose only evidence is these pages, served by the Econ repository's API
// as a second knowledge base (/api/atlas/*), kept apart from the Econ chat. Its behaviour is ported from the Econ
// chat's front end (web/app.js there: the stream, drafts, the answer's cited runs, the claims, the evidence trail,
// Copy and the JSON export); its look is the atlas's own. Every string from the server reaches the page as text
// (the `el` helper) or through `renderMarkdown` and `highlight`, which escape it first.

import { el, esc } from "../../assets/js/util.js";

let U = null; // the atlas's helpers and data, from app.js (initChat)
const STORE = "atlas-chat-v1";
const RATING = { 3: "essential", 2: "useful", 1: "on topic, not usable", 0: "not about the question" };
const STEPS = [["plan", "Plan the search"], ["search", "Search the pages"], ["filter", "Choose the passages"], ["answer", "Write the answer"], ["check", "Check every quote and number"]];

const newId = () => (crypto.randomUUID ? crypto.randomUUID() : Array.from(crypto.getRandomValues(new Uint8Array(16)), (b) => b.toString(16).padStart(2, "0")).join(""));
const state = { turns: [], selected: null, health: null, session: newId(), about: null, meta: null, busy: false, root: null };

export function initChat(ctx) {
  U = ctx;
  restore();
}

// ------------------------------------------------------------------------------------------------ the API

function api() {
  // The page calls nothing outside the configured address (the Content Security Policy names its host). A
  // same-origin path in ?api= serves a local check (analysis/atlas/chat_check.mjs) through the page's own server.
  const q = new URLSearchParams(location.search).get("api");
  return (q && q.startsWith("/") ? q : U.A.site.chat?.api || "").replace(/\/$/, "");
}

async function* sse(resp) {
  const reader = resp.body.getReader();
  const dec = new TextDecoder();
  let buf = "";
  for (;;) {
    const { value, done } = await reader.read();
    if (done) break;
    buf += dec.decode(value, { stream: true });
    let i;
    while ((i = buf.indexOf("\n\n")) >= 0) {
      const block = buf.slice(0, i);
      buf = buf.slice(i + 2);
      const data = block.split("\n").filter((l) => l.startsWith("data: ")).map((l) => l.slice(6)).join("\n");
      if (data) yield JSON.parse(data);
    }
  }
}

/** Wake the service (Render sleeps when idle) and say what it can do: answers, or the passages alone. */
async function wake(line) {
  const set = (cls, text) => { line.className = `chat-status ${cls}`; line.lastChild.textContent = text; };
  if (!api()) return set("down", "The chat's address is not configured.");
  if (state.health) return showHealth(line);
  const t0 = Date.now();
  set("waking", "Waking the service…");
  for (let i = 0; i < 40; i++) {
    try {
      const r = await fetch(`${api()}/health`, { cache: "no-store" });
      if (r.ok) {
        state.health = await r.json();
        return showHealth(line);
      }
    } catch (e) { /* still waking */ }
    set("waking", `Waking the service… ${Math.round((Date.now() - t0) / 1000)}s (free hosting sleeps when idle; about a minute)`);
    await new Promise((r) => setTimeout(r, 3000));
  }
  set("down", "The service is unavailable just now. Try again in a few minutes.");
}
function showHealth(line) {
  const llm = state.health.llm;
  line.className = `chat-status ${llm.mode === "answer" ? "ready" : "evidence"}`;
  line.lastChild.textContent = llm.mode === "answer"
    ? `Ready: ${llm.answer_model} answers, ${llm.plan_model} plans and chooses the passages`
    : llm.budget_reached ? "Today's budget is reached: the chat shows the passages it finds, without an answer" : "Passages only: no answer model is configured";
  currency();
}

/** Whether the chat reads these pages as they are now: its index records the passages' hash. */
let localMeta = null;
async function currency() {
  const at = state.health?.atlas;
  const box = document.getElementById("chat-currency");
  if (!at || !box) return;
  try { localMeta ||= await (await fetch("data/passages.meta.json")).json(); } catch (e) { return; }
  if (localMeta.passages_sha256 === at.passages_sha256) { box.hidden = true; return; }
  box.hidden = false;
  box.replaceChildren(U.icon("info"), el("div", el("p", `The chat reads the atlas as at ${U.longDate(at.built)}; these pages have changed since. Quotes are checked against that version, and each still leads to its page.`)));
}

// ------------------------------------------------------------------------------------------------ the page

export function chatPage(params) {
  const S = U.A.site.chat;
  U.setCrumbs([{ label: "Overview", href: "#/" }, { label: "Ask the atlas" }]);
  U.setNav("ask");
  document.title = "Ask the atlas · Evidence atlas";
  const about = params.get("about");
  if (about && U.byId[about]) state.about = about;

  const status = el("p.chat-status.waking", { role: "status" }, el("span.dot", { "aria-hidden": "true" }), el("span", "Waking the service…"));
  const q = el("textarea", { id: "chat-q", rows: "3", maxlength: "2000", placeholder: "Ask about the evidence, for example: Do patents filed without an attorney fare worse?", "aria-label": "Your question" });
  const ctx = el("textarea", { id: "chat-ctx", rows: "4", maxlength: "20000", placeholder: "Paste a paragraph to compare with the atlas. It is never cited.", "aria-label": "Your own material" });
  const extra = el("details.chat-extra", el("summary", "Compare with your own material"), ctx);
  const send = el("button.btn.primary", { id: "chat-send", type: "submit", disabled: state.busy }, "Ask", U.icon("arrow"));
  const chip = el("span.chat-about");
  const drawAbout = () => {
    const o = U.byId[state.about];
    chip.replaceChildren(...(o ? [el("span.chip.about-chip", { title: o.headline }, `About ${o.id}`,
      el("button", { type: "button", "aria-label": `Stop asking about ${o.id}`, onclick: () => { state.about = null; history.replaceState(null, "", "#/ask"); drawAbout(); } }, U.icon("x")))] : []));
  };
  drawAbout();
  const form = el("form.card.chat-form", { onsubmit: (ev) => {
    ev.preventDefault();
    const text = q.value.trim();
    if (!text || state.busy) return;
    const c = ctx.value.trim();
    q.value = ""; ctx.value = ""; extra.open = false;
    ask(text, c);
  } }, el("label.sr", { for: "chat-q" }, "Your question"), q, extra, el("div.chat-form-foot", chip, el("span.muted.small", "Enter to send · Shift+Enter for a new line"), send));
  q.addEventListener("keydown", (ev) => { if (ev.key === "Enter" && !ev.shiftKey) { ev.preventDefault(); form.requestSubmit(); } });

  const starters = el("div.chipbar.chat-starters", { role: "group", "aria-label": "Questions to start with" },
    (S.starters || []).map((s) => el("button", { type: "button", onclick: () => { q.value = s; q.focus(); } }, s)));
  const thread = el("div.chat-thread", { "aria-live": "polite" });
  const trail = el("aside.chat-trail", { id: "chat-trail", "aria-label": "Evidence trail" });
  const bar = el("div.chat-bar", { id: "chat-bar", hidden: !state.turns.length },
    el("span.muted.small", { id: "chat-count" }),
    el("button.btn.small", { type: "button", onclick: (ev) => copyOut(ev.currentTarget, chatJson()) }, U.icon("copy"), el("span", "Copy as JSON")),
    el("button.btn.small", { type: "button", onclick: saveChat }, U.icon("source"), el("span", "Download the conversation")),
    el("button.btn.small", { type: "button", onclick: () => { if (state.busy) return; state.turns = []; state.selected = null; state.session = newId(); persist(); U.route(); } }, U.icon("x"), el("span", "Start again")));

  U.show(
    el("div.eyebrow", S.eyebrow),
    el("h1", S.title),
    ...U.paras(S.lead, "lead"),
    el("div.banner", { id: "chat-currency", hidden: true, style: { margin: "16px 0 0" } }),
    el("div.chat-grid",
      el("div.chat-main", status, bar, thread, state.turns.length ? null : el("div.chat-empty", el("p.muted.small", "Try one of these:"), starters), form),
      trail),
    U.section(S.how_title, null, el("div.dsteps", (S.how || []).map((s, i) => el("div.dstep", el("div.dn", String(i + 1)), el("div", el("h3", s.title), ...U.paras(s.text)))))));
  state.root = { thread, trail, send };
  for (const t of state.turns) {
    t.el = botShell(t);
    thread.append(userMsg(t), t.el);
    renderBot(t);
  }
  showBar();
  const pick = state.selected && state.turns.includes(state.selected) ? state.selected : state.turns[state.turns.length - 1];
  state.selected = null;
  if (pick) select(pick); else renderTrail(null);
  wake(status);
}

function userMsg(t) {
  return el("div.cmsg.user", el("p", t.question),
    t.context ? el("span.chip", `+ ${t.context.length.toLocaleString("en-AU")} characters of your material`) : null,
    t.observations?.length ? el("span.chip", `About ${t.observations.join(", ")}`) : null);
}
function botShell(t) {
  return el("div.cmsg.bot", { tabindex: "0", onclick: () => { select(t); if (narrow()) document.getElementById("chat-trail")?.scrollIntoView({ behavior: "smooth" }); } });
}
function showBar() {
  const b = document.getElementById("chat-bar");
  if (!b) return;
  b.hidden = !state.turns.length;
  document.getElementById("chat-count").textContent = `${state.turns.length} ${state.turns.length === 1 ? "question" : "questions"} in this conversation`;
}

// ------------------------------------------------------------------------------------------------ asking

async function ask(question, context) {
  const R = state.root;
  R.thread.parentElement.querySelector(".chat-empty")?.remove();
  const observations = state.about ? [state.about] : null;
  const t = { question, context, observations, events: {}, checks: [], t0: performance.now(), askedAt: new Date().toISOString(), shown: {} };
  state.turns.push(t);
  t.el = botShell(t);
  R.thread.append(userMsg(t), t.el);
  renderBot(t);
  t.el.scrollIntoView({ block: "end" });
  select(t);
  showBar();
  const history = state.turns.slice(0, -1).flatMap((x) => [
    { role: "user", text: x.question },
    x.events.answer ? { role: "assistant", text: x.events.answer.answer.replace(/\[\d+\]/g, "") } : null,
  ]).filter(Boolean).slice(-6);
  state.busy = true;
  setSend(true);
  try {
    const resp = await fetch(`${api()}/ask`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question, context, history, observations, session_id: state.session }),
    });
    if (!resp.ok) throw new Error((await resp.json().catch(() => ({}))).detail || `The service answered ${resp.status}.`);
    for await (const ev of sse(resp)) {
      if (ev.event === "draft") {
        if (t.draft?.attempt !== ev.attempt) t.draft = { attempt: ev.attempt, text: "" };
        if (ev.withheld) t.draft.withheld = true; else t.draft.text += ev.text;
        drawSoon(t);
        continue;
      }
      ev._t = (performance.now() - t.t0) / 1000;
      if (ev.event === "check") t.checks.push(ev);
      if (ev.event === "answer") t.events.answers = [...(t.events.answers || []), ev];
      t.events[ev.event] = ev;
      if (ev.event === "meta") state.meta = ev;
      renderBot(t);
      if (state.selected === t) renderTrail(t);
    }
  } catch (e) {
    t.events.error = { message: e.message || String(e), _t: (performance.now() - t.t0) / 1000 };
    renderBot(t);
    if (state.selected === t) renderTrail(t);
  } finally {
    state.busy = false;
    setSend(false);
    persist();
  }
}
function setSend(on) {
  const b = document.getElementById("chat-send");
  if (b) b.disabled = on;
}
function drawSoon(t) {
  if (t.drawing) return;
  t.drawing = true;
  requestAnimationFrame(() => { t.drawing = false; renderBot(t); });
}
const liveDraft = (t) => (t.draft && !t.events.done && !(t.events.answer && t.events.answer.attempt >= t.draft.attempt) ? t.draft : null);
const narrow = () => window.matchMedia("(max-width: 860px)").matches;

// The conversation survives a visit to a cited page (module state) and a reload (sessionStorage, this tab only).
function persist() {
  try {
    const turns = state.turns.filter((t) => t.events.done || t.events.error).map((t) => ({
      question: t.question, context: t.context, observations: t.observations, askedAt: t.askedAt, checks: t.checks,
      events: Object.fromEntries(Object.entries(t.events).map(([k, v]) => [k, k === "retrieval" ? { ...v, traces: [] } : v])),
    }));
    sessionStorage.setItem(STORE, JSON.stringify({ session: state.session, turns }));
  } catch (e) { /* not kept; the page still works */ }
}
function restore() {
  try {
    const s = JSON.parse(sessionStorage.getItem(STORE) || "null");
    if (!s?.turns) return;
    state.session = s.session || state.session;
    state.turns = s.turns.map((t) => ({ ...t, shown: {}, t0: 0 }));
  } catch (e) { /* nothing to restore */ }
}

// ------------------------------------------------------------------------------------------------ the answer

function progressText(t) {
  const e = t.events;
  if (e.done || (e.error && !e.answer)) return null;
  if (liveDraft(t)) return "Writing the answer. Its quotes and numbers are checked when it is finished.";
  if (e.answer) return "Checking every quote and number…";
  if (e.retrieval) {
    if (e.meta?.mode !== "answer") return "Collecting the passages…";
    return `Chose ${e.retrieval.evidence.length} of ${e.retrieval.filter?.read || e.retrieval.evidence.length} passages. Writing the answer…`;
  }
  if (e.search) return `Read ${e.search.read} passages. Choosing the most useful…`;
  if (e.plan) return `Searching: ${e.plan.queries.join(" · ")}`;
  return "Planning the search…";
}

// Emphasis is marked before escaping, so a run cut at a claim marker can close what is open and reopen it.
const EMPH = { "": ["strong", true], "": ["strong", false], "": ["em", true], "": ["em", false] };
const emphasis = (s) => s.replace(/[-]/g, "").replace(/\*\*(.+?)\*\*/g, "$1").replace(/(^|[^*])\*([^*]+)\*/g, "$1$2");
function emphHtml(s, open) {
  if (!s) return "";
  let out = (open.strong ? "<strong>" : "") + (open.em ? "<em>" : "");
  out += esc(s).replace(/[-]/g, (c) => { const [tag, on] = EMPH[c]; open[tag] = on; return on ? `<${tag}>` : `</${tag}>`; });
  return out + (open.em ? "</em>" : "") + (open.strong ? "</strong>" : "");
}
// A run ending in claim markers rests on those claims' sentences; prose after a line's last marker, or on a line
// with none, is the assistant's own words (the rule of cite._claim_text on the server).
const MARKER_RUN = /((?:\[\d{1,3}\][ \t]*)+)/;
function lineParts(line) {
  const bits = line.split(MARKER_RUN);
  const parts = [];
  for (let i = 0; i < bits.length; i += 2) {
    const text = bits[i], run = bits[i + 1];
    if (run) parts.push({ kind: "cited", text, claims: [...run.matchAll(/\[(\d{1,3})\]/g)].map((m) => +m[1]), run });
    else if (text) parts.push({ kind: /\w/.test(text) ? "own" : "plain", text });
  }
  return parts;
}
function answerParts(md) {
  return md.split("\n").flatMap((line) => {
    const heading = /^\s*#{1,4}\s+/.test(line);
    return lineParts(line.replace(/^\s*(?:[-*•]|\d+[.)]|#{1,4})\s+/, "").replace(/\*+/g, ""))
      .filter((p) => p.kind !== "plain")
      .map((p) => (p.kind === "cited" ? { kind: "cited", claims: p.claims, text: p.text.trim() } : { kind: heading ? "heading" : "own", text: p.text.trim() }));
  });
}
/** Markdown-lite: escape first, then paragraphs, lists, bold and italics; markers become buttons; cited runs are
 * marked so the stylesheet draws them in the atlas's teal. */
function renderMarkdown(md, { claims = [], draft = false, parts = false } = {}) {
  const failed = new Set(claims.filter((c) => !c.verified).map((c) => c.n));
  const marker = (n) => `<button class="cite${failed.has(n) ? " failed" : ""}" type="button" data-claim="${n}" title="Claim ${n}${failed.has(n) ? ": failed the check" : ""}. Select to read the sentences it cites">${n}</button>`;
  const inlineMd = (s) => emphHtml(emphasis(s), {}).replace(draft ? /\[(\d{1,3}(?:\.\d{1,3})?)\]/g : /\[(\d{1,3})\]/g, (_, n) => draft
    ? `<span class="cite pending" title="${n.includes(".") ? `Passage ${n.split(".")[0]}, sentence ${n.split(".")[1]}` : `Claim ${n}`}: not yet checked">${n}</span>`
    : marker(+n));
  const said = (s) => {
    const open = {};
    return lineParts(emphasis(s)).map((p) => {
      if (p.kind !== "cited") return emphHtml(p.text, open);
      const lead = p.text.match(/^[\s.,;:!?)\]”’"']*/)[0];
      const rest = p.text.slice(lead.length);
      const tail = rest.match(/\s*$/)[0];
      const body = rest.slice(0, rest.length - tail.length);
      return emphHtml(lead, open)
        + (body ? `<span class="said cited" data-claims="${p.claims.join(" ")}" title="Rests on the sentences claim ${p.claims.join(", ")} cites">${emphHtml(body, open)}</span>` : "")
        + emphHtml(tail, open) + p.run.replace(/\[(\d{1,3})\]/g, (_, n) => marker(+n));
    }).join("");
  };
  const text = (s) => (parts && !draft ? said(s) : inlineMd(s));
  const out = [];
  let list = null;
  for (const raw of md.split("\n")) {
    const line = raw.trimEnd();
    const m = line.match(/^\s*([-*•]|\d+[.)])\s+(.*)$/);
    if (m) {
      const kind = /\d/.test(m[1]) ? "ol" : "ul";
      if (!list || list.kind !== kind) { if (list) out.push(`</${list.kind}>`); out.push(`<${kind}>`); list = { kind }; }
      out.push(`<li>${text(m[2])}</li>`);
      continue;
    }
    if (list) { out.push(`</${list.kind}>`); list = null; }
    if (!line.trim()) continue;
    const hd = line.match(/^#{1,4}\s+(.*)$/);
    out.push(hd ? `<h4>${text(hd[1])}</h4>` : `<p>${text(line)}</p>`);
  }
  if (list) out.push(`</${list.kind}>`);
  return out.join("");
}
/** Observation ids in rendered prose become links to their pages (text nodes only; existing ids only). */
function linkIds(root) {
  const walk = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
  const nodes = [];
  while (walk.nextNode()) if (/\b[UBM]\d{1,3}\b/.test(walk.currentNode.nodeValue) && !walk.currentNode.parentElement.closest("a, button")) nodes.push(walk.currentNode);
  for (const n of nodes) {
    const frag = document.createDocumentFragment();
    let last = 0;
    for (const m of n.nodeValue.matchAll(/\b([UBM]\d{1,3})\b/g)) {
      if (!U.byId[m[1]]) continue;
      frag.append(n.nodeValue.slice(last, m.index), el("a.id", { href: `#/${m[1]}`, title: U.byId[m[1]].headline }, m[1]));
      last = m.index + m[0].length;
    }
    if (last) { frag.append(n.nodeValue.slice(last)); n.replaceWith(frag); }
  }
}
function claimsOf(t) {
  const c = t.checks[t.checks.length - 1];
  return c && (!t.events.answer || c.attempt === t.events.answer.attempt) ? c.claims : [];
}
const evidenceByN = (t) => Object.fromEntries((t.events.retrieval?.evidence || []).map((x) => [x.n, x]));
const sentenceColour = (k) => `k k${Math.min(k, 4)}`;

function renderBot(t) {
  const e = t.events;
  const node = t.el;
  if (!node) return;
  node.classList.toggle("selected", state.selected === t);
  node.replaceChildren();
  const check = t.checks[t.checks.length - 1];
  const badges = el("div.chat-badges");
  const draft = liveDraft(t);
  if (draft) {
    badges.append(el("span.vtag.vt-none", draft.withheld ? "Draft hidden: it failed a text check" : "Draft · not yet checked"));
  } else if (e.answer) {
    const cov = { complete: ["vt-hold", "Complete answer"], partial: ["vt-weak", "Partial answer"], not_in_kb: ["vt-none", "Not in the atlas"] }[e.answer.coverage];
    badges.append(el(`span.vtag.${cov[0]}`, cov[1]));
    if (check && check.attempt === e.answer.attempt) {
      const n = check.claims.length, bad = check.claims.filter((c) => !c.verified).length;
      if (check.passed) {
        badges.append(el("span.vtag.vt-hold", { title: "Each claim's quotes are whole sentences copied by code from the passages, and every number the claim states is in them. The check does not judge whether a sentence supports its claim." },
          n ? `Checked: ${n} ${n === 1 ? "claim" : "claims"}, every quote and number found` : "Checked"));
      } else {
        const why = el("ul.chat-why", { hidden: true }, check.errors.map((x) => el("li", x)));
        badges.append(el("button.vtag.vt-weak", { type: "button", title: "Show why", onclick: (ev) => { ev.stopPropagation(); why.hidden = !why.hidden; } },
          `Flagged: ${bad || "some"} of ${n} claims failed the check`), why);
      }
    }
  } else if (e.meta?.mode === "evidence_only" && e.retrieval) {
    badges.append(el("span.vtag.vt-none", "Passages only"));
  }
  if (badges.childNodes.length) node.append(badges);
  if (draft) {
    if (!draft.withheld) {
      const body = el("div.chat-prose.draft");
      body.innerHTML = renderMarkdown(draft.text, { draft: true });
      node.append(body);
    }
  } else if (e.answer) {
    if (t.shownAttempt !== e.answer.attempt) Object.assign(t, { shownAttempt: e.answer.attempt, claimOn: null });
    const claims = claimsOf(t);
    if (claims.length) node.append(tabs(t, claims.length));
    node.append(t.view === "claims" && claims.length ? claimsPanel(t, claims) : answerPanel(t, claims));
  } else if (e.retrieval && e.meta?.mode === "evidence_only") {
    node.append(el("p", `No answer is written just now, so here are the ${e.retrieval.evidence.length} passages that bear most on the question, best first, in the evidence trail.`));
  }
  if (e.error) node.append(el("p.chat-error", `Something went wrong: ${e.error.message}`));
  const prog = progressText(t);
  if (prog) node.append(el("p.chat-progress", el("span.spinner", { "aria-hidden": "true" }), el("span", prog)));
  if (e.done) {
    const cost = e.done.cost_usd ? ` · US$${e.done.cost_usd.toFixed(4)}` : "";
    node.append(el("div.chat-foot",
      e.answer ? el("button.btn.small", { type: "button", title: "Copy the answer, what it doesn't cover and its sources", onclick: (ev) => { ev.stopPropagation(); copyAnswer(t, ev.currentTarget); } }, U.icon("copy"), el("span", "Copy")) : null,
      el("span.muted.small", `${e.done.seconds}s${cost} · ${narrow() ? "tap" : "select"} to see the evidence trail`)));
    const next = e.answer?.follow_ups || [];
    if (next.length) {
      node.append(el("div.chat-next", el("span.muted.small", "You could ask next:"), el("div.chipbar", next.map((q) => el("button", { type: "button", onclick: (ev) => { ev.stopPropagation(); if (!state.busy) ask(q, ""); } }, q)))));
    }
  }
  node.querySelectorAll(".chat-answer button.cite").forEach((b) => b.addEventListener("click", (ev) => {
    ev.stopPropagation();
    pickClaim(t, +b.dataset.claim, { scroll: true });
  }));
  if (t.claimOn != null) {
    node.querySelectorAll(`.cite[data-claim="${t.claimOn}"], .claim-card[data-claim="${t.claimOn}"]`).forEach((x) => x.classList.add("on"));
    node.querySelectorAll(".said.cited[data-claims]").forEach((x) => x.classList.toggle("on", x.dataset.claims.split(" ").includes(String(t.claimOn))));
  }
}

function tabs(t, n) {
  const cur = t.view === "claims" ? "claims" : "answer";
  const go = (key) => { if (state.selected !== t) select(t); t.view = key; renderBot(t); t.el.querySelector(`[data-view="${key}"]`)?.focus(); if (t.claimOn != null) focusClaim(t, t.claimOn); };
  return el("div.chipbar.chat-tabs", { role: "tablist", "aria-label": "This answer", onkeydown: (ev) => {
    if (ev.key !== "ArrowLeft" && ev.key !== "ArrowRight") return;
    ev.preventDefault();
    go(cur === "answer" ? "claims" : "answer");
  } }, [["answer", "Answer"], ["claims", `Claims (${n})`]].map(([key, label]) => el("button", {
    type: "button", role: "tab", "data-view": key, "aria-selected": String(key === cur), "aria-pressed": String(key === cur), tabindex: key === cur ? "0" : "-1",
    onclick: (ev) => { ev.stopPropagation(); if (key !== cur) go(key); },
  }, label)));
}

function answerPanel(t, claims) {
  const a = t.events.answer;
  const body = el("div.chat-prose");
  body.innerHTML = renderMarkdown(a.answer, { claims, parts: true });
  linkIds(body);
  return el("div.chat-answer", { role: claims.length ? "tabpanel" : null }, body,
    a.gaps?.length ? el("div.chat-gaps", el("strong", "What the atlas doesn't cover"), el("ul", a.gaps.map((g) => el("li", g)))) : null);
}

function quoteBlock(t, q, src, n, k = null) {
  return el(`figure.chat-quote${q.found ? "" : ".missing"}${k ? `.${sentenceColour(k).split(" ").join(".")}` : ""}`,
    k ? el("span.qk", { title: `Sentence ${k} of this claim` }, String(k)) : null,
    el("blockquote", q.quote),
    el("figcaption", el("span", src ? sourceLine(src) : `Passage ${q.evidence}`, q.found ? "" : " · not found in the passage"),
      el("button.linkish", { type: "button", onclick: (ev) => { ev.stopPropagation(); pickClaim(t, n, { passage: q.evidence, span: q.start != null ? `${q.start}-${q.end}` : null, scroll: true }); } }, `Passage ${q.evidence}`),
      src ? el("a", { href: pageHash(src), onclick: (ev) => ev.stopPropagation() }, `Open ${src.observation || "the page"}`) : null));
}

function claimsPanel(t, claims) {
  const ev = evidenceByN(t);
  return el("div.chat-claims", { role: "tabpanel" },
    el("p.muted.small", "Each claim is in the assistant's words, above the sentences it cites, copied word for word by code, not by the AI. When a claim cites several sentences, each has its own colour and number, here and in the evidence trail."),
    el("ol.claim-cards", claims.map((c) => el(`li.claim-card${c.verified ? "" : ".failed"}`, {
      "data-claim": c.n, tabindex: "0", onclick: (e2) => { e2.stopPropagation(); pickClaim(t, c.n, {}); },
    },
    el("div.cc-head", el("span.cite", String(c.n)), c.verified ? el("span.vtag.sm.vt-hold", "Found word for word") : el("span.vtag.sm.vt-weak", "Failed the check")),
    el("p.cc-text", c.text),
    c.citations.map((q, i) => quoteBlock(t, q, ev[q.evidence], c.n, c.citations.length > 1 ? i + 1 : null)),
    c.errors.length ? el("p.chat-error.small", c.errors.join("; ")) : null))));
}

function pickClaim(t, n, { passage = null, span = null, scroll = false } = {}) {
  if (state.selected !== t) select(t);
  t.claimOn = n;
  renderBot(t);
  focusClaim(t, n, { scroll: scroll || !narrow(), passage, span });
}

// ------------------------------------------------------------------------------------------------ copy and export

const pageHash = (x) => {
  const u = String(x.url || "");
  const i = u.indexOf("#/");
  return i >= 0 ? u.slice(i) : "#/";
};
const pageUrl = (x) => new URL(pageHash(x), location.href.split("#")[0]).href;
const sourceLine = (s) => (s ? `${s.observation ? `${s.observation} (${s.strength}, Stage ${s.stage})` : s.title}${s.section?.length ? `, ${s.section[s.section.length - 1]}` : ""}` : "");

function copyAnswer(t, btn) {
  const a = t.events.answer;
  const ev = evidenceByN(t);
  const claims = claimsOf(t);
  const pages = [...new Set(claims.flatMap((c) => c.citations.map((q) => ev[q.evidence]).filter(Boolean).map(pageUrl)))];
  const plain = [
    `Q: ${t.question}`, "", a.answer.trim(), "",
    a.gaps?.length ? `What the atlas doesn't cover: ${a.gaps.join("; ")}\n` : null,
    claims.length ? "Sources" : null,
    ...claims.map((c) => `[${c.n}] ${c.citations.map((q) => `"${q.quote}" (${sourceLine(ev[q.evidence])}, ${ev[q.evidence] ? pageUrl(ev[q.evidence]) : ""})`).join("; ")}`),
    pages.length ? "\nPages" : null,
    ...pages.map((p, i) => `${i + 1}. ${p}`),
    "", "From the evidence atlas, an exploratory research view for IPAVentures (not an official publication); every quote was checked against the atlas's text.",
  ].filter((x) => x !== null).join("\n");
  copyOut(btn, plain);
}
function copyOut(btn, text) {
  const label = btn.lastChild;
  const was = label.textContent;
  const done = (ok) => { label.textContent = ok ? "Copied" : "Couldn't copy"; setTimeout(() => { label.textContent = was; }, 1600); };
  const fallback = () => {
    const ta = Object.assign(document.createElement("textarea"), { value: text });
    ta.style.position = "fixed"; ta.style.opacity = "0";
    document.body.append(ta); ta.select();
    let ok = false;
    try { ok = document.execCommand("copy"); } catch (e) { ok = false; }
    ta.remove();
    done(ok);
  };
  if (navigator.clipboard) navigator.clipboard.writeText(text).then(() => done(true), fallback);
  else fallback();
}

function exportTurn(t, i) {
  const e = t.events, r = e.retrieval, a = e.answer;
  const ev = evidenceByN(t);
  const claims = claimsOf(t);
  const check = t.checks[t.checks.length - 1];
  const citedBy = {};
  for (const c of claims) for (const x of c.citations) (citedBy[x.evidence] ||= new Set()).add(c.n);
  const sourceOf = (x) => ({ doc_id: x.doc_id, title: x.title, kind: x.kind ?? null, observation: x.observation ?? null, stage: x.stage ?? null, lens: x.lens ?? null, strength: x.strength ?? null, section: x.section, page_url: pageUrl(x) });
  const claimOut = (c) => ({ n: c.n, text: c.text, verified: c.verified, errors: c.errors,
    citations: c.citations.map((q) => ({ passage: q.evidence, chunk_id: q.chunk_id, quote: q.quote, found: q.found, start: q.start, end: q.end, source: ev[q.evidence] ? sourceOf(ev[q.evidence]) : null })) });
  return {
    n: i + 1, asked_at: t.askedAt, question: t.question, pasted_context: t.context || null, observations: t.observations || null,
    status: e.error ? "error" : e.done ? (e.done.outcome || e.done.mode) : "in progress",
    request_id: e.meta?.request_id ?? null, mode: e.meta?.mode ?? null,
    models: { plan: e.meta?.plan_model ?? null, filter: r?.filter?.model ?? null, answer: e.meta?.answer_model ?? null },
    prompt: e.meta?.prompt ?? null, atlas: e.meta?.atlas ?? null,
    plan: e.plan ? { standalone_question: e.plan.standalone_question, queries: e.plan.queries, error: e.plan.error ?? null } : null,
    filter: r?.filter ?? null, pinned: r?.pinned ?? [],
    answer: a ? { attempt: a.attempt, coverage: a.coverage, text: a.answer, parts: answerParts(a.answer), gaps: a.gaps, follow_ups: a.follow_ups || [] } : null,
    check: check && a && check.attempt === a.attempt ? { passed: check.passed, errors: check.errors } : null,
    claims: claims.map(claimOut),
    earlier_attempts: (e.answers || []).filter((x) => x.attempt !== a?.attempt).map((x) => {
      const c = t.checks.find((k) => k.attempt === x.attempt);
      return { attempt: x.attempt, coverage: x.coverage, text: x.answer, gaps: x.gaps, check: c ? { passed: c.passed, errors: c.errors } : null, claims: (c?.claims || []).map(claimOut) };
    }),
    evidence: (r?.evidence || []).map((x) => ({ n: x.n, chunk_id: x.chunk_id, ...sourceOf(x), pinned: Boolean(x.pinned), search_rank: x.search_rank ?? null, filter_rating: x.filter_grade ?? null, cited_by: [...(citedBy[x.n] || [])], matched_terms: x.matched_terms })),
    passages_read: (r?.pool || []).map((x) => ({ search_rank: x.search_rank, filter_rating: x.filter_grade ?? null, selected: x.selected, n: x.n ?? null, chunk_id: x.chunk_id, title: x.title, section: x.section })),
    done: e.done ? { outcome: e.done.outcome ?? null, attempts: e.done.attempts ?? null, seconds: e.done.seconds, cost_usd: e.done.cost_usd, timings: e.done.timings } : null,
    error: e.error?.message ?? null,
  };
}
function exportChat() {
  return {
    format: "atlas-chat-export/1",
    exported_at: new Date().toISOString(),
    page: location.origin + location.pathname,
    session_id: state.session,
    service: state.health ? { build: { commit: state.health.build?.commit, prompt: state.health.build?.prompt }, llm: state.health.llm, atlas: state.health.atlas } : null,
    notes: [
      "Everything the page showed for each question except the passages' full text: each passage is named by its chunk_id and links to its atlas page (page_url).",
      "answer.text is the assistant's prose, where [k] marks claim k. answer.parts splits it into runs that rest on claims (kind cited), the assistant's own words (kind own), and headings.",
      "Each claim's quotes are the sentences it cites, copied word for word from the passage by code; verified means every quote was found there and every number the claim states is in them. It does not judge whether a quote supports its claim.",
      "pinned: passages put first because the question named their observation. filter_rating: 3 essential, 2 useful, 1 on topic but not usable, 0 not about the question.",
    ],
    turns: state.turns.map(exportTurn),
  };
}
const chatJson = () => JSON.stringify(exportChat(), null, 2);
function saveChat() {
  const url = URL.createObjectURL(new Blob([chatJson()], { type: "application/json" }));
  const a = el("a", { href: url, download: `atlas-chat-${new Date().toISOString().slice(0, 16).replace(/[:T]/g, "-")}.json` });
  document.body.append(a);
  a.click();
  a.remove();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}

// ------------------------------------------------------------------------------------------------ the evidence trail

function select(t) {
  if (state.selected === t) return;
  state.selected = t;
  state.turns.forEach((x) => x.el?.classList.toggle("selected", x === t));
  renderTrail(t);
}

function quoteRanges(t) {
  const by = {};
  for (const c of claimsOf(t)) for (const cit of c.citations) {
    if (!cit.found || cit.start == null) continue;
    const list = (by[cit.evidence] ||= []);
    const same = list.find((r) => r.start === cit.start && r.end === cit.end);
    if (same) same.claims.push(c.n); else list.push({ start: cit.start, end: cit.end, claims: [c.n] });
  }
  return by;
}
function highlight(text, quotes) {
  const ranges = [...(quotes || [])].sort((a, b) => a.start - b.start);
  let out = "", pos = 0;
  for (const r of ranges) {
    if (r.start < pos) continue;
    out += esc(text.slice(pos, r.start));
    out += `<mark class="q" data-claims="${r.claims.join(" ")}" data-span="${r.start}-${r.end}" title="Cited by claim ${r.claims.join(", ")}">${esc(text.slice(r.start, r.end))}</mark>`;
    pos = r.end;
  }
  return out + esc(text.slice(pos));
}

function stepStates(t) {
  const e = t.events, r = e.retrieval, f = r?.filter, only = e.meta && e.meta.mode !== "answer";
  const s = {}, sub = {};
  if (only) { s.plan = "skipped"; sub.plan = "no model: searched as asked"; }
  else if (e.plan) { s.plan = e.plan.error ? "warn" : "done"; sub.plan = e.plan.error ? "searched as asked" : `${e.plan.queries.length} searches`; }
  else { s.plan = e.meta ? "active" : "pending"; sub.plan = e.meta ? "rewriting the question" : "waking the service"; }
  const found = e.search || r;
  if (found) { s.search = found.dense === "ok" ? "done" : "warn"; sub.search = `${found.candidates} found${found.dense === "ok" ? "" : ", keywords only"}${r?.pinned?.length ? `; ${r.pinned.join(", ")} pinned` : ""}`; }
  else { s.search = ["done", "warn", "skipped"].includes(s.plan) ? "active" : "pending"; sub.search = "by meaning and by keywords"; }
  const filtering = f && !String(f.status).startsWith("off");
  if (only || (r && !filtering)) { s.filter = "skipped"; sub.filter = only ? "no model" : "off"; }
  else if (r) { s.filter = f.status === "ok" ? "done" : "warn"; sub.filter = f.status === "ok" ? `kept ${f.kept} of ${f.read}` : "failed: the search's order kept"; }
  else { s.filter = e.search ? "active" : "pending"; sub.filter = e.search ? `rating ${e.search.read} passages` : "chooses 20 passages"; }
  const answers = e.answers || [], checks = t.checks, last = checks[checks.length - 1];
  if (only) { s.answer = s.check = "skipped"; sub.answer = "no model"; sub.check = "nothing to check"; }
  else {
    const retrying = checks.length && checks.length === answers.length && !last.passed && !e.done;
    if (retrying) { s.answer = "active"; sub.answer = "second attempt, after the check"; }
    else if (answers.length) { s.answer = "done"; const a = answers[answers.length - 1]; sub.answer = `${a.claims.length} claims${a.attempt > 1 ? ", 2nd attempt" : ""}`; }
    else { s.answer = r ? "active" : "pending"; sub.answer = r ? `reading ${r.evidence.length} passages` : e.meta?.answer_model || "the answer model"; }
    if (last && checks.length === answers.length) { s.check = last.passed ? "done" : e.done ? "failed" : "warn"; sub.check = last.passed ? "every quote and number found" : `${last.claims.filter((c) => !c.verified).length || "some"} claims failed`; }
    else if (answers.length > checks.length) { s.check = "active"; sub.check = "matching quotes and numbers"; }
    else { s.check = "pending"; sub.check = "quotes and numbers, word for word"; }
  }
  if (e.error) { const k = STEPS.map(([key]) => key).find((key) => s[key] === "active") || "answer"; s[k] = "failed"; sub[k] = "stopped here"; }
  return { s, sub };
}

function renderTrail(t) {
  const pane = document.getElementById("chat-trail");
  if (!pane) return;
  pane.replaceChildren(el("h2", "Evidence trail"));
  if (!t) {
    pane.append(el("p.muted.small", "Ask a question, and the passages the answer rests on appear here: each with its page, its observation's stage and strength of evidence, and the sentences quoted lit up."));
    return;
  }
  const { s, sub } = stepStates(t);
  pane.append(el("ol.chat-steps", { "aria-label": "How this answer is made" }, STEPS.map(([key, name], i) => el(`li.cstep.${s[key]}`,
    el("span.dn", { "aria-hidden": "true" }, { done: "✓", warn: "!", failed: "✕", skipped: "–" }[s[key]] || String(i + 1)),
    el("div", el("strong", name), el("span.muted.small", sub[key]))))));
  const r = t.events.retrieval;
  if (!r) return;
  const quotes = quoteRanges(t);
  const citedBy = {};
  for (const c of claimsOf(t)) for (const x of c.citations) (citedBy[x.evidence] ||= new Set()).add(c.n);
  pane.append(el("h3", `Passages the answer ${t.events.meta?.mode === "answer" ? "read" : "would read"} (${r.evidence.length})`),
    el("p.muted.small", "In the order the answer model saw them, pinned passages first. A teal edge marks a passage the answer cites; its quoted sentences are lit."));
  const list = el("div.chat-passages");
  for (const x of r.evidence) list.append(passageCard(t, x, quotes[x.n], citedBy[x.n]));
  pane.append(list);
  if (r.pool?.length) pane.append(poolTable(r, citedBy));
  if (t.claimOn != null) focusClaim(t, t.claimOn);
}

function passageCard(t, x, quotes, cited) {
  const o = x.observation ? U.byId[x.observation] : null;
  const part = x.section?.[0] || "";
  const tone = x.kind === "glossary" ? "explain" : /^Assumptions and limits/.test(part) ? "limit" : x.kind === "observation" ? "obs" : "plain";
  const textEl = el("div.ptext");
  textEl.innerHTML = highlight(x.text, quotes);
  const verdicts = o ? U.verdictsOf(o) : [];
  return el(`article.card.flat.pcard.t-${tone}${cited ? ".cited" : ""}`, { id: `chat-ev-${x.n}`, "data-n": x.n },
    el("div.phead",
      el("span.pn", String(x.n)),
      o ? U.obsLink(o.id) : el("strong.small", x.title),
      o ? U.stageChip(o) : null,
      o ? U.strengthBadge(o.strength) : null,
      x.lens ? U.lensChip(x.lens, false) : null,
      ...verdicts.map((v) => U.verdictTag(v, true)),
      x.pinned ? el("span.chip", { title: "Put first because the question named this observation" }, "Pinned") : null,
      cited ? el("span.pcited", "cited by", [...cited].map((n) => el("button.cite", { type: "button", "data-claim": n, onclick: () => pickClaim(t, n, { passage: x.n }) }, String(n)))) : null),
    el("div.pmeta.muted.small", [o ? trimText(o.headline, 120) : null, x.section?.join(" › "),
      x.filter_grade != null ? `rated ${x.filter_grade} (${RATING[x.filter_grade]})` : null,
      x.search_rank != null ? `search rank ${x.search_rank}` : null].filter(Boolean).join(" · ")),
    textEl,
    el("div.pactions",
      el("button.linkish", { type: "button", onclick: () => textEl.classList.toggle("open") }, "Expand"),
      el("a", { href: pageHash(x) }, o ? `Open ${o.id}'s page` : "Open the page", U.icon("arrow"))));
}
const trimText = (s, n) => (s.length > n ? `${s.slice(0, s.lastIndexOf(" ", n))}…` : s);

function poolTable(r, citedBy) {
  const used = r.pool.filter((x) => x.selected).length;
  return el("details.chat-pool", el("summary", el("strong", `All ${r.pool.length} passages the search read`), el("span.muted.small", ` · ${used} used${r.filter?.status === "ok" ? `, rated by ${r.filter.model}` : ""}`)),
    el("div.tablewrap", el("table.data", el("thead", el("tr", el("th.n", "Search"), el("th.n", "Rating"), el("th", "Used"), el("th", "Passage"))),
      el("tbody", r.pool.map((x) => el("tr", el("td.n", String(x.search_rank)), el("td.n", x.filter_grade == null ? "–" : String(x.filter_grade)),
        el("td", x.selected ? `[${x.n}]${citedBy[x.n] ? " cited" : ""}` : "not used"),
        el("td", el("a", { href: pageHash(x.url ? x : { url: `#/${String(x.doc_id).replace(/^atlas-/, "")}` }) }, x.title), el("span.muted.small", ` · ${(x.section || []).join(" › ")}`))))))));
}

function focusClaim(t, n, { scroll = false, passage = null, span = null } = {}) {
  if (state.selected !== t) return;
  const pane = document.getElementById("chat-trail");
  if (!pane) return;
  pane.querySelectorAll(".cite.on, mark.q.on").forEach((x) => { x.classList.remove("on", "k", "k1", "k2", "k3", "k4"); delete x.dataset.k; });
  pane.querySelectorAll(".pcard.focus").forEach((a) => a.classList.remove("focus"));
  const claim = claimsOf(t).find((c) => c.n === n);
  if (!claim) return;
  pane.querySelectorAll(`.cite[data-claim="${n}"]`).forEach((b) => b.classList.add("on"));
  const order = new Map(claim.citations.length > 1 ? claim.citations.map((q, i) => [`${q.evidence}:${q.start}-${q.end}`, i + 1]) : []);
  pane.querySelectorAll("mark.q[data-claims]").forEach((m) => {
    if (!m.dataset.claims.split(" ").includes(String(n))) return;
    m.classList.add("on");
    const k = order.get(`${m.closest(".pcard")?.dataset.n}:${m.dataset.span}`);
    if (k) { m.classList.add(...sentenceColour(k).split(" ")); m.dataset.k = k; }
  });
  let first = null;
  for (const c of claim.citations) {
    const card = document.getElementById(`chat-ev-${c.evidence}`);
    if (!card) continue;
    card.classList.add("focus");
    card.querySelector(".ptext").classList.add("open");
    if (passage == null || c.evidence === passage) first ||= (span && card.querySelector(`mark.q[data-span="${span}"]`)) || card.querySelector("mark.q.on") || card;
  }
  if (scroll) first?.scrollIntoView({ behavior: "smooth", block: "center" });
}

// A quoted sentence in the trail shows the claim that cites it.
document.addEventListener("click", (ev) => {
  const m = ev.target.closest?.("#chat-trail mark.q[data-claims]");
  if (m && state.selected) {
    pickClaim(state.selected, +m.dataset.claims.split(" ")[0], {});
    state.selected.el?.querySelector(`.cite[data-claim="${m.dataset.claims.split(" ")[0]}"]`)?.scrollIntoView({ behavior: "smooth", block: "nearest" });
  }
});
