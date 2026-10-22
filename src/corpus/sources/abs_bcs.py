"""ABS Business Characteristics Survey and the characteristics of Australian business series, from the ABS Data API.

Innovation activity and status, methods and collaboration, finance, barriers to innovation and to business activity,
markets and competition, performance, IT use, by employment size, industry (ANZSIC 2006) and region where published.
Raw: each flow's CSV (repo, gzipped). Processed: one tidy table per flow, named after the flow in lower case.
"""

from __future__ import annotations

from ..core import Ctx
from ._abs import fetch_flow, flows

FLOWS = [
    "BCS_INN",  # innovation: collaboration, fee-for-service, financing, assessment
    "BCS_INNACT",  # innovation activity: implemented, in development, abandoned
    "BCS_INNSIG",  # most significant innovation: target markets, commercialisation
    "BCS_BUSINF",  # business information and performance
    "BCS_BUSINF2",  # business profile, performance and arrangements, 2021-22
    "BCS_BUSGVTSK",  # interaction with government, and skills, 2021-22
    "ABS_IT_BARRIER",  # barriers to business activity and to innovation
    "ABS_IT_INNOVATION",
    "ABS_IT_FINANCE",
    "ABS_IT_MKTCOMP",  # markets and competition
    "ABS_IT_PERF",
    "ABS_IT_BUS_STRUC",
    "ABS_IT_SUPPORT",  # IT use
]


def run(ctx: Ctx) -> None:
    names = flows()
    for f in FLOWS:
        if f not in names:
            ctx.note(f"abs_bcs: {f} is no longer in the ABS Data API; left out")
            continue
        df = fetch_flow(ctx, f)
        ctx.table(df, f.lower(), describe=names[f])
