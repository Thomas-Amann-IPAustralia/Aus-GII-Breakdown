"""PBS date-of-supply data: prescriptions and costs for every PBS item by month (Department of Health, Disability
and Ageing), for the health pathway of public value (section 2 of docs/data-plan.md): what the public pays for
medicines, which can be followed through patent expiry and IPGOD's pharmaceutical extensions of term.

Raw: every file on the date-of-supply page (R2). Processed: `supply` (every row of the yearly CSVs, July 2020 on:
month, item, drug type, patient category, pharmacy type, script type, prescriptions and the patient, government and
total cost; R2), `item_month` (prescriptions and costs by item and month, summed over the breakdowns; repo) and
`item_drug_map` (item code to drug name, form and strength, and ATC code; repo). The xlsx summary (from July 2022)
and the older date-of-processing zip (to January 2018) are kept raw only.
"""

from __future__ import annotations

import re

import duckdb
import pandas as pd

from ..core import CorpusError, Ctx, http_get

PAGE = "https://www.pbs.gov.au/info/statistics/dos-and-dop/dos-and-dop"
BASE = "https://www.pbs.gov.au"


def run(ctx: Ctx) -> None:
    links = sorted(set(re.findall(r'href="([^"]+\.(?:csv|xlsx|zip))"', http_get(PAGE).text)))
    if not links:
        raise CorpusError("pbs: no files on the date-of-supply page")
    yearly, mapping = [], None
    for link in links:
        name = link.rsplit("/", 1)[1]
        keep = "repo" if name == "pbs-item-drug-map.csv" else "r2"
        f = ctx.fetch(BASE + link if link.startswith("/") else link, name, keep=keep)
        if re.match(r"dos-jul-\d{4}-to-jun-\d{4}-phrmcy-type\.csv", name):
            yearly.append(str(f))
        elif name == "pbs-item-drug-map.csv":
            mapping = f
    if mapping is not None:
        m = pd.read_csv(mapping, dtype=str, encoding="latin-1")
        m.columns = [re.sub(r"[^a-z0-9]+", "_", c.lower()).strip("_") for c in m.columns]
        ctx.table(m, "item_drug_map", describe="PBS item code to drug, form and strength, ATC")
    con = duckdb.connect()
    files = ", ".join(f"'{f}'" for f in yearly)
    out = ctx.cache / "processed/supply.parquet"
    out.parent.mkdir(parents=True, exist_ok=True)
    con.execute(f"""COPY (SELECT * REPLACE (CAST(MONTH_OF_SUPPLY AS VARCHAR) AS MONTH_OF_SUPPLY)
        FROM read_csv([{files}], union_by_name=true, header=true)) TO '{out}' (FORMAT parquet, COMPRESSION zstd)""")
    rows = con.execute(f"SELECT count(*) FROM '{out}'").fetchone()[0]
    cols = [r[0] for r in con.execute(f"DESCRIBE SELECT * FROM '{out}'").fetchall()]
    ctx.keep_table(out, "supply", rows, cols, keep="r2", describe="Every date-of-supply row, July 2020 on")
    im = con.execute(f"""SELECT MONTH_OF_SUPPLY AS month, ITEM_CODE AS item_code, sum(PRESCRIPTIONS) AS prescriptions,
        sum(PATIENT_CONTRIB) AS patient_contribution, sum(GOVT_CONTRIB) AS government_contribution,
        sum(TOTAL_COST) AS total_cost FROM '{out}' GROUP BY 1, 2 ORDER BY 1, 2""").df()
    ctx.table(im, "item_month", describe="Prescriptions and costs by PBS item and month")
