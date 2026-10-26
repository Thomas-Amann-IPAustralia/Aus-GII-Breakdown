"""ROR, the Research Organization Registry: every Australian research organisation's identifier, names and links.

The key of the `institutions` lens (ADR 0021): ROR identifiers join OpenAlex (which carries each institution's ROR),
the NHMRC (whose workbooks give the administering institution's ROR from the 2025 round) and, through the names and
aliases kept here, the ARC's administering organisations and IP RAPID's applicants. Free, no key, CC0. Raw: ROR's data
dump (one Zenodo release, every organisation in the world; R2), from which every Australian record, active, inactive
and withdrawn, is kept. The API is not used: its pages are not in a stable order, so paging through a query returns some
records twice and misses others (2,052 rows for 1,518 records). Processed:
- `organisations`: one row per ROR record: id, display name, types, status, the year established, state and city,
  website, and its Wikidata, GRID and ISNI ids;
- `names`: one row per record and name (display name, labels, aliases and acronyms), for matching;
- `relationships`: one row per record and related record (parent, child, related, predecessor, successor), as ROR
  gives them.
"""

from __future__ import annotations

import json
import zipfile

import pandas as pd

from ..core import Ctx, raw_path

RECORD = "https://zenodo.org/api/records/23500708/files/"  # ROR Data v2.15, 2026-10-20
DUMP = "v2.15-2026-10-20-ror-data.zip"


def _australian(zpath) -> list[dict]:
    """Every record with a location in Australia, from the dump's JSON (schema 2), sorted by id."""
    with zipfile.ZipFile(zpath) as z:
        with z.open(next(n for n in z.namelist() if n.endswith(".json"))) as f:
            items = json.load(f)
    au = [
        o
        for o in items
        if any((loc.get("geonames_details") or {}).get("country_code") == "AU" for loc in o.get("locations") or [])
    ]
    return sorted(au, key=lambda o: o["id"])


def _rows(items: list[dict]) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    orgs, names, rels = [], [], []
    for o in items:
        rid = o["id"].rsplit("/", 1)[1]
        display = next((n["value"] for n in o["names"] if "ror_display" in n["types"]), None)
        geo = (o.get("locations") or [{}])[0].get("geonames_details") or {}
        ext = {e["type"]: e.get("preferred") or (e.get("all") or [None])[0] for e in o.get("external_ids") or []}
        site = next((x["value"] for x in o.get("links") or [] if x["type"] == "website"), None)
        orgs.append(
            {
                "ror": rid,
                "name": display,
                "types": " ".join(o.get("types") or []),
                "status": o.get("status"),
                "established": o.get("established"),
                "state": geo.get("country_subdivision_code"),
                "city": geo.get("name"),
                "website": site,
                "wikidata": ext.get("wikidata"),
                "grid": ext.get("grid"),
                "isni": ext.get("isni"),
            }
        )
        for n in o["names"]:
            names.append({"ror": rid, "name": n["value"], "name_types": " ".join(n["types"]), "lang": n.get("lang")})
        for r in o.get("relationships") or []:
            rels.append({"ror": rid, "type": r["type"], "related_ror": r["id"].rsplit("/", 1)[1], "label": r["label"]})
    return pd.DataFrame(orgs), pd.DataFrame(names), pd.DataFrame(rels)


def _tables(ctx: Ctx, items: list[dict]) -> None:
    orgs, names, rels = _rows(items)
    ctx.table(orgs, "organisations", describe="Australian research organisations in ROR")
    ctx.table(names, "names", describe="Every name, alias and acronym of each Australian ROR record")
    ctx.table(rels, "relationships", describe="Each Australian ROR record's parents, children and successors")


def run(ctx: Ctx) -> None:
    _tables(ctx, _australian(ctx.fetch(RECORD + DUMP + "/content", DUMP, keep="r2")))


def reprocess(ctx: Ctx, tables: list[str] | None = None) -> None:
    _tables(ctx, _australian(raw_path("ror", DUMP)))
