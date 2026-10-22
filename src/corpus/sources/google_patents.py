"""Google Patents Public Data (BigQuery): the worldwide patent families that touch Australia.

Q1 and Q3: patent families as value measures (how many offices an invention is filed in, forward citations), where
Australian applicants and inventors file abroad, and which foreign families come to Australia. The families are those
with a publication in Australia or an Australian applicant or inventor (by Google's harmonised country codes, which
some offices leave blank, so foreign filings by Australians are undercounted): 1.75 million families and 17 million
publications in the October 2026 release. Queried in BigQuery (`patents-public-data.patents.publications`, CC BY 4.0;
about 140 GB of query per run, within BigQuery's free terabyte a month, billed to `GCP_PROJECT_ID`); the families are
summarised in BigQuery and only the summaries and the Australian publications are downloaded. No raw files.

Processed (R2 unless small):
- `families`: one row per family: first priority, filing and grant dates, offices filed in (`offices`; `n_offices`
  counts national and regional offices other than WO and EP), PCT and EP filings, whether filed and granted in
  Australia and granted in the United States, Australian applicant or inventor, publications, the earliest
  publication's first IPC code, an English title, and forward citations (distinct citing families, in all and within
  five years of the family's first priority).
- `members`: one row per publication that is Australian or in a family with an Australian applicant or inventor:
  numbers, office, kind, dates, applicant and inventor countries and counts, first IPC and CPC codes and IPC
  subclasses, patent and non-patent citations made, the names of Australian applicants (organisations and
  individuals, as published), and `au_application` (the 10-digit Australian application number, to join to
  `iprapid`; every standard patent and innovation patent application from the 1960s on maps, but not provisional
  applications in the letter series of the 1990s, such as PO4687/97, nor designs, which Google also holds).
- `citations`: family-level citation pairs (citing family, cited family, citing family's first priority date) where
  the cited family has an Australian applicant or inventor.
"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor

import pyarrow as pa

from ..core import Ctx, bigquery

P = "`patents-public-data.patents.publications`"
AU_APPLICANT = "exists(select 1 from unnest(assignee_harmonized) a where a.country_code = 'AU')"
AU_INVENTOR = "exists(select 1 from unnest(inventor_harmonized) a where a.country_code = 'AU')"
FAM = f"""
fam as (
  select distinct family_id from {P}
  where family_id != '-1' and (country_code = 'AU' or {AU_APPLICANT} or {AU_INVENTOR})),
au_fam as (
  select distinct family_id from {P} where family_id != '-1' and ({AU_APPLICANT} or {AU_INVENTOR}))"""


def _date(col: str) -> str:
    return f"safe.parse_date('%Y%m%d', cast(nullif({col}, 0) as string)) as {col}"


FAMILIES = f"""
with {FAM},
m as (
  select family_id, country_code, publication_date, {_date("priority_date")}, {_date("filing_date")},
    {_date("grant_date")}, (select x.code from unnest(ipc) x where x.first limit 1) as ipc_first,
    {AU_APPLICANT} as au_applicant, {AU_INVENTOR} as au_inventor
  from {P} where family_id in (select family_id from fam)),
f as (
  select family_id, min(priority_date) as first_priority_date, min(filing_date) as first_filing_date,
    min(grant_date) as first_grant_date, count(*) as publications,
    string_agg(distinct country_code, ' ' order by country_code) as offices,
    count(distinct if(country_code not in ('WO', 'EP'), country_code, null)) as n_offices,
    logical_or(country_code = 'WO') as pct, logical_or(country_code = 'EP') as ep,
    logical_or(country_code = 'AU') as filed_au,
    logical_or(country_code = 'AU' and grant_date is not null) as granted_au,
    logical_or(country_code = 'US' and grant_date is not null) as granted_us,
    logical_or(au_applicant) as au_applicant, logical_or(au_inventor) as au_inventor,
    array_agg(ipc_first ignore nulls order by publication_date limit 1)[safe_offset(0)] as ipc_first
  from m group by 1),
pubs as (select publication_number, family_id from {P} where family_id in (select family_id from fam)),
cit as (
  select pf.family_id as cited_family, p.family_id as citing_family,
    min(safe.parse_date('%Y%m%d', cast(nullif(p.priority_date, 0) as string))) as citing_priority_date
  from {P} p, unnest(p.citation) c join pubs pf on pf.publication_number = c.publication_number
  where p.family_id != pf.family_id and p.family_id != '-1'
  group by 1, 2),
c as (
  select cit.cited_family as family_id, count(*) as citing_families,
    countif(cit.citing_priority_date <= date_add(f.first_priority_date, interval 5 year)) as citing_families_5y
  from cit join f on f.family_id = cit.cited_family group by 1),
t as (
  select family_id, array_agg(tl.text order by p.publication_date limit 1)[offset(0)] as title
  from {P} p, unnest(title_localized) tl
  where tl.language = 'en' and family_id in (select family_id from fam) group by 1)
select f.*, t.title, coalesce(c.citing_families, 0) as citing_families,
  coalesce(c.citing_families_5y, 0) as citing_families_5y
from f left join c using (family_id) left join t using (family_id)
"""

MEMBERS = f"""
with {FAM}
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
from {P}
where family_id != '-1' and (country_code = 'AU' or family_id in (select family_id from au_fam))
"""

CITATIONS = f"""
with {FAM},
pubs as (select publication_number, family_id from {P} where family_id in (select family_id from au_fam))
select p.family_id as citing_family, pf.family_id as cited_family,
  min(safe.parse_date('%Y%m%d', cast(nullif(p.priority_date, 0) as string))) as citing_priority_date
from {P} p, unnest(p.citation) c join pubs pf on pf.publication_number = c.publication_number
where p.family_id != pf.family_id and p.family_id != '-1'
group by 1, 2
"""


def _query(ctx: Ctx, client, sql: str, name: str, threads: int = 16) -> pa.Table:
    """Run a query and download its result in parallel slices (the faster BigQuery Storage API needs the BigQuery
    Read Session User role, which this service account may not have)."""
    job = client.query(sql)
    rows = job.result(max_results=0).total_rows
    dest = client.get_table(job.destination)
    step = max(-(-rows // threads), 1)

    def part(start: int) -> pa.Table:
        it = client.list_rows(dest, start_index=start, max_results=step, page_size=50_000)
        return it.to_arrow(create_bqstorage_client=False)

    with ThreadPoolExecutor(threads) as pool:
        t = pa.concat_tables(pool.map(part, range(0, max(rows, 1), step)))
    ctx.log(f"{name}: {t.num_rows:,} rows, {(job.total_bytes_billed or 0) / 1e9:.1f} GB billed")
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
    families = _query(ctx, client, FAMILIES, "families")
    ctx.table(families.sort_by("family_id"), "families", describe="Families touching Australia: offices, citations")
    citations = _query(ctx, client, CITATIONS, "citations")
    ctx.table(citations, "citations", describe="Family-level citations to families with Australian applicants")
    members = _query(ctx, client, MEMBERS, "members")
    members = members.append_column("au_application", pa.array(_au_application(members["application_number"])))
    ctx.table(members, "members", describe="Australian publications and families with Australian applicants")
