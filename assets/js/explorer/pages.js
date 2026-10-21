// The explorer's reference pages: where every dataset came from and what the build did with it (from
// data/processed/manifest.json), and the glossary of every term the hover call-outs explain.

import { GROUPS, TERMS } from "../glossary.js";
import { el, fmt, link, n as nfmt } from "../util.js";

const REPO = "https://github.com/Thomas-Amann-IPAustralia/Aus-GII-Breakdown/blob/main/";

export function renderSources(root, man) {
  const t = man.totals;
  root.append(el("div.card",
    el("h2", "Where the data come from"),
    el("p.lede", `${nfmt(t.time_variables)} Australian series over time and ${nfmt(t.economy_variables)} measures across ${nfmt(t.economies)} economies, read from the files below by `,
      el("code", "uv run breakdown build"), ". The build is deterministic: the same raw files always give the same data, and ",
      el("code", "--check"), " proves the published data match them."),
    el("p", "Every file's SHA-256 is recorded so a number can be traced to the exact file it came from. Licences are as the publishers state them; where we were not sure, the entry says so. ",
      link("The source register", `${REPO}config/sources.yaml`), " · ", link("How the data are built", `${REPO}docs/methods.md`), " · ",
      link("The framework lenses", `${REPO}config/lenses.yaml`))));

  const reads = man.read;
  const readFor = { gii: ["gii"], wdi: ["wdi"], hdr_annex: ["hdr_annex"], hdr_series: ["hdr_series"], oecd_wise: ["oecd_wise"], whr: ["whr_series", "whr_latest"], ctg: ["ctg"] };
  for (const s of man.sources) {
    const counts = (readFor[s.id] || []).map((k) => [k, reads[k]]).filter(([, v]) => v);
    root.append(el("div.card",
      el("div.card-head", el("div", el("p.eyebrow", s.publisher), el("h3", s.title)), el("span.chip", s.licence)),
      el("p", el("strong", "Used: "), s.used),
      s.notes ? el("p.small.ink2", s.notes) : null,
      counts.length ? el("p.small.muted", "Read: ", counts.map(([k, v]) => `${k}: ${Object.entries(v).filter(([, x]) => typeof x === "number").map(([a, x]) => `${a.replaceAll("_", " ")} ${nfmt(x)}`).join(", ")}`).join("; ")) : null,
      el("p.small", link("The publisher's page", s.url), " · originally uploaded as ", el("code", s.original)),
      el("details", el("summary.small", `${s.files.length} file${s.files.length === 1 ? "" : "s"}`),
        el("ul.src-files", s.files.map((f) => el("li", el("a", { href: `../${f.path}` }, f.path), ` · ${fmt(f.bytes / 1024, 3)} KB · sha256 ${f.sha256.slice(0, 16)}…`))))));
  }
  const unmatched = reads.hdr_annex?.unmatched_labels;
  if (unmatched?.length) {
    root.append(el("div.card", el("h3", "Rows left out of the HDR annex"),
      el("p.small.ink2", "Rows whose label is not a country (groups, regions, the world). Listed so a missed country would be visible: ", unmatched.join("; "), ".")));
  }
}

export function renderGlossary(root, focus) {
  const byGroup = {};
  for (const [k, t] of Object.entries(TERMS)) (byGroup[t.group] ||= []).push([k, t]);
  root.append(el("div.card",
    el("h2", "Glossary"),
    el("p.lede", "Every dotted term and every “?” on these pages explains itself on hover or focus. Here they all are in one place, with what to watch out for."),
    el("div.gloss", Object.entries(GROUPS).map(([g, name]) => el("section",
      el("h3", name),
      el("dl", (byGroup[g] || []).map(([k, t]) => [
        el("dt", { id: k }, t.title),
        el("dd", el("p", t.short), t.tool ? el("p", el("strong", "Here: "), t.tool) : null, t.watch ? el("p", el("strong", "Watch out: "), t.watch) : null),
      ])))))));
  if (focus) requestAnimationFrame(() => document.getElementById(focus)?.scrollIntoView({ block: "start" }));
}
