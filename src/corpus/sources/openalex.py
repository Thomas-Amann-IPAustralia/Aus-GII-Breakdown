"""OpenAlex: the research output of Australian institutions (universities, companies, government, health and others).

Innovation potential by institution and field, to set beside patenting (Q2 research institutions; Q4 the
commercialisation gap). Needs a free OpenAlex API key in `OPENALEX_API_KEY` (OpenAlex no longer serves keyless
requests from shared networks). Raw: the API responses (repo, gzipped JSON). Processed: `institutions` (every
Australian institution: OpenAlex id, ROR, name, type, city, works and citations to date) and `institution_year` (works
and citations by institution and year, as OpenAlex counts them, for the last ten years), and `field_year` (works with
an Australian institution, by primary field and publication year, 2000 on).
"""

from __future__ import annotations

import datetime as dt
import gzip
import json
import os

import pandas as pd

from ..core import CorpusError, Ctx, http_get

API = "https://api.openalex.org"


def _get(path: str, params: dict) -> dict:
    return http_get(f"{API}/{path}", params={**params, "api_key": os.environ["OPENALEX_API_KEY"]}, timeout=120).json()


def _keep(ctx: Ctx, name: str, data) -> None:
    p = ctx.raw / f"{name}.json.gz"
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "wb") as raw, gzip.GzipFile(fileobj=raw, mode="wb", mtime=0, filename="") as f:
        f.write(json.dumps(data, sort_keys=True, ensure_ascii=False).encode())
    ctx.keep_raw(p, url=API)


def run(ctx: Ctx) -> None:
    if not os.environ.get("OPENALEX_API_KEY"):
        raise CorpusError("openalex: set OPENALEX_API_KEY (a free key from https://openalex.org/settings/api)")
    insts, cursor = [], "*"
    while cursor:
        d = _get("institutions", {"filter": "country_code:au", "per_page": 200, "cursor": cursor})
        insts += d["results"]
        cursor = d["meta"].get("next_cursor") if d["results"] else None
    _keep(ctx, "institutions", insts)
    rows, years = [], []
    for i in insts:
        geo = i.get("geo") or {}
        rows.append(
            {
                "id": i["id"].rsplit("/", 1)[1],
                "ror": i.get("ror"),
                "name": i.get("display_name"),
                "type": i.get("type"),
                "city": geo.get("city"),
                "region": geo.get("region"),
                "works_count": i.get("works_count"),
                "cited_by_count": i.get("cited_by_count"),
            }
        )
        for c in i.get("counts_by_year") or []:
            years.append(
                {
                    "id": rows[-1]["id"],
                    "year": c["year"],
                    "works_count": c["works_count"],
                    "cited_by_count": c["cited_by_count"],
                }
            )
    ctx.table(pd.DataFrame(rows), "institutions", describe="Australian institutions in OpenAlex")
    ctx.table(pd.DataFrame(years), "institution_year", describe="Works and citations by institution and year")
    fields = []
    for y in range(2000, dt.date.today().year + 1):
        d = _get(
            "works",
            {"filter": f"institutions.country_code:au,publication_year:{y}", "group_by": "primary_topic.field.id"},
        )
        for g in d.get("group_by", []):
            fields.append(
                {
                    "year": y,
                    "field_id": str(g["key"]).rsplit("/", 1)[-1],
                    "field": g["key_display_name"],
                    "works": g["count"],
                }
            )
    _keep(ctx, "field_year", fields)
    ctx.table(pd.DataFrame(fields), "field_year", describe="Works with an Australian institution by field and year")
