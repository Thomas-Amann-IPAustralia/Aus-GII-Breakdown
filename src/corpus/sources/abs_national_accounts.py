"""Australian National Accounts (ABS Data API): GDP, state final demand and gross value added by industry, quarterly
(gap B2).

Context for the timeline and the industries lens (Q1, Q4): IP filing over time read beside the economy's size and
cycle, by state and by industry. Flows, in the raw tidy form of the ABS sources (a code and a label for every
dimension, then `value`, the unit and the observation status):

- `ANA_AGG`: key aggregates (GDP and its per-person and price measures), quarterly from 1959.
- `ANA_SFD`: state final demand by state, quarterly.
- `ANA_IND_GVA`: gross value added by ANZSIC division, quarterly.

Raw: each flow's CSV (repo, gzipped, or R2 when large). Processed: one table per flow, named after it in lower case.
"""

from __future__ import annotations

from ..core import Ctx
from ._abs import fetch_flow, flows

FLOWS = ["ANA_AGG", "ANA_SFD", "ANA_IND_GVA"]


def run(ctx: Ctx) -> None:
    names = flows()
    for f in FLOWS:
        if f not in names:
            ctx.note(f"abs_national_accounts: {f} is no longer in the ABS Data API; left out")
            continue
        df = fetch_flow(ctx, f, keep="auto")
        ctx.table(df, f.lower(), describe=names[f])
