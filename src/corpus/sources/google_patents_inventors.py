"""Inventors of the patent families that touch Australia (Google Patents Public Data, BigQuery): who invents, from which
country, and (estimated) of which gender.

For Q1 and Q2: where the inventions filed in Australia are made, against who owns them; Australians' inventions owned
abroad; and the gender of inventors. IP RAPID records no inventors, and its names for individual applicants are
pseudonymised codes, so this is the corpus's only source of inventors and of names to estimate gender from. The families
are those of `google_patents` (a publication in Australia, or an Australian applicant or inventor). Queried in BigQuery
(CC BY 4.0), billed to `GCP_PROJECT_ID` as `google_patents` is: a dry run measures the query first, and the run stops if
it would scan more than `MAX_GB`. The downloaded result is cached outside the repo, so the gender step can be re-run
without querying again.

Gender is an estimate from first names, the method WIPO and IP Australia use. The World Gender-Name Dictionary (`wgnd`)
gives, for a first name in a country, the share of its bearers who are women; that share is the inventor's `p_female`.
It falls back to the name without a country (0 or 1), and is empty for initials and for names the dictionary lacks. It
is not anyone's stated gender, and family totals are expected counts. The dictionary's quality varies by country (it
gives "hiroshi" in Japan a 17% chance of being a woman), so Stage 1 checks the estimates country by country. The given
name is the word after a comma ("SMITH, JOHN"), else the first or second word, whichever matches the dictionary more
often (logged at each run).

Harmonised names differ across a family's publications (a middle initial, a transliteration), so counting the distinct
names in a family roughly doubles its inventors (ADR 0008). Each family's inventors are therefore those of one
publication: the one naming the most inventors (then the most with a country). An inventor that publication gives no
country takes the most common one given to the same name elsewhere in the family, else to the same first two words. A
family member that adds an inventor (a divisional, say) is missed, so the counts per family are lower bounds.

Processed:
- `inventors` (R2, because it holds names as published): one row per family and inventor (Google's harmonised name,
  as the representative publication gives it), with the inventor's country and where it came from (`country_basis`:
  `publication`, `name` or `name_key`; empty if none is given), the family's publications naming them, the given name
  used, `p_female`, and its basis (`country` or `name`).
- `family_inventors` (repo if it fits): one row per family: inventors; inventors in Australia, abroad and of unknown
  country; their countries; the expected numbers of women and men among the inventors with an estimate; and how many
  have none. No names.
"""

from __future__ import annotations

import hashlib

import duckdb

from ..core import CorpusError, Ctx, bigquery, path
from .google_patents import FAM, P, _query

MAX_GB = 250


def name_key(col: str) -> str:
    """BigQuery SQL for the first two words of a harmonised name ('SMITH JOHN A' -> 'SMITH JOHN')."""
    return f"regexp_extract({col}, r'^\\S+(?:\\s+\\S+)?')"


INVENTORS = f"""
with {FAM},
inv as (
  select p.family_id, p.publication_number, upper(trim(i.name)) as name, nullif(i.country_code, '') as country_code
  from {P} p, unnest(p.inventor_harmonized) i
  where p.family_id in (select family_id from fam) and trim(i.name) != ''),
pub as (
  select family_id, publication_number, count(distinct name) as n,
    count(distinct if(country_code is not null, name, null)) as n_country
  from inv group by 1, 2),
rep as (
  select family_id,
    array_agg(publication_number order by n desc, n_country desc, publication_number limit 1)[offset(0)]
      as publication_number
  from pub group by 1),
r as (
  select family_id, name, max(country_code) as country_code
  from inv join rep using (family_id, publication_number) group by 1, 2),
g as (select family_id, name, country_code, count(*) as n from inv group by 1, 2, 3),
by_name as (
  select family_id, name, sum(n) as publications,
    array_agg(country_code ignore nulls order by n desc, country_code limit 1)[safe_offset(0)] as country_code
  from g group by 1, 2),
k as (
  select family_id, {name_key("name")} as name_key, country_code, sum(n) as n
  from g where country_code is not null group by 1, 2, 3),
by_key as (
  select family_id, name_key, array_agg(country_code order by n desc, country_code limit 1)[offset(0)] as country_code
  from k group by 1, 2)
select r.family_id, r.name, coalesce(r.country_code, b.country_code, k.country_code) as country_code,
  case when r.country_code is not null then 'publication' when b.country_code is not null then 'name'
       when k.country_code is not null then 'name_key' end as country_basis,
  b.publications
from r
join by_name b using (family_id, name)
left join by_key k on k.family_id = r.family_id and k.name_key = {name_key("r.name")}
"""


def given_sql(col: str, position: int) -> str:
    """SQL for the given name in a harmonised name, in lower case: the word after a comma ('SMITH, JOHN A' -> 'john'),
    else the word at `position` (1 for 'JOHN A SMITH', 2 for 'SMITH JOHN A'). Initials give NULL."""

    def words(x: str) -> str:
        cleaned = "replace(regexp_replace(lower(" + x + "), '[^\\pL''\\- ]+', ' ', 'g'), '''', '')"
        return "string_split(trim(regexp_replace(" + cleaned + ", ' +', ' ', 'g')), ' ')"

    after_comma = words("split_part(" + col + ", ',', 2)")
    w = f"CASE WHEN strpos({col}, ',') > 0 THEN {after_comma}[1] ELSE {words(col)}[{position}] END"
    return f"CASE WHEN length({w}) >= 2 THEN {w} END"


