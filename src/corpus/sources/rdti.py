"""R&D Tax Incentive transparency reports: every company's R&D expenditure as claimed, by income year (ATO).

Raw: each year's xlsx (repo). Processed: `entities`, one row per company per report: name, ABN (or ACN where the
report gives one), total R&D expenditure, any amended total, income year, and the report it came from. A report can
restate earlier years (late lodgements and amendments); keep the latest report's row for a company and year.
"""

from __future__ import annotations

from ..core import Ctx
from ._ato import read_reports


def run(ctx: Ctx) -> None:
    df = read_reports(ctx, "research-and-development-tax-incentive", r"expenditure")
    df = df.rename(
        columns={
            "total_randd_expenditure": "rd_expenditure",
            "total_amended_randd_expenditure": "rd_expenditure_amended",
        }
    )
    ctx.table(df, "entities", describe="R&D Tax Incentive claimants by income year, with ABN or ACN")
