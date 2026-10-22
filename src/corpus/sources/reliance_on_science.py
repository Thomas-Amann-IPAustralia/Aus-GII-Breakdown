"""Reliance on Science (Marx and Fuegi): US patents' citations to scientific papers, matched to OpenAlex works.

Q1 and Q2: knowledge flows from research to invention, in place of the Lens (whose API is paid). Every citation from
a USPTO patent to a scholarly work, through 2025, with whether the applicant or examiner made it, a confidence score
(1 to 10) and whether it is on the front page, in the body text or both; and the patent-paper pairs (USPTO, through
2021). From https://zenodo.org/records/22967630, CC BY-NC 4.0 (non-commercial use; cite Marx and Fuegi 2020, Strategic
Management Journal 41(9), and 2022, Journal of Economics and Management Strategy). Raw: the citations file (R2,
1.4 GB) and the pairs file (repo).

Processed:
- `citations_au`: the citations made by US publications in patent families with an Australian applicant or inventor
  (from `google_patents/members`), with the family, so the science behind Australian inventions can be traced. `oaid` is the OpenAlex work id without its 'W'.
- `ppp`: patent-paper pairs, as published.

Which citing patents rely on Australian research needs the OpenAlex works with an Australian institution (about 2.4
million cited works); the full citations file is kept in R2 for that join.
"""

from __future__ import annotations

import duckdb

from ..core import Ctx, path

RECORD = "https://zenodo.org/records/22967630/files/"


def run(ctx: Ctx) -> None:
    cites = ctx.fetch(RECORD + "pcs_oa_uspto.csv?download=1", "pcs_oa_uspto.csv", keep="r2")
    pairs = ctx.fetch(RECORD + "finalpppsadjusted.csv?download=1", "finalpppsadjusted.csv", keep="repo")
    members = path("google_patents", "members")
    con = duckdb.connect()
    au = con.sql(
        f"""
        with us as (
          select lower(publication_number) as patent, family_id, country_code
          from '{members}' where country_code = 'US')
        select c.patent, us.family_id, c.oaid, c.reftype, c.confscore, c.wherefound
        from read_csv('{cites}', header = true, all_varchar = true) c join us using (patent)
        order by us.family_id, c.patent, c.oaid
        """
    ).to_arrow_table()
    ctx.table(au, "citations_au", describe="US patents' citations to papers, families with Australian applicants or inventors")
    ppp = con.sql(f"select * from read_csv('{pairs}', header = true, all_varchar = true)").to_arrow_table()
    ctx.table(ppp, "ppp", describe="Patent-paper pairs (USPTO, through 2021), as published")
