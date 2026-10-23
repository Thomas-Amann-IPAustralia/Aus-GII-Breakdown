"""OpenAlex: every cited work with an Australian institution, and the patents that cite Australian research.

Q2 and Q4: which Australian research, and which institutions' research, US patents build on (knowledge diffusion
from public research, and the commercialisation gap). Joins Reliance on Science (`reliance_on_science`, every USPTO
patent's citations to OpenAlex works) to the OpenAlex works with at least one Australian institution. Needs
`OPENALEX_API_KEY`. OpenAlex charges about US$0.0001 a call and gives each key US$1 (10,000 calls) a day free; the
full harvest takes about 13,000 calls, so a run stops before the day's allowance is spent and the next run (after
OpenAlex's daily reset) carries on where it stopped.

Two steps:
1. Every work with an Australian institution that has been cited at least once (about 2.4 million), by publication
   year: id, year, type and primary topic's field and subfield (light pages, 200 works a call). Raw: one gzipped CSV
   per year (repo), kept as each year completes.
2. For the works among those that USPTO patents cite, their Australian institutions (100 works a call; authors' names
   are not kept). Raw: the results (repo, gzipped JSON lines).

Processed:
- `au_works`: every cited work with an Australian institution (step 1).
- `cited_au_works`: the works patents cite, with the OpenAlex ids, names and types of their Australian institutions.
- `patent_citations`: every USPTO patent citation to Australian research (patent, work, reference type, confidence,
  where found), with whether the citing patent's family has an Australian applicant or inventor (`google_patents`).
"""

from __future__ import annotations

import csv
import gzip
import io
import json
import os

import duckdb
import pandas as pd

from ..core import CorpusError, Ctx, http_get, path, raw_path

API = "https://api.openalex.org/works"
FILTER = "institutions.country_code:au,cited_by_count:>0"
RESERVE_USD = 0.02  # stop with this much of the day's allowance left


class Budget(Exception):
    """The day's OpenAlex allowance is nearly spent."""


def _get(params: dict) -> dict:
    r = http_get(API, params={**params, "api_key": os.environ["OPENALEX_API_KEY"]}, timeout=120)
    left = r.headers.get("x-ratelimit-remaining-usd")
    if left is not None and float(left) < RESERVE_USD:
        raise Budget(left)
    return r.json()


def _year(ctx: Ctx, year: int) -> None:
    """Every cited Australian work of one year, by cursor paging; written only when the year is complete."""
    rows, cursor = [], "*"
    while cursor:
        d = _get(
            {
                "filter": f"{FILTER},publication_year:{year}",
                "select": "id,publication_year,type,primary_topic",
                "per_page": 200,
                "cursor": cursor,
            }
        )
        for w in d["results"]:
            t = w.get("primary_topic") or {}
            rows.append(
                (
                    w["id"].rsplit("/", 1)[-1],
                    w.get("publication_year"),
                    w.get("type"),
                    (t.get("field") or {}).get("display_name"),
                    (t.get("subfield") or {}).get("display_name"),
                )
            )
        cursor = d["meta"].get("next_cursor") if d["results"] else None
    buf = io.StringIO()
    csv.writer(buf).writerows([("work_id", "year", "type", "field", "subfield"), *rows])
    p = ctx.raw / f"au_works_{year}.csv.gz"
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "wb") as raw, gzip.GzipFile(fileobj=raw, mode="wb", mtime=0, filename="") as f:
        f.write(buf.getvalue().encode())
    ctx.log(f"{year}: {len(rows):,} works")


def _institutions(ctx: Ctx, ids: list[str]) -> None:
    """The Australian institutions of the given works, 100 a call, appended to a JSON lines file as they come."""
    p = ctx.raw / "cited_au_works.jsonl.gz"
    done = set()
    if p.exists():
        with gzip.open(p, "rt") as f:
            done = {json.loads(line)["work_id"] for line in f}
    todo = [i for i in ids if i not in done]
    ctx.log(f"institutions: {len(done):,} works done, {len(todo):,} to fetch")
    for k in range(0, len(todo), 100):
        batch = todo[k : k + 100]
        d = _get({"filter": "openalex_id:" + "|".join(batch), "select": "id,authorships", "per_page": 100})
        with gzip.open(p, "at") as out:
            for w in d["results"]:
                insts = {
                    i["id"].rsplit("/", 1)[-1]: (i.get("display_name"), i.get("type"))
                    for a in w.get("authorships") or []
                    for i in a.get("institutions") or []
                    if i.get("country_code") == "AU"
                }
                rec = {"work_id": w["id"].rsplit("/", 1)[-1], "institutions": insts}
                out.write(json.dumps(rec, ensure_ascii=False) + "\n")


def run(ctx: Ctx) -> None:
    if not os.environ.get("OPENALEX_API_KEY"):
        raise CorpusError("openalex_works needs OPENALEX_API_KEY")
    years = _get({"filter": FILTER, "group_by": "publication_year"})["group_by"]
    years = sorted(int(g["key"]) for g in years if str(g["key"]).isdigit())
    try:
        for y in years:
            if not (ctx.raw / f"au_works_{y}.csv.gz").exists():
                _year(ctx, y)
        con = duckdb.connect()
        works = con.sql(f"select * from read_csv('{ctx.raw}/au_works_*.csv.gz', header = true)").df()
        works["work_id"] = works["work_id"].astype(str)
        cites = raw_path("reliance_on_science", "pcs_oa_uspto.csv")
        con.register("works", works)
        cited = (
            con.sql(
                f"""select distinct 'W' || c.oaid as work_id
                from read_csv('{cites}', header = true, all_varchar = true) c
                join works w on w.work_id = 'W' || c.oaid order by 1"""
            )
            .df()["work_id"]
            .tolist()
        )
        _institutions(ctx, cited)
    except Budget as e:  # the finished years and institutions stay in data/raw/openalex_works/ for the next run
        raise CorpusError(
            f"openalex_works: stopped with US${e} of today's OpenAlex allowance left; progress is kept in "
            "data/raw/openalex_works/, run again after the daily reset"
        ) from e
    for p in sorted(ctx.raw.glob("*.gz")):
        ctx.keep_raw(p)
    ctx.table(works, "au_works", describe="Cited works with an Australian institution (OpenAlex)")
    with gzip.open(ctx.raw / "cited_au_works.jsonl.gz", "rt") as f:
        recs = [json.loads(line) for line in f]
    inst = pd.DataFrame(
        [(r["work_id"], i, n, t) for r in recs for i, (n, t) in r["institutions"].items()],
        columns=["work_id", "institution_id", "institution", "institution_type"],
    )
    ctx.table(inst, "cited_au_works", describe="Australian works cited by US patents, by Australian institution")
    members = path("google_patents", "members")
    pc = con.sql(
        f"""
        with au as (select distinct lower(publication_number) as patent from '{members}'
                    where country_code = 'US')
        select c.patent, 'W' || c.oaid as work_id, c.reftype, c.confscore, c.wherefound,
               c.patent in (select patent from au) as citing_au_family
        from read_csv('{cites}', header = true, all_varchar = true) c
        join works w on w.work_id = 'W' || c.oaid
        order by 2, 1
        """
    ).to_arrow_table()
    ctx.table(pc, "patent_citations", describe="USPTO patent citations to Australian research")
