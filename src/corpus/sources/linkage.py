"""The ABN spine: one row per ABN that appears anywhere in the corpus, with what the business registers say about it.

Built from the other sources (run it after them). Processed: `abn_spine` (repo), one row per ABN seen in IP RAPID's
parties (an applicant or owner of any right, founding or current), IPLORD, the R&D Tax Incentive reports, AusTender
suppliers or the corporate tax transparency reports, with:

- from the ABR: entity type, ABN status and the date it took effect, GST status and date, state, postcode, ACN, and
  whether the business is a deductible gift recipient;
- from ASIC (through the ACN): company registration and deregistration dates, type, class and status;
- `first_seen`, the earliest of the ABN status date (for an active ABN), GST registration and ASIC registration: a
  lower bound on the business's start, since the public ABR gives only the date of the current status;
- flags for each source it appears in (`in_iprapid_patent` and so on: an applicant or owner of that right, founding or
  current; `in_rdti`, `in_austender`, `in_ato_ctt`), and its first and last filing financial years by right type, as a
  founding applicant, from `iprapid/applicant_year`;
- `austender_contracts` and `austender_value`: the contracts it supplies, each counted once at its latest notice (the
  highest amendment, whose value is the contract's total), and credited to that notice's supplier. Summing every
  notice would count a contract once per amendment (ADR 0011).

`abn_spine` is how the analysis joins IP use to R&D, procurement, size and survival. ABNs in IP RAPID cover Australian
applicants that IP Australia matched to the ABR; foreign applicants and many individuals have none.
"""

from __future__ import annotations

import duckdb

from ..core import Ctx, path


