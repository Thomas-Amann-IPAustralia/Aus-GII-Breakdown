"""Shared by the ATO's transparency reports (`rdti`, `ato_ctt`): every yearly xlsx on a data.gov.au dataset, stacked."""

from __future__ import annotations

import re

import pandas as pd

from ..core import CorpusError, Ctx, http_get


def snake(s: str) -> str:
    s = re.sub(r"\(.*?\)", "", str(s)).replace("$", "").replace("&", "and")
    return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")


def read_reports(ctx: Ctx, package: str, wanted: str) -> pd.DataFrame:
    """Fetch every xlsx resource of a data.gov.au package and stack every sheet with an ABN column and a column
    matching the regex `wanted`. Older files repeat earlier years' sheets; exact repeats are dropped."""
    res = http_get(f"https://data.gov.au/data/api/3/action/package_show?id={package}").json()["result"]["resources"]
    frames = []
    for r in res:
        if not r["url"].lower().endswith(".xlsx"):
            continue
        year = re.search(r"(20\d\d-\d\d)", r["name"])
        name = f"{year.group(1) if year else snake(r['name'])}.xlsx"
        f = ctx.fetch(r["url"], name, keep="repo")
        sheets = pd.read_excel(f, sheet_name=None, engine="calamine", header=None, dtype=str)
        used = 0
        for sheet, df in sheets.items():
            head = next((i for i in range(min(10, len(df))) if df.iloc[i].astype(str).str.contains("ABN").any()), None)
            if head is None:
                continue
            cols = [snake(c) for c in df.iloc[head]]
            if not any(re.search(wanted, c) for c in cols):
                continue
            df = df.iloc[head + 1 :].dropna(how="all").copy()
            df.columns = cols
            df["report"] = name.removesuffix(".xlsx")
            df["sheet"] = sheet
            frames.append(df)
            used += 1
        if not used:
            raise CorpusError(f"{ctx.source}: {name} has no sheet with an ABN column and a column matching {wanted}")
    if not frames:
        raise CorpusError(f"{ctx.source}: no xlsx resources on {package}")
    out = pd.concat(frames, ignore_index=True)
    out = out.loc[:, [c for c in out.columns if c and c != "nan"]]
    sheet_year = out["sheet"].where(out["sheet"].str.fullmatch(r"\d{4}-\d{2}"))
    report_year = out["report"].where(out["report"].str.fullmatch(r"\d{4}-\d{2}"))
    year = out["income_year"].fillna(sheet_year) if "income_year" in out else sheet_year
    out["income_year"] = year.fillna(report_year)
    if "company_name" in out:  # some years call it "Name"
        out["name"] = out["company_name"].fillna(out["name"]) if "name" in out else out["company_name"]
        out = out.drop(columns=["company_name"])
    out = out.drop_duplicates(subset=[c for c in out.columns if c not in ("report", "sheet")], keep="first")
    idcol = next(c for c in out.columns if c.startswith("abn"))
    digits = out[idcol].astype(str).str.replace(r"\D", "", regex=True)
    out["abn"] = digits.where(digits.str.len() == 11)
    out["acn"] = digits.where(digits.str.len() == 9)
    if idcol != "abn":
        out = out.drop(columns=[idcol])
    for c in out.columns:
        if c.endswith(("expenditure", "income", "payable")):
            out[c] = pd.to_numeric(out[c].str.replace(",", ""), errors="coerce")
    return out
