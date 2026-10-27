# 0024: Stage 1 audited against IP Australia's published evidence

**Date:** 2026-10-27. **Whose:** Claude's (the owner asked for Stage 1's observations to be audited against the
observations and conclusions IP Australia has published, as the Econ repository breaks them down, to validate or
invalidate them wherever possible, with the decisions recorded here); the owner can overturn any of it. The full
account is [`docs/audit-ip-australia.md`](../audit-ip-australia.md).

**Context.** Stage 1's 99 observations rest on the lenses' own checks and on WIPO and the World Bank (U67, U89). IP
Australia's own published figures were a planned benchmark (the handover's "high value, little work" additions, and
the owner's request to IP Australia). The Econ repository holds the text of IP Australia's twelve Australian IP
Reports (2015 to 2026), nine economic research papers, two analytic notes and an Office of the Chief Economist
report, page by page (`library/elements/`), with six WIPO documents beside them.

**Decision.**

1. **A benchmark, kept and tested.** `analysis/audit/published.csv` holds 195 figures IP Australia published, each
   with its document and page; `analysis/audit/benchmark.py` (`python -m audit.benchmark`) recomputes each from the
   lenses and writes `analysis/audit/output/` (the comparison, a summary by measure, the states' shares and the
   lens-only figures the audit quotes). `tests/test_audit.py` checks the table and, where the lenses are built, that
   the committed output is in step. It is rerun whenever the lenses are rebuilt, and Stage 2 adds a row for any IP
   Australia figure it leans on.
2. **IP Australia's definitions, for any comparison with IP Australia:** calendar years; a resident application has
   a founding applicant in Australia (`founding_australian`), which reproduces IP Australia's 2022 and 2025 resident
   standard patents exactly; a PCT application counted at national phase entry. The notebook keeps its financial
   years, and `australian_applicant` keeps describing who holds a right.
3. **Tolerance and verdicts.** A count agrees within 2%, a share within 1 percentage point (5 where IP Australia gives
   it in words). Each observation gets one verdict: corroborated, consistent, qualified, disputed, contradicted or
   not testable (the audit, section 2). The result: 155 of the 195 figures agree; of the 99 observations, 23 are
   corroborated, 9 consistent, 1 disputed in part and 66 not testable; none is contradicted.
4. **Design shares are lower bounds** (U7, U13). The lens finds 10% to 14% fewer resident designs than IP Australia
   counts, with totals agreeing: about three in four of the designs IP RAPID leaves "origin unknown" are Australian on IP
   Australia's count. A design share among known origin is labelled a lower bound (about 2 to 3 points low in recent
   years), beside the unknown share U7 already requires.
5. **Trade marks filed in 2018 are flagged** (U5, U25, U90). IP RAPID holds 1,994 fewer than IP Australia reported
   (0.9749), all in Madrid applications; every other year from 2015 to 2025 agrees within 0.05%. Stage 2 marks 2018 in
   any trade mark series and does not read a Madrid change across it without that caveat.
6. **Second-tier counts include conversions.** IP RAPID's innovation patents are 6% to 7% above IP Australia's counts
   for 2015 to 2017 and agree for 2020 and 2021, when IP Australia included standard patents converted to innovation
   patents. U67's 2016 lead is closed as an IP RAPID artefact: IP Australia reported the 2016 rise itself (2,322, from
   non-residents), so the gap with WIPO's 1,855 utility models is between IP Australia's count and WIPO's.
7. **The innovation closure's window covers standard patents** (U28). IP Australia attributes Australians' 24.8% rise
   in standard patents in 2021 to the closure (applicants kept the option of converting them), and the lens shows the
   same 24.8%. Stage 2's before-and-after for the closure includes residents' standard patents in 2021 and 2022.
8. **First-time filers are counted by applicant as well as by ABN** (U45). Counted by IP RAPID's party id, which needs
   no ABN, first-time resident trade mark filers rose from 22,838 (2024) to 28,626 (2025), and IP Australia reports
   record resident trade marks in 2025; so U45's fall in ABN-linked first-time filers is a fall in linking. From FY2025
   Stage 2 reads entry by applicant beside the ABN count; firm-level filing by ABN still stops at FY2024 (ADR 0016)
   until IP Australia answers OQ7.
9. **Grants: say which.** The timeline's `patents_granted` includes second-tier patents (U27's 25,687 in 2016);
   standard grants, which reproduce IP Australia's in every year published, come from `rights`.
10. **A new Stage 2 pair:** expedited examination (U34) against years in force (U36), the two measures behind the
    finding of IP Australia's commissioned study that fast-tracked patents are renewed, commercialised and built on
    more (ipr-2025 p9 to p15).
11. **IP Australia's interpretations are evidence, not conclusions.** Its readings (digital tools behind the provisional
    rise, country mix behind direct filing, the productivity of first IP rights) are reported with the strength IP
    Australia gives them; adopting any is the owner's call.
12. **The notebook is not rewritten.** Its observations quote the outputs above them, and IP Australia's figures are
    not among those outputs; the verdicts live in the audit, this ADR, the handover and `docs/stage-1-summary.md`.

**Consequences.** Stage 1's counts now have a published benchmark, rerun with every rebuild. Three questions go to IP
Australia with the owner's request (OQ12 to OQ14: the base of its "55.6% of resident applications filed by
individuals" in 2022, which the lens cannot reproduce, U13 and U48 standing meanwhile; the 2018 Madrid gap; the origin
of designs IP RAPID leaves unknown); OQ5 and OQ7 narrow, and two items of the request are answered from the reports.
Agreement with IP Australia shows the lenses read the register as IP Australia does, not that the register is right;
the independent checks remain WIPO's and the World Bank's.
