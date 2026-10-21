// Small shared helpers, adapted from Moria's dashboard (Moria/dashboard/assets/js/util.js). Text from a data file
// (names, descriptions) is untrusted: it reaches the page only through textContent or esc(), and a link only when
// it is plain http(s).

export function esc(s) {
  return String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]);
}

/** Build an element: el("div.card.flat", {onclick}, child, "text", ...). Strings become text nodes (never HTML). */
export function el(spec, attrs, ...children) {
  const [tag, ...classes] = spec.split(".");
  const node = document.createElement(tag || "div");
  if (classes.length) node.className = classes.join(" ");
  if (attrs && (typeof attrs !== "object" || attrs instanceof Node || Array.isArray(attrs))) {
    children.unshift(attrs);
    attrs = null;
  }
  for (const [k, v] of Object.entries(attrs || {})) {
    if (v == null || v === false) continue;
    if (k.startsWith("on") && typeof v === "function") node.addEventListener(k.slice(2), v);
    else if (k === "style" && typeof v === "object") Object.assign(node.style, v);
    else if (k === "dataset") Object.assign(node.dataset, v);
    else if (k === "value") node.value = v;
    else node.setAttribute(k, v === true ? "" : v);
  }
  append(node, children);
  return node;
}

export function append(node, children) {
  for (const c of children.flat(Infinity)) {
    if (c == null || c === false) continue;
    node.append(c instanceof Node ? c : document.createTextNode(String(c)));
  }
  return node;
}

/** Trusted static SVG markup (icons written in this code base) as a node. */
export function svg(markup) {
  const t = document.createElement("template");
  t.innerHTML = markup.trim();
  return t.content.firstChild;
}

export function safeUrl(u) {
  return typeof u === "string" && /^https?:\/\/[^\s<>"']+$/i.test(u) ? u : null;
}

export function link(text, url) {
  const u = safeUrl(url);
  return u ? el("a", { href: u, target: "_blank", rel: "noopener noreferrer" }, text) : el("span", text);
}

const nf = new Intl.NumberFormat("en-AU");
export function n(v) {
  return v == null || Number.isNaN(v) ? "–" : nf.format(v);
}
export function fmt(v, digits = 3) {
  if (v == null || Number.isNaN(v)) return "–";
  if (typeof v !== "number") return String(v);
  if (v === 0) return "0";
  const a = Math.abs(v);
  if (a >= 1e6) return compact(v);
  if (a >= 1000) return nf.format(Math.round(v));
  if (a >= 1) return String(+v.toPrecision(Math.max(digits, 3)));
  if (a >= 0.001) return String(+v.toPrecision(digits));
  return v.toExponential(1);
}
/** A correlation-like number: always two decimals, a true minus sign. */
export function r2d(v) {
  if (v == null || Number.isNaN(v)) return "–";
  return v.toFixed(2).replace("-", "−");
}
export function pct(v, digits = 0) {
  if (v == null || Number.isNaN(v)) return "–";
  return `${(v * 100).toFixed(digits)}%`;
}
export function pval(p) {
  if (p == null || Number.isNaN(p)) return "–";
  if (p < 0.0001) return "< 0.0001";
  if (p >= 0.995) return "1.00";
  return p < 0.01 ? p.toFixed(4) : p.toFixed(3);
}
export function compact(v) {
  return new Intl.NumberFormat("en-AU", { notation: "compact", maximumFractionDigits: 1 }).format(v);
}
export function ordinal(k) {
  const s = ["th", "st", "nd", "rd"], v = k % 100;
  return `${k}${s[(v - 20) % 10] || s[v] || s[0]}`;
}

export function css(name) {
  return getComputedStyle(document.documentElement).getPropertyValue(name).trim();
}

export function debounce(fn, ms = 200) {
  let t;
  return (...a) => {
    clearTimeout(t);
    t = setTimeout(() => fn(...a), ms);
  };
}

export function clamp(v, lo, hi) {
  return Math.max(lo, Math.min(hi, v));
}

export function download(name, text, type = "text/csv") {
  const url = URL.createObjectURL(new Blob([text], { type }));
  const a = el("a", { href: url, download: name });
  document.body.append(a);
  a.click();
  a.remove();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}
export function toCsv(rows, cols) {
  const q = (v) => {
    let s = v == null ? "" : String(v);
    if (typeof v === "string" && /^[=+\-@\t\r]/.test(s)) s = `'${s}`; // a spreadsheet never runs a source's text
    return /[",\n]/.test(s) ? `"${s.replaceAll('"', '""')}"` : s;
  };
  return [cols.map((c) => q(c.label)).join(","), ...rows.map((r) => cols.map((c) => q(c.value(r))).join(","))].join("\n");
}

/** The light/dark switch shared by both pages: remembered per browser, and the OS setting until it is used. */
export function initTheme(button) {
  const root = document.documentElement;
  try {
    const saved = localStorage.getItem("gii-theme");
    if (saved === "light" || saved === "dark") root.dataset.theme = saved;
  } catch { /* storage blocked: follow the OS */ }
  const current = () => root.dataset.theme || (matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");
  const label = () => button && button.setAttribute("aria-label", `Switch to ${current() === "dark" ? "light" : "dark"} mode`);
  label();
  button?.addEventListener("click", () => {
    root.dataset.theme = current() === "dark" ? "light" : "dark";
    try { localStorage.setItem("gii-theme", root.dataset.theme); } catch { /* not remembered */ }
    label();
    window.dispatchEvent(new CustomEvent("themechange"));
  });
  matchMedia("(prefers-color-scheme: dark)").addEventListener("change", () => window.dispatchEvent(new CustomEvent("themechange")));
}
