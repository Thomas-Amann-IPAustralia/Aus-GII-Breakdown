"""Workplace Gender Equality Agency (WGEA) public data: every private-sector employer with 100 or more employees, by
ABN, with its industry (ANZSIC class) and its size, as reported each year (gap A3: firms' size and industry, free).

Q2, Q3 (who files IP, by size and industry): WGEA is the only free source found that gives firm-level industry and
size by ABN (ADR 0032). It covers employers of 100 or more, so it says nothing of small firms. Raw: the public data
files for 2022-23, 2023-24 and 2024-25 (zips, R2), as published on data.gov.au (CC BY 3.0 AU). Processed:

- `employers`: one row per reporting year and ABN: the employer's and its corporate group's names, the size band as
  WGEA publishes it (for 2022-23, the submission group's; from 2023-24, the employer's), its ANZSIC class (code and
  the names of its division, subdivision, group and class), and its workforce: employees (the sum of the workforce
  composition's headcounts), women and managers. In 2022-23 a submission group reports under its primary ABN only.
"""

from __future__ import annotations

import io
import zipfile

import pandas as pd

from ..core import CorpusError, Ctx, http_get

DATASET = "https://data.gov.au/data/api/3/action/package_show?id=wgea-dataset"
YEARS = {"2025": "2024-25", "2024": "2023-24", "2023": "2022-23"}  # file label: reporting year

# 2022-23's columns, named as from 2023-24
OLD = {
    "primary_abn": "employer_abn",
    "primary_employer_name": "employer_name",
    "submission_group_size": "employer_size",
    "primary_anzsic": "anzsic_code",
    "primary_division_name": "anzsic_division",
    "primary_subdivision_name": "anzsic_subdivision",
    "primary_group_name": "anzsic_group",
    "primary_class_name": "anzsic_class",
}
KEYS = [
    "employer_abn",
    "employer_name",
    "corporate_group_name",
    "employer_size",
    "anzsic_code",
    "anzsic_division",
    "anzsic_subdivision",
    "anzsic_group",
    "anzsic_class",
]


def employers(df: pd.DataFrame, year: str) -> pd.DataFrame:
    """One row per ABN from a workforce composition file (one row per ABN, occupation, status, type and gender)."""
    df = df.rename(columns=OLD)
    if "corporate_group_name" not in df:
        df["corporate_group_name"] = None
    df["employer_size"] = df["employer_size"].str.replace(" employees", "", regex=False).str.replace(" ", "")
    df["n_employees"] = pd.to_numeric(df["n_employees"], errors="coerce").fillna(0)
    df["employer_abn"] = df["employer_abn"].astype(str).str.replace(r"\D", "", regex=True).str.zfill(11)
    df["women"] = df["n_employees"].where(df["gender"] == "Women", 0)
    df["managers"] = df["n_employees"].where(df["manager_category"] == "Manager", 0)
    out = (
        df.groupby(KEYS, dropna=False)[["n_employees", "women", "managers"]]
        .sum()
        .reset_index()
        .rename(columns={"n_employees": "employees"})
    )
    if out["employer_abn"].duplicated().any():  # an ABN under two names or classes: keep its largest record
        out = out.sort_values(["employer_abn", "employees"], ascending=[True, False]).drop_duplicates("employer_abn")
    out.insert(0, "reporting_year", year)
    return out.rename(columns={"employer_abn": "abn"})


def run(ctx: Ctx) -> None:
    res = http_get(DATASET).json()["result"]["resources"]
    frames = []
    for label, year in YEARS.items():
        r = next((r for r in res if r["name"].startswith(f"{label} WGEA Data - Public Data File")), None)
        if r is None:
            raise CorpusError(f"wgea: no public data file for {label} on data.gov.au")
        p = ctx.fetch(r["url"], f"wgea_public_dataset_{label}.zip", keep="r2")
        z = zipfile.ZipFile(p)
        member = next((n for n in z.namelist() if n.endswith(f"workforce_composition_{label}.csv")), None)
        if member is None:
            raise CorpusError(f"wgea: the {label} file no longer holds its workforce composition")
        df = pd.read_csv(io.BytesIO(z.read(member)), dtype=str, keep_default_na=False, na_values=[""])
        frames.append(employers(df, year))
    out = pd.concat(frames, ignore_index=True)
    for c in ("employees", "women", "managers"):
        out[c] = out[c].astype("int64")
    ctx.table(out, "employers", describe="WGEA employers (100+ staff): ABN, ANZSIC class, size band, headcounts")
