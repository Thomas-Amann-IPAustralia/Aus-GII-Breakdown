// The variable picker: a button showing the chosen measure; it opens a searchable list with filters by framework lens
// and source. Arrow keys move, Enter picks, Escape closes. Names are inserted as text, never HTML.

import { coverage, search, SOURCES } from "../data.js";
import { el } from "../util.js";

const MAX = 120;
let openPicker = null;
document.addEventListener("pointerdown", (e) => {
  if (openPicker && !openPicker.contains(e.target)) openPicker.close();
});

/**
 * picker({ds, value, onChange, label, swatch, lenses, placeholder, exclude}) -> element.
 * `swatch` is a CSS colour (a var()) shown beside the name, so the picker reads as the chart's legend.
 */
export function picker({ ds, value, onChange, label, swatch, lenses, placeholder = "Choose a measure…", exclude = [], allowNone = false }) {
  const v = value ? ds.byId.get(value) : null;
  const sw = el("span.swatch");
  if (swatch) sw.style.background = swatch;
  const btn = el("button.picker-btn", { type: "button", "aria-haspopup": "listbox", "aria-expanded": "false" },
    swatch ? sw : null,
    el("span.pk-name", v ? v.name : placeholder),
    v ? el("span.pk-meta", coverage(v)) : null);
  const root = el("div.picker", btn);
  let pop = null;

  function close() {
    pop?.remove();
    pop = null;
    btn.setAttribute("aria-expanded", "false");
    if (openPicker === root) openPicker = null;
  }
  root.close = close;

  function open() {
    if (pop) return close();
    openPicker?.close();
    openPicker = root;
    btn.setAttribute("aria-expanded", "true");
    const q = el("input", { type: "search", placeholder: "Search: words in the name, topic or source (e.g. patent, life expectancy, GII 6.1)", "aria-label": `Search for ${label}` });
    const lensSel = el("select", { "aria-label": "Framework lens" }, el("option", { value: "" }, "Every lens"),
      Object.entries(lenses || {}).map(([k, l]) => el("option", { value: k }, l.name)));
    const sources = [...new Set(ds.vars.map((x) => x.source))].sort();
    const srcSel = el("select", { "aria-label": "Source" }, el("option", { value: "" }, "Every source"),
      sources.map((s) => el("option", { value: s }, SOURCES[s] || s)));
    const list = el("ul.picker-list", { role: "listbox", "aria-label": label });
    const note = el("p.picker-note");
    pop = el("div.picker-pop", q,
      el("div.picker-filters", lensSel, srcSel, allowNone ? el("button.btn.small", { type: "button", onclick: () => { close(); onChange(null); } }, "None") : null),
      list, note);
    root.append(pop);
    let items = [], active = -1;

    function render() {
      const found = search(ds, q.value, { lens: lensSel.value || null, source: srcSel.value || null })
        .filter((x) => !exclude.includes(x.id));
      found.sort((a, b) => rankOf(a, q.value) - rankOf(b, q.value) || a.name.localeCompare(b.name));
      items = found.slice(0, MAX);
      list.replaceChildren(...items.map((x, i) => el("li", {
        role: "option", id: `opt-${i}`, "aria-selected": String(i === active),
        onclick: () => pick(x),
      }, el("span.nm", x.name), el("span.cov", coverage(x)),
      el("p.mt", el("span.chip", SOURCES[x.source] || x.source), el("span.chip.lens", lenses?.[x.lens]?.short ?? x.lens), x.topic, x.unit ? ` · ${x.unit}` : ""))));
      note.textContent = found.length > MAX ? `Showing ${MAX} of ${found.length.toLocaleString("en-AU")}: type more to narrow.` : `${found.length.toLocaleString("en-AU")} measures.`;
    }
    function pick(x) {
      close();
      onChange(x.id);
    }
    function move(d) {
      if (!items.length) return;
      active = (active + d + items.length) % items.length;
      [...list.children].forEach((li, i) => li.setAttribute("aria-selected", String(i === active)));
      list.children[active]?.scrollIntoView({ block: "nearest" });
    }
    q.addEventListener("input", () => { active = -1; render(); });
    lensSel.addEventListener("change", render);
    srcSel.addEventListener("change", render);
    pop.addEventListener("keydown", (e) => {
      if (e.key === "ArrowDown") { e.preventDefault(); move(1); }
      else if (e.key === "ArrowUp") { e.preventDefault(); move(-1); }
      else if (e.key === "Enter" && active >= 0) { e.preventDefault(); pick(items[active]); }
      else if (e.key === "Escape") { close(); btn.focus(); }
    });
    render();
    q.focus();
  }
  btn.addEventListener("click", open);
  return root;
}

// Without a query, put the framework's IP and headline measures first and the long tail of breakdowns last.
const ORDER = { ip: 0, composite: 1, activity: 2, potential: 3, outcomes: 4, public_value: 5, context: 6 };
const SRC_ORDER = { gii: 0, wdi: 1, hdr_annex: 2, hdr_series: 2, whr: 3, oecd_wise: 4, ctg: 5 };
function rankOf(v, query) {
  const q = query.trim().toLowerCase();
  let r = (SRC_ORDER[v.source] ?? 9) * 10 + (ORDER[v.lens] ?? 9);
  if (q) {
    const name = v.name.toLowerCase();
    r = name.startsWith(q) ? 0 : name.includes(q) ? 100 : 200;
    r += SRC_ORDER[v.source] ?? 9;
  }
  return r;
}
