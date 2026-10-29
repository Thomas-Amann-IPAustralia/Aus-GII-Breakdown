"""National Survey of Research Commercialisation (NSRC), unit records, 2000 to 2015 (gap B9).

For Q2 and Q4: how much universities and research institutes commercialised their research (invention disclosures,
licences, options and assignments (LOAs) and their income, start-ups, consultancies and contracts), beside the patents
the `institutions` lens counts for them. The Department of Industry, Science and Resources ran the survey of
Australian universities, medical research institutes and publicly funded research agencies; the unit record file on
data.gov.au holds every participant's answers for each year, 2000 to 2015 (CC BY 2.5 AU). Raw: the CSV as published
(repo). Processed: `responses`, one row per year and institution as named in the survey, with the survey's questions
as columns (`q1_research_expenditure` ... `q18b_research_students`; money in Australian dollars). Questions first
asked in 2014 (skills training) are empty before then, and a participant that left a question unanswered has an
empty value.
"""

from __future__ import annotations

import io
import re

import pandas as pd

from ..core import CorpusError, Ctx, http_get

PACKAGE = (
    "https://data.gov.au/data/api/3/action/package_show"
    "?id=national-survey-of-research-commercialisation-nsrc-2000-2015-unit-record-data"
)
NAME = "NSRC 2000-2015 unit record data"


def snake(header: str) -> str:
    """'Q13a No start-ups dependent upon licensing/ assigment for initiation' -> 'q13a_no_start_ups_dependent_...'."""
    return re.sub(r"[^a-z0-9]+", "_", " ".join(header.split()).lower()).strip("_")


def responses(text: str) -> pd.DataFrame:
    """The CSV after its title rows: the header row starts with 'Year'."""
    lines = text.splitlines()
    head = next((i for i, line in enumerate(lines) if line.startswith("Year,")), None)
    if head is None:
        raise CorpusError("nsrc: no header row starting with 'Year'")
    df = pd.read_csv(io.StringIO("\n".join(lines[head:])), dtype=str).dropna(how="all")
    df.columns = [snake(c) for c in df.columns]
    df = df[df["year"].astype(str).str.fullmatch(r"\d{4}")].copy()
    df["institution_name"] = df["institution_name"].str.strip()
    for c in df.columns[2:]:
        df[c] = pd.to_numeric(df[c].str.replace(r"[,$\s]", "", regex=True), errors="coerce")
    return df.assign(year=df["year"].astype(int)).reset_index(drop=True)


def run(ctx: Ctx) -> None:
    res = http_get(PACKAGE).json()["result"]["resources"]
    r = next((r for r in res if r["name"].strip() == NAME), None)
    if r is None:
        raise CorpusError(f"nsrc: no resource named '{NAME}' on data.gov.au")
    p = ctx.fetch(r["url"], "2000-2015-nsrc-unit-record-data.csv", keep="repo")
    df = responses(p.read_bytes().decode("cp1252"))
    ctx.log(f"{df.year.min()} to {df.year.max()}: {len(df):,} responses, {df.institution_name.nunique()} institutions")
    ctx.table(df, "responses", describe="NSRC unit records: one row per year and institution, 2000 to 2015")
