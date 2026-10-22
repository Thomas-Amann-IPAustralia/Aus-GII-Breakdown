"""NHMRC grant outcomes: every grant in the NHMRC's summary of results workbooks, application rounds 2013 to 2026.

Health and medical research funding by institution, scheme, sector and field (Q2 research institutions; Q3 public
funding). The NHMRC site refuses this environment, so the workbooks were downloaded by hand from
https://www.nhmrc.gov.au/funding/data-research/outcomes into data/raw/nhmrc_grants/ (repo); to add a round, put its
workbook there and run `corpus run nhmrc_grants`.

Processed: `grants`, one row per grant from each workbook's grants sheet, with the columns harmonised across the
rounds' layouts (amounts in dollars; keywords '; '-joined). Chief investigators' names and ORCIDs are left out.
"""

from __future__ import annotations

import re

import pandas as pd

from ..core import CorpusError, Ctx
from ._manual import _framed

# each round's column names, mapped to one set
COLUMNS = {
    "application_id": ["app_id", "application_id"],
    "date_announced": ["date_announced"],
    "scheme": ["grant_type", "funding_type", "funding_scheme"],
    "sub_type": ["sub_type", "funding_sub_type", "level_stream_or_sub_type"],
    "grant_opportunity": ["grant_opportunity"],
    "title": ["grant_title", "simplified_title", "scientific_title"],
    "admin_institution": ["admin_institution", "app_admin_institution", "administering_institution"],
    "admin_institution_ror": ["administering_institution_ror_id"],
    "state": ["state", "state_or_territory"],
    "sector": ["sector", "organisation_type"],
    "participating_institutions": ["participating_institutions"],
    "international_collaboration": ["involve_international_collaboration_y_n"],
    "collaborating_countries": ["collaborating_countries"],
    "start": ["start_yr", "start_year", "grant_start_date"],
    "end": ["end_yr", "grant_end_date"],
    "amount": ["total", "final_budget_rounded", "total_amount_awarded"],
    "broad_research_area": ["broad_research_area"],
    "for_category": ["for_category"],
    "fields_of_research": ["field_of_research", "fields_of_research", "field_s_of_research"],
    "plain_description": ["plain_description", "media_summary"],
}
KEYWORDS = re.compile(r"^(res_kw\d|research_kw_\d|research_keywords)$")


def _round(name: str) -> int:
    m = re.search(r"(20\d\d)[-_ ]?app", name) or re.search(r"^(20\d\d)", name)
    if not m:
        raise CorpusError(f"nhmrc_grants: no application round year in {name}")
    return int(m.group(1))


def _grants(path) -> pd.DataFrame:
    sheets = pd.read_excel(path, sheet_name=None, header=None, dtype=str, engine="calamine")
    sheet = next((s for s in sheets if s.strip().upper() == "GRANTS DATA" or s.endswith("App Data")), None)
    if sheet is None:
        raise CorpusError(f"nhmrc_grants: no grants sheet in {path.name}")
    t = _framed(sheets[sheet])
    out = pd.DataFrame(index=t.index)
    for col, names in COLUMNS.items():
        have = [n for n in names if n in t.columns]
        out[col] = t[have[0]] if have else None
    kw = [c for c in t.columns if KEYWORDS.match(c)]
    out["keywords"] = t[kw].apply(lambda r: "; ".join(v.strip() for v in r if isinstance(v, str) and v.strip()), axis=1)
    out = out[out["application_id"].notna() & out["application_id"].str.strip().str.match(r"^\d+$")]
    out.insert(1, "round", _round(path.name))
    out["source_file"] = path.name
    return out


def run(ctx: Ctx) -> None:
    files = sorted(p for p in ctx.raw.glob("*.xlsx") if "dictionary" not in p.name.lower())
    if not files:
        raise CorpusError(
            "nhmrc_grants: no workbooks in data/raw/nhmrc_grants/ yet. From "
            "https://www.nhmrc.gov.au/funding/data-research/outcomes, the summary of results workbooks (xlsx)."
        )
    for p in ctx.raw.glob("*.xlsx"):
        ctx.keep_raw(p)
    df = pd.concat([_grants(p) for p in files], ignore_index=True)
    df["application_id"] = df["application_id"].str.strip()
    df["amount"] = pd.to_numeric(df["amount"].astype("string").str.replace(r"[$,\s]", "", regex=True), errors="coerce")
    for c in ("date_announced", "start", "end"):
        v = df[c].astype("string").str.strip()
        year = v.str.fullmatch(r"\d{4}").fillna(False).astype(bool)
        dt = pd.to_datetime(v.where(~year), errors="coerce", format="mixed")
        if c == "date_announced":
            df[c] = dt.dt.date
        else:
            df[c + "_year"] = pd.to_numeric(v.where(year), errors="coerce").fillna(dt.dt.year).astype("Int64")
            df = df.drop(columns=c)
    for c in df.select_dtypes(include=["object", "string"]).columns:
        df[c] = df[c].map(lambda v: v.strip() if isinstance(v, str) else v).replace({"": None, "nan": None})
    dupes = df.duplicated(["application_id", "round"]).sum()
    if dupes:
        ctx.note(f"{dupes} grants listed twice within a round; kept as published")
    ctx.table(df, "grants", describe="NHMRC grants, application rounds 2013 to 2026, harmonised")
