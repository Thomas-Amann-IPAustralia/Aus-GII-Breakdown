"""The Labour Force Survey (ABS Data API): employment and unemployment, and how many people run their own business.

Background for the timeline and national lenses (Q2, Q4, Q5): the labour market around each policy change, and the
open count of owner-managers, the denominator for who runs businesses (TableBuilder's Census counts, by postal area,
need an account; `docs/tablebuilder-owner-managers.md`). Monthly, Australia, and the states for `LF`:

- `LF`: the headline series: labour force, employed (full-time and part-time), unemployed, unemployment and
  participation rates, and the employment-to-population ratio, by sex and state, from 1978, each as original,
  seasonally adjusted and trend. An analysis uses one adjustment type, never several.
- `LF_STAT_EMP`: employed persons by status in employment of their main job: employees; owner-managers of
  incorporated and of unincorporated enterprises, each with or without employees; contributing family workers. By sex,
  for Australia, from 1991, in thousands (original, not seasonally adjusted). Owner-managers are people, not
  businesses, counted by their main job.

Each flow is in the raw tidy form of the ABS sources (a code and a label for every dimension, then `value`, the unit,
the multiplier and the observation status). Raw: each flow's CSV (repo, gzipped). Processed: one table per flow, named
after the flow in lower case.
"""

from __future__ import annotations

from ..core import Ctx
from ._abs import fetch_flow, flows

FLOWS = ["LF", "LF_STAT_EMP"]


def run(ctx: Ctx) -> None:
    names = flows()
    for f in FLOWS:
        if f not in names:
            ctx.note(f"abs_labour: {f} is no longer in the ABS Data API; left out")
            continue
        df = fetch_flow(ctx, f)
        ctx.table(df, f.lower(), describe=names[f])
