"""PBS date-of-supply data: prescriptions and costs for every PBS item by month (Department of Health, Disability
and Ageing), for the health pathway of public value (section 2 of docs/data-plan.md): what the public pays for
medicines, which can be followed through patent expiry and IP RAPID's pharmaceutical extensions of term.

Raw: every file on the date-of-supply page (R2). Processed: `supply` (every row of the yearly CSVs, July 2020 on:
month, item, drug type, patient category, pharmacy type, script type, prescriptions and the patient, government and
total cost; R2), `item_month` (prescriptions and costs by item and month, summed over the breakdowns; repo) and
`item_drug_map` (item code to drug name, form and strength, and ATC code; repo). The older date-of-processing zip (to
January 2018) is kept raw only.

The yearly CSVs are by pharmacy type and hold only Section 85 (the general schedule) and the Repatriation PBS. The
workbook of monthly totals (`dos-jul-2022-to-...xlsx`, one sheet a financial year from July 2022) also holds Section
100, the highly specialised drugs and chemotherapy dispensed through hospitals, about 30% of the government's cost
(gap B11). Processed: `monthly`, every row of the workbook: month, item, ATC code, drug name, patient category,
section (`drug_type`: Section 85, Section 100, RPBS or Unknown), script type, prescriptions and the patient,
government, retail mark-up, total and net patient costs. The workbook and the CSVs are never added together.
"""

from __future__ import annotations

import re

import duckdb
import pandas as pd

from ..core import CorpusError, Ctx, http_get, raw_path, read_manifest

PAGE = "https://www.pbs.gov.au/info/statistics/dos-and-dop/dos-and-dop"
BASE = "https://www.pbs.gov.au"


MONTHLY = {
    "MONTH_OF_SUPPLY": "month", "ITEM_CODE": "item_code", "ATC5_CODE": "atc5_code", "DRUG_NAME": "drug_name",
    "PTNT_CTGRY_DRVD_CD": "patient_category", "DRG_TYP_CTGRY": "drug_type", "SCRIPT_TYPE": "script_type",
    "PRSCRPTN_CNT": "prescriptions", "PATIENT_CONTRIB": "patient_contribution",
    "GOVT_CONTRIB": "government_contribution", "RETAIL_MARKUP": "retail_markup", "TOTAL_COST": "total_cost",
    "PATIENT_NET_CONTRIB": "patient_net_contribution",
}  # fmt: skip


MONTHLY_DESCRIBE = "PBS monthly totals by item, section and patient category, July 2022 on"


def monthly(path) -> pd.DataFrame:
    """Every sheet of the monthly workbook (one per financial year), one row per month, item, patient category, section
    and script type; the month as YYYYMM text, as in the CSVs."""
    from python_calamine import CalamineWorkbook

    wb = CalamineWorkbook.from_path(str(path))
    frames = []
    for name in wb.sheet_names:
        rows = wb.get_sheet_by_name(name).to_python()
        df = pd.DataFrame(rows[1:], columns=rows[0])
        missing = set(MONTHLY) - set(df.columns)
        if missing:
            raise CorpusError(f"pbs: sheet {name} lacks {sorted(missing)}")
        frames.append(df[list(MONTHLY)].rename(columns=MONTHLY))
    out = pd.concat(frames, ignore_index=True)
    out["month"] = out["month"].astype(float).astype(int).astype(str)
    for c in ("prescriptions", "patient_contribution", "government_contribution", "retail_markup", "total_cost",
              "patient_net_contribution"):  # fmt: skip
        out[c] = pd.to_numeric(out[c], errors="coerce")
    return out


def run(ctx: Ctx) -> None:
    links = sorted(set(re.findall(r'href="([^"]+\.(?:csv|xlsx|zip))"', http_get(PAGE).text)))
    if not links:
        raise CorpusError("pbs: no files on the date-of-supply page")
    yearly, mapping, book = [], None, None
    for link in links:
        name = link.rsplit("/", 1)[1]
        keep = "repo" if name == "pbs-item-drug-map.csv" else "r2"
        f = ctx.fetch(BASE + link if link.startswith("/") else link, name, keep=keep)
        if re.match(r"dos-jul-\d{4}-to-jun-\d{4}-phrmcy-type\.csv", name):
            yearly.append(str(f))
        elif name == "pbs-item-drug-map.csv":
            mapping = f
        elif re.match(r"dos-jul-2022-.*\.xlsx$", name):
            book = f
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
    if book is None:
        raise CorpusError("pbs: no monthly workbook (dos-jul-2022-...xlsx) on the date-of-supply page")
    ctx.table(monthly(book), "monthly", describe=MONTHLY_DESCRIBE)


def reprocess(ctx: Ctx, tables: list[str] | None = None) -> None:
    """`monthly` from the stored workbook (R2); the other tables are left as they are."""
    if tables not in (None, ["monthly"]):
        raise CorpusError("pbs: only `monthly` can be reprocessed; use corpus run for the rest")
    files = [k for k in read_manifest()["sources"]["pbs"]["files"] if re.match(r"raw/dos-jul-2022-.*\.xlsx$", k)]
    if not files:
        raise CorpusError("pbs: the manifest records no monthly workbook")
    ctx.table(monthly(raw_path("pbs", files[0][4:])), "monthly", describe=MONTHLY_DESCRIBE)
