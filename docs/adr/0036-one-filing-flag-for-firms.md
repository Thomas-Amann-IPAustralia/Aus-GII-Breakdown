# 0036: One filing flag for firms; "no filing linked", never "never filed"

**Date:** 2026-11-01. **Whose:** Claude's. The owner asked for the most urgent cross-cutting issue in the external
notebook audits (`analysis/GPT-audit/261030/`) to be verified and corrected in the back end; the owner can overturn any
of it. The audits' findings acted on, and the verification of each, are in
`analysis/GPT-audit/261030/AMENDMENTS.md`.

**Context.** The `firms` lens held three ways of saying a firm "has filed IP", and the lenses and notebooks used them
interchangeably:
1. `ip_filed_total > 0`: a founding applicant in IP RAPID's own applicant panel (`iprapid/applicant_year`), which
   predates the register's ABNs (ADR 0029). 265,615 ABNs.
2. A count in `n_patents_standard` to `n_designs`: credited as the filer (`filer_abn` in the `rights` lens), which
   includes the register's ABNs. 323,604 ABNs.
3. Either of the two (Stage 2's B22 and B24). 325,650 ABNs.

60,035 ABNs are filers by rule 2 and not rule 1 (60,021 of them only through the register's ABNs); 2,046 by rule 1 and
not rule 2 (co-applicants not credited as the filer). The `regions` lens built `ip_filing_firms` and
`rdti_firms_no_ip` from rule 1, the narrowest, so the register's ABNs never reached it: active IP-filing firms placed
in a postal area were 162,359, and R&D claimants that had "never filed IP" 8,939 of 17,627 (50.7%, U54). Stage 1's
§2.1 and §2.5 (U42, U47) and Stage 2's B23 also used rule 1; U112 and B50 used rule 2; B22 and B24 rule 3. The
complement of a linked filing was then called "never filed" or a "missing filer", though no record can show that a
firm never filed: a firm can file without its ABN being recorded, or hold IP it did not file. Nine findings in five
of the twelve audits raise this (S1 L2 R47, R48; S1 L3 R15; S8-S9 R17; S2 L2 R04, R08, R09, R10; S2 L3 R06), two of
the index's recurring themes; B23's IPLORD percentage also had the wrong denominator (S2 L2 R08).

**Decision.**
1. **One flag, `firms.ip_record`**, three values: `filed` (a filing linked to the ABN by either rule, rule 3);
   `other_ip_link` (no filing linked, but the ABN holds a right now, is an applicant or owner on an IP RAPID record, is
   an owner in the register, or IPLORD links it to IP to FY2020); `no_ip_link` (none of these). Built in
   `build.firms_sql`; every query in the notebooks that asks who has filed uses it.
2. **The `regions` lens counts firms by it.** `ip_filing_firms` is active firms with `ip_record` = filed (207,537
   placed in a postal area, against 162,359). `rdti_firms_no_ip` becomes `rdti_firms_no_filing` (active R&D
   claimants not `filed`: 8,521, 48.3%), and `rdti_firms_no_ip_link` is added beside it (`no_ip_link`: 7,873,
   44.7%). The screen's `missing_filer_share` becomes `no_filing_share`.
3. **The wording rule.** "No filing linked (to the ABN)" and "no link to IP", never "never filed" or "missing
   filers". Recorded counts are counts under the stated attribution rule, not proven bounds on a firm's activity.
4. **The other counts stay, labelled.** `ip_filed_total` and `ip_filed_weighted` remain (IP RAPID's panel, every
   founding applicant, for the weighting IPLORD uses); their notes say they are not the filing flag. The per-type
   `n_*` counts remain the counts of applications by the filer.
5. **B23's IPLORD figure** is replaced by the share of claimants with no filing linked who are linked to IP another
   way, numerator and denominator shown.

**Rejected.**
- **Rule 2 alone** (the per-type counts): it drops 2,046 firms that co-filed as founding applicants.
- **Rule 1 alone:** it drops the 60,021 firms only the register's ABNs link to their filings, which ADR 0029 added to
  the lens precisely so that recent filing could be followed.
- **Counting `other_ip_link` firms as filers:** holding a right, or an IPLORD link without an attributable application,
  is not a filing by the firm; it is shown beside, not added.
- **Bringing IPLORD's counts in:** they are built differently (ADR 0016).
- **Renaming `ip_filing_firms`:** its meaning (active firms that have filed) is unchanged; only its attribution is
  completed.

**Checked.**
- `tests/test_eda.py::test_firms_have_one_filing_flag_and_regions_count_by_it`: `ip_record` is `filed` exactly where
  either rule links a filing, never `no_ip_link` where any link to IP exists, never empty; the regions lens's
  `ip_filing_firms` and `rdti_firms_no_filing` sum to the firms lens's counts for the places; no area has more
  claimants with no link than with no filing, or more with no filing than claimants.
- The lenses as built: `firms` 463,279 rows and 51 columns (one added), `regions` 2,641 rows and 43 columns (one
  added). No other lens changes.
- The notebooks were re-executed whole; the observations quoting the changed counts were restated (U41, U42, U44,
  U47, U54, U112, B23, B27, B28, B50, the lens and stage summaries, and `docs/stage-1-summary.md` and
  `docs/stage-2-summary.md`); `AMENDMENTS.md` lists each. Two conclusions changed, not only numbers: IP filers are no
  more advantaged than firms in general (U47: 33.3% in the top IRSAD decile against 33.4%; 34.1% before), and
  another link to IP explains little of B23's group (10.9% of the oldest claimants with no filing linked, not the
  54.3% of all the oldest claimants first given). B22 and B24 already used rule 3, so their outputs are unchanged.
- Not changed here: the evidence atlas (`evidence/`, `analysis/atlas/`), which is updated in its own pass; until then
  the five tests in `tests/test_atlas.py` stop at its numbers rule, as they should (its pages for U47, U54, B23, B27
  and B50 quote figures no longer on the notebook's page), and `analysis/atlas/charts.py` still selects "IP filers"
  by `ip_filed_total > 0`. Every other test passes (119).
