"""The evidence register: the literature and evaluations behind the research questions, checked against Crossref.

Raw: `register.yaml` (repo; compiled by hand, add to it freely). For each journal item (with a `venue`) the module asks
Crossref for the closest match to its title and first author, and records the DOI, the title Crossref has and a
similarity score; `match` is false below 0.85, so a reference that does not check out is flagged rather than trusted.
Processed: `register` (one row per item). Also writes docs/evidence-register.md, the register as a readable list.
"""

from __future__ import annotations

import difflib
import re

import pandas as pd
import yaml

from ..core import ROOT, Ctx, http_get


def _norm(s: str) -> str:
    return re.sub(r"[^a-z0-9 ]+", "", s.lower().replace("“", "").replace("”", ""))


def _sim(a: str, b: str) -> float:
    return difflib.SequenceMatcher(None, _norm(a), _norm(b)).ratio()


def _year(x: dict) -> int | None:
    return ((x.get("issued") or {}).get("date-parts") or [[None]])[0][0]


def _crossref(it: dict) -> tuple[dict | None, float]:
    """The published version: a candidate within two years of the cited year, scored on title and then venue."""
    first = it["authors"].split(",")[0]
    found = http_get(
        "https://api.crossref.org/works",
        params={
            "query.bibliographic": f"{it['title']} {first}",
            "query.container-title": it["venue"],
            "rows": 10,
        },
    ).json()["message"]["items"]
    near = [x for x in found if _year(x) and abs(_year(x) - int(it["year"])) <= 2] or found

    def key(x):
        return _sim(it["title"], (x.get("title") or [""])[0]) + 0.5 * _sim(
            it["venue"], (x.get("container-title") or [""])[0]
        )

    best = max(near, key=key, default=None)
    score = _sim(it["title"], (best.get("title") or [""])[0]) if best else 0.0
    if score < 0.85:  # law reviews and books are thinly indexed by venue; try the title alone
        found = http_get(
            "https://api.crossref.org/works", params={"query.bibliographic": f"{it['title']} {first}", "rows": 10}
        ).json()["message"]["items"]
        alt = max(found, key=lambda x: _sim(it["title"], (x.get("title") or [""])[0]), default=None)
        alt_score = _sim(it["title"], (alt.get("title") or [""])[0]) if alt else 0.0
        if alt_score > score:
            best, score = alt, alt_score
    return best, score


def run(ctx: Ctx) -> None:
    path = ctx.raw / "register.yaml"
    ctx.keep_raw(path)
    items = yaml.safe_load(path.read_text("utf-8"))["items"]
    rows = []
    for it in items:
        row = {k: it.get(k) for k in ("id", "kind", "authors", "year", "title", "venue", "url", "why")}
        row["questions"] = ",".join(str(q) for q in it.get("questions", []))
        if it.get("venue") and it.get("kind") in ("study", "review", "data"):
            best, score = _crossref(it)
            if best:
                row.update(
                    doi=best.get("DOI"),
                    crossref_title=(best.get("title") or [None])[0],
                    crossref_year=_year(best),
                    crossref_venue=(best.get("container-title") or [None])[0],
                    similarity=round(score, 3),
                    match=score >= 0.85,
                )
            if not best or score < 0.85:
                ctx.note(f"evidence: {it['id']} did not match Crossref well ({score:.2f})")
        rows.append(row)
    df = pd.DataFrame(rows)
    ctx.table(df, "register", describe="Evidence register with Crossref checks")
    lines = [
        "# Evidence register",
        "",
        "Compiled from `data/raw/evidence/register.yaml` by `corpus run evidence`; edit the YAML, not this file.",
        "Journal items are checked against Crossref (DOI shown where the title matched).",
        "",
    ]
    for kind, g in df.groupby("kind", sort=False):
        lines += [f"## {kind.capitalize()}", ""]
        for r in g.itertuples():
            ref = f"{r.authors} ({r.year}). {r.title}."
            if isinstance(r.venue, str):
                ref += f" *{r.venue}*."
            doi = getattr(r, "doi", None)
            if isinstance(doi, str) and getattr(r, "match", False):
                ref += f" https://doi.org/{doi}"
            elif isinstance(r.url, str):
                ref += f" {r.url}"
            lines += [f"- {ref} Questions {r.questions}. {r.why}"]
        lines.append("")
    (ROOT / "docs/evidence-register.md").write_text("\n".join(lines), encoding="utf-8")
