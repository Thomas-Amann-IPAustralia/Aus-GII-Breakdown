// Write every observation's Markdown copy (evidence/js/markdown.js) and report what each carries, for
// tests/test_atlas.py: `node analysis/atlas/markdown_check.mjs` prints one JSON line per observation.
import { existsSync, readFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const root = resolve(dirname(fileURLToPath(import.meta.url)), "../..");
const { observationMarkdown } = await import(pathToFileURL(`${root}/evidence/js/markdown.js`).href);
const { chartTable, viewSpec } = await import(pathToFileURL(`${root}/evidence/js/tables.js`).href);
const A = JSON.parse(readFileSync(`${root}/evidence/data/atlas.json`, "utf8"));
for (const o of A.observations) {
  const p = `${root}/evidence/data/charts/${o.chart}.json`;
  const chart = o.chart && existsSync(p) ? JSON.parse(readFileSync(p, "utf8")) : null;
  const md = observationMarkdown(o, { atlas: A, chart, base: "https://example.org/evidence/" });
  const views = chart ? (chart.views?.length ? chart.views.map((_, k) => viewSpec(chart, k)) : [chart]) : [];
  const rows = views.map((s) => chartTable(s).rows.length);
  console.log(JSON.stringify({ id: o.id, chart: !!chart, rows, md }));
}
