"""ARC National Competitive Grants Program: every grant the Australian Research Council has announced since 2001.

Public research funding by scheme (Discovery, Linkage and others), administering organisation, field of research and
year; Linkage grants are research done with industry and other partners. Raw: the API's pages (repo, gzipped JSON).
Processed: `grants`, one row per grant with every attribute the API gives (nested scheme fields flattened; lists as
'; '-joined text).
"""

from __future__ import annotations

import gzip
import json

import pandas as pd

from ..core import Ctx, http_get

API = "https://dataportal.arc.gov.au/NCGP/API/grants"


def _flat(a: dict, prefix: str = "") -> dict:
    out = {}
    for k, v in a.items():
        key = (prefix + k).replace("-", "_")
        if isinstance(v, dict):
            out.update(_flat(v, key + "_"))
        elif isinstance(v, list):
            out[key] = "; ".join(json.dumps(x, ensure_ascii=False) if isinstance(x, dict) else str(x) for x in v)
        else:
            out[key] = v.strip() if isinstance(v, str) else v
    return out


def run(ctx: Ctx) -> None:
    data, page, pages = [], 1, 1
    while page <= pages:
        d = http_get(API, params={"page[size]": 1000, "page[number]": page}, timeout=300).json()
        pages = d["meta"]["total-pages"]
        data += d["data"]
        page += 1
    p = ctx.raw / "grants.json.gz"
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "wb") as raw, gzip.GzipFile(fileobj=raw, mode="wb", mtime=0, filename="") as f:
        f.write(json.dumps(data, sort_keys=True, ensure_ascii=False).encode())
    ctx.keep_raw(p, url=API)
    df = pd.DataFrame([{"id": g["id"], **_flat(g["attributes"])} for g in data])
    ctx.table(df, "grants", describe="ARC grants, every attribute")
