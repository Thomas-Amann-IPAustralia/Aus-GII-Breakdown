"""Corporate Tax Transparency: total income, taxable income and tax payable of large corporate entities (ATO).

Covers entities with total income of $100 million or more (and, for private Australian-owned companies, $200 million
before 2022-23). Raw: each year's xlsx (repo). Processed: `entities`, one row per entity per income year.
"""

from __future__ import annotations

from ..core import Ctx
from ._ato import read_reports


def run(ctx: Ctx) -> None:
    df = read_reports(ctx, "corporate-transparency", r"total_income")
    ctx.table(df, "entities", describe="Large corporate entities' income and tax by income year, with ABN")
