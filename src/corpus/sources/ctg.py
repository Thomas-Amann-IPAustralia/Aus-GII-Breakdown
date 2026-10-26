"""Closing the Gap Annual Data Compilation Report 2026, targets 8, 15 and 16 (Productivity Commission).

Context for a First Nations workstream (economic participation; land and waters; cultures and languages): they
describe the setting, not the IP system's effect. Raw: the three targets' CSVs (repo, as uploaded). Processed: `data`,
long, one value per row: the descriptive columns as published, `jurisdiction` (NSW to NT, Aus Gov, Total, Aust) and
`value` (numeric where the cell is a number; `value_text` keeps the cell, for '..', 'np' and the like). Target 15's
"Aus Gov" column (land and sea held by the Australian Government) is a jurisdiction like the states (ADR 0019).
"""

from __future__ import annotations

import pandas as pd

from ..core import CorpusError, Ctx

JURISDICTIONS = ["NSW", "Vic", "Qld", "WA", "SA", "Tas", "ACT", "NT", "Aus Gov", "Total", "Aust"]
DESCRIPTIVE = {
    "Table_Number",
    "Year",
    "Measure",
    "Age",
    "Sex",
    "Indigenous_Status",
    "Remoteness",
    "SEIFA_IRSD",
    "Description1",
    "Description2",
    "Description3",
    "Description4",
    "Description6",
    "Description7",
    "Uncertainty",
    "Data_Source",
    "Unit",
}


def run(ctx: Ctx) -> None:
    _build(ctx)


def reprocess(ctx: Ctx, tables: list[str] | None = None) -> None:
    """The table again from the raw CSVs in the repo (the same as `run`: this source fetches nothing)."""
    _build(ctx)


def _build(ctx: Ctx) -> None:
    frames = []
    for f in sorted(ctx.raw.glob("ctg*.csv")):
        ctx.keep_raw(f)
        df = pd.read_csv(f, dtype=str)
        unknown = set(df.columns) - set(JURISDICTIONS) - DESCRIPTIVE
        if unknown:  # a new column could be a jurisdiction that would otherwise stay unmelted, as "Aus Gov" did
            raise CorpusError(f"ctg: {f.name} has columns this parser does not know: {sorted(unknown)}")
        ids = [c for c in df.columns if c not in JURISDICTIONS]
        long = df.melt(
            id_vars=ids,
            value_vars=[c for c in JURISDICTIONS if c in df],
            var_name="jurisdiction",
            value_name="value_text",
        )
        long = long.dropna(subset=["value_text"])
        long["value"] = pd.to_numeric(long["value_text"].str.replace(",", ""), errors="coerce")
        long.insert(0, "target", f.stem.split("-")[0])
        frames.append(long)
    out = pd.concat(frames, ignore_index=True)
    out.columns = [c.lower() for c in out.columns]
    ctx.table(out, "data", describe="Targets 8, 15 and 16, long")
