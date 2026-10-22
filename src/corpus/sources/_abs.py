"""Shared by the ABS sources: a dataflow from the ABS Data API (SDMX) as a tidy table.

Each flow's CSV (with labels) is kept gzipped in data/raw/<source>/. The tidy table has, for every dimension, a code
column and a `_label` column (the API's "CODE: Label" split), then `value`, the unit and the observation status.
"""

from __future__ import annotations

import gzip
import re

import pandas as pd

from ..core import CorpusError, Ctx, http_get

API = "https://data.api.abs.gov.au/rest"


def snake(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")


def flows() -> dict[str, str]:
    """Every ABS dataflow id and its name."""
    r = http_get(f"{API}/dataflow/ABS?detail=allstubs", headers={"Accept": "application/vnd.sdmx.structure+json"})
    return {f["id"]: f["name"] for f in r.json()["data"]["dataflows"]}


def fetch_flow(ctx: Ctx, flow: str, key: str = "all", keep: str = "repo") -> pd.DataFrame:
    url = f"{API}/data/ABS,{flow}/{key}"
    r = http_get(
        url,
        params={"dimensionAtObservation": "AllDimensions"},
        headers={"Accept": "application/vnd.sdmx.data+csv;labels=both"},
        timeout=600,
    )
    name = f"{flow}.csv.gz" if key == "all" else f"{flow}.{snake(key)}.csv.gz"
    dest = (ctx.raw if keep == "repo" else ctx.cache) / name
    dest.parent.mkdir(parents=True, exist_ok=True)
    with open(dest, "wb") as raw, gzip.GzipFile(fileobj=raw, mode="wb", mtime=0, filename="") as f:
        f.write(r.content)  # mtime=0: the same response gives the same bytes
    ctx.keep_raw(dest, keep=keep, url=url)
    return tidy(pd.read_csv(dest, dtype=str, keep_default_na=False), flow)


def tidy(raw: pd.DataFrame, flow: str) -> pd.DataFrame:
    if "OBS_VALUE" not in raw:
        raise CorpusError(f"abs: {flow} has no OBS_VALUE column; has the API changed?")
    out = {}
    for col in raw.columns:
        if col in ("DATAFLOW", "OBS_VALUE"):
            continue
        code, _, label = col.partition(": ")
        name = snake(label or code)
        parts = raw[col].str.split(": ", n=1, expand=True)
        out[name] = parts[0].replace("", None)
        if parts.shape[1] > 1 and parts[1].notna().any():
            out[f"{name}_label"] = parts[1]
    df = pd.DataFrame(out)
    df.insert(0, "flow", flow)
    df["value"] = pd.to_numeric(raw["OBS_VALUE"], errors="coerce")
    return df
