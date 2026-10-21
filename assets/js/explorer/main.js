// The correlation explorer: routes (#/compare, #/matrix, #/scan, #/sources, #/glossary/<term>), each with its
// settings in the address so any view can be linked to; the mode (Australia over time, or economies compared) is
// part of the address too.

import { disposeAll } from "../charts.js";
import { load, manifest, MODES } from "../data.js";
import { initPopover, term } from "../glossary.js";
import { el, initTheme } from "../util.js";
import { renderCompare, seg } from "./compare.js";
import { renderMatrix } from "./matrix.js";
import { renderGlossary, renderSources } from "./pages.js";
import { renderScan } from "./scan.js";

const BASE = "../data/processed/";
const main = document.getElementById("main");
const TABS = [
  ["compare", "Compare two"],
  ["matrix", "Correlation matrix"],
  ["scan", "Find correlates"],
  ["sources", "Sources"],
  ["glossary", "Glossary"],
];
const DEFAULTS = {
  compare: { time: { x: "wdi:GB.XPD.RSDV.GD.ZS", y: "wdi:IP.PAT.RESD" }, economy: { x: "gii:score:IN", y: "gii:score:OUT" } },
  matrix: { time: { v: "wdi:IP.PAT.RESD,wdi:IP.PAT.NRES,wdi:IP.TMK.RSCT,wdi:GB.XPD.RSDV.GD.ZS,wdi:IP.JRN.ARTC.SC,wdi:NY.GDP.PCAP.KD", t: "diff" },
    economy: { v: "gii:score:IN.1,gii:score:IN.2,gii:score:IN.3,gii:score:IN.4,gii:score:IN.5,gii:score:OUT.6,gii:score:OUT.7" } },
  scan: { time: { x: "wdi:IP.PAT.RESD", t: "diff" }, economy: { x: "gii:score:GII" } },
};

function parse() {
  const h = location.hash.replace(/^#\/?/, "");
  const [path, query = ""] = h.split("?");
  const [route = "compare", sub] = path.split("/");
  const p = Object.fromEntries(new URLSearchParams(query));
  return { route: TABS.some(([k]) => k === route) ? route : "compare", sub, p };
}

export function go(route, params = {}) {
  const q = new URLSearchParams(Object.entries(params).filter(([, v]) => v != null && v !== ""));
  const next = `#/${route}${q.toString() ? `?${q}` : ""}`;
  if (next === location.hash) render();
  else location.hash = next;
}

let lensCache = null;
let token = 0;

async function render() {
  const { route, sub, p } = parse();
  const mine = ++token;
  const mode = p.m === "economy" ? "economy" : "time";
  document.title = `${TABS.find(([k]) => k === route)[1]} · Correlation explorer · GII breakdown`;
  disposeAll(main);
  const scrollY = window.scrollY;

  const nav = el("nav.tabs", { "aria-label": "Explorer sections" }, TABS.map(([k, name]) => el("a", {
    href: `#/${k}${["compare", "matrix", "scan"].includes(k) ? `?m=${mode}` : ""}`, "aria-current": k === route ? "page" : null,
  }, name)));
  const frame = el("div");
  const head = el("div",
    el("p.eyebrow", "Correlation explorer"),
    el("h1", "Look for patterns, and test them honestly"),
    el("p.lede", "Compare measures from the datasets behind IP Australia's research goal: over time for Australia, or across economies. Every number explains itself on hover; every comparison comes with the checks that keep a correlation from being over-read. ",
      el("span.badge", "Exploratory"), " ", term("causation", "Correlation is not causation"), "."));
  const modeBar = ["compare", "matrix", "scan"].includes(route)
    ? el("div.row.mt", el("span.small.muted", "Unit of comparison:"),
        seg(Object.entries(MODES).map(([k, m]) => [k, m.name]), mode, (m) => go(route, { m, ...(DEFAULTS[route]?.[m] || {}) })),
        el("span.small.muted", mode === "time" ? "Each point is a year (Australia's own series)." : "Each point is an economy (GII 2026, UNDP HDR 2025, World Happiness Report 2026)."))
    : null;
  main.replaceChildren(head, modeBar || "", nav, frame);
  frame.append(el("p.muted", "Loading the data…"));

  try {
    const man = await manifest(BASE);
    lensCache = man.lenses;
    if (mine !== token) return;
    frame.replaceChildren();
    if (route === "sources") return renderSources(frame, man);
    if (route === "glossary") return renderGlossary(frame, sub);
    const ds = await load(mode, BASE);
    if (mine !== token) return;
    const params = Object.keys(p).filter((k) => k !== "m").length ? p : { ...(DEFAULTS[route]?.[mode] || {}) };
    const ctx = { go: (r, q) => go(r, { m: mode, ...q }), lenses: lensCache };
    if (route === "compare") renderCompare(frame, ds, params, ctx);
    else if (route === "matrix") renderMatrix(frame, ds, params, ctx);
    else if (route === "scan") renderScan(frame, ds, params, ctx);
    requestAnimationFrame(() => window.scrollTo({ top: scrollY }));
  } catch (e) {
    frame.replaceChildren(el("div.notice", `Could not load the data (${e.message}). If you opened this file from disk, serve the folder instead: python3 -m http.server, then open http://localhost:8000/explorer/.`));
    throw e;
  }
}

initTheme(document.getElementById("theme"));
initPopover("#/glossary/");
window.addEventListener("hashchange", render);
render();
