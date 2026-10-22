"""NATSEM small-area synthetic estimates of life satisfaction and generalised trust (SA2).

Wellbeing and social cohesion by place, beside regional IP use (context, not effect). CC BY-NC 4.0. This environment
cannot fetch it: put the files in data/raw/natsem/ and run `corpus run natsem`. To get them: From data.gov.au, the
AURIN download manager links on 'NATSEM - Life Satisfaction Indicators - Synthetic Estimates SA2 2016', 'NATSEM -
Trust Indicators - Synthetic Estimates SA2 2016' and 'SA2 OECD Indicators: Estimates of Generalised Trust (Synthetic
Data) 2011', as CSV. AURIN's servers refuse this environment.

Processed: one table per file (and per sheet of a workbook), all columns as text; see `_manual.read_dropped`.
"""

from __future__ import annotations

from ..core import Ctx
from ._manual import read_dropped

HOW = (
    "From data.gov.au, the AURIN download manager links on 'NATSEM - Life Satisfaction Indicators - Synthetic "
    "Estimates SA2 2016', 'NATSEM - Trust Indicators - Synthetic Estimates SA2 2016' and 'SA2 OECD Indicators: "
    "Estimates of Generalised Trust (Synthetic Data) 2011', as CSV. AURIN's servers refuse this environment."
)


def run(ctx: Ctx) -> None:
    read_dropped(ctx, HOW)
