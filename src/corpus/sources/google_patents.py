"""Google Patents Public Data (BigQuery): the worldwide patent families that touch Australia.

Q1 and Q3: patent families as value measures (how many offices an invention is filed in, forward citations), where
Australian applicants and inventors file abroad, and which foreign families come to Australia. The families are those
with a publication in Australia or an Australian applicant or inventor (by Google's harmonised country codes, which
some offices leave blank, so foreign filings by Australians are undercounted), 1.75 million families and 17 million
publications in the October 2026 release. Queried in BigQuery (`patents-public-data.patents.publications`, CC BY 4.0;
about 60 GB of query per run, billed to `GCP_PROJECT_ID`); no raw files.

Processed (R2 unless small):
- `members`: one row per publication in those families: numbers, office, kind, dates, applicant and inventor
  countries and counts, first IPC and CPC codes and IPC subclasses, patent and non-patent citations made, the names
  of Australian applicants (organisations and individuals, as published), and `au_application` (the 10-digit
  Australian application number, to join to `iprapid`).
- `families`: one row per family: first priority and filing dates, offices filed in (`offices`, `n_offices`), whether
  granted in Australia and the United States, Australian applicant or inventor, the first IPC code, English title,
  and forward citations (distinct citing families, in all and within five years of the family's first priority).
- `citations`: family-level citation pairs (citing family, cited family, citing family's first priority date) where
  the cited family is in the set.
"""

from __future__ import annotations

import duckdb
import pyarrow as pa

from ..core import Ctx, bigquery

P = "`patents-public-data.patents.publications`"
FAMILIES = f"""
fam as (
  select distinct family_id from {P}
  where family_id != '-1' and (country_code = 'AU'
     or exists(select 1 from unnest(assignee_harmonized) a where a.country_code = 'AU')
     or exists(select 1 from unnest(inventor_harmonized) a where a.country_code = 'AU')))"""


def _date(col: str) -> str:
    return f"safe.parse_date('%Y%m%d', cast(nullif({col}, 0) as string)) as {col}"


MEMBERS = f"""
with {FAMILIES}
select publication_number, application_number, pct_number, country_code, kind_code, application_kind, family_id,
  {_date("publication_date")}, {_date("filing_date")}, {_date("grant_date")}, {_date("priority_date")},
  entity_status,
  array_to_string(array(select distinct a.country_code from unnest(assignee_harmonized) a
                        where a.country_code != '' order by 1), ' ') as assignee_countries,
  array_to_string(array(select distinct a.country_code from unnest(inventor_harmonized) a
                        where a.country_code != '' order by 1), ' ') as inventor_countries,
  array_length(assignee_harmonized) as assignees,
  array_length(inventor_harmonized) as inventors,
  array_to_string(array(select distinct a.name from unnest(assignee_harmonized) a
                        where a.country_code = 'AU' order by 1), '; ') as au_assignee_names,
  (select x.code from unnest(ipc) x where x.first limit 1) as ipc_first,
  array_to_string(array(select distinct substr(x.code, 1, 4) from unnest(ipc) x order by 1), ' ') as ipc_subclasses,
  (select x.code from unnest(cpc) x where x.first limit 1) as cpc_first,
  (select count(*) from unnest(citation) c where c.publication_number != '') as patent_citations,
  (select count(*) from unnest(citation) c where c.npl_text != '') as npl_citations
from {P} where family_id in (select family_id from fam)
"""

CITATIONS = f"""
with {FAMILIES},
pubs as (select publication_number, family_id from {P} where family_id in (select family_id from fam))
select p.family_id as citing_family, pf.family_id as cited_family,
  min(safe.parse_date('%Y%m%d', cast(nullif(p.priority_date, 0) as string))) as citing_priority_date
from {P} p, unnest(p.citation) c join pubs pf on pf.publication_number = c.publication_number
where p.family_id != pf.family_id and p.family_id != '-1'
group by 1, 2
"""

TITLES = f"""
with {FAMILIES}
select family_id, array_agg(t.text order by p.publication_date limit 1)[offset(0)] as title
from {P} p, unnest(title_localized) t
where t.language = 'en' and family_id in (select family_id from fam)
group by 1
"""

FAMILY = """
with m as (select * from members),
  au as (select family_id, bool_or(country_code = 'AU') as filed_au,
           bool_or(country_code = 'AU' and grant_date is not null) as granted_au,
           bool_or(country_code = 'US' and grant_date is not null) as granted_us,
           bool_or(list_contains(string_split(assignee_countries, ' '), 'AU')) as au_applicant,
           bool_or(list_contains(string_split(inventor_countries, ' '), 'AU')) as au_inventor
         from m group by 1),
  f as (select family_id, min(priority_date) as first_priority_date, min(filing_date) as first_filing_date,
          min(grant_date) as first_grant_date, count(*) as publications,
          string_agg(distinct country_code, ' ' order by country_code) as offices,
          count(distinct country_code) filter (where country_code not in ('WO', 'EP')) as n_offices,
          bool_or(country_code = 'WO') as pct, bool_or(country_code = 'EP') as ep,
          arg_min(ipc_first, coalesce(priority_date, filing_date)) as ipc_first
        from m group by 1),
  c as (select c.cited_family as family_id, count(*) as citing_families,
          count(*) filter (where c.citing_priority_date <= f.first_priority_date + interval 5 year)
            as citing_families_5y
        from citations c join f on f.family_id = c.cited_family group by 1)
select f.*, au.* exclude (family_id), t.title,
  coalesce(c.citing_families, 0) as citing_families, coalesce(c.citing_families_5y, 0) as citing_families_5y
from f join au using (family_id) left join c using (family_id) left join titles t using (family_id)
order by family_id
"""


def _query(ctx: Ctx, client, sql: str, name: str) -> pa.Table:
    from google.api_core.exceptions import PermissionDenied

    job = client.query(sql)
    try:
        t = job.result().to_arrow(create_bqstorage_client=True)
    except PermissionDenied:  # without the BigQuery Read Session User role, page through the results instead
        t = job.result(page_size=50_000).to_arrow(create_bqstorage_client=False)
    ctx.log(f"{name}: {t.num_rows:,} rows, {job.total_bytes_billed / 1e9:.1f} GB billed")
    return t


def _au_application(numbers: pa.Array) -> list:
    """'AU-2017352992-A' -> '2017352992'; the old 'AU-6508386-A' (65083/86) -> '1986065083'."""
    out = []
    for n in numbers.to_pylist():
        part = n.split("-")[1] if n and n.startswith("AU-") else ""
        if len(part) == 10 and part.isdigit():
            out.append(part)
        elif 6 <= len(part) <= 8 and part.isdigit():
            yy = int(part[-2:])
            out.append(f"{1900 + yy if yy > 30 else 2000 + yy}{int(part[:-2]):06d}")
        else:
            out.append(None)
    return out


def run(ctx: Ctx) -> None:
    client = bigquery()
    members = _query(ctx, client, MEMBERS, "members")
    members = members.append_column("au_application", pa.array(_au_application(members["application_number"])))
    citations = _query(ctx, client, CITATIONS, "citations")
    titles = _query(ctx, client, TITLES, "titles")
    con = duckdb.connect()
    con.register("members", members)
    con.register("citations", citations)
    con.register("titles", titles)
    families = con.execute(FAMILY).to_arrow_table()
    ctx.table(members, "members", describe="Publications in families touching Australia")
    ctx.table(families, "families", describe="Families touching Australia: offices, grants, forward citations")
    ctx.table(citations, "citations", describe="Family-level citations to families touching Australia")
