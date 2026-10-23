"""Closing the Gap Annual Data Compilation Report 2026, targets 8, 15 and 16 (Productivity Commission).

Context for a First Nations workstream (economic participation; land and waters; cultures and languages): they
describe the setting, not the IP system's effect. Raw: the three targets' CSVs (repo, as uploaded). Processed: `data`,
long, one value per row: the descriptive columns as published, `jurisdiction` (NSW to NT, Total, Aust) and `value`
(numeric where the cell is a number; `value_text` keeps the cell, for '..', 'np' and the like).
"""

from __future__ import annotations

import pandas as pd

from ..core import Ctx

JURISDICTIONS = ["NSW", "Vic", "Qld", "WA", "SA", "Tas", "ACT", "NT", "Total", "Aust"]


def run(ctx: Ctx) -> None:
    frames = []
    for f in sorted(ctx.raw.glob("ctg*.csv")):
        ctx.keep_raw(f)
        df = pd.read_csv(f, dtype=str)
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
