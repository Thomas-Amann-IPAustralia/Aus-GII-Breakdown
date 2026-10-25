"""R&D Tax Incentive transparency reports: every company's R&D expenditure as claimed, by income year (ATO).

Raw: each year's xlsx (repo). Processed: `entities`, one row per company per report: name, ABN (or ACN where the
report gives one), total R&D expenditure, any amended total, income year, and the report it came from. A report can
restate earlier years (late lodgements and amendments); keep the latest report's row for a company and year, with
its amended total where there is one.

Where a report gives only an ACN, the ABN is taken from the ABR when exactly one ABN has that ACN (`abn_from` is
`acn`; otherwise `report`): 521 of the 551 rows without an ABN, $228 million of R&D, which would otherwise drop
out of every join on ABN. The other 30 ($16 million) have no usable identifier.
"""

from __future__ import annotations

import duckdb
import pandas as pd

from ..core import Ctx, path
from ._ato import read_reports


def abn_from_acn(df: pd.DataFrame, abns: str) -> pd.DataFrame:
    """Fill `abn` from the ABR (`abns`, a Parquet path) where the row has only an ACN that one ABN holds."""
    con = duckdb.connect()
    con.register("r", df[df.abn.isna() & df.acn.notna()][["acn"]].drop_duplicates())
    m = con.execute(f"""SELECT acn, any_value(abn) AS abr_abn FROM '{abns}'
        WHERE acn IN (SELECT acn FROM r) GROUP BY 1 HAVING count(*) = 1""").df()
    out = df.merge(m, on="acn", how="left")
    out["abn_from"] = "report"
    fill = out.abn.isna() & out.abr_abn.notna()
    out.loc[fill, "abn"] = out.loc[fill, "abr_abn"]
    out.loc[fill, "abn_from"] = "acn"
    out.loc[out.abn.isna(), "abn_from"] = None
    return out.drop(columns="abr_abn")


def run(ctx: Ctx) -> None:
    df = read_reports(ctx, "research-and-development-tax-incentive", r"expenditure")
    df = df.rename(
        columns={
            "total_randd_expenditure": "rd_expenditure",
            "total_amended_randd_expenditure": "rd_expenditure_amended",
        }
    )
    df = abn_from_acn(df, str(path("abr", "abns")))
    ctx.table(df, "entities", describe="R&D Tax Incentive claimants by income year, with ABN or ACN")
