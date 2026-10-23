"""Global Innovation Index 2026 (WIPO): every economy's score, rank and value on every node of the index.

Context for the research (Q4: where Australia stands, and hypotheses about where to look). Raw: WIPO's data file and
Appendix III (repo, as uploaded). Processed: `structure` (the index tree: number, name, level, type, profile,
description, source), `economies` (income group, region, population, GDP), and `data` (one row per economy and node:
the screened value and its data year, the 0-100 score, the rank, and WIPO's strength and weakness flags).
The page in `index.html` reads a frozen summary in `assets/data/gii-australia.json`.
"""

from __future__ import annotations

import re

import pandas as pd

from ..core import CorpusError, Ctx


def _sheet(sheets: dict, name: str) -> pd.DataFrame:
    if name not in sheets:
        raise CorpusError(f"gii: the data file has no '{name}' sheet")
    df = sheets[name]
    df.columns = [re.sub(r"[^a-z0-9]+", "_", str(c).lower()).strip("_") for c in df.columns]
    return df


def run(ctx: Ctx) -> None:
    xlsx = ctx.keep_raw(ctx.raw / "gii-2026-data.xlsx")
    ctx.keep_raw(ctx.raw / "gii-2026-appendix-3-sources-and-definitions.md")
    sheets = pd.read_excel(xlsx, sheet_name=None, engine="calamine", dtype=str)
    structure = _sheet(sheets, "Index Structure")
    economies = _sheet(sheets, "Economies")
    data = _sheet(sheets, "Data")
    for c in ("pop", "pppgdp", "ppppc"):
        economies[c] = pd.to_numeric(economies[c], errors="coerce")
    for c in ("value_screen", "score", "rank", "datayr"):
        if c in data:
            data[c] = pd.to_numeric(data[c], errors="coerce")
    data["num"] = data["num"].fillna("")
    structure["num"] = structure["num"].fillna("")
    ctx.table(structure, "structure", describe="The GII 2026 tree")
    ctx.table(economies, "economies", describe="GII 2026 economies")
    ctx.table(data, "data", describe="Every economy's value, score and rank on every GII node")