def run(ctx: Ctx) -> None:
    con = duckdb.connect()
    con.execute("SET memory_limit='8GB'; SET preserve_insertion_order=false")
    p = {
        k: path(*k.split("/"))
        for k in [
            "abr/abns",
            "asic/companies",
            "iprapid/applicant_year",
            "iprapid/party",
            "iplord/iplord_abn",
            "rdti/entities",
            "austender/contracts",
            "ato_ctt/entities",
        ]
    }
    out = ctx.cache / "processed/abn_spine.parquet"
    out.parent.mkdir(parents=True, exist_ok=True)
    con.execute(f"""
    COPY (
      WITH party AS (  -- every ABN on an applicant or owner of a right, founding or current
        SELECT abn,
               bool_or(ip_right_type = 'patent') AS in_iprapid_patent,
               bool_or(ip_right_type = 'trade_mark') AS in_iprapid_trade_mark,
               bool_or(ip_right_type = 'design') AS in_iprapid_design,
               bool_or(ip_right_type = 'pbr') AS in_iprapid_pbr
        FROM '{p["iprapid/party"]}' WHERE abn IS NOT NULL AND party_role_category IN ('applicant', 'owner') GROUP BY 1),
      ip AS (
        SELECT applicant_id AS abn,
               min(financial_year) FILTER (WHERE ip_right_type = 'patent' AND filed > 0) AS patent_first_fy,
               max(financial_year) FILTER (WHERE ip_right_type = 'patent' AND filed > 0) AS patent_last_fy,
               min(financial_year) FILTER (WHERE ip_right_type = 'trade_mark' AND filed > 0) AS trade_mark_first_fy,
               max(financial_year) FILTER (WHERE ip_right_type = 'trade_mark' AND filed > 0) AS trade_mark_last_fy,
               min(financial_year) FILTER (WHERE ip_right_type = 'design' AND filed > 0) AS design_first_fy,
               max(financial_year) FILTER (WHERE ip_right_type = 'design' AND filed > 0) AS design_last_fy,
               sum(filed) AS ip_filed_total
        FROM '{p["iprapid/applicant_year"]}' WHERE applicant_id_type = 'abn' GROUP BY 1),
      lord AS (SELECT DISTINCT lord_party_id AS abn FROM '{p["iplord/iplord_abn"]}'),
      rd AS (SELECT DISTINCT abn FROM '{p["rdti/entities"]}' WHERE abn IS NOT NULL),
      latest AS (  -- each contract once, at its latest notice: an amendment's value is the new total, not the change
        SELECT parent_cn_id,
               arg_max(supplier_abn, (amendment IS NOT NULL, amendment, published)) FILTER (supplier_abn IS NOT NULL)
                 AS supplier_abn,
               arg_max(value, (amendment IS NOT NULL, amendment, published)) FILTER (value IS NOT NULL) AS value
        FROM '{p["austender/contracts"]}' GROUP BY 1),
      tender AS (SELECT supplier_abn AS abn, count(*) AS austender_contracts, sum(value) AS austender_value
                 FROM latest WHERE supplier_abn IS NOT NULL GROUP BY 1),
      ctt AS (SELECT DISTINCT abn FROM '{p["ato_ctt/entities"]}' WHERE abn IS NOT NULL),
      ids AS (SELECT abn FROM party UNION SELECT abn FROM ip UNION SELECT abn FROM lord UNION SELECT abn FROM rd
              UNION SELECT abn FROM tender UNION SELECT abn FROM ctt),
      abr AS (SELECT * FROM '{p["abr/abns"]}' WHERE abn IN (SELECT abn FROM ids)),
      co AS (SELECT * FROM '{p["asic/companies"]}')
      SELECT ids.abn,
             abr.entity_type, abr.entity_type_text, abr.abn_status, abr.abn_status_from, abr.gst_status,
             abr.gst_status_from, abr.state, abr.postcode, abr.acn, abr.dgr, abr.name,
             co.registered AS asic_registered, co.deregistered AS asic_deregistered, co.type AS asic_type,
             co.class AS asic_class, co.status AS asic_status,
             least(CASE WHEN abr.abn_status = 'ACT' THEN abr.abn_status_from END, abr.gst_status_from,
                   co.registered) AS first_seen,
             abr.abn IS NOT NULL AS in_abr,
             coalesce(party.in_iprapid_patent, false) AS in_iprapid_patent,
             coalesce(party.in_iprapid_trade_mark, false) AS in_iprapid_trade_mark,
             coalesce(party.in_iprapid_design, false) AS in_iprapid_design,
             coalesce(party.in_iprapid_pbr, false) AS in_iprapid_pbr,
             lord.abn IS NOT NULL AS in_iplord, rd.abn IS NOT NULL AS in_rdti,
             tender.abn IS NOT NULL AS in_austender, ctt.abn IS NOT NULL AS in_ato_ctt,
             ip.patent_first_fy, ip.patent_last_fy, ip.trade_mark_first_fy, ip.trade_mark_last_fy,
             ip.design_first_fy, ip.design_last_fy, coalesce(ip.ip_filed_total, 0) AS ip_filed_total,
             coalesce(tender.austender_contracts, 0) AS austender_contracts, tender.austender_value
      FROM ids
      LEFT JOIN abr USING (abn)
      LEFT JOIN co ON co.acn = abr.acn
      LEFT JOIN party USING (abn) LEFT JOIN ip USING (abn) LEFT JOIN lord USING (abn) LEFT JOIN rd USING (abn)
      LEFT JOIN tender USING (abn) LEFT JOIN ctt USING (abn)
      ORDER BY ids.abn
    ) TO '{out}' (FORMAT parquet, COMPRESSION zstd, COMPRESSION_LEVEL 9)""")
    rows = con.execute(f"SELECT count(*) FROM '{out}'").fetchone()[0]
    cols = [r[0] for r in con.execute(f"DESCRIBE SELECT * FROM '{out}'").fetchall()]
    unmatched = con.execute(f"SELECT avg((NOT in_abr)::int) FROM '{out}'").fetchone()[0]
    if unmatched > 0.02:
        ctx.note(f"linkage: {unmatched:.1%} of ABNs are not in the ABR extract (cancelled long ago, or mistyped)")
    ctx.keep_table(out, "abn_spine", rows, cols, describe="One row per ABN in the corpus, with ABR and ASIC attributes")
