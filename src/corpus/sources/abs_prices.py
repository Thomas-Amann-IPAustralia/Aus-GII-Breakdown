"""Prices, wages and living costs (ABS Data API): the cost-of-living background, and the deflators for money series.

For Q1, Q2, Q4 and Q5: fees, R&D claims and contract values in real terms, and whether cost-of-living pressure moves
with IP filing over time (context, not effect; series that trend together over decades correlate whatever their link,
so comparisons use changes). Australia by state capital, quarterly unless noted:

- `CPI`: the Consumer Price Index, all groups and every expenditure group and class, quarterly from 1948-Q3 and
  monthly from 2017-09 (one flow holds both; `frequency` tells them apart, and an analysis uses one, never both).
  Index numbers are on one base, September 2025 = 100.
- `LCI`: Selected Living Cost Indexes by household type (employees, age pensioners, self-funded retirees and others),
  from 1998-Q2. Closer than the CPI to what each kind of household pays (they include mortgage interest).
- `WPI`: the Wage Price Index by sector and industry, from 1997-Q3.
- `RPPI`: the Residential Property Price Index, 2002-Q1 to 2021-Q4 (the ABS has discontinued it).

Each flow is in the raw tidy form of the ABS sources: a code and a label for every dimension (measure, index,
adjustment, region and so on), then `value`, the unit and the observation status. Raw: each flow's CSV (repo, gzipped).
Processed: one table per flow, named after the flow in lower case.
"""

from __future__ import annotations

from ..core import Ctx
from ._abs import fetch_flow, flows

FLOWS = ["CPI", "LCI", "WPI", "RPPI"]


def run(ctx: Ctx) -> None:
    names = flows()
    for f in FLOWS:
        if f not in names:
            ctx.note(f"abs_prices: {f} is no longer in the ABS Data API; left out")
            continue
        df = fetch_flow(ctx, f)
        ctx.table(df, f.lower(), describe=names[f])