def estimate_sql(inventors: str, wgnd_code: str, wgnd_name: str, position: int) -> str:
    """SQL adding `given_name`, `p_female` and `p_female_basis` to a relation with `name` and `country_code`."""
    return f"""
    WITH i AS (SELECT *, {given_sql("name", position)} AS given_name FROM {inventors}),
    wc AS (SELECT name, code, coalesce(sum(wgt) FILTER (gender = 'F'), 0) AS f,
                  coalesce(sum(wgt) FILTER (gender = 'M'), 0) AS m
           FROM {wgnd_code} GROUP BY 1, 2),
    wn AS (SELECT name, any_value(gender) AS gender FROM {wgnd_name} WHERE gender IN ('F', 'M') GROUP BY 1)
    SELECT i.*,
        CASE WHEN wc.f + wc.m > 0 THEN wc.f / (wc.f + wc.m)
             WHEN wn.gender = 'F' THEN 1.0 WHEN wn.gender = 'M' THEN 0.0 END AS p_female,
        CASE WHEN wc.f + wc.m > 0 THEN 'country' WHEN wn.gender IS NOT NULL THEN 'name' END AS p_female_basis
    FROM i
    LEFT JOIN wc ON wc.name = i.given_name AND wc.code = i.country_code
    LEFT JOIN wn ON wn.name = i.given_name
    """


def _dry_run_gb(client, sql: str) -> float:
    from google.cloud import bigquery as bq

    job = client.query(sql, job_config=bq.QueryJobConfig(dry_run=True, use_query_cache=False))
    return job.total_bytes_processed / 1e9


def run(ctx: Ctx) -> None:
    # named after the query, so a changed query is run again rather than read from an old cache
    raw = ctx.cache / f"inventors_raw_{hashlib.sha256(INVENTORS.encode()).hexdigest()[:8]}.parquet"
    if not raw.exists():
        client = bigquery()
        gb = _dry_run_gb(client, INVENTORS)
        ctx.log(f"dry run: the inventor query scans {gb:.1f} GB")
        if gb > MAX_GB:
            raise CorpusError(f"google_patents_inventors: the query would scan {gb:.0f} GB, over the {MAX_GB} GB limit")
        t = _query(ctx, client, INVENTORS, "inventors")
        raw.parent.mkdir(parents=True, exist_ok=True)
        tmp = duckdb.connect()
        tmp.register("t", t)
        tmp.execute(f"COPY t TO '{raw}' (FORMAT parquet, COMPRESSION zstd)")
    con = duckdb.connect()
    con.execute("SET memory_limit='8GB'; SET preserve_insertion_order=false")
    code, name = path("wgnd", "name_gender_code"), path("wgnd", "name_gender")
    hits = {}
    for pos in (1, 2):
        hits[pos] = con.execute(f"""
            SELECT avg((g IN (SELECT name FROM '{name}'))::int)
            FROM (SELECT DISTINCT {given_sql("name", pos)} AS g FROM '{raw}') WHERE g IS NOT NULL""").fetchone()[0]
    pos = max(hits, key=hits.get)
    ctx.log(f"given name: word {pos} (dictionary match {hits[1]:.1%} for the first word, {hits[2]:.1%} for the second)")
    ctx.note(f"google_patents_inventors: given name taken as word {pos} of Google's harmonised names")
    out = ctx.cache / "processed/inventors.parquet"
    out.parent.mkdir(parents=True, exist_ok=True)
    con.execute(f"""COPY ({estimate_sql(f"'{raw}'", f"'{code}'", f"'{name}'", pos)} ORDER BY family_id, name)
        TO '{out}' (FORMAT parquet, COMPRESSION zstd)""")
    rows, cols = _shape(con, out)
    ctx.keep_table(out, "inventors", rows, cols, keep="r2", describe="Inventors per family, with estimated gender")
    fam = ctx.cache / "processed/family_inventors.parquet"
    con.execute(f"""COPY (
        SELECT family_id, count(*) AS inventors,
               count(*) FILTER (country_code = 'AU') AS inventors_au,
               count(*) FILTER (country_code <> 'AU') AS inventors_abroad,
               count(*) FILTER (country_code IS NULL) AS inventors_country_unknown,
               string_agg(DISTINCT country_code, ' ' ORDER BY country_code) AS countries,
               sum(p_female) AS women_expected, sum(1 - p_female) AS men_expected,
               count(*) FILTER (p_female IS NULL) AS gender_unknown
        FROM '{out}' GROUP BY 1 ORDER BY 1) TO '{fam}' (FORMAT parquet, COMPRESSION zstd)""")
    rows, cols = _shape(con, fam)
    ctx.keep_table(fam, "family_inventors", rows, cols, describe="Per family: inventors by country, expected gender")


def _shape(con, f) -> tuple[int, list[str]]:
    rows = con.execute(f"SELECT count(*) FROM '{f}'").fetchone()[0]
    return rows, [r[0] for r in con.execute(f"DESCRIBE SELECT * FROM '{f}'").fetchall()]
