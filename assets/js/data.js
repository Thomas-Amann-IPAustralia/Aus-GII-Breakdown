// Loading the built data (data/processed/*.json, from `uv run breakdown build`) and the helpers every view shares:
// a variable's values in a common shape, part-whole links, search, and the coverage summary the picker shows.

const cache = new Map();

async function getJson(path) {
  if (!cache.has(path)) {
    cache.set(path, fetch(path).then((r) => {
      if (!r.ok) throw new Error(`${path}: HTTP ${r.status}`);
      return r.json();
    }));
  }
  return cache.get(path);
}

export const MODES = {
  time: { file: "australia.json", name: "Australia over time", unit: "year", units: "years" },
  economy: { file: "economies.json", name: "Economies compared", unit: "economy", units: "economies" },
};

/** The dataset for a mode, indexed: {mode, vars, byId, economies?, iso?}. `base` is the path to data/processed/. */
export async function load(mode, base) {
  const raw = await getJson(`${base}${MODES[mode].file}`);
  if (raw._indexed) return raw._indexed;
  const vars = raw.variables;
  const byId = new Map(vars.map((v) => [v.id, v]));
  const out = { mode, vars, byId };
  if (mode === "time") {
    let lo = Infinity, hi = -Infinity;
    for (const v of vars) {
      v.series = new Map();
      v.values.forEach((x, i) => x != null && v.series.set(v.start + i, x));
      const ys = [...v.series.keys()];
      v.cov = { n: ys.length, from: ys[0], to: ys[ys.length - 1] };
      lo = Math.min(lo, v.cov.from); hi = Math.max(hi, v.cov.to);
    }
    out.years = { from: lo, to: hi };
  } else {
    out.economies = raw.economies;
    out.iso = raw.economies.map((e) => e.iso3);
    out.au = out.iso.indexOf("AUS");
    for (const v of vars) v.cov = { n: v.values.filter((x) => x != null).length, year: v.year };
  }
  for (const v of vars) v.search = `${v.name} ${v.topic} ${v.source} ${v.id} ${v.unit ?? ""}`.toLowerCase();
  raw._indexed = out;
  return out;
}

export async function manifest(base) {
  return getJson(`${base}manifest.json`);
}

export async function giiPage(base) {
  return getJson(`${base}gii-australia.json`);
}

/** Every composite a variable feeds, directly or through others (the transitive `parts_of`). */
export function wholes(ds, id) {
  const seen = new Set();
  const stack = [...(ds.byId.get(id)?.parts_of ?? [])];
  while (stack.length) {
    const p = stack.pop();
    if (seen.has(p)) continue;
    seen.add(p);
    stack.push(...(ds.byId.get(p)?.parts_of ?? []));
  }
  return seen;
}

/** How two variables are built from each other, if they are: "a-in-b", "b-in-a", "siblings" (one composite's parts). */
export function construction(ds, a, b) {
  const wa = wholes(ds, a), wb = wholes(ds, b);
  if (wb.has(a)) return "b-in-a";
  if (wa.has(b)) return "a-in-b";
  const pa = ds.byId.get(a)?.parts_of ?? [], pb = ds.byId.get(b)?.parts_of ?? [];
  if (pa.some((p) => pb.includes(p))) return "siblings";
  return null;
}

/** Search: every word must appear somewhere in the variable's name, topic, source, id or unit. */
export function search(ds, query, { lens, source, topic, minN = 0 } = {}) {
  const words = query.toLowerCase().split(/\s+/).filter(Boolean);
  return ds.vars.filter((v) => (!lens || v.lens === lens) && (!source || v.source === source) &&
    (!topic || v.topic === topic) && v.cov.n >= minN && words.every((w) => v.search.includes(w)));
}

export const SOURCES = {
  gii: "WIPO GII 2026",
  wdi: "World Bank WDI",
  hdr_annex: "UNDP HDR 2025",
  hdr_series: "UNDP HDR",
  oecd_wise: "OECD How's Life",
  whr: "World Happiness Report",
  ctg: "Closing the Gap",
};

export function coverage(v) {
  return v.cov.from != null ? `${v.cov.from}–${v.cov.to} · ${v.cov.n} yrs` : `${v.cov.n} economies · ${v.cov.year ?? ""}`;
}
