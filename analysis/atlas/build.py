"""Build the evidence pages' data: `evidence/data/atlas.json`, the quoted charts and the notebook's own charts.

    uv run python -m atlas.build            # seconds; no corpus or lens tables needed
    uv run python -m atlas.charts           # the charts drawn from the lens tables (needs `eda.build` first)

The pages (`evidence/index.html`) read only what this writes. Three kinds of input meet here:
- the plain-English layer in `analysis/atlas/content/` (written for readers who are not data scientists);
- the notebook itself (`analysis/notebooks/01_univariate.ipynb`): each observation's own words and the charts above
  it, read by `atlas.notebook`, so the pages quote the notebook instead of copying it;
- the corpus's records of where each source came from and where it is kept (`config/sources.yaml`,
  `data/manifest.json`).

**The numbers rule.** Every number in an observation's plain-English statement, its key figures, its points and its
quoted charts must appear in the notebook's own observation or in the outputs above it (`check_numbers`). A number
that is not on the notebook's page is not a finding, so it cannot be one here either. The build fails if one is
missing.
"""

from __future__ import annotations

import hashlib
import io
import json
import re
import sys
from pathlib import Path

import yaml

from . import notebook

ROOT = Path(__file__).resolve().parents[2]
CONTENT = Path(__file__).resolve().parent / "content"
OUT = ROOT / "evidence"
DATA = OUT / "data"
CHARTS = DATA / "charts"
IMAGES = OUT / "img" / "notebook"
REPO = "https://github.com/Thomas-Amann-IPAustralia/Aus-GII-Breakdown"

LENSES = ["corpus", "rights", "timeline", "firms", "regions", "national", "industries", "institutions"]
OBS_FIELDS = {
    "id": str,
    "lens": str,
    "about": str,  # "system": what the data say about the IP system; "data": what Stage 1 learned about the data
    "headline": str,
    "statement": str,
    "figures": list,
    "points": list,
    "questions": list,
    "sources": list,
    "prep": list,
    "steps": list,
    "assumptions": list,
    "limits": list,
    "next": str,
}
OPTIONAL = {"chart", "notebook_charts", "related", "terms", "attachment", "featured"}

# A number: digits with optional thousands commas and decimals (1,439,947; 0.2686; 55.3). Observation and question
# references ({U44}, Q2), and glossary markup, are removed before numbers are read.
_NUMBER = re.compile(r"(?<![\w.])\d[\d,]*(?:\.\d+)?")
_REFS = re.compile(r"\{U\d+\}|\bQ[1-5]\b|\bU\d+\b|\bADR \d{4}\b|\bFY(?=\d)|\[\[[^\]|]+\|?|\]\]")


def numbers(text: str) -> set[str]:
    """The numbers in `text`, without thousands commas and trailing zeros after a decimal point."""
    out = set()
    for n in _NUMBER.findall(_REFS.sub(" ", text)):
        n = n.rstrip(",").replace(",", "")
        if "." in n:
            n = n.rstrip("0").rstrip(".")
        out.add(n)
    return out


def _strings(x) -> list[str]:
    """Every string inside a YAML value."""
    if isinstance(x, str):
        return [x]
    if isinstance(x, dict):
        return [s for v in x.values() for s in _strings(v)]
    if isinstance(x, list):
        return [s for v in x for s in _strings(v)]
    if isinstance(x, int | float):
        return [repr(x)]
    return []


def check_numbers(obs: dict, nb: notebook.Observation) -> list[str]:
    """The numbers in an observation's plain-English layer (and its quoted chart) that are not on the notebook's page."""
    page = numbers(nb.text + "\n" + nb.evidence_text)
    fields = [obs["headline"], obs["statement"], obs["figures"], obs["points"]]
    if isinstance(obs.get("chart"), dict):  # a chart of quoted values
        c = obs["chart"]
        fields += [c.get("series", []), c.get("views", []), c.get("x", {}).get("values", [])]
    missing = set()
    for s in _strings(fields):
        missing |= numbers(s) - page
    return sorted(missing, key=lambda n: (len(n), n))


def load_yaml(name: str):
    return yaml.safe_load((CONTENT / name).read_text(encoding="utf-8"))


def sources() -> dict:
    """Each source's record (publisher, link, licence) with its processed tables (rows, where kept, fingerprint)."""
    register = {s["id"]: s for s in yaml.safe_load((ROOT / "config" / "sources.yaml").read_text())["sources"]}
    manifest = json.loads((ROOT / "data" / "manifest.json").read_text())["sources"]
    out = {}
    for sid, s in register.items():
        m = manifest.get(sid, {})
        tables, raw = [], 0
        for name, f in sorted(m.get("files", {}).items()):
            if name.startswith("processed/"):
                tables.append(
                    {
                        "table": name.removeprefix("processed/"),
                        "rows": f.get("rows"),
                        "columns": len(f.get("columns", [])),
                        "where": f["location"],
                        "bytes": f["bytes"],
                        "sha256": f["sha256"][:12],
                        "describe": f.get("describe"),
                    }
                )
            elif name.startswith("raw/"):
                raw += 1
        derived = s["publisher"].startswith(("built here", "compiled here"))
        url = s.get("url") or ""
        out[sid] = {
            "id": sid,
            "title": s["title"],
            "publisher": s["publisher"],
            "derived": derived,  # made by this project from other sources, so its link is to the code that makes it
            "url": url if url.startswith("http") else f"{REPO}/blob/main/{url}" if url else None,
            "licence": s.get("licence"),
            "coverage": s.get("coverage"),
            "tier": s.get("tier"),
            "questions": s.get("questions", []),
            "fetched": m.get("run"),
            "raw_files": raw,
            "tables": tables,
        }
    return out


def _webp(png: bytes) -> bytes:
    from PIL import Image

    out = io.BytesIO()
    Image.open(io.BytesIO(png)).convert("RGB").save(out, "WEBP", quality=82, method=6)
    return out.getvalue()


def notebook_charts(nb: notebook.Observation, pick: list[int] | None) -> list[dict]:
    """Write the notebook's own charts above an observation as WebP, and return where they are."""
    charts = nb.charts if pick is None else [nb.charts[i] for i in pick]
    out = []
    for c in charts:
        name = f"{c.cell_id}-{c.index}.webp"
        path = IMAGES / name
        if not path.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(_webp(c.png))
        out.append({"src": f"img/notebook/{name}", "cell": c.cell_id})
    return out


def observations(nbs: dict[str, notebook.Observation]) -> tuple[list[dict], list[str]]:
    """Every observation's plain-English layer joined to the notebook, and the problems found on the way."""
    problems, out = [], []
    for lens in LENSES:
        path = CONTENT / "observations" / f"{lens}.yaml"
        if not path.exists():
            continue
        for o in yaml.safe_load(path.read_text(encoding="utf-8")) or []:
            oid = o.get("id", "?")
            for f, t in OBS_FIELDS.items():
                if not isinstance(o.get(f), t):
                    problems.append(f"{oid}: '{f}' is missing or not a {t.__name__}")
            unknown = set(o) - set(OBS_FIELDS) - OPTIONAL
            if unknown:
                problems.append(f"{oid}: unknown fields {sorted(unknown)}")
            if oid not in nbs:
                problems.append(f"{oid}: not an observation in the notebook")
                continue
            if o.get("lens") != lens:
                problems.append(f"{oid}: lens '{o.get('lens')}' in {path.name}")
            nb = nbs[oid]
            if not problems or not any(p.startswith(f"{oid}:") for p in problems):
                missing = check_numbers(o, nb)
                if missing:
                    problems.append(f"{oid}: numbers not on the notebook's page: {', '.join(missing)}")
            chart = o.pop("chart", None)
            if isinstance(chart, dict):
                chart = {"id": oid, **chart}
                CHARTS.mkdir(parents=True, exist_ok=True)
                (CHARTS / f"{oid}.json").write_text(json.dumps(chart, ensure_ascii=False, separators=(",", ":")))
                o["chart"], o["chart_origin"] = oid, "quoted"
            elif isinstance(chart, str):
                o["chart"], o["chart_origin"] = chart, "query"
            o["strength"] = nb.strength
            o["section"] = nb.section
            o["chapter"] = nb.chapter
            o["original"] = nb.text
            o["notebook_charts"] = notebook_charts(nb, o.get("notebook_charts"))
            out.append(o)
    seen = [o["id"] for o in out]
    for oid in nbs:
        if oid not in seen:
            problems.append(f"{oid}: no plain-English entry in analysis/atlas/content/observations/")
    dupes = {x for x in seen if seen.count(x) > 1}
    problems += [f"{d}: written twice" for d in sorted(dupes)]
    order = {oid: i for i, oid in enumerate(nbs)}
    out.sort(key=lambda o: order.get(o["id"], 1e9))
    return out, problems


def build(strict: bool = True) -> dict:
    nbs = {o.id: o for o in notebook.read()}
    obs, problems = observations(nbs)
    site = load_yaml("site.yaml")
    atlas = {
        "built": site["as_at"],
        "repo": REPO,
        "notebook": f"{REPO}/blob/main/analysis/notebooks/01_univariate.ipynb",
        "site": site,
        "lenses": load_yaml("lenses.yaml"),
        "questions": load_yaml("questions.yaml"),
        "glossary": load_yaml("glossary.yaml"),
        "sources": sources(),
        "observations": obs,
    }
    ids = {o["id"] for o in obs}
    for ref in sorted(set(re.findall(r"\{(U\d+)\}", json.dumps(atlas, ensure_ascii=False)))):
        if ref not in nbs:
            problems.append(f"a reference to {ref}, which is not an observation")
    terms = set(atlas["glossary"])
    for t in sorted(set(re.findall(r"\[\[([^\]|]+)", json.dumps(atlas, ensure_ascii=False)))):
        if t not in terms:
            problems.append(f"the term [[{t}]] has no entry in glossary.yaml")
    for o in obs:
        for s in o["sources"]:
            if s not in atlas["sources"]:
                problems.append(f"{o['id']}: unknown source '{s}'")
        if o.get("chart") and not (CHARTS / f"{o['chart']}.json").exists():
            problems.append(f"{o['id']}: chart '{o['chart']}' has not been drawn (run `python -m atlas.charts`)")
    if problems and strict:
        sys.exit("The evidence pages were not built:\n- " + "\n- ".join(problems))
    DATA.mkdir(parents=True, exist_ok=True)
    text = json.dumps(atlas, ensure_ascii=False, separators=(",", ":"))
    (DATA / "atlas.json").write_text(text, encoding="utf-8")
    digest = hashlib.sha256(text.encode()).hexdigest()[:10]
    print(f"evidence/data/atlas.json: {len(obs)} observations ({len(text) / 1e3:.0f} kB, {digest}); {len(ids)} ids")
    for p in problems:
        print("  problem:", p)
    return atlas


if __name__ == "__main__":
    build(strict="--draft" not in sys.argv)
